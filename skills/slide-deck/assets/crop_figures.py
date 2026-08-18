#!/usr/bin/env python3
"""Crop scene-coordinate regions out of a full-canvas screenshot.

The tab's zoom-to-fit letterboxing is not uniform, so a solved-padding linear map
breaks on extreme scene aspect ratios. Instead: detect the rendered ink bounding
box in the PNG and map the scene's element bounding box onto it. Stroke overshoot
adds a few units of error, so crop regions must keep >= 20 scene-units of margin.

Usage:
  python3 crop_figures.py SCREENSHOT REGIONS.json
where REGIONS.json is [{"out": "fig.png", "box": [x0, y0, x1, y1]}, ...] in scene units.
"""
import json
import subprocess
import sys

from PIL import Image

CLI = ["npx", "-y", "mcp-excalidraw-server"]


def scene_bbox():
    r = subprocess.run(CLI + ["export"], capture_output=True, text=True)
    els = json.loads(r.stdout[r.stdout.index("{"):])["elements"]
    els = [e for e in els if not e.get("isDeleted")]
    xs = [e["x"] for e in els]
    ys = [e["y"] for e in els]
    xe = [e["x"] + (e.get("width") or 0) for e in els]
    ye = [e["y"] + (e.get("height") or 0) for e in els]
    return min(xs), min(ys), max(xe), max(ye)


def ink_bbox(im):
    from PIL import ImageChops
    bg = im.getpixel((0, 0))
    diff = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, bg[:3] if isinstance(bg, tuple) else bg))
    return diff.convert("L").point(lambda v: 255 if v > 8 else 0).getbbox()


def main():
    shot, regions_path = sys.argv[1], sys.argv[2]
    im = Image.open(shot)
    ix0, iy0, ix1, iy1 = ink_bbox(im)
    sx0, sy0, sx1, sy1 = scene_bbox()
    fx = (ix1 - ix0) / (sx1 - sx0)
    fy = (iy1 - iy0) / (sy1 - sy0)

    def m(x, y):
        return int(ix0 + (x - sx0) * fx), int(iy0 + (y - sy0) * fy)

    for r in json.load(open(regions_path)):
        x0, y0, x1, y1 = r["box"]
        a, b = m(x0, y0), m(x1, y1)
        im.crop((max(0, a[0]), max(0, a[1]), min(im.width, b[0]), min(im.height, b[1]))).save(r["out"])
        print("cropped", r["out"])


if __name__ == "__main__":
    main()
