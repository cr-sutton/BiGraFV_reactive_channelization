#!/usr/bin/env python3
"""
Who joins and who leaves the flow channel in Phase 1 (per fracture, per run).

Inputs per run RUN = phase1/L2_r15_p{P}_sg{S}_seed{N}/{gypsum|gypsum_calcite}__uncorrected_graph__phase1:
  channel_fractures.csv   in_s90_start, in_s90_peak (90 %-flow set at the start / at the n90 minimum), Q0, Q_peak, rank0, t_half_dissolved_y
  full_mesh_vol_area.uge  cells 1..n_fractures = fractures (volume, centre); connections between fracture cells = intersections
  dfn_properties.h5       initial permeability per cell, aperture b = sqrt(12 k)
  boundary_left_w.ex / boundary_right_e.ex + altered_cells_df.dat   inlet / outlet fractures (parent of the boundary helper cell)

Groups: stayer = start & peak; joiner = peak & not start; leaver = start & not peak; other = neither.
Features per fracture: x of the centre, area, volume, k0, b0 = sqrt(12 k0), rank0/n, degree (intersecting fractures),
  adjacent to a start-set fracture, graph distance (hops over intersections) to the nearest inlet / outlet fracture,
  flow share at start (Q0 / sum Q0) and at the peak (Q_peak / sum Q_peak; the throughflow sums count a fracture on every
  path through it, so these are shares of total throughflow, not of the inflow), t_half_dissolved_y.
Tests: joiners vs others and leavers vs stayers, Mann-Whitney U on all fractures pooled over the 120 runs (the pooled
  p-values over-count independent samples: runs share structure) and on the per-run medians (Wilcoxon signed-rank on the
  paired run medians); effect size = median ratio (pooled median of group A / median of group B, and median over runs of
  the per-run median ratio).

  python3 forsmark_reactive/channel_turnover.py
  -> phase1/channel_turnover.csv, phase1/channel_turnover_summary.csv, phase1/figures/manuscript/channel_turnover.png
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "physics_upscaling"))
from write_corrected_bigrafv_inputs import read_uge  # noqa: E402

P1 = HERE / "phase1"
FIG = P1 / "figures" / "manuscript"
P32S = [4.0, 6.0, 8.0, 16.0]
COL = {4.0: "#86b6ef", 6.0: "#2a78d6", 8.0: "#104281", 16.0: "#d2572a"}
INK, INK2, GRID = "#16181a", "#4c5157", "#e6e5e1"
GROUPS = ["stayer", "joiner", "leaver", "other"]
GCOL = {"stayer": "#104281", "joiner": "#d2572a", "leaver": "#86b6ef", "other": "#b9b8b3"}


def style():
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID,
                         "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.dpi": 130, "savefig.dpi": 200})


def run_dirs(tag="phase1", mode_tags=None):
    """(P32, sigma, seed, mode, path) for every run folder with channel_fractures.csv."""
    out = []
    for d in sorted(P1.glob("L2_r15_p*_sg*_seed*")):
        m = re.match(r"L2_r15_p([\d.]+)_sg([\d.]+)_seed(\d+)", d.name)
        for mode in ("gypsum", "gypsum_calcite"):
            r = d / f"{mode}__uncorrected_graph__{tag}"
            if (r / "channel_fractures.csv").exists():
                out.append((float(m[1]), float(m[2]), int(m[3]), mode, r))
    return out


def load_run(r):
    """Per-fracture frame + fracture graph pieces for one run folder."""
    cf = pd.read_csv(r / "channel_fractures.csv")
    nf = len(cf)
    cells, cons = read_uge(r / "full_mesh_vol_area.uge")
    alt = pd.read_csv(r / "altered_cells_df.dat", sep=r"\s+").set_index("id")
    with h5py.File(r / "dfn_properties.h5") as h:
        ids, k = h["Cell Ids"][:], h["Permeability"][:]
    k = k[np.argsort(ids)][:nf]
    ij = cons[:, :2].astype(int)
    ff = ij[(ij[:, 0] <= nf) & (ij[:, 1] <= nf)] - 1
    ff = np.unique(np.sort(ff, axis=1), axis=0)
    A = coo_matrix((np.ones(len(ff)), (ff[:, 0], ff[:, 1])), shape=(nf, nf)).tocsr()
    A = A + A.T

    def ends(fn):
        ex = [int(l.split()[0]) for l in (r / fn).read_text().splitlines()[1:] if l.strip()]
        return np.unique([int(alt.loc[c, "parent_cell_id"]) - 1 for c in ex])

    inl, outl = ends("boundary_left_w.ex"), ends("boundary_right_e.ex")
    hop_in = dijkstra(A, unweighted=True, indices=inl, min_only=True)
    hop_out = dijkstra(A, unweighted=True, indices=outl, min_only=True)
    df = pd.DataFrame(dict(fracture=cf.fracture, x=cells[:nf, 1], y=cells[:nf, 2], z=cells[:nf, 3], area=cf.area,
                           volume=cells[:nf, 4], k0=k, b0=np.sqrt(12 * k), rank_frac=cf.rank0 / nf,
                           degree=np.asarray(A.sum(1)).ravel(), Q0=cf.Q0, Q_peak=cf.Q_peak,
                           in_start=cf.in_s90_start.astype(bool), in_peak=cf.in_s90_peak.astype(bool),
                           dist_in=hop_in, dist_out=hop_out, t_half=cf.t_half_dissolved_y))
    df["flow_start"] = df.Q0 / df.Q0.sum()
    df["flow_peak"] = df.Q_peak / df.Q_peak.sum()
    nb = np.asarray(A @ df.in_start.values.astype(float)).ravel()
    df["adj_start"] = nb > 0
    return df, A, inl, outl


FEATS = ["x", "area", "volume", "b0", "k0", "rank_frac", "degree", "adj_start", "dist_in", "dist_out", "flow_start",
         "flow_peak", "t_half"]


def group_of(df):
    g = np.where(df.in_start & df.in_peak, "stayer", np.where(df.in_peak, "joiner", np.where(df.in_start, "leaver", "other")))
    return g


def mw(a, b):
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 5 or len(b) < 5:
        return np.nan, np.nan
    return stats.mannwhitneyu(a, b).pvalue, np.median(a) / np.median(b) if np.median(b) != 0 else np.nan


def main():
    style()
    FIG.mkdir(parents=True, exist_ok=True)
    rows, counts = [], []
    for p, s, n, mode, r in run_dirs("phase1"):
        if s not in (0.0, 0.5, 1.0) or p not in P32S:
            continue
        df, *_ = load_run(r)
        df["group"] = group_of(df)
        df["P32"], df["sigma"], df["seed"], df["mode"] = p, s, n, mode
        rows.append(df)
        c = df.group.value_counts()
        counts.append(dict(P32=p, sigma=s, seed=n, mode=mode, n_frac=len(df), **{g: int(c.get(g, 0)) for g in GROUPS},
                           n_start=int(df.in_start.sum()), n_peak=int(df.in_peak.sum())))
    D = pd.concat(rows, ignore_index=True)
    C = pd.DataFrame(counts)
    C["joiner_share_of_peak"] = C.joiner / C.n_peak
    C["leaver_share_of_start"] = C.leaver / C.n_start
    C["stayer_share_of_start"] = C.stayer / C.n_start
    D.to_csv(P1 / "channel_turnover.csv", index=False)
    C.to_csv(P1 / "channel_turnover_counts.csv", index=False)

    def miqr(x):
        q = np.nanpercentile(x, [25, 50, 75])
        return f"{q[1]:.3g} [{q[0]:.3g}-{q[2]:.3g}]"

    S = []
    # counts and shares
    for (p, mode), g in C.groupby(["P32", "mode"]):
        S.append(dict(section="counts", P32=p, mode=mode, item="n_start", value=miqr(g.n_start)))
        S.append(dict(section="counts", P32=p, mode=mode, item="n_peak", value=miqr(g.n_peak)))
        for gr in GROUPS:
            S.append(dict(section="counts", P32=p, mode=mode, item=gr, value=miqr(g[gr])))
        S.append(dict(section="counts", P32=p, mode=mode, item="joiner_share_of_peak", value=miqr(g.joiner_share_of_peak)))
        S.append(dict(section="counts", P32=p, mode=mode, item="leaver_share_of_start", value=miqr(g.leaver_share_of_start)))
    # per-group feature medians (pooled, and median over runs of the per-run median [IQR])
    for mode in ("gypsum", "gypsum_calcite", "all"):
        Dm = D if mode == "all" else D[D["mode"] == mode]
        for gr in GROUPS:
            Dg = Dm[Dm.group == gr]
            runmed = Dg.groupby(["P32", "sigma", "seed", "mode"])[FEATS].median()
            runmean = Dg.groupby(["P32", "sigma", "seed", "mode"])[FEATS].mean()
            for f in FEATS:
                if f == "adj_start":   # a share, not a median
                    S.append(dict(section="group_feature", P32="all", mode=mode, item=f"{gr}:{f}",
                                  value=f"pooled share {Dg[f].astype(float).mean():.4g}; runs {miqr(runmean[f].values.astype(float))}"))
                    continue
                S.append(dict(section="group_feature", P32="all", mode=mode, item=f"{gr}:{f}",
                              value=f"pooled {np.nanmedian(Dg[f].astype(float)):.4g}; runs {miqr(runmed[f].values.astype(float))}"))
    # tests
    tests = [("joiner_vs_other", "joiner", "other"), ("leaver_vs_stayer", "leaver", "stayer")]
    for mode in ("gypsum", "gypsum_calcite", "all"):
        Dm = D if mode == "all" else D[D["mode"] == mode]
        key = ["P32", "sigma", "seed", "mode"]
        med = {gr: Dm[Dm.group == gr].groupby(key)[FEATS].median().astype(float) for gr in GROUPS}
        for name, a, b in tests:
            for f in FEATS:
                xa, xb = Dm[Dm.group == a][f].astype(float).values, Dm[Dm.group == b][f].astype(float).values
                pp, ratio = mw(xa, xb)
                ma, mb = med[a][f].align(med[b][f], join="inner")
                ok = ma.notna() & mb.notna()
                ma, mb = ma[ok], mb[ok]
                pw = stats.wilcoxon(ma, mb).pvalue if len(ma) > 5 and (ma != mb).any() else np.nan
                rr = (ma / mb.replace(0, np.nan)).median() if len(ma) else np.nan
                S.append(dict(section="test", P32="all", mode=mode, item=f"{name}:{f}",
                              value=f"median_a {np.nanmedian(xa):.4g} median_b {np.nanmedian(xb):.4g} pooled_ratio {ratio:.3g} "
                                    f"pooled_p {pp:.2g} run_median_ratio {rr:.3g} run_wilcoxon_p {pw:.2g} n_runs {len(ma)} "
                                    f"na {len(xa)} nb {len(xb)}"))
    pd.DataFrame(S).to_csv(P1 / "channel_turnover_summary.csv", index=False)

    # figure: pooled distributions per group (mode gypsum + calcite pooled), 6 panels
    panels = [("x", "x of fracture centre (m)", False), ("volume", "fracture volume (m$^3$)", True),
              ("b0", "initial aperture $\\sqrt{12k}$ (m)", True), ("rank_frac", "initial throughflow rank / n", False),
              ("dist_in", "graph hops to nearest inlet fracture", False), ("dist_out", "graph hops to nearest outlet fracture", False)]
    fig, axs = plt.subplots(2, 3, figsize=(8.6, 5.2))
    for ax, (f, lab, lg) in zip(axs.ravel(), panels):
        data = []
        for gr in GROUPS:
            v = D[D.group == gr][f].astype(float).values
            v = v[np.isfinite(v)]
            data.append(np.log10(v[v > 0]) if lg else v)
        bp = ax.boxplot(data, vert=True, showfliers=False, patch_artist=True, widths=0.6,
                        medianprops=dict(color=INK, lw=1.2), whiskerprops=dict(color=INK2), capprops=dict(color=INK2))
        for b, gr in zip(bp["boxes"], GROUPS):
            b.set(facecolor=GCOL[gr], edgecolor=INK2, alpha=0.9)
        ax.set_xticks(range(1, 5)); ax.set_xticklabels(GROUPS, rotation=20)
        ax.set_ylabel(("log$_{10}$ " if lg else "") + lab)
        ax.grid(axis="x", visible=False)
    n = D.groupby("group").size()
    fig.suptitle("Phase 1, all P32, sigma and chemistries pooled; fractures: " + ", ".join(f"{g} {n[g]:,}" for g in GROUPS), fontsize=8, color=INK2)
    fig.tight_layout()
    fig.savefig(FIG / "channel_turnover.png")
    # second figure: x position histograms of joiners / leavers by P32
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    bins = np.linspace(-500, 500, 21)
    for ax, gr in zip(axs, ("joiner", "leaver")):
        for p in P32S:
            sub = D[(D.group == gr) & (D.P32 == p)]
            nn = D[(D.P32 == p) & (D.group == gr)].groupby(["sigma", "seed", "mode"]).ngroups
            h, _ = np.histogram(sub.x, bins)
            ax.step(bins[:-1], h / max(nn, 1), where="post", color=COL[p], label=f"P32 x{p:g}")
        ax.set_title(gr + "s", fontsize=8); ax.set_xlabel("x (m)")
    axs[0].set_ylabel("fractures per run per 50 m"); axs[0].legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "channel_turnover_x.png")
    print(C.groupby(["P32", "mode"])[["n_start", "n_peak"] + GROUPS + ["joiner_share_of_peak", "leaver_share_of_start"]].median().round(3).to_string())


if __name__ == "__main__":
    main()
