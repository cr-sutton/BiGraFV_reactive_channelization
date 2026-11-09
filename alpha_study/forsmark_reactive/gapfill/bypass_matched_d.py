#!/usr/bin/env python3
"""
Exploratory (not pre-registered), A2 rule 3 follow-up: dissolution efficiency E = dd/dt_cap and bypass index I compared
at matched dissolved fraction instead of matched capacity time (the locked rule was confounded by the gypsum left).
First run Sun 8 Nov on ceilN2L / ceilN3L (d 0.5, 0.6, 0.7); rerun with ceilN3XL (n = 3 to capacity time 20) and
d up to 0.8 once those runs finished.
  python3 forsmark_reactive/gapfill/bypass_matched_d.py   (needs gapA2_bypass_states.csv from analyze_gapfill_a2.py)
  -> gapA2_bypass_matched_d.csv, gapA2_bypass_matched_d_summary.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DS = (0.5, 0.6, 0.7, 0.8)
B = pd.read_csv(HERE / "gapA2_bypass_states.csv")
rows = []
for (p, s, tag), h in B.groupby(["p32", "seed", "tag"]):
    h = h.sort_values("k")
    h = h[h.t_cap > 0]
    t, d, I = h.t_cap.values, h.dissolved.values, h.I.values
    tm, dm, E = 0.5 * (t[1:] + t[:-1]), 0.5 * (d[1:] + d[:-1]), np.diff(d) / np.diff(t)
    for dd in DS:
        if dm.min() <= dd <= dm.max():
            rows.append(dict(p32=p, seed=s, tag=tag, d=dd, E=float(np.interp(dd, dm, E)), I=float(np.interp(dd, d, I)),
                             t_at=float(np.interp(dd, d, t))))
R = pd.DataFrame(rows)
R.to_csv(HERE / "gapA2_bypass_matched_d.csv", index=False)
P = R.pivot_table(index=["p32", "seed", "d"], columns="tag", values=["E", "I", "t_at"])
out = []
for n3 in ("ceilN3L", "ceilN3XL"):
    for dd in DS:
        q = P.xs(dd, level="d")[[("E", "ceilN2L"), ("E", n3), ("I", "ceilN2L"), ("I", n3), ("t_at", "ceilN2L"), ("t_at", n3)]].dropna()
        if not len(q):
            continue
        out.append(dict(n3_tag=n3, d=dd, networks=len(q), n2_E=q["E"]["ceilN2L"].median(), n3_E=q["E"][n3].median(),
                        n2_I=q["I"]["ceilN2L"].median(), n3_I=q["I"][n3].median(), n2_t=q["t_at"]["ceilN2L"].median(),
                        n3_t=q["t_at"][n3].median(), n3_lower_E=int((q["E"][n3] < q["E"]["ceilN2L"]).sum()),
                        n3_lower_I=int((q["I"][n3] < q["I"]["ceilN2L"]).sum())))
S = pd.DataFrame(out)
S.to_csv(HERE / "gapA2_bypass_matched_d_summary.csv", index=False)
pd.set_option("display.width", 250)
print(S.round(4).to_string())
