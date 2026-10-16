#!/usr/bin/env python3
"""Render crisp figure crops from the live canvas.

The canvas screenshot renders the whole scene at roughly scale 1, so cropping a
figure-sized region yields a soft ~1x image. This tool "zooms in before crop":
for each figure it loads ONLY that region's elements, scaled up by K, onto the
canvas (import --replace), screenshots, crops the scaled region exactly, and
finally restores the original scene.

Usage:
  python3 render_figures.py REGIONS.json [--only name1,name2] [--scale 2.5]
REGIONS.json: {"name": {"out": "fig-name.png", "box": [x0, y0, x1, y1]}, ...}
in scene coordinates. The live canvas is replaced during the run and restored
afterwards; avoid editing the canvas while this runs.
"""
import copy
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageChops

CLI = ["npx", "-y", "mcp-excalidraw-server@2.1.2"]
SYNC_SECONDS = 3


def sh(args, data=None):
    r = subprocess.run(CLI + args, capture_output=True, text=True, input=data)
    out = r.stdout
    if "{" not in out:
        raise SystemExit(f"CLI error: {out[-200:]}{r.stderr[-200:]}")
    return json.loads(out[out.index("{"):])


def bbox(e):
    return e["x"], e["y"], e["x"] + (e.get("width") or 0), e["y"] + (e.get("height") or 0)


def intersects(e, box, pad=4):
    x0, y0, x1, y1 = bbox(e)
    return not (x1 < box[0] - pad or x0 > box[2] + pad or y1 < box[1] - pad or y0 > box[3] + pad)


def scaled(e, k):
    c = copy.deepcopy(e)
    # the server writes invalid fractional indices (a0, a10, a34), which can blank the export
    c.pop("index", None)
    for f in ("x", "y", "width", "height", "fontSize", "strokeWidth"):
        if isinstance(c.get(f), (int, float)):
            c[f] = c[f] * k
    if c.get("points"):
        c["points"] = [[p[0] * k, p[1] * k] for p in c["points"]]
    return c


def screenshot():
    out = Path(tempfile.mkstemp(suffix=".png")[1])
    sh(["screenshot", "--out", str(out)])
    return Image.open(out)


def ink_bbox(im):
    bg = im.convert("RGB").getpixel((0, 0))
    diff = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, bg))
    return diff.convert("L").point(lambda v: 255 if v > 8 else 0).getbbox()


def main():
    regions = json.loads(Path(sys.argv[1]).read_text())
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    k = float(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 2.5

    original = sh(["export"])
    for e in original["elements"]:
        e.pop("index", None)  # restore without the invalid indices too
    els = [e for e in original["elements"] if not e.get("isDeleted")]
    backup = Path(tempfile.mkstemp(suffix=".excalidraw")[1])
    backup.write_text(json.dumps(original))
    print(f"scene backed up to {backup}")

    try:
        for name, spec in regions.items():
            if only and name not in only:
                continue
            box = spec["box"]
            kept = [scaled(e, k) for e in els if intersects(e, box)]
            scene = {"type": "excalidraw", "version": 2, "elements": kept}
            tmp = Path(tempfile.mkstemp(suffix=".excalidraw")[1])
            tmp.write_text(json.dumps(scene))
            sh(["import", str(tmp), "--replace"])
            time.sleep(SYNC_SECONDS)
            im = screenshot()
            ix0, iy0, ix1, iy1 = ink_bbox(im)
            xs = [e["x"] for e in kept]
            ys = [e["y"] for e in kept]
            xe = [e["x"] + (e.get("width") or 0) for e in kept]
            ye = [e["y"] + (e.get("height") or 0) for e in kept]
            sx0, sy0, sx1, sy1 = min(xs), min(ys), max(xe), max(ye)
            fx = (ix1 - ix0) / (sx1 - sx0)
            fy = (iy1 - iy0) / (sy1 - sy0)
            a = (int(ix0 + (box[0] * k - sx0) * fx), int(iy0 + (box[1] * k - sy0) * fy))
            b = (int(ix0 + (box[2] * k - sx0) * fx), int(iy0 + (box[3] * k - sy0) * fy))
            crop = im.crop((max(0, a[0]), max(0, a[1]), min(im.width, b[0]), min(im.height, b[1])))
            crop.save(spec["out"])
            print(f"{name}: {crop.size[0]}x{crop.size[1]} -> {spec['out']}")
    finally:
        sh(["import", str(backup), "--replace"])
        time.sleep(SYNC_SECONDS)
        print("original scene restored")


if __name__ == "__main__":
    main()
