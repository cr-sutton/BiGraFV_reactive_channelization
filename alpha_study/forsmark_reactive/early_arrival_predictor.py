#!/usr/bin/env python3
"""
Early-arrival breakthrough predictor (7 Nov 2026; story item D).

The one number: the time by which the first p % of a conservative tracer pulse has left the UNREACTED network, in
units of its mean residence time (t_p / tau_res, from the start-of-run tracer probe snap_0: steady flow on the initial
permeability, pulse of 0.1 tau_res; probe_frozen_state_tracer.py).  It needs a flow solve and a tracer pulse on the
unreacted network, nothing from the reactive run.

Why it should work: at local equilibrium the dissolution front is a strongly retarded copy of the fast part of the
flow field, so how much gypsum must dissolve before the front reaches the outlet is set by how quickly the fast paths
deliver water there, weighted by the flow they carry.  (The single fastest path does not predict it: fastpath_predictor.py,
rank correlation 0.17-0.25.)

Tests, fixed before looking at 2 km: choose p by leave-one-P32-out R^2 on the 1 km runs (x4/x6/x8, 45 networks per
chemistry, the same snap_0 probe settings as 2 km); then fit d_bt = a + b x on all 1 km runs and predict the 45 2 km
networks (new geometries, twice the length) without refitting.  Compared with the largest-fracture flow share.
Events: scale2km/scale_runs.csv (capacity time <= 2 at both scales).
Outputs: phase1/early_arrival_predictor.csv, early_arrival_predictor_fit.csv
  python3 forsmark_reactive/early_arrival_predictor.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]
from analyze_phase1_tracer import read_probe  # noqa: E402

PS = (0.01, 0.05, 0.10, 0.16)


def arrivals(snap):
    meta, t, f = read_probe(snap)
    cum = np.concatenate([[0], np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(t))])
    F = cum / cum[-1]
    return {f"t{int(100 * p):02d}": float(np.interp(p, F, t)) / meta["tau_res_y"] for p in PS} | {"recovery": float(cum[-1])}


def loo(h, x):
    pr = np.empty(len(h))
    for p in h.p32.unique():
        tr = (h.p32 != p).values
        a, b = np.polyfit(h[x][tr], h.d_bt[tr], 1)
        pr[~tr] = a * h[x][~tr] + b
    return 1 - ((h.d_bt - pr) ** 2).sum() / ((h.d_bt - h.d_bt.mean()) ** 2).sum()


def main():
    rows = []
    for scale, base in (("1km", HERE / "phase1"), ("2km", HERE / "scale2km")):
        for run in sorted(base.glob("L2_r15_p*_sg*_seed*/gyp*__phase1")):
            m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d+)", str(run))
            if float(m[1]) not in (4.0, 6.0, 8.0) or not (run / "snap_0" / "snap-mas.dat").exists():
                continue
            rows.append(dict(scale=scale, mode="gypcal" if "calcite" in run.name else "gyponly", p32=float(m[1]),
                             sigma=float(m[2]), seed=int(m[3]), **arrivals(run / "snap_0")))
    A = pd.DataFrame(rows)
    ev = pd.read_csv(HERE / "scale2km" / "scale_runs.csv").rename(columns={"domain": "scale", "breakthrough": "d_bt"})
    bp = pd.read_csv(HERE / "phase1" / "breakthrough_predictor.csv")[["p32", "sigma", "seed", "top1_share"]].drop_duplicates(["p32", "sigma", "seed"])
    D = ev[["scale", "mode", "p32", "sigma", "seed", "d_bt"]].merge(A, on=["scale", "mode", "p32", "sigma", "seed"])
    D = D.merge(bp.assign(scale="1km"), on=["scale", "p32", "sigma", "seed"], how="left")
    D.to_csv(HERE / "phase1" / "early_arrival_predictor.csv", index=False)
    out = []
    for mo, h in D.groupby("mode"):
        a = h[h.scale == "1km"].reset_index(drop=True)
        b = h[h.scale == "2km"].reset_index(drop=True)
        r = dict(mode=mo, n_1km=len(a), n_2km=len(b), loo_top1=loo(a, "top1_share"), rho_top1=spearmanr(a.top1_share, a.d_bt).statistic)
        for p in PS:
            x = f"t{int(100 * p):02d}"
            r[f"loo_{x}"] = loo(a, x)
            r[f"rho_{x}"] = spearmanr(a[x], a.d_bt).statistic
        best = max((f"t{int(100 * p):02d}" for p in PS), key=lambda x: r[f"loo_{x}"])
        s, c = np.polyfit(a[best], a.d_bt, 1)
        pb = c + s * b[best]
        r.update(best=best, slope=s, icpt=c, r2_2km=1 - ((b.d_bt - pb) ** 2).sum() / ((b.d_bt - b.d_bt.mean()) ** 2).sum(),
                 rho_2km=spearmanr(b[best], b.d_bt).statistic, mae_2km=float((b.d_bt - pb).abs().median()),
                 bias_2km=float((b.d_bt - pb).median()))
        out.append(r)
    F = pd.DataFrame(out)
    F.to_csv(HERE / "phase1" / "early_arrival_predictor_fit.csv", index=False)
    pd.set_option("display.width", 250)
    print(F.round(3).T.to_string())


if __name__ == "__main__":
    main()
