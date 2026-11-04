"""Write corrected BiGraFV PFLOTRAN inputs and (optionally) run them.

The correction is carried entirely by the existing input files:
  full_mesh_vol_area.uge : connection AREA multiplied by c_e  (local+global)
  dfn_properties.h5      : permeability unchanged (K-only global option kept)
  boundary_*.ex          : unchanged
Cell volumes / apertures are untouched, so storage and pore volume are those
of the uncorrected BiGraFV graph.

Modes
  multiport : c_e from the local-global multiport upscaling (graph-only)
  oracle    : uniform K-only multiplier alpha* (uses DFN Q; benchmark only)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from local_global_transmissibility import bigrafv_edges, local_global_multipliers, solve_graph  # noqa: E402
from mp_pressure_check import multiport_solution  # noqa: E402

PFLOTRAN = str(Path.home() / "bin" / "pflotran")
DECK_DIR = HERE.parent


def read_uge(path):
    lines = Path(path).read_text().splitlines()
    nc = int(lines[0].split()[1])
    cells = np.array([[float(x) for x in l.split()] for l in lines[1 : 1 + nc]])
    hdr = 1 + nc
    ncon = int(lines[hdr].split()[1])
    cons = np.array([[float(x) for x in l.split()] for l in lines[hdr + 1 : hdr + 1 + ncon]])
    return cells, cons


def write_uge(path, cells, cons):
    with open(path, "w") as fh:
        fh.write(f"CELLS\t{len(cells)}\n")
        for c in cells:
            fh.write(f"{int(c[0])}\t" + "\t".join(f"{v:.16E}" for v in c[1:]) + "\n")
        fh.write(f"CONNECTIONS\t{len(cons)}\n")
        for c in cons:
            fh.write(f"{int(c[0])}\t{int(c[1])}\t" + "\t".join(f"{v:.16E}" for v in c[2:]) + "\n")


def connection_multipliers(raw_dir: Path, E: pd.DataFrame, domain_x: float):
    """Map per-edge multipliers onto UGE connection rows."""
    cells, cons = read_uge(raw_dir / "full_mesh_vol_area.uge")
    alt = pd.read_csv(raw_dir / "altered_cells_df.dat", sep=r"\s+")
    alt = alt.set_index("id")
    pair_c = {}
    for u, v, c in zip(E.u, E.v, E.c):
        pair_c[(u, v) if isinstance(v, str) else frozenset((u, v))] = c
    half = 0.5 * domain_x
    mult = np.ones(len(cons))
    kind = []
    for k, (i, j) in enumerate(cons[:, :2].astype(int)):
        ti, tj = alt.loc[i, "row_type"], alt.loc[j, "row_type"]
        if ti == "internal" and tj == "internal":
            mult[k] = pair_c.get(frozenset((i, j)), np.nan)
            kind.append("internal")
            continue
        b, f = (i, j) if ti != "internal" else (j, i)
        f = int(alt.loc[b, "parent_cell_id"]) if pd.notna(alt.loc[b, "parent_cell_id"]) else f
        xb = float(alt.loc[b, "x"])
        if abs(xb + half) < 1e-6 * max(1.0, half):
            mult[k] = pair_c.get((f, "source"), np.nan); kind.append("source")
        elif abs(xb - half) < 1e-6 * max(1.0, half):
            mult[k] = pair_c.get((f, "target"), np.nan); kind.append("target")
        else:
            kind.append("side")
    kind = np.array(kind)
    # any unmapped flow connection falls back to the median multiplier
    bad = ~np.isfinite(mult)
    if bad.any():
        mult[bad] = float(np.exp(np.nanmedian(np.log(mult[~bad & (kind != "side")]))))
    return cells, cons, mult, kind


def write_geometric_uge(raw_dir: Path, work: Path, E: pd.DataFrame, fracs, g: dict, domain_x: float,
                        boundary_t=1.0 - 1.0e-3):
    """Encode per-half geometric factors Gamma = b * g as UGE geometry only.

    PFLOTRAN's TPFA conductance for any coefficient c (k, phi*tau*D_s, ...) is
        A / (d_i/c_i + d_j/c_j),  d_i = t D, d_j = (1-t) D,  D = |x_j - x_i|.
    Choosing  t = Gamma_j/(Gamma_i+Gamma_j)  and  A = D Gamma_i Gamma_j/(Gamma_i+Gamma_j)
    gives half conductances c_i Gamma_i and c_j Gamma_j for every coefficient,
    so flow and every species' diffusion see the same in-plane geometry, and
    changes of k or phi on one side act only on that half.  The face stays on
    the centre-centre segment (TPFA orthogonality) and D is the physical
    distance.  Cell volumes, permeability (h5) and boundary .ex are untouched.
    """
    cells, cons = read_uge(raw_dir / "full_mesh_vol_area.uge")
    alt = pd.read_csv(raw_dir / "altered_cells_df.dat", sep=r"\s+").set_index("id")
    xyz = {int(c[0]): c[1:4] for c in cells}
    iid_of = {frozenset((u, v)): iid for iid, u, v in zip(E.intersection_id, E.u, E.v) if not isinstance(v, str)}
    half = 0.5 * domain_x
    cons = cons.copy()
    status = []
    for k, (i, j) in enumerate(cons[:, :2].astype(int)):
        ti, tj = alt.loc[i, "row_type"], alt.loc[j, "row_type"]
        xi, xj = xyz[i], xyz[j]
        D = float(np.linalg.norm(xj - xi))
        if ti == "internal" and tj == "internal":
            iid = iid_of.get(frozenset((i, j)))
            gi, gj = g.get((i, iid)), g.get((j, iid))
            if iid is None or gi is None or gj is None:
                status.append("unchanged"); continue
            Gi, Gj = fracs[i].aperture * gi, fracs[j].aperture * gj
            t = Gj / (Gi + Gj)
            cons[k, 2:5] = xi + t * (xj - xi)
            cons[k, 5] = D * Gi * Gj / (Gi + Gj)
            status.append("internal")
            continue
        b_cell, f = (i, j) if ti != "internal" else (j, i)
        xb = float(alt.loc[b_cell, "x"])
        side = "source" if abs(xb + half) < 1e-6 * max(1.0, half) else (
            "target" if abs(xb - half) < 1e-6 * max(1.0, half) else None)
        gf = g.get((f, side)) if side else None
        if gf is None:
            status.append("unchanged"); continue
        Gf = fracs[f].aperture * gf
        xf, xbc = xyz[f], xyz[b_cell]
        # face next to the boundary cell: the fracture half carries all the resistance
        cons[k, 2:5] = xf + boundary_t * (xbc - xf)
        cons[k, 5] = Gf * boundary_t * D
        status.append(side)
    write_uge(work / "full_mesh_vol_area.uge", cells, cons)
    return pd.Series(status).value_counts().to_dict()


def slow_zone_table(fracs, ports, det, ncell):
    """Per-fracture flowing fraction and fast/slow exchange (unit-pressure units)."""
    from multiport_upscaling import flow_partition, fracture_dtn

    rows = []
    for fid, plist in ports.items():
        if len(plist) < 2 or fid not in det["pbar"]:
            continue
        keys, _, _, field = fracture_dtn(fracs[fid], plist, ncell=ncell, return_field=True)
        pp = np.array([det["p"][k] for k in keys])
        phi, q_ex, q_th = flow_partition(field, pp)
        T = fracs[fid].transmissivity
        rows.append(dict(fracture_id=fid, phi_flow=phi, q_ex=T * q_ex, q_through=T * q_th))
    return pd.DataFrame(rows)


def add_slow_cells(work: Path, sz: pd.DataFrame, q_scale_m3s: float, min_slow=0.02,
                   porosity=0.9, tortuosity=1.0, diffusion=1.0e-9, offset=1.0e-3,
                   slow_perm_factor=1.0e-8):
    """Attach one dead-end slow cell per flowing fracture (first-order exchange).

    The fracture cell keeps phi_flow*V; the new cell holds (1-phi_flow)*V.  The
    connection area/distance is set so PFLOTRAN's diffusive exchange
    (porosity*tortuosity*D*A/d) equals the slow-zone throughput q_ex.  Steady
    advection into a dead-end cell is zero, so the flow solution is unchanged.
    """
    cells, cons = read_uge(work / "full_mesh_vol_area.uge")
    with h5py.File(work / "dfn_properties.h5", "r") as h:
        ids = h["Cell Ids"][...]
        perm = h["Permeability"][...]
    perm_of = dict(zip(ids.tolist(), perm.tolist()))
    vol_row = {int(c[0]): k for k, c in enumerate(cells)}
    new_cells, new_cons, new_ids, new_perm = [], [], [], []
    nid = int(cells[:, 0].max())
    for r in sz.itertuples():
        slow = 1.0 - r.phi_flow
        if slow < min_slow or r.q_ex <= 0:
            continue
        k = vol_row[int(r.fracture_id)]
        V = cells[k, 4]
        cells[k, 4] = V * r.phi_flow
        nid += 1
        x = cells[k, 1:4] + np.array([offset, 0.0, 0.0])
        new_cells.append([nid, *x, V * slow])
        q = r.q_ex * q_scale_m3s
        area = q * offset / (porosity * tortuosity * diffusion)
        new_cons.append([int(r.fracture_id), nid, *(cells[k, 1:4] + 0.5 * (x - cells[k, 1:4])), area])
        new_ids.append(nid)
        # near-impermeable: no flow coupling, exchange is diffusive only
        new_perm.append(perm_of[int(r.fracture_id)] * slow_perm_factor)
    if new_cells:
        cells = np.vstack([cells, np.array(new_cells)])
        cons = np.vstack([cons, np.array(new_cons)])
    write_uge(work / "full_mesh_vol_area.uge", cells, cons)
    with h5py.File(work / "dfn_properties.h5", "w") as h:
        h["Cell Ids"] = np.r_[ids, np.array(new_ids, ids.dtype)]
        h["Permeability"] = np.r_[perm, np.array(new_perm)]
    return len(new_cells)


def run_pflotran(work: Path, tracer=True, np_=1):
    shutil.copy(DECK_DIR / "pflotran_graph_pressure.in", work / "pflotran_graph_pressure.in")
    shutil.copy(DECK_DIR / "pflotran_graph_tracer.in", work / "pflotran_graph_tracer.in")
    for deck in (["pflotran_graph_pressure.in"] + (["pflotran_graph_tracer.in"] if tracer else [])):
        cmd = [PFLOTRAN, "-pflotranin", deck]
        r = subprocess.run(cmd, cwd=work, capture_output=True, text=True)
        (work / (deck + ".stdout")).write_text(r.stdout[-20000:] + r.stderr[-5000:])
        if r.returncode != 0:
            raise RuntimeError(f"pflotran failed in {work} on {deck}")


def mass_rate(path, col="INFLOW Water Mass [kg/y]"):
    hdr = Path(path).read_text().splitlines()[0]
    names = [h.strip().strip('"') for h in hdr.split('","')]
    names = [n.strip('"') for n in names]
    d = np.loadtxt(path, skiprows=1)
    return d[:, names.index(col)]


def prepare_case(seed_dir: Path, out_root: Path, modes=("multiport", "oracle"), tracer=True,
                 ncell=128, n_sub=12):
    seed_dir = Path(seed_dir)
    st = seed_dir / "study"
    raw = st / "graph_uncorrected_raw"
    ft = json.loads((st / "flow_targets.json").read_text())
    ns = json.loads((st / "network_summary.json").read_text())
    alpha_star = float(ft.get("alpha_q_ratio", ft.get("alpha_star")))
    res = dict(seed_dir=str(seed_dir), alpha_star=alpha_star)

    if list(modes) == ["geometric"]:
        from star_case import run_flow_conditioned
        row, g, Fg, Eg = run_flow_conditioned(st)
        res.update({k: v for k, v in row.items() if k != "study"})
        work = out_root / seed_dir.parent.name / seed_dir.name / "geometric"
        work.mkdir(parents=True, exist_ok=True)
        for f in ("boundary_left_w.ex", "boundary_right_e.ex", "dfn_properties.h5", "full_mesh_vol_area.uge"):
            shutil.copy(raw / f, work / f)
        res["uge_status"] = write_geometric_uge(raw, work, Eg, Fg, g, ns["domain_x"])
        pd.DataFrame([dict(fracture_id=f, port=k, g=v) for (f, k), v in g.items()]).to_csv(
            work / "half_geometric_factors.csv", index=False)
        run_pflotran(work, tracer=tracer)
        res["Q_geometric"] = float(mass_rate(work / "pflotran_graph_pressure-mas.dat")[-1])
        return res

    F, I, q_mp, det = multiport_solution(st, ncell=ncell, n_sub=n_sub)
    E = bigrafv_edges(st)
    Qg, _ = solve_graph(E, "G_graph")
    E, fill = local_global_multipliers(E, det)
    Qlg, Plg = solve_graph(E, "G_lg")
    # global level: first-order Richardson extrapolation of the multiport
    # conductance (grid spacing and sub-port length both halved)
    _, _, q_c, _ = multiport_solution(st, ncell=ncell // 2, n_sub=max(n_sub // 2, 1))
    alpha_inf = (2.0 * q_mp - q_c) / Qg
    E["c"] *= alpha_inf * Qg / Qlg
    E["G_lg"] = E.G_graph * E.c
    res.update(alpha_mp=q_mp / Qg, alpha_mp_coarse=q_c / Qg, alpha_inf=alpha_inf,
               alpha_lg_unscaled=Qlg / Qg, frac_illposed=float((E.status != "ok").mean()))

    for mode in modes:
        work = out_root / seed_dir.parent.name / seed_dir.name / mode
        work.mkdir(parents=True, exist_ok=True)
        for f in ("boundary_left_w.ex", "boundary_right_e.ex", "dfn_properties.h5", "full_mesh_vol_area.uge"):
            shutil.copy(raw / f, work / f)
        if mode == "multiport":
            cells, cons, mult, kind = connection_multipliers(raw, E, ns["domain_x"])
            cons = cons.copy()
            cons[:, 5] *= mult
            write_uge(work / "full_mesh_vol_area.uge", cells, cons)
            pd.DataFrame(dict(i=cons[:, 0].astype(int), j=cons[:, 1].astype(int), kind=kind, multiplier=mult)).to_csv(
                work / "connection_multipliers.csv", index=False)
        elif mode == "multiport_tail":
            # same corrected hydraulics as 'multiport', plus slow cells; needs the
            # multiport run for the physical flux scale (kg/y -> m3/s)
            mp_dir = work.parent / "multiport"
            shutil.copy(mp_dir / "full_mesh_vol_area.uge", work / "full_mesh_vol_area.uge")
            from multiport_upscaling import build_ports
            sz = slow_zone_table(F, build_ports(F, I, n_sub=n_sub), det, ncell)
            # multiport fluxes are in unit-pressure units summing to q_mp
            q_real = float(mass_rate(mp_dir / "pflotran_graph_pressure-mas.dat")[-1]) / 997.16 / (365.25 * 86400.0)
            res["n_slow_cells"] = add_slow_cells(work, sz, q_real / q_mp)
            sz.to_csv(work / "slow_zones.csv", index=False)
            res["phi_flow_median"] = float(sz.phi_flow.median())
        elif mode == "oracle":
            with h5py.File(work / "dfn_properties.h5", "r+") as h:
                h["Permeability"][...] = h["Permeability"][...] * alpha_star
        run_pflotran(work, tracer=tracer)
        res[f"Q_{mode}"] = float(mass_rate(work / "pflotran_graph_pressure-mas.dat")[-1])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed_dirs", nargs="+")
    ap.add_argument("--out-root", default=str(HERE / "pflotran_runs"))
    ap.add_argument("--modes", nargs="+", default=["multiport", "oracle"])
    ap.add_argument("--no-tracer", action="store_true")
    a = ap.parse_args()
    for s in a.seed_dirs:
        r = prepare_case(Path(s), Path(a.out_root), a.modes, tracer=not a.no_tracer)
        print(json.dumps(r), flush=True)


if __name__ == "__main__":
    main()
