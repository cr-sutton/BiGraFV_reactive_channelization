#!/usr/bin/env python3
"""
PDF: channelization binned by fracture x (distance from the inlet) for every paired gypsum-only / coupled Phase 1 ensemble
(5 Nov 2026, user request).  From phase1/xbin_channelization.csv (xbin_channelization.py).

Pages 1-3: Hyman's active surface area (d_Q/P32 of the fractures in each 100 m bin), one page per transmissivity sigma.
Pages 4-6: volume-weighted participation ratio PR_V of each bin, one page per sigma.
Each page: rows gypsum-only, coupled, coupled / gypsum-only (paired by seed); columns P32 x4, x6, x8, x16.
Colour = the bin's value relative to its own start (state 0), median over the 5 seeds, on the dissolved fraction (main clock).
Blue = flow concentrates into fewer fractures in that bin, red = flow spreads.  Lines: ensemble median dissolved fraction
at the PR_V minimum (solid) and at breakthrough (dashed), stage_events_clocks.csv.  Cells with < 3 seeds are blank.

  python3 forsmark_reactive/make_xbin_figure.py   -> phase1/figures/xbin_channelization.pdf
"""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

HERE = Path(__file__).resolve().parent
P1 = HERE / "phase1"
D = np.round(np.arange(0.0, 0.901, 0.01), 3)
DE = np.r_[D - 0.005, D[-1] + 0.005]
EDGES = np.arange(0.0, 1001.0, 100.0)
P32S, SIGMAS = (4.0, 6.0, 8.0, 16.0), (0.0, 0.5, 1.0)
MODES = (("gyponly", "Gypsum-only"), ("gypcal", "Coupled gypsum–calcite"))
METRICS = (("active", "active surface area d$_Q$/P32 (Hyman)", "Active surface area"),
           ("prv", "participation ratio PR$_V$", "Participation ratio PR$_V$"))

df = pd.read_csv(P1 / "xbin_channelization.csv")
ev = pd.read_csv(P1 / "stage_events_clocks.csv")
ev = ev[ev.tag == "phase1"].groupby(["mode", "p32", "sigma", "event"]).dissolved.median()


def grids(metric):
    """{(mode, p32, sigma, seed): array (len(D), n_bins)} of metric / metric at state 0, interpolated on D."""
    out = {}
    for key, g in df.groupby(["mode", "p32", "sigma", "seed"]):
        a = np.full((len(D), len(EDGES) - 1), np.nan)
        for b, h in g.groupby("bin"):
            h = h.sort_values("k")
            if h.k.iloc[0] != 0:
                continue
            y = h[metric].values / h[metric].values[0]
            x = np.maximum.accumulate(h.dissolved.values)
            a[:, b] = np.where(D <= x.max(), np.interp(D, x, y), np.nan)
        out[key] = a
    return out


def med(stack):
    s = np.array(stack)
    m = np.nanmedian(s, axis=0)
    m[np.sum(np.isfinite(s), axis=0) < 3] = np.nan
    return m


with PdfPages(P1 / "figures" / "xbin_channelization.pdf") as pdf:
    for metric, cbl, title in METRICS:
        G = grids(metric)
        for sg in SIGMAS:
            fig, axs = plt.subplots(3, 4, figsize=(15, 11), sharex=True, sharey=True, constrained_layout=True)
            for j, p in enumerate(P32S):
                rel = {}
                for i, (mode, lab) in enumerate(MODES):
                    rel[mode] = {s: G[(mode, p, sg, s)] for s in range(1, 6) if (mode, p, sg, s) in G}
                    m = med(list(rel[mode].values()))
                    ax = axs[i, j]
                    im = ax.pcolormesh(EDGES, DE, m, cmap="RdBu_r", norm=LogNorm(1 / 3, 3), shading="flat")
                    for e, ls in (("PRV_min", "-"), ("breakthrough", "--")):
                        if (mode, p, sg, e) in ev:
                            ax.axhline(ev[(mode, p, sg, e)], color="k", ls=ls, lw=1.2)
                    ax.set_title(f"{lab}, P32 ×{p:g} (n = {len(rel[mode])})", fontsize=10)
                pair = [rel["gypcal"][s] / rel["gyponly"][s] for s in rel["gypcal"] if s in rel["gyponly"]]
                ax = axs[2, j]
                im2 = ax.pcolormesh(EDGES, DE, med(pair), cmap="PuOr_r", norm=LogNorm(1 / 2, 2), shading="flat")
                ax.set_title(f"Coupled ÷ gypsum-only, paired (n = {len(pair)})", fontsize=10)
            for ax in axs[:, 0]:
                ax.set_ylabel("fraction of the gypsum dissolved")
            for ax in axs[-1]:
                ax.set_xlabel("distance of fracture centre from inlet (m)")
            fig.colorbar(im, ax=axs[:2, :], shrink=0.6, label=f"{cbl}, bin value / its start\n(blue = flow concentrates, red = spreads)")
            fig.colorbar(im2, ax=axs[2, :], shrink=0.9, label="coupled ÷ gypsum-only\n(orange = coupled more spread)")
            fig.suptitle(f"{title} by distance from the inlet — Phase 1, transmissivity σ = {sg:g}\n"
                         "Each cell: fractures whose centre lies in that 100 m bin, median over 5 seeds. "
                         "Solid line: median dissolved fraction at the network PR$_V$ minimum; dashed: at breakthrough.",
                         fontsize=11)
            pdf.savefig(fig)
            if os.environ.get("PREVIEW"):
                fig.savefig(f"{os.environ['PREVIEW']}/xbin_{metric}_sg{sg:g}.png", dpi=int(os.environ.get("PREVIEW_DPI", 55)))
            plt.close(fig)
print("wrote", P1 / "figures" / "xbin_channelization.pdf")
