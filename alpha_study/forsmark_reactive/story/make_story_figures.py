#!/usr/bin/env python3
"""
Story figures (7 Nov 2026): four figures, one per story item, all BiGraFV-against-BiGraFV.
  fig1_stages.png      the stages the front moves through (network PR_V, PR_pore and their ratio against dissolved fraction)
  fig2_front.png       the focus moves with the front and relaxes behind it (100 m bins)
  fig3_gain.png        depth against attainable permeability gain; chemistries on one curve; same (nested) channel
  fig4_predictor.png   one pre-run number predicts the gypsum dissolved at breakthrough
Inputs (no new runs): phase1/phase1_mechanism.csv, stage_events_clocks.csv, xbin_channelization.csv, xbin_bin_minima.csv,
xbin_spanning_minima.csv, ceilsweep/ceilsweep_runs.csv, ceilsweep_residuals.csv, channel_overlap.csv,
phase1/early_arrival_predictor.csv, early_arrival_predictor_fit.csv.
  python3 forsmark_reactive/story/make_story_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

H = Path(__file__).resolve().parent
FR = H.parent
P1 = FR / "phase1"
COL = {"gyponly": "#1f5f8b", "gypcal": "#c4472d"}
LAB = {"gyponly": "gypsum-only", "gypcal": "coupled gypsum–calcite"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 10,
                     "axes.titlelocation": "left", "legend.frameon": False})
GRID = np.linspace(0, 0.9, 91)


def on_grid(d, y):
    d = np.maximum.accumulate(np.asarray(d, float))
    out = np.interp(GRID, d, y, left=np.nan, right=np.nan)
    out[GRID > d.max()] = np.nan
    return out


def events():
    e = pd.read_csv(P1 / "stage_events_clocks.csv")
    e = e[(e.tag == "phase1") & e.p32.isin([4.0, 6.0, 8.0])].drop_duplicates(["mode", "p32", "sigma", "seed", "event"])
    return e.pivot_table(index=["mode", "p32", "sigma", "seed"], columns="event", values="dissolved").reset_index()


# ---------------------------------------------------------------- Figure 1: stages
def fig1():
    m = pd.read_csv(P1 / "phase1_mechanism.csv")
    m = m[(m.tag == "phase1") & m.p32.isin([4.0, 6.0, 8.0])]
    E = events()
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.3), constrained_layout=True)
    stats = {}
    for ax, mo in zip(axs[:2], ("gyponly", "gypcal")):
        V, P, R = [], [], []
        for _, g in m[m["mode"] == mo].groupby(["p32", "sigma", "seed"]):
            g = g.sort_values("k")
            v, p = g.pr_frac / g.pr_frac.iloc[0], g.pr_pore / g.pr_pore.iloc[0]
            V.append(on_grid(g.dissolved, v)); P.append(on_grid(g.dissolved, p)); R.append(on_grid(g.dissolved, g.pr_pore / g.pr_frac))
        V, P, R = map(np.array, (V, P, R))
        n = np.sum(np.isfinite(V), 0)
        ok = n >= 30
        for arr, c, lab, ls in ((V, COL[mo], "PR$_V$: flow against fracture volume", "-"), (P, "0.45", "PR$_{pore}$: flow against open pore volume", "--")):
            med = np.nanmedian(arr, 0); lo = np.nanpercentile(arr, 25, 0); hi = np.nanpercentile(arr, 75, 0)
            ax.fill_between(GRID[ok], lo[ok], hi[ok], color=c, alpha=0.15, lw=0)
            ax.plot(GRID[ok], med[ok], ls, color=c, lw=2, label=lab)
        e = E[E["mode"] == mo]
        ev = {k: e[k].median() for k in ("PRpore_min", "PRV_min", "breakthrough")}
        stats[mo] = dict(n=len(V), **ev, end_prv=float(np.nanmedian([r[np.isfinite(r)][-1] for r in V])))
        for k, lab in (("PRpore_min", "1"), ("PRV_min", "3"), ("breakthrough", "bt")):
            ax.axvline(ev[k], color="0.75", lw=0.9)
        y0 = 1.06
        for x0, x1, s in ((0, ev["PRpore_min"], "1"), (ev["PRpore_min"], ev["PRV_min"], "2"),
                          (ev["PRV_min"], ev["breakthrough"], "3"), (ev["breakthrough"], 0.9, "4")):
            ax.text((x0 + x1) / 2, y0, s, ha="center", va="bottom", fontsize=12, fontweight="bold", color="0.35")
        ax.set_ylim(0.0, 1.22)
        ax.set_xlim(0, 0.9)
        ax.set_xlabel("fraction of the network's gypsum dissolved")
        ax.set_title(f"{'A' if mo == 'gyponly' else 'B'}. {LAB[mo]} (median and IQR, {len(V)} runs)", fontsize=10)
        ax.legend(loc="lower right", fontsize=8.5)
    axs[0].set_ylabel("participation ratio / its start\n(lower = flow more concentrated)")
    ax = axs[2]
    for mo in ("gyponly", "gypcal"):
        R = []
        for _, g in m[m["mode"] == mo].groupby(["p32", "sigma", "seed"]):
            g = g.sort_values("k")
            R.append(on_grid(g.dissolved, (g.pr_pore / g.pr_frac) / (g.pr_pore.iloc[0] / g.pr_frac.iloc[0])))
        R = np.array(R); ok = np.sum(np.isfinite(R), 0) >= 30
        ax.fill_between(GRID[ok], np.nanpercentile(R, 25, 0)[ok], np.nanpercentile(R, 75, 0)[ok], color=COL[mo], alpha=0.15, lw=0)
        ax.plot(GRID[ok], np.nanmedian(R, 0)[ok], color=COL[mo], lw=2, label=LAB[mo])
    ax.axhline(1, color="0.7", lw=0.8)
    ax.set_xlim(0, 0.9)
    ax.set_xlabel("fraction of the network's gypsum dissolved")
    ax.set_ylabel("PR$_{pore}$ / PR$_V$, relative to start\n(< 1: flow decoupled from open space)")
    ax.set_title("C. Decoupling and recoupling of flow and open space", fontsize=10)
    ax.legend(loc="lower right", fontsize=8.5)
    fig.savefig(H / "fig1_stages.png", dpi=170)
    plt.close(fig)
    return stats


# ---------------------------------------------------------------- Figure 2: moving focus and relaxation
def fig2():
    X = pd.read_csv(P1 / "xbin_channelization.csv")
    X = X[X.p32.isin([4.0, 6.0, 8.0])]
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.3), constrained_layout=True, gridspec_kw=dict(width_ratios=[1, 1, 1.15]))
    for ax, mo in zip(axs[:2], ("gyponly", "gypcal")):
        cube = []
        for _, g in X[X["mode"] == mo].groupby(["p32", "sigma", "seed"]):
            g = g.sort_values(["bin", "k"])
            rows = []
            for b in range(10):
                h = g[g.bin == b]
                rows.append(on_grid(h.dissolved, h.prv / h.prv.iloc[0]) if len(h) > 2 else np.full(len(GRID), np.nan))
            cube.append(np.array(rows))
        cube = np.array(cube)
        med = np.nanmedian(cube, 0)
        im = ax.pcolormesh(np.arange(0, 1001, 100), np.r_[GRID - 0.005, GRID[-1] + 0.005], med.T, cmap="RdBu_r", vmin=0.3, vmax=1.7, shading="flat")
        ax.set_xlabel("distance of fracture centre from inlet (m)")
        ax.set_title(f"{'A' if mo == 'gyponly' else 'B'}. {LAB[mo]}: PR$_V$ of each 100 m stretch", fontsize=10)
    axs[0].set_ylabel("fraction of the network's gypsum dissolved")
    fig.colorbar(im, ax=axs[:2], shrink=0.9, label="PR$_V$ of the stretch / its start (blue = focused)")
    ax = axs[2]
    Mc = pd.read_csv(P1 / "xbin_bin_minima.csv"); Mc = Mc[Mc.metric == "prv"]
    Ms = pd.read_csv(P1 / "xbin_spanning_minima.csv")
    x = np.arange(50, 1000, 100)
    for mo in ("gyponly", "gypcal"):
        c = Mc[Mc["mode"] == mo].sort_values("bin"); s = Ms[Ms["mode"] == mo].sort_values("bin")
        ax.plot(x, c.min_rel, "-o", color=COL[mo], ms=4, label=f"{LAB[mo]}: lowest value")
        ax.plot(x, s.min_rel, ":", color=COL[mo], lw=1.2)
        ax.plot(x, c.end_rel, "-s", color=COL[mo], ms=4, mfc="white", label=f"{LAB[mo]}: value at the end")
        ax.plot(x, s.end_rel, ":", color=COL[mo], lw=1.2)
    ax.axhline(1, color="0.7", lw=0.8)
    ax.set_ylim(0.3, 1.1)
    ax.set_xlabel("distance from inlet (m)")
    ax.set_ylabel("PR$_V$ of the stretch / its start")
    ax.set_title("C. Each stretch focuses, then returns to its start", fontsize=10)
    ax2 = ax.twinx()
    for mo in ("gyponly", "gypcal"):
        c = Mc[Mc["mode"] == mo].sort_values("bin")
        ax2.plot(x, c.d_at_min, "--", color=COL[mo], lw=1, alpha=0.6)
    ax2.set_ylabel("dissolved fraction at the stretch's minimum (dashed)", color="0.4")
    ax2.set_ylim(0, 0.7)
    ax2.spines["right"].set_visible(True)
    ax.plot([], [], ":", color="0.4", label="dotted: fractures counted in every stretch they span")
    ax.plot([], [], "--", color="0.4", label="dashed (right axis): dissolved fraction at the minimum")
    ax.legend(loc="lower left", fontsize=7)
    fig.savefig(H / "fig2_front.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------- Figure 3: attainable gain
def fig3():
    R = pd.read_csv(FR / "ceilsweep" / "ceilsweep_runs.csv")
    Res = pd.read_csv(FR / "ceilsweep" / "ceilsweep_residuals.csv")
    J = pd.read_csv(FR / "ceilsweep" / "channel_overlap.csv")
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.3), constrained_layout=True)
    ax = axs[0]
    for (p, s), h in R.groupby(["p32", "seed"]):
        g = h[h["mode"] == "gyponly"].sort_values("C")
        ax.plot(g.C, g.depth, "-o", color=COL["gyponly"], lw=1, ms=3.5, alpha=0.65)
        c = h[h["mode"] == "gypcal"]
        ax.plot(c.C, c.depth, "s", color=COL["gypcal"], ms=4.5, mfc="white", mew=1.3, alpha=0.85)
    ax.plot([], [], "-o", color=COL["gyponly"], label="gypsum-only (one line per network)")
    ax.plot([], [], "s", color=COL["gypcal"], mfc="white", mew=1.3, label="coupled, at its own gain")
    ax.set_xscale("log")
    ax.set_xlabel("attainable permeability gain C = k(fully reacted) / k$_0$")
    ax.set_ylabel("channel depth: PR$_V$ minimum / start")
    ax.set_title("A. Depth follows the attainable gain (9 networks)", fontsize=10)
    ax.legend(loc="lower left", fontsize=8.5)
    ax = axs[1]
    ax.axhspan(-0.05, 0.05, color="0.93")
    ax.axhline(0, color="0.6", lw=0.8)
    ax.scatter(Res.C, Res.residual, color=COL["gypcal"], s=20)
    ax.set_xscale("log")
    ax.set_xlabel("coupled gain C")
    ax.set_ylabel("coupled depth − gypsum-only depth at the same C")
    ax.set_title(f"B. Same curve: median gap {Res.residual.abs().median():.3f} ({len(Res)} points)", fontsize=10)
    ax = axs[2]
    nm = {"ceilN148": ("n = 1.48", 1.4771), "ceilN2": ("n = 2", 2.0), "ceilN3": ("n = 3", 3.0)}
    for mo, off in (("gyponly", -0.08), ("gypcal", 0.08)):
        Jm = J[(J["mode"] == mo) & J.tag.isin(nm)]
        xs = np.array([nm[t][1] for t in Jm.tag]) + off
        ax.scatter(xs, Jm.frac_n1_in_b / Jm.nb_over_na, marker="o", color=COL[mo], s=22, label=f"{LAB[mo]}: share of the channel inside the n = 1 channel")
        ax.scatter(xs, Jm.nb_over_na, marker="v", color=COL[mo], s=22, alpha=0.6, label=f"{LAB[mo]}: channel size / n = 1 size")
    ax.set_xticks([1.4771, 2, 3], ["n = 1.48\n(×30)", "n = 2\n(×100)", "n = 3\n(×1000)"])
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("fraction")
    ax.set_title("C. A higher gain keeps fewer of the same fractures", fontsize=10)
    ax.legend(loc="lower left", fontsize=7)
    fig.savefig(H / "fig3_gain.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------- Figure 4: predictor
def fig4():
    D = pd.read_csv(P1 / "early_arrival_predictor.csv")
    F = pd.read_csv(P1 / "early_arrival_predictor_fit.csv").set_index("mode")
    x = "t10"
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    mk = {4.0: "o", 6.0: "s", 8.0: "^"}
    out = {}
    for ax, mo in zip(axs[:2], ("gyponly", "gypcal")):
        a, b = D[(D["mode"] == mo) & (D.scale == "1km")], D[(D["mode"] == mo) & (D.scale == "2km")]
        sl, ic = np.polyfit(a[x], a.d_bt, 1)
        pb = ic + sl * b[x]
        r2b = 1 - ((b.d_bt - pb) ** 2).sum() / ((b.d_bt - b.d_bt.mean()) ** 2).sum()
        rb = spearmanr(b[x], b.d_bt).statistic
        out[mo] = dict(slope=sl, icpt=ic, loo=F.loc[mo]["loo_" + x], rho1=F.loc[mo]["rho_" + x], r2_2km=r2b, rho_2km=rb,
                       mae_2km=float((b.d_bt - pb).abs().median()), ratio1=float((a.d_bt / a[x]).median()), ratio2=float((b.d_bt / b[x]).median()))
        for p, g in a.groupby("p32"):
            ax.scatter(g[x], g.d_bt, marker=mk[p], color=COL[mo], s=24, label=f"1 km, P32 ×{p:g}")
        ax.scatter(b[x], b.d_bt, marker="x", color="0.35", s=22, label="2 km (not used in the fit)")
        xx = np.linspace(min(a[x].min(), b[x].min()) * 0.95, max(a[x].max(), b[x].max()) * 1.03, 10)
        ax.plot(xx, ic + sl * xx, color=COL[mo], lw=1.5, label=f"1 km fit: {ic:.2f} + {sl:.2f} x")
        ax.set_xlabel("t$_{10}$ / τ$_{res}$ of the unreacted network (tracer)")
        ax.set_ylabel("fraction of gypsum dissolved at breakthrough")
        ax.set_title(f"{'A' if mo == 'gyponly' else 'B'}. {LAB[mo]}: 1 km held-out R² {out[mo]['loo']:.2f}; 2 km ρ {rb:.2f}", fontsize=10)
        ax.legend(loc="upper left", fontsize=7.5)
    ax = axs[2]
    labels = ["largest-fracture\nflow share", "t$_{01}$", "t$_{05}$", "t$_{10}$", "t$_{16}$"]
    keys = ["loo_top1", "loo_t01", "loo_t05", "loo_t10", "loo_t16"]
    w = 0.38
    for i, mo in enumerate(("gyponly", "gypcal")):
        ax.bar(np.arange(5) + (i - 0.5) * w, [F.loc[mo][k] for k in keys], width=w, color=COL[mo], label=LAB[mo])
    ax.set_xticks(range(5), labels, fontsize=8.5)
    ax.set_ylim(0, 1)
    ax.set_ylabel("R², each P32 level held out in turn (1 km)")
    ax.set_title("C. Early tracer arrival beats the largest-fracture share", fontsize=10)
    ax.legend(loc="upper left", fontsize=8)
    fig.savefig(H / "fig4_predictor.png", dpi=170)
    plt.close(fig)
    return out


if __name__ == "__main__":
    s = fig1()
    print(s)
    fig2(); fig3()
    print(fig4())
    print("wrote", H)
