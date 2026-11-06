#!/usr/bin/env python3
"""
k-phi exponent test (5 Nov 2026): Phase 1 network P32 x6, sigma 1, seed 1, PERMEABILITY_POWER n = 3 (tag kphi_n3, ceiling
x1000) against the Phase 1 run on the same network (n = 1, ceiling x10).  Same measures and window as
scale2km/compare_scale.py: mechanism measures at every state, stage events and depth/inheritance within capacity time
<= 2 (the n = 3 runs end there), outlet window x > 400 m; k_eff gain from channelization.csv.

  python3 forsmark_reactive/kphi_n3_compare.py   -> phase1/kphi_n3_compare.csv
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "scale2km")]
from compare_scale import TCAP_MAX, chan, events, mech_2km  # noqa: E402

NET = HERE / "phase1" / "L2_r15_p6.0_sg1.0_seed1"
rows = []
for mdir, mode in (("gypsum", "gyponly"), ("gypsum_calcite", "gypcal")):
    for tag, n in (("phase1", 1), ("kphi_n3", 3)):
        run = NET / f"{mdir}__uncorrected_graph__{tag}"
        if not (run / "channelization.csv").exists():
            continue
        g = mech_2km(run, xout=400.0, use_cache=(tag != "phase1"))
        c = pd.read_csv(run / "channelization.csv")
        c = c[c.k.isin(g.k[g.t_cap <= TCAP_MAX])]
        rows.append(dict(mode=mode, n=n, **events(g), **chan(run, g), keff_gain_max=float(c.k_eff_ratio.max()),
                         t_cap_end=float(g.t_cap.max())))
out = pd.DataFrame(rows)
out.to_csv(HERE / "phase1" / "kphi_n3_compare.csv", index=False)
pd.set_option("display.width", 200)
print(out.round(3).to_string(index=False))
