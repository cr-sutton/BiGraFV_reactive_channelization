#!/usr/bin/env python3
"""
Numbers for the colloquium deck (deck/build_deck.js), computed from the same CSVs as the report, so the deck can be rebuilt
1:1 whenever the report changes.  -> deck/numbers.json

  python3 forsmark_reactive/deck/deck_numbers.py
"""
import glob, json, re
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
P1 = HERE.parent / "phase1"
med = lambda s: float(np.median(s))
iqr = lambda s: [float(np.quantile(s, .25)), float(np.quantile(s, .75))]
out = {}

# runs and networks
ch = []
for f in sorted(glob.glob(str(P1 / "L2_r15_p*_sg*_seed*/gyp*__*/channelization.csv"))):
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)/(gyp\w+?)__uncorrected_graph__(\w+)/", f)
    d = pd.read_csv(f).sort_values("k")
    k_n90 = d.n90.idxmin()
    ch.append(dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode="gypcal" if "calcite" in m[4] else "gyponly", tag=m[5],
                   depth=float(d.pr_fracture_vol.min() / d.pr_fracture_vol.iloc[0]), inherit=float(d.overlap0[k_n90]),
                   n_fr=None))
ch = pd.DataFrame(ch)
p1 = ch[ch.tag == "phase1"]   # x4-x16 pooled since 5 Nov (user: include the x16 data everywhere)
out["n_phase1_runs"] = int(len(p1)); out["n_phase1_networks"] = int(len(p1[p1["mode"] == "gyponly"]))
out["n_x16_runs"] = int(len(ch[(ch.tag == "phase1") & (ch.p32 == 16)]))
stats = [json.loads(Path(f).read_text()) for f in glob.glob(str(P1 / "L2_r15_p*_sg*_seed*/network_stats.json"))]
nf = {}
for f in glob.glob(str(P1 / "L2_r15_p*_sg*_seed*/gypsum__uncorrected_graph__phase1/channel_fractures.csv")):
    p = float(re.search(r"_p([\d.]+)_", f)[1]); nf.setdefault(p, []).append(sum(1 for _ in open(f)) - 1)
out["fractures_by_p32"] = {f"{k:g}": [min(v), max(v)] for k, v in sorted(nf.items())}

# inheritance at the n90 minimum, Phase 1
out["inheritance"] = {m: dict(median=med(g.inherit), min=float(g.inherit.min()), max=float(g.inherit.max()), n=int(len(g)))
                      for m, g in p1.groupby("mode")}
co3lo = ch[ch.tag == "phase2_co3lo"]
out["inheritance_2mM"] = dict(min=float(co3lo.inherit.min()), max=float(co3lo.inherit.max()), n=int(len(co3lo)))

# channel depth: Phase 1 by chemistry; matched table; paired differences
out["depth_phase1"] = {m: dict(median=med(g.depth), iqr=iqr(g.depth), n=int(len(g))) for m, g in p1.groupby("mode")}
mt = ch[(ch.sigma == 1.0) & (ch.seed <= 3)]
cases = {"x10 gypsum-only (P1)": ("phase1", "gyponly", 10), "x10.6 coupled phi0 0.05 (P2)": ("phase2_phi005", "gypcal", 10.6),
         "x10 coupled 2 mM (P2)": ("phase2_co3lo", "gypcal", 10), "x5.5 coupled 0.5 M (P1)": ("phase1", "gypcal", 5.5),
         "x20 gypsum-only phi0 0.05 (P2)": ("phase2_phi005", "gyponly", 20)}
out["depth_matched"] = {k: dict(ceiling=c, by_p32={f"{p:g}": med(g.depth) for p, g in mt[(mt.tag == t) & (mt["mode"] == m)].groupby("p32")})
                        for k, (t, m, c) in cases.items()}
