#!/usr/bin/env python3
"""
Link between frozen-state tracer metrics and channel measures (Phase 1, P32 x4-x8, the states probed in phase1_tracer.csv).

Merge: phase1_tracer.csv with phase1_mechanism.csv (tag phase1) on (p32, sigma, seed, mode, k).  Per probed state:
  PRV_rel   = pr_frac / pr_frac(k=0)         PR_V / PR_V0
  PRp_rel   = pr_pore / pr_pore(k=0)         PR_pore / PR_pore0
  decoup    = pr_pore / pr_frac              decoupling ratio PR_pore / PR_V
  dlnPRV    = ln PRV_rel,  dlnPRp = ln PRp_rel
  for X in t50_res, gamma, alpha_L:  dX = X - X(k=0) (difference), rX = X / X(k=0) (ratio), of the same run.
  (t50_res = t50 / tau_res, alpha_L = D_L / v in m; definitions in analyze_phase1_tracer.py.)
Analyses (summary kinds):
  pooled_spearman      Spearman rho between each tracer measure (X, dX, rX) and each channel measure over all probed states
                       (k = 0 included: dX = 0, rX = 1 there; n = 720 pooled, 360 per chemistry)
  within_run_spearman  same per run (6 states each); median, q25, q75 of rho over the 120 runs, per chemistry
  linear_model         per chemistry, OLS with intercept:  dX ~ dlnPRV + dlnPRp   (additive) and  + dlnPRV*dlnPRp
                       (interaction), for X = t50_res, gamma, alpha_L; coefficients, in-sample R2, leave-one-P32-level-out
                       R2 (3 levels: train on two, predict the third; R2 about the held-out mean, pooled over folds as
                       1 - sum SS_res / sum SS_tot_fold) and the per-level values.
  python3 forsmark_reactive/transport_channel_link.py
  -> phase1/transport_channel_link.csv, phase1/transport_channel_link_summary.csv,
     phase1/figures/manuscript/transport_channel_link.png, transport_channel_link_by_chemistry.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
P1 = HERE / "phase1"
FIG = P1 / "figures" / "manuscript"
FIG.mkdir(parents=True, exist_ok=True)
KEY = ["p32", "sigma", "seed", "mode"]
COL = {4.0: "#86b6ef", 6.0: "#2a78d6", 8.0: "#104281"}
INK, INK2, GRID = "#16181a", "#4c5157", "#e6e5e1"
XS = ["t50_res", "gamma", "alpha_L"]
CHAN = ["PRV_rel", "PRp_rel", "decoup", "dlnPRV", "dlnPRp"]
MK = {"gyponly": "o", "gypcal": "^"}


def build():
    t = pd.read_csv(P1 / "phase1_tracer.csv")
    m = pd.read_csv(P1 / "phase1_mechanism.csv")
    m = m[m.tag == "phase1"][KEY + ["k", "pr_frac", "pr_pore", "dissolved"]]
    d = t.merge(m, on=KEY + ["k"], how="left", validate="one_to_one")
    assert d.pr_frac.notna().all()
    d = d.sort_values(KEY + ["k"]).reset_index(drop=True)
    g = d.groupby(KEY)
    d["PRV_rel"] = d.pr_frac / g.pr_frac.transform("first")
    d["PRp_rel"] = d.pr_pore / g.pr_pore.transform("first")
    d["decoup"] = d.pr_pore / d.pr_frac
    d["dlnPRV"] = np.log(d.PRV_rel)
    d["dlnPRp"] = np.log(d.PRp_rel)
    for x in XS:
        d["d" + x] = d[x] - g[x].transform("first")
        d["r" + x] = d[x] / g[x].transform("first")
    return d.rename(columns={"pr_frac": "PR_V", "pr_pore": "PR_pore"})


def spearman_tables(d):
    meas = [c for x in XS for c in (x, "d" + x, "r" + x)]
    rows = []
    for ch, sub in [("all", d)] + [(c, d[d["mode"] == c]) for c in ("gyponly", "gypcal")]:
        for a in meas:
            for b in CHAN:
                rows.append(dict(kind="pooled_spearman", chem=ch, tracer=a, channel=b, n=len(sub),
                                 rho=spearmanr(sub[a], sub[b])[0]))
                rs = []
                for _, r in sub.groupby(KEY):
                    if r[a].nunique() > 1 and r[b].nunique() > 1:
                        rs.append(spearmanr(r[a], r[b])[0])
                rs = np.array(rs)
                rows.append(dict(kind="within_run_spearman", chem=ch, tracer=a, channel=b, n=len(rs), rho=np.median(rs),
                                 rho_q25=np.percentile(rs, 25), rho_q75=np.percentile(rs, 75)))
    return rows


def design(d, inter):
    X = [d.dlnPRV.values, d.dlnPRp.values] + ([d.dlnPRV.values * d.dlnPRp.values] if inter else [])
    return np.column_stack([np.ones(len(d))] + X)


def lm_rows(d):
    rows = []
    for ch in ("gyponly", "gypcal"):
        s = d[d["mode"] == ch]
        for x in XS:
            y = s["d" + x].values
            for inter in (False, True):
                A = design(s, inter)
                b = np.linalg.lstsq(A, y, rcond=None)[0]
                r2 = 1 - ((y - A @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
                ssr = sst = 0.0
                per = {}
                for L in sorted(s.p32.unique()):
                    tr, te = s[s.p32 != L], s[s.p32 == L]
                    bt = np.linalg.lstsq(design(tr, inter), tr["d" + x].values, rcond=None)[0]
                    e = ((te["d" + x].values - design(te, inter) @ bt) ** 2).sum()
                    tt = ((te["d" + x].values - te["d" + x].mean()) ** 2).sum()
                    ssr += e; sst += tt
                    per[f"R2_heldout_p32_{int(L)}"] = 1 - e / tt
                r = dict(kind="linear_model", chem=ch, tracer="d" + x, channel="dlnPRV+dlnPRp" + ("+interaction" if inter else ""),
                         n=len(s), intercept=b[0], b_dlnPRV=b[1], b_dlnPRp=b[2], b_interaction=b[3] if inter else np.nan,
                         R2=r2, R2_loo_p32=1 - ssr / sst)
                r.update(per)
                rows.append(r)
    return rows


def style(ax):
    ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8.5)


def figures(d):
    yl = {"rt50_res": "t50_res / t50_res(0)", "rgamma": "gamma / gamma(0)"}
    xl = {"PRV_rel": "PR_V / PR_V0", "PRp_rel": "PR_pore / PR_pore0"}
    for name, chems in (("transport_channel_link", ("gyponly", "gypcal")), ("transport_channel_link_by_chemistry", None)):
        if chems:
            fig, axs = plt.subplots(2, 2, figsize=(8.4, 7.2))
            cells = [(i, j, yv, xv, ("gyponly", "gypcal")) for i, yv in enumerate(yl) for j, xv in enumerate(xl)]
        else:
            fig, axs = plt.subplots(2, 4, figsize=(15, 6.8))
            cells = [(i, 2 * j + c, yv, xv, (ch,)) for i, yv in enumerate(yl) for j, xv in enumerate(xl)
                     for c, ch in enumerate(("gyponly", "gypcal"))]
        for i, j, yv, xv, chs in cells:
            ax = axs[i, j]
            for ch in chs:
                for _, r in d[d["mode"] == ch].groupby(KEY):
                    ax.plot(r[xv], r[yv], color=COL[r.p32.iloc[0]], lw=0.6, alpha=0.5, ls="-" if ch == "gyponly" else "--", zorder=2)
                    ax.scatter(r[xv], r[yv], s=14, marker=MK[ch], color=COL[r.p32.iloc[0]], lw=0, alpha=0.9, zorder=3)
            ax.axhline(1, color=INK2, lw=0.7); ax.axvline(1, color=INK2, lw=0.7)
            ax.set_xlabel(xl[xv], color=INK2, fontsize=9); ax.set_ylabel(yl[yv], color=INK2, fontsize=9)
            if len(chs) == 1:
                ax.set_title("gypsum only" if chs[0] == "gyponly" else "gypsum + calcite", fontsize=9, color=INK)
            style(ax)
        h = [plt.Line2D([], [], color=c, marker="s", ls="", label=f"P32 x{int(p)}") for p, c in COL.items()]
        h += [plt.Line2D([], [], color=INK2, marker="o", ls="-", label="gypsum only"),
              plt.Line2D([], [], color=INK2, marker="^", ls="--", label="gypsum + calcite")]
        fig.legend(handles=h, loc="lower center", ncol=5, frameon=False, fontsize=8.5)
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        fig.savefig(FIG / f"{name}.png", dpi=160)
        plt.close(fig)


def main():
    d = build()
    d.to_csv(P1 / "transport_channel_link.csv", index=False)
    S = pd.DataFrame(spearman_tables(d) + lm_rows(d))
    S.to_csv(P1 / "transport_channel_link_summary.csv", index=False)
    num = d.select_dtypes("number")
    assert np.isfinite(num.drop(columns=["tau_res_y"], errors="ignore").values).all(), num.isna().sum()[num.isna().sum() > 0]
    pd.set_option("display.width", 220)
    print(len(d), "states,", d.groupby(KEY).ngroups, "runs")
    p = S[(S.kind == "pooled_spearman") & (S.chem == "all") & S.tracer.isin(["rt50_res", "rgamma", "ralpha_L", "t50_res", "gamma"])]
    print(p.pivot_table(index="tracer", columns="channel", values="rho").round(2))
    w = S[(S.kind == "within_run_spearman") & (S.chem != "all") & S.tracer.isin(["dt50_res", "dgamma", "dalpha_L"])]
    print(w[["chem", "tracer", "channel", "n", "rho", "rho_q25", "rho_q75"]].round(2).to_string())
    print(S[S.kind == "linear_model"].drop(columns=["kind", "rho", "rho_q25", "rho_q75"]).round(3).to_string())
    figures(d)


if __name__ == "__main__":
    main()
