#!/usr/bin/env python3
"""
Effective-permeability gain of a frozen state by a direct TPFA solve on the
run's UGE (same boundaries as the paper-style probe deck: injection at the
inlet manifold, permeability-scaled extraction on the outflow cells, one
pinned outflow node).  PFLOTRAN's VTK pressures carry ~1 Pa resolution, too
coarse once k has risen 100x; this solve has none of that rounding.

  python3 compute_keff_tpfa.py RUN_DIR [RUN_DIR ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import h5py
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

MU = 8.904156e-4            # Pa s (PFLOTRAN default water viscosity)


def read_uge(path):
    lines = Path(path).read_text().split("\n")
    nc = int(lines[0].split()[1])
    cells = np.array([list(map(float, l.split())) for l in lines[1:1 + nc]])
    nf = int(lines[1 + nc].split()[1])
    conns = np.array([list(map(float, l.split())) for l in lines[2 + nc:2 + nc + nf]])
    return cells, conns


def read_ex(path):
    lines = Path(path).read_text().split("\n")
    n = int(lines[0].split()[1])
    return np.array([list(map(float, l.split())) for l in lines[1:1 + n]])


def dp(run, k, rate_m3s):
    cells, conns = read_uge(run / "full_mesh_vol_area.uge")
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
    out = read_ex(run / "boundary_right_e.ex")
    oc = out[:, 0].astype(int) - 1
    w = k[oc] / k[oc].sum()
    np.add.at(q, oc, -rate_m3s * w)
    pin = read_ex(run / "pinned.ex")[0]
    c = int(pin[0]) - 1
    L[c, c] += pin[4] / (MU * np.linalg.norm(pin[1:4] - xyz[c]) / k[c])   # Dirichlet face, p_bc = 0
    p = spsolve(L.tocsr(), q)
    return float(p[man])


def main():
    for run in map(Path, sys.argv[1:]):
        sched = json.loads((run / "single_stage.in.schedule.json").read_text())
        rate = sched["rate_m3y"] / 3.15576e7
        rows, p0 = [], None
        for snap in sorted(run.glob("snap_*"), key=lambda s: int(s.name.split("_")[1])):
            with h5py.File(snap / "snap_properties.h5") as h:
                ids = np.asarray(h["Cell Ids"]).astype(int)
                k = np.empty(ids.max())
                k[ids - 1] = np.asarray(h["Permeability"], float)
            d = dp(run, k, rate)
            p0 = p0 or d
            rows.append(dict(k=int(snap.name.split("_")[1]), dp_Pa=d, k_eff_ratio=p0 / d))
        (run / "tpfa_keff.json").write_text(json.dumps(rows, indent=1))
        print(run.name, " ".join(f"{r['k']}:{r['dp_Pa']:.2f}Pa/x{r['k_eff_ratio']:.2f}" for r in rows))


if __name__ == "__main__":
    main()