piv = ch.pivot_table(index=["p32", "sigma", "seed"], columns=["tag", "mode"], values="depth")
d55 = (piv[("phase1", "gypcal")] - piv[("phase1", "gyponly")]).dropna()
d20 = (piv[("phase2_phi005", "gyponly")] - piv[("phase1", "gyponly")]).dropna()
d106 = (piv[("phase2_phi005", "gypcal")] - piv[("phase1", "gyponly")]).dropna().abs()
d2 = (piv[("phase2_co3lo", "gypcal")] - piv[("phase1", "gyponly")]).dropna().abs()
out["depth_paired"] = dict(x55_minus_x10=dict(median=med(d55), n=int(len(d55)), all_positive=bool((d55 > 0).all())),
                           x20_minus_x10=dict(min=float(d20.min()), max=float(d20.max()), n=int(len(d20)), all_negative=bool((d20 < 0).all())),
                           x106_vs_x10=dict(median_abs=med(d106), max_abs=float(d106.max()), n=int(len(d106))),
                           co3lo_vs_gyponly=dict(median_abs=med(d2), max_abs=float(d2.max()), n=int(len(d2))))

# stage events on the main clock (Phase 1) and the paired gaps
e = pd.read_csv(P1 / "stage_events_clocks.csv")
e1 = e[e.tag == "phase1"]
out["stages"] = {ev: {m: dict(median=med(g.dissolved), iqr=iqr(g.dissolved), t_cap=med(g.t_cap), n=int(len(g)))
                      for m, g in e1[e1.event == ev].groupby("mode")} for ev in ["PRpore_min", "outlet5", "PRV_min", "breakthrough"]}
pv = e1.pivot_table(index=["p32", "sigma", "seed", "event"], columns="mode", values=["dissolved", "t_cap"])
out["stage_gaps"] = {ev: dict(d=med((pv[("dissolved", "gypcal")] - pv[("dissolved", "gyponly")]).xs(ev, level="event")),
                              t_cap=med((pv[("t_cap", "gypcal")] - pv[("t_cap", "gyponly")]).xs(ev, level="event")))
                     for ev in ["PRV_min", "breakthrough"]}
e48 = e[(e.tag == "phase1") & (e.p32 <= 8)]   # x4-x8 only, for the x16 comparison slide
out["stages_x4x8"] = {ev: {m: dict(median=med(g.dissolved), n=int(len(g))) for m, g in e48[e48.event == ev].groupby("mode")}
                      for ev in ["PRpore_min", "outlet5", "PRV_min", "breakthrough"]}
er = pd.read_csv(P1 / "early_redistribution_summary.csv")
gv = lambda ds, item: float(er[(er.dstar == ds) & (er.scope == "pooled") & (er.item == item)].value.iloc[0])
out["early"] = dict(rho10=gv(0.10, "spearman resid vs dPRV_w"), r2_10=gv(0.10, "LOPO R2 (dPRV_w only)"), r2_05=gv(0.05, "LOPO R2 (dPRV_w only)"),
                    n10=int(gv(0.10, "n runs with minimum after d*")))
DV = HERE.parent / "dfn_validation" / "rf_p4.0_sg1.0_seed1"
if (DV / "gypsum__dfn__smoke" / "smoke.json").exists():
    sm = {m: json.loads((DV / f"{d}__dfn__smoke" / "smoke.json").read_text()) for m, d in (("gyponly", "gypsum"), ("gypcal", "gypsum_calcite"))}
    bsum = json.loads((DV / "build_summary.json").read_text())
    steps = dict(gypcal_tcap2=908, gyponly_tcap1=12885, gyponly_tcap2=25703)   # graph step counts on this network (gate runs)
    out["dfn"] = dict(cells=bsum["dfn_cells"], q_ratio=bsum["Q_ratio_dfn_graph"], s_step={m: v["s_per_step_2nd_half"] for m, v in sm.items()},
                      rss={m: v["peak_rss_GB"] for m, v in sm.items()},
                      wall_h=dict(gypcal_tcap2=steps["gypcal_tcap2"] * sm["gypcal"]["s_per_step_2nd_half"] / 3600,
                                  gyponly_tcap1=steps["gyponly_tcap1"] * sm["gyponly"]["s_per_step_2nd_half"] / 3600,
                                  gyponly_tcap2=steps["gyponly_tcap2"] * sm["gyponly"]["s_per_step_2nd_half"] / 3600))
