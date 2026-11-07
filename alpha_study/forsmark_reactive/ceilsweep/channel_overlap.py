#!/usr/bin/env python3
"""
Channel overlap across k-phi exponents (7 Nov 2026; story item 3).  For each of the 9 sweep networks and each chemistry:
A = peak-channel set of the n = 1 run (phase1; channel_fractures.csv, in_s90_peak = in the 90 %-flow set at its smallest),
B = the same set for the n = 1.48 / 2 / 3 run (ceilN148, ceilN2, ceilN3; kphi_n3 for P32 x6 seed 1 at n = 3).
  jac = |A∩B| / |A∪B|,  frac_n1_in_b = |A∩B| / |A|,  nb_over_na = |B| / |A|,  b_in_a = |A∩B| / |B|
Note: the peak sets come from the whole run (channel_fractures.csv is not cut at capacity time 2).
  python3 forsmark_reactive/ceilsweep/channel_overlap.py  -> ceilsweep/channel_overlap.csv
"""
from pathlib import Path

import pandas as pd

FR = Path(__file__).resolve().parents[1]
rows = []
for p in (4.0, 6.0, 8.0):
    for s in (1, 2, 3):
        for mdir, mo in (("gypsum", "gyponly"), ("gypsum_calcite", "gypcal")):
            base = FR / "phase1" / f"L2_r15_p{p}_sg1.0_seed{s}"
            a = set(pd.read_csv(base / f"{mdir}__uncorrected_graph__phase1" / "channel_fractures.csv").query("in_s90_peak").fracture)
            for tag in ("ceilN148", "ceilN2", "ceilN3", "kphi_n3"):
                f = base / f"{mdir}__uncorrected_graph__{tag}" / "channel_fractures.csv"
                if not f.exists():
                    continue
                b = set(pd.read_csv(f).query("in_s90_peak").fracture)
                rows.append(dict(p32=p, seed=s, mode=mo, tag=tag, n_a=len(a), n_b=len(b), jac=len(a & b) / len(a | b),
                                 frac_n1_in_b=len(a & b) / len(a), nb_over_na=len(b) / len(a), b_in_a=len(a & b) / len(b)))
J = pd.DataFrame(rows)
J.to_csv(FR / "ceilsweep" / "channel_overlap.csv", index=False)
J["n"] = J.tag.map({"ceilN148": "1.48", "ceilN2": "2", "ceilN3": "3", "kphi_n3": "3"})
print(J.groupby(["mode", "n"])[["b_in_a", "nb_over_na"]].agg(["median", "min", "max", "size"]).round(3))
