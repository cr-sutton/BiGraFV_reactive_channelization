#!/usr/bin/env python3
"""
Inheritance and mechanism figures for the Phase 1 report, each on three clocks (pore volumes injected, capacity-normalised
time, Hyman's dissolved volume / initial volume; time_axes.py).  Layout as the channel figures: columns P32, one line per
sigma (median of its 5 seeds, 10-90 % band).

  inheritance_<x>.png        rows chemistry: share of the current 90 %-flow set that was in the initial 90 % set
                             (overlap0, channelization.csv)
  mechanism_<mode>_<x>.png   rows: participation ratio against fracture volume, against open pore volume, flow-weighted
                             dissolved fraction at the outlet (last 100 m), flow-weighted front position
                             (phase1_mechanism.csv, analyze_phase1_mechanism.py)

  python3 forsmark_reactive/make_phase1_report_figures.py
"""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from time_axes import clocks  # noqa: E402

P1 = HERE / "phase1"
OUT = P1 / "figures"
SIG = {0.0: "#86b6ef", 0.5: "#2a78d6", 1.0: "#104281"}
INK2, GRID = "#52514e", "#e6e5e1"
MODES = (("gyponly", "gypsum only"), ("gypcal", "gypsum → calcite"))
XLAB = {"diss": "fraction of the gypsum dissolved (logit axis)", "pv": "pore volumes injected", "t_cap": "capacity-normalised time", "tau_H": "dissolved volume / initial volume (Hyman τ)"}
XTAG = {"diss": "diss", "pv": "pv", "t_cap": "tcap", "tau_H": "tauH"}


def axis(ax, x):
    if x == "pv":
        ax.set_xscale("symlog", linthresh=100, linscale=0.6)
        ax.set_xlim(0, 4e4)
    elif x == "tau_H":
        ax.set_xscale("log"); ax.set_xlim(5e-3, 10)
    elif x == "diss":
        ax.set_xscale("logit"); ax.set_xlim(1e-3, 0.99)
        ax.set_xticks([1e-3, 0.01, 0.1, 0.5, 0.9, 0.99]); ax.set_xticklabels(["0.001", "0.01", "0.1", "0.5", "0.9", "0.99"])
        ax.minorticks_off()
    else:
        ax.set_xscale("log"); ax.set_xlim(1e-3, 160)
    ax.grid(color=GRID, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK2, labelsize=8)


def lines(ax, d, x, y):
    for s, c in SIG.items():
        g = d[d.sigma == s]
        if g.empty:
            continue
        piv = g.pivot_table(index="k", columns="seed", values=y)
        xs = g.groupby("k")[x].median().reindex(piv.index)
        ok = ((xs > 0) & (xs < 1 if x == "diss" else True)) if x != "pv" else xs.notna()
        Y = piv.to_numpy()
        ax.fill_between(xs[ok], np.nanpercentile(Y, 10, 1)[ok], np.nanpercentile(Y, 90, 1)[ok], color=c, alpha=0.15, lw=0)
        ax.plot(xs[ok], np.nanmedian(Y, 1)[ok], color=c, lw=2, label=f"σ = {s:g}")


def inheritance():
    rows = []
    for f in sorted(glob.glob(str(P1 / "L2_r15_p*_sg*_seed*/gyp*__phase1/channelization.csv"))):
        m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", f)
        d = pd.read_csv(f)
        c = clocks(Path(f).parent)
        d["pv"], d["t_cap"], d["tau_H"], d["diss"] = c.pv(d.t_y), c.t_cap(d.t_y), c.tau_H(d.t_y), c.diss(d.t_y)
        d["p32"], d["sigma"], d["seed"] = float(m[1]), float(m[2]), int(m[3])
        d["mode"] = "gypcal" if "calcite" in f else "gyponly"
        rows.append(d)
    df = pd.concat(rows)
    for x in XLAB:
        fig, axs = plt.subplots(2, 4, figsize=(14.5, 5.6), sharex=True, sharey=True)
        for i, (mode, lab) in enumerate(MODES):
            for j, p in enumerate((4.0, 6.0, 8.0, 16.0)):
                ax = axs[i, j]
                lines(ax, df[(df["mode"] == mode) & (df.p32 == p)], x, "overlap0")
                axis(ax, x)
                if i == 0:
                    ax.set_title(f"P32 × {p:g}", fontsize=10)
                if j == 0:
                    ax.set_ylabel(f"{lab}\nshare of 90 %-flow set\nalready in the initial set", fontsize=9, color=INK2)
                if i == 1:
                    ax.set_xlabel(XLAB[x], fontsize=9, color=INK2)
        axs[0, 0].set_ylim(0.85, 1.005)
        axs[0, 0].legend(frameon=False, fontsize=8, title="5 seeds each", title_fontsize=8)
        fig.tight_layout(); fig.savefig(OUT / f"inheritance_{XTAG[x]}.png", dpi=160); plt.close(fig)


def mechanism():
    df = pd.read_csv(P1 / "phase1_mechanism.csv")
    df = df[df.tag == "phase1"] if "tag" in df else df
    df = df.assign(diss=df.dissolved)
    mets = [("pr_frac", "participation ratio\n(fracture volume)"), ("pr_pore", "participation ratio\n(open pore volume)"),
            ("outlet_diss", "dissolved at the outlet\n(flow-weighted, last 100 m)"), ("front_x", "front position x (m)\n(inlet −500, outlet +500)")]
    for mode, lab in MODES:
        for x in XLAB:
            fig, axs = plt.subplots(len(mets), 4, figsize=(14.5, 10), sharex=True, sharey="row")
            for j, p in enumerate((4.0, 6.0, 8.0, 16.0)):
                for i, (y, yl) in enumerate(mets):
                    ax = axs[i, j]
                    lines(ax, df[(df["mode"] == mode) & (df.p32 == p)], x, y)
                    axis(ax, x)
                    if i == 0:
                        ax.set_title(f"P32 × {p:g}", fontsize=10)
                    if j == 0:
                        ax.set_ylabel(yl, fontsize=9, color=INK2)
                    if i == len(mets) - 1:
                        ax.set_xlabel(XLAB[x], fontsize=9, color=INK2)
            axs[0, 0].legend(frameon=False, fontsize=8, title="5 seeds each", title_fontsize=8)
            fig.suptitle(f"{lab}: flow focusing, pore space and the dissolution front", fontsize=11)
            fig.tight_layout(); fig.savefig(OUT / f"mechanism_{mode}_{XTAG[x]}.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    inheritance()
    mechanism()
