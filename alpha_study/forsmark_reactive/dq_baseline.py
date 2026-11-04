#!/usr/bin/env python3
"""
Why published d_Q/P32 falls with P32 while PR_V rises: d_Q/P32 = (sum S Q)^2 / (sum S . sum S Q^2) equals 1 only when every
fracture carries the SAME flow (Cauchy-Schwarz), whatever its size; PR_V equals 1 when flow is proportional to volume.
Per Phase 1 network (initial state, gyponly run; the initial flow is the same for both chemistries) -> phase1/dq_baseline.csv:
  dQ_P32_actual        100 d_Q/P32 of the initial flow (as patterns.csv)
  dQ_P32_if_Q_prop_V   100 d_Q/P32 if each fracture's flow were proportional to its volume (PR_V = 1)
  dQ_P32_if_Q_prop_S   the same with flow proportional to area
  prv_actual           PR_V of the initial flow
  python3 forsmark_reactive/dq_baseline.py
"""
import glob, re, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parent / "physics_upscaling")]
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

dq = lambda S, Q: 100 * (S * Q).sum() ** 2 / (S.sum() * (S * Q ** 2).sum())
prv = lambda Q, V: (Q.sum() ** 2) / (Q ** 2 / (V / V.sum())).sum()
rows = []
for f in sorted(glob.glob(str(HERE / "phase1/L2_r15_p*_sg*_seed*/gypsum__uncorrected_graph__phase1/channel_fractures.csv"))):
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", f)
    if float(m[1]) > 8:
        continue
    fr = pd.read_csv(f)
    S, Q = fr.area.to_numpy(float), fr.Q0.to_numpy(float)
    V = read_uge(Path(f).parent / "full_mesh_vol_area.uge")[0][: len(fr), 4].astype(float)
    rows.append(dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), n_fractures=len(fr), dQ_P32_actual=dq(S, Q),
                     dQ_P32_if_Q_prop_V=dq(S, V), dQ_P32_if_Q_prop_S=dq(S, S), prv_actual=prv(Q, V),
                     dQ_actual_over_V_baseline=dq(S, Q) / dq(S, V)))
d = pd.DataFrame(rows)
d.to_csv(HERE / "phase1/dq_baseline.csv", index=False)
q = lambda s: f"{s.median():.3g} [{s.quantile(.25):.3g}-{s.quantile(.75):.3g}]"
print(d.groupby("p32").agg(n=("seed", "size"), dQ_actual=("dQ_P32_actual", q), dQ_if_prop_V=("dQ_P32_if_Q_prop_V", q),
                           dQ_if_prop_S=("dQ_P32_if_Q_prop_S", q), ratio=("dQ_actual_over_V_baseline", q), PR_V=("prv_actual", q)).to_string())
