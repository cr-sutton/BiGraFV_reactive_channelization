#!/usr/bin/env python3
"""
Where along the flow direction does channelization happen? (5 Nov 2026, user request)

Phase 1 runs (tag phase1, P32 x4-x16, sigma 0/0.5/1, seeds 1-5, gyponly + gypcal).  Fractures are binned by the x of
their centre (10 bins of 100 m, distance from the inlet), and at every saved state each bin gets:
  active    Hyman's active surface fraction of the fractures in the bin, d_Q/P32 = (sum S Q)^2 / (sum S * sum S Q^2)
            (pydfnworks dfnGraph compute_dQ; S = polygon area, Q = fracture throughflow)
  prv       volume-weighted participation ratio of the bin, (sum Q)^2 / (sum V * sum Q^2 / V)
  qshare    summed fracture throughflow in the bin over the injected rate (water crossing several fractures counts in each;
            a fracture spanning bins counts once,
            in the bin of its centre)
Inputs: paraview/<net>__<run>/fractures_KKK.vtu (Q_frac = throughflow / injected rate, x_center), polygon areas from
polygons.dat, fracture volumes from the UGE, dissolved fraction from patterns.csv.

  python3 forsmark_reactive/xbin_channelization.py   -> phase1/xbin_channelization.csv
"""
from __future__ import annotations

import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT), str(ROOT / "physics_upscaling")]
from analyze_km_dissolution_patterns import poly_area, read_polygons  # noqa: E402
from analyze_phase1_mechanism import read_vtu  # noqa: E402
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

P1 = HERE / "phase1"
PV = ROOT / "paraview"
EDGES = np.arange(0.0, 1001.0, 100.0)


def one(run):
    run = Path(run)
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", str(run))
    mode = "gypcal" if "calcite" in run.name else "gyponly"
    files = sorted((PV / f"{run.parent.name}__{run.name}").glob("fractures_*.vtu"))
    pat = pd.read_csv(run / "patterns.csv").set_index("k")
    polys = read_polygons(run / "polygons.dat")
    nf = len(polys)
    S = np.array([poly_area(P) for P in polys])
    V = read_uge(run / "full_mesh_vol_area.uge")[0][:nf, 4]
    rows = []
    for f in files:
        k = int(f.stem.split("_")[1])
        if k not in pat.index:
            continue
        a = read_vtu(f)
        q = np.abs(a["Q_frac"]).astype(float)
        b = np.clip(np.digitize(a["x_center"].astype(float) + 500.0, EDGES) - 1, 0, len(EDGES) - 2)
        for i in range(len(EDGES) - 1):
            s = b == i
            if s.sum() < 2 or q[s].sum() <= 0:
                continue
            qs, Ss, Vs = q[s], S[s], V[s]
            rows.append(dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode=mode, k=k, dissolved=pat.loc[k, "dissolved"],
                             bin=i, x_mid=0.5 * (EDGES[i] + EDGES[i + 1]), n_frac=int(s.sum()),
                             active=float((Ss * qs).sum() ** 2 / (Ss.sum() * (Ss * qs ** 2).sum())),
                             prv=float(qs.sum() ** 2 / (Vs.sum() * (qs ** 2 / Vs).sum())), qshare=float(qs.sum())))
    return rows


def main():
    runs = sorted(str(r) for r in P1.glob("L2_r15_p*_sg*_seed*/gyp*__phase1") if (r / "patterns.csv").exists())
    with Pool(4) as p:
        rows = [r for rs in p.map(one, runs) for r in rs]
    df = pd.DataFrame(rows).sort_values(["mode", "p32", "sigma", "seed", "k", "bin"])
    df.to_csv(P1 / "xbin_channelization.csv", index=False)
    print(len(runs), "runs,", len(df), "rows")


if __name__ == "__main__":
    main()
