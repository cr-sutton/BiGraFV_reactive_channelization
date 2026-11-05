#!/usr/bin/env python3
"""
Gate summary for the rFram candidates (5 Nov 2026).  Baseline: each Phase 1 x4 sigma 1 network scored against the other four
(leave-one-out; how many of the 16 measures fall inside their min-max) - the same test the rFram networks get.  Also each rFram
network against all 15 Phase 1 x4 networks (sigma 0, 0.5, 1).  Measures as gate_check.py.
  python3 forsmark_reactive/dfn_validation/gate_summary.py  -> dfn_validation/gate_summary.csv
"""
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; P1 = HERE.parent / "phase1"
M = ["PRpore_min", "PRV_min", "outlet5", "breakthrough", "depth", "inheritance", "n90_min_rel", "prv0"]
e = pd.read_csv(P1 / "stage_events_clocks.csv")
def chan(r):
    d = pd.read_csv(r / "channelization.csv").sort_values("k")
    return dict(depth=d.pr_fracture_vol.min() / d.pr_fracture_vol.iloc[0], inheritance=d.overlap0[d.n90.idxmin()],
                n90_min_rel=d.n90.min() / d.n90.iloc[0], prv0=d.pr_fracture_vol.iloc[0])
R = pd.DataFrame([dict(sigma=sg, seed=sd, mode=mo, **e[(e.tag == "phase1") & (e["mode"] == mo) & (e.p32 == 4.0) & (e.sigma == sg) & (e.seed == sd)]
                       .set_index("event").dissolved.to_dict(), **chan(P1 / f"L2_r15_p4.0_sg{sg}_seed{sd}" / f"{md}__uncorrected_graph__phase1"))
                  for sg in (0.0, 0.5, 1.0) for sd in range(1, 6) for mo, md in (("gyponly", "gypsum"), ("gypcal", "gypsum_calcite"))])
rows = []
for sd in range(1, 6):
    n = sum(R[(R.sigma == 1) & (R["mode"] == mo) & (R.seed != sd)][m].between(-1, 9).any() and
            R[(R.sigma == 1) & (R["mode"] == mo) & (R.seed != sd)][m].min() <= R[(R.sigma == 1) & (R["mode"] == mo) & (R.seed == sd)][m].iloc[0]
            <= R[(R.sigma == 1) & (R["mode"] == mo) & (R.seed != sd)][m].max() for mo in ("gyponly", "gypcal") for m in M)
    rows.append(dict(network=f"Phase 1 x4 sigma 1 seed {sd} (leave-one-out)", inside_sigma1=n, inside_all_x4=None, outside_all_x4=""))
for s in (1, 2, 3):
    g = pd.read_csv(HERE / f"rf_p4.0_sg1.0_seed{s}" / "gate_check.csv")
    out = [f"{r['mode']} {r.measure} {r.rfram:.3f}" for _, r in g.iterrows()
           if not R[R["mode"] == r["mode"]][r.measure].min() <= r.rfram <= R[R["mode"] == r["mode"]][r.measure].max()]
    rows.append(dict(network=f"rFram seed {s}", inside_sigma1=int(g.inside.sum()), inside_all_x4=16 - len(out), outside_all_x4="; ".join(out)))
S = pd.DataFrame(rows); S.to_csv(HERE / "gate_summary.csv", index=False); print(S.to_string(index=False))
