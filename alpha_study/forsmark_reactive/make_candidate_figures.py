#!/usr/bin/env python3
"""
Figures for the candidate findings (re-run as Phase 2 and the P32 x16 runs land; points appear when their runs exist).
  breakthrough_dissolved.png  dissolved fraction when the outlet zone (x > 400 m) passes 50 % dissolved (flow-weighted),
                              one point per run; Phase 1 and, when available, porosity-0.05 runs
  depth_law.png               channel depth (min / start of the volume-weighted participation ratio) against the
                              permeability gain the reaction can reach under k-phi n = 1:
                              gyponly 1/phi0; coupled 1 + (vf0/phi0)(1 - Gamma), Gamma = 36.934/74.69
"""
from pathlib import Path
import glob, re, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
P1 = HERE / "phase1"
OUT = P1 / "figures"
GAM = 36.934 / 74.69
INK2, GRID = "#52514e", "#e6e5e1"
COL = {"gyponly": "#2a78d6", "gypcal": "#eb6834"}


def ceiling(mode, phi0):
    vf0 = 1 - phi0
    return 1 / phi0 if mode == "gyponly" else 1 + (vf0 / phi0) * (1 - GAM)


def channel_rows():
    rows = []
    for f in glob.glob(str(P1 / "L2_r15_p*_sg*_seed*/gyp*__*/channelization.csv")):
        m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d)/(gyp\w+?)__uncorrected_graph__(\w+)/", f)
        tag = m[5]
        if tag not in ("phase1", "phase2_phi005", "phase3_phi0182"):
            continue
        mode = "gypcal" if "calcite" in m[4] else "gyponly"
        phi0 = {"phase2_phi005": 0.05, "phase3_phi0182": 0.182}.get(tag, 0.1)
        d = pd.read_csv(f)
        rows.append(dict(p32=float(m[1]), sigma=float(m[2]), seed=int(m[3]), mode=mode, phi0=phi0, tag=tag,
                         contrast=ceiling(mode, phi0), depth=d.pr_fracture_vol.min() / d.pr_fracture_vol.iloc[0]))
    return pd.DataFrame(rows)


def depth_law(df):
    fig, ax = plt.subplots(figsize=(6.2, 4))
    for mode, lab in (("gyponly", "gypsum only"), ("gypcal", "gypsum → calcite")):
        for phi0, mk in ((0.1, "o"), (0.05, "s"), (0.182, "D")):
            d = df[(df["mode"] == mode) & (df.phi0 == phi0)]
            c = ceiling(mode, phi0)
            if len(d):
                jit = np.exp(np.random.default_rng(0).normal(0, 0.02, len(d)))
                ax.scatter(d.contrast * jit, d.depth, s=14, color=COL[mode], alpha=0.35, lw=0, marker=mk)
                ax.errorbar(c, d.depth.median(), yerr=[[d.depth.median() - d.depth.quantile(0.1)], [d.depth.quantile(0.9) - d.depth.median()]],
                            fmt=mk, color=COL[mode], ms=8, mec="white", capsize=3, label=f"{lab}, porosity {phi0:g} (n = {len(d)})")
            else:
                ax.scatter([c], [0.5], marker=mk, s=70, facecolors="none", edgecolors=COL[mode], lw=1.5, label=f"{lab}, porosity {phi0:g}: running")
                ax.annotate("pending", (c, 0.5), xytext=(6, -12), textcoords="offset points", fontsize=8, color=INK2)
    ax.set_xscale("log"); ax.set_xlim(2.8, 25); ax.set_ylim(0.3, 1.0)
    ax.set_xticks([3.3, 5.5, 10, 20]); ax.set_xticklabels(["×3.3", "×5.5", "×10", "×20"]); ax.minorticks_off()
    ax.grid(color=GRID, lw=0.8)
    ax.set_xlabel("permeability gain the reaction can reach (n = 1 ceiling)", fontsize=9, color=INK2)
    ax.set_ylabel("channel depth: participation ratio\nminimum ÷ start", fontsize=9, color=INK2)
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    fig.tight_layout(); fig.savefig(OUT / "depth_law.png", dpi=160); plt.close(fig)


def breakthrough():
    sys.path.insert(0, str(HERE))
    d = pd.read_csv(P1 / "phase1_mechanism.csv")
    rows = []
    if "tag" not in d:
        d["tag"] = "phase1"
    for key, g in d.groupby(["tag", "mode", "p32", "sigma", "seed"]):
        g = g.reset_index(drop=True); r = g[g.outlet_diss >= 0.5]
        if len(r):
            rows.append(dict(tag=key[0], mode=key[1], p32=key[2], diss=r.dissolved.iloc[0]))
    b = pd.DataFrame(rows)
    hi = b[b.tag == "phase2_phi005"]
    b = b[b.tag == "phase1"]
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    for i, (mode, lab) in enumerate((("gyponly", "gypsum only"), ("gypcal", "gypsum → calcite"))):
        for j, p in enumerate((4.0, 6.0, 8.0, 16.0)):
            v = b[(b["mode"] == mode) & (b.p32 == p)].diss
            x = j + (i - 0.5) * 0.28
            ax.scatter(x + np.random.default_rng(j).uniform(-0.06, 0.06, len(v)), v, s=14, color=COL[mode], alpha=0.5, lw=0)
            ax.plot([x - 0.1, x + 0.1], [v.median()] * 2, color=COL[mode], lw=2.5, label=lab if j == 0 else None)
    for i, mode in enumerate(("gyponly", "gypcal")):
        for j, p in enumerate((4.0, 6.0, 8.0, 16.0)):
            v = hi[(hi["mode"] == mode) & (hi.p32 == p)].diss
            if len(v):
                x = j + (i - 0.5) * 0.28 + 0.12
                ax.scatter([x] * len(v), v, s=26, marker="s", facecolors="none", edgecolors=COL[mode], lw=1.2,
                           label="porosity 0.05 (×2 contrast)" if (i, j) == (0, 0) else None)
    ax.axhspan(0, 0.1, color="#e6e5e1", alpha=0.6, lw=0)
    ax.text(3.45, 0.05, "wormhole-like (few % dissolved)", fontsize=8, color=INK2, ha="right", va="center")
    ax.set_xticks([0, 1, 2, 3]); ax.set_xticklabels(["P32 ×4", "×6", "×8", "×16"])
    ax.set_ylim(0, 1); ax.grid(color=GRID, lw=0.8, axis="y")
    ax.set_ylabel("gypsum dissolved when the\nfront reaches the outlet", fontsize=9, color=INK2)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(OUT / "breakthrough_dissolved.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    depth_law(channel_rows())
    breakthrough()
    print("ok")
