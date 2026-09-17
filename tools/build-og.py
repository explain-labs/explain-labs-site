#!/usr/bin/env python3
"""Render site/img/og.png (1200x630) from the brand mark + wordmark.

macOS only: uses `qlmanage` (WebKit) to rasterise an SVG, because neither
rsvg-convert nor ImageMagick is installed and headless Chrome does not run
reliably here. qlmanage renders into a SQUARE canvas, so the artwork is laid
out on a 1200x1200 board and the middle 630 rows are cropped out afterwards.

The Nunito Sans woff2 is inlined as a data URI so the render matches the site
exactly instead of falling back to a system font.

    python3 tools/build-og.py
"""
import base64
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parent / "site"
OUT = SITE / "img" / "og.png"

W, H = 1200, 630
BOARD = 1200
TOP = (BOARD - H) // 2  # 285

MARK = (SITE / "favicon.svg").read_text()
# reuse only the <g> of paths from favicon.svg (skip the plate rect)
MARK_PATHS = MARK.split("<g ", 1)[1].split(">", 1)[1].rsplit("</g>", 1)[0]

font_b64 = base64.b64encode(
    (SITE / "fonts" / "nunito-sans-latin-normal.woff2").read_bytes()
).decode()
font_i_b64 = base64.b64encode(
    (SITE / "fonts" / "nunito-sans-latin-italic.woff2").read_bytes()
).decode()

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{BOARD}" height="{BOARD}" viewBox="0 0 {BOARD} {BOARD}">
<defs>
  <style>
    @font-face {{ font-family:"NS"; font-weight:400 800; font-style:normal;
      src:url(data:font/woff2;base64,{font_b64}) format("woff2"); }}
    @font-face {{ font-family:"NS"; font-weight:400 800; font-style:italic;
      src:url(data:font/woff2;base64,{font_i_b64}) format("woff2"); }}
    text {{ font-family:"NS"; }}
  </style>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#003399"/><stop offset="1" stop-color="#CC0099"/>
  </linearGradient>
</defs>
<rect width="{BOARD}" height="{BOARD}" fill="#0B0B0F"/>
<g transform="translate(143 {TOP + 132}) scale(0.60) translate(-99.1 -100.2)">{MARK_PATHS}</g>
<text x="230" y="{TOP + 152}" font-size="66" font-weight="800" fill="#ffffff" letter-spacing="1">EXPLAIN</text>
<text x="532" y="{TOP + 152}" font-size="66" font-weight="800" font-style="italic" fill="#FF4DC4">LABS</text>
<rect x="80" y="{TOP + 220}" width="96" height="4" rx="2" fill="url(#accent)"/>
<text x="80" y="{TOP + 320}" font-size="54" font-weight="800" fill="#E9EAF0" letter-spacing="-1">Model driven educational tools</text>
<text x="80" y="{TOP + 390}" font-size="54" font-weight="800" fill="#E9EAF0" letter-spacing="-1">for neonatal care</text>
<text x="80" y="{TOP + 500}" font-size="27" font-weight="400" fill="#A3A7B5">explain-labs.com &#183; physiological simulation for neonatology</text>
</svg>
"""

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    src = td / "og.svg"
    src.write_text(svg)
    subprocess.run(
        ["qlmanage", "-t", "-s", str(BOARD), "-o", str(td), str(src)],
        check=True, capture_output=True,
    )
    rendered = td / "og.svg.png"
    im = Image.open(rendered).convert("RGB")
    if im.size != (BOARD, BOARD):
        raise SystemExit(f"unexpected render size {im.size}")
    im.crop((0, TOP, W, TOP + H)).save(OUT, optimize=True)

print(f"{OUT}: {OUT.stat().st_size} bytes")
