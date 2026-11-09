#!/usr/bin/env python3
"""
PI deck (9 Nov 2026): the whole Forsmark reactive-channel study for someone who has not seen it, laid out as
"what I'm confident of / what changed my mind / where we are". Written for Jeff Hyman: normalized times in his notation
(acid capacity gamma, tau = dV/V0), breakthrough curves in his style.
Figures: story/report/img (the report "Reactive Channels at Kilometre Scale") plus the new ones in this folder
(make_pi_figures.py). Movies are embedded (H.264 MP4). Numbers: story/STORY.md, gapfill/GAPFILL.md, pi_figures_numbers.json.
  cd forsmark_reactive/story/pi_deck && ../../deck/.venv/bin/python build_pi_deck.py   -> Reactive_Channels_PI.pptx
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "deck"))
from _helpers import prs, new_slide, text, bullets, title, picture, card, badge, stat, source, section, IMG, \
    INK, INK2, ACCENT, FLOW, WHITE, OPEN, CALCITE, HL, HEAD, M, W, H  # noqa: E402
from pptx.util import Inches  # noqa: E402

RUST, GREEN, PURPLE, WARM = "C4472D", "2F7A4F", "6B3FA0", "F8ECE7"
NUM = json.loads((HERE / "pi_figures_numbers.json").read_text())


def movie(s, mp4, poster, x, y, w, h):
    from PIL import Image
    iw, ih = Image.open(poster).size
    sc = min(w / iw, h / ih)
    pw, ph = iw * sc, ih * sc
    s.shapes.add_movie(str(mp4), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph),
                       poster_frame_image=str(poster), mime_type="video/mp4")


def fig_right_text(s, img, items, alt, fw=8.2, size=15):
    picture(s, img, M, 1.45, fw, 5.4, alt=alt)
    bullets(s, items, M + fw + 0.3, 1.6, W - 2 * M - fw - 0.3, 5.3, size=size)


def three_cards(s, cards, y=1.6, h=4.9, size=14):
    w = (W - 2 * M - 0.6) / 3
    for i, (head, body, fill) in enumerate(cards):
        x = M + i * (w + 0.3)
        card(s, x, y, w, h, fill=fill)
        text(s, head, x + 0.25, y + 0.2, w - 0.5, 0.8, size=18, bold=True, font=HEAD)
        bullets(s, body, x + 0.25, y + 1.0, w - 0.5, h - 1.1, size=size)


B = NUM["btc"]
CL = NUM["clocks"]
CO = NUM["collapse"]
DP = NUM["depth"]

# ===================================================================================================== opening
s = new_slide(dark=True, notes=(
    "Title. This is the Forsmark reactive-channel study: 456 reactive simulations on 117 fracture networks built from SKB "
    "Forsmark FFM01 statistics, 1 to 2 km long, 1,587 to 14,658 fractures each. The model is BiGraFV: PFLOTRAN reactive "
    "transport on a graph where one control volume is one whole fracture. The deck is laid out as what I am confident of, "
    "what changed my mind, and where we are."))
text(s, "Reactive channels in mineral-filled fracture networks", M, 1.9, W - 2 * M, 1.6, size=40, bold=True, font=HEAD,
     color=WHITE)
text(s, "What 456 BiGraFV simulations at kilometre scale taught us, and where we are", M, 3.55, W - 2 * M, 0.8, size=20,
     color="C9D4DC", italic=True)
text(s, "Forsmark FFM01 networks · gypsum and coupled gypsum–calcite · PFLOTRAN on a fracture graph · 9 November 2026",
     M, 6.6, W - 2 * M, 0.4, size=12, color="8FA3B3")

s = new_slide(notes=(
    "The short version. Three things I am confident of: one sequence of four stages; a focus that travels with the dissolution "
    "front and relaxes behind it because the soluble fill runs out (the part we have not found published; Hyman 2026 Fig. 11 "
    "has the moving front, with wall rock that keeps dissolving, and focusing persists behind it); and a channel depth set by the attainable "
    "permeability gain C, the same curve for both chemistries. One thing that changed my mind: the early-arrival predictor "
    "only ranks breakthrough roughly, it failed its blind test. Where we are: the story is stable, the DFN check on a 500 m "
    "network started this morning and is the one thing that could change it."))
title(s, "The short version")
rows = [("1", "One sequence, four stages", "open space decouples from flow, recouples, focuses and breaks through, relaxes "
         "(87 of 90 runs)", ACCENT),
        ("2", "A focus that travels and relaxes", "each 100 m stretch focuses as the front passes, then returns to within 2 % "
         "of its start: the fill runs out", ACCENT),
        ("3", "Depth set by the attainable gain C", "how far flow concentrates: 0.78 of its start at ×5.5 to 0.15 at ×1000; "
         "both chemistries on one curve (within ~0.02)", ACCENT),
        ("?", "Changed my mind", "early tracer arrival ranks breakthrough only roughly (blind test failed); the right clock is "
         "gypsum dissolved, not time", RUST),
        ("→", "Where we are", "story stable; DFN check on the 500 m network running since this morning, verdict ~Wednesday", GREEN)]
for i, (b, head, body, col) in enumerate(rows):
    y = 1.55 + i * 1.08
    badge(s, b, M, y + 0.05, d=0.6, fill=col)
    text(s, head, M + 0.9, y, 4.2, 0.5, size=19, bold=True, font=HEAD)
    text(s, body, M + 5.2, y + 0.05, W - 2 * M - 5.2, 0.9, size=15, color=INK2)

s = new_slide(notes=(
    "Where this sits. Hyman, Szawełło, Kang and Szymczak (2026, JGR) run a graph model of 3D DFNs, up to 25 m and about 526 "
    "fractures, where the wall rock itself dissolves and apertures keep growing (no exhaustion of the soluble rock is modelled); they map regimes in Da and G. "
    "Meshed DFN studies stop around 10 m. Our system is different in two ways that matter: the soluble material is a finite "
    "vein fill (gypsum filling 90 % of each fracture), and the networks are a kilometre long with thousands of fractures. "
    "One BiGraFV cell per fracture is what makes 456 runs of that size possible."))
title(s, "Where this sits relative to Hyman et al. 2026")
card(s, M, 1.6, 5.9, 4.9, fill=HL)
text(s, "Hyman et al. 2026 (JGR)", M + 0.3, 1.8, 5.3, 0.5, size=20, bold=True, font=HEAD)
bullets(s, ["graph model of 3D DFNs, ~25 m, ~526 fractures",
            "the wall rock dissolves: apertures keep growing",
            "regimes mapped in Da and G; wormholing at high Da",
            "a focusing front moves downstream (Fig. 11); behind it focusing persists",
            "time: τ = ΔV/V0, dissolved volume over initial void volume"], M + 0.3, 2.5, 5.3, 4.0, size=15)
card(s, M + 6.3, 1.6, W - 2 * M - 6.3, 4.9, fill="E3F1E8")
text(s, "This study", M + 6.6, 1.8, 5.3, 0.5, size=20, bold=True, font=HEAD)
bullets(s, ["BiGraFV: one PFLOTRAN control volume per fracture, 1–2 km, 1,587–14,658 fractures",
            "a finite vein fill dissolves (gypsum, 90 % of each fracture); walls never do",
            "real gypsum and calcite kinetics, mineral volume, porosity–permeability feedback",
            "456 runs: chemistry, permeability law, rate, length, density, transmissivity spread",
            "flow re-solved on the frozen state at every saved step"], M + 6.6, 2.5, W - 2 * M - 6.9, 4.0, size=15)

# ===================================================================================================== setup
section("Set-up", "The model, what we ran, and the three normalized times",
        notes="Set-up: what one cell is, what we ran, and the clocks, defined the way Hyman defines his.")

s = new_slide(notes=(
    "One cell is one whole fracture, well mixed: one porosity, one concentration, one permeability. Each fracture starts as a "
    "vein: 90 % gypsum, 10 % open. Two chemistries. Gypsum-only: dilute water dissolves the vein away; porosity can only reach "
    "1, so with k proportional to porosity the permeability can only rise ×10. Coupled: a 0.5 M carbonate brine; calcite "
    "replaces gypsum and keeps 0.494 of its volume, so the cell ends 44.5 % calcite, porosity 0.555, ×5.55. Neighbours connect "
    "through intersections. No fronts inside a fracture: it opens all at once. That is the main limitation and why the DFN "
    "check matters."))
title(s, "One cell = one fracture, filled with a gypsum vein")
picture(s, IMG / "fracture_cell.png", M, 1.4, W - 2 * M, 5.5, alt="Fracture cell cartoon")

s = new_slide(notes=(
    "What we ran. Networks from SKB Forsmark FFM01 statistics, 1000 × 250 × 250 m (and 2000 × 500 × 250 m), intensity P32 "
    "scaled ×4 to ×16 so they percolate over a kilometre, transmissivity spread σ 0, 0.5 and 1, 5 seeds. Flow: one network "
    "pore volume per year at a fixed rate (Hyman's convention). Permeability k = k0 (φ/φ0)^n; n = 1 in the main runs, "
    "n = 0.5 to 8 in the law tests. Each saved state the flow is re-solved on the frozen permeability to get per-fracture "
    "throughflow. 456 reactive runs in all."))
title(s, "What we ran")
for i, (big, lab) in enumerate([("456", "reactive runs"), ("117", "networks, 1–2 km"), ("1,587–14,658", "fractures per network")]):
    stat(s, big, lab, M + i * 4.1, 1.5, 3.9, color=[FLOW, ACCENT, RUST][i], big_size=40)
bullets(s, ["Networks: SKB Forsmark FFM01 fracture statistics; P32 ×4, ×6, ×8, ×16; transmissivity spread σ 0 / 0.5 / 1; 5 seeds",
            "Flow: fixed rate of one network pore volume per year",
            "Chemistry: gypsum-only (dilute water) and coupled gypsum–calcite (0.5 M carbonate brine)",
            "Permeability: k = k0 (φ/φ0)ⁿ, φ0 = 0.1; n = 1 main runs, n = 0.5–8 in the law tests",
            "Measures: flow re-solved on every saved state; per-fracture throughflow, porosity, gypsum"],
        M, 3.6, W - 2 * M, 3.4, size=16)

s = new_slide(notes=(
    "Normalized times. Three clocks. PVI, pore volumes injected, is Q t over the initial pore volume. Gypsum dissolved d is the "
    "fraction of the network's gypsum gone; it is Hyman's tau = ΔV/V0 divided by its maximum, tau_max = V_gypsum,0 / V_pore,0 = 9 "
    "here, because each fracture is 90 % gypsum. Capacity time uses Hyman's acid capacity number gamma = c0/(ν c_sol): the volume "
    "of mineral one volume of injected fluid can remove. For gypsum the 'reactant' is undersaturation: dilute water can carry "
    "16.6 mol/m3 before it is saturated, and solid gypsum is 13,400 mol/m3, so gamma = 1.24e-3. Capacity time is gamma × PVI "
    "divided by tau_max: t_cap = 1 means enough water has gone in to remove the whole inventory if every parcel left saturated. "
    "That is 7,259 PVI for gypsum-only; for the coupled brine each carbonate also takes one Ca out as calcite, gamma = 0.039 "
    "and t_cap = 1 is 233 PVI. The figure is one network. Up to d about 0.4 the curve sits on the dashed line: every parcel of "
    "water leaves saturated. After breakthrough water exits through the opened channel undersaturated, and d falls below t_cap."))
title(s, "Normalized times, in Hyman's notation")
picture(s, HERE / "fig_clocks.png", M, 1.4, 7.6, 5.6, alt="Gypsum dissolved against capacity time")
x0 = M + 7.85
text(s, [[("PVI", {"bold": True, "color": ACCENT}), ("  pore volumes injected = Q t / V", {}), ("pore,0", {"sub": True})]],
     x0, 1.55, W - x0 - M, 0.6, size=15)
text(s, [[("γ", {"bold": True, "color": ACCENT}), ("  acid capacity (Hyman): c", {}), ("0", {"sub": True}),
          (" / (ν c", {}), ("sol", {"sub": True}), (") = volume of mineral one volume of fluid removes", {})]],
     x0, 2.2, W - x0 - M, 0.9, size=15)
text(s, "gypsum: c0 = 16.6 mol/m³ (saturation of dilute water), c_sol = 13,400 mol/m³ → γ = 1.24 × 10⁻³", x0, 3.0,
     W - x0 - M, 0.7, size=12, color=INK2)
text(s, [[("t", {"bold": True, "color": ACCENT}), ("cap", {"sub": True, "bold": True, "color": ACCENT}),
          ("  capacity time = γ · PVI / τ", {}), ("max", {"sub": True}),
          ("; 1 = enough water in to remove the whole inventory if it all left saturated", {})]], x0, 3.7, W - x0 - M, 1.1, size=15)
text(s, "gypsum-only: 1 t_cap = 7,259 PVI · coupled: 1 t_cap = 233 PVI", x0, 4.75, W - x0 - M, 0.5, size=12, color=INK2)
text(s, [[("d", {"bold": True, "color": ACCENT}), ("  gypsum dissolved = Hyman τ / τ", {}), ("max", {"sub": True}),
          (", τ = ΔV/V", {}), ("0", {"sub": True}), (", τ", {}), ("max", {"sub": True}), (" = 9; d ≤ t", {}),
          ("cap", {"sub": True}), (" always", {})]], x0, 5.3, W - x0 - M, 0.9, size=15)
text(s, "Every stage event is timed on d.", x0, 6.25, W - x0 - M, 0.4, size=15, bold=True)

# ===================================================================================================== confident: stages
section("What I'm confident of · 1", "One sequence: four stages in the same order",
        notes="First of three results I am confident of.")

s = new_slide(notes=(
    "The four stages as a cartoon. Stage 1: gypsum near the inlet dissolves, but the water still has to squeeze through filled "
    "fractures further on, so the opened space does not yet change where water goes: open space and flow decouple. Stage 2: "
    "the front runs down the paths that already carried the flow. Stage 3: flow crowds into those opened paths, most strongly "
    "just before the front reaches the outlet, and breaks through. Stage 4: once the gypsum along those paths is gone, "
    "neighbouring paths catch up and flow spreads out again."))
title(s, "Four stages, one order")
picture(s, IMG / "four_stages.png", M, 1.35, W - 2 * M, 5.7, alt="Four stages cartoon")

s = new_slide(notes=(
    "The data behind the cartoon, median and IQR of 45 runs per chemistry. PR_V is the participation ratio of flow against "
    "fracture volume: 1 when flow is proportional to volume, smaller when flow is concentrated. PR_pore is the same against open "
    "pore volume. Event medians on d: pore-volume minimum 0.17 (gypsum-only) / 0.20 (coupled); PR_V minimum 0.37 / 0.44; "
    "breakthrough 0.56 / 0.63. The order pore-volume minimum ≤ PR_V minimum ≤ breakthrough holds in 87 of 90 runs at 1 km and "
    "83 of 90 at 2 km. Decoupling: PR_pore/PR_V falls below its start in all 45 runs per chemistry (to 0.68 / 0.80 at d ≈ 0.1), "
    "crosses 1 at d ≈ 0.3 and peaks at 1.52 / 1.28 near d = 0.5. At the end PR_V is 0.995 / 1.01 of its start."))
title(s, "The same order in 87 of 90 runs")
picture(s, IMG / "fig1_stages.png", M, 1.35, W - 2 * M, 3.9, alt="Stage figure")
stat(s, "87 / 90", "runs with pore-volume minimum ≤ PR_V minimum ≤ breakthrough (83 / 90 at 2 km)", M, 5.35, 3.9, big_size=30, label_size=13)
stat(s, "0.17 · 0.37 · 0.56", "gypsum dissolved at the three events (gypsum-only medians)", M + 4.2, 5.35, 4.1, color=ACCENT, big_size=30, label_size=13)
stat(s, "0.995", "network PR_V at the end relative to its start: it relaxes", M + 8.6, 5.35, 3.5, color=RUST, big_size=30, label_size=13)

s = new_slide(notes=(
    "The four stages in a real network: two slices through the example network (P32 ×6, σ 1, seed 1, gypsum-only). Blue is open "
    "and flowing, light blue open with little flow, orange flow through still-filled rock. Play it: the inlet opens without "
    "taking the flow, then the flow finds the opened paths, the focus runs to the outlet, and the network spreads out again."))
title(s, "Watch it in one network")
movie(s, IMG / "movie_gyponly.mp4", IMG / "stages_gyponly.png", M, 1.35, W - 2 * M, 5.75)

# ===================================================================================================== confident: moving focus
section("What I'm confident of · 2", "The focus travels with the front and relaxes behind it",
        notes="Second result, the one we have not found published.")

s = new_slide(notes=(
    "Cut each network into ten 100 m stretches along the flow and compute PR_V per stretch relative to its start. Short bar = "
    "flow concentrated. Median of 45 networks per chemistry. Watch the short bar travel from inlet to outlet while the "
    "stretches behind it grow back to 1. It is a travelling wave of focusing, not a permanent channel."))
title(s, "The focus is a travelling wave")
movie(s, IMG / "focus_front.mp4", IMG / "focus_front_mid.png", M, 1.35, W - 2 * M, 5.75)

s = new_slide(notes=(
    "Numbers. The gypsum dissolved at each stretch's minimum rises from 0.03 at the inlet to 0.50 (gypsum-only) and 0.58 "
    "(coupled) at the outlet. The outlet stretch focuses most: 0.36 / 0.52 of its start, against 0.54–0.66 / 0.67–0.76 upstream, "
    "because it is the last place where the opened channel still pushes through filled rock. Every stretch ends within 0.8 % "
    "(gypsum-only) and 1.7 % (coupled) of its start. It holds when fractures are counted in every stretch they span."))
title(s, "Each stretch focuses once, then returns to its start")
picture(s, IMG / "fig2_front.png", M, 1.35, W - 2 * M, 3.9, alt="Front figure")
stat(s, "0.03 → 0.50", "gypsum dissolved at each stretch's minimum, inlet → outlet", M, 5.35, 3.9, big_size=30, label_size=13)
stat(s, "0.36", "outlet stretch at its minimum: the strongest local focusing", M + 4.2, 5.35, 3.9, color=ACCENT, big_size=30, label_size=13)
stat(s, "< 2 %", "every stretch ends this close to its start", M + 8.6, 5.35, 3.5, color=RUST, big_size=30, label_size=13)

s = new_slide(notes=(
    "Why this is new relative to Hyman 2026 Fig. 11. There, a focusing front moves downstream too, but the soluble material is "
    "the wall rock itself, which keeps dissolving, so behind the front focusing persists near its maximum (our reading of their "
    "snapshots, which stop at tau = 1). Here the soluble material is "
    "a finite fill. Once a stretch's gypsum is gone, the opened paths stop gaining on their neighbours, the neighbours catch up, "
    "and the stretch relaxes. We tested and rejected one explanation: the width of the focused zone does not set when the whole "
    "network is most focused (pre-set test failed, rank correlation 0.27–0.50)."))
title(s, "What is new: relaxation behind the front")
for i, (head, body, fill) in enumerate([
        ("Dissolving wall rock (Hyman et al. 2026)", ["a focusing front moves downstream (Fig. 11)",
                                                    "behind it, focusing persists near its maximum",
                                                    "apertures keep growing; the channel stays"], HL),
        ("Finite soluble fill (this study)", ["the same moving front",
                                             "behind it, each stretch returns to its start",
                                             "the fill runs out, so the channel's advantage ends"], "E3F1E8")]):
    x = M + i * 6.2
    card(s, x, 1.7, 5.9, 4.3, fill=fill)
    text(s, head, x + 0.3, 1.95, 5.3, 0.6, size=19, bold=True, font=HEAD)
    bullets(s, body, x + 0.3, 2.75, 5.3, 3.0, size=17)
text(s, "Not the explanation: the width of the focused zone does not set when the whole network is most focused "
     "(pre-set test failed, ρ 0.27–0.50).", M, 6.35, W - 2 * M, 0.6, size=13, color=INK2)

s = new_slide(notes=(
    "Does it still relax when a cleared fracture gains far more permeability? Run A took n = 2 (×100) and n = 3 (×1000) to "
    "capacity time 8, run A2 took gypsum-only ×1000 to 20. ×100 completes by capacity time 8 (network 0.99 of its start). ×1000 "
    "completes in the median: network PR_V 0.95, every stretch median at least 0.935 recovered, the median curve crosses 0.9 at "
    "capacity time 10.3 against about 2.5 at ×100. Per network it is less uniform: 8 of 9 reach 0.9, only 3 of 9 recover every "
    "stretch, and one network (p4 seed 2) is not done. Panel B: below d 0.5 ×1000 dips much deeper at the same d (the depth law, "
    "next section); from d 0.5 to 0.81 ×100 and ×1000 sit within 0.028 (pre-set rule, thin margin). Panel D, exploratory: with "
    "the same gypsum left, ×1000 dissolves it 3–4× more slowly (all-network medians, panel D; 3.4–7.7× on matched networks) and its flow sees 5–8× less of it, consistent with the channel "
    "bypassing the gypsum left. It needs about four times the water to get to the same place (capacity time 10.3 against 2.5 to "
    "reach PR_V 0.9; 8.5 against 2.1 to reach d 0.8). The pre-set bypass test compared "
    "at matched capacity time and failed, because ×1000 holds more gypsum at any given time."))
title(s, "At high gain it still relaxes, it just needs more water")
picture(s, IMG / "fig5_latetime.png", M, 1.35, 8.1, 5.6, alt="Figure 5")
stat(s, "0.95", "median network PR_V / start at ×1000, capacity time 20 (×100: 0.99 by 8); 8 of 9 networks ≥ 0.9", 8.8, 1.5, 3.9, big_size=30, label_size=13)
stat(s, "≤ 0.03", "gap between ×100 and ×1000 at the same gypsum dissolved, d 0.5–0.81 (pre-set)", 8.8, 3.25, 3.9, color=ACCENT, big_size=30, label_size=13)
stat(s, "3–4×", "slower dissolution at ×1000 with the same gypsum left, consistent with bypass (exploratory)", 8.8, 5.0, 3.9, color=RUST, big_size=30, label_size=13)

# ===================================================================================================== transport
section("What it does to transport", "Breakthrough curves, read the way Hyman reads them",
        notes="Transport. At each saved state we freeze the reacted network, re-solve flow, and push a tracer pulse through it.")

s = new_slide(notes=(
    "The reaction is paused at each stage, flow is re-solved on the frozen network, and a tracer pulse of 0.1 residence times "
    "runs through. The left panel is the network, the right the outlet breakthrough curve building up. This is an Eulerian pulse "
    "with numerical dispersion, not particle tracking, so compare states with each other rather than with Hyman's particle "
    "curves in absolute terms."))
title(s, "A tracer pulse through the frozen network at each stage")
movie(s, IMG / "pulse_gyponly.mp4", HERE / "pulse_poster.png", M, 1.35, W - 2 * M, 5.75)

bt = B["t50_res"]
gm = B["gamma"]
al = B["alpha_L_rel"]
s = new_slide(notes=(
    "Breakthrough curves in Hyman's style: the PDF of travel time on log-log axes, time normalized by the first arrival in the "
    "unreacted network, median and IQR over 60 gypsum-only networks (45 at capacity time 5), at fixed snapshots in capacity time (his snapshots are in "
    "tau; ours are capacity time 0, 0.1, 0.5, 1, 2, 5, median gypsum dissolved 0, 0.10, 0.50, 0.76, 0.90, 0.93). Panel A: the "
    "whole curve moves about ten times later. That is the pore volume growing ×10 at a fixed flow rate, exactly the effect Hyman "
    "reports in his uniform regime (peak arrival almost doubles as the void volume doubles at tau = 1, Da 2e-4, G 0.1). It is not the channel. Panel B removes "
    "it by scaling with the current residence time: the shape changes little, and what changes, C to E, follows the stages. "
    f"Median arrival rises from {bt['0'][1]:.2f} to {bt['1'][1]:.2f} residence times at capacity time 1 and falls back to "
    f"{bt['5'][1]:.2f}; the tail exponent rises from {gm['0'][1]:.1f} to {gm['0.5'][1]:.1f} and returns to {gm['5'][1]:.1f}; "
    f"dispersivity drops to {al['0.5'][1]:.2f} of the unreacted value and returns to {al['5'][1]:.2f}."))
title(s, "Breakthrough curves, Hyman-style")
picture(s, HERE / "fig_btc_hyman.png", M, 1.3, 8.3, 5.75, alt="Hyman-style breakthrough curves")
x0 = M + 8.5
text(s, "How to read it", x0, 1.45, W - x0 - M, 0.5, size=19, bold=True, font=HEAD)
bullets(s, [[("A: ", {"bold": True}), ("the whole curve moves ~10× later: pore volume grows ×10 at fixed Q (Hyman's uniform-regime "
             "shift), not the channel", {})],
            [("B: ", {"bold": True}), ("scaled by current residence time, the shape barely changes", {})],
            [("C–E: ", {"bold": True}), (f"while the channel exists the curve narrows (arrival {bt['0'][1]:.2f} → {bt['1'][1]:.2f}, "
             f"tail γ {gm['0'][1]:.1f} → {gm['0.5'][1]:.1f}, dispersivity −{100 * (1 - al['0.5'][1]):.0f} %), then relaxes back", {})],
            [("No dual scaling: ", {"bold": True}), ("unlike a wormhole, there is no fast primary and slow secondary branch", {})]],
        x0, 2.05, W - x0 - M, 4.9, size=14)

s = new_slide(notes=(
    "What is happening physically. Early on (stage 1), the opened space is near the inlet but the flow is not there yet, so the "
    "tracer samples the network much as before. In the channel stages, open space and flow coincide: the paths that carry the "
    "flow are the paths whose pore space has opened (PR_pore/PR_V peaks at 1.5 near d 0.5). Water then spends its time in the "
    "pore volume that actually exists, so the median arrival moves towards one residence time, the curve narrows and the tail "
    "steepens: fewer slow, side paths. This is the opposite sign to Hyman's wormhole regime, where first arrivals get earlier "
    "and the curve shows dual scaling, because there the wormhole takes almost all the flow while the rest stagnates. Here the "
    "fill runs out everywhere, so the side paths catch up and the curve relaxes back, the transport signature of the relaxation."))
title(s, "What the curves say")
three_cards(s, [
    ("Stage 1–2: little change", ["opened space sits near the inlet; flow has not moved",
                                  "the pulse samples the network much as before",
                                  f"median arrival {bt['0'][1]:.2f} → {bt['0.1'][1]:.2f} residence times"], HL),
    ("Stage 3: narrower, steeper tail", ["flow and opened space coincide (PR_pore/PR_V peaks at 1.5)",
                                         "water spends its time in space that exists: arrival → 1 residence time",
                                         f"tail γ {gm['0'][1]:.1f} → {gm['0.5'][1]:.1f}; dispersivity −{100 * (1 - al['0.5'][1]):.0f} %"], WARM),
    ("Stage 4: back again", ["the fill runs out everywhere; side paths catch up",
                             f"arrival back to {bt['5'][1]:.2f}, tail γ {gm['5'][1]:.1f}, dispersivity ×{al['5'][1]:.2f}",
                             "Hyman's wormhole regime goes the other way: earlier first arrival and dual scaling"], "E3F1E8")], size=16)

# ===================================================================================================== confident: depth law
section("What I'm confident of · 3", "How deep the channel gets is set by the attainable permeability gain",
        notes="Third result, and the hardest one to explain. Four slides: what depth means, what the law does, the collapse, "
              "and what does and does not change.")

s = new_slide(notes=(
    "What the depth numbers mean. PR_V is a participation ratio: (sum of Q)^2 over the sum of Q^2 / w, with w each fracture's "
    "share of the volume. It is 1 when flow is spread in proportion to volume, and it reads as the share of the network's "
    f"fracture volume that effectively carries the flow. At the start a typical network is about {DP['prv_start_median_9net']:.2f} "
    f"(9 networks, {DP['prv_start_range'][0]:.2f}–{DP['prv_start_range'][1]:.2f}): flow effectively uses about 40 % of the "
    "volume. Depth is the lowest PR_V reached over its start value. Depth 0.78 (at ×5.5 gain) means at its most focused the flow "
    "uses 78 % of the volume it used at the start: a mild crowding. Depth 0.15 (at ×1000) means it uses 15 % of it: the same "
    "water squeezed into about a seventh of the volume. The bars are a cartoon with 40 equal fractures, tuned to those numbers."))
title(s, "What 'depth 0.78' and 'depth 0.15' mean")
picture(s, HERE / "fig_depth_meaning.png", M, 1.35, W - 2 * M, 3.75, alt="Flow shares cartoon")
bullets(s, [[("PR", {"bold": True}), ("V", {"sub": True, "bold": True}),
             (": the share of fracture volume that effectively carries the flow (1 = flow in proportion to volume). "
              f"A typical network starts at {DP['prv_start_median_9net']:.2f}.", {})],
            [("Depth", {"bold": True}), (" = lowest PR", {}), ("V", {"sub": True}), (" / PR", {}), ("V", {"sub": True}),
             (" at the start. Lower = flow squeezed into less of the network.", {})],
            [("0.78", {"bold": True, "color": ACCENT}), (": flow uses 78 % of the volume it used at the start (mild).  ", {}),
             ("0.15", {"bold": True, "color": RUST}), (": 15 %, the same water in about a seventh of the volume.", {})]],
        M, 5.25, W - 2 * M, 1.9, size=15, space=6)

s = new_slide(notes=(
    "The permeability law, plainly. Every run is a filled vein; only the fill dissolves, never the wall rock, and every run "
    "eventually runs out of fill. The law k = k0 (φ/φ0)^n says how much more permeable the vein gets as it clears. n = 1: "
    "permeability in proportion to open space, as if the cleared space stays rough and porous; fully cleared it is ×10. n = 3: "
    "permeability goes as porosity cubed, which is exactly the cubic law for a vein whose fill clears to leave a smooth "
    "parallel-plate slot: ×1000. So n sets the end value, the attainable gain C. Calcite refills part of the space, so the same "
    "law gives the coupled chemistry a lower C (×5.55 instead of ×10 at n = 1). Right panel: two separate questions. Solid "
    "lines change where the law ends (C = ×10 to ×1000). Dashed lines all end at ×10 but take different paths (n = 0.5, 2, 8 "
    "with a critical porosity chosen so the end is ×10)."))
title(s, "The permeability law: how much a cleared vein gains")
picture(s, HERE / "fig_kphi_laws.png", M, 1.35, W - 2 * M, 5.7, alt="k-phi cartoon and laws")

s = new_slide(notes=(
    f"The collapse. Panel A: plotted against n, the two chemistries sit apart: at the same n, coupled is shallower by "
    f"{CO['paired_n_median_gap']:.2f} (median, same network). That is because calcite lowers C. Panel B: plotted against C, "
    "both chemistries, both starting porosities (φ0 0.10 and 0.18) and the four law shapes at ×10 fall on one curve "
    "(median and IQR of 9 networks; the spread is network to network). Panel C is the cleanest test: network by network, coupled "
    f"depth against gypsum-only depth on the same network. Matched by n (open circles) they are off the diagonal. Matched by C "
    f"(filled, gypsum-only interpolated to the coupled C) they sit on it, within {CO['paired_C_median_abs']:.3f} (median of 36 "
    "pairs; pre-set σ 1 rule R2 passed at 0.05; at σ 0, 0.029 against the run C rule of 0.03). The coupled runs sit slightly shallower, consistently, by about 0.02."))
title(s, "Plot against C, and the chemistries collapse")
picture(s, HERE / "fig_collapse.png", M, 1.35, W - 2 * M, 4.3, alt="Collapse figure")
stat(s, f"{CO['paired_n_median_gap']:.2f}", "coupled minus gypsum-only depth at the same n (same network, median)", M, 5.75, 3.9, color=RUST, big_size=30, label_size=13)
stat(s, f"{CO['paired_C_median_abs']:.3f}", "the same at the same C: one curve (36 pairs; σ 0: 0.029)", M + 4.2, 5.75, 3.9, color=ACCENT, big_size=30, label_size=13)
stat(s, "0.78 → 0.15", "median depth from ×5.5 to ×1000 (gypsum-only, 9 networks)", M + 8.6, 5.75, 3.5, big_size=30, label_size=13)

e0 = CO["e0_depths"]
s = new_slide(notes=(
    "What '±0.04' means. On one network (P32 ×6, σ 1, seed 1) we held the end value at ×10 and changed only the shape of the "
    f"law: n = 0.5, 1, 2, 8. Depth was {e0['n0.5']:.2f}, {e0['n1']:.2f}, {e0['n2']:.2f}, {e0['n8']:.2f}: a spread of 0.08, "
    "±0.04 around the n = 1 value. Going from ×10 to ×1000 on the same network moved depth to 0.21, a change of 0.47. So the "
    "shape is a small correction and the end value is the big lever. The apertures show why the law matters physically: with "
    "any ×10 law the hydraulic aperture can grow at most ×2.15, the cube root of 10 (median 75 to 106–122 µm); with n = 3, 13 % of "
    "fractures open fully and the top 5 % reach 0.93 mm. Caveat: one network."))
title(s, "'±0.04': same end value, four shapes")
picture(s, IMG / "kphi_e0_curves.png", M, 1.35, W - 2 * M, 3.4, alt="Four law shapes at x10")
stat(s, f"{e0['n0.5']:.2f} · {e0['n1']:.2f} · {e0['n2']:.2f} · {e0['n8']:.2f}",
     "depth for n = 0.5, 1, 2, 8, all ending at ×10 (one network): a spread of 0.08, ±0.04", M, 4.95, 6.0, big_size=28, label_size=13)
stat(s, "0.21", "depth on the same network at ×1000: a change of 0.47", M + 6.4, 4.95, 2.8, color=RUST, big_size=28, label_size=13)
text(s, "The shape of the law is a small correction; where it ends (C) is the lever.", M + 9.4, 5.0, W - M - 9.4 - M, 1.4,
     size=16, bold=True, color=INK)

s = new_slide(notes=(
    "Answering the obvious question directly. Does changing the law change the model's outcome? It changes the channel: how "
    "deep (0.78 to 0.15), how early (breakthrough at 0.65 to 0.27 of the gypsum dissolved), and how much water the relaxation "
    "needs (about four times more at ×1000). It does not change the story: the four stages in order, the moving focus that "
    "relaxes behind the front, the channel forming inside the paths that already carried the flow (91–100 % of the high-gain "
    "channel lies inside the n = 1 channel), and the two chemistries on one curve. Two refinements. First, it is C, not n: the "
    "same C reached by different n or by different chemistry gives the same depth. Second, low and high n are not 'runs out "
    "of fill' versus 'dissolves wall rock': no run ever dissolves wall rock, and every run runs out of fill. Low C is a cleared "
    "vein that stays rough; high C is a cleared vein that becomes a smooth open slot. High C behaves more like Hyman's unlimited "
    "case for longer (deeper, earlier, slower to relax) but still relaxes, because the fill runs out."))
title(s, "So what does the law change, and what does it not?")
three_cards(s, [
    ("Changes with C", ["how deep: depth 0.78 → 0.15 (×5.5 → ×1000)",
                        "how early: breakthrough at 0.65 → 0.27 of the gypsum dissolved",
                        "how much water to relax: about 4× more at ×1000"], WARM),
    ("Does not change", ["four stages in the same order",
                         "the focus travels and relaxes behind the front",
                         "the channel forms inside the initial fast paths (91–100 %)",
                         "both chemistries on one curve (within ~0.02)"], "E3F1E8"),
    ("Not 'fill vs wall rock'", ["no run dissolves wall rock; every run runs out of fill",
                                 "low C: the cleared vein stays rough (k ∝ φ)",
                                 "high C: it clears to a smooth slot (cubic law, k ∝ φ³)",
                                 "high C looks like Hyman's case for longer, then still relaxes"], HL)], h=4.3, size=16)
text(s, "In one line: the law changes the channel (how deep, how early, how much water), not the story.", M, 6.25, W - 2 * M, 0.5,
     size=18, bold=True, font=HEAD, color=ACCENT)

# ===================================================================================================== changed my mind
section("What changed my mind", "A predictor that only ranks, and the right clock",
        notes="Two things I believed a week ago that I no longer do, at least not as strongly.")

s = new_slide(notes=(
    "The predictor. Before any reaction, push a tracer pulse through the network and time how fast the first 10 % comes out, "
    "in mean residence times: t10. Fitted on 45 networks per chemistry, it predicted the gypsum dissolved at breakthrough with "
    "R² 0.77 / 0.75 (each P32 level held out). Grey crosses: 45 new 2 km networks, where it ranks only weakly (R² 0.39 / 0.01). "
    "Open diamonds: 12 new 1 km networks run after the line was frozen. The pre-set blind test failed: R² −0.17 / 0.45, rank "
    "correlation 0.51 / 0.72. The honest estimate, all 27 σ 1 networks with one left out at a time: R² 0.51 / 0.62, rank "
    "correlation 0.76 / 0.83. It ranks breakthrough; it does not pin it down."))
title(s, "Early tracer arrival ranks breakthrough, roughly")
picture(s, IMG / "fig4_predictor.png", M, 1.35, W - 2 * M, 3.9, alt="Predictor figure")
stat(s, "0.77", "R² with each P32 level held out (gypsum-only, training set)", M, 5.35, 3.9, big_size=30, label_size=13)
stat(s, "−0.17 / 0.45", "R² on 12 blind networks (gypsum-only / coupled): failed", M + 4.2, 5.35, 3.9, color=RUST, big_size=30, label_size=13)
stat(s, "0.51 / 0.62", "honest estimate, 27 networks one left out (ρ 0.76 / 0.83)", M + 8.6, 5.35, 3.5, color=ACCENT, big_size=30, label_size=13)

s = new_slide(notes=(
    "Why it missed. Not the measurement: saved states are 0.059–0.065 of the gypsum apart in every set (medians), and interpolating "
    "breakthrough does not help. Not the probe: recovery 0.998–0.999 and the same t10 spread. Not network structure: none of 8 "
    "pre-run statistics correlates with the residual (|ρ| ≤ 0.16) and the blind and training networks are indistinguishable. "
    "Panel A is the answer: across 20,000 random 15 / 12 splits of the 27 σ 1 networks, the test R² has median 0.49 / 0.60 and "
    "falls below 0.5 in 52 % / 30 % of splits; the actual blind split sits at the 6th / 26th percentile. With 12 test networks, "
    "passing at 0.5 was close to a coin flip, and the training 0.77 was a lucky draw. At 2 km the relation itself is weaker: "
    "slope 1.23 / 0.90 against 1.45 / 1.49, and noisier. Why is still open. The lesson for the papers: this is a supporting "
    "result, and any stronger claim needs many more networks and a new blind set."))
title(s, "Why the blind test missed")
picture(s, IMG / "figS4_predictor_diag.png", M, 1.35, W - 2 * M, 3.9, alt="Predictor diagnosis")
bullets(s, ["Not the measurement, the probe or the network structure (8 pre-run statistics, |ρ| ≤ 0.16)",
            "Random 15 / 12 splits: the test R² falls below 0.5 in 52 % (gypsum-only); the real split sat at the 6th percentile",
            "At 2 km the relation is shallower and noisier (slope 1.23 against 1.45): early arrival says less over a longer path"],
        M, 5.4, W - 2 * M, 1.8, size=15, space=4)

s = new_slide(notes=(
    "The second thing: the clock. A week ago I compared runs at the same time. The ×1000 runs looked slow, and the pre-set test of "
    "why compared them with ×100 at the same capacity time; it failed, because at any given time ×1000 still holds much more "
    "gypsum (d 0.52 against 0.74 at capacity time 2). Compared at the same gypsum dissolved, the two relax together from d 0.5, and "
    "×1000's slowness shows up as lower dissolution efficiency: the water passes the gypsum that is left. Every event in this "
    "deck is timed on d for that reason. Capacity time is still the right axis for 'how much water', d for 'how far along'."))
title(s, "The right clock is gypsum dissolved, not time")
picture(s, HERE / "fig_clocks.png", M, 1.4, 6.6, 4.9, alt="clocks")
bullets(s, ["Compared at the same capacity time, ×1000 and ×100 differ, but mostly because ×1000 holds more gypsum "
            "(d 0.52 against 0.74 at capacity time 2): the pre-set bypass test was confounded",
            "Compared at the same gypsum dissolved, they relax together from d 0.5 (within 0.028)",
            "So: d for 'how far along', capacity time for 'how much water'. Every event here is timed on d."],
        M + 6.9, 1.6, W - 2 * M - 6.9, 5.0, size=16)

# ===================================================================================================== robustness + where we are
section("Where we are", "What holds up, what could still change it, and what runs now",
        notes="Robustness, limits, the DFN check that is running, and next steps.")

s = new_slide(notes=(
    "What we tried to break. 2 km networks (45 networks, 90 runs): the same dip and recovery, inheritance 0.96–1.00, breakthrough "
    "needs a little more gypsum dissolved (0.56 to 0.64). Rate 0.1 to 10 pore volumes per year (3 networks per chemistry): gypsum-only "
    "depth and PR_V minimum move by at most 0.001 in d, breakthrough and outlet events by up to 0.046 (one network); coupled depth by "
    "at most 0.019, coupled events up to 0.04 and its weakly defined pore-volume minimum by 0.094 on one network. Density P32 ×16: "
    "same order in 27 of 30. σ 0: the "
    "depth law and the chemistry match hold. Binning: the moving focus holds when fractures count in every stretch they span. "
    "What did not survive: an apparent early network peak on sparse 2 km networks vanished at σ 0 on the same geometries."))
title(s, "What we tried to break")
picture(s, IMG / "scale2km_prv.png", M, 1.4, 6.3, 5.3, alt="2 km PR_V")
bullets(s, ["2 km (90 runs): same dip and recovery; inheritance 0.96–1.00; breakthrough 0.56 → 0.64",
            "Rate ×100 (0.1–10 PV/yr): depth ≤ 0.02; event timing mostly ≤ 0.04 in d",
            "Density P32 ×16: same order in 27 of 30",
            "σ 0: depth law and chemistry match hold (9 of 9; 0.029)",
            "Dropped: an early network peak on sparse 2 km networks (gone at σ 0)"],
        M + 6.6, 1.6, W - 2 * M - 6.6, 5.2, size=15)

s = new_slide(notes=(
    "Limits, in the order a reviewer will raise them. One cell per fracture: no fronts or wormholes inside a fracture, no "
    "intersection throats; the literature says that biases channels shallower and later, so depths here are conservative, but "
    "earlier validation showed the simple graph misses channel timing at high gain. That is why the DFN check matters. The "
    "permeability law is unknown for these veins; the depth law turns it into a parameter. Inputs: FFM01 200–400 m geometry with "
    "the 0–200 m transmissivity law and P32 scaled up to percolate over 1 km. Statistics: σ variants share geometry, so there are "
    "15 independent networks per scale. Tracer: Eulerian pulses with numerical dispersion. And the coupled chemistry sits "
    "consistently about 0.02 shallower than gypsum-only, right at the edge of the 0.03 tolerance."))
title(s, "Limits")
for i, (b, head, body) in enumerate([
        ("1", "One cell per fracture", "no fronts inside a fracture, no intersection throats; the DFN check tests this"),
        ("2", "Permeability law", "unknown for these veins; part 3 turns it into a parameter (C)"),
        ("3", "Inputs", "FFM01 geometry with P32 scaled ×4–×16 to percolate over 1 km"),
        ("4", "Statistics", "σ variants share geometry: 15 independent networks per scale"),
        ("5", "Chemistry match", "coupled sits ~0.02 shallower than gypsum-only, at the edge of 0.03")]):
    y = 1.6 + i * 1.02
    badge(s, b, M, y, d=0.55, fill=ACCENT)
    text(s, head, M + 0.85, y + 0.05, 3.6, 0.5, size=18, bold=True, font=HEAD)
    text(s, body, M + 4.6, y + 0.08, W - 2 * M - 4.6, 0.8, size=15, color=INK2)

s = new_slide(notes=(
    "The DFN check, launched this morning (Mon 9 Nov 11:08). Network: 500 × 125 × 125 m trial network, P32 ×6, σ 1, 381 "
    "fractures, meshed DFN of 196,864 cells; BiGraFV graph and DFN built from the same dfnGen output, so the fractures and "
    "apertures are identical. Same deck, both chemistries, to capacity time 2. Pass criteria were fixed on 6 Nov before any DFN "
    "state existed: C1 stage order; C2 event timing within 0.10 of d; C3 depth within 0.10; C4 inheritance ≥ 0.8 and channel-set "
    "overlap ≥ 0.5; C5 front moves inlet to outlet; C6 every 50 m bin relaxes to ≥ 0.9; C7 per-fracture dissolved fraction rank "
    "correlation ≥ 0.6. Verdict: agrees, agrees on mechanism but differs in magnitude, or differs. Gypsum-only is primary; the "
    "coupled graph run itself fails C1 (a known near-tie), so coupled is descriptive. Timing, measured over the first 30 minutes on a "
    "shared, heavily loaded machine: coupled about 1 simulated year per 50 s with 467 years to go, so about 6–7 h (Monday evening); "
    "gypsum-only about 25,500 steps at 6–8 s each on 6 ranks, 40–60 h, so Wednesday, with breakthrough about a third of the way "
    "through (Tuesday). The steady-flow difference is 1.69 (DFN carries 1.69× the graph's flow at the "
    "same pressure drop), reported, not tested."))
title(s, "Running now: the DFN check on a 500 m network")
card(s, M, 1.55, 5.6, 5.3, fill=HL)
text(s, "Set-up", M + 0.3, 1.75, 5.0, 0.5, size=19, bold=True, font=HEAD)
bullets(s, ["500 × 125 × 125 m, P32 ×6, σ 1, 381 fractures",
            "meshed DFN 196,864 cells; graph from the same dfnGen output",
            "both chemistries, to capacity time 2; gypsum-only primary",
            "launched Mon 9 Nov 11:08",
            "coupled: ~6–7 h (Monday evening)",
            "gypsum-only: ~25,500 steps × 6–8 s → 40–60 h (Wednesday)"], M + 0.3, 2.4, 5.0, 4.3, size=15)
card(s, M + 5.9, 1.55, W - 2 * M - 5.9, 5.3, fill="E3F1E8")
text(s, "Pass criteria (fixed 6 Nov, before any DFN state)", M + 6.2, 1.75, W - 2 * M - 6.5, 0.5, size=19, bold=True, font=HEAD)
bullets(s, ["C1 stage order kept", "C2 event timing within 0.10 of d", "C3 depth within 0.10",
            "C4 inheritance ≥ 0.8, channel-set overlap ≥ 0.5", "C5 front moves inlet → outlet",
            "C6 every bin relaxes to ≥ 0.9", "C7 per-fracture dissolved fraction ρ ≥ 0.6",
            "Verdict: agrees / agrees on mechanism, differs in magnitude / differs"],
        M + 6.2, 2.4, W - 2 * M - 6.5, 4.3, size=15, space=5)

s = new_slide(notes=(
    "Next. Read the DFN verdict when it lands (coupled this evening, gypsum-only Wednesday). A final literature check "
    "of the 'not found reported' claims, especially relaxation behind the front. Then draft paper 1: transient reactive channels "
    "in finite-fill fracture networks (stages, moving focus and relaxation, transport). Paper 2: channel depth set by the "
    "attainable permeability gain. Paper 3 later: BiGraFV at kilometre scale as a method, with the DFN comparison. Open "
    "questions that the papers do not need: why some networks relax much more slowly at ×1000, and why early arrival says less "
    "at 2 km."))
title(s, "Next")
three_cards(s, [
    ("This week", ["read the DFN verdict (coupled this evening, gypsum-only ~Wed)",
                   "final literature check of the 'not found reported' claims",
                   "start drafting paper 1"], "E3F1E8"),
    ("Papers", ["1 · transient channels in finite-fill networks: stages, travelling focus, transport",
                "2 · channel depth set by the attainable gain C",
                "3 · BiGraFV at kilometre scale, with the DFN comparison"], HL),
    ("Open, not needed for the papers", ["why some networks relax much more slowly at ×1000",
                                         "why early arrival says less at 2 km",
                                         "a better pre-run predictor (needs a new blind set)"], WARM)])

s = new_slide(dark=True, notes=(
    "Take-home. One order of stages. The focus travels with the front and relaxes behind it, because the soluble fill runs out; "
    "that relaxation is what we did not find published. How deep the channel gets is set by the attainable permeability gain C, "
    "one curve for both chemistries; the shape of the law barely matters. The early-arrival predictor ranks, it does not "
    "predict. The DFN check is running."))
text(s, "Take-home", M, 0.7, W - 2 * M, 0.9, size=36, bold=True, font=HEAD, color=WHITE)
takes = [("4 stages", "one order in 87 of 90 runs: decouple, recouple, focus and break through, relax"),
         ("travels", "the focus moves with the front and relaxes behind it, because the soluble fill runs out"),
         ("C", "how deep the channel gets: one curve for both chemistries (within ~0.02); the law's shape barely matters")]
for i, (b, l) in enumerate(takes):
    x = M + i * 4.1
    text(s, b, x, 2.3, 3.8, 1.0, size=40, bold=True, font=HEAD, color=OPEN if i != 2 else CALCITE)
    text(s, l, x, 3.45, 3.6, 1.8, size=18, color="C9D4DC")
text(s, "Changed my mind: early arrival ranks breakthrough, it does not predict it.  Running: DFN check, verdict ~Wednesday.",
     M, 5.7, W - 2 * M, 0.6, size=16, color="8FA3B3", italic=True)

# ===================================================================================================== backup
s = new_slide(notes="Definitions, for reference.")
title(s, "Backup: definitions")
rows = [("PVI", "Q t / V_pore,0, pore volumes injected (one per year here)"),
        ("γ", "Hyman's acid capacity c0/(ν c_sol): 1.24 × 10⁻³ gypsum-only, 0.039 coupled"),
        ("τ (Hyman)", "ΔV/V0, dissolved volume over initial pore volume; τ_max = 9 here"),
        ("d", "fraction of the network's fracture gypsum dissolved = τ/τ_max (gypsum-only)"),
        ("t_cap", "γ · PVI / τ_max; 1 = enough water to remove the inventory if it all left saturated"),
        ("PR_V", "(Σ Q)² / Σ(Q²/w), w = fracture volume share; 1 when flow ∝ volume"),
        ("PR_pore", "the same with w = open pore volume share"),
        ("depth", "min PR_V / PR_V at the start"),
        ("breakthrough", "first state with flow-weighted d of fractures in the last 100 m ≥ 0.5"),
        ("C", "k of a fully reacted fracture / k0 = (φ_end/φ0)ⁿ; φ_end = 1 gypsum-only, 0.555 coupled"),
        ("t10/τ_res", "time for 10 % of a tracer pulse to leave the unreacted network / mean residence time")]
for i, (k, v) in enumerate(rows):
    y = 1.45 + i * 0.5
    text(s, k, M, y, 2.0, 0.45, size=15, bold=True, color=ACCENT)
    text(s, v, M + 2.1, y, W - 2 * M - 2.1, 0.45, size=15)

s = new_slide(notes=(
    "Backup: apertures. The physical side of the law. With any ×10 law the hydraulic aperture can grow at most ×2.15 (median 75 to "
    "106–122 µm); with n = 3, 13 % of fractures open fully and the top 5 % reach 0.93 mm."))
title(s, "Backup: apertures before and after")
picture(s, IMG / "kphi_e0_apertures.png", M, 1.4, W - 2 * M, 5.5, alt="Aperture histograms")

out = HERE / "Reactive_Channels_PI.pptx"
prs.save(out)
print("slides", len(prs.slides), out)
