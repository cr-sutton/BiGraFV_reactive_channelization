#!/usr/bin/env python3
"""
Does the EARLY flow redistribution predict the channelization depth?  (5 Nov 2026, follow-up to depth_variability.py, which found
that no initial-state feature predicts depth out of sample.)

  depth   = min_k PR_V(k) / PR_V(0)   (channelization.csv pr_fracture_vol; same as depth_variability.py, rows read from
            phase1/depth_variability.csv, which also holds resid = depth - median of the same (mode, tag, P32) group)
  d_min   = dissolved fraction at that minimum
Early features at a dissolved fraction d* (linear interpolation of channelization.csv on `dissolved`), d* = 0.02, 0.05, 0.10, 0.20:
  dPRV    PR_V(d*) / PR_V(0) - 1        focusing so far (same measure as depth: a partial trajectory, i.e. an early warning)
  dn90    n90(d*) / n90(0) - 1
  dtop1   top1_share(d*) - top1_share(0)
  dgini   flow_gini(d*) - flow_gini(0)
  keff    k_eff_ratio(d*)
  ovl     overlap0(d*)
Each feature is also centred on its (mode, tag, P32) group median (suffix _w), like resid.
Statistics per d*: n runs whose minimum comes after d* (only those are a prediction), Spearman rho of resid with each _w feature
(pooled), within-condition rho for dPRV, and leave-one-P32-out R2 with in-fold forward selection (<= 3 features), using
depth_variability.lopo (R2 = 1 - SSE / sum resid^2).  Also the share of the eventual drop already reached at d*:
(1 - PR_V(d*)/PR_V(0)) / (1 - depth).

  python3 forsmark_reactive/early_redistribution_predictor.py
  -> phase1/early_redistribution.csv, phase1/early_redistribution_summary.csv, phase1/figures/manuscript/early_redistribution.png
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from channel_turnover import COL, FIG, GRID, INK, INK2, P1, style  # noqa: E402
from depth_variability import lopo  # noqa: E402

DSTAR = [0.02, 0.05, 0.10, 0.20]
F = ["dPRV", "dn90", "dtop1", "dgini", "keff", "ovl"]
TAGRUN = lambda r: P1 / f"L2_r15_p{r.P32:.1f}_sg{r.sigma:.1f}_seed{int(r.seed)}" / f"{r['mode']}__uncorrected_graph__{r.tag}"


def lopo_fixed(D, y, cols):
    """Leave-one-P32-out OLS with a FIXED feature set (standardised on the training fold); R2 = 1 - SSE / sum y^2."""
    X = D[cols].values.astype(float); pred = np.full(len(D), np.nan)
    for p in np.unique(D.P32):
        te = (D.P32 == p).values
        mu, sd = X[~te].mean(0), X[~te].std(0) + 1e-12
        A = np.column_stack([np.ones((~te).sum()), (X[~te] - mu) / sd])
        b = np.linalg.lstsq(A, y[~te], rcond=None)[0]
        pred[te] = b[0] + ((X[te] - mu) / sd) @ b[1:]
    return 1 - np.sum((y - pred) ** 2) / np.sum(y ** 2), pred


def early(ch, ds):
    d = ch.dissolved.values
    g = lambda c: float(np.interp(ds, d, ch[c].values))
    p0, n0, t0, g0 = ch.pr_fracture_vol.iloc[0], ch.n90.iloc[0], ch.top1_share.iloc[0], ch.flow_gini.iloc[0]
    return dict(dPRV=g("pr_fracture_vol") / p0 - 1, dn90=g("n90") / n0 - 1, dtop1=g("top1_share") - t0, dgini=g("flow_gini") - g0,
                keff=g("k_eff_ratio"), ovl=g("overlap0"))


def main():
    style(); FIG.mkdir(parents=True, exist_ok=True)
    D = pd.read_csv(P1 / "depth_variability.csv")[["P32", "sigma", "seed", "mode", "tag", "cond", "depth", "resid"]]
    rows = []
    for _, r in D.iterrows():
        ch = pd.read_csv(TAGRUN(r) / "channelization.csv").sort_values("k")
        ch = ch[np.isfinite(ch.dissolved)]
        i = ch.pr_fracture_vol.idxmin()
        base = dict(r); base["d_min"] = float(ch.loc[i, "dissolved"])
        for ds in DSTAR:
            e = early(ch, ds)
            rows.append({**base, "dstar": ds, **e, "drop_reached": (-e["dPRV"]) / (1 - r.depth) if r.depth < 1 else np.nan})
    E = pd.DataFrame(rows)
    for c in F:
        E[c + "_w"] = E[c] - E.groupby(["dstar", "mode", "tag", "P32"])[c].transform("median")
    E.to_csv(P1 / "early_redistribution.csv", index=False)
    S = []
    add = lambda **k: S.append(k)
    print("d_min median [IQR] by cond:")
    m = E[E.dstar == DSTAR[0]]
    for c, g in m.groupby("cond"):
        add(dstar=np.nan, scope=c, item="d_min median [IQR]", value=f"{g.d_min.median():.3f} [{g.d_min.quantile(.25):.3f}-{g.d_min.quantile(.75):.3f}]", n=len(g))
        print(" ", c, S[-1]["value"], len(g))
    for ds in DSTAR:
        x = E[(E.dstar == ds) & (E.d_min > ds)].reset_index(drop=True)
        add(dstar=ds, scope="pooled", item="n runs with minimum after d*", value=len(x), n=len(E[E.dstar == ds]))
        add(dstar=ds, scope="pooled", item="drop reached median [IQR]",
            value=f"{x.drop_reached.median():.3f} [{x.drop_reached.quantile(.25):.3f}-{x.drop_reached.quantile(.75):.3f}]", n=len(x))
        for c in F:
            rho, p = stats.spearmanr(x[c + "_w"], x.resid, nan_policy="omit")
            add(dstar=ds, scope="pooled", item=f"spearman resid vs {c}_w", value=rho, p=p, n=len(x))
        for cond, g in x.groupby("cond"):
            rho, p = stats.spearmanr(g.dPRV, g.depth)
            add(dstar=ds, scope=cond, item="spearman depth vs dPRV (raw, within condition)", value=rho, p=p, n=len(g))
        r2, chosen, pred = lopo(x, x.resid.values, [c + "_w" for c in F], None)
        add(dstar=ds, scope="pooled", item="LOPO R2 (forward, <=3 of 6 _w)", value=r2, n=len(x),
            chosen="; ".join(",".join(c) for c in chosen))
        r2b, predb = lopo_fixed(x, x.resid.values, ["dPRV_w"])
        add(dstar=ds, scope="pooled", item="LOPO R2 (dPRV_w only)", value=r2b, n=len(x))
        r2c, chosen_c, _ = lopo(x, x.resid.values, [c + "_w" for c in F if c != "dPRV"], None)
        add(dstar=ds, scope="pooled", item="LOPO R2 (forward, without dPRV)", value=r2c, n=len(x),
            chosen="; ".join(",".join(c) for c in chosen_c))
        if ds == 0.10:
            E.loc[(E.dstar == ds) & (E.d_min > ds), "pred_lopo"] = predb
    S = pd.DataFrame(S)
    S.to_csv(P1 / "early_redistribution_summary.csv", index=False)
    with pd.option_context("display.width", 220, "display.max_colwidth", 60):
        print(S[S.item.str.contains("LOPO|n runs|drop|dPRV_w|within")].to_string(index=False))

    # figure: resid vs dPRV_w at d* = 0.05 and 0.10, coloured by P32; marker by chemistry
    fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.8), sharey=True)
    for ax, ds in zip(axs, (0.05, 0.10)):
        x = E[(E.dstar == ds) & (E.d_min > ds)]
        for (p, mode), g in x.groupby(["P32", "mode"]):
            ax.scatter(g.dPRV_w, g.resid, s=22, color=COL.get(p, INK2), marker="o" if mode == "gypsum" else "^",
                       edgecolor="white", linewidth=0.5, label=f"x{p:g} {'gypsum-only' if mode == 'gypsum' else 'coupled'}")
        rho = stats.spearmanr(x.dPRV_w, x.resid).statistic
        r2 = S[(S.dstar == ds) & (S.item == "LOPO R2 (dPRV_w only)")].value.iloc[0]
        ax.set_title(f"at {ds:.0%} dissolved: Spearman {rho:.2f}, held-out R² {r2:.2f} (n {len(x)})", fontsize=9, color=INK)
        ax.axhline(0, color=GRID, lw=1); ax.axvline(0, color=GRID, lw=1)
        ax.set_xlabel("early PR$_V$ change, minus group median"); ax.grid(color=GRID, lw=0.6)
    axs[0].set_ylabel("depth minus group median")
    h, l = axs[1].get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.1, 1, 1)); fig.savefig(FIG / "early_redistribution.png", dpi=160)


if __name__ == "__main__":
    main()
