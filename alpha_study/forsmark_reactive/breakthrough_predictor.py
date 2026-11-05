#!/usr/bin/env python3
"""
Can the dissolved fraction at gypsum breakthrough be predicted from the INITIAL channel state alone?

Targets (stage_events_clocks.csv, per run): d_bt = `dissolved` at event `breakthrough`; d_prv = `dissolved` at `PRV_min`.
Predictors (initial state only): first row of channelization.csv (flow_gini, n90_share, n90_vol_share, pr_fracture_vol,
dQ_P32, top1_share, backbone_share), network_stats.json (n_fractures, n_intersections, mean_degree, n_inlet_fractures,
n_outlet_fractures, node_disjoint_paths, edge_disjoint_paths, backbone_fraction, n_dead_end_fractures), sigma, p32.
Chemistry indicator (gypcal = 1) is added in the pooled fits.

Models, each fitted per chemistry ("chem") and pooled over both chemistries with the indicator ("pool"):
  S_<x>  d = b0 + b1 x                                   (one per predictor)
  M2     d = a x,  x = n90_vol_share0, no intercept      (pool: d = a x + c*chem, no intercept)
  M3     ridge (alpha = 1) on standardised predictors, at most 3 chosen by forward selection (greedy, adds a predictor only
         if it lowers the inner CV MAE by > 1 %), selection scored by leave-one-P32-level-out inside the training levels;
         pool always includes the chemistry indicator on top of the 3.
Validation: leave-one-P32-level-out over the 120 Phase 1 runs (train 3 levels, predict the 4th).  R2 = 1 - SS_res/SS_tot
about the mean of the evaluated set (held-out level, or all runs for "overall"), MAE in dissolved fraction, Spearman rho.
Out-of-sample: models fitted on all 120 Phase 1 runs predict the Phase 2 runs (phase2_phi005, phase2_co3lo; sigma = 1 only,
so no sigma variation there).  Phase 2 initial states are read from their own channelization.csv.

  python3 forsmark_reactive/breakthrough_predictor.py
  -> phase1/breakthrough_predictor.csv, phase1/breakthrough_predictor_summary.csv,
     phase1/figures/manuscript/breakthrough_predictor_{d_bt,d_prv}.png
"""
from __future__ import annotations

import json
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
CH = ["flow_gini", "n90_share", "n90_vol_share", "pr_fracture_vol", "dQ_P32", "top1_share", "backbone_share"]
NS = ["n_fractures", "n_intersections", "mean_degree", "n_inlet_fractures", "n_outlet_fractures",
      "node_disjoint_paths", "edge_disjoint_paths", "backbone_fraction", "n_dead_end_fractures"]
PRED = CH + NS + ["sigma", "p32"]
COL = {4.0: "#86b6ef", 6.0: "#2a78d6", 8.0: "#104281", 16.0: "#d2572a"}
INK, INK2, GRID = "#16181a", "#4c5157", "#e6e5e1"
CHEMDIR = {"gyponly": "gypsum", "gypcal": "gypsum_calcite"}
TARGETS = {"d_bt": "breakthrough", "d_prv": "PRV_min"}
RIDGE = 1.0


# ---------------------------------------------------------------- data
def load():
    ev = pd.read_csv(P1 / "stage_events_clocks.csv")
    rows = []
    for (tag, mode, p32, sg, seed), g in ev.groupby(["tag", "mode", "p32", "sigma", "seed"]):
        net = P1 / f"L2_r15_p{p32}_sg{sg}_seed{int(seed)}"
        ch = pd.read_csv(net / f"{CHEMDIR[mode]}__uncorrected_graph__{tag}" / "channelization.csv").iloc[0]
        ns = json.loads((net / "network_stats.json").read_text())
        r = dict(tag=tag, mode=mode, p32=p32, sigma=sg, seed=int(seed), chem=float(mode == "gypcal"))
        r.update({c: ch[c] for c in CH})
        r.update({c: ns[c] for c in NS})
        for t, e in TARGETS.items():
            r[t] = float(g.loc[g.event == e, "dissolved"].iloc[0])
        rows.append(r)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- fitting
