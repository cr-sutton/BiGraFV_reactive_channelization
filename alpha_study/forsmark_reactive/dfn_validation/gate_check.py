#!/usr/bin/env python3
"""
DFN-validation stage 0 gate (5 Nov 2026): does the rFram network's one-cell run sit inside the Phase 1 envelope (P32 x4, sigma 1,
seeds 1-5, same chemistry and deck)?  Same measures as the report: stage events on the dissolved fraction (PR_pore minimum,
outlet 5 %, PR_V minimum, breakthrough; analyze_phase1_mechanism.one, events within t_cap <= 3 as stage_events_clocks.py),
depth = PR_V min / start and inheritance = overlap0 at the n90 minimum (channelization.csv).
  python3 forsmark_reactive/dfn_validation/gate_check.py  -> dfn_validation/rf_p4.0_sg1.0_seed1/gate_check.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FR = HERE.parent
sys.path[:0] = [str(FR), str(FR.parent), str(FR.parent / "physics_upscaling")]
from analyze_phase1_mechanism import one  # noqa: E402

NET = HERE / "rf_p4.0_sg1.0_seed1"
P1 = FR / "phase1"


def events(rows):
    g = pd.DataFrame(rows).sort_values("k").reset_index(drop=True)
    g = g[g.t_cap <= 3.0].reset_index(drop=True)
    ev = {"PRpore_min": g.pr_pore.idxmin(), "PRV_min": g.pr_frac.idxmin()}
    o = g.index[g.outlet_diss > 0.05]; ev["outlet5"] = o[0] if len(o) else None
    o = g.index[g.outlet_diss >= 0.5]; ev["breakthrough"] = o[0] if len(o) else None
    return {e: (float(g.dissolved[i]) if i is not None else np.nan) for e, i in ev.items()}


def chan(run):
    d = pd.read_csv(run / "channelization.csv").sort_values("k")
    return dict(depth=float(d.pr_fracture_vol.min() / d.pr_fracture_vol.iloc[0]), inheritance=float(d.overlap0[d.n90.idxmin()]),
                n90_min_rel=float(d.n90.min() / d.n90.iloc[0]), prv0=float(d.pr_fracture_vol.iloc[0]))


rows = []
e = pd.read_csv(P1 / "stage_events_clocks.csv")
for mode, mdir in (("gyponly", "gypsum"), ("gypcal", "gypsum_calcite")):
    r = NET / f"{mdir}__uncorrected_graph__dfnval"
    new = {**events(one(r)), **chan(r)}
    ref = []
    for seed in range(1, 6):
        rr = P1 / f"L2_r15_p4.0_sg1.0_seed{seed}" / f"{mdir}__uncorrected_graph__phase1"
        x = e[(e.tag == "phase1") & (e["mode"] == mode) & (e.p32 == 4.0) & (e.sigma == 1.0) & (e.seed == seed)].set_index("event").dissolved.to_dict()
        ref.append({**x, **chan(rr)})
    ref = pd.DataFrame(ref)
    for k, v in new.items():
        lo, hi = ref[k].min(), ref[k].max()
        rows.append(dict(mode=mode, measure=k, rfram=v, phase1_min=lo, phase1_median=ref[k].median(), phase1_max=hi,
                         inside=bool(lo <= v <= hi), n_ref=int(ref[k].notna().sum())))
out = pd.DataFrame(rows)
out.to_csv(NET / "gate_check.csv", index=False)
pd.set_option("display.width", 200)
print(out.round(3).to_string(index=False))
