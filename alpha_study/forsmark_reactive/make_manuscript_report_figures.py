#!/usr/bin/env python3
"""Compact report figures for section 8 from the manuscript-analysis CSVs:
  breakthrough_top1.png   gypsum dissolved at breakthrough against the initial flow share of the single largest-flow
                          fracture (Phase 1 x4-x16 filled, Phase 2 open), with the leave-one-P32-out CV fit per chemistry
  transport_binned.png    gamma/gamma0 and t50_res/t50_res0 against PR_V/PR_V0: medians and IQR in bins (720 probed states)
  python3 forsmark_reactive/make_manuscript_report_figures.py -> phase1/figures/manuscript/"""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
P1 = Path(__file__).resolve().parent / "phase1"; OUT = P1 / "figures" / "manuscript"
COL = {4.0: "#86b6ef", 6.0: "#2a78d6", 8.0: "#104281", 16.0: "#d2572a"}
MODES = (("gyponly", "gypsum only"), ("gypcal", "gypsum → calcite"))
def style(ax):
    ax.grid(color="#e6e5e1", lw=0.8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
b = pd.read_csv(P1 / "breakthrough_predictor.csv")
s = pd.read_csv(P1 / "breakthrough_predictor_summary.csv")
fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, (m, lab) in zip(axs, MODES):
    d = b[b["mode"] == m]
    for p, g in d.groupby("p32"):
        ph1 = g[g.tag == "phase1"]; ph2 = g[g.tag != "phase1"]
        ax.scatter(ph1.top1_share, ph1.d_bt, s=22, color=COL[p], label=f"P32 ×{p:g}")
        ax.scatter(ph2.top1_share, ph2.d_bt, s=34, facecolors="none", edgecolors=COL[p], lw=1.3)
    r = s[(s.target == "d_bt") & (s.scope == "chem") & (s.model == "S_top1_share") & (s.subset == "overall") & (s.chem == m)].iloc[0]
    r2 = s[(s.target == "d_bt") & (s.scope == "chem") & (s.model == "S_top1_share") & (s.subset.str.contains("phase2", case=False)) & (s.chem == m)]
    t = f"leave-one-P32-out: R² {r.R2:.2f}, MAE {r.MAE:.3f}, ρ {r.spearman:.2f} (n {int(r.n)})"
    ax.set_title(f"{lab}\n{t}", fontsize=10); style(ax)
    ax.set_xlabel("initial flow share of the largest-flow fracture", fontsize=9, color="#4c5157")
axs[0].set_ylabel("gypsum dissolved at breakthrough", fontsize=9, color="#4c5157")
axs[0].legend(frameon=False, fontsize=8, title="filled: Phase 1, open: Phase 2", title_fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "breakthrough_top1.png", dpi=160); plt.close(fig)
t = pd.read_csv(P1 / "transport_channel_link.csv")
t = t[t.k > 0]
bins = np.linspace(0.55, 1.05, 11)
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
for ax, (y, lab) in zip(axs, (("rgamma", "tail exponent γ / start"), ("rt50_res", "t50/τ_res / start"))):
    for m, ls, mk in (("gyponly", "-", "o"), ("gypcal", "--", "^")):
        d = t[t["mode"] == m]; c = pd.cut(d.PRV_rel, bins)
        g = d.groupby(c, observed=True)[y].agg(["median", lambda v: v.quantile(.25), lambda v: v.quantile(.75), "size"])
        g.columns = ["med", "lo", "hi", "n"]; g = g[g.n >= 5]
        x = [iv.mid for iv in g.index]
        ax.fill_between(x, g.lo, g.hi, color="#2a78d6" if m == "gyponly" else "#d2572a", alpha=0.18, lw=0)
        ax.plot(x, g.med, ls, marker=mk, color="#2a78d6" if m == "gyponly" else "#d2572a", lw=2, ms=4,
                label="gypsum only" if m == "gyponly" else "gypsum → calcite")
    ax.axhline(1, color="#4c5157", lw=0.8); ax.invert_xaxis(); style(ax)
    ax.set_xlabel("PR_V / start  (← more focused)", fontsize=9, color="#4c5157"); ax.set_ylabel(lab, fontsize=9, color="#4c5157")
axs[0].legend(frameon=False, fontsize=8)
fig.suptitle("Transport against channel focusing: medians and IQR over probed states (P32 ×4–×8, 45 runs per chemistry)", fontsize=10)
fig.tight_layout(); fig.savefig(OUT / "transport_binned.png", dpi=160); plt.close(fig)
print("ok")
