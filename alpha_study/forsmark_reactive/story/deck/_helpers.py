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
IMG = HERE.parent / "report" / "img"
CART = HERE.parents[1] / "deck" / "cartoons"
N = None   # story deck: numbers from story/STORY.md (reviewed 7 Nov) and its source CSVs

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