gr = pd.read_csv(P1 / "gypsum_reprecipitation.csv"); grc = gr[(gr.tag == "phase1") & (gr["mode"] == "gypsum_calcite")]
out["reprecip"] = dict(n=int(len(grc)), runs_gain=int((grc.n_gyp_up > 0).sum()), runs_floor=int((grc.n_floor > 0).sum()),
                       floor_max=int(grc.n_floor_ever.max()), q_floor_max=float(grc.q_floor_max.max()))
mech = pd.read_csv(P1 / "phase1_mechanism_summary.csv")
mech = mech[mech.tag == "phase1"]
out["breakthrough_dissolved_by_mode"] = {m: dict(p32_medians=[med(gg.dissolved_at_outlet50.dropna()) for _, gg in g.groupby("p32")],
                                                 run_min=float(g.dissolved_at_outlet50.min()), run_max=float(g.dissolved_at_outlet50.max()))
                                         for m, g in mech.groupby("mode")}

# transport (fine probes): start, channel peak, end
t = pd.read_csv(P1 / "phase1_tracer.csv")
tr = {}
for m, tc in [("gyponly", 0.5), ("gypcal", 0.63)]:
    s = t[t["mode"] == m]
    g = s.groupby(["p32", "sigma", "seed"])
    start = s[s.k == 0]
    peak = s.loc[[gg.index[(np.log(gg.t_cap.clip(1e-9)) - np.log(tc)).abs().argmin()] for _, gg in g]]
    end = s.sort_values("t_y").groupby(["p32", "sigma", "seed"]).tail(1)
    tr[m] = {name: dict(t50_res=med(x.t50_res), gamma=med(x.gamma), alpha_L=med(x.alpha_L), diss=med(x.diss), n=int(len(x)))
             for name, x in [("start", start), ("peak", peak), ("end", end)]}
out["transport"] = tr

# d_Q baseline
b = pd.read_csv(P1 / "dq_baseline.csv")
out["dq_baseline"] = {f"{p:g}": dict(actual=med(g.dQ_P32_actual), if_prop_V=med(g.dQ_P32_if_Q_prop_V), prv=med(g.prv_actual), n=int(len(g)))
                      for p, g in b.groupby("p32")}

# P32 x16 (Phase 1): stage events, depth, inheritance, start levels
x16e = e[(e.tag == "phase1") & (e.p32 == 16)]
x16 = ch[(ch.tag == "phase1") & (ch.p32 == 16)]
out["x16"] = dict(stages={ev: {m: dict(median=med(g.dissolved), iqr=iqr(g.dissolved), n=int(len(g))) for m, g in x16e[x16e.event == ev].groupby("mode")}
                          for ev in ["PRpore_min", "PRV_min", "breakthrough"]},
                  depth={m: dict(median=med(g.depth), n=int(len(g))) for m, g in x16.groupby("mode")},
                  inheritance={m: dict(median=med(g.inherit), min=float(g.inherit.min())) for m, g in x16.groupby("mode")},
                  depth_gap=med((piv[("phase1", "gypcal")] - piv[("phase1", "gyponly")]).dropna().xs(16.0, level=0)))
# paused-pulse trace (example network)
out["pulse"] = {}
for m, ks in (("gyponly", [0, 35, 42, 47, 55]), ("gypcal", [0, 12, 18, 23, 30])):
    t = pd.read_csv(P1 / "figures" / "anim3" / f"transport_trace_{m}.csv").set_index("k")
    out["pulse"][m] = [dict(k=k, diss=float(t.loc[k, "diss"]), tau=float(t.loc[k, "tau_res_y"]), t50=float(t.loc[k, "t50_res"])) for k in ks]
# wormhole regime map and bound
rs = pd.read_csv(P1 / "wormhole_regime_summary.csv")
rp = rs[(rs.level != "network") & (rs.k_choice == "R")]
out["regime"] = {f"{r.P32:g}": dict(wormhole=float(r.flow_wormhole), compact=float(r.flow_compact), uniform=float(r.flow_uniform),
                                    validated=float(r.flow_in_validated), Pe=float(r.Pe_p50), Da=float(r.Da_effL_p50)) for r in rp.itertuples()}
