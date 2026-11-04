#!/usr/bin/env python3
"""Report figure of the exploratory olivine run (RUN/clogging.csv from clogging_summary.py) against pore volumes injected
(1 PV per year): network k_eff / initial, fracture-volume-weighted mean porosity, fractures at the porosity floor and below
0.01, and inheritance (share of the current 90 %-flow set that was in the initial set).
  python3 forsmark_reactive/explore_olivine/olivine_figure.py -> explore_olivine/olivine_clogging.png"""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
HERE = Path(__file__).resolve().parent
RUN = HERE / "L2_r15_p6.0_sg1.0_seed1" / "olivine__uncorrected_graph__explore"
d = pd.read_csv(RUN / "clogging.csv").sort_values("k")
s = json.loads((RUN / "single_stage.in.schedule.json").read_text())
d["pv"] = d.t_y * s["rate_m3y"] / s["pore_volume0_m3"]
d = d[d.pv > 0]
panels = [("k_eff_ratio", "network k_eff / initial", "#16181a"), ("phi_mean", "mean porosity (fracture-volume weighted)", "#2a78d6"),
          ("n_below_0p01", "fractures with porosity < 0.01", "#d2572a"), ("overlap0", "share of the 90 %-flow set\nalready in the initial set", "#6b4fbb")]
fig, axs = plt.subplots(1, 4, figsize=(14, 3.3))
for ax, (c, lab, col) in zip(axs, panels):
    if c in d:
        ax.plot(d.pv, d[c], color=col, lw=2)
    ax.set_xscale("log"); ax.set_xlabel("pore volumes injected", fontsize=9, color="#4c5157"); ax.set_title(lab, fontsize=10)
    ax.grid(color="#e6e5e1", lw=0.8)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
if "n_at_floor" in d:
    axs[2].plot(d.pv, d.n_at_floor, color="#d2572a", lw=1, ls="--", label="at the floor (1e-3)"); axs[2].legend(frameon=False, fontsize=8)
fig.suptitle("Exploratory olivine carbonation, P32 ×6, σ = 1, seed 1 (one run)", fontsize=11)
fig.tight_layout(); fig.savefig(HERE / "olivine_clogging.png", dpi=160)
print(d[["pv", "k_eff_ratio", "phi_mean", "phi_min", "n_below_0p01", "n_at_floor", "n90", "overlap0"]].iloc[::6].round(4).to_string(index=False))
