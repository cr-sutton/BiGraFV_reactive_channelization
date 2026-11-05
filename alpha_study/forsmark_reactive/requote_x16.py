#!/usr/bin/env python3
"""Re-quote of the report's Phase 1 pooled numbers with P32 x16 included (5 Nov 2026): every statistic is printed for the old
set (P32 x4-x8, n = 45 per chemistry) and the new set (x4-x16, n = 60), so each replacement can be checked against the old text.
  python3 forsmark_reactive/requote_x16.py  -> phase1/requote_x16.txt"""
import numpy as np, pandas as pd
from pathlib import Path
P1 = Path(__file__).resolve().parent / "phase1"
q = lambda s, f="{:.3f}": f"{f.format(s.median())} [{f.format(s.quantile(.25))}-{f.format(s.quantile(.75))}]"
e = pd.read_csv(P1 / "stage_events_clocks.csv"); m = pd.read_csv(P1 / "phase1_mechanism.csv")
dv = pd.read_csv(P1 / "depth_variability.csv"); wb = pd.read_csv(P1 / "wormhole_bound.csv")
out = []
P = lambda *a: out.append(" ".join(str(x) for x in a))
for name, sel in (("x4-x8", lambda d: d.p32 <= 8), ("x4-x16", lambda d: d.p32 > 0)):
    P(f"\n##### {name}")
    E1 = e[(e.tag == "phase1") & sel(e)]
    for ev in ("PRpore_min", "outlet5", "PRV_min", "breakthrough"):
        for mode in ("gyponly", "gypcal"):
            g = E1[(E1.event == ev) & (E1["mode"] == mode)]
            P(f"stage {ev:13s} {mode:8s} n={len(g)} d={q(g.dissolved, '{:.2f}')} tcap={q(g.t_cap, '{:.2f}')} d/tcap={q(g.dissolved / g.t_cap)}")
    pv = E1.pivot_table(index=["p32", "sigma", "seed", "event"], columns="mode", values=["dissolved", "t_cap"])
    for ev in ("PRpore_min", "PRV_min", "outlet5", "breakthrough"):
        for c in ("t_cap", "dissolved"):
            x = (pv[(c, "gypcal")] - pv[(c, "gyponly")]).xs(ev, level="event").dropna()
            P(f"gap {ev:13s} {c:9s} n={len(x)} {q(x)} positive={(x > 0).sum()}")
    # stage 3 details
    M = m[(m.tag == "phase1") & sel(m)]
    pos = []; prv_before5 = []; prv_le_bt = []
    for key, g in M.groupby(["mode", "p32", "sigma", "seed"]):
        g = g.sort_values("k").reset_index(drop=True); g = g[g.t_cap <= 3].reset_index(drop=True)
        ip = g.pr_frac.idxmin(); o5 = g.index[g.outlet_diss > 0.05]; bt = g.index[g.outlet_diss >= 0.5]
        if len(bt): pos.append(g.pr_pore[bt[0]] / g.pr_pore[0]); prv_le_bt.append(ip <= bt[0])
        if len(o5): prv_before5.append(ip < o5[0])
    P(f"PRpore at bt / start {q(pd.Series(pos), '{:.2f}')} ; PRV min before outlet5 {np.mean(prv_before5):.2f} ; PRV min <= bt {np.mean(prv_le_bt):.3f} (n {len(prv_le_bt)})")
    B = E1[E1.event == "breakthrough"]
    for mode in ("gyponly", "gypcal"):
        g = B[B["mode"] == mode]; P(f"bt dissolved {mode} per-P32 medians {g.groupby('p32').dissolved.median().round(3).to_dict()} runs {g.dissolved.min():.3f}-{g.dissolved.max():.3f}")
    # depth pairs
    D = dv[sel(dv.rename(columns={'P32': 'p32'}))].copy()
    piv = D.pivot_table(index=["P32", "sigma", "seed"], columns=["tag", "mode"], values="depth")
    def pr(a, b, absol=False):
        x = (piv[a] - piv[b]).dropna(); x = x.abs() if absol else x
        return f"n={len(x)} median {x.median():+.3f} min {x.min():+.3f} max {x.max():+.3f} pos {(x > 0).sum()}"
    P("depth x5.5-x10 P1:", pr(("phase1", "gypsum_calcite"), ("phase1", "gypsum")))
    P("depth x20-x10:", pr(("phase2_phi005", "gypsum"), ("phase1", "gypsum")))
    P("depth |x10.6-x10|:", pr(("phase2_phi005", "gypsum_calcite"), ("phase1", "gypsum"), True))
    P("depth |2mM-x10|:", pr(("phase2_co3lo", "gypsum_calcite"), ("phase1", "gypsum"), True))
    eq = pd.concat([(piv[("phase2_phi005", "gypsum_calcite")] - piv[("phase1", "gypsum")]).dropna().abs(), (piv[("phase2_co3lo", "gypsum_calcite")] - piv[("phase1", "gypsum")]).dropna().abs()])
    P(f"equal ceilings pooled |diff| median {eq.median():.3f} max {eq.max():.3f} n {len(eq)}")
    W = wb[sel(wb)]
    for mode in ("gyponly", "gypcal"):
        for f, g in W[W["mode"] == mode].groupby("f"):
            cols = [c for c in g.columns if c.startswith(("D_", "T_", "t_"))]
            P(f"bound {mode} f={f:g} n={len(g)} " + " ".join(f"{c}={g[c].median():.3f}" for c in cols))
(P1 / "requote_x16.txt").write_text("\n".join(out)); print("\n".join(out))
