#!/usr/bin/env python3
"""Rasterize the report's inline cartoons (report_phase1/index.html is the source of truth) to deck/cartoons/<name>.png
with resvg (deck/.venv).  Light theme: CSS variables replaced by the report's light-mode colours.
  forsmark_reactive/deck/.venv/bin/python forsmark_reactive/deck/render_cartoons.py"""
import re
import resvg_py
from pathlib import Path
HERE = Path(__file__).resolve().parent
html = (HERE.parent / "report_phase1" / "index.html").read_text()
VARS = dict(mineral="#8a8f96", open="#9fd3f0", calcite="#e9b949", flow="#d2572a", ion="#6b4fbb", rock="#d9d4c7",
            ink="#16181a", **{"ink-2": "#4c5157"}, rule="#dcdcd6", accent="#1f5f8b", surface="#ffffff", bg="#ffffff")
out = HERE / "cartoons"; out.mkdir(exist_ok=True)
for m in re.findall(r'<svg xmlns="http://www\.w3\.org/2000/svg" class="cartoon".*?</svg>', html, re.S):
    name = re.search(r'<marker id="([a-z0-9_]+)-', m)[1]
    s = re.sub(r"var\(--([a-z0-9-]+)\)", lambda v: VARS.get(v[1], "#888888"), m).replace("currentColor", VARS["ink"])
    w, h = map(int, re.search(r'viewBox="0 0 (\d+) (\d+)"', s).groups())
    s = s.replace('class="cartoon"', f'width="{w}" height="{h}" font-family="Calibri, Arial, sans-serif"', 1)
    png = resvg_py.svg_to_bytes(svg_string=s, background="#ffffff", width=3 * w, height=3 * h)
    (out / f"{name}.png").write_bytes(bytes(png)); print(name, w, h)
