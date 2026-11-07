#!/usr/bin/env python3
"""
Animation of the moving focus and the relaxation behind it (7 Nov 2026, story item 2).
Median over runs (P32 x4-x8, 45 per chemistry) of PR_V of each 100 m stretch / its start, as bars along the flow path,
stepping through the dissolved fraction d = 0 ... 0.9; below it the network PR_V / start with a moving marker.
Input: phase1/xbin_channelization.csv, phase1/phase1_mechanism.csv.  Output: story/report/img/focus_front.mp4 (+ poster png).
  python3 forsmark_reactive/story/make_story_animation.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.animation import FFMpegWriter  # noqa: E402

H = Path(__file__).resolve().parent
FR = H.parent
OUT = H / "report" / "img"
OUT.mkdir(parents=True, exist_ok=True)
GRID = np.linspace(0, 0.9, 181)
COL = {"gyponly": "#1f5f8b", "gypcal": "#c4472d"}
LAB = {"gyponly": "gypsum-only", "gypcal": "coupled gypsum–calcite"}


def on_grid(d, y):
    d = np.maximum.accumulate(np.asarray(d, float))
    out = np.interp(GRID, d, y, left=np.nan, right=np.nan)
    out[GRID > d.max()] = np.nan
    return out


X = pd.read_csv(FR / "phase1" / "xbin_channelization.csv")
X = X[X.p32.isin([4.0, 6.0, 8.0])]
M = pd.read_csv(FR / "phase1" / "phase1_mechanism.csv")
M = M[(M.tag == "phase1") & M.p32.isin([4.0, 6.0, 8.0])]
bins, net = {}, {}
for mo in ("gyponly", "gypcal"):
    cube = []
    for _, g in X[X["mode"] == mo].groupby(["p32", "sigma", "seed"]):
        cube.append([on_grid(h.sort_values("k").dissolved, (h.sort_values("k").prv / h.sort_values("k").prv.iloc[0]))
                     if len(h) > 2 else np.full(len(GRID), np.nan) for b, h in g.groupby("bin")])
    bins[mo] = np.nanmedian(np.array(cube), 0)                       # (10, len(GRID))
    nn = [on_grid(g.sort_values("k").dissolved, g.sort_values("k").pr_frac / g.sort_values("k").pr_frac.iloc[0])
          for _, g in M[M["mode"] == mo].groupby(["p32", "sigma", "seed"])]
    net[mo] = np.nanmedian(np.array(nn), 0)

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(12, 6.4))
gs = fig.add_gridspec(2, 2, height_ratios=[2.2, 1], hspace=0.45, wspace=0.22)
axb = [fig.add_subplot(gs[0, i]) for i in range(2)]
axn = [fig.add_subplot(gs[1, i]) for i in range(2)]
x = np.arange(50, 1000, 100)
bars, mark, txt = {}, {}, {}
for i, mo in enumerate(("gyponly", "gypcal")):
    ax = axb[i]
    bars[mo] = ax.bar(x, np.ones(10), width=90, color=COL[mo], alpha=0.85)
    ax.axhline(1, color="0.6", lw=0.8, ls="--")
    ax.set_ylim(0, 1.25)
    ax.set_xlim(0, 1000)
    ax.set_xlabel("distance from inlet (m)")
    ax.set_title(LAB[mo], loc="left", fontsize=11)
    txt[mo] = ax.text(0.98, 0.96, "", transform=ax.transAxes, ha="right", va="top", fontsize=11, color="0.25")
    ax2 = axn[i]
    ok = np.isfinite(net[mo])
    ax2.plot(GRID[ok], net[mo][ok], color=COL[mo], lw=2)
    ax2.axhline(1, color="0.6", lw=0.8, ls="--")
    mark[mo], = ax2.plot([0], [1], "o", color="k", ms=7)
    ax2.set_xlim(0, 0.9)
    ax2.set_ylim(0.6, 1.08)
    ax2.set_xlabel("fraction of the gypsum dissolved")
    ax2.set_ylabel("network PR$_V$")
axb[0].set_ylabel("PR$_V$ of each 100 m stretch / start\n(short bar = flow concentrated)")
fig.suptitle("The focus moves with the dissolution front and relaxes behind it (median of 45 networks per chemistry)", fontsize=12)


def draw(j):
    for mo in ("gyponly", "gypcal"):
        h = bins[mo][:, j]
        for b, v in zip(bars[mo], h):
            b.set_height(v if np.isfinite(v) else 0)
            b.set_alpha(0.35 + 0.6 * float(np.clip((1 - v) / 0.5, 0, 1)) if np.isfinite(v) else 0.2)
        if np.isfinite(net[mo][j]):
            mark[mo].set_data([GRID[j]], [net[mo][j]])
        txt[mo].set_text(f"dissolved {GRID[j]:.2f}")


draw(0)
fig.savefig(OUT / "focus_front_poster.png", dpi=110)
w = FFMpegWriter(fps=15, bitrate=1800, codec="libx264", extra_args=["-pix_fmt", "yuv420p"])
with w.saving(fig, str(OUT / "focus_front.mp4"), dpi=110):
    for j in range(len(GRID)):
        draw(j)
        w.grab_frame()
    for _ in range(20):
        w.grab_frame()
draw(int(np.searchsorted(GRID, 0.45)))
fig.savefig(OUT / "focus_front_mid.png", dpi=110)
print("wrote", OUT / "focus_front.mp4")
