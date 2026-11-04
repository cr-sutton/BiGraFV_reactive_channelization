#!/usr/bin/env python3
"""
Channel formation in Phase 1: active surface area and volume-weighted participation ratio through time,
one line per transmissivity spread sigma (median over its 5 seeds, 10-90 % band), one panel per P32 and
chemistry.  Reads RUN/channelization.csv (analyze_channelization.py).

  dQ_P32           100 d_Q / P32 = 100 (sum S Q)^2 / (sum S sum S Q^2), the active fracture surface area of Maillot et al.
                   2016 Eq. 8 as used by Hyman 2020/2024/2026 (Q = fracture throughflow; checked against the source, 3 Nov)
  pr_fracture_vol  (sum Q)^2 / sum(Q^2 / w), w = fracture volume share: effective share of the fracture volume
                   carrying the flow (1 when flow is proportional to volume)

Two time axes:
  PV       pore volumes injected (1 PV per year)
  t_cap    capacity-normalised time = PV x c_cap / C_inv: the gypsum the injected water could carry if it left
           saturated, as a fraction of the inventory.  c_cap = 16.6 mol/m3 (gypsum solubility) for gyponly and
           16.6 + 500 mol/m3 for gypcal (0.5 M carbonate takes one Ca per CO3); C_inv = 0.9 / (0.1 x 74.69e-6)
           mol per m3 of pore.  On this axis both chemistries run on the same clock when the reaction is
           transport-limited.

  python3 forsmark_reactive/make_phase1_channel_figures.py  -> forsmark_reactive/phase1/figures/channel_*.png
"""
from __future__ import annotations

import glob
import re
from pathlib import Path

import sys

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
SIG = {0.0: "#86b6ef", 0.5: "#2a78d6", 1.0: "#104281"}          # one-hue ramp, light -> dark with sigma
MODES = (("gyponly", "gypsum only"), ("gypcal", "gypsum → calcite"))
C_INV = 0.9 / (0.1 * 74.69e-6)
C_CAP = {"gyponly": 16.6, "gypcal": 16.6 + 500.0}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
METRICS = {"dQ_P32": "active surface area\n100 d_Q/P32 (%)", "pr_fracture_vol": "participation ratio (volume-weighted)"}


def load():
    out = []
    for f in sorted(glob.glob(str(P1 / "L2_r15_p*_sg*_seed*/gyp*__phase1/channelization.csv"))):
        m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)", f)
        if float(m[1]) > 8:                       # P32 x16 ran to capacity time 2 only; merged separately
            continue
        mode = "gypcal" if "calcite" in f else "gyponly"
        d = pd.read_csv(f).sort_values("k")
        c = clocks(Path(f).parent)
        d["pv"], d["t_cap"], d["tau_H"], d["diss"] = c.pv(d.t_y), c.t_cap(d.t_y), c.tau_H(d.t_y), c.diss(d.t_y)
        out.append(dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode=mode, d=d))
    return out


XLAB = {"diss": "fraction of the gypsum dissolved (logit axis)", "pv": "pore volumes injected", "t_cap": "capacity-normalised time (inventory units)",
        "tau_H": "dissolved volume / initial volume (Hyman τ)"}


def axis(ax, xcol):
    if xcol == "pv":
        ax.set_xscale("symlog", linthresh=100, linscale=0.6)
        ax.set_xlim(0, 4e4)
    elif xcol == "tau_H":
        ax.set_xscale("log")
        ax.set_xlim(5e-3, 10)
    elif xcol == "diss":
        ax.set_xscale("logit"); ax.set_xlim(1e-3, 0.99)
        ax.set_xticks([1e-3, 0.01, 0.1, 0.5, 0.9, 0.99]); ax.set_xticklabels(["0.001", "0.01", "0.1", "0.5", "0.9", "0.99"])
        ax.minorticks_off()
    else:
        ax.set_xscale("log")
        ax.set_xlim(1e-3, 160)
    ax.grid(color=GRID, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK2, labelsize=8)


def figure(runs, metric, xcol, fname):
    fig, axs = plt.subplots(2, 3, figsize=(11, 6.2), sharey=True, sharex=True)
    for i, (mode, mlab) in enumerate(MODES):
        for j, p in enumerate((4.0, 6.0, 8.0)):
            ax = axs[i, j]
            for s, c in SIG.items():
                rs = [r for r in runs if r["p32"] == p and r["mode"] == mode and r["sigma"] == s]
                n = min(len(r["d"]) for r in rs)
                x = rs[0]["d"][xcol].to_numpy()[:n]
                Y = np.array([r["d"][metric].to_numpy()[:n] for r in rs])
                ok = (x > 0) & (x < 1 if xcol == "diss" else True) if xcol != "pv" else np.ones(n, bool)
                ax.fill_between(x[ok], np.percentile(Y, 10, 0)[ok], np.percentile(Y, 90, 0)[ok], color=c, alpha=0.15, lw=0)
                ax.plot(x[ok], np.median(Y, 0)[ok], color=c, lw=2, label=f"σ = {s:g}")
            axis(ax, xcol)
            if i == 0:
                ax.set_title(f"P32 × {p:g}", fontsize=10, color=INK)
            if j == 0:
                ax.set_ylabel(f"{mlab}\n{METRICS[metric]}", fontsize=9, color=INK2)
            if i == 1:
                ax.set_xlabel(XLAB[xcol], fontsize=9, color=INK2)
    axs[0, 0].legend(frameon=False, fontsize=8, title="5 seeds each", title_fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=160)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    runs = load()
    assert len(runs) == 90, len(runs)
    for metric, tag in (("dQ_P32", "active_area"), ("pr_fracture_vol", "pr_vol")):
        figure(runs, metric, "pv", f"channel_{tag}_pv.png")
        figure(runs, metric, "t_cap", f"channel_{tag}_tcap.png")
        figure(runs, metric, "tau_H", f"channel_{tag}_tauH.png")
        figure(runs, metric, "diss", f"channel_{tag}_diss.png")
    rows = []
    for r in runs:
        d = r["d"]
        for metric in ("dQ_P32", "pr_fracture_vol"):
            i = d[metric].idxmin()
            rows.append(dict(mode=r["mode"], p32=r["p32"], sigma=r["sigma"], seed=r["seed"], metric=metric, start=d[metric].iloc[0],
                             minimum=d[metric].min(), min_rel=d[metric].min() / d[metric].iloc[0], pv_at_min=d.pv[i],
                             tcap_at_min=d.t_cap[i], tauH_at_min=d.tau_H[i], dissolved_at_min=d.dissolved[i]))
    s = pd.DataFrame(rows)
    s.to_csv(P1 / "phase1_channel_minima.csv", index=False)
    pd.set_option("display.width", 200)
    print(s.groupby(["metric", "mode", "p32"])[["min_rel", "pv_at_min", "tcap_at_min", "tauH_at_min", "dissolved_at_min"]].median().round(3).to_string())


if __name__ == "__main__":
    main()
