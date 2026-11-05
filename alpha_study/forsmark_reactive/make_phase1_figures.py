#!/usr/bin/env python3
"""
Phase 1 ensemble figures (Forsmark FFM01, 1000 x 250 x 250 m, 45 networks x {gyponly, gypcal}).

  python3 forsmark_reactive/make_phase1_figures.py   -> forsmark_reactive/phase1/figures/*.png, phase1_end_summary.csv

Every run saves its states at the same pore volumes (t_end and the log-spaced VTK times are identical), so
curves are combined row by row: median over the 15 runs of one P32 level (5 seeds x 3 sigma) and the
10-90 % band.  Time axis: pore volumes injected (1 PV per year), symlog (linear to 100, log beyond).
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
P1 = HERE / "phase1"
OUT = P1 / "figures"
COL = {"gyponly": "#2a78d6", "gypcal": "#eb6834"}          # reference palette slots 1, 2
LAB = {"gyponly": "gypsum only", "gypcal": "gypsum → calcite"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"


def load():
    runs = []
    for f in sorted(glob.glob(str(P1 / "L2_r15_p*_sg*_seed*/gyp*__phase1/patterns.csv"))):
        m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", f)
        d = pd.read_csv(f)
        d["n90_rel"] = d.n90 / d.n90.iloc[0]
        d["dQ_rel"] = d.dQ_P32 / d.dQ_P32.iloc[0]
        net = Path(f).parents[1]
        s = json.loads((net / "network_stats.json").read_text())
        runs.append(dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode="gypcal" if "calcite" in f else "gyponly",
                         d=d, dead=1 - s["backbone_fraction"], paths=s["node_disjoint_paths"], nfrac=s["n_fractures"]))
    return runs


def style(ax):
    ax.set_xscale("symlog", linthresh=100, linscale=0.6)
    ax.set_xlim(0, 4e4)
    ax.grid(color=GRID, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)


def ensemble(runs, col, ylabel, fname, ylim=None):
    fig, axs = plt.subplots(1, 4, figsize=(14, 3.2), sharey=True)
    for ax, p in zip(axs, (4.0, 6.0, 8.0, 16.0)):
        for mode in ("gyponly", "gypcal"):
            rs = [r for r in runs if r["p32"] == p and r["mode"] == mode]
            t = rs[0]["d"].t_y.to_numpy()
            n = min(len(r["d"]) for r in rs)
            Y = np.array([r["d"][col].to_numpy()[:n] for r in rs])
            ax.fill_between(t[:n], np.percentile(Y, 10, 0), np.percentile(Y, 90, 0), color=COL[mode], alpha=0.18, lw=0)
            ax.plot(t[:n], np.median(Y, 0), color=COL[mode], lw=2, label=LAB[mode])
        style(ax)
        ax.set_title(f"P32 × {p:g}", fontsize=10, color=INK)
        ax.set_xlabel("pore volumes injected", fontsize=9, color=INK2)
        if ylim:
            ax.set_ylim(*ylim)
    axs[0].set_ylabel(ylabel, fontsize=9, color=INK2)
    axs[0].legend(frameon=False, fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=160)
    plt.close(fig)


def deadend(runs):
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    for mode in ("gyponly", "gypcal"):
        rs = [r for r in runs if r["mode"] == mode]
        x = np.array([r["dead"] for r in rs])
        y = np.array([1 - r["d"].dissolved.iloc[-1] for r in rs])
        ax.scatter(x, y, s=34, color=COL[mode], edgecolor="white", lw=1, label=LAB[mode], zorder=3)
        a, b = np.polyfit(x, y, 1)
        xx = np.linspace(x.min(), x.max(), 10)
        ax.plot(xx, a * xx + b, color=COL[mode], lw=1.5, ls="--")
        r = np.corrcoef(x, y)[0, 1]
        ax.annotate(f"r = {r:.2f}", (xx[-1], a * xx[-1] + b), xytext=(4, 0), textcoords="offset points",
                    fontsize=8, color=INK2, va="center")
    ax.grid(color=GRID, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.set_xlabel("dead-end fracture share (topology)", fontsize=9, color=INK2)
    ax.set_ylabel("gypsum left at 36,515 PV (fraction)", fontsize=9, color=INK2)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "phase1_leftover_vs_deadend.png", dpi=160)
    plt.close(fig)


def summary(runs):
    rows = []
    for r in runs:
        d = r["d"]
        half = d.t_y[d.dissolved >= 0.5]
        rows.append(dict(p32=r["p32"], sigma=r["sigma"], seed=r["seed"], mode=r["mode"], n_fractures=r["nfrac"],
                         dead_frac=r["dead"], paths=r["paths"], diss_end=d.dissolved.iloc[-1],
                         keff_end=d.k_eff_ratio.iloc[-1], n90_min_rel=d.n90_rel.min(), pv_n90_min=d.t_y[d.n90.idxmin()],
                         dQ_min_rel=d.dQ_rel.min(), pv_half=half.min() if len(half) else np.nan))
    df = pd.DataFrame(rows)
    df.to_csv(P1 / "phase1_end_summary.csv", index=False)
    return df


def main():
    OUT.mkdir(exist_ok=True)
    runs = load()
    assert len(runs) == 120, len(runs)
    ensemble(runs, "dissolved", "fraction of gypsum dissolved", "phase1_dissolved.png", (0, 1.02))
    ensemble(runs, "k_eff_ratio", "k_eff / k_eff,0", "phase1_keff.png")
    ensemble(runs, "n90_rel", "n90 / n90 at start", "phase1_n90.png")
    deadend(runs)
    df = summary(runs)
    print(df.groupby(["mode", "p32"])[["diss_end", "keff_end", "n90_min_rel", "pv_half"]].median().round(3))


if __name__ == "__main__":
    main()
