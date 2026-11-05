#!/usr/bin/env python3
"""
Master-curve collapse of the channelization measures against candidate state coordinates.

For every saved-state series in phase1_mechanism.csv (Phase 1 x4-x16, 120 runs, and Phase 2, 36 runs):
  y1 = pr_frac / pr_frac(k=0)    volume-weighted fracture participation, relative to the initial state (PR_V / PR_V0)
  y2 = pr_pore / pr_pore(k=0)    pore-volume participation, relative to the initial state
x candidates:
  d          dissolved gypsum fraction
  d_dbt      d / d_bt            d_bt = `dissolved` at the `breakthrough` event of stage_events_clocks.csv (same run)
  t_cap      capacity-normalised time
  t_cap_tbt  t_cap / t_cap_bt    t_cap at the breakthrough event
  tau_H      time / Hyman residence time
  pv         injected pore volumes
Collapse metric: each run is cut at its x where d first reaches 0.95 (or at its last state), y is interpolated onto a common
grid of x from x_lo to x_hi = the smallest cut over the runs of the set; at every grid point IQR(y) = q75 - q25 across runs;
the metric is the mean of that IQR over the grid (lower = better collapse).  Grids: "lin" (200 points from 0 to x_hi) and
"log" (200 log-spaced points from the largest first positive x over the runs to x_hi; interpolation in log x).  The primary
grid is lin for d and d/d_bt and log for the time-like coordinates.  Metrics on different x are over different x ranges, so
compare them as indicative.  mean_median_y reports the average median level of y over the grid for scale.
Sets: (i) Phase 1 x4-x16 both chemistries pooled (n = 120), (ii) all runs including Phase 2 (n = 156), plus the Phase 1 set
per chemistry (n = 60 each).

  python3 forsmark_reactive/master_curves.py
  -> phase1/master_curve_collapse.csv, phase1/figures/manuscript/master_curves.png, master_curves_by_chemistry.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
P1 = HERE / "phase1"
FIG = P1 / "figures" / "manuscript"
FIG.mkdir(parents=True, exist_ok=True)
COL = {4.0: "#86b6ef", 6.0: "#2a78d6", 8.0: "#104281", 16.0: "#d2572a"}
INK, INK2, GRID = "#16181a", "#4c5157", "#e6e5e1"
XS = ["d", "d_dbt", "t_cap", "t_cap_tbt", "tau_H", "pv"]
XLAB = {"d": "dissolved fraction d", "d_dbt": "d / d_bt", "t_cap": "t_cap", "t_cap_tbt": "t_cap / t_cap,bt",
        "tau_H": "t / tau_H", "pv": "pore volumes"}
PRIMARY = {"d": "lin", "d_dbt": "lin", "t_cap": "log", "t_cap_tbt": "log", "tau_H": "log", "pv": "log"}
NG = 200


def load():
    m = pd.read_csv(P1 / "phase1_mechanism.csv")
    e = pd.read_csv(P1 / "stage_events_clocks.csv")
    e = e[e.event == "breakthrough"][["tag", "mode", "p32", "sigma", "seed", "dissolved", "t_cap"]]
    e = e.rename(columns={"dissolved": "d_bt", "t_cap": "t_cap_bt"})
    key = ["tag", "mode", "p32", "sigma", "seed"]
    m = m.merge(e, on=key, how="left").sort_values(key + ["k"])
    runs = []
    for kk, g in m.groupby(key):
        g = g.reset_index(drop=True)
        r = dict(zip(key, kk))
        r["y1"] = (g.pr_frac / g.pr_frac.iloc[0]).values
        r["y2"] = (g.pr_pore / g.pr_pore.iloc[0]).values
        d = g.dissolved.values
        r["x"] = {"d": d, "d_dbt": d / g.d_bt.iloc[0], "t_cap": g.t_cap.values, "t_cap_tbt": g.t_cap.values / g.t_cap_bt.iloc[0],
                  "tau_H": g.tau_H.values, "pv": g.pv.values}
        hit = np.where(d >= 0.95)[0]
        r["n"] = int(hit[0]) + 1 if len(hit) else len(g)  # keep states up to and including the first d >= 0.95
        runs.append(r)
    return runs


def cut(r, xn, yn):
    """x, y of a run up to d = 0.95 (the crossing state is replaced by interpolation at d = 0.95)."""
    n = r["n"]
    x, y, d = r["x"][xn][:n].copy(), r[yn][:n].copy(), r["x"]["d"][:n]
    if d[-1] > 0.95 and n > 1:
        f = (0.95 - d[-2]) / (d[-1] - d[-2])
        x[-1] = x[-2] + f * (x[-1] - x[-2])
        y[-1] = y[-2] + f * (y[-1] - y[-2])
    return x, y


def collapse(runs, xn, yn, grid):
    cuts = [cut(r, xn, yn) for r in runs]
    hi = min(x[-1] for x, _ in cuts)
    if grid == "lin":
        g = np.linspace(0, hi, NG)
        Y = np.array([np.interp(g, x, y) for x, y in cuts])
    else:
        lo = max(x[x > 0][0] for x, _ in cuts)
        if lo >= hi:
            return np.nan, np.nan, hi
        g = np.geomspace(lo, hi, NG)
        Y = np.array([np.interp(np.log(g), np.log(np.maximum(x, 1e-300)), y) for x, y in cuts])
    iqr = np.percentile(Y, 75, 0) - np.percentile(Y, 25, 0)
    return iqr.mean(), np.median(Y, 0).mean(), hi


def main():
    runs = load()
    sets = {"phase1_x4_x16_pooled": lambda r: r["tag"] == "phase1",
            "phase1_gyponly": lambda r: r["tag"] == "phase1" and r["mode"] == "gyponly",
            "phase1_gypcal": lambda r: r["tag"] == "phase1" and r["mode"] == "gypcal",
            "all_incl_phase2": lambda r: True}
    rows = []
    for sn, f in sets.items():
        rs = [r for r in runs if f(r)]
        for yn, yl in (("y1", "PR_V/PR_V0"), ("y2", "PR_pore/PR_pore0")):
            for xn in XS:
                for grid in ("lin", "log"):
                    v, med, hi = collapse(rs, xn, yn, grid)
                    rows.append(dict(set=sn, n_runs=len(rs), y=yl, x=xn, grid=grid, primary=PRIMARY[xn] == grid,
                                     mean_IQR=v, mean_median_y=med, x_hi=hi))
    C = pd.DataFrame(rows)
    assert np.isfinite(C[["mean_IQR", "mean_median_y"]].values).all()
    C.to_csv(P1 / "master_curve_collapse.csv", index=False)
    pd.set_option("display.width", 200)
    print(C[C.primary].pivot_table(index=["set", "y"], columns="x", values="mean_IQR")[XS].round(3).to_string())
    print(C[C.grid == "lin"].pivot_table(index=["set", "y"], columns="x", values="mean_IQR")[XS].round(3).to_string())
    figures(runs, C)


def style(ax):
    ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8.5)


def median_curve(rs, xn, yn):
    cuts = [cut(r, xn, yn) for r in rs]
    hi = min(x[-1] for x, _ in cuts)
    g = np.linspace(0, hi, NG)
    return g, np.median([np.interp(g, x, y) for x, y in cuts], 0)


def draw(ax, runs, xn, yn, C, chems, title=True):
    for r in runs:
        if r["mode"] not in chems:
            continue
        x, y = cut(r, xn, yn)
        ax.plot(x, y, color=COL[r["p32"]], lw=0.6, alpha=0.35 if r["tag"] == "phase1" else 0.6,
                ls="-" if r["tag"] == "phase1" else ":", zorder=2)
    for mode, ls in (("gyponly", "-"), ("gypcal", "--")):
        if mode in chems:
            g, m = median_curve([r for r in runs if r["mode"] == mode and r["tag"] == "phase1"], xn, yn)
            ax.plot(g, m, color=INK, lw=2.2, ls=ls, zorder=5, label=f"median {mode} (Phase 1)")
    yl = "PR_V/PR_V0" if yn == "y1" else "PR_pore/PR_pore0"
    q = C[(C.y == yl) & (C.x == xn) & (C.grid == "lin")].set_index("set").mean_IQR
    ax.set_title(f"IQR  Phase 1 {q['phase1_x4_x16_pooled']:.3f} | all {q['all_incl_phase2']:.3f}", fontsize=9, color=INK)
    ax.set_xlabel(XLAB[xn], color=INK2, fontsize=9)
    ax.set_ylabel(yl, color=INK2, fontsize=9)
    style(ax)


def figures(runs, C):
    fig, axs = plt.subplots(2, 2, figsize=(8.4, 7.2))
    for i, yn in enumerate(("y1", "y2")):
        for j, xn in enumerate(("d", "d_dbt")):
            draw(axs[i, j], runs, xn, yn, C, ("gyponly", "gypcal"))
    h = [plt.Line2D([], [], color=c, lw=1.5, label=f"P32 x{int(p)}") for p, c in COL.items()]
    h += [plt.Line2D([], [], color=INK, lw=2.2, label="median gypsum only"),
          plt.Line2D([], [], color=INK, lw=2.2, ls="--", label="median gypsum + calcite"),
          plt.Line2D([], [], color=INK2, lw=1, ls=":", label="Phase 2 runs")]
    fig.legend(handles=h, loc="lower center", ncol=4, frameon=False, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(FIG / "master_curves.png", dpi=170)
    plt.close(fig)
    fig, axs = plt.subplots(2, 4, figsize=(15, 6.8))
    for i, yn in enumerate(("y1", "y2")):
        for j, (xn, ch) in enumerate((("d", "gyponly"), ("d", "gypcal"), ("d_dbt", "gyponly"), ("d_dbt", "gypcal"))):
            draw(axs[i, j], runs, xn, yn, C, (ch,))
            axs[i, j].set_title(f"{'gypsum only' if ch == 'gyponly' else 'gypsum + calcite'}", fontsize=9, color=INK)
    fig.legend(handles=h, loc="lower center", ncol=7, frameon=False, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(FIG / "master_curves_by_chemistry.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