def ridge_fit(X, y, alpha=RIDGE):
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Z = (X - mu) / sd
    ym = y.mean()
    w = np.linalg.solve(Z.T @ Z + alpha * np.eye(Z.shape[1]), Z.T @ (y - ym))
    return lambda Xn: ((Xn - mu) / sd) @ w + ym


def ols_fit(X, y, intercept=True):
    A = np.column_stack([np.ones(len(X)), X]) if intercept else X
    b = np.linalg.lstsq(A, y, rcond=None)[0]
    return (lambda Xn: np.column_stack([np.ones(len(Xn)), Xn]) @ b) if intercept else (lambda Xn: Xn @ b), b


def forward_select(df, target, base, kmax=3):
    """Greedy forward selection scored by leave-one-P32-level-out MAE inside df (the training set)."""
    levels = sorted(df.p32.unique())
    chosen, best = [], np.inf
    for _ in range(kmax):
        cand = []
        for c in PRED:
            if c in chosen:
                continue
            cols = base + chosen + [c]
            err = []
            for L in levels:
                tr, te = df[df.p32 != L], df[df.p32 == L]
                f = ridge_fit(tr[cols].values.astype(float), tr[target].values)
                err.append(np.abs(f(te[cols].values.astype(float)) - te[target].values))
            cand.append((np.concatenate(err).mean(), c))
        m, c = min(cand)
        if m < 0.99 * best or not chosen:
            chosen.append(c)
            best = m
        else:
            break
    return chosen


def fit_predict(model, scope, tr, te, target):
    """Return predictions for te (and the predictor list used) from a model fitted on tr."""
    base = ["chem"] if scope == "pool" else []
    if model.startswith("S_"):
        cols = base + [model[2:]]
        fn, _ = ols_fit(tr[cols].values.astype(float), tr[target].values)
        return fn(te[cols].values.astype(float)), cols
    if model == "M2":
        cols = base + ["n90_vol_share"]
        fn, _ = ols_fit(tr[cols].values.astype(float), tr[target].values, intercept=False)
        return fn(te[cols].values.astype(float)), cols
    sel = forward_select(tr, target, base)
    cols = base + sel
    f = ridge_fit(tr[cols].values.astype(float), tr[target].values)
    return f(te[cols].values.astype(float)), cols


def run_scope(df, target, model, scope):
    """CV predictions on Phase 1 rows (index-aligned) and OOS predictions on Phase 2 rows; selections used."""
    p1 = df[df.tag == "phase1"]
    p2 = df[df.tag != "phase1"]
    groups = [(None, p1)] if scope == "pool" else [(m, p1[p1["mode"] == m]) for m in ("gyponly", "gypcal")]
    out, sel = {}, {}
    for m, sub in groups:
        for L in sorted(sub.p32.unique()):
            tr, te = sub[sub.p32 != L], sub[sub.p32 == L]
            pr, cols = fit_predict(model, scope, tr, te, target)
            out.update(dict(zip(te.index, pr)))
            sel[(m, L)] = cols
        te = p2 if m is None else p2[p2["mode"] == m]
        pr, cols = fit_predict(model, scope, sub, te, target)
        out.update(dict(zip(te.index, pr)))
        sel[(m, "full")] = cols
    return pd.Series(out), sel


def metrics(o, p):
    o, p = np.asarray(o), np.asarray(p)
    ss = ((o - o.mean()) ** 2).sum()
    r2 = 1 - ((o - p) ** 2).sum() / ss if ss > 0 else np.nan
    rho = spearmanr(o, p)[0] if len(o) > 2 and np.ptp(p) > 0 else np.nan
    return r2, np.abs(o - p).mean(), rho


