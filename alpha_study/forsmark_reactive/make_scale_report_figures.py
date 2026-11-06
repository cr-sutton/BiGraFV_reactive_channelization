#!/usr/bin/env python3
"""
Report figures for the 2 km scale test and the k-phi exponent test (6 Nov 2026).  All within capacity time <= 2.

  scale2km_prv.png     median PR_V / start against the dissolved fraction, 1 km vs 2 km, sigma 1, P32 x4 / x6 / x8
  scale2km_events.png  per-run breakthrough and depth, 1 km vs 2 km, and the share of runs whose early PR_V dip is deeper
  scale2km_bins.png    PR_V / start in 200 m bins along x for two 2 km gypsum-only runs (x4 seed 3, x8 seed 3)
  kphi_n3.png          n = 1 vs n = 3 on P32 x6 sigma 1 seed 1: PR_V / start and k_eff gain against the dissolved fraction

Inputs: phase1/phase1_mechanism.csv, scale2km/scale_mechanism.csv, scale2km/scale_runs.csv, the kphi_n3 run caches,
paraview/S2KM__* per-fracture files (bins).

  python3 forsmark_reactive/make_scale_report_figures.py   -> report_phase1/img/
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT), str(ROOT / "physics_upscaling")]
OUT = HERE / "report_phase1" / "img"
TCAP = 2.0
D = np.round(np.arange(0, 0.851, 0.01), 3)
C1, C2 = "#7a7f86", "#1f5f8b"          # 1 km grey, 2 km blue
MODES = (("gyponly", "Gypsum-only"), ("gypcal", "Coupled gypsum–calcite"))
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

p1 = pd.read_csv(HERE / "phase1" / "phase1_mechanism.csv")
p1 = p1[(p1.tag == "phase1") & p1.p32.isin([4.0, 6.0, 8.0])]
p2 = pd.read_csv(HERE / "scale2km" / "scale_mechanism.csv")
runs = pd.read_csv(HERE / "scale2km" / "scale_runs.csv")


def curves(m):
    """{(mode, p32, sigma): array (n_seeds, len(D))} of PR_V / start on D, t_cap <= 2."""
    out = {}
    for (mo, p, sg, s), g in m.groupby(["mode", "p32", "sigma", "seed"]):
        g = g[g.t_cap <= TCAP].sort_values("k")
        y = g.pr_frac.values / g.pr_frac.values[0]
        x = np.maximum.accumulate(g.dissolved.values)
        out.setdefault((mo, p, sg), []).append(np.where(D <= x.max(), np.interp(D, x, y), np.nan))
    return {k: np.array(v) for k, v in out.items()}


def fig_prv():
    c1, c2 = curves(p1), curves(p2)
    fig, axs = plt.subplots(2, 3, figsize=(12, 6.4), sharex=True, sharey=True, constrained_layout=True)
    for i, (mo, lab) in enumerate(MODES):
        for j, p in enumerate((4.0, 6.0, 8.0)):
            ax = axs[i, j]
            for c, col, dom in ((c1, C1, "1 km"), (c2, C2, "2 km")):
                a = c.get((mo, p, 1.0))
                if a is None:
                    continue
                ok = np.sum(np.isfinite(a), 0) >= 3
                q = np.nanpercentile(a, [25, 50, 75], axis=0)
                ax.fill_between(D[ok], q[0][ok], q[2][ok], color=col, alpha=0.18, lw=0)
                ax.plot(D[ok], q[1][ok], color=col, lw=2, label=f"{dom} (n = {len(a)})")
                r = runs[(runs.domain == dom.replace(" ", "")) & (runs["mode"] == mo) & (runs.p32 == p) & (runs.sigma == 1.0)]
                ax.axvline(r.breakthrough.median(), color=col, ls="--", lw=1.2)
            ax.axhline(1, color="0.8", lw=0.8)
            ax.set_title(f"{lab}, P32 ×{p:g}", fontsize=10)
            if i == 1:
                ax.set_xlabel("fraction of the gypsum dissolved")
            if j == 0:
                ax.set_ylabel("PR$_V$ / its start")
            if i == 0 and j == 0:
                ax.legend(frameon=False, loc="lower left")
    axs[0, 0].set_ylim(0.45, 1.08)
    fig.suptitle("Flow focusing at 1 km and 2 km, σ = 1: median (line) and interquartile range (band) over 5 seeds; "
                 "dashed = median breakthrough", fontsize=10.5)
    fig.savefig(OUT / "scale2km_prv.png", dpi=150)
    plt.close(fig)


def early_late(m):
    rows = []
    for (mo, p, sg, s), g in m.groupby(["mode", "p32", "sigma", "seed"]):
        g = g[g.t_cap <= TCAP].sort_values("k")
        y = (g.pr_frac / g.pr_frac.iloc[0]).values
        e = g.dissolved.values < 0.35
        rows.append(dict(mode=mo, p32=p, sigma=sg, seed=s, early_deeper=bool(y[e].min() < y[~e].min())))
    return pd.DataFrame(rows)


def fig_events():
    cells = [(p, sg) for p, sg in ((4.0, 1.0), (6.0, 1.0), (8.0, 1.0), (8.0, 0.5))
             if ((runs.domain == "2km") & (runs.p32 == p) & (runs.sigma == sg)).sum() >= 10]
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.2), constrained_layout=True)
    rng = np.random.default_rng(0)
    for a, (meas, lab) in enumerate((("breakthrough", "dissolved fraction at breakthrough"),
                                     ("depth", "depth = min PR$_V$ / start"))):
        ax = axs[a]
        ticks, tl = [], []
        for ci, (p, sg) in enumerate(cells):
            for mi, (mo, mlab) in enumerate(MODES):
                x0 = ci * 2.6 + mi * 1.1
                for di, (dom, col) in enumerate((("1km", C1), ("2km", C2))):
                    v = runs[(runs.domain == dom) & (runs["mode"] == mo) & (runs.p32 == p) & (runs.sigma == sg)][meas].dropna()
                    xx = x0 + di * 0.42
                    ax.scatter(xx + rng.uniform(-0.08, 0.08, len(v)), v, s=16, color=col, alpha=0.8,
                               label=(dom.replace("km", " km") if (ci == 0 and mi == 0) else None))
                    ax.hlines(v.median(), xx - 0.15, xx + 0.15, color=col, lw=2.2)
                ticks.append(x0 + 0.21)
                tl.append(f"{'gyp' if mo == 'gyponly' else 'cpl'}\n×{p:g} σ{sg:g}")
        ax.set_xticks(ticks, tl, fontsize=8)
        ax.set_ylabel(lab)
        if a == 0:
            ax.legend(frameon=False, loc="upper left")
    el = pd.concat([early_late(p1).assign(domain="1km"), early_late(p2).assign(domain="2km")])
    ax = axs[2]
    for di, (dom, col) in enumerate((("1km", C1), ("2km", C2))):
        sh, ns = [], []
        for p, sg in cells:
            g = el[(el.domain == dom) & (el.p32 == p) & (el.sigma == sg)]
            sh.append(g.early_deeper.mean())
            ns.append(len(g))
        xs = np.arange(len(cells)) + (di - 0.5) * 0.38
        ax.bar(xs, sh, width=0.36, color=col, label=dom.replace("km", " km"))
        for x, s_, n in zip(xs, sh, ns):
            ax.text(x, s_ + 0.02, f"{round(s_ * n)}/{n}", ha="center", fontsize=8)
    ax.set_xticks(range(len(cells)), [f"×{p:g} σ{sg:g}" for p, sg in cells])
    ax.set_ylim(0, 1)
    ax.set_ylabel("share of runs whose early dip (d < 0.35) is deepest")
    ax.legend(frameon=False, loc="upper right")
    fig.suptitle("Per-run stage measures at 1 km and 2 km (both chemistries; bar = median), and how often the "
                 "network PR$_V$ minimum comes mid-transit", fontsize=10.5)
    fig.savefig(OUT / "scale2km_events.png", dpi=150)
    plt.close(fig)


def bins(run, pvname, L=2000.0, step=200.0):
    from analyze_km_dissolution_patterns import read_polygons
    from analyze_phase1_mechanism import read_vtu
    from write_corrected_bigrafv_inputs import read_uge
    E = np.arange(0, L + 1, step)
    pat = pd.read_csv(run / "patterns.csv").set_index("k")
    nf = len(read_polygons(run / "polygons.dat"))
    V = read_uge(run / "full_mesh_vol_area.uge")[0][:nf, 4]
    ks, rows = [], []
    for f in sorted((ROOT / "paraview" / pvname).glob("fractures_*.vtu")):
        k = int(f.stem.split("_")[1])
        if k not in pat.index:
            continue
        a = read_vtu(f)
        q = np.abs(a["Q_frac"]).astype(float)
        b = np.clip(np.digitize(a["x_center"].astype(float) + L / 2, E) - 1, 0, len(E) - 2)
        rows.append([q[b == i].sum() ** 2 / (V[b == i].sum() * (q[b == i] ** 2 / V[b == i]).sum()) for i in range(len(E) - 1)])
        ks.append(k)
    a = np.array(rows)
    a = a / a[0]
    d = np.maximum.accumulate(pat.loc[ks, "dissolved"].values)
    return E, d, a


def fig_bins():
    S = HERE / "scale2km"
    sel = (("L2_r15_p4.0_sg1.0_seed3", "P32 ×4, seed 3"), ("L2_r15_p8.0_sg1.0_seed3", "P32 ×8, seed 3"))
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True, constrained_layout=True)
    for ax, (net, lab) in zip(axs, sel):
        run = S / net / "gypsum__uncorrected_graph__phase1"
        E, d, a = bins(run, f"S2KM__{net}__gypsum__uncorrected_graph__phase1")
        grid = np.array([[np.interp(x, d, a[:, i]) if x <= d.max() else np.nan for i in range(a.shape[1])] for x in D])
        im = ax.pcolormesh(E, np.r_[D - 0.005, D[-1] + 0.005], grid, cmap="RdBu_r", norm=LogNorm(1 / 3, 3), shading="flat")
        r = runs[(runs.domain == "2km") & (runs["mode"] == "gyponly") & (runs.p32 == float(net.split("_p")[1][:3]))
                 & (runs.sigma == 1.0) & (runs.seed == 3)].iloc[0]
        ax.axhline(r.PRV_min, color="k", lw=1.2)
        ax.axhline(r.breakthrough, color="k", ls="--", lw=1.2)
        ax.set_title(f"2 km gypsum-only, {lab}", fontsize=10)
        ax.set_xlabel("distance of fracture centre from inlet (m)")
    axs[0].set_ylabel("fraction of the gypsum dissolved")
    fig.colorbar(im, ax=axs, shrink=0.85, label="PR$_V$ of the 200 m bin / its start\n(blue = flow concentrates)")
    fig.suptitle("Where the focusing is at 2 km. Solid line: network PR$_V$ minimum; dashed: breakthrough", fontsize=10.5)
    fig.savefig(OUT / "scale2km_bins.png", dpi=150)
    plt.close(fig)


def fig_n3():
    net = HERE / "phase1" / "L2_r15_p6.0_sg1.0_seed1"
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), constrained_layout=True)
    sty = {1: dict(ls="-", lw=1.6), 3: dict(ls="-", lw=2.4)}
    col = {("gyponly", 1): "#9bb7cf", ("gyponly", 3): "#1f5f8b", ("gypcal", 1): "#e7b98c", ("gypcal", 3): "#b5541c"}
    for mdir, mo, mlab in (("gypsum", "gyponly", "gypsum-only"), ("gypsum_calcite", "gypcal", "coupled")):
        for tag, n in (("phase1", 1), ("kphi_n3", 3)):
            run = net / f"{mdir}__uncorrected_graph__{tag}"
            if tag == "phase1":
                g = p1[(p1["mode"] == mo) & (p1.p32 == 6) & (p1.sigma == 1) & (p1.seed == 1)]
            else:
                g = pd.read_csv(run / "scale_mechanism_run.csv")
            g = g[g.t_cap <= TCAP].sort_values("k")
            axs[0].plot(g.dissolved, g.pr_frac / g.pr_frac.iloc[0], color=col[(mo, n)], label=f"{mlab}, n = {n}", **sty[n])
            c = pd.read_csv(run / "channelization.csv")
            c = c[c.k.isin(g.k)].sort_values("k")
            axs[1].plot(c.dissolved, c.k_eff_ratio, color=col[(mo, n)], label=f"{mlab}, n = {n}", **sty[n])
    axs[0].axhline(1, color="0.8", lw=0.8)
    axs[0].set_ylabel("PR$_V$ / its start")
    axs[1].set_yscale("log")
    axs[1].set_ylabel("network k$_{eff}$ / start")
    for ax in axs:
        ax.set_xlabel("fraction of the gypsum dissolved")
    axs[0].legend(frameon=False, loc="lower right")
    fig.suptitle("k–φ exponent test, P32 ×6, σ = 1, seed 1, to capacity time 2: n = 1 (ceiling ×10) vs n = 3 (ceiling ×1000)",
                 fontsize=10.5)
    fig.savefig(OUT / "kphi_n3.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig_prv()
    fig_events()
    fig_bins()
    fig_n3()
    print("wrote", OUT)
