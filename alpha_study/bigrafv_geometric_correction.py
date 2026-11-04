"""Fit-free geometric (TPFA-consistent) BiGraFV correction.

Slots into the existing workflow between graph_to_pflotran and pflotran:

    G = DFN.create_graph("bipartite", inflow="left", outflow="right")
    DFN.graph_to_pflotran(G, uge_filename="full_mesh_vol_area.uge")   # unchanged
    apply_geometric_correction(graph_dir, DFN.perm, DFN.aperture, domain)
    DFN.pflotran(...)

Only UGE connection face positions and areas are rewritten.  Cell volumes,
dfn_properties.h5, boundary .ex files, graph_to_pflotran and dfnWorks are
untouched.  For each fracture the steady 2D Darcy problem is solved in its
own (dfnGen) polygon between its intersection ports; the flow-conditioned
half factor g_{f,k} = q_{f,k} / (T_f (Pbar_f - pbar_k)) is geometric (T_f
divided out), and each connection's face is placed on the centre-centre
segment at t = Gamma_j/(Gamma_i+Gamma_j) with area
A = D Gamma_i Gamma_j/(Gamma_i+Gamma_j), Gamma = b g, so PFLOTRAN's own
harmonic averaging gives the right half conductance for k and for every
species' phi*tau*D.  The half factors are computed at two raster levels and
extrapolated with the observed convergence order (see
physics_upscaling/convergence_order_study.py).  No DFN pressure or flow is
used.
"""
from __future__ import annotations

import json
import os
import pickle
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE / "physics_upscaling"))

from convergence_order_study import fill_bad  # noqa: E402
from dfn_geometry import fractures_from_dfngen, intersections_from_dfngen  # noqa: E402
from mp_pressure_check import recentered_segments  # noqa: E402
from multiport_upscaling import assemble_and_solve, build_ports  # noqa: E402
from star_geometry import flow_conditioned_half_factors  # noqa: E402
from write_corrected_bigrafv_inputs import write_geometric_uge  # noqa: E402

# (cells across a fracture, sub-ports per intersection), both halved together
DEFAULT_LEVELS = ((64, 6), (128, 12))
# observed convergence order of the corrected-graph flow: median 0.84 (IQR 0.75-0.92)
# over 33 archived networks at 4 raster levels (physics_upscaling/convergence_order_study.py)
DEFAULT_ORDER = 0.84

GRAPH_INPUTS = ("full_mesh_vol_area.uge", "dfn_properties.h5", "boundary_left_w.ex",
                "boundary_right_e.ex", "altered_cells_df.dat")


@contextmanager
def _pushd(path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def half_factors(F, I, levels=DEFAULT_LEVELS, order=DEFAULT_ORDER):
    """Extrapolated geometric half factors g[(fracture_id, port)].

    Well-posed halves come from the in-plane physics, extrapolated in raster
    resolution with the observed convergence order.  Halves whose in-plane
    flux runs against the centre-to-port pressure drop (or carry no flux)
    cannot be represented by a positive two-point half-transmissibility; they
    take the median factor of the fracture's well-posed halves.  (Setting them
    instead so the graph matches the multiport flow was tested and rejected:
    the target is unreachable with positive values, because raising those
    halves pushes more flux the wrong way.)
    """
    sols, qs = [], []
    for nc, ns in levels:
        q, det = assemble_and_solve(F, build_ports(F, I, n_sub=ns), ncell=nc, return_details=True)
        sols.append(flow_conditioned_half_factors(F, det))
        qs.append(q)
    (g_c, _), (g_f, bad_f) = sols[-2], sols[-1]
    r = 1.0 / (2.0 ** order - 1.0)
    g = {}
    for k, vf in g_f.items():
        v = vf + (vf - g_c.get(k, vf)) * r
        g[k] = v if v > 0 else vf
    level_data = [dict(level=list(lv), q_multiport=q, g=gg, bad=bb) for lv, q, (gg, bb) in zip(levels, qs, sols)]
    return fill_bad(g, bad_f), dict(n_half=len(g_f) + len(bad_f), n_unrepresentable=len(bad_f)), level_data


def apply_geometric_correction(graph_dir, perm, aperture, domain, flow_axis="x",
                               levels=DEFAULT_LEVELS, order=DEFAULT_ORDER):
    """Rewrite graph_dir/full_mesh_vol_area.uge in place (original kept as *_uncorrected.uge)."""
    if flow_axis != "x":
        raise NotImplementedError("only x-direction flow (left_w -> right_e) is implemented")
    t0 = perf_counter()
    graph_dir = Path(graph_dir)
    dfngen = graph_dir / "dfnGen_output"
    F = fractures_from_dfngen(dfngen, np.asarray(perm, float), np.asarray(aperture, float), domain)
    ints = intersections_from_dfngen(dfngen)
    I = recentered_segments(None, F, ints)
    g, info, level_data = half_factors(F, I, levels, order)
    (graph_dir / "geometric_levels.pkl").write_bytes(pickle.dumps(level_data))
    uge = graph_dir / "full_mesh_vol_area.uge"
    backup = graph_dir / "full_mesh_vol_area_uncorrected.uge"
    if not backup.exists():
        shutil.copy(uge, backup)
    E = pd.DataFrame(dict(intersection_id=I.intersection_id, u=I.f1, v=I.f2))
    status = write_geometric_uge(graph_dir, graph_dir, E, F, g, float(domain[0]))
    pd.DataFrame([dict(fracture_id=f, port=k, g=v) for (f, k), v in g.items()]).to_csv(
        graph_dir / "geometric_half_factors.csv", index=False)
    summary = dict(levels=[list(l) for l in levels], order=order, n_fractures=len(F),
                   n_intersections=len(ints), connections=status, seconds=perf_counter() - t0, **info)
    (graph_dir / "geometric_correction.json").write_text(json.dumps(summary, indent=2))
    return summary


def run_geometric_graph(DFN, raw_graph_dir, out_dir, domain, restart_file=None,
                        inflow_pressure=2.0e6, outflow_pressure=1.0e6):
    """Copy a finished raw-graph run, apply the correction, run PFLOTRAN the
    same way the drivers do (DFN.pflotran / pflotran_cleanup / effective_perm)."""
    raw_graph_dir, out_dir = Path(raw_graph_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in GRAPH_INPUTS:
        shutil.copy(raw_graph_dir / f, out_dir / f)
    if not (out_dir / "dfnGen_output").exists():
        shutil.copytree(raw_graph_dir / "dfnGen_output", out_dir / "dfnGen_output")
    summary = apply_geometric_correction(out_dir, DFN.perm, DFN.aperture, domain)
    with _pushd(out_dir):
        if restart_file:
            DFN.pflotran(restart=True, restart_file=str(restart_file))
        else:
            DFN.pflotran()
        DFN.pflotran_cleanup()
        Q = float(DFN.effective_perm(inflow_pressure=inflow_pressure, outflow_pressure=outflow_pressure,
                                     boundary_file="boundary_left_w.ex", direction="x",
                                     darcy_vel_file="darcyvel_001.dat"))
    summary["Q_geometric"] = Q
    return Q, summary
