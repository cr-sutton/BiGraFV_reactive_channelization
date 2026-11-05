#!/usr/bin/env python3
"""Phase 3 tests (5 Nov 2026).
Ceiling test: channel depth (min/start of pr_fracture_vol) at porosity 0.182 (gypsum-only ceiling x5.5, coupled x3.3)
against the same networks at porosity 0.1 (gypsum-only x10, coupled x5.5), sigma 1, seeds 1-3, P32 x4/x6/x8.
Rate test: stage events on the dissolved fraction, depth and inheritance at rate x0.1 and x10 against x1 (Phase 1), P32 x6,
sigma 1, seeds 1-3, both chemistries.  -> phase1/phase3_ceiling.csv, phase3_rate.csv; prints the tables.
  python3 forsmark_reactive/phase3_tests.py"""
import glob, re
from pathlib import Path
import numpy as np, pandas as pd
P1 = Path(__file__).resolve().parent / "phase1"
rows = []
for f in glob.glob(str(P1 / "L2_r15_p*_sg1.0_seed[123]/gyp*__*/channelization.csv")):
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)/(gyp\w+?)__uncorrected_graph__(\w+)/", f)
    if float(m[1]) > 8: continue
    d = pd.read_csv(f).sort_values("k")
    rows.append(dict(p32=float(m[1]), seed=int(m[3]), mode="gypcal" if "calcite" in m[4] else "gyponly", tag=m[5],
                     depth=float(d.pr_fracture_vol.min() / d.pr_fracture_vol.iloc[0]), inherit=float(d.overlap0[d.n90.idxmin()])))
c = pd.DataFrame(rows)
piv = c.pivot_table(index=["p32", "seed"], columns=["tag", "mode"], values="depth")
ce = pd.DataFrame({"gyp_x10_phi01": piv[("phase1", "gyponly")], "cal_x55_phi01": piv[("phase1", "gypcal")],
                   "gyp_x55_phi0182": piv[("phase3_phi0182", "gyponly")], "cal_x33_phi0182": piv[("phase3_phi0182", "gypcal")]}).dropna()
ce["d_gyp55_minus_cal55"] = ce.gyp_x55_phi0182 - ce.cal_x55_phi01
ce["d_gyp55_minus_gyp10"] = ce.gyp_x55_phi0182 - ce.gyp_x10_phi01
ce["d_cal33_minus_cal55"] = ce.cal_x33_phi0182 - ce.cal_x55_phi01
ce.to_csv(P1 / "phase3_ceiling.csv")
pd.set_option("display.width", 200)
print("CEILING (n =", len(ce), ")"); print(ce.round(3).to_string())
for k in ["d_gyp55_minus_cal55", "d_gyp55_minus_gyp10", "d_cal33_minus_cal55"]:
    v = ce[k]; print(f"  {k}: median {v.median():+.3f} [{v.quantile(.25):+.3f} {v.quantile(.75):+.3f}], |median| {v.abs().median():.3f}, max|| {v.abs().max():.3f}, positive {int((v>0).sum())}/{len(v)}")
print("  medians by ceiling:", {k: round(ce[k].median(), 3) for k in ["cal_x33_phi0182", "gyp_x55_phi0182", "cal_x55_phi01", "gyp_x10_phi01"]})
# rate test
e = pd.read_csv(P1 / "stage_events_clocks.csv")
e = e[(e.p32 == 6) & (e.sigma == 1) & (e.seed <= 3) & e.tag.isin(["phase1", "phase3_rate01", "phase3_rate10"])]
r = []
for (mode, seed), g in e.groupby(["mode", "seed"]):
    base = g[g.tag == "phase1"].set_index("event").dissolved
    for tag in ("phase3_rate01", "phase3_rate10"):
        x = g[g.tag == tag].set_index("event").dissolved
        for ev in base.index.intersection(x.index):
            r.append(dict(mode=mode, seed=seed, rate=tag, event=ev, d_x1=base[ev], d_rate=x[ev], diff=x[ev] - base[ev]))
cr = c[(c.p32 == 6)]
for tag in ("phase3_rate01", "phase3_rate10"):
    for mode in ("gyponly", "gypcal"):
        for s in (1, 2, 3):
            a = cr[(cr.tag == "phase1") & (cr["mode"] == mode) & (cr.seed == s)]; b = cr[(cr.tag == tag) & (cr["mode"] == mode) & (cr.seed == s)]
            if len(a) and len(b):
                r.append(dict(mode=mode, seed=s, rate=tag, event="depth", d_x1=a.depth.iloc[0], d_rate=b.depth.iloc[0], diff=b.depth.iloc[0] - a.depth.iloc[0]))
                r.append(dict(mode=mode, seed=s, rate=tag, event="inheritance", d_x1=a.inherit.iloc[0], d_rate=b.inherit.iloc[0], diff=b.inherit.iloc[0] - a.inherit.iloc[0]))
r = pd.DataFrame(r); r.to_csv(P1 / "phase3_rate.csv", index=False)
print("RATE: paired differences rate - x1 (3 networks per chemistry)")
print(r.groupby(["rate", "mode", "event"])["diff"].agg(["median", lambda v: v.abs().max(), "size"]).round(4).to_string())