wb = pd.read_csv(P1 / "wormhole_bound.csv"); wb8 = wb   # x4-x16
out["bound"] = {m: {f"{f:g}": dict(D_lo=med(g.D_lo), D_hi=med(g.D_hi)) for f, g in gm.groupby("f")} for m, gm in wb8.groupby("mode")}
w1 = wb8[wb8.f == 1.0]
out["bound_channel_share"] = med(w1.D_ch / w1.D_bt)
# olivine exploration
ol = pd.read_csv(HERE.parent / "explore_olivine" / "L2_r15_p6.0_sg1.0_seed1" / "olivine__uncorrected_graph__explore" / "clogging.csv")
out["olivine"] = dict(k_eff_end=float(ol.k_eff_ratio.iloc[-1]), floor_end=int(ol.n_at_floor.iloc[-1]), overlap_min_after10=float(ol[ol.t_y >= 10].overlap0.min()),
                      overlap_end=float(ol.overlap0.iloc[-1]), n90_0=int(ol.n90.iloc[0]), n90_max=int(ol.n90.max()))

# manuscript analyses (section 8)
bs = pd.read_csv(P1 / "breakthrough_predictor_summary.csv")
g = lambda chem, subset: bs[(bs.target == "d_bt") & (bs.scope == "chem") & (bs.model == "S_top1_share") & (bs.subset == subset) & (bs.chem == chem)].iloc[0]
out["predictor"] = dict(r2_gyp=float(g("gyponly", "overall").R2), r2_cal=float(g("gypcal", "overall").R2), rho=float(g("all", "overall").spearman),
                        oos_r2=float(g("all", "oos_phase2_all").R2), oos_rho=float(g("all", "oos_phase2_all").spearman))
tl = pd.read_csv(P1 / "transport_channel_link.csv")
from scipy.stats import spearmanr
out["transport_link"] = dict(rho_gamma_prv=float(spearmanr(tl.rgamma, tl.PRV_rel).correlation))
tc = pd.read_csv(P1 / "channel_turnover_counts.csv")
out["turnover"] = dict(leaver_share=med(tc.leaver_share_of_start), joiner_share=med(tc.joiner_share_of_peak), n=int(len(tc)))
dv = pd.read_csv(P1 / "depth_variability.csv"); pp = dv[dv.tag == "phase1"].pivot_table(index=["P32", "sigma", "seed"], columns="mode", values="depth").dropna()
out["depth_rank_rho"] = float(spearmanr(pp.gypsum, pp.gypsum_calcite).correlation)

# Phase 3 ceiling and rate tests
c3 = pd.read_csv(P1 / "phase3_ceiling.csv")
out["ceiling"] = dict(gyp55_minus_cal55=med(c3.d_gyp55_minus_cal55), max_abs=float(c3.d_gyp55_minus_cal55.abs().max()),
                      gyp55_minus_gyp10=med(c3.d_gyp55_minus_gyp10), cal33_minus_cal55=med(c3.d_cal33_minus_cal55), n=int(len(c3)),
                      depth_x33=med(c3.cal_x33_phi0182), depth_x55_gyp=med(c3.gyp_x55_phi0182))
r3 = pd.read_csv(P1 / "phase3_rate.csv")
pr3 = r3.pivot_table(index=["mode", "seed", "event"], columns="rate", values="d_rate")
dd = (pr3.phase3_rate10 - pr3.phase3_rate01).abs().reset_index(name="d")
ev = dd[dd.event.isin(["PRV_min", "outlet5", "breakthrough"])]
out["rate"] = dict(gyp_max=float(dd[dd["mode"] == "gyponly"].d.max()), cal_events_max=float(ev[ev["mode"] == "gypcal"].d.max()),
                   cal_depth_max=float(dd[(dd["mode"] == "gypcal") & (dd.event == "depth")].d.max()), n=3)
(HERE / "numbers.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1)[:4000])
