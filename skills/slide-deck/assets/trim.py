#!/usr/bin/env python3
"""Trim figures/*.png to their drawn content plus an even white margin.

Crop regions come from estimated text widths, so renders carry uneven slack.
Run after render_figures.py:  python3 trim.py FIGURES_DIR [name ...]   (no names trims every figure)
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops

PAD = 8  # pixels of white kept around the ink


def trim(path):
    im = Image.open(path).convert("RGB")
    ink = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255)))
    box = ink.convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not box:
        return
    x0, y0, x1, y1 = box
    out = Image.new("RGB", (x1 - x0 + 2 * PAD, y1 - y0 + 2 * PAD), "white")
    out.paste(im.crop(box), (PAD, PAD))
    out.save(path)
    print(f"{path.name}: {im.size[0]}x{im.size[1]} -> {out.size[0]}x{out.size[1]}")


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: trim.py FIGURES_DIR [name ...]")
    figures, names = Path(sys.argv[1]), sys.argv[2:]
    paths = [figures / f"fig-{n}.png" for n in names] if names else sorted(figures.glob("fig-*.png"))
    for p in paths:
        trim(p)


if __name__ == "__main__":
    main()
