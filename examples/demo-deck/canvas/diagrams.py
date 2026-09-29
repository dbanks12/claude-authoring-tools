#!/usr/bin/env python3
"""The demo deck's one diagram, written as code with the slide-deck draw helper.

Usage (with the canvas server running and its browser tab open):
  python3 diagrams.py          # push the diagram to the live canvas, write regions.json
  python3 ../../../skills/slide-deck/assets/render_figures.py regions.json
  python3 ../../../skills/slide-deck/assets/trim.py ../figures
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "skills/slide-deck/assets"))
from draw import D  # noqa: E402

Y = 30000  # far away from anything else on a shared live canvas


def flow():
    d = D("demoflow")
    d.row([
        ("md", "slides.md", "gray", "data"),
        ("build", "build.py", "purple", "container"),
        ("html", "demo-deck.html", "blue", "data"),
        ("pdf", "pdf.py", "purple", "container"),
        ("out", "demo-deck.pdf", "green", "data"),
    ], 0, Y + 40, gap=80, h=64, fs=18)
    for a, b in [("md", "build"), ("build", "html"), ("html", "pdf"), ("pdf", "out")]:
        d.link(a, b)
    md = d.boxes["md"]
    d.box("figs", md["x"], Y + 200, 170, 64, "figures/*.png", "orange", "data", fs=16)
    d.box("canvas", md["x"], Y + 340, 170, 64, "canvas", "gray", "container", fs=16)
    d.link("canvas", "figs", note="render + trim")
    d.link("figs", "build", way="v")
    return d


def main():
    d = flow()
    d.push()
    box = d.region()
    (HERE / "regions.json").write_text(json.dumps({"flow": {"out": "../figures/fig-flow.png", "box": box}}, indent=1))


if __name__ == "__main__":
    main()
