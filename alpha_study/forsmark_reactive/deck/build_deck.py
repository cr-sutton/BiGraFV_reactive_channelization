#!/usr/bin/env python3
"""
Colloquium deck that mirrors the Forsmark Reactive Channels report (report_phase1/index.html) with a narrative arc.
Kept 1:1 with the report: every number comes from deck/numbers.json (deck_numbers.py, same CSVs as the report), every
figure from report_phase1/img/ and the report's own cartoons (render_cartoons.py).  Rebuild after any report update:

  cd forsmark_reactive/deck
  python3 deck_numbers.py && .venv/bin/python render_cartoons.py && .venv/bin/python build_deck.py
  -> Forsmark_Reactive_Channels.pptx
"""
from __future__ import annotations

import datetime
import math
import json
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
IMG = HERE.parent / "report_phase1" / "img"
CART = HERE / "cartoons"
N = json.loads((HERE / "numbers.json").read_text())

# palette = the report's light-mode tokens
INK, INK2, RULE = "16181A", "4C5157", "DCDCD6"
DARK, ACCENT, FLOW = "14212B", "1F5F8B", "D2572A"
MINERAL, OPEN, CALCITE, HL = "8A8F96", "9FD3F0", "E9B949", "EAF2F8"
WHITE = "FFFFFF"
HEAD, BODY = "Cambria", "Calibri"
W, H = 13.333, 7.5
M = 0.6                                          # side margin (in)

pct = lambda x: f"{100 * x:.0f} %"
prange = lambda a, b: f"{100 * a:.0f}–{100 * b:.0f} %"
f2 = lambda x: f"{x:.2f}"


def rgb(h):
    return RGBColor.from_string(h)


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]
SLIDE_NO = [0]


def new_slide(dark=False, notes=""):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(DARK if dark else WHITE)
    SLIDE_NO[0] += 1
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    if not dark:   # slide number, bottom right
        text(s, f"{SLIDE_NO[0]}", W - M - 0.6, H - 0.45, 0.6, 0.3, size=10, color=INK2, align=PP_ALIGN.RIGHT)
    return s


