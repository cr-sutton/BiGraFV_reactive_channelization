#!/usr/bin/env python3
"""Figure for the front-occupancy test (front_occupancy.py), 6 Nov 2026 -> report_phase1/img/front_occupancy.png
A/B: d at the largest focused share of the domain (bins with PR_V/start <= 0.8) against d at the network PR_V minimum, 1 km and 2 km.
C: Hyman-style f50 profile analogue, gypsum-only 1 km, median over runs per dissolved-fraction band."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
H = Path(__file__).resolve().parent
R = pd.read_csv(H / "phase1/front_occupancy_runs.csv")
T = pd.read_csv(H / "phase1/front_occupancy_tests.csv")
P = pd.read_csv(H / "phase1/f50_profile.csv")
col = {"gyponly": "#1f5f8b", "gypcal": "#c4472d"}
lab = {"gyponly": "gypsum-only", "gypcal": "coupled"}
fig, axs = plt.subplots(1, 3, figsize=(14, 4.3), constrained_layout=True)
for ax, sc in zip(axs[:2], ("1km", "2km")):
    ax.plot([0, 0.8], [0, 0.8], color="0.8", lw=1)
    txt = []
    for mo in ("gyponly", "gypcal"):
        h = R[(R.scale == sc) & (R["mode"] == mo)]
        ax.scatter(h.d_prv_min, h["d_occ_max_0.8"], s=16, color=col[mo], alpha=0.7, lw=0, label=lab[mo])
        t = T[(T.scale == sc) & (T["mode"] == mo) & (T.threshold == 0.8)].iloc[0]
        txt.append(f"{lab[mo]}: ρ {t.T1_rho:.2f}, within 0.05: {t.T1_share_within_005:.0%} (n {int(t.n)})")
    ax.text(0.02, 0.98, "\n".join(txt), transform=ax.transAxes, va="top", fontsize=8)
    ax.set_xlim(0, 0.8); ax.set_ylim(0, 0.8)
    ax.set_xlabel("dissolved fraction at the network PR$_V$ minimum")
    ax.set_title(f"{'A' if sc == '1km' else 'B'}. {sc[0]} km: when is the focused zone widest?", fontsize=10, loc="left")
axs[0].set_ylabel("dissolved fraction when most 100 m bins\nare focused (PR$_V$ ≤ 0.8 of start)")
axs[0].legend(frameon=False, loc="lower right", fontsize=8)
bands = [(0, 0.001, "start"), (0.1, 0.25, "0.10–0.25"), (0.25, 0.4, "0.25–0.40"), (0.4, 0.55, "0.40–0.55"), (0.55, 0.7, "0.55–0.70"), (0.7, 1, "0.70+")]
cm = plt.cm.viridis(np.linspace(0, 0.9, len(bands)))
g = P[P["mode"] == "gyponly"]
for (lo, hi, nm), c in zip(bands, cm):
    s = g[(g.dissolved >= lo) & (g.dissolved <= hi)] if lo == 0 else g[(g.dissolved > lo) & (g.dissolved <= hi)]
    m = s.groupby("x").f50.median()
    axs[2].plot(m.index, m.values, color=c, lw=1.6, label=nm)
axs[2].set_ylim(0.6, 1.0)
axs[2].set_xlabel("distance from inlet (m)")
axs[2].set_ylabel("flow focusing index f$_{50}$ (fracture analogue)")
axs[2].set_title("C. Hyman-style focusing profile, 1 km gypsum-only", fontsize=10, loc="left")
axs[2].legend(frameon=False, fontsize=8, title="dissolved", title_fontsize=8, loc="lower left", ncol=2)
fig.savefig(H / "report_phase1/img/front_occupancy.png", dpi=150)
print("ok")
