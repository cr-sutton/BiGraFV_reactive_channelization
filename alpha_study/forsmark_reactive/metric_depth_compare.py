#!/usr/bin/env python3
"""
Channel depth on three measures for the 120 Phase 1 runs (6 Nov 2026): PR_V (pr_fracture_vol), area-weighted PR
(pr_fracture_area) and Hyman's active surface area 100 d_Q/P32 (dQ_P32; Maillot et al. 2016 Eq. 8, pydfnworks compute_dQ).
Per run and measure: start value, depth = min / start, dissolved fraction at the minimum, end / min.  All saved states.

  python3 forsmark_reactive/metric_depth_compare.py   -> phase1/metric_depth_compare.csv (+ summary printed)
"""
import re
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
rows = []
for run in sorted((HERE / "phase1").glob("L2_r15_p*_sg*_seed*/gyp*__phase1")):
    f = run / "channelization.csv"
    if not f.exists():
        continue
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", str(run))
    c = pd.read_csv(f).sort_values("k").reset_index(drop=True)
    r = dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode="gypcal" if "calcite" in run.name else "gyponly")
    for col, lab in (("pr_fracture_vol", "prv"), ("pr_fracture_area", "pra"), ("dQ_P32", "dq")):
        i = c[col].idxmin()
        r[f"{lab}_start"] = c[col].iloc[0]
        r[f"{lab}_depth"] = c[col].min() / c[col].iloc[0]
        r[f"{lab}_d_at_min"] = c.dissolved[i]
        r[f"{lab}_end_over_min"] = c[col].iloc[-1] / c[col].min()
    rows.append(r)
df = pd.DataFrame(rows)
df.to_csv(HERE / "phase1" / "metric_depth_compare.csv", index=False)
print(len(df), "runs")
print(df.groupby("mode")[[c for c in df.columns if c.endswith(("_start", "_depth", "_d_at_min", "_end_over_min"))]].median().round(3).T)
print("Spearman PR_V depth vs dQ depth:", round(spearmanr(df.prv_depth, df.dq_depth)[0], 3))