def text(s, runs, x, y, w, h, size=16, color=INK, bold=False, font=BODY, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         italic=False, name=None):
    """runs: str, or list of paragraphs; a paragraph is str or list of (text, {opts})."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras = [runs] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for t, o in ([(para, {})] if isinstance(para, str) else para):
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = o.get("font", font)
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", italic)
            f.color.rgb = rgb(o.get("color", color))
            if o.get("sub"):
                r._r.get_or_add_rPr().set("baseline", "-25000")
    return tb


def bullets(s, items, x, y, w, h, size=16, color=INK, space=8):
    """items: str or list of (text, {opts}) runs; real bullets via a:buChar."""
    tb = text(s, items, x, y, w, h, size=size, color=color)
    for p in tb.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Emu(Inches(0.25))))
        pPr.set("indent", str(-Emu(Inches(0.25))))
        bu = pPr.makeelement(qn("a:buChar"), {"char": "•"})
        pPr.append(bu)
        p.space_after = Pt(space)
    return tb


def title(s, t, sub=None, dark=False):
    text(s, t, M, 0.45, W - 2 * M, 0.9, size=34, bold=True, font=HEAD, color=WHITE if dark else INK, name="Title")
    if sub:
        text(s, sub, M, 1.28, W - 2 * M, 0.5, size=17, color="C9D4DC" if dark else INK2, italic=True)


def picture(s, path, x, y, w, h, alt="", align="center"):
    """Fit an image inside the box, keeping its aspect ratio."""
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    px = x + (w - pw) / 2 if align == "center" else x
    py = y + (h - ph) / 2
    pic = s.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(pw), Inches(ph))
    pic._element.nvPicPr.cNvPr.set("descr", alt)
    return pic


def card(s, x, y, w, h, fill=HL):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.06
    sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def badge(s, label, x, y, d=0.55, fill=FLOW, color=WHITE, size=18):
    sh = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    sh.line.fill.background()
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    r.font.size = Pt(size); r.font.bold = True; r.font.name = BODY; r.font.color.rgb = rgb(color)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return sh


def stat(s, big, label, x, y, w, color=FLOW, big_size=44, label_size=14, dark=False):
    text(s, big, x, y, w, 0.8, size=big_size, bold=True, font=HEAD, color=color)
    text(s, label, x, y + 0.85, w, 0.9, size=label_size, color="C9D4DC" if dark else INK2)


def source(s, t):
    text(s, t, M, H - 0.45, W - 2 * M - 0.8, 0.3, size=10, color=INK2, italic=True)


def section(t, sub, notes=""):
    s = new_slide(dark=True, notes=notes)
    text(s, t, M, 2.7, W - 2 * M, 1.0, size=40, bold=True, font=HEAD, color=WHITE)
    text(s, sub, M, 3.75, W - 2 * M, 0.8, size=18, color="C9D4DC", italic=True)
    return s


fr = N["fractures_by_p32"]
st = N["stages"]
tr = N["transport"]
inh = N["inheritance"]
dp = N["depth_paired"]
bt = N["breakthrough_dissolved_by_mode"]
gap = N["stage_gaps"]
dq = N["dq_baseline"]

# 1 ----------------------------------------------------------------------------------------------------------------
s = new_slide(dark=True, notes=(
    "Opening. The question of the talk: when water dissolves minerals in a fractured rock mass, do the channels that "
    "form invent new paths or follow ones the network already had? We answer it for kilometre-scale networks built from "
    "the Forsmark site statistics, with gypsum dissolution alone and coupled to calcite precipitation."))
text(s, "Dissolution channels follow paths the network already has", M, 1.2, 6.6, 2.4, size=40, bold=True, font=HEAD, color=WHITE)
text(s, "Reactive flow in kilometre-scale Forsmark fracture networks", M, 3.75, 6.4, 0.8, size=20, color="C9D4DC", italic=True)
text(s, f"{N['n_phase1_runs']} Phase 1 runs on {N['n_phase1_networks']} networks · early Phase 2 · BiGraFV + PFLOTRAN",
     M, 4.65, 6.4, 0.5, size=15, color="C9D4DC")
text(s, f"Status {datetime.date.today():%d %B %Y}", M, 6.6, 6.4, 0.4, size=12, color="8FA3B3")
picture(s, HERE / "network_p6_flow.png", 7.3, 1.4, 5.5, 3.6, alt="Forsmark-statistics fracture network, coloured by share of flow")
text(s, "share of injected flow per fracture, P32 ×6, σ = 1", 7.3, 5.15, 5.5, 0.4, size=12, color="8FA3B3", align=PP_ALIGN.CENTER)

# 2 ----------------------------------------------------------------------------------------------------------------
s = new_slide(notes=(
    "Why this matters: in fractured crystalline rock a handful of fractures carry most of the flow. If reaction "
    "re-routes that flow, transport and storage security change. Three questions frame the talk."))
title(s, "Three questions about reacting fracture networks")
qs = [("1", "Emergent or inherited?", "Do dissolution channels open new paths, or deepen the ones that already carry the flow?"),
      ("2", "Does precipitation re-route?", "Calcite forms where gypsum dissolves. Can it block a path and push the flow elsewhere?"),
      ("3", "What sets channel depth?", "How strongly does flow focus, and does that depend on the chemistry or on something simpler?")]
for i, (n, h, b) in enumerate(qs):
    x = M + i * 4.1
    card(s, x, 2.0, 3.8, 3.9)
    badge(s, n, x + 0.3, 2.3)
    text(s, h, x + 0.3, 3.05, 3.2, 0.9, size=21, bold=True, font=HEAD)
    text(s, b, x + 0.3, 3.95, 3.2, 1.8, size=16, color=INK2)

# 3 ----------------------------------------------------------------------------------------------------------------
s = new_slide(notes=(
    "What is known. Single fractures: wormholes emerge from instability and forget the initial aperture field "
    "(Szymczak & Ladd; Upadhyay et al. 2015). Networks: dissolution follows the topological backbone (Hyman et al. "
    "2024, 2026). Coupled precipitation: calcite replacing gypsum limits the permeability gain (Szawełło et al. 2026; "
    "Budek et al. 2026). The gap: kilometre scale, mineral-filled fractures, site statistics."))
title(s, "What we know, and where the gap is")
cols = [("Single fractures", "Wormholes emerge from an instability; the initial aperture field is largely forgotten.",
         "Szymczak & Ladd 2009, 2012; Upadhyay et al. 2015"),
        ("Small networks", "Dissolution follows the flow backbone that topology sets before any reaction.",
         "Hyman et al. 2024, 2026"),
        ("Coupled precipitation", "Calcite replacing gypsum limits how much permeability a fracture can gain.",
         "Szawełło et al. 2026; Budek et al. 2026")]
for i, (h, b, c) in enumerate(cols):
    x = M + i * 4.1
    card(s, x, 1.8, 3.8, 3.3)
    text(s, h, x + 0.3, 2.05, 3.2, 0.5, size=21, bold=True, font=HEAD, color=ACCENT)
    text(s, b, x + 0.3, 2.7, 3.2, 1.6, size=16)
    text(s, c, x + 0.3, 4.35, 3.2, 0.6, size=12, color=INK2, italic=True)
card(s, M, 5.45, W - 2 * M, 1.1, fill="FBE9E2")
text(s, [[("Gap. ", {"bold": True, "color": FLOW}),
          ("None of this has been tested on kilometre-scale networks of mineral-filled fractures built from site data, "
           "with precipitation coupled in.", {})]], M + 0.3, 5.68, W - 2 * M - 0.6, 0.8, size=17)

# 4 Approach -------------------------------------------------------------------------------------------------------
section("Approach", "Forsmark networks, one control volume per fracture, two chemistries, one shared clock",
        notes="Section divider: how we set the problem up.")

s = new_slide(notes=(
    "The networks: SKB FFM01 fracture families (NS, NE, NW, EW, HZ), 1000 × 250 × 250 m, layer 2, minimum radius 15 m. "
    "Real FFM01 intensity does not percolate across a kilometre, so we scale P32 by 4, 6, 8 and 16. "
    "Transmissivity heterogeneity sigma 0, 0.5, 1; five seeds each. Water is injected at one network pore volume per year. "
    "The transmissivity law is the 0-200 m SKB law applied at 200-400 m depth; we kept and labelled it."))
title(s, f"{N['n_phase1_networks']} networks built from Forsmark fracture statistics")
picture(s, HERE / "network_p6_flow.png", M, 1.75, 6.6, 4.3, alt="Example network coloured by flow share")
x0 = 7.6
stat(s, f"{fr['4'][0]:,}–{fr['16'][1]:,}", "fractures per network (P32 ×4 to ×16)", x0, 1.8, 5.2)
stat(s, "1 km", "inlet to outlet, 1000 × 250 × 250 m, SKB FFM01 families", x0, 3.25, 5.2, color=ACCENT)
bullets(s, ["P32 ×4, ×6, ×8, ×16 (×16: " + f"{fr['16'][0]:,}–{fr['16'][1]:,}" + " fractures, run to capacity time 2)",
            "transmissivity spread σ = 0, 0.5, 1; 5 seeds each",
            "fixed rate: one network pore volume per year (Hyman)"], x0, 4.75, 5.2, 1.7, size=16)
source(s, "Transmissivity: SKB 0–200 m law used at 200–400 m (kept and labelled).")

# 5 ----------------------------------------------------------------------------------------------------------------
s = new_slide(notes=(
    "BiGraFV: each fracture is one well-mixed control volume, connected through its intersections; PFLOTRAN solves "
    "flow and reactive transport on that graph. It is fast enough for 1 km networks, but by construction it cannot form "
    "a front inside a fracture or resolve an intersection throat. Keep that in mind for the candidate findings."))
title(s, "One well-mixed cell per fracture")
picture(s, CART / "fracture_cell.png", M, 1.6, 7.6, 4.9, alt="Cartoon: a fracture as one control volume")
bullets(s, [[("Fast: ", {"bold": True}), ("a 1 km network in hours on a laptop", {})],
            [("Captures: ", {"bold": True}), ("which fractures carry the flow, and how that changes", {})],
            [("Misses: ", {"bold": True}), ("fronts and wormholes inside a fracture; intersection throats", {})]],
        8.6, 2.2, 4.1, 3.6, size=17, space=14)

# 6 ----------------------------------------------------------------------------------------------------------------
s = new_slide(notes=(
    "Two chemistries with the same gypsum kinetics. Dilute water leaves carrying about 17 mol/m3 of gypsum. In 0.5 M "
    "sodium carbonate brine the calcium precipitates as calcite where it is released, so the water never saturates and "
    "removes about 30 times more gypsum per pore volume. Calcite occupies about half the volume of the gypsum it "
    "replaces (Gamma = 0.49), which caps the permeability gain: x10 for gypsum-only, x5.5 coupled (k-phi with n = 1)."))
title(s, "Two chemistries: same kinetics, 30× the capacity")
picture(s, CART / "chemistry.png", M, 1.55, W - 2 * M, 4.6, alt="Cartoon: gypsum dissolution alone and coupled to calcite precipitation")
text(s, [[("Permeability ceiling (n = 1): ", {"bold": True}), ("×10 gypsum-only, ×5.5 coupled, because calcite takes back about half the volume.", {})]],
     M, 6.35, W - 2 * M, 0.5, size=16)

# 7 ----------------------------------------------------------------------------------------------------------------
g = gap
s = new_slide(notes=(
    "Pore volumes put the two chemistries 30 times apart. We time everything by the fraction of the gypsum dissolved, "
    "a measured quantity. Capacity time (pore volumes times what each pore volume can remove, over the inventory) is the "
    "prediction of that fraction; it holds until breakthrough and drifts after it. On the dissolved fraction the coupled "
    "run still comes a little later than gypsum-only on the same network, but the gap is about two thirds of that on "
    "capacity time. Hyman's tau (open volume gained over the initial) does not line the stages up across chemistries: "
    "here it is the mean permeability gain instead."))
title(s, "One clock for both chemistries: the fraction dissolved")
picture(s, CART / "capacity_clock.png", M, 1.6, 7.7, 3.4, alt="Cartoon: pore volumes against capacity time for the two chemistries")
stat(s, f"+{g['breakthrough']['d']:.3f}", f"coupled minus gypsum-only at breakthrough, same network ({N['n_phase1_networks']} pairs), on the dissolved fraction; +{g['breakthrough']['t_cap']:.2f} on capacity time",
     8.7, 1.7, 4.0, big_size=40)
stat(s, "×3.2", "spread of breakthrough across chemistries and porosities on Hyman's τ, against ×1.3 on the dissolved fraction (12 matched networks per group)",
     8.7, 3.75, 4.0, color=ACCENT, big_size=40)
text(s, "Capacity time stays as the prediction made before a run; τ = ΔV/V₀ is read as the mean permeability gain.",
     M, 5.45, 7.7, 0.8, size=15, color=INK2)

# Results ----------------------------------------------------------------------------------------------------------
section("What happens", "Four stages, one inherited channel", notes="Section divider: the Phase 1 results.")

s = new_slide(notes=(
    f"The sequence every run follows. Stage 1, up to about 10 % dissolved: pore space opens near the inlet while the flow "
    f"is still set by filled fractures downstream. Stage 2: the front runs down the paths that already carried the most "
    f"flow. Stage 3: flow focusing is strongest (PR_V minimum at {pct(st['PRV_min']['gyponly']['median'])} dissolved "
    f"gypsum-only, {pct(st['PRV_min']['gypcal']['median'])} coupled) and the outlet breaks through "
    f"({pct(st['breakthrough']['gyponly']['median'])} and {pct(st['breakthrough']['gypcal']['median'])}). Stage 4: "
    "neighbouring paths open and the flow spreads again. Phase 1 medians, 60 runs per chemistry, P32 x4-x16."))
title(s, "Every run passes through the same four stages")
picture(s, CART / "four_stages.png", M, 1.45, W - 2 * M, 5.5, alt="Cartoon: the four stages of channel formation")

s = new_slide(notes=(
    "The same stages in a real network: two horizontal slices through P32 x6, sigma 1, seed 1, gypsum-only, at "
    "breakthrough. Blue is open and flowing, light blue open but nearly idle, orange flow through still-filled rock, grey "
    "filled and idle. The bar shows that open channels already carry most of the flow."))
title(s, "Stage 3 in a real network: open channels carry the flow")
picture(s, IMG / "anim2" / "stage3_gyponly.png", M, 1.4, 7.4, 5.6, alt="Slices of the example network at breakthrough")
stat(s, pct(st["breakthrough"]["gyponly"]["median"]), "of the gypsum dissolved when the outlet breaks through (gypsum-only, Phase 1 median)",
     8.5, 1.9, 4.2)
stat(s, pct(st["breakthrough"]["gypcal"]["median"]), "for the coupled brine on the same networks", 8.5, 3.6, 4.2, color=ACCENT)
text(s, "Example network: P32 ×6, σ = 1, seed 1. Movies of all stages are in the report.", 8.5, 5.4, 4.2, 0.9, size=14, color=INK2)

s = new_slide(notes=(
    f"Stage 1 decoupling. PR_pore compares flow with where the open space is; it bottoms out first, at "
    f"{pct(st['PRpore_min']['gyponly']['median'])} dissolved gypsum-only and {pct(st['PRpore_min']['gypcal']['median'])} "
    f"coupled, while PR_V, flow against fracture volume, has barely moved. The pore space opens near the inlet but the flow "
    f"is still controlled by filled fractures downstream. The two realign later: PR_V reaches its minimum at "
    f"{pct(st['PRV_min']['gyponly']['median'])} and {pct(st['PRV_min']['gypcal']['median'])}."))
title(s, "Pore space opens before the flow moves")
picture(s, CART / "decoupling.png", M, 1.55, W - 2 * M, 3.6, alt="Cartoon: open pore space near the inlet while flow is set downstream")
stat(s, pct(st["PRpore_min"]["gyponly"]["median"]), "dissolved when flow and open space are most mismatched (PR_pore minimum, gypsum-only)",
     M, 5.3, 3.9, big_size=36)
stat(s, pct(st["PRV_min"]["gyponly"]["median"]), "dissolved when flow is most focused (PR_V minimum, gypsum-only)", M + 4.2, 5.3, 3.9,
     color=ACCENT, big_size=36)
stat(s, f"{N['n_phase1_runs']}", "runs, both chemistries, same order every time", M + 8.4, 5.3, 3.6, color=INK, big_size=36)

s = new_slide(notes=(
    f"Channel depth through time, PR_V: 1 if flow were spread in proportion to fracture volume, lower when it concentrates. "
    f"Every panel dips while the channel forms and recovers after breakthrough. The dip is deeper for gypsum-only: "
    f"the minimum is {f2(N['depth_phase1']['gyponly']['median'])} of the start (median) against "
    f"{f2(N['depth_phase1']['gypcal']['median'])} coupled. Lines are sigma ensembles, medians of 5 seeds with 10-90 % bands."))
title(s, "Channels deepen, then the flow spreads again")
picture(s, IMG / "channel_pr_vol_diss.png", M, 1.4, 8.4, 5.4, alt="Volume-weighted participation ratio against fraction dissolved")
stat(s, f2(N["depth_phase1"]["gyponly"]["median"]), f"PR_V minimum over its start, gypsum-only (median of {N['depth_phase1']['gyponly']['n']})", 9.3, 1.9, 3.4)
stat(s, f2(N["depth_phase1"]["gypcal"]["median"]), "same for the coupled brine: a shallower channel", 9.3, 3.6, 3.4, color=ACCENT)
source(s, "PR_V = (ΣQ)² / Σ(Q²/w), w = fracture volume share. Rows: chemistries; columns: P32 ×4, ×6, ×8, ×16 (×16 ends at capacity time 2).")

s = new_slide(notes=(
    f"Inheritance: of the fractures carrying 90 % of the flow when the channel is strongest, a median "
    f"{pct(inh['gyponly']['median'])} (gypsum-only) and {pct(inh['gypcal']['median'])} (coupled) were already in the "
    f"initial 90 % set; the lowest of {inh['gyponly']['n'] + inh['gypcal']['n']} runs is {pct(min(inh['gyponly']['min'], inh['gypcal']['min']))}. The channel is "
    "chosen by the network before any reaction. This answers question 1, for this model."))
title(s, "The channel is inherited")
stat(s, pct(inh["gyponly"]["median"]), "of the peak channel was already in the initial 90 %-flow set (median, gypsum-only)", M, 1.9, 3.6, big_size=60)
stat(s, pct(min(inh["gyponly"]["min"], inh["gypcal"]["min"])), f"lowest of {inh['gyponly']['n'] + inh['gypcal']['n']} runs", M, 3.95, 3.6, color=ACCENT, big_size=44)
picture(s, IMG / "inheritance_diss.png", 4.6, 1.5, 8.1, 4.9, alt="Inheritance through time")
source(s, "Inheritance: share of the 90 %-flow set at its smallest that was in the initial set (n90 minimum). Phase 1, 60 runs per chemistry, P32 ×4–×16.")

tg, tc = tr["gyponly"], tr["gypcal"]
s = new_slide(notes=(
    f"Transport, from tracer pulses through frozen snapshots of the reacted network (fine probes, all 45 networks per "
    f"chemistry). While the channel forms the median arrival moves towards the mean residence time "
    f"({f2(tg['start']['t50_res'])} to {f2(tg['peak']['t50_res'])} for gypsum-only), the tail steepens (gamma "
    f"{tg['start']['gamma']:.1f} to {tg['peak']['gamma']:.1f}) and dispersivity falls ({tg['start']['alpha_L']:.0f} to "
    f"{tg['peak']['alpha_L']:.0f} m). Gamma and dispersivity recover after breakthrough; arrival only partly."))
title(s, "Transport narrows while the channel forms")
picture(s, IMG / "tracer_btc_annotated_gyponly.png", M, 1.5, 6.7, 4.6, alt="Breakthrough curves at three stages, example network")
rows = [("median arrival / τ_res", "t50_res", "{:.2f}"), ("tail exponent γ", "gamma", "{:.1f}"), ("dispersivity α_L (m)", "alpha_L", "{:.0f}")]
text(s, [[("gypsum-only, medians of 45 networks", {"bold": True})]], 7.7, 1.6, 5.0, 0.4, size=15, color=INK2)
for i, (lab, key, fmt) in enumerate(rows):
    y = 2.15 + i * 1.25
    text(s, lab, 7.7, y, 5.0, 0.4, size=15, color=INK2)
    text(s, [[(fmt.format(tg["start"][key]), {"color": INK2}), ("  →  ", {"color": INK2}),
              (fmt.format(tg["peak"][key]), {"color": FLOW, "bold": True}), ("  →  ", {"color": INK2}),
              (fmt.format(tg["end"][key]), {"color": ACCENT})]], 7.7, y + 0.4, 5.0, 0.6, size=26, font=HEAD)
text(s, f"start  →  channel peak ({pct(tg['peak']['diss'])} dissolved)  →  end ({pct(tg['end']['diss'])})", 7.7, 5.95, 5.0, 0.4, size=13, color=INK2)
source(s, "Coupled runs move the same way: arrival " + f"{f2(tc['start']['t50_res'])} → {f2(tc['peak']['t50_res'])} → {f2(tc['end']['t50_res'])}; "
       f"γ {tc['start']['gamma']:.1f} → {tc['peak']['gamma']:.1f} → {tc['end']['gamma']:.1f}.")

# x16 and paused pulse ------------------------------------------------------------------------------------------------
x = N["x16"]
s = new_slide(notes=(
    f"P32 x16 doubles the fracture count (7,849-8,229). The stages keep their order, inheritance stays at "
    f"{pct(x['inheritance']['gyponly']['median'])} (lowest {pct(min(x['inheritance']['gyponly']['min'], x['inheritance']['gypcal']['min']))}), "
    f"and the coupled run is shallower on the same network by +{x['depth_gap']:.3f} (all 15 pairs). What shifts: the flow/open-space "
    f"mismatch peaks later, at {pct(x['stages']['PRpore_min']['gyponly']['median'])} dissolved gypsum-only and "
    f"{pct(x['stages']['PRpore_min']['gypcal']['median'])} coupled, against {pct(N['stages_x4x8']['PRpore_min']['gyponly']['median'])} and "
    f"{pct(N['stages_x4x8']['PRpore_min']['gypcal']['median'])} at x4-x8."))
title(s, "Twice the fractures, the same story")
rowsx = [("PR_pore minimum", "PRpore_min"), ("PR_V minimum", "PRV_min"), ("breakthrough", "breakthrough")]
text(s, [[("fraction of the gypsum dissolved (gypsum-only)", {"bold": True})]], M, 1.65, 7.0, 0.4, size=15, color=INK2)
text(s, "P32 ×4–×8", M + 3.6, 2.15, 1.6, 0.4, size=14, color=INK2)
text(s, "P32 ×16", M + 5.4, 2.15, 1.6, 0.4, size=14, color=FLOW, bold=True)
for i, (lab, key) in enumerate(rowsx):
    y = 2.65 + i * 0.75
    text(s, lab, M, y, 3.4, 0.5, size=17)
    text(s, pct(N["stages_x4x8"][key]["gyponly"]["median"]), M + 3.6, y - 0.05, 1.6, 0.6, size=24, font=HEAD, color=INK2)
    text(s, pct(x["stages"][key]["gyponly"]["median"]), M + 5.4, y - 0.05, 1.6, 0.6, size=24, font=HEAD, color=FLOW, bold=True)
text(s, "Order unchanged; the mismatch between flow and open space peaks later.", M, 5.05, 7.0, 0.8, size=15, color=INK2)
stat(s, pct(x["inheritance"]["gyponly"]["median"]), "inheritance at ×16 (gypsum-only, median of 15)", 8.4, 1.8, 4.3)
stat(s, f"+{x['depth_gap']:.2f}", "coupled minus gypsum-only depth, same network: all 15 positive", 8.4, 3.55, 4.3, color=ACCENT)
source(s, "Phase 1 at P32 ×16, 15 networks per chemistry, run to capacity time 2. Phase 2 at ×16 (3 networks per case) gives the same depth law.")

pg, pc = N["pulse"]["gyponly"], N["pulse"]["gypcal"]
s = new_slide(notes=(
    "The paused-pulse movie: the reaction freezes at each stage and a conservative tracer pulse runs through the frozen network. "
    f"In stage 1 the residence time grows from {pg[0]['tau']:.2f} to {pg[1]['tau']:.2f} years while t50/tau_res moves only from "
    f"{pg[0]['t50']:.2f} to {pg[1]['t50']:.2f}: pore volume is added before the flow paths change. By stage 3 the shape changes: "
    f"t50/tau_res {pg[3]['t50']:.2f}. Curves are normalised concentration against pore volumes since the pulse, in the frozen network's pore "
    "volume: in years they stretch much more, but that is the added pore volume at the same flow, not dispersion. One network only "
    "(P32 x6, sigma 1, seed 1). The movies are in the report."))
title(s, "Pause the reaction, pulse a tracer")
picture(s, IMG / "anim3" / "pulse_btc_only_gyponly.png", M, 1.6, 7.8, 3.1, alt="Normalised breakthrough curves before reaction and at the four stages, gypsum-only")
text(s, [[("gypsum-only, example network", {"bold": True})]], 8.6, 1.6, 4.1, 0.4, size=15, color=INK2)
for i, (lab, key, fmt) in enumerate([("residence time τ_res (yr)", "tau", "{:.1f}"), ("median arrival (pore volumes)", "t50", "{:.2f}")]):
    y = 2.15 + i * 1.45
    text(s, lab, 8.6, y, 4.1, 0.4, size=15, color=INK2)
    text(s, "  ".join(fmt.format(r[key]) for r in pg), 8.6, y + 0.4, 4.2, 0.7, size=22, font=HEAD, color=FLOW if key == "t50" else ACCENT)
text(s, "start · pause 1 · 2 · 3 · 4", 8.6, 5.0, 4.1, 0.4, size=13, color=INK2)
text(s, f"Across {N['transport_link']['n']:,} probed states the change in tail exponent tracks PR_V: ρ {N['transport_link']['rho_gamma_prv']:.2f}.", 8.6, 5.5, 4.1, 0.9, size=15)

# Candidates -------------------------------------------------------------------------------------------------------
section("Candidate findings", "What might be new, and what could make it wrong", notes="Section divider: candidate findings.")

s = new_slide(notes=(
    f"Channel depth law. Paired on the same network, chemistries with the same permeability ceiling give the same depth: "
    f"x10.6 coupled at porosity 0.05 against x10 gypsum-only differ by a median {dp['x106_vs_x10']['median_abs']:.3f} "
    f"(max {dp['x106_vs_x10']['max_abs']:.3f}, {dp['x106_vs_x10']['n']} pairs). A lower ceiling is shallower (x5.5 minus "
    f"x10: +{dp['x55_minus_x10']['median']:.3f}, all {dp['x55_minus_x10']['n']} pairs positive); a higher one deeper (x20 "
    f"minus x10: {dp['x20_minus_x10']['max']:.2f} to {dp['x20_minus_x10']['min']:.2f}, all {dp['x20_minus_x10']['n']} "
    "negative). Caveat: x5.5 and x20 change chemistry or porosity together with the ceiling; three seeds per case."))
title(s, "Depth is set by the permeability ceiling, not chemistry")
picture(s, IMG / "depth_law.png", M, 1.45, 6.9, 4.6, alt="Channel depth against permeability ceiling")
items = [(f"{dp['x106_vs_x10']['median_abs']:.3f}", f"median |difference|, equal ceilings ×10.6 vs ×10 ({dp['x106_vs_x10']['n']} pairs)", INK),
         (f"+{dp['x55_minus_x10']['median']:.2f}", f"×5.5 minus ×10: shallower in all {dp['x55_minus_x10']['n']} pairs", ACCENT),
         (f"{dp['x20_minus_x10']['max']:.2f} to {dp['x20_minus_x10']['min']:.2f}", f"×20 minus ×10: deeper in all {dp['x20_minus_x10']['n']} pairs", FLOW)]
for i, (b, l, c) in enumerate(items):
    stat(s, b, l, 7.9, 1.55 + i * 1.6, 4.8, color=c, big_size=34)
source(s, f"Depth = PR_V minimum over start, paired on the same network (σ = 1, seeds 1–3). Phase 3: gypsum-only at ×5.5 vs coupled ×5.5: {N['ceiling']['gyp55_minus_cal55']:+.3f} (n {N['ceiling']['n']}).")
cl, rt = N["ceiling"], N["rate"]
s = new_slide(notes=(
    f"Two robustness tests from Phase 3. Ceiling: gypsum-only at porosity 0.182 has the same x5.5 ceiling as the coupled runs at 0.1; on the "
    f"same 9 networks the depths match within a median {abs(cl['gyp55_minus_cal55']):.3f} (gypsum-only slightly deeper in all 9), against "
    f"+{cl['gyp55_minus_gyp10']:.2f} when the same chemistry goes from x10 to x5.5. The depth law now spans x3.3 to x20. Rate: 100-fold range, "
    f"0.1 to 10 pore volumes per year, three networks per chemistry: stage timing on the dissolved fraction changes by at most "
    f"{rt['gyp_max']:.4f} (gypsum-only) and {rt['cal_events_max']:.4f} (coupled), depth by at most {rt['cal_depth_max']:.3f}. Local equilibrium. "
    "One coupled network has its PR_pore minimum at 0.003 at the slow rate: gypsum re-precipitates and fills 72 cells that briefly still carry 0.4 % "
    "of the flow, so PR_pore collapses for one saved state. Not a timing shift."))
title(s, "Same ceiling, same depth; any rate, same stages")
picture(s, IMG / "depth_law.png", M, 1.45, 6.9, 4.4, alt="Depth law from x3.3 to x20")
stat(s, f"{abs(cl['gyp55_minus_cal55']):.3f}", f"depth difference at equal ×5.5 ceiling, two chemistries and porosities (median, {cl['n']} networks)", 7.9, 1.55, 4.8, big_size=36)
stat(s, f"+{cl['gyp55_minus_gyp10']:.2f}", "depth change from ×10 to ×5.5 with the same chemistry", 7.9, 3.1, 4.8, color=ACCENT, big_size=36)
stat(s, f"< {math.ceil(rt['cal_events_max'] * 1000) / 1000:.3f}", "largest shift in the PR_V minimum, outlet and breakthrough between 0.1 and 10 pore volumes per year (3 networks per chemistry)", 7.9, 4.65, 4.8, color=FLOW, big_size=36)

s = new_slide(notes=(
    f"Breakthrough is expensive: when the outlet passes 50 % dissolved, the network has used "
    f"{pct(min(bt['gyponly']['p32_medians']))}-{pct(max(bt['gyponly']['p32_medians']))} of its gypsum (gypsum-only, "
    f"per-P32 medians) and {pct(min(bt['gypcal']['p32_medians']))}-{pct(max(bt['gypcal']['p32_medians']))} coupled; "
    f"single runs {pct(min(bt['gyponly']['run_min'], bt['gypcal']['run_min']))}-{pct(max(bt['gyponly']['run_max'], bt['gypcal']['run_max']))}. "
    "That is a compact front, not a wormhole. But the one-cell model cannot form a wormhole inside a fracture, so this is "
    "model-dependent. The wormhole checks queued tonight bound how much in-fracture wormholes could move breakthrough."))
title(s, "Breakthrough needs more than half the gypsum")
picture(s, IMG / "breakthrough_dissolved.png", M, 1.45, 6.9, 4.4, alt="Gypsum dissolved at breakthrough")
stat(s, prange(min(bt['gyponly']['p32_medians']), max(bt['gyponly']['p32_medians'])), "of the gypsum dissolved at breakthrough, gypsum-only (per-P32 medians)", 7.9, 1.6, 4.8)
stat(s, prange(min(bt['gypcal']['p32_medians']), max(bt['gypcal']['p32_medians'])), "coupled brine", 7.9, 3.2, 4.8, color=ACCENT)
card(s, 7.9, 4.6, 4.8, 1.5, fill="FBE9E2")
text(s, [[("Model-dependent. ", {"bold": True, "color": FLOW}),
          ("One cell per fracture cannot form an in-fracture wormhole; a bound is being computed.", {})]], 8.15, 4.8, 4.3, 1.2, size=15)

s = new_slide(notes=(
    f"Question 2, precipitation rerouting. At 2 mM carbonate (capacity matched to gypsum-only) the channel depth matches "
    f"gypsum-only (median |difference| {dp['co3lo_vs_gyponly']['median_abs']:.3f}, {dp['co3lo_vs_gyponly']['n']} networks) "
    f"and inheritance at the channel peak stays {pct(N['inheritance_2mM']['min'])}-{pct(N['inheritance_2mM']['max'])}: no "
    "rerouting. In a well-mixed cell calcite only forms where gypsum dissolves and takes half its volume, so a dissolving cell "
    f"opens. Gypsum does re-precipitate in the coupled runs ({N['reprecip']['runs_gain']} of {N['reprecip']['n']}) and fills up to "
    f"{N['reprecip']['floor_max']} low-flow cells per run, which carry at most {100 * N['reprecip']['q_floor_max']:.4f} % of the flow. "
    "The olivine-carbonation run tests a chemistry that adds solid volume."))
title(s, "No rerouting at low carbonate, and we can see why")
picture(s, CART / "precipitation_reroute.png", M, 1.45, W - 2 * M, 3.6, alt="Cartoon: precipitation rerouting test")
stat(s, prange(N['inheritance_2mM']['min'], N['inheritance_2mM']['max']), f"inheritance at 2 mM carbonate ({N['inheritance_2mM']['n']} networks)", M, 5.2, 4.0, big_size=36)
text(s, [[("Why: ", {"bold": True}), ("calcite (36.9 cm³/mol) replaces gypsum (74.7 cm³/mol) where it dissolves, so dissolving cells open. "
          "Re-precipitated gypsum fills a few low-flow cells without moving the flow; clogging the channel needs a reaction that adds solid volume.", {})]], M + 4.5, 5.25, 7.6, 1.3, size=16)

# manuscript analyses -----------------------------------------------------------------------------------------------------
MS = HERE.parent / "report_phase1" / "img" / "manuscript"
pr, to = N["predictor"], N["turnover"]
s = new_slide(notes=(
    f"Breakthrough can be predicted from the initial flow field. The single best predictor, held out one P32 level at a time, is the "
    f"initial flow share of the largest-flow fracture: R2 {pr['r2_gyp']:.2f} (gypsum-only) and {pr['r2_cal']:.2f} (coupled), Spearman "
    f"{pr['rho']:.2f}; on the Phase 2 runs (same 12 networks, new ceiling and porosity, so not independent) R2 {pr['oos_r2']:.2f} and Spearman {pr['oos_rho']:.2f}. The more one "
    "fracture dominates at the start, the less gypsum has to dissolve before the outlet breaks through."))
title(s, "One fracture's flow share predicts breakthrough")
picture(s, MS / "breakthrough_top1.png", M, 1.45, 8.2, 3.6, alt="Dissolved at breakthrough against the largest fracture's flow share")
stat(s, f"R² {pr['r2_gyp']:.2f}", "held-out P32 level, gypsum-only (coupled 0.47)", 9.1, 1.6, 3.6, big_size=36)
stat(s, f"ρ {pr['oos_rho']:.2f}", "rank agreement on Phase 2 runs (same networks, new ceiling and porosity; not independent)", 9.1, 3.3, 3.6, color=ACCENT, big_size=36)
text(s, "The channel-volume share, the obvious mass-balance guess, predicts poorly (R² 0.12).", M, 5.4, 8.2, 0.8, size=15, color=INK2)

s = new_slide(notes=(
    f"Turnover: inheritance says the peak channel is built from the initial one, but about {pct(to['leaver_share'])} of the initial "
    f"90 %-flow set drops out (median over {to['n']} runs), mostly small, narrow fractures downstream where the flow converges. Only "
    f"{pct(to['joiner_share'])} of the peak set is new, all of them side branches touching the channel. And the depth of focusing is a "
    f"stable property of each network: the gypsum-only and coupled depths on the same network have Spearman {N['depth_rank_rho']:.2f}, "
    "although none of 19 initial-state features predicts it out of sample. It is set early in the reaction: how far PR_V has fallen by 10 % "
    f"dissolved ranks the final depth (Spearman {N['early']['rho10']:.2f}, held-out R2 {N['early']['r2_10']:.2f}, n {N['early']['n10']}); at 5 % it does not "
    f"(held-out R2 {N['early']['r2_05']:.2f}). That is an early warning from the same measure, not a forecast from the initial state."))
title(s, "The channel narrows; depth belongs to the network")
picture(s, MS / "channel_turnover.png", M, 1.45, 7.3, 4.5, alt="Stayers, joiners, leavers and others compared")
picture(s, MS / "depth_network_property.png", 8.1, 1.45, 4.6, 4.2, alt="Coupled against gypsum-only depth on the same network")
text(s, [[(f"{pct(to['leaver_share'])} ", {"bold": True, "color": FLOW, "size": 22, "font": HEAD}), ("of the initial channel drops out (median); ", {}),
          (f"{pct(to['joiner_share'])} ", {"bold": True, "color": ACCENT, "size": 22, "font": HEAD}), ("of the peak channel is new.", {})]], M, 6.15, 7.3, 0.7, size=15)
text(s, f"Depth rank kept across chemistry: ρ {N['depth_rank_rho']:.2f} (n 60). Set by 10 % dissolved: ρ {N['early']['rho10']:.2f}, held-out R² {N['early']['r2_10']:.2f}", 8.1, 5.65, 4.6, 0.8, size=13, color=INK2)

s = new_slide(notes=(
    "Validation scope. The Phase 1 networks were generated with dfnWorks' feasibility checks off, so they cannot be meshed; a validation "
    "needs a regenerated network. With relaxed checks (rFram) the P32 x4 network keeps 1,605 fractures and 9 inlet-outlet paths "
    "(Phase 1: 1,608 and 11). At h = 1 m that is about 0.78 M DFN cells: the coupled chemistry to capacity time 2 is about 9-17 core-h, "
    "gypsum-only to capacity time 1 about 120-240 core-h. x8 at 1 m and x16 do not fit in 24 GB. Built and smoke-tested on 5 Nov: "
    f"{N['dfn']['cells']:,} cells, steady flow {N['dfn']['q_ratio']:.2f}x the graph at the same pressure drop, 40 steps per chemistry with no cuts. "
    f"Measured {N['dfn']['s_step']['gypcal']:.1f} and {N['dfn']['s_step']['gyponly']:.1f} s per step on 6 ranks on a busy machine, peak "
    f"{N['dfn']['rss']['gyponly']:.1f} GB: coupled to capacity time 2 about {N['dfn']['wall_h']['gypcal_tcap2']:.0f} h, gypsum-only to "
    f"capacity time 1 about {N['dfn']['wall_h']['gyponly_tcap1'] / 24:.1f} days. Gate: on this network the one-cell runs fall inside the "
    "Phase 1 x4 envelope for depth, inheritance and breakthrough, but the PR_V minimum comes very early (8-11 % dissolved) and the coupled "
    "run shows no PR_pore dip, so it is atypical in stage timing. Seeds 2 and 3 were gated too. Scored the same way, Phase 1 networks fall inside "
    "the range of the other four on 7-14 of 16 measures; the rFram seeds score 12, 11 and 10, so all are typical. Seed 2 is the only one with "
    "typical stage timing in both chemistries, but LaGriT crashes meshing one of its fractures at h = 1 m. Seed 3 meshes cleanly (766,560 cells). "
    "Proposal: coupled DFN on seeds 1 and 3 (about 4 h each), gypsum-only on seed 1 (about 2.5 days)."))
title(s, "DFN check built: 4 h coupled, 2.5 days gypsum-only")
rows_dfn = [("1 km, P32 ×4, h = 1 m", f"{N['dfn']['cells'] / 1e6:.2f} M cells (built)", f"measured: coupled {N['dfn']['wall_h']['gypcal_tcap2']:.0f} h · gypsum-only {N['dfn']['wall_h']['gyponly_tcap1'] / 24:.1f} d to t_cap 1", "smoke-tested"),
            ("1 km, P32 ×8, h = 2 m", "1.5 M cells", "coupled 17–38 core-h", "coupled only"),
            ("1 km, ×8 at 1 m; ×16", "2.9 M; 11 M", "16–110 GB memory", "not on this laptop"),
            ("250 m block, ×4", "0.19 M cells", "cannot test 1 km depth or breakthrough", "partial")]
for i, (a1, a2, a3, a4) in enumerate(rows_dfn):
    y = 1.75 + i * 1.0
    card(s, M, y, W - 2 * M, 0.85, fill=HL if i else "FBE9E2")
    text(s, a1, M + 0.25, y + 0.22, 3.6, 0.5, size=17, bold=True)
    text(s, a2, M + 4.0, y + 0.22, 2.2, 0.5, size=16, color=INK2)
    text(s, a3, M + 6.3, y + 0.22, 4.0, 0.5, size=15, color=INK2)
    text(s, a4, M + 10.4, y + 0.22, 1.8, 0.5, size=15, color=FLOW if i == 0 else INK2, bold=i == 0)
text(s, "Gate, three rebuilt networks: all as typical as Phase 1 (12, 11, 10 of 16 inside; Phase 1 itself 7–14). Seed 2 will not mesh; proposal: coupled on seeds 1 and 3, gypsum-only on seed 1.", M, 5.95, W - 2 * M, 0.6, size=15, color=INK2)
source(s, "Row 1 measured on 5 Nov (40-step smoke test, 6 ranks, machine load ~22); other rows are estimates (forsmark_reactive/DFN_VALIDATION_SCOPE.md).")

rg, bd = N["regime"], N["bound"]
s = new_slide(notes=(
    "Would in-fracture wormholes change this? The dissolved budget, stage 1 and inheritance do not depend on the in-fracture "
    f"pattern. On the published single-fracture diagram (Li et al. 2026) uniform dissolution is excluded by about 1e6; the "
    f"compact/wormhole split is an extrapolation (only {100 * rg['6']['validated']:.1f} % of the flow at x6 is inside the tested range). "
    f"The channel fractures hold {pct(N['bound_channel_share'])} of the gypsum dissolved by breakthrough, so if a wormhole crossed a "
    f"fracture after dissolving half of it, breakthrough would need {pct(bd['gyponly']['0.5']['D_lo'])}-{pct(bd['gyponly']['0.5']['D_hi'])} "
    "of the gypsum (gypsum-only) instead of more than half."))
title(s, "Wormholes could move breakthrough, not the channel")
picture(s, IMG / "wormhole_bound_report.png", M, 1.45, 7.6, 3.0, alt="Breakthrough bound against the share of each fracture dissolved")
picture(s, IMG / "wormhole_regime.png", M, 4.55, 7.6, 2.4, alt="Fractures on the Li et al. regime diagram")
stat(s, prange(bd["gyponly"]["0.5"]["D_lo"], bd["gyponly"]["0.5"]["D_hi"]), "dissolved at breakthrough if fronts cross a fracture at half dissolution (gypsum-only; model 56 %)", 8.6, 1.6, 4.1, big_size=36)
stat(s, "×10⁶", "margin by which uniform in-fracture dissolution is excluded", 8.6, 3.35, 4.1, color=ACCENT, big_size=36)
text(s, f"Compact vs wormhole is an extrapolation: {100 * rg['6']['validated']:.1f} % of the flow lies inside the published tested range.", 8.6, 5.1, 4.1, 1.2, size=15, color=INK2)

ov = N["olivine"]
s = new_slide(notes=(
    "Exploratory, one run: olivine carbonation adds solid volume (+80 % with chalcedony, from the PFLOTRAN database), so a well-mixed "
    f"cell can clog. The inlet fractures seal first; around 10 pore volumes k_eff drops to about a fifth and the 90 %-flow set turns "
    f"over to {ov['overlap_min_after10']:.2f}-{ov['overlap_end']:.2f} inherited while n90 grows from {ov['n90_0']} to about {ov['n90_max']}. "
    f"By 300 pore volumes {ov['floor_end']} fractures are at the porosity floor and k_eff is {ov['k_eff_end']:.3f} of the start. "
    "Caveats: one run, no pressure, no CO2 phase, surface area sets the rate, the floor keeps 1 % of k."))
title(s, "A reaction that adds volume does re-route the flow")
picture(s, HERE.parent / "explore_olivine" / "olivine_clogging.png", M, 1.5, W - 2 * M, 3.0, alt="Olivine run: k_eff, porosity, clogged fractures and inheritance")
stat(s, f"{ov['overlap_min_after10']:.2f}–{ov['overlap_end']:.2f}", "inheritance after clogging starts (gypsum runs: never below 0.92)", M, 4.85, 3.9, big_size=36)
stat(s, f"{ov['n90_0']} → {ov['n90_max']}", "fractures in the 90 %-flow set: the flow spreads", M + 4.2, 4.85, 3.9, color=ACCENT, big_size=36)
card(s, M + 8.4, 4.9, 3.7, 1.6, fill="FBE9E2")
text(s, [[("Exploratory. ", {"bold": True, "color": FLOW}), ("One olivine run at 185 °C on one network; not part of the Forsmark result.", {})]], M + 8.65, 5.1, 3.25, 1.3, size=14)

s = new_slide(notes=(
    "What is new and what is not. Channels following the initial structure, and calcite replacement limiting the "
    "permeability gain, are known from smaller systems; we show them at 1 km on site statistics. The candidates that may "
    "be new: the stage-1 decoupling of flow and open space, the depth law, and the compact front."))
title(s, "What is new, and what is not")
card(s, M, 1.7, 5.8, 4.6)
text(s, "Known, now shown at 1 km", M + 0.3, 1.95, 5.2, 0.5, size=21, bold=True, font=HEAD, color=INK2)
bullets(s, ["channels follow the initial structure (Hyman et al. 2026)",
            "replacement by calcite limits the permeability gain (Szawełło et al. 2026; Budek et al. 2026)",
            "transport narrows while a channel forms"], M + 0.3, 2.65, 5.2, 3.4, size=16, space=12)
card(s, M + 6.3, 1.7, 5.8, 4.6, fill="FBE9E2")
text(s, "Candidate findings", M + 6.6, 1.95, 5.2, 0.5, size=21, bold=True, font=HEAD, color=FLOW)
bullets(s, ["flow and open pore space decouple in stage 1, then realign",
            "channel depth set by the permeability ceiling, not the chemistry",
            "a compact front: breakthrough after more than half the inventory (model-dependent)",
            "stages timed by the fraction dissolved, not by open-volume gain"], M + 6.6, 2.65, 5.2, 3.4, size=16, space=12)

# Outlook ----------------------------------------------------------------------------------------------------------
section("Limits and next steps", "What the model cannot see, and what is running", notes="Section divider.")

s = new_slide(notes=(
    "Limits. The one-cell model misses in-fracture fronts, wormholes and intersection throats. The transmissivity law is "
    "the shallow SKB law used deeper. Capacity time assumes saturated outflow, which fails after breakthrough. Phase 2 "
    f"has three seeds per case. And the published active surface area mostly reflects fracture-size spread here: with flow "
    f"exactly proportional to volume it would already be {dq['4']['if_prop_V']:.0f}, {dq['6']['if_prop_V']:.0f} and "
    f"{dq['8']['if_prop_V']:.0f} % at P32 x4, x6, x8, close to the measured {dq['4']['actual']:.0f}, {dq['6']['actual']:.0f}, "
    f"{dq['8']['actual']:.0f} %."))
title(s, "Limits we know about")
lims = [("Model", "One cell per fracture: no in-fracture fronts, wormholes or intersection throats."),
        ("Inputs", "SKB 0–200 m transmissivity law used at 200–400 m; kept and labelled."),
        ("Clock", "Capacity time assumes saturated outflow; it drifts after breakthrough, so we time stages by the fraction dissolved."),
        ("Statistics", "Phase 2: 3 seeds per case (9 networks per group)."),
        ("Measure", f"Published active surface area ≈ its value for size-proportional flow ({dq['6']['if_prop_V']:.0f} vs {dq['6']['actual']:.0f} % at ×6): it mostly tracks fracture-size spread.")]
for i, (h, b) in enumerate(lims):
    y = 1.6 + i * 1.0
    badge(s, str(i + 1), M, y + 0.05, d=0.5, fill=ACCENT, size=16)
    text(s, [[(h + ".  ", {"bold": True}), (b, {})]], M + 0.75, y + 0.08, W - 2 * M - 0.8, 0.9, size=17)

s = new_slide(notes=(
    "Next steps proposed, not yet started: resolve in-fracture fronts on a few channel fractures to pin down how much of a fracture "
    "a real front dissolves (the f of the wormhole bound); understand why the stage-1 mismatch peaks later at x16; extend the "
    "olivine exploration; and draft the paper."))
title(s, "Proposed next steps")
steps = [("Test", "Resolve in-fracture fronts on a few channel fractures (DFN or multi-cell) to pin down f in the wormhole bound"),
         ("Test", "Why the flow/open-space mismatch peaks later at ×16"),
         ("Test", "Olivine: more networks, surface-area range, pressure-dependent CO₂"),
         ("Write", "Draft the paper around inheritance, the depth law and the clock")]
for i, (when, what) in enumerate(steps):
    x = M + i * 3.07
    badge(s, str(i + 1), x, 2.0, d=0.6, fill=FLOW if i < 3 else ACCENT)
    if i < 3:
        line = s.shapes.add_connector(1, Inches(x + 0.65), Inches(2.3), Inches(x + 3.0), Inches(2.3))
        line.line.color.rgb = rgb(RULE); line.line.width = Pt(2)
    text(s, when, x, 2.85, 2.8, 0.5, size=19, bold=True, font=HEAD, color=FLOW if i < 3 else ACCENT)
    text(s, what, x, 3.4, 2.8, 2.4, size=16)

s = new_slide(dark=True, notes="Closing: three take-home messages, one per question.")
text(s, "Take-home", M, 0.7, W - 2 * M, 0.9, size=36, bold=True, font=HEAD, color=WHITE)
takes = [(pct(inh["gyponly"]["median"]), "of the peak channel was there before any reaction: channels are inherited"),
         ("4", "stages in every run, timed by the fraction of gypsum dissolved"),
         ("×10 = ×10.6", "equal permeability ceilings give equal channel depth, whatever the chemistry")]
for i, (b, l) in enumerate(takes):
    x = M + i * 4.1
    text(s, b, x, 2.3, 3.8, 1.0, size=44, bold=True, font=HEAD, color=OPEN if i != 1 else CALCITE)
    text(s, l, x, 3.45, 3.6, 1.6, size=18, color="C9D4DC")
text(s, "Full report, numbers and sources: Forsmark Reactive Channels (claude.ai artifact)", M, 6.5, W - 2 * M, 0.4, size=13, color="8FA3B3")

# Backup -----------------------------------------------------------------------------------------------------------
section("Backup", "Measures and clocks", notes="Backup slides.")

s = new_slide(notes=(
    "How the channel measures differ. All three fall when flow concentrates. Active surface area has 'equal flow in every "
    "fracture' as its reference, so in power-law networks it is low even without channelling. PR_V has 'flow in "
    "proportion to volume' as its reference. n90 counts fractures to 90 % of summed throughflow and defines the channel set "
    "used for inheritance."))
title(s, "Three channel measures")
ms = [("Active surface area", "d_Q / P32 = (Σ S Q)² / (Σ S · Σ S Q²)", "100 % only if every fracture carries the same flow. Maillot et al. 2016; Hyman."),
      ("Participation ratio PR_V", "(Σ Q)² / Σ (Q² / w),  w = volume share", "1 if flow is proportional to volume. Ours."),
      ("n90", "fractures to 90 % of summed throughflow", "A set: used for inheritance. Counts each fracture once.")]
for i, (h, f, b) in enumerate(ms):
    x = M + i * 4.1
    card(s, x, 1.7, 3.8, 3.2)
    text(s, h, x + 0.3, 1.95, 3.2, 0.5, size=19, bold=True, font=HEAD, color=ACCENT)
    text(s, f, x + 0.3, 2.6, 3.2, 0.9, size=15, font="Cambria Math")
    text(s, b, x + 0.3, 3.55, 3.2, 1.2, size=15, color=INK2)
text(s, [[("Size-proportional baseline of d_Q/P32: ", {"bold": True}),
          (f"{dq['4']['if_prop_V']:.1f} / {dq['6']['if_prop_V']:.1f} / {dq['8']['if_prop_V']:.1f} % against measured "
           f"{dq['4']['actual']:.1f} / {dq['6']['actual']:.1f} / {dq['8']['actual']:.1f} % at P32 ×4 / ×6 / ×8 (medians of 15).", {})]],
     M, 5.3, W - 2 * M, 0.8, size=16)

prs.save(HERE / "Forsmark_Reactive_Channels.pptx")
print("slides", len(prs.slides), HERE / "Forsmark_Reactive_Channels.pptx")
