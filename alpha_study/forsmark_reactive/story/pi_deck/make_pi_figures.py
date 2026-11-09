#!/usr/bin/env python3
"""
New figures for the PI deck (9 Nov 2026). Everything else in the deck reuses story/report/img.
  fig_clocks.png        the three normalized times on one example network: gypsum dissolved d against capacity time t_cap
                        (Hyman acid capacity gamma x PVI over the inventory), PVI on a top axis
  fig_btc_hyman.png     Hyman-style breakthrough curves (PDF of travel time, log-log, time / unreacted first arrival;
                        ensemble median and IQR over the gypsum-only Phase 1 networks) at five gypsum-dissolved states,
                        the same against current residence time, and peak arrival / tail exponent / dispersivity against d
  fig_kphi_laws.png     cartoon of a filled vein and the two readings of its permeability, and k/k0 against d for
                        every law used (different ceilings; same x10 ceiling with different shapes)
  fig_collapse.png      channel depth against n (two chemistries apart) and against the attainable gain C (one curve)
  fig_depth_meaning.png what PR_V and depth 0.78 / 0.15 mean, drawn as flow shares over equal fractures
  DYLD_LIBRARY_PATH=/opt/homebrew/Cellar/freetype/2.14.1_1/lib python3 forsmark_reactive/story/pi_deck/make_pi_figures.py
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np
import pandas as pd

H = Path(__file__).resolve().parent
FR = H.parent.parent
P1 = FR / "phase1"
sys.path[:0] = [str(FR), str(FR.parent)]
from time_axes import clocks  # noqa: E402
from analyze_phase1_tracer import read_probe  # noqa: E402

COL = {"gyponly": "#1f5f8b", "gypcal": "#c4472d"}
LAB = {"gyponly": "gypsum-only", "gypcal": "coupled gypsum–calcite"}
INK, INK2, GRIDC = "#1f2328", "#52514e", "#e6e5e1"
GYP, WALL, OPEN = "#e9c46a", "#8d8f94", "#d8ecf7"
V_GYP = 74.69e-6
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
OUTS = {}


def save(fig, name):
    fig.savefig(H / name, dpi=170)
    plt.close(fig)
    print("wrote", name)


# ------------------------------------------------------------------------------------------------------------ clocks
def fig_clocks():
    fig, ax = plt.subplots(figsize=(8.6, 4.6), constrained_layout=True)
    out = {}
    for mo, md in (("gyponly", "gypsum"), ("gypcal", "gypsum_calcite")):
        run = P1 / "L2_r15_p6.0_sg1.0_seed1" / f"{md}__uncorrected_graph__phase1"
        c = clocks(run)
        pat = pd.read_csv(run / "patterns.csv").dropna(subset=["t_y"]).sort_values("t_y")
        tc = c.t_cap(pat.t_y.to_numpy())
        ax.plot(tc, pat.dissolved, color=COL[mo], lw=2.2, label=f"{LAB[mo]} (1 capacity time = {1 / c.t_cap(1.0):,.0f} PVI)")
        out[mo] = dict(pvi_per_tcap=float(1 / c.t_cap(1.0)), gamma=float(c.c_cap * V_GYP),
                       inv_over_pore=float(c.vf0 / (1 - c.vf0)), d_at_tcap1=float(np.interp(1.0, tc, pat.dissolved)))
    x = np.linspace(0, 1, 2)
    ax.plot(x, x, color="0.35", lw=1, ls="--")
    ax.text(0.06, 0.78, "dashed, d = t$_{cap}$: every parcel of injected water leaves\nsaturated, so all of the injected capacity is used",
            fontsize=8.5, color="0.3")
    ax.text(1.98, 0.08, "Hyman τ = ΔV/V$_0$ (dissolved volume over initial pore volume);\n"
            "τ$_{max}$ = V$_{gypsum,0}$/V$_{pore,0}$ = 9 here, so d = τ / 9", ha="right", fontsize=8.5, color="0.3")
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("capacity time t$_{cap}$ = γ · PVI / (V$_{gypsum,0}$ / V$_{pore,0}$)")
    ax.set_ylabel("gypsum dissolved d  (= Hyman τ / τ$_{max}$)")
    ax.grid(color=GRIDC, lw=0.8)
    ax.legend(loc="center right", fontsize=8.5, frameon=False)
    ax.set_title("Example network (P32 ×6, σ 1, seed 1): the gap below the dashed line is capacity that left unused",
                 fontsize=9.5, loc="left")
    top = ax.secondary_xaxis("top", functions=(lambda t: t * out["gyponly"]["pvi_per_tcap"] / 1000,
                                                lambda p: p * 1000 / out["gyponly"]["pvi_per_tcap"]))
    top.set_xlabel("pore volumes injected, gypsum-only (thousands)", fontsize=9, color=INK2)
    save(fig, "fig_clocks.png")
    OUTS["clocks"] = out


# ------------------------------------------------------------------------------------------------------------ BTCs
TSNAP = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]                     # capacity-time snapshots probed on every network
DCOL = ["#9a9a9a", "#9ecae1", "#2b7bba", "#c4472d", "#e08a3c", "#5b3a8c"]


def fig_btc():
    T = pd.read_csv(P1 / "phase1_tracer.csv")
    T = T[T["mode"] == "gyponly"].copy()
    T["snap"] = [min(TSNAP + [0.02], key=lambda x: abs(x - t)) if abs(min(TSNAP + [0.02], key=lambda x: abs(x - t)) - t) < 0.02 * max(t, 0.05) + 1e-6 else np.nan
                 for t in T.t_cap]
    TA = np.logspace(np.log10(0.3), np.log10(300), 220)
    TB = np.logspace(np.log10(0.03), np.log10(10), 220)
    A = {i: [] for i in range(len(TSNAP))}
    B = {i: [] for i in range(len(TSNAP))}
    dmed = {}
    for (p, sg, s), g in T.groupby(["p32", "sigma", "seed"]):
        run = P1 / f"L2_r15_p{p}_sg{sg}_seed{int(s)}" / "gypsum__uncorrected_graph__phase1"
        t0 = float(g[g.k == 0].t_first.iloc[0])
        for i, ts in enumerate(TSNAP):
            h = g[g.snap == ts]
            if not len(h):
                continue
            r = h.iloc[0]
            _, t, f = read_probe(run / f"snapfine_{int(r.k)}")
            ok = (t > 0) & (f > 0)
            t, f = t[ok], f[ok]
            A[i].append(np.exp(np.interp(np.log(TA), np.log(t / t0), np.log(f * t0), left=np.nan, right=np.nan)))
            B[i].append(np.exp(np.interp(np.log(TB), np.log(t / r.tau_res_y), np.log(f * r.tau_res_y), left=np.nan, right=np.nan)))
    for i, ts in enumerate(TSNAP):
        dmed[ts] = float(T[T.snap == ts].diss.median())
    fig = plt.figure(figsize=(13, 8.4), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.35, 1])
    axA, axB = fig.add_subplot(gs[0, :2]), fig.add_subplot(gs[0, 2])
    for ax, D, X in ((axA, A, TA), (axB, B, TB)):
        for i, ts in enumerate(TSNAP):
            Z = np.array(D[i])
            m = np.nanmedian(Z, 0)
            lo, hi = np.nanpercentile(Z, 25, 0), np.nanpercentile(Z, 75, 0)
            ax.fill_between(X, lo, hi, color=DCOL[i], alpha=0.13, lw=0)
            ax.loglog(X, m, color=DCOL[i], lw=2.2,
                      label=("unreacted" if ts == 0 else f"t$_{{cap}}$ {ts:g}  (d {dmed[ts]:.2f})") + f"  n = {len(Z)}")
        ax.grid(color=GRIDC, lw=0.7, which="both")
        ax.set_ylim(1e-4, 3)
    axA.set_xlim(0.3, 300)
    axA.set_xlabel("t / first arrival in the unreacted network  (Hyman's normalisation)")
    axA.set_ylabel("breakthrough curve f(t)  (PDF of travel time)")
    axA.set_title("A. Hyman-style BTC at fixed snapshots (gypsum-only, median and IQR over 60 networks)", fontsize=10, loc="left")
    axA.legend(fontsize=8, frameon=False, loc="lower left")
    axB.set_xlim(0.03, 10)
    axB.set_xlabel("t / current mean residence time")
    axB.set_title("B. Same curves, pore-volume growth removed", fontsize=10, loc="left")
    xs = np.arange(len(TSNAP))
    mets = [("t50_res", "median arrival t$_{50}$ / residence time", "C. Median arrival (volume-free)"),
            ("gamma", "tail exponent γ  (f ∝ t$^{-γ}$)", "D. Tail exponent"),
            ("alpha_L_rel", "dispersivity / unreacted", "E. Longitudinal dispersivity")]
    out = {"d_median_at_snap": dmed}
    for k, (c, yl, tt) in enumerate(mets):
        ax = fig.add_subplot(gs[1, k])
        q = T[T.snap.isin(TSNAP)].groupby("snap")[c].quantile([0.25, 0.5, 0.75]).unstack().reindex(TSNAP)
        ax.fill_between(xs, q[0.25], q[0.75], color=COL["gyponly"], alpha=0.18, lw=0)
        ax.plot(xs, q[0.5], "-o", color=COL["gyponly"], lw=2, ms=5)
        ax.set_xticks(xs, [f"{ts:g}\n(d {dmed[ts]:.2f})" for ts in TSNAP], fontsize=8)
        ax.set_xlabel("capacity time snapshot (median gypsum dissolved)", fontsize=9)
        ax.set_ylabel(yl, fontsize=9)
        ax.set_title(tt, fontsize=10, loc="left")
        ax.grid(color=GRIDC, lw=0.7)
        out[c] = {f"{ts:g}": [float(q.loc[ts, 0.25]), float(q.loc[ts, 0.5]), float(q.loc[ts, 0.75])] for ts in TSNAP}
    out["n_per_snap"] = {f"{ts:g}": len(A[i]) for i, ts in enumerate(TSNAP)}
    save(fig, "fig_btc_hyman.png")
    OUTS["btc"] = out


# ------------------------------------------------------------------------------------------------------------ k-phi
CAL = "#b9b9c9"


def vein(ax, x0, y0, w, h, open_frac, label, sub, cal_frac=0.0):
    ax.add_patch(Rectangle((x0, y0 + h), w, 0.18, color=WALL))
    ax.add_patch(Rectangle((x0, y0 - 0.18), w, 0.18, color=WALL))
    ax.add_patch(Rectangle((x0, y0), w, h, color=GYP))
    if cal_frac:
        ax.add_patch(Rectangle((x0, y0), w, h, facecolor=CAL, edgecolor="#6f6f86", hatch="///", lw=0))
    ho = h * open_frac
    ax.add_patch(Rectangle((x0, y0 + (h - ho) / 2), w, ho, color=OPEN))
    ax.text(x0 + w / 2, y0 + h + 0.32, label, ha="center", fontsize=9.5, weight="bold")
    ax.text(x0 + w / 2, y0 - 0.42, sub, ha="center", va="top", fontsize=8.5, color=INK2)


def fig_kphi():
    fig = plt.figure(figsize=(13.5, 5.8), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1])
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 10.6)
    ax.set_ylim(-3.7, 2.5)
    ax.axis("off")
    W, S = 2.25, 2.6
    states = [(0.1, "start: 90 % gypsum", "φ0 = 0.10", 0), (0.55, "half dissolved", "φ = 0.55", 0),
              (1.0, "gypsum-only: gone", "φ = 1.00", 0), (0.555, "coupled: calcite in", "φ = 0.555 (calcite 0.445)", 1)]
    for i, (of, lab, sub, cal) in enumerate(states):
        vein(ax, 0.2 + i * S, 0.6, W, 0.9, of, lab, sub, cal)
    rows = [("n = 1   k ∝ φ: the opened space stays rough and porous", ["×1", "×5.5", "×10", "×5.55"], COL["gyponly"]),
            ("n = 3   k ∝ φ³: the fill clears to a smooth slot (cubic law)", ["×1", "×166", "×1000", "×171"], "#7b3294")]
    for r, (lab, ks, c) in enumerate(rows):
        y = -1.5 - r * 1.05
        ax.text(0.2, y + 0.38, lab, fontsize=9, color=c, weight="bold")
        for i, k in enumerate(ks):
            ax.text(0.2 + W / 2 + i * S, y, f"k/k0 {k}", ha="center", fontsize=10, color=c)
    ax.text(0.2, 2.4, "A. Every run is a mineral-filled vein: only the fill dissolves, never the wall rock",
            fontsize=10, weight="bold", va="top")
    ax.text(0.2, -3.65, "The value in the fully reacted vein is the attainable gain C. Calcite refills part of the space, "
            "so the same law\ngives the coupled chemistry a lower C (×5.55 instead of ×10 at n = 1).",
            fontsize=8.5, color=INK2, va="bottom")
    # B: laws
    ax = fig.add_subplot(gs[1])
    d = np.linspace(0, 1, 201)
    phi = 0.1 + 0.9 * d
    blues = {1.0: "#9ecae1", 1.4771: "#4a98c9", 2.0: "#1f5f8b", 3.0: "#0b2c4a"}
    for n, c in blues.items():
        ax.semilogy(d, (phi / 0.1) ** n, color=c, lw=2.4, label=f"n = {n:.3g}: C = ×{10 ** n:,.0f}")
    E = pd.read_csv(P1 / "kphi_e0" / "kphi_e0_summary.csv")
    for _, r in E[E.ceiling.round() == 10].iterrows():
        if r.n == 1:
            continue
        pc = r.phi_c
        ax.semilogy(d, ((phi - pc) / (0.1 - pc)) ** r.n, color="0.45", lw=1.4, ls="--")
    ax.plot([], [], color="0.45", ls="--", label="n = 0.5, 2, 8 squeezed to end at ×10\n(same C, different shape)")
    ax.set_xlabel("gypsum dissolved in the fracture")
    ax.set_ylabel("permeability k / k0")
    ax.set_ylim(0.8, 2000)
    ax.grid(color=GRIDC, lw=0.7, which="both")
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    ax.set_title("B. Where the law ends (C) vs how it gets there (shape)", fontsize=10, loc="left")
    save(fig, "fig_kphi_laws.png")


# ------------------------------------------------------------------------------------------------------------ collapse
def fig_collapse():
    R = pd.read_csv(FR / "ceilsweep" / "ceilsweep_runs.csv")
    R["phi0"] = R.phi0.round(3)
    E = pd.read_csv(P1 / "kphi_e0" / "kphi_e0_summary.csv")
    RS = pd.read_csv(FR / "ceilsweep" / "ceilsweep_residuals.csv")
    fig, axs = plt.subplots(1, 3, figsize=(14.5, 4.9), constrained_layout=True, gridspec_kw=dict(width_ratios=[1, 1.15, 1]))
    out = {}

    def medbar(ax, x, h, color, mk, fill, lab, off=1.0):
        q = h.depth.quantile([0.25, 0.5, 0.75])
        ax.errorbar([x * off], [q[0.5]], yerr=[[q[0.5] - q[0.25]], [q[0.75] - q[0.5]]], fmt=mk, color=color, ms=8,
                    mfc=color if fill else "white", mew=1.6, capsize=3, lw=1.4, label=lab, zorder=3)
        return float(q[0.5])

    # A: against n
    ax = axs[0]
    for mo, off in (("gyponly", -0.05), ("gypcal", 0.05)):
        h = R[(R["mode"] == mo) & (R.phi0 == 0.1)]
        ax.scatter(h.n + off, h.depth, s=12, color=COL[mo], alpha=0.25, lw=0)
        m = {n: medbar(ax, n + off, g, COL[mo], "o" if mo == "gyponly" else "s", True, None) for n, g in h.groupby("n")}
        ax.plot(np.array(list(m)) + off, list(m.values()), color=COL[mo], lw=1.6, label=LAB[mo])
        out[mo] = {f"n{n:g}": v for n, v in m.items()}
    ax.set_xlabel("permeability exponent n  (k = k0 (φ/φ0)$^n$)")
    ax.set_ylabel("channel depth  (PR$_V$ minimum / start)")
    ax.set_xticks([1, 1.48, 2, 3])
    ax.set_ylim(0, 1)
    ax.grid(color=GRIDC, lw=0.7)
    ax.legend(frameon=False, fontsize=9)
    ax.set_title("A. Same law (n), two chemistries: apart", fontsize=10.5, loc="left")
    # B: against C, medians and IQR over 9 networks
    ax = axs[1]
    for mo, mk in (("gyponly", "o"), ("gypcal", "s")):
        for ph, fill in ((0.1, True), (0.182, False)):
            h = R[(R["mode"] == mo) & (R.phi0 == ph)]
            ax.scatter(h.C, h.depth, s=12, color=COL[mo], alpha=0.2, lw=0)
            for i, (n, g) in enumerate(h.groupby("n")):
                medbar(ax, g.C.median(), g, COL[mo], mk, fill,
                       (f"{LAB[mo]}, " + ("φ0 0.10, n = 1–3" if ph == 0.1 else "φ0 0.18, n = 1")) if i == 0 else None)
    e = E[E.ceiling.round() == 10]
    ax.scatter(e.ceiling * np.array([0.9, 0.96, 1.04, 1.1]), e.depth, marker="D", s=30, color="#e9a23b", edgecolor="k",
               lw=0.6, zorder=4, label="×10, four law shapes (one network)")
    g = R[(R["mode"] == "gyponly") & (R.phi0 == 0.1)].groupby("C").depth.median()
    ax.plot(g.index, g.values, color=COL["gyponly"], lw=1.2, ls="--", zorder=2)
    ax.set_xscale("log")
    ax.set_xlabel("attainable permeability gain C = k(fully dissolved) / k0")
    ax.set_ylim(0, 1)
    ax.grid(color=GRIDC, lw=0.7, which="both")
    ax.legend(frameon=False, fontsize=7.8, loc="lower left")
    ax.set_title("B. Same gain (C): one curve (median, IQR of 9 networks)", fontsize=10.5, loc="left")
    # C: same network, paired: coupled vs gypsum-only, matched by n and matched by C
    ax = axs[2]
    a = R[(R["mode"] == "gyponly") & (R.phi0 == 0.1)][["p32", "seed", "n", "depth"]]
    b = R[(R["mode"] == "gypcal") & (R.phi0 == 0.1)][["p32", "seed", "n", "depth"]]
    mn = a.merge(b, on=["p32", "seed", "n"], suffixes=("_g", "_c"))
    ax.plot([0, 1], [0, 1], color="0.4", lw=1, ls="--")
    ax.scatter(mn.depth_g, mn.depth_c, s=30, facecolor="white", edgecolor=COL["gypcal"], lw=1.2,
               label=f"matched by n: coupled shallower by {np.median(mn.depth_c - mn.depth_g):.2f} (median)")
    ax.scatter(RS.depth_gyp_interp, RS.depth_cal, s=30, color=COL["gypcal"],
               label=f"matched by C: within {RS.residual.abs().median():.3f} (median)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("gypsum-only depth on that network")
    ax.set_ylabel("coupled depth on the same network")
    ax.grid(color=GRIDC, lw=0.7)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title("C. Network by network (36 pairs each)", fontsize=10.5, loc="left")
    out["paired_n_median_gap"] = float(np.median(mn.depth_c - mn.depth_g))
    out["paired_n_count"] = int(len(mn))
    out["paired_C_median_abs"] = float(RS.residual.abs().median())
    out["paired_C_median"] = float(RS.residual.median())
    out["e0_depths"] = {f"n{r.n:g}": float(r.depth) for _, r in e.iterrows()}
    save(fig, "fig_collapse.png")
    OUTS["collapse"] = out


# ------------------------------------------------------------------------------------------------------------ depth meaning
def fig_depth():
    starts = []
    for p in (4.0, 6.0, 8.0):
        for s in (1, 2, 3):
            c = pd.read_csv(P1 / f"L2_r15_p{p}_sg1.0_seed{s}" / "gypsum__uncorrected_graph__phase1" / "channelization.csv").sort_values("k")
            starts.append(float(c.pr_fracture_vol.iloc[0]))
    prv0 = float(np.median(starts))
    N = 40
    i = np.arange(N)

    def shares(a):
        q = np.exp(-a * i)
        return q / q.sum()

    def neff(q):
        return 1 / (q ** 2).sum() / N

    from scipy.optimize import brentq
    a0 = brentq(lambda a: neff(shares(a)) - prv0, 1e-4, 5)     # start spread = the median network PR_V at the start
    target0 = neff(shares(a0))
    a78 = brentq(lambda a: neff(shares(a)) - 0.78 * target0, a0, 5)
    a15 = brentq(lambda a: neff(shares(a)) - 0.15 * target0, a0, 5)
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.9), constrained_layout=True, sharey=True)
    for ax, a, t in zip(axs, (a0, a78, a15), ("start", "depth 0.78  (×5.5 gain)", "depth 0.15  (×1000 gain)")):
        q = shares(a)
        ax.bar(i, q, color=COL["gyponly"], width=0.85)
        ax.set_title(f"{t}\nPR$_V$ {neff(q):.2f}: flow effectively in {neff(q) * N:.0f} of {N} fractures", fontsize=10, loc="left")
        ax.set_xlabel("fractures of equal volume, ranked by flow")
        ax.set_xticks([])
        ax.grid(color=GRIDC, lw=0.7, axis="y")
    axs[0].set_ylabel("share of the total flow")
    save(fig, "fig_depth_meaning.png")
    OUTS["depth"] = dict(prv_start_median_9net=prv0, prv_start_range=[min(starts), max(starts)], N=N,
                         eff_start=float(neff(shares(a0)) * N), eff_078=float(neff(shares(a78)) * N), eff_015=float(neff(shares(a15)) * N))


if __name__ == "__main__":
    which = sys.argv[1:] or ["clocks", "btc", "kphi", "collapse", "depth"]
    for w in which:
        {"clocks": fig_clocks, "btc": fig_btc, "kphi": fig_kphi, "collapse": fig_collapse, "depth": fig_depth}[w]()
    p = H / "pi_figures_numbers.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    old.update(OUTS)
    p.write_text(json.dumps(old, indent=1))
    print(json.dumps(OUTS, indent=1)[:3000])
