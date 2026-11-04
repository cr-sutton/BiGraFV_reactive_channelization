#!/usr/bin/env python3
"""
Frames and animation of flow / pore-space decoupling for one network (P32 x6, sigma 1, seed 1), both chemistries.
Each frame: horizontal slice at z = 0 (fracture traces from above, inlet left at x = -500 m, outlet right at +500 m)
coloured by (1) share of the injected flow, (2) porosity, (3) flow-to-pore mismatch log10(flow share / pore share);
under them the network's participation ratios against fracture volume and against open pore volume and the outlet
dissolved fraction against capacity-normalised time, with a marker at the frame's time.

  python3 forsmark_reactive/make_mechanism_animation.py
  -> phase1/figures/anim/<mode>/frame_KKK.png, mechanism_<mode>.mp4, stage stills stage<i>_<mode>.png
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm, colors

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIG = HERE / "phase1" / "figures"
NET = "L2_r15_p6.0_sg1.0_seed1"
STAGES = [0.05, 0.2, 0.45, 1.0]                      # capacity times shown as stills (nearest saved state)
FIELDS = [("log10_Q", "share of injected flow", "inferno", (-6, -1), lambda v: f"1e{int(v)}"),
          ("porosity", "porosity (open fraction of the fracture)", "viridis", (0.1, 1), lambda v: f"{v:g}"),
          ("mismatch", "flow share ÷ pore share (log)", "coolwarm", (-2, 2), lambda v: f"{10 ** v:g}×")]
INK2, GRID = "#52514e", "#e6e5e1"


def frames(mode, label):
    run = "gypsum" if mode == "gyponly" else "gypsum_calcite"
    sl = FIG / "slices" / run
    st = pd.read_csv(ROOT / "paraview" / f"{NET}__{run}__uncorrected_graph__phase1__mech" / "states.csv")
    mech = pd.read_csv(HERE / "phase1" / "phase1_mechanism.csv")
    mech = mech[(mech["mode"] == mode) & (mech.p32 == 6.0) & (mech.sigma == 1.0) & (mech.seed == 1)
                & (mech.tag == "phase1" if "tag" in mech else True)].sort_values("k")
    out = FIG / "anim" / mode
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("frame_*.png"):
        f.unlink()
    st = st[st.t_cap > 0].reset_index(drop=True) if mode == "gypcal" else st
    paths = []
    for i, r in st.iterrows():
        k = int(r.k)
        fig = plt.figure(figsize=(12, 9.4))
        gs = fig.add_gridspec(4, 2, height_ratios=[1, 1, 1, 1.15], width_ratios=[40, 1], hspace=0.32, wspace=0.02)
        for row, (fld, lab, cmap, rng, fmt) in enumerate(FIELDS):
            ax = fig.add_subplot(gs[row, 0])
            ax.imshow(plt.imread(sl / f"{fld}_{k:03d}.png"), aspect="auto")
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_color(GRID)
            ax.set_title(lab, fontsize=10, loc="left", color=INK2)
            cax = fig.add_subplot(gs[row, 1])
            cb = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(*rng), cmap=cmap), cax=cax)
            ticks = np.linspace(*rng, 5) if fld != "log10_Q" else np.arange(rng[0], rng[1] + 1)
            cb.set_ticks(ticks); cb.set_ticklabels([fmt(t) for t in ticks]); cb.ax.tick_params(labelsize=7)
            if row == 0:
                ax.text(0.0, -0.06, "inlet  x = −500 m", transform=ax.transAxes, fontsize=8, color=INK2, va="top")
                ax.text(1.0, -0.06, "outlet  x = +500 m", transform=ax.transAxes, fontsize=8, color=INK2, va="top", ha="right")
        ax = fig.add_subplot(gs[3, 0])
        ax.plot(mech.t_cap, mech.pr_frac, color="#2a78d6", lw=2, label="participation ratio, fracture volume")
        ax.plot(mech.t_cap, mech.pr_pore, color="#eb6834", lw=2, label="participation ratio, open pore volume")
        ax.plot(mech.t_cap, mech.outlet_diss * 0.6, color="#52514e", lw=1.4, ls="--", label="outlet dissolved (× 0.6)")
        ax.axvline(max(r.t_cap, 1e-3), color="#0b0b0b", lw=1)
        ax.set_xscale("log"); ax.set_xlim(1e-3, 6); ax.set_ylim(0, 0.62)
        ax.grid(color=GRID, lw=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(labelsize=8, colors=INK2)
        ax.set_xlabel("capacity-normalised time", fontsize=9, color=INK2)
        ax.legend(frameon=False, fontsize=8, loc="lower left")
        fig.suptitle(f"{label}: P32 ×6, σ = 1, seed 1 — slice at z = 0 (1000 m × 250 m)\n"
                     f"capacity time {r.t_cap:.3g}   |   {r.pv:,.0f} pore volumes   |   ΔV/V₀ = {r.tau_H:.2f}   |   "
                     f"{100 * r.dissolved:.0f} % of the gypsum dissolved", fontsize=11, y=0.995)
        p = out / f"frame_{i:03d}.png"
        fig.savefig(p, dpi=110); plt.close(fig)
        paths.append((r.t_cap, p))
    mp4 = FIG / "anim" / f"mechanism_{mode}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "4", "-i", str(out / "frame_%03d.png"),
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", str(mp4)], check=True)
    for j, tc in enumerate(STAGES, 1):
        tcap, p = min(paths, key=lambda tp: abs(np.log(max(tp[0], 1e-6)) - np.log(tc)))
        (FIG / "anim" / f"stage{j}_{mode}.png").write_bytes(p.read_bytes())
    print(mode, len(paths), "frames", mp4)


if __name__ == "__main__":
    frames("gyponly", "gypsum only")
    frames("gypcal", "gypsum → calcite")
