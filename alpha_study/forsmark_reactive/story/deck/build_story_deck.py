#!/usr/bin/env python3
"""
Story deck (7 Nov 2026; gap-filling runs A-C folded in 8 Nov): mirrors the new report "Reactive Channels at Kilometre Scale" (story/report/index.html) 1:1,
separate from the older colloquium deck.  Numbers are those of story/STORY.md (reviewed by Karen, 7 Nov) and its CSVs;
figures and movies from story/report/img/.
  cd forsmark_reactive/story/deck && ../../deck/.venv/bin/python build_story_deck.py  -> Reactive_Channels_Story.pptx
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import *  # noqa: F401,F403,E402
from _helpers import prs, new_slide, text, bullets, title, picture, card, badge, stat, source, section, IMG, CART, HERE, \
    INK, INK2, ACCENT, FLOW, WHITE, OPEN, CALCITE, HL, HEAD, M, W, H  # noqa: E402
from pptx.util import Inches  # noqa: E402

RUST = "C4472D"


def movie(s, mp4, poster, x, y, w, h):
    from PIL import Image
    iw, ih = Image.open(poster).size
    sc = min(w / iw, h / ih)
    pw, ph = iw * sc, ih * sc
    s.shapes.add_movie(str(mp4), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph),
                       poster_frame_image=str(poster), mime_type="video/mp4")


# 1 title ------------------------------------------------------------------------------------------------------------
s = new_slide(dark=True, notes="Title. 447 BiGraFV reactive runs on 117 Forsmark FFM01 networks of 1,587 to 14,658 fractures.")
text(s, "Reactive Channels at Kilometre Scale", M, 2.2, W - 2 * M, 1.2, size=44, bold=True, font=HEAD, color=WHITE)
text(s, "A focus that moves and relaxes, and a depth law, from 447 BiGraFV simulations of mineral-filled "
        "fracture networks", M, 3.5, W - 2 * M - 1, 1.0, size=20, color="C9D4DC", italic=True)
text(s, "BiGraFV · Forsmark FFM01 · draft 8 November 2026", M, 6.4, W - 2 * M, 0.4, size=13, color="8FA3B3")

# 2 four findings ----------------------------------------------------------------------------------------------------
s = new_slide(notes=(
    "The four findings in one slide. 1: the order holds in 87 of 90 runs at 1 km. 2: each 100 m stretch focuses as the front passes "
    "(dissolved fraction 0.03 at the inlet to 0.50 at the outlet, gypsum-only) and returns to within 0.8-1.7 % of its start. 3: depth "
    "0.78 at x5.5 to 0.15 at x1000 attainable gain, 9 networks; coupled within a median 0.021 at the same gain; holds at sigma 0 (run C). "
    "4: early tracer arrival ranks the dissolved fraction at breakthrough (pooled rank correlation 0.76 / 0.83) but explains only half "
    "the variation out of sample (R2 0.51 / 0.62); the pre-set blind test failed, so it is a supporting result."))
title(s, "Four findings")
items = [("1 · Stages", "87 / 90", "runs follow one order: open space decouples from flow, recouples, focuses and breaks through, relaxes"),
         ("2 · Moving focus", "0.03 → 0.50", "dissolved fraction when each 100 m stretch focuses, inlet → outlet; each then returns to its start, at ×100 too"),
         ("3 · Depth law", "0.78 → 0.15", "channel depth from ×5.5 to ×1000 attainable gain; coupled on the same curve; holds at σ 0"),
         ("4 · Early arrival", "ρ 0.76", "ranks the gypsum dissolved at breakthrough; out of sample R² 0.5–0.6, blind test failed")]
for i, (k, big, lab) in enumerate(items):
    x = M + i * 3.07
    card(s, x, 1.7, 2.85, 4.6)
    text(s, k, x + 0.25, 1.9, 2.4, 0.4, size=14, color=INK2)
    text(s, big, x + 0.25, 2.4, 2.5, 0.9, size=34, bold=True, font=HEAD, color=FLOW if i != 2 else RUST)
    text(s, lab, x + 0.25, 3.45, 2.4, 2.7, size=15)

# 3 why BiGraFV -------------------------------------------------------------------------------------------------------
s = new_slide(notes=(
    "Why this needs BiGraFV. Published reactive network studies stop at 10 m (meshed DFN) to 25 m and about 526 fractures (graph, "
    "Hyman et al. 2026). One control volume per fracture lets PFLOTRAN run full reactive transport with mineral volume and "
    "permeability feedback on 1,587-14,658 fractures in hours, so the same network can be run hundreds of ways (447 runs). Every comparison here is "
    "BiGraFV against BiGraFV."))
title(s, "What BiGraFV makes possible")
stat(s, "25 m · 526", "largest published reactive network study found: domain size and fractures (Hyman et al. 2026)", M, 1.9, 3.8, color=INK2)
stat(s, "14,658", "this study: fractures in the largest network; domains 1–2 km long", M + 4.2, 1.9, 3.8)
stat(s, "447", "reactive runs, flow re-solved at every saved state", M + 8.4, 1.9, 3.6, color=RUST)
text(s, [[("How. ", {"bold": True}), ("Each fracture is one control volume and each intersection a connection; PFLOTRAN solves "
          "gypsum and calcite kinetics, mineral volume and the porosity–permeability feedback on that graph.", {})],
         [("Why it matters. ", {"bold": True}), ("We can run the same network with different chemistries, permeability laws, rates, "
          "lengths and densities, and compare BiGraFV with BiGraFV, one change at a time.", {})]], M, 4.2, W - 2 * M, 2.0, size=17)

# 4 setup -------------------------------------------------------------------------------------------------------------
s = new_slide(notes=(
    "Setup. Forsmark FFM01 statistics, 1000 x 250 x 250 m and 2000 x 500 x 250 m, P32 x4-x16, sigma 0/0.5/1, 5 seeds. One pore volume "
    "per year. Fractures start 90 % gypsum. Gypsum-only and coupled gypsum-calcite (calcite takes 49.4 % of the gypsum volume). "
    "k = k0 (phi/phi0)^n. The clock is the fraction of the gypsum dissolved."))
title(s, "What we ran")
picture(s, IMG / "fracture_cell.png", M, 1.5, 6.4, 4.6, alt="One fracture cell and its two chemistries")
bullets(s, ["Forsmark FFM01 networks, 1 km and 2 km; P32 ×4–×16; σ 0/0.5/1; 5 seeds",
            "one network pore volume per year, fixed rate",
            "fractures start 90 % gypsum; gypsum-only or coupled gypsum–calcite",
            "k = k₀(φ/φ₀)ⁿ: n = 1 main runs, 0.5–8 in the law tests",
            "clock: fraction of the gypsum dissolved; depth: PR_V minimum / start"], 7.3, 1.7, 5.4, 4.6, size=16, space=10)

# Part 1 --------------------------------------------------------------------------------------------------------------
section("1 · The front moves through four stages", "Open space decouples from flow, recouples, breaks through, relaxes")
s = new_slide(notes="The four stages as a cartoon: (1) pore space opens near the inlet while flow is set downstream; (2) flow moves "
                    "into the opened fractures; (3) focusing peaks, then the front breaks through; (4) neighbouring paths open, flow spreads.")
title(s, "Four stages, one order")
picture(s, CART / "four_stages.png", M, 1.45, W - 2 * M, 5.5, alt="Cartoon: four stages")
s = new_slide(notes=(
    "Figure 1. Event medians (dissolved fraction): pore-volume minimum 0.17 / 0.20, PR_V minimum 0.37 / 0.44, breakthrough 0.56 / 0.63 "
    "(gypsum-only / coupled, 45 runs each). Full order in 87 of 90 runs at 1 km, 83 of 90 at 2 km. PR_pore/PR_V falls below its start in "
    "every run (median curve 0.68 / 0.80 at d about 0.1), recrosses 1 near d = 0.3 and peaks at 1.52 / 1.28 near d = 0.5. Last state: "
    "PR_V 0.995 / 1.01 of its start."))
title(s, "Decoupling, recoupling, peak, relaxation")
picture(s, IMG / "fig1_stages.png", M, 1.4, W - 2 * M, 3.9, alt="Figure 1")
stat(s, "87 / 90", "runs with the full order at 1 km (83 / 90 at 2 km)", M, 5.35, 3.8, big_size=30, label_size=13)
stat(s, "45 / 45", "runs per chemistry where flow decouples from open space first", M + 4.2, 5.35, 3.8, color=ACCENT, big_size=30, label_size=13)
stat(s, "0.995", "PR_V at the end relative to start (gypsum-only): the network relaxes", M + 8.4, 5.35, 3.6, color=RUST, big_size=30, label_size=13)
s = new_slide(notes="Movie: two slices through the example network (P32 x6, sigma 1, seed 1, gypsum-only) through the four stages.")
title(s, "The stages in a real network")
movie(s, IMG / "movie_gyponly.mp4", IMG / "stages_gyponly.png", M, 1.4, W - 2 * M, 5.6)

# Part 2 --------------------------------------------------------------------------------------------------------------
section("2 · A focus that moves and relaxes", "Each stretch focuses as the front passes, then returns to its start")
s = new_slide(notes="Animation: median of 45 networks per chemistry. Bars: PR_V of each 100 m stretch over its start. Watch the short bar "
                    "travel from inlet to outlet while the stretches behind it grow back to 1.")
title(s, "Watch the focus travel")
movie(s, IMG / "focus_front.mp4", IMG / "focus_front_mid.png", M, 1.35, W - 2 * M, 5.7)
s = new_slide(notes=(
    "Figure 2. The dissolved fraction at each stretch's minimum rises from 0.03 at the inlet to 0.50 (gypsum-only) and 0.58 (coupled). "
    "Outlet stretch minimum 0.36 / 0.52 against 0.54-0.66 and 0.67-0.76 upstream. Every stretch ends within 0.8 % / 1.7 % of its start; "
    "with fractures counted in every stretch they span, within 2.3 % / 1.3 %. At high gain the front still moves; run A follows those "
    "runs to capacity time 8 (next slide)."))
title(s, "Focus moves inlet → outlet, then relaxes")
picture(s, IMG / "fig2_front.png", M, 1.4, W - 2 * M, 3.9, alt="Figure 2")
stat(s, "0.03 → 0.50", "dissolved fraction at each stretch's minimum, inlet → outlet", M, 5.35, 3.8, big_size=30, label_size=13)
stat(s, "0.36", "outlet stretch at its minimum: the strongest local focusing", M + 4.2, 5.35, 3.8, color=ACCENT, big_size=30, label_size=13)
stat(s, "< 2 %", "every stretch ends this close to its start", M + 8.4, 5.35, 3.6, color=RUST, big_size=30, label_size=13)
s = new_slide(notes=(
    "Figure 5, run A: n = 2 and 3 on the 9 sweep networks continued to capacity time 8. n = 2 (x100): every stretch 97-99 % recovered, "
    "network PR_V 0.99 of its start, 9 of 9 networks; the pre-set rule is met. n = 3 (x1000): not met by capacity time 8, stretches 74-89 % "
    "recovered, network 0.84 and still rising (0.56 at capacity time 2, 0.85 at 8) with a quarter of the gypsum left. At the same dissolved "
    "fraction n = 2 and n = 3 sit within 0.03 (0.54 / 0.53 at d 0.5, 0.80 / 0.78 at d 0.7): recovery is paced by the gypsum left, not by the "
    "gain. Why x1000 is slower in time is untested (hypothesis: its channel bypasses the gypsum left). Coupled runs relax fully at both n."))
title(s, "At high gain the relaxation is paced by the gypsum left")
picture(s, IMG / "fig5_latetime.png", M, 1.4, W - 2 * M, 3.9, alt="Figure 5")
stat(s, "0.99", "network PR_V / start at ×100 gain, capacity time 8 (9 of 9 networks)", M, 5.35, 3.8, big_size=30, label_size=13)
stat(s, "0.84 ↑", "at ×1000: not yet complete, still rising, a quarter of the gypsum left", M + 4.2, 5.35, 3.8, color=ACCENT, big_size=30, label_size=13)
stat(s, "≤ 0.03", "gap between ×100 and ×1000 at the same dissolved fraction", M + 8.4, 5.35, 3.6, color=RUST, big_size=30, label_size=13)
s = new_slide(notes=(
    "What is new here. Hyman et al. (2026, Fig. 11) show a focusing front moving downstream in 3D DFN graphs, but there focusing behind "
    "the front holds at its maximum because the wall rock never runs out. Here the soluble fill runs out, so each stretch relaxes behind "
    "the front. The width of the focused zone does not predict when the whole network is most focused (pre-set test failed)."))
title(s, "What is new: relaxation behind the front")
card(s, M, 1.7, 5.8, 3.6)
text(s, "Unlimited wall rock (Hyman et al. 2026)", M + 0.3, 1.95, 5.2, 0.5, size=19, bold=True, font=HEAD, color=INK2)
bullets(s, ["a focusing front moves downstream", "behind it, focusing holds at its maximum", "after breakthrough, channelization stops changing"],
        M + 0.3, 2.6, 5.2, 2.6, size=16, space=10)
card(s, M + 6.3, 1.7, 5.8, 3.6, fill="E3F1E8")
text(s, "Finite soluble fill (this study)", M + 6.6, 1.95, 5.2, 0.5, size=19, bold=True, font=HEAD, color="2F7A4F")
bullets(s, ["the same moving front", "behind it, each stretch returns to its start", "after breakthrough, the network relaxes"],
        M + 6.6, 2.6, 5.2, 2.6, size=16, space=10)
text(s, "Not the explanation: the width of the focused zone does not set when the whole network is most focused (pre-set test, ρ 0.27–0.50).",
     M, 5.6, W - 2 * M, 0.8, size=15, color=INK2)

# Part 3 --------------------------------------------------------------------------------------------------------------
section("3 · Depth follows the attainable gain", "The chemistry acts through how much more permeable a fracture can become")
s = new_slide(notes=(
    "Figure 3. Depth falls with the attainable gain C on 9 of 9 networks: median 0.78 at x5.5, 0.68 at x10, 0.55 at x30, 0.34 at x100, "
    "0.15 at x1000 (gypsum-only); about 0.25 per decade, flattening at high C. Coupled at its own C (x3.3 to x171) sits a median 0.021 from "
    "the gypsum-only curve at the same C (36 points; 6 beyond 0.05, all positive). Matched points compare different n at the same C and "
    "agree. 91-100 % of the high-n channel lies inside the n = 1 channel, which shrinks to 0.71 / 0.47 / 0.16 of its size at n = 1.48 / 2 / 3. "
    "Panel D, run C: the same 9 geometries without transmissivity spread (sigma 0). Depth falls with C on 9 of 9; coupled within a median "
    "0.029 (27 points, median +0.027, passes the pre-set 0.03 narrowly; sigma 1 on the same laws 0.022); median depth 0.65 / 0.43 / 0.25 / 0.16 at x10 / x30 / x100 / x1000."))
title(s, "One depth law for both chemistries, at σ 1 and σ 0")
picture(s, IMG / "fig3_gain.png", M, 1.35, 7.8, 5.6, alt="Figure 3")
stat(s, "0.78 → 0.15", "median depth, ×5.5 → ×1000; falls on 9 of 9 networks at σ 1 and at σ 0", 8.5, 1.5, 4.2, big_size=30, label_size=13)
stat(s, "0.021", "median gap, coupled vs gypsum-only at the same gain (σ 1, 36 points; σ 0: 0.029)", 8.5, 3.25, 4.2, color=ACCENT, big_size=30, label_size=13)
stat(s, "91–100 %", "of the high-gain channel inside the n = 1 channel", 8.5, 5.0, 4.2, color=RUST, big_size=30, label_size=13)
s = new_slide(notes=(
    "Separating the gain from the shape. At a fixed x10 gain, four law shapes (n = 0.5, 1, 2, 8) give depth 0.72, 0.68, 0.66, 0.64 on one "
    "network; going to x1000 gives 0.21 on that network. Hydraulic aperture can at most double under any x10 law (median 75 to 106-122 um); "
    "with n = 3, 13 % of fractures open to about 1 mm. The gain also moves events earlier: breakthrough 0.65 to 0.27 from x5.5 to x1000."))
title(s, "The gain matters, the shape barely")
picture(s, IMG / "kphi_e0_curves.png", M, 1.45, 7.6, 2.6, alt="E0 curves")
picture(s, IMG / "kphi_e0_apertures.png", M, 4.15, 7.6, 2.7, alt="E0 apertures")
stat(s, "±0.04", "depth spread from four law shapes at the same ×10 gain (one network)", 8.6, 1.6, 4.1, big_size=34)
stat(s, "0.47", "depth change from ×10 to ×1000 on the same network", 8.6, 3.2, 4.1, color=RUST, big_size=34)
text(s, "A higher gain also makes everything earlier: breakthrough at 0.65 → 0.27 of the gypsum dissolved (×5.5 → ×1000).", 8.6, 4.85, 4.1, 1.3, size=15, color=INK2)

# Part 4 --------------------------------------------------------------------------------------------------------------
section("4 · Early arrival ranks breakthrough, roughly", "Early tracer arrival through the unreacted network: a supporting result")
s = new_slide(notes=(
    "Figure 4. d_bt = 0.03 + 1.45 t10/tau (gypsum-only), 0.11 + 1.49 t10/tau (coupled). Held-out R2 0.77 / 0.75 with each P32 level left out, "
    "against 0.62 / 0.55 for the largest fracture's flow share (training). On 45 new 2 km networks it ranks weakly (rho 0.60 / 0.43). "
    "Run B, blind, 12 new 1 km networks against the frozen line: R2 -0.17 / 0.45, rho 0.51 / 0.72, bias -0.043 / -0.034, so the pre-set test "
    "failed for both chemistries. Not the sigma mix (sigma-1 in-sample R2 0.80 / 0.76); likely an optimistic training fit. All 27 sigma-1 1 km networks with one left out: R2 0.51 / 0.62, rho 0.76 / 0.83."))
title(s, "Early arrival ranks breakthrough; the blind test failed")
picture(s, IMG / "fig4_predictor.png", M, 1.4, W - 2 * M, 3.9, alt="Figure 4")
stat(s, "ρ 0.76", "rank correlation, all 27 σ 1 1 km networks (coupled 0.83)", M, 5.35, 3.8, big_size=30, label_size=13)
stat(s, "R² 0.51", "one network left out at a time (coupled 0.62); training said 0.77", M + 4.2, 5.35, 3.8, color=ACCENT, big_size=30, label_size=13)
stat(s, "R² −0.17", "blind, 12 new networks, gypsum-only (coupled 0.45); pass was 0.5", M + 8.4, 5.35, 3.6, color=RUST, big_size=30, label_size=13)

# Robustness ----------------------------------------------------------------------------------------------------------
s = new_slide(notes=(
    "Robustness. 2 km (90 runs): same dip and recovery, inheritance 0.96-1.00, breakthrough needs more gypsum dissolved (0.56 to 0.64). "
    "Rate 0.1-10 pore volumes per year: stage timing moves at most 0.003, depth at most 0.014. P32 x16: same order in 26 of 30. Binning: the "
    "moving focus holds with spanning bins. Sigma 0: the depth law holds (run C). Dropped: an apparent early peak on sparse 2 km networks vanished at sigma 0."))
title(s, "What holds, and what we dropped")
picture(s, IMG / "scale2km_prv.png", M, 1.45, 7.2, 4.9, alt="1 km vs 2 km")
bullets(s, ["2 km: same stages, inheritance 0.96–1.00",
            "rate ×100 range: timing ≤ 0.003, depth ≤ 0.014",
            "P32 ×16: same order in 26 of 30",
            "spanning bins: focus still moves and relaxes",
            "σ 0: depth law and chemistry match hold (run C)",
            "dropped: the sparse 2 km early peak (gone at σ 0)"], 8.1, 1.7, 4.6, 4.8, size=16, space=12)

# New or known --------------------------------------------------------------------------------------------------------
s = new_slide(notes="What is known and what we did not find reported. A final literature check before submission is still to do.")
title(s, "New or known")
card(s, M, 1.7, 5.8, 4.7)
text(s, "Known, now at 1–2 km", M + 0.3, 1.95, 5.2, 0.5, size=21, bold=True, font=HEAD, color=INK2)
bullets(s, ["channels follow the initial flow paths (Hyman et al. 2026)", "a focusing front moves downstream (Hyman et al. 2026, Fig. 11)",
            "calcite replacement limits the gain (Budek et al. 2026)"], M + 0.3, 2.65, 5.2, 3.5, size=16, space=12)
card(s, M + 6.3, 1.7, 5.8, 4.7, fill="E3F1E8")
text(s, "Not found reported", M + 6.6, 1.95, 5.2, 0.5, size=21, bold=True, font=HEAD, color="2F7A4F")
bullets(s, ["focus relaxes behind the front (finite fill)", "four-stage sequence with flow–open-space decoupling in 3D networks",
            "one depth law for both chemistries; narrowing inside the initial channel", "early tracer arrival ranks breakthrough inventory (moderately)",
            "reactive network runs at km scale with thousands of fractures"], M + 6.6, 2.65, 5.2, 3.6, size=16, space=10)

# Limits --------------------------------------------------------------------------------------------------------------
s = new_slide(notes="Limits: one cell per fracture (no in-fracture fronts, wormholes or throats; biases channels shallower); permeability "
                    "law unknown (part 3 makes it a parameter); FFM01 inputs with the shallow transmissivity law; sigma variants share geometry.")
title(s, "Limits")
lims = [("Model", "One cell per fracture: no in-fracture fronts, wormholes or throats; channels are, if anything, too shallow."),
        ("Law", "The permeability law is unknown; part 3 turns it into the parameter C."),
        ("Inputs", "FFM01 200–400 m geometry with the 0–200 m transmissivity law; P32 scaled to percolate across 1 km."),
        ("Statistics", "σ variants share geometry: 15 independent networks per scale."),
        ("Tracer", "Eulerian pulses with numerical dispersion: compare states, not with particle tracking.")]
for i, (h, b) in enumerate(lims):
    y = 1.6 + i * 1.0
    badge(s, str(i + 1), M, y + 0.05, d=0.5, fill=ACCENT, size=16)
    text(s, [[(h + ".  ", {"bold": True}), (b, {})]], M + 0.75, y + 0.08, W - 2 * M - 0.8, 0.9, size=17)

# Manuscripts and gaps ------------------------------------------------------------------------------------------------
s = new_slide(notes="Manuscripts. Paper 1: the dynamics, four figures plus late-time relaxation; early arrival as a supporting result. Paper 2 (optional): the depth law, now extended by runs A and C. Paper 3 "
                    "(later): BiGraFV at kilometre scale, the method and its checks.")
title(s, "Toward manuscripts")
papers = [("Paper 1", "Transient reactive channels in finite-fill fracture networks", "stages · moving focus and relaxation · depth law · late-time relaxation"),
          ("Paper 2", "Channel depth is set by the attainable permeability gain", "optional, now supported: σ 0 and late-time runs extend Figure 3"),
          ("Paper 3", "BiGraFV at kilometre scale", "later: the method, its checks and the parked DFN comparison")]
for i, (k, t, b) in enumerate(papers):
    x = M + i * 4.1
    card(s, x, 1.7, 3.8, 4.4, fill=HL if i else "E3F1E8")
    text(s, k, x + 0.3, 1.95, 3.2, 0.4, size=15, color=INK2)
    text(s, t, x + 0.3, 2.4, 3.2, 1.6, size=20, bold=True, font=HEAD)
    text(s, b, x + 0.3, 4.1, 3.2, 1.8, size=15, color=INK2)
s = new_slide(notes="Gap-filling runs, 7 Nov 11:18-22:39, 114 runs, rules fixed before the runs (gapfill/GAPFILL.md). A: n = 2 met, n = 3 not "
                    "met by capacity time 8 (still recovering). B: failed for both chemistries. C: passed (chemistry match narrowly, 0.029).")
title(s, "Gap-filling runs: what passed and what did not")
gaps = [("A", "Does relaxation complete at high gain?", "n = 2, 3 · 9 networks · to capacity time 8 · 36 runs",
         "×100: complete (0.99). ×1000: not yet, 0.84 and rising", "2F7A4F"),
        ("B", "Does the predictor hold on unseen networks?", "12 new 1 km networks · start-of-run tracer · 24 runs",
         "failed: R² −0.17 / 0.45, ρ 0.51 / 0.72 (pass 0.5 / 0.7)", RUST),
        ("C", "Is the depth law specific to σ 1?", "n = 1.48, 2, 3 · 9 σ-0 networks · 54 runs",
         "passed: falls on 9 of 9; chemistry gap 0.029", "2F7A4F")]
for i, (k, q, what, res, col) in enumerate(gaps):
    y = 1.7 + i * 1.6
    badge(s, k, M, y + 0.1, d=0.65, fill=col)
    text(s, q, M + 0.95, y, 5.6, 0.5, size=19, bold=True, font=HEAD)
    text(s, what, M + 0.95, y + 0.55, 5.6, 0.8, size=15, color=INK2)
    text(s, res, M + 6.9, y + 0.15, 5.2, 1.0, size=16, bold=True, color=col)

# Take-home -----------------------------------------------------------------------------------------------------------
s = new_slide(dark=True, notes="Take-home: one order of stages; the focus travels and relaxes because the fill runs out, at a pace set by the gypsum left; "
                               "depth is set by the attainable gain. Early tracer arrival only ranks breakthrough roughly (blind test failed).")
text(s, "Take-home", M, 0.7, W - 2 * M, 0.9, size=36, bold=True, font=HEAD, color=WHITE)
takes = [("4 stages", "one order in 87 of 90 runs: decouple, recouple, focus and break through, relax"),
         ("travels", "the focus moves with the front and relaxes behind it, because the soluble fill runs out"),
         ("0.78 → 0.15", "channel depth set by the attainable permeability gain, one curve for both chemistries and both σ")]
for i, (b, l) in enumerate(takes):
    x = M + i * 4.1
    text(s, b, x, 2.3, 3.8, 1.0, size=40, bold=True, font=HEAD, color=OPEN if i != 2 else CALCITE)
    text(s, l, x, 3.45, 3.6, 1.8, size=18, color="C9D4DC")
text(s, "Report: Reactive Channels at Kilometre Scale (claude.ai artifact) · code and data: github.com/cr-sutton/BiGraFV_reactive_channelization",
     M, 6.5, W - 2 * M, 0.4, size=13, color="8FA3B3")

prs.save(HERE / "Reactive_Channels_Story.pptx")
print("slides", len(prs.slides), HERE / "Reactive_Channels_Story.pptx")
