#!/usr/bin/env python3
"""
Dissolution patterns of a graph-only reactive run (no DFN mesh): paints each
fracture's state on its dfnGen polygon for every VTK output and tracks
network-scale pattern metrics through time.

For each output k of RUN_DIR/single_stage-k.vtk:
  paraview/<name>/fractures_KKK.vtu   one polygon per fracture, cell data:
        fraction_dissolved, <mineral>_VF, (Calcite_VF for gypcal runs), log10_permeability, Q_frac (share
        of the injected flow through the fracture), fracture_id, x_center
  paraview/<name>/fractures.pvd       the time series (time = years)
  RUN_DIR/patterns.csv               one row per output:
        dissolved        fraction of the mineral inventory dissolved
        k_eff_ratio      effective-permeability gain (direct TPFA solve on the
                         frozen permeability, compute_keff_tpfa.py boundaries)
        dQ_P32           100 (sum S Q)^2 / (sum S sum S Q^2): active surface
                         area share (Hyman 2020 flow channelization indicator)
        n90              fractures carrying 90% of the throughflow
        front_x50        x below which half of the dissolved mass sits
        cleared          fraction of fracture area with < 1% mineral left
        gini             Gini coefficient of dissolved mass over fractures
                         (0 = spread evenly, 1 = all in one fracture)

  python3 analyze_km_dissolution_patterns.py RUN_DIR [--name NAME]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "physics_upscaling")]
from diagnose_damkohler_per_fracture import throughflow  # noqa: E402
from compute_keff_tpfa import MU, read_ex, read_uge  # noqa: E402
from bipartite_pressure_solutions_functions import read_scalar_from_vtk  # noqa: E402


def read_polygons(path):
    polys = []
    for line in Path(path).read_text().splitlines()[1:]:
        if not line.strip():
            continue
        pts = re.findall(r"\{([^}]*)\}", line)
        polys.append(np.array([[float(v) for v in p.split(",")] for p in pts]))
    return polys


def poly_area(P):
    c = P.mean(0)
    return 0.5 * np.linalg.norm(sum(np.cross(P[i] - c, P[(i + 1) % len(P)] - c) for i in range(len(P))))


def solve(run, cells, conns, k, rate_m3s, return_pressure=False):
    """Paper-free version of compute_keff_tpfa.dp: manifold injection, seepage
    outflow cells held at a common pressure (Dirichlet on the outflow faces).
    Returns manifold pressure and connection fluxes (m^3/s, i -> j positive)."""
    N = len(cells)
    xyz = cells[:, 1:4]
    i, j = conns[:, 0].astype(int) - 1, conns[:, 1].astype(int) - 1
    f, A = conns[:, 2:5], conns[:, 5]
    d1 = np.linalg.norm(f - xyz[i], axis=1)
    d2 = np.linalg.norm(f - xyz[j], axis=1)
    T = A / (MU * (d1 / k[i] + d2 / k[j]))
    L = coo_matrix((np.r_[T, T, -T, -T], (np.r_[i, j, i, j], np.r_[i, j, j, i])), shape=(N, N)).tolil()
    q = np.zeros(N)
    man = json.loads((run / "inlet_manifold.json").read_text())["manifold_cell"] - 1
    q[man] += rate_m3s
    for row in read_ex(run / "boundary_right_e.ex"):
        c = int(row[0]) - 1
        L[c, c] += row[4] / (MU * max(np.linalg.norm(row[1:4] - xyz[c]), 1e-9) / k[c])
    A = L.tocsr()
    if N > 20000:                                  # dense km graphs: direct LU fill-in costs GBs; CG on the SPD system
        from scipy.sparse.linalg import cg
        d = A.diagonal()
        p, info = cg(A, q, rtol=1e-12, maxiter=20000, M=coo_matrix((1 / d, (np.arange(N), np.arange(N))), shape=(N, N)).tocsr())
    else:
        p = spsolve(A, q)
    if return_pressure:
        return float(p[man]), T * (p[i] - p[j]), i + 1, j + 1, p
    return float(p[man]), T * (p[i] - p[j]), i + 1, j + 1


def gini(x):
    x = np.sort(np.clip(x, 0, None))
    if x.sum() <= 0:
        return np.nan
    n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))


def write_vtu(path, polys, fields):
    pts = np.vstack(polys)
    offs = np.cumsum([len(p) for p in polys])
    conn = np.arange(len(pts))
    with open(path, "w") as fh:
        fh.write('<?xml version="1.0"?>\n<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">\n<UnstructuredGrid>\n')
        fh.write(f'<Piece NumberOfPoints="{len(pts)}" NumberOfCells="{len(polys)}">\n<Points>\n'
                 '<DataArray type="Float64" NumberOfComponents="3" format="ascii">\n')
        fh.write(" ".join(f"{v:.6g}" for v in pts.ravel()) + "\n</DataArray>\n</Points>\n<Cells>\n")
        fh.write('<DataArray type="Int64" Name="connectivity" format="ascii">\n' + " ".join(map(str, conn)) + "\n</DataArray>\n")
        fh.write('<DataArray type="Int64" Name="offsets" format="ascii">\n' + " ".join(map(str, offs)) + "\n</DataArray>\n")
        fh.write('<DataArray type="UInt8" Name="types" format="ascii">\n' + " ".join(["7"] * len(polys)) + "\n</DataArray>\n</Cells>\n")
        fh.write("<CellData>\n")
        for name, v in fields.items():
            fh.write(f'<DataArray type="Float64" Name="{name}" format="ascii">\n' + " ".join(f"{x:.6g}" for x in v) + "\n</DataArray>\n")
        fh.write("</CellData>\n</Piece>\n</UnstructuredGrid>\n</VTKFile>\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--name", default=None)
    ap.add_argument("--no-vtu", action="store_true")
    ap.add_argument("--no-csv", action="store_true", help="do not (over)write RUN_DIR/patterns.csv")
    a = ap.parse_args()
    run = a.run_dir.resolve()
    name = a.name or f"{run.parent.name}__{run.name}"
    out = HERE / "paraview" / name
    out.mkdir(parents=True, exist_ok=True)
    sched = json.loads((run / "single_stage.in.schedule.json").read_text())
    mineral, vf0 = sched.get("mineral", "Gypsum"), sched.get("vf0", 0.77)
    times = [0.0] + list(sched["vtk_times_y"])
    polys = read_polygons(run / "polygons.dat")
    nf = len(polys)
    area = np.array([poly_area(P) for P in polys])
    xc = np.array([P[:, 0].mean() for P in polys])
    cells, conns = read_uge(run / "full_mesh_vol_area.uge")
    vol = cells[:nf, 4]
    own = np.zeros(len(cells), int)
    own[:nf] = np.arange(1, nf + 1)
    own[nf:] = -np.arange(1, len(cells) - nf + 1)
    rate = sched["rate_m3y"] / 3.15576e7
    rows, p0, pvd = [], None, []
    vtks = sorted(run.glob("single_stage-*.vtk"), key=lambda p: int(p.stem.split("-")[1]))
    vf_init = None                                   # per-cell initial fill (heterogeneous fill runs)
    for vk in vtks:
        idx = int(vk.stem.split("-")[1])
        vf = np.asarray(read_scalar_from_vtk(str(vk), f"{mineral}_VF"), float)
        kk = np.asarray(read_scalar_from_vtk(str(vk), "Permeability"), float)
        if len(kk) < len(cells):                     # manifold cell written without data in some outputs
            kk = np.r_[kk, np.full(len(cells) - len(kk), kk.max())]
        pm, flux, ci, cj = solve(run, cells, conns, kk[: len(cells)], rate)
        p0 = p0 or pm
        Qf = throughflow(ci, cj, flux, own)
        Qv = np.array([Qf.get(f, 0.0) for f in range(1, nf + 1)])
        if vf_init is None:
            vf_init = np.where(vf[:nf] > 0, vf[:nf], vf0)
        diss = 1 - np.clip(vf[:nf] / vf_init, 0, 1)
        dmol = diss * vol * vf_init / vf0           # dissolved volume, weighted by each fracture's own fill
        srt = np.sort(Qv)[::-1]
        order = np.argsort(xc)
        cum = np.cumsum(dmol[order])
        rows.append(dict(k=idx, t_y=times[idx] if idx < len(times) else np.nan,
                         dissolved=float(dmol.sum() / (vol * vf_init / vf0).sum()), k_eff_ratio=p0 / pm,
                         dQ_P32=float(100 * (area * Qv).sum() ** 2 / (area.sum() * (area * Qv ** 2).sum())),
                         n90=int(np.searchsorted(np.cumsum(srt) / srt.sum(), 0.9) + 1),
                         front_x50=float(xc[order][np.searchsorted(cum, 0.5 * cum[-1])]) if cum[-1] > 0 else np.nan,
                         cleared=float(area[vf[:nf] < 0.01 * vf_init].sum() / area.sum()), gini=gini(dmol)))
        if not a.no_vtu and (nf < 10000 or idx % 4 == 0 or vk == vtks[-1]):   # dense networks: every 4th frame (disk)
            f = out / f"fractures_{idx:03d}.vtu"
            fields = {"fraction_dissolved": diss, f"{mineral}_VF": vf[:nf],
                      "log10_permeability": np.log10(kk[:nf]), "Q_frac": Qv / rate,
                      "log10_Q_frac": np.log10(np.maximum(Qv / rate, 1e-8)),
                      "fracture_id": np.arange(1, nf + 1), "x_center": xc}
            if sched.get("mode") == "gypcal":                  # coupled runs: also export the calcite volume fraction
                fields["Calcite_VF"] = np.asarray(read_scalar_from_vtk(str(vk), "Calcite_VF"), float)[:nf]
            write_vtu(f, polys, fields)
            pvd.append((rows[-1]["t_y"], f.name))
    d = pd.DataFrame(rows)
    if not a.no_csv:
        d.to_csv(run / "patterns.csv", index=False)
    if pvd:
        (out / "fractures.pvd").write_text('<?xml version="1.0"?>\n<VTKFile type="Collection" version="0.1">\n<Collection>\n'
                                           + "".join(f'<DataSet timestep="{t:.6g}" file="{n}"/>\n' for t, n in pvd)
                                           + "</Collection>\n</VTKFile>\n")
    pd.set_option("display.width", 200)
    print(name, nf, "fractures")
    print(d.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
