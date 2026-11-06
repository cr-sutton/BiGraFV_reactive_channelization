#!/usr/bin/env python3
"""Per 100 m bin (Phase 1, 120 runs): lowest value / start of PR_V and of Hyman active area, the dissolved fraction at that
minimum and the end value / start; medians over runs by chemistry and bin.  phase1/xbin_channelization.csv ->
phase1/xbin_bin_minima.csv.   python3 forsmark_reactive/xbin_bin_minima.py"""
from pathlib import Path
import pandas as pd
P1 = Path(__file__).resolve().parent / "phase1"
df = pd.read_csv(P1 / "xbin_channelization.csv")
r = []
for (mo, p, sg, s, b), h in df.groupby(["mode", "p32", "sigma", "seed", "bin"]):
    h = h.sort_values("k")
    if h.k.iloc[0] != 0:
        continue
    for m in ("prv", "active"):
        y = h[m] / h[m].iloc[0]
        r.append(dict(mode=mo, p32=p, sigma=sg, seed=s, bin=b, x_from_inlet_m=f"{100*b}-{100*b+100}", metric=m,
                      min_rel=y.min(), d_at_min=h.dissolved[y.idxmin()], end_rel=y.iloc[-1]))
r = pd.DataFrame(r)
out = r.groupby(["metric", "mode", "bin", "x_from_inlet_m"])[["min_rel", "d_at_min", "end_rel"]].median().reset_index()
out["n_runs"] = r.groupby(["metric", "mode", "bin"]).size().values
out.to_csv(P1 / "xbin_bin_minima.csv", index=False)
print(out.round(3).to_string(index=False))
