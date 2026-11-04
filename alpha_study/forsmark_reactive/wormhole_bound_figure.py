#!/usr/bin/env python3
"""Report figure of the wormhole-limit bound (phase1/wormhole_bound.csv from wormhole_bound.py): per chemistry, the
dissolved fraction at breakthrough if only a fraction f of each channel fracture had to dissolve.  Band = median lower to
median upper bound over the 45 P32 x4-x8 runs; orange line = P32 x16 (15 runs); dashed = the model (f = 1).
  python3 forsmark_reactive/wormhole_bound_figure.py -> phase1/figures/wormhole_bound_report.png"""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
P1 = Path(__file__).resolve().parent / "phase1"
d = pd.read_csv(P1 / "wormhole_bound.csv")
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, (mode, lab) in zip(axs, (("gyponly", "gypsum only"), ("gypcal", "gypsum → calcite"))):
    a = d[(d["mode"] == mode) & (d.p32 <= 8)].groupby("f")[["D_lo", "D_hi"]].median()
    b = d[(d["mode"] == mode) & (d.p32 == 16)].groupby("f")[["D_lo", "D_hi"]].median()
    ax.fill_between(a.index, a.D_lo, a.D_hi, color="#2a78d6", alpha=0.25, lw=0, label="P32 ×4–×8, lower–upper bound")
    ax.plot(a.index, a.D_lo, color="#2a78d6", lw=2); ax.plot(a.index, a.D_hi, color="#2a78d6", lw=1, ls=":")
    ax.plot(b.index, b.D_lo, color="#d2572a", lw=1.6, label="P32 ×16, lower bound")
    ax.axhline(a.D_lo.iloc[-1], color="#16181a", lw=1, ls="--")
    ax.text(0.12, a.D_lo.iloc[-1] + 0.015, f"model: {a.D_lo.iloc[-1]:.2f} dissolved at breakthrough", fontsize=9, color="#16181a")
    ax.set_title(lab, fontsize=11); ax.set_xlim(0.08, 1.02); ax.set_ylim(0, 0.75); ax.grid(color="#e6e5e1", lw=0.8)
    ax.set_xlabel("f: share of a channel fracture that must dissolve before the front passes", fontsize=9, color="#4c5157")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axs[0].set_ylabel("gypsum dissolved at breakthrough", fontsize=9, color="#4c5157")
axs[0].legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(P1 / "figures" / "wormhole_bound_report.png", dpi=160)
