#!/usr/bin/env python3
"""
Channel identity per network (rebuilt 5 Nov 2026 as a script; the earlier phase1_channel_identity.csv was made ad hoc for
P32 x4-x8 only).  From channel_fractures.csv of the gypsum-only and coupled run on the same network:
  S0 = initial 90 %-flow set (in_s90_start), S_peak = 90 %-flow set at the n90 minimum (in_s90_peak)
  overlap0          |S_peak & S0| / |S_peak|          new_channel_frac = 1 - overlap0
  flow_in_initial   sum Q_peak over S0 / sum Q_peak over all fractures (share of the peak-state flow in the initial set; 0.90 at the start)
  jaccard_gyp_cal   |S_peak,gyp & S_peak,cal| / |S_peak,gyp | S_peak,cal|
  python3 forsmark_reactive/channel_identity.py [TAG ...]   (default phase1)  -> phase1/<tag>_channel_identity.csv
"""
import re, sys
from pathlib import Path
import pandas as pd
P1 = Path(__file__).resolve().parent / "phase1"

def one(r):
    c = pd.read_csv(r / "channel_fractures.csv"); s0, sp = c.in_s90_start.astype(bool), c.in_s90_peak.astype(bool)
    ov = (sp & s0).sum() / sp.sum()
    return dict(n90_start=int(s0.sum()), n90_peak=int(sp.sum()), overlap0=ov, new_channel_frac=1 - ov,
                flow_in_initial_set=c.Q_peak[s0].sum() / c.Q_peak.sum()), set(c.fracture[sp])

for tag in (sys.argv[1:] or ["phase1"]):
    rows = []
    for d in sorted(P1.glob("L2_r15_p*_sg*_seed*")):
        m = re.match(r"L2_r15_p([\d.]+)_sg([\d.]+)_seed(\d+)", d.name)
        row = dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3])); sets = {}
        for mode, k in (("gypsum", "gyp"), ("gypsum_calcite", "cal")):
            r = d / f"{mode}__uncorrected_graph__{tag}"
            if (r / "channel_fractures.csv").exists():
                v, sets[k] = one(r); row["n90_start"] = v.pop("n90_start"); row["n90_peak_" + k] = v.pop("n90_peak")
                row.update({f"{a}_{k}": b for a, b in v.items()})
        if len(sets) == 2:
            row["jaccard_gyp_cal"] = len(sets["gyp"] & sets["cal"]) / len(sets["gyp"] | sets["cal"])
        if sets: rows.append(row)
    pd.DataFrame(rows).to_csv(P1 / f"{tag}_channel_identity.csv", index=False)
    print(tag, len(rows))