# ---------------------------------------------------------------- main
def main():
    df = load()
    assert np.isfinite(df[PRED + list(TARGETS)].values.astype(float)).all()
    models = ["M2", "M3"] + ["S_" + c for c in PRED]
    wide, summ, picks = df.copy(), [], []
    for target in TARGETS:
        for scope in ("chem", "pool"):
            for model in models:
                pred, sel = run_scope(df, target, model, scope)
                pred = pred.reindex(df.index)
                wide[f"{target}__{scope}__{model}"] = pred
                if model == "M3":
                    for (m, L), cols in sel.items():
                        picks.append(dict(target=target, scope=scope, chem=m or "pool", fit=L, predictors=" ".join(cols)))
                sets = [("overall", df.tag == "phase1")]
                sets += [(f"heldout_p32_{int(L)}", (df.tag == "phase1") & (df.p32 == L)) for L in (4, 6, 8, 16)]
                sets += [("oos_phase2_all", df.tag != "phase1"), ("oos_phase2_phi005", df.tag == "phase2_phi005"),
                         ("oos_phase2_co3lo", df.tag == "phase2_co3lo")]
                for name, msk in sets:
                    for chem in ("all", "gyponly", "gypcal"):
                        mm = msk & ((df["mode"] == chem) if chem != "all" else True)
                        if mm.sum() < 3:
                            continue
                        r2, mae, rho = metrics(df.loc[mm, target], pred.loc[mm])
                        summ.append(dict(target=target, scope=scope, model=model, subset=name, chem=chem, n=int(mm.sum()),
                                         R2=r2, MAE=mae, spearman=rho))
    wide.to_csv(P1 / "breakthrough_predictor.csv", index=False)
    S = pd.DataFrame(summ)
    S.to_csv(P1 / "breakthrough_predictor_summary.csv", index=False)
    pd.DataFrame(picks).to_csv(P1 / "breakthrough_predictor_m3_selection.csv", index=False)
    for target in TARGETS:
        figure(wide, S, target)
    print(S[(S.subset == "overall") & (S.chem == "all")].pivot_table(index=["target", "model"], columns="scope",
                                                                     values=["R2", "MAE"]).round(3).to_string())


def figure(wide, S, target):
    rows = [("M2", "chem", "d = a n90_vol_share0"), ("M3", "chem", "ridge, <=3 predictors (fwd. sel.)"),
            ("S_top1_share", "chem", "d = b0 + b1 top1_share0")]
    fig, axs = plt.subplots(3, 2, figsize=(8.2, 10.4), sharex=True, sharey=True)
    lim = [0, wide[target].max() * 1.08]
    for i, (model, scope, lab) in enumerate(rows):
        for j, mode in enumerate(("gyponly", "gypcal")):
            ax = axs[i, j]
            ax.plot(lim, lim, color=INK2, lw=0.9, ls="--", zorder=1)
            d = wide[wide["mode"] == mode]
            pred = d[f"{target}__{scope}__{model}"]
            for L, c in COL.items():
                s = d[(d.tag == "phase1") & (d.p32 == L)]
                ax.scatter(s[target], s[f"{target}__{scope}__{model}"], s=22, color=c, alpha=0.85, lw=0, label=f"P32 x{int(L)}", zorder=3)
            for L, c in COL.items():
                s = d[(d.tag != "phase1") & (d.p32 == L)]
                if len(s):
                    ax.scatter(s[target], s[f"{target}__{scope}__{model}"], s=34, facecolor="none", edgecolor=c, lw=1.3, zorder=4)
            q = S[(S.target == target) & (S.scope == scope) & (S.model == model) & (S.chem == mode)]
            a = q[q.subset == "overall"].iloc[0]
            o = q[q.subset == "oos_phase2_all"].iloc[0]
            ax.text(0.04, 0.96, f"CV  R$^2$ {a.R2:.2f}  MAE {a.MAE:.3f}\nPhase 2  R$^2$ {o.R2:.2f}  MAE {o.MAE:.3f}",
                    transform=ax.transAxes, va="top", fontsize=8.5, color=INK)
            ax.set_title(f"{'gypsum only' if mode == 'gyponly' else 'gypsum + calcite'}: {lab}", fontsize=9, color=INK)
            ax.set_xlim(lim); ax.set_ylim(lim)
            ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            for sp in ("left", "bottom"):
                ax.spines[sp].set_color(INK2)
            ax.tick_params(colors=INK2, labelsize=8.5)
            if j == 0:
                ax.set_ylabel("predicted (leave-one-P32-out)", color=INK2, fontsize=9)
            if i == 2:
                ax.set_xlabel(f"observed {target}", color=INK2, fontsize=9)
    h, l = axs[0, 0].get_legend_handles_labels()
    h.append(plt.Line2D([], [], marker="o", ls="", mfc="none", mec=INK2, label="Phase 2 (open)"))
    fig.legend(h, [x.get_label() for x in h], loc="lower center", ncol=5, frameon=False, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG / f"breakthrough_predictor_{target}.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
