#!/usr/bin/env python3
"""
What explains the run-to-run variation of the channelization depth at a fixed ceiling?

  depth = min_k pr_fracture_vol(k) / pr_fracture_vol(0)      (channelization.csv; pr_fracture_vol = (sum Q)^2 / sum(Q^2 / w),
                                                              w = fracture volume share)
  resid = depth - median(depth of the runs with the same (mode, tag, P32))        ceiling / chemistry / P32 effect removed
  resid_pair = depth(coupled) - depth(gypsum-only, same network and tag)          coupled runs only, paired network

Features of the INITIAL state per run (from channel_fractures.csv, the UGE, dfn_properties.h5; channel = initial 90 %-flow set S):
  vol_share_S        sum of fracture volume in S / total fracture volume (the initial gypsum inventory is proportional to volume
                     because porosity and gypsum volume fraction start uniform, so this is also the inventory share held by S)
  n_S, mean_area_S   number of channel fractures and their mean area (m2)
  b_ratio_med        median b in S / median b in the rest, b = sqrt(12 k) (k from dfn_properties.h5)
  b_ratio_flow       exp( sum Q0 ln b / sum Q0 - median ln b of all fractures ): flow-weighted mean ln b against the network median
  sd_lnb_S, sd_lnb_all   sd of ln b inside S and over the whole network
  vol_S_inlet3, vol_S_outlet3   share of the S volume with centre x < -L/6 (inlet third) / x > L/6 (outlet third)
  n_inlet90, n_outlet90  fewest inlet (outlet) fractures whose Q0 sum to 90 % of the Q0 sum over the inlet (outlet) fractures
  path_hops, path_bneck   widest path from any inlet to any outlet fracture (node weight Q0): hops of the shortest path inside
                     the subgraph of fractures with Q0 >= the largest threshold that still connects them; bneck = that threshold
                     divided by max Q0
  S_xextent          x-extent of the S centres / L
  gini, top1_share   flow Gini and share of the largest fracture throughflow (channelization.csv row 0)
  pr_vol0            pr_fracture_vol at k = 0 (initial focusing against volume)
  sigma, P32         network parameters
Statistics: Spearman rho (p, n) of resid with each feature, pooled and with the feature centred on its (mode, tag, P32) group median
  ("within"); a forward-selected OLS (<= 3 features, selected inside each training fold, 3-fold-inner-free LOO criterion) with
  leave-one-P32-out R2 = 1 - SSE/SST (SST about zero, since resid is centred); pooled-over-ceilings OLS depth ~ condition fixed
  effects + P32 fixed effects + feature (t-test p of the feature coefficient).

  python3 forsmark_reactive/depth_variability.py
  -> phase1/depth_variability.csv, phase1/depth_variability_summary.csv, phase1/figures/manuscript/depth_variability.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse.csgraph import connected_components, dijkstra

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from channel_turnover import COL, FIG, GRID, INK, INK2, P1, load_run, run_dirs, style  # noqa: E402

L = 1000.0
CEIL = {("gypsum", "phase1"): 10.0, ("gypsum_calcite", "phase1"): 5.5, ("gypsum", "phase2_phi005"): 20.0,
        ("gypsum_calcite", "phase2_phi005"): 10.6, ("gypsum_calcite", "phase2_co3lo"): 10.0}   # nominal, from the brief
FEATS = ["vol_share_S", "n_S", "mean_area_S", "b_ratio_med", "b_ratio_flow", "sd_lnb_S", "sd_lnb_all", "vol_S_inlet3",
         "vol_S_outlet3", "n_inlet90", "n_outlet90", "path_hops", "path_bneck", "S_xextent", "gini", "top1_share", "pr_vol0",
         "sigma", "P32"]


def n90_ends(Q, idx):
    q = np.sort(Q[idx])[::-1]
    return int(np.searchsorted(np.cumsum(q) / q.sum(), 0.9) + 1)


def widest_path(A, Q, inl, outl):
    """Largest Q threshold at which inlet and outlet fractures connect, and the hop length of the shortest path there."""
    cand = np.unique(Q[Q > 0])
    lo, hi, best = 0, len(cand) - 1, None
    def ok(t):
        keep = np.where(Q >= t)[0]
        sub = A[keep][:, keep]
        nc, lab = connected_components(sub, directed=False)
        li = set(lab[np.isin(keep, inl)]); lo_ = set(lab[np.isin(keep, outl)])
        return bool(li & lo_), keep, sub
    while lo <= hi:
        mid = (lo + hi) // 2
        good, keep, sub = ok(cand[mid])
        if good:
            best, lo = (cand[mid], keep, sub), mid + 1
        else:
            hi = mid - 1
    if best is None:
        return np.nan, np.nan
    t, keep, sub = best
    si = np.where(np.isin(keep, inl))[0]; so = np.where(np.isin(keep, outl))[0]
    d = dijkstra(sub, unweighted=True, indices=si, min_only=True)
    return float(d[so].min()), float(t / Q.max())


def features(r):
    df, A, inl, outl = load_run(r)
    ch = pd.read_csv(r / "channelization.csv")
    S, Q = df.in_start.values, df.Q0.values
    lnb = np.log(df.b0.values)
    f = dict(depth=ch.pr_fracture_vol.min() / ch.pr_fracture_vol.iloc[0], n_frac=len(df))
    f["vol_share_S"] = df.volume[S].sum() / df.volume.sum()
    f["n_S"] = int(S.sum()); f["mean_area_S"] = df.area[S].mean()
    f["b_ratio_med"] = np.exp(np.median(lnb[S]) - np.median(lnb[~S]))
    f["b_ratio_flow"] = np.exp((Q * lnb).sum() / Q.sum() - np.median(lnb))
    f["sd_lnb_S"] = lnb[S].std(); f["sd_lnb_all"] = lnb.std()
    vS = df.volume[S].sum()
    f["vol_S_inlet3"] = df.volume[S & (df.x < -L / 6)].sum() / vS
    f["vol_S_outlet3"] = df.volume[S & (df.x > L / 6)].sum() / vS
    f["n_inlet90"], f["n_outlet90"] = n90_ends(Q, inl), n90_ends(Q, outl)
    f["path_hops"], f["path_bneck"] = widest_path(A, Q, inl, outl)
    f["S_xextent"] = (df.x[S].max() - df.x[S].min()) / L
    f["gini"] = ch.flow_gini.iloc[0]; f["top1_share"] = ch.top1_share.iloc[0]; f["pr_vol0"] = ch.pr_fracture_vol.iloc[0]
    return f


def ols(X, y):
    X1 = np.column_stack([np.ones(len(X)), X])
    b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    return b


def loo_sse(X, y):
    X1 = np.column_stack([np.ones(len(X)), X])
    H = X1 @ np.linalg.pinv(X1.T @ X1) @ X1.T
    res = y - H @ y
    return float(np.sum((res / (1 - np.diag(H))) ** 2))


def forward(X, y, names, kmax=3):
    sel = []
    best = float(np.sum(y ** 2))
    while len(sel) < kmax:
        c = [(loo_sse(X[:, sel + [j]], y), j) for j in range(X.shape[1]) if j not in sel]
        s, j = min(c)
        if s >= best * 0.98:
            break
        sel.append(j); best = s
    return sel


def lopo(D, y, cols, grp):
    """Leave-one-P32-out with in-fold forward selection; X standardised with the training mean/sd."""
    pred = np.full(len(D), np.nan); chosen = []
    X = D[cols].values.astype(float)
    for p in np.unique(D.P32):
        te = (D.P32 == p).values
        mu, sd = np.nanmean(X[~te], 0), np.nanstd(X[~te], 0) + 1e-12
        Z = (X - mu) / sd
        Z = np.nan_to_num(Z)
        sel = forward(Z[~te], y[~te], cols)
        chosen.append([cols[j] for j in sel])
        b = ols(Z[~te][:, sel], y[~te]) if sel else np.array([y[~te].mean()])
        pred[te] = b[0] + (Z[te][:, sel] @ b[1:] if sel else 0)
    ok = np.isfinite(y)
    return 1 - np.sum((y[ok] - pred[ok]) ** 2) / np.sum(y[ok] ** 2), chosen, pred


def main():
    style(); FIG.mkdir(parents=True, exist_ok=True)
    rows = []
    for tag in ("phase1", "phase2_phi005", "phase2_co3lo"):
        for p, s, n, mode, r in run_dirs(tag):
            f = features(r)
            f.update(P32=p, sigma=s, seed=n, mode=mode, tag=tag, ceiling=CEIL[(mode, tag)])
            rows.append(f)
    D = pd.DataFrame(rows)
    D["cond"] = D["mode"] + "|" + D.tag
    D["resid"] = D.depth - D.groupby(["mode", "tag", "P32"]).depth.transform("median")
    gyp = D[D["mode"] == "gypsum"].set_index(["tag", "P32", "sigma", "seed"]).depth
    key = pd.MultiIndex.from_frame(D[["tag", "P32", "sigma", "seed"]])
    pair = gyp.reindex(key).values
    D["resid_pair"] = np.where(D["mode"] == "gypsum_calcite", D.depth - pair, np.nan)
    D["resid_pair_c"] = D.resid_pair - D.groupby(["mode", "tag", "P32"]).resid_pair.transform("median")
    for c in FEATS:
        D[c + "_w"] = D[c] - D.groupby(["mode", "tag", "P32"])[c].transform("median")
    D.to_csv(P1 / "depth_variability.csv", index=False)
    print(D.groupby(["cond"]).depth.describe().round(3).to_string())

    S = []
    def add(sec, cond, item, val, p=np.nan, n=np.nan):
        S.append(dict(section=sec, cond=cond, item=item, value=val, p=p, n=n))
    conds = {"phase1 gypsum": D[(D.tag == "phase1") & (D["mode"] == "gypsum")],
             "phase1 gypcal": D[(D.tag == "phase1") & (D["mode"] == "gypsum_calcite")],
             "phase2 phi005 gypsum": D[(D.tag == "phase2_phi005") & (D["mode"] == "gypsum")],
             "phase2 phi005 gypcal": D[(D.tag == "phase2_phi005") & (D["mode"] == "gypsum_calcite")],
             "phase2 co3lo gypcal": D[D.tag == "phase2_co3lo"], "all": D}
    sub = (D.tag == "phase1") & (D.sigma == 1.0) & (D.seed <= 3)      # the 12 networks that Phase 2 re-ran
    conds["phase1 gypsum sg1 seeds1-3"] = D[sub & (D["mode"] == "gypsum")]
    conds["phase1 gypcal sg1 seeds1-3"] = D[sub & (D["mode"] == "gypsum_calcite")]
    for name, d in conds.items():
        add("depth", name, "median [min-max] sd", f"{d.depth.median():.3f} [{d.depth.min():.3f}-{d.depth.max():.3f}] sd {d.depth.std():.3f}", n=len(d))
        add("depth", name, "resid sd", d.resid.std(), n=len(d))
        for tgt in ["resid"] + (["resid_pair_c"] if "gypcal" in name else []):
            for c in FEATS:
                for suffix, lab in (("", "raw"), ("_w", "within")):
                    if c in ("P32",) and suffix == "_w":
                        continue
                    x = d[c + suffix].values.astype(float); y = d[tgt].values
                    ok = np.isfinite(x) & np.isfinite(y)
                    if ok.sum() > 5 and np.ptp(x[ok]) > 0:
                        rho, p = stats.spearmanr(x[ok], y[ok])
                        add(f"spearman_{tgt}_{lab}", name, c, rho, p, int(ok.sum()))
    # does a network keep its depth rank across conditions (same network, different chemistry / porosity)?
    W = D.pivot_table(index=["P32", "sigma", "seed"], columns="cond", values="resid")
    for a, b in [("gypsum|phase1", "gypsum_calcite|phase1"), ("gypsum|phase1", "gypsum|phase2_phi005"),
                 ("gypsum_calcite|phase1", "gypsum_calcite|phase2_phi005"), ("gypsum_calcite|phase1", "gypsum_calcite|phase2_co3lo"),
                 ("gypsum|phase2_phi005", "gypsum_calcite|phase2_phi005")]:
        ok = W[a].notna() & W[b].notna()
        rho, pv = stats.spearmanr(W[a][ok], W[b][ok])
        add("cross_condition_resid_spearman", f"{a} vs {b}", "rho", rho, pv, int(ok.sum()))
    # multivariable, leave-one-P32-out
    for name in ["phase1 gypsum", "phase1 gypcal", "all"]:
        d = conds[name].reset_index(drop=True)
        cols = [c + "_w" for c in FEATS if c not in ("P32",)]
        y = d.resid.values
        r2, chosen, pred = lopo(d, y, cols, None)
        add("lopo", name, "R2 (resid, features centred in group)", r2, n=len(d))
        add("lopo", name, "features selected per held-out P32", "; ".join(f"{p:g}: {','.join(c.replace('_w','') for c in ch) or '-'}" for p, ch in zip(np.unique(d.P32), chosen)))
        if name != "all":
            Z = np.nan_to_num((d[cols] - d[cols].mean()) / d[cols].std()).astype(float)
            sel = forward(Z, y, cols)
            b = ols(Z[:, sel], y)
            yh = b[0] + Z[:, sel] @ b[1:]
            add("fit_all", name, "selected", ",".join(cols[j].replace("_w", "") for j in sel))
            add("fit_all", name, "in-sample R2", 1 - np.sum((y - yh) ** 2) / np.sum(y ** 2))
            for j, bb in zip(sel, b[1:]):
                add("fit_all", name, "std coef " + cols[j].replace("_w", ""), bb)
    # across ceilings: depth ~ condition x P32 fixed effects + feature
    d = D.copy()
    FE = pd.get_dummies(d[["cond"]].assign(P=d.P32.astype(str)), drop_first=False).astype(float)
    FE = pd.get_dummies(d.cond + "|" + d.P32.astype(str)).astype(float).values
    for c in FEATS:
        if c == "P32":
            continue
        x = d[c].values.astype(float); ok = np.isfinite(x)
        X = np.column_stack([FE[ok], (x[ok] - x[ok].mean()) / x[ok].std()]); y = d.depth.values[ok]
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ b; dof = len(y) - np.linalg.matrix_rank(X)
        cov = np.linalg.pinv(X.T @ X) * (res @ res / dof)
        t = b[-1] / np.sqrt(cov[-1, -1])
        add("pooled_fixed_effects", "all conditions x P32", c, b[-1], 2 * stats.t.sf(abs(t), dof), int(ok.sum()))
    # feature relation to ceiling-removed depth in each condition separately (sigma-controlled): partial via same OLS per cond
    pd.DataFrame(S).to_csv(P1 / "depth_variability_summary.csv", index=False)

    # figure: resid vs top 3 features (by |rho_within| in phase1 gypcal+gypsum), panels = chemistry x feature
    SS = pd.DataFrame(S)
    sp = SS[(SS.section == "spearman_resid_within") & SS.cond.isin(["phase1 gypsum", "phase1 gypcal"])]
    top = sp.assign(a=sp.value.abs()).groupby("item").a.mean().sort_values(ascending=False).index[:3].tolist()
    fig, axs = plt.subplots(2, 3, figsize=(8.6, 5.2))
    for i, nm in enumerate(["phase1 gypsum", "phase1 gypcal"]):
        d = conds[nm]
        for j, c in enumerate(top):
            ax = axs[i, j]
            for p in sorted(d.P32.unique()):
                s = d[d.P32 == p]
                ax.scatter(s[c], s.resid, s=14, color=COL[p], edgecolor="none", alpha=0.9, label=f"x{p:g}")
            x, y = d[c].values.astype(float), d.resid.values
            ok = np.isfinite(x)
            rho, pv = stats.spearmanr(x[ok], y[ok])
            ax.axhline(0, color=INK2, lw=0.6)
            ax.set_xlabel(c); ax.set_ylabel("depth - group median" if j == 0 else "")
            ax.set_title(f"{nm}: rho {rho:+.2f}, p {pv:.2g}, n {ok.sum()}", fontsize=7, color=INK2)
    axs[0, 0].legend(frameon=False, fontsize=6, ncol=2)
    fig.tight_layout(); fig.savefig(FIG / "depth_variability.png")
    print("top features", top)


if __name__ == "__main__":
    main()
