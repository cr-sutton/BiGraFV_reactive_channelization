#!/usr/bin/env python3
"""
Draft main-text figures 1-8 for the manuscript (5 Nov 2026), following the figure list in MANUSCRIPT_PLAN.md / report 8.6.

New data panels are plotted here from the study CSVs:
  Fig 3b  stage-event timing on four clocks (pv, t_cap, dissolved d, tau_H): group medians of the five matched groups
          (sigma 1, seeds 1-3, the Phase 2 networks), each divided by the median over the groups    <- phase1/stage_events_clocks.csv
  Fig 5b  ceiling test, paired on the same network                                                   <- phase1/phase3_ceiling.csv
  Fig 8a  rate test: stage events on d at 0.1, 1 and 10 pore volumes per year                        <- phase1/phase3_rate.csv
  Fig 8b  stage events on d by P32 (x4-x16), Phase 1                                                <- phase1/stage_events_clocks.csv
The other panels are the existing study figures (same CSVs, scripts named in manuscript_figures/FIGURES.md), assembled with panel
letters.  Output: forsmark_reactive/manuscript_figures/Figure_N.png (+ panel PNGs) and FIGURES.md (draft captions).

  python3 forsmark_reactive/make_manuscript_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
P1 = HERE / "phase1"
FIGD = P1 / "figures"
IMG = HERE / "report_phase1" / "img"
CART = HERE / "deck" / "cartoons"
OUT = HERE / "manuscript_figures"
INK, INK2, GRID = "#1f1f1c", "#6b6a64", "#e4e3de"
CHEM = {"gyponly": "#2a78d6", "gypcal": "#d2572a"}
P32C = {4.0: "#86b6ef", 6.0: "#2a78d6", 8.0: "#104281", 16.0: "#d2572a"}
EVLAB = {"PRpore_min": "PR$_{pore}$ min", "outlet5": "outlet 5 %", "PRV_min": "PR$_V$ min", "breakthrough": "breakthrough"}


def style():
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                         "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200, "savefig.bbox": "tight",
                         "font.family": "DejaVu Sans"})


# ---------------------------------------------------------------- new data panels
def panel_clocks(path):
    e = pd.read_csv(P1 / "stage_events_clocks.csv")
    groups = [("phase1", "gyponly", "gypsum-only, φ0 0.1"), ("phase1", "gypcal", "coupled, φ0 0.1"),
              ("phase2_phi005", "gyponly", "gypsum-only, φ0 0.05"), ("phase2_phi005", "gypcal", "coupled, φ0 0.05"),
              ("phase2_co3lo", "gypcal", "coupled 2 mM, φ0 0.1")]
    nets = e[e.tag == "phase2_phi005"][["p32", "sigma", "seed"]].drop_duplicates()   # x4-x16 (n = 12), as report section 3 since 5 Nov
    m = e.merge(nets, on=["p32", "sigma", "seed"])
    clocks = [("pv", "pore volumes"), ("t_cap", "capacity time"), ("dissolved", "dissolved fraction d"), ("tau_H", "Hyman τ")]
    marks = ["o", "^", "s", "D", "v"]
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.2), sharey=True)
    rows = []
    for ax, ev in zip(axs, ("PRV_min", "breakthrough")):
        for j, (col, lab) in enumerate(clocks):
            med = []
            for tag, mode, gl in groups:
                g = m[(m.tag == tag) & (m["mode"] == mode) & (m.event == ev)]
                med.append(g[col].median())
                rows.append(dict(event=ev, clock=col, group=gl, n=len(g), median=g[col].median()))
            med = np.array(med); rel = med / np.median(med)
            for i, (r, (_, mode, gl)) in enumerate(zip(rel, groups)):
                ax.scatter(j + (i - 2) * 0.07, r, marker=marks[i], s=30, color=CHEM[mode], edgecolor="white", lw=0.5,
                           label=gl if j == 0 else None, zorder=3)
            ax.text(j, rel.max() * 1.45, f"×{med.max() / med.min():.2f}", ha="center", fontsize=8.5, color=INK)
        ax.set_yscale("log"); ax.set_xticks(range(4), [c[1] for c in clocks], rotation=0, fontsize=8)
        ax.axhline(1, color=GRID, lw=1, zorder=1); ax.set_title(EVLAB[ev], fontsize=9.5, color=INK)
        ax.set_ylim(0.03, 30); ax.grid(axis="y", color=GRID, lw=0.5)
    axs[0].set_ylabel("group median / median over groups")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7, frameon=False, loc="lower center", ncol=5)
    fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(path); plt.close(fig)
    pd.DataFrame(rows).to_csv(OUT / "fig3b_clock_groups.csv", index=False)


def panel_ceiling(path):
    c = pd.read_csv(P1 / "phase3_ceiling.csv")
    pairs = [("gyp_x55_phi0182", "cal_x55_phi01", "gypsum-only ×5.5\nvs coupled ×5.5", "equal ceiling,\ndifferent chemistry"),
             ("gyp_x55_phi0182", "gyp_x10_phi01", "gypsum-only ×5.5\nvs ×10", "same chemistry,\nlower ceiling"),
             ("cal_x33_phi0182", "cal_x55_phi01", "coupled ×3.3\nvs ×5.5", "same chemistry,\nlower ceiling")]
    fig, ax = plt.subplots(figsize=(4.4, 3.2))
    for i, (a, b, lab, sub) in enumerate(pairs):
        d = c[a] - c[b]
        for p, g in c.assign(d=d).groupby("p32"):
            ax.scatter(i + np.linspace(-0.12, 0.12, len(g)), g.d, s=26, color=P32C[p], edgecolor="white", lw=0.5,
                       label=f"×{p:g}" if i == 0 else None, zorder=3)
        q = d.quantile([.25, .5, .75]).values
        ax.plot([i - 0.25, i + 0.25], [q[1]] * 2, color=INK, lw=1.6)
        ax.text(i, max(d.max(), 0) + 0.018, f"{q[1]:+.3f}\n[{q[0]:+.3f}, {q[2]:+.3f}]", ha="center", fontsize=7, color=INK)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(range(3), [p[2] for p in pairs], fontsize=7.5)
    ax.set_ylabel("Δ depth (PR$_V$ min / PR$_V$(0)), same network")
    ax.set_ylim(-0.08, 0.27); ax.legend(title="P32", fontsize=7, title_fontsize=7, frameon=False, loc="upper left")
    ax.grid(axis="y", color=GRID, lw=0.5)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def panel_rate(path):
    r = pd.read_csv(P1 / "phase3_rate.csv")
    r = r[r.event.isin(["PRpore_min", "PRV_min", "breakthrough"])]
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.0), sharey=True)
    xs = {"phase3_rate01": 0.1, "x1": 1.0, "phase3_rate10": 10.0}
    em = {"PRpore_min": "o", "PRV_min": "s", "breakthrough": "^"}
    for ax, mode in zip(axs, ("gyponly", "gypcal")):
        g = r[r["mode"] == mode]
        for (seed, ev), h in g.groupby(["seed", "event"]):
            x1 = h.d_x1.iloc[0]
            pts = [(0.1, h[h.rate == "phase3_rate01"].d_rate.iloc[0]), (1.0, x1), (10.0, h[h.rate == "phase3_rate10"].d_rate.iloc[0])]
            ax.plot(*zip(*pts), color=P32C[6.0] if mode == "gyponly" else CHEM["gypcal"], lw=0.8, alpha=0.6)
            ax.scatter(*zip(*pts), marker=em[ev], s=22, color=CHEM[mode], edgecolor="white", lw=0.4, zorder=3,
                       label=EVLAB[ev] if seed == 1 else None)
        ax.set_xscale("log"); ax.set_xticks([0.1, 1, 10], ["0.1", "1", "10"])
        ax.set_xlabel("injection rate (pore volumes per year)")
        ax.set_title("gypsum-only" if mode == "gyponly" else "coupled", fontsize=9.5, color=INK)
        ax.grid(color=GRID, lw=0.5)
    axs[0].set_ylabel("dissolved fraction at event")
    axs[0].legend(fontsize=7, frameon=False, loc="upper left")
    fig.text(0.5, -0.02, "P32 ×6, σ 1, seeds 1–3; ×1 = Phase 1 run (different save times)", ha="center", fontsize=7, color=INK2)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def panel_p32(path):
    e = pd.read_csv(P1 / "stage_events_clocks.csv")
    e = e[(e.tag == "phase1") & e.event.isin(["PRpore_min", "PRV_min", "breakthrough"])]
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.0), sharey=True)
    for ax, mode in zip(axs, ("gyponly", "gypcal")):
        for k, ev in enumerate(("PRpore_min", "PRV_min", "breakthrough")):
            for j, p in enumerate((4.0, 6.0, 8.0, 16.0)):
                g = e[(e["mode"] == mode) & (e.event == ev) & (e.p32 == p)].dissolved
                x = k + (j - 1.5) * 0.17
                q = g.quantile([.25, .5, .75]).values
                ax.plot([x, x], [q[0], q[2]], color=P32C[p], lw=3, solid_capstyle="butt")
                ax.scatter(x, q[1], s=18, color="white", edgecolor=P32C[p], lw=1.2, zorder=3, label=f"×{p:g} (n {len(g)})" if k == 0 else None)
        ax.set_xticks(range(3), [EVLAB[v] for v in ("PRpore_min", "PRV_min", "breakthrough")], fontsize=8)
        ax.set_title("gypsum-only" if mode == "gyponly" else "coupled", fontsize=9.5, color=INK); ax.grid(axis="y", color=GRID, lw=0.5)
    axs[0].set_ylabel("dissolved fraction at event (median, IQR)")
    axs[0].legend(fontsize=7, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


# ---------------------------------------------------------------- assembly
def assemble(name, rows, width=7.2, title=None):
    """rows: list of rows, each a list of (png path, relative width).  Height of a row follows the image aspect."""
    ims = [[(mpimg.imread(p), w) for p, w in r] for r in rows]
    heights = []
    for r in ims:
        tot = sum(w for _, w in r)
        heights.append(max(width * w / tot * im.shape[0] / im.shape[1] for im, w in r))
    fig = plt.figure(figsize=(width, sum(heights) + 0.15 * len(rows)))
    y = 1.0; H = sum(heights) + 0.15 * len(rows); letter = 0
    for r, h in zip(ims, heights):
        tot = sum(w for _, w in r); x = 0.0
        for im, w in r:
            ax = fig.add_axes([x, y - h / H, w / tot - 0.01, h / H - 0.01])
            ax.imshow(im); ax.axis("off")
            ax.text(-0.01, 1.0, "abcdefgh"[letter], transform=ax.transAxes, fontsize=12, fontweight="bold", va="top", ha="right", color=INK)
            x += w / tot; letter += 1
        y -= (h + 0.15) / H
    fig.savefig(OUT / f"{name}.png", dpi=220); plt.close(fig)


CAPTIONS = {
    1: ("Set-up.", "(a) Example Forsmark FFM01 network (P32 ×6, σ 1, seed 1, 1 km × 250 m × 250 m), fractures coloured by their "
        "share of the injected flow. (b) The one-cell BiGraFV model: one well-mixed control volume per fracture. (c) The two "
        "chemistries (gypsum dissolution; gypsum dissolution with calcite precipitation) with their capacity and permeability ceilings.",
        "deck/network_p6_flow.png; report cartoons fracture_cell.svg, chemistry.svg. NOTE: panel a is a 542 x 223 px render; re-render at print resolution (and add a colour bar) before submission."),
    2: ("Four stages of channel formation.", "(a) Cartoon of the four stages on the dissolved-fraction clock. (b) Stage snapshots of "
        "the example network (gypsum-only, P32 ×6, σ 1, seed 1): open channel, open space with little flow, flow through filled rock. "
        "(c) PR_V against the fraction of gypsum dissolved, all 120 Phase 1 runs (P32 ×4–×16, σ ensembles). (d) PR_V and PR_pore against d (gypsum-only); the "
        "PR_pore minimum (pore space and flow decoupled) comes before the PR_V minimum.",
        "four_stages.svg; anim2/stages_gyponly.png (make_stage_movie); channel_pr_vol_diss.png, mechanism_gyponly_diss.png (make_candidate_figures.py). "
        "NOTE: panel b still shows a capacity-time strip at the bottom; redraw on d before submission."),
    3: ("The clock is the mineral consumed.", "(a) Capacity time as the predicted clock. (b) Event timing of the five matched groups "
        "(σ 1, seeds 1–3, P32 ×4–×16, n = 12 per group, as the report table; Phase 1 gypsum-only and coupled at φ0 0.1, Phase 2 at φ0 0.05 and 2 mM carbonate), "
        "each group median divided by the median over groups, on four clocks. Numbers: largest/smallest group median (d ×1.36 and ×1.30, capacity time ×1.42 and ×1.44, τ ×3.1 and ×3.2). On P32 ×4–×8 alone the spread on d is ×1.16–1.20.",
        "capacity_clock.svg; new panel from phase1/stage_events_clocks.csv (fig3b_clock_groups.csv)"),
    4: ("Channels are inherited and narrow.", "(a) Share of the 90 %-flow set already in the initial set (overlap0) against d. "
        "(b) Stayers, leavers, joiners: size, transmissivity and position. (c) Where along x the leavers and joiners are.",
        "inheritance_diss.png; manuscript/channel_turnover.png, channel_turnover_x.png (channel_turnover.py)"),
    5: ("Depth law.", "(a) Channel depth (PR_V minimum / PR_V(0)) against the permeability ceiling, ×3.3–×20 (Phase 1 n = 60 per chemistry, Phase 2 n = 12 per case, Phase 3 n = 9). (b) Ceiling test "
        "paired on the same network (P32 ×4–×8, σ 1, seeds 1–3, n = 9): equal ceilings give equal depth across chemistries; "
        "lower ceilings give shallower channels. (c) Depth is a network property: same-network depth across chemistries.",
        "depth_law.png (make_candidate_figures.py); new panel from phase1/phase3_ceiling.csv; manuscript/depth_network_property.png"),
    6: ("Breakthrough is predicted by the initial flow field.", "(a) Dissolved fraction at breakthrough against the initial flow "
        "share of the largest-flow fracture, with leave-one-P32-out cross-validation and Phase 2 (same networks). (b) Wormhole "
        "scenario bound: breakthrough if part of each fracture's gypsum stays unreacted.",
        "manuscript/breakthrough_top1.png (breakthrough_predictor.py); wormhole_bound_report.png (wormhole_bound_figure.py)"),
    7: ("Transport signature.", "(a) Paused-pulse breakthrough curves before reaction and at the four stages, normalised concentration against pore volumes since the pulse (gypsum-only, P32 ×6, σ 1, seed 1). "
        "(b) Tail exponent and t50/τ_res against PR_V across all probed states.",
        "anim3/pulse_btc_only_gyponly.png (make_pulse_movie.py); manuscript/transport_binned.png (transport_channel_link.py)"),
    8: ("Robustness.", "(a) Rate test: dissolved fraction at the stage events at 0.1, 1 and 10 pore volumes per year (P32 ×6, σ 1, "
        "seeds 1–3; ×1 is the Phase 1 run, saved at different times). (b) Stage events on d by fracture intensity, P32 ×4–×16.",
        "new panels from phase1/phase3_rate.csv and phase1/stage_events_clocks.csv"),
}


def main():
    style(); OUT.mkdir(exist_ok=True)
    panel_clocks(OUT / "fig3b_clocks.png"); panel_ceiling(OUT / "fig5b_ceiling.png")
    panel_rate(OUT / "fig8a_rate.png"); panel_p32(OUT / "fig8b_p32.png")
    MS = FIGD / "manuscript"
    assemble("Figure_1", [[(HERE / "deck/network_p6_flow.png", 1)], [(CART / "fracture_cell.png", 1), (CART / "chemistry.png", 1)]])
    assemble("Figure_2", [[(CART / "four_stages.png", 1)], [(IMG / "anim2/stages_gyponly.png", 1)],
                          [(IMG / "channel_pr_vol_diss.png", 1.1), (IMG / "mechanism_gyponly_diss.png", 1)]])
    assemble("Figure_3", [[(CART / "capacity_clock.png", 1)], [(OUT / "fig3b_clocks.png", 1)]])
    assemble("Figure_4", [[(IMG / "inheritance_diss.png", 1)], [(MS / "channel_turnover.png", 1)], [(MS / "channel_turnover_x.png", 1)]])
    assemble("Figure_5", [[(FIGD / "depth_law.png", 1.15), (OUT / "fig5b_ceiling.png", 1), (MS / "depth_network_property.png", 0.8)]], width=9.0)
    assemble("Figure_6", [[(MS / "breakthrough_top1.png", 1)], [(IMG / "wormhole_bound_report.png", 1)]])
    assemble("Figure_7", [[(IMG / "anim3/pulse_btc_only_gyponly.png", 1)], [(MS / "transport_binned.png", 1)]])
    assemble("Figure_8", [[(OUT / "fig8a_rate.png", 1)], [(OUT / "fig8b_p32.png", 1)]])
    md = ["# Draft manuscript figures (5 Nov 2026)", "",
          "Built by `forsmark_reactive/make_manuscript_figures.py`. Drafts: panels are the study figures assembled with letters; "
          "new data panels (3b, 5b, 8a, 8b) are plotted from the CSVs. Supplement candidates: DFN validation (once run), regime map, "
          "d_Q size baseline, master curves, early-redistribution depth predictor, olivine outlook.", ""]
    for k, (t, cap, src) in CAPTIONS.items():
        md += [f"## Figure {k}. {t}", "", f"![Figure {k}](Figure_{k}.png)", "", cap, "", f"*Sources:* {src}", ""]
    (OUT / "FIGURES.md").write_text("\n".join(md))
    print("done", sorted(p.name for p in OUT.glob("Figure_*.png")))


if __name__ == "__main__":
    main()
