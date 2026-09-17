#!/usr/bin/env python3
"""Regenerate site/img/ from tools/source/.

Requires Pillow with AVIF and WebP support (Pillow >= 11 bundles both):
    python3 -m pip install --upgrade pillow
Run from anywhere:
    python3 tools/build-images.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source"
OUT = ROOT.parent / "site" / "img"

# (source file, output stem, widths, avif quality, webp quality)
JOBS = [
    ("background.png", "hero", [1536, 1024, 640], 45, 72),
    ("explain-model-product.png", "modeling", [1600, 1100, 760], 55, 80),
    ("explain-monitor-product.png", "monitor", [1600, 1100, 760], 55, 80),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, stem, widths, q_avif, q_webp in JOBS:
        src = Image.open(SRC / filename).convert("RGB")
        for width in widths:
            if width > src.width:  # never upscale
                continue
            height = round(src.height * width / src.width)
            resized = src.resize((width, height), Image.LANCZOS)
            resized.save(OUT / f"{stem}-{width}.avif", quality=q_avif, speed=4)
            resized.save(OUT / f"{stem}-{width}.webp", quality=q_webp, method=6)
            print(f"{stem}-{width}: {width}x{height}")


if __name__ == "__main__":
    main()
