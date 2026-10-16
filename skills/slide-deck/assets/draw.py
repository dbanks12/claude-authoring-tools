#!/usr/bin/env python3
"""Tiny layout helper for helper-canvas diagrams written as code.

A deck's diagrams.py imports D and tw from here (add this directory to sys.path).

Each diagram module builds a list of elements with the helpers below, then
push() sends them to the live canvas in one apply. Connectors are plain lines
with polyline arrowheads (arrow_doctor style) so the browser tab never
re-routes them. Re-running a diagram deletes its previous elements first
(every id is prefixed with the diagram key).
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # arrow_doctor.py sits next to this file
from arrow_doctor import connector_element, route  # noqa: E402

CLI = ["npx", "-y", "mcp-excalidraw-server@2.1.2"]

# hue families (AVM mapping of the style system)
FAM = {
    "blue":   ("#1971c2", "#e3f2fd"),   # simulation
    "orange": ("#f08c00", "#fff9db"),   # events
    "purple": ("#9c36b5", "#f3d9fa"),   # tracegen
    "green":  ("#2f9e44", "#d3f9d8"),   # constraining / proving
    "gray":   ("#495057", "#e9ecef"),   # inputs, external, supporting
    "red":    ("#e03131", "#ffe3e3"),   # critical gates
    "teal":   ("#0ca678", "#e6fcf5"),   # the proof (root of trust)
    "ink":    ("#1e1e1e", "#ffffff"),
}
CHAR = 0.6  # hand font width per char per fontSize unit


def tw(text, fs):
    """Estimated rendered width of the longest line."""
    return max(len(line) for line in text.split("\n")) * CHAR * fs


class D:
    def __init__(self, key):
        self.key = key
        self.els = []
        self.boxes = {}
        self.scale = 1.0  # multiplies every font size in this diagram

    def id(self, n):
        return f"{self.key}-{n}"

    def box(self, n, x, y, w, h, text="", fam="gray", kind="data", fs=16, sw=1, sharp=True, fill=None):
        """w=None sizes the box to its label (32px side padding, min 120).
        fill overrides the family tint of a data box."""
        fs = round(fs * self.scale)
        if w is None:
            w = max(120, round(tw(text, fs) + 40))
        if h is None:
            h = round(fs * 1.25 * (text.count("\n") + 1) + 28)
        stroke, tint = FAM[fam]
        e = {"id": self.id(n), "type": "rectangle", "x": x, "y": y, "width": w, "height": h,
             "strokeColor": stroke, "strokeWidth": sw, "roughness": 1}
        if sharp:  # roundness=None does not survive the tab's sync; a zero adaptive radius does
            e["roundness"] = {"type": 3, "value": 0}
        if kind == "data":
            e.update(fillStyle="solid", backgroundColor=fill or tint)
        elif kind == "hash":
            e.update(fillStyle="cross-hatch", backgroundColor=tint)
        elif kind == "container":
            e.update(backgroundColor="transparent")
        elif kind == "zone":
            e.update(backgroundColor="transparent", strokeStyle="dotted")
        elif kind == "elided":
            e.update(backgroundColor="transparent", strokeStyle="dashed", strokeColor=FAM["gray"][0])
        elif kind == "gate":
            e.update(fillStyle="solid", backgroundColor=FAM["red"][1], strokeWidth=2)
        if text:
            assert tw(text, fs) + 16 <= w, f"{n}: '{text}' too wide for {w} (needs {tw(text, fs) + 16:.0f})"
            e.update(text=text, fontSize=fs, strokeColor=e["strokeColor"])
        self.els.append(e)
        self.boxes[n] = e
        return e

    def text(self, n, x, y, text, fs=16, fam="ink", align="left"):
        fs = round(fs * self.scale)
        e = {"id": self.id(n), "type": "text", "x": x, "y": y, "text": text, "fontSize": fs,
             "strokeColor": FAM[fam][0], "textAlign": align, "verticalAlign": "top",
             "width": tw(text, fs), "height": fs * 1.25 * (text.count("\n") + 1)}
        self.els.append(e)
        return e

    def label(self, text, y):
        """Big uppercase nav label in the left margin column."""
        return self.text("navlabel", -520, y, text.upper(), fs=36, fam="gray")

    def link(self, a, b, fam="ink", dashed=False, sw=1, note=None, way=None):
        """way="v" forces edge-center to edge-center vertical routing."""
        s, t = self.boxes[a], self.boxes[b]
        r = route(s, t)
        if way == "v":
            scx, ecx = s["x"] + s["width"] / 2, t["x"] + t["width"] / 2
            if t["y"] > s["y"]:
                r = (scx, s["y"] + s["height"] + 6), (ecx, t["y"] - 6)
            else:
                r = (scx, s["y"] - 6), (ecx, t["y"] + t["height"] + 6)
        assert r, f"{a}->{b} overlap"
        style = {"strokeColor": FAM[fam][0], "strokeWidth": sw}
        if dashed:
            style["strokeStyle"] = "dashed"
        c = connector_element(self.id(f"ln-{a}-{b}"), r[0], r[1], style, self.id(a), self.id(b))
        self.els.append(c)
        if note:
            (sx, sy), (ex, ey) = r
            mx, my = (sx + ex) / 2, (sy + ey) / 2
            if abs(ex - sx) > abs(ey - sy):   # horizontal: note above the line
                self.text(f"nt-{a}-{b}", mx - tw(note, 14) / 2, my - 24, note, fs=14, fam=fam)
            else:                             # vertical: note right of midpoint
                self.text(f"nt-{a}-{b}", mx + 14, my - 9, note, fs=14, fam=fam)
        return c

    def line(self, n, pts, fam="gray", dashed=False, head=True):
        """Free polyline connector through absolute points."""
        style = {"strokeColor": FAM[fam][0]}
        if dashed:
            style["strokeStyle"] = "dashed"
        c = connector_element(self.id(n), pts[0], pts[-1], style, mid_points=pts[1:-1])
        if not head:
            c["points"] = c["points"][:-3]
        self.els.append(c)
        return c

    def row(self, items, x, y, gap=60, h=None, fs=16):
        """Lay (name, text, fam, kind) boxes left to right. Returns the end x."""
        for n, text, fam, kind in items:
            e = self.box(n, x, y, None, h, text, fam, kind, fs)
            x += e["width"] + gap
        return x - gap

    def region(self):
        """Content bbox (without the nav label) plus 30 units of margin."""
        es = [e for e in self.els if not e["id"].endswith("navlabel")]
        x0 = min(e["x"] for e in es); y0 = min(e["y"] for e in es)
        x1 = max(e["x"] + e.get("width", 0) for e in es); y1 = max(e["y"] + e.get("height", 0) for e in es)
        return [x0 - 30, y0 - 30, x1 + 30, y1 + 30]

    def push(self):
        existing = json.loads(run(["export"]))["elements"]
        # also drop bound labels the tab re-injects under random ids
        old = [e["id"] for e in existing if e["id"].startswith(self.key + "-")
               or (e.get("containerId") or "").startswith(self.key + "-")]
        if old:
            run(["apply"], json.dumps({"delete": old}))
        run(["apply"], json.dumps({"create": self.els}))
        reindex()
        # create ignores roundness=None and defaults to rounded; an update sticks
        rects = [{"id": e["id"]} for e in self.els if e["type"] == "rectangle"]
        run(["apply"], json.dumps({"update": rects}))
        print(f"{self.key}: {len(self.els)} elements")


def reindex():
    """Re-import the scene without `index` keys. The server writes invalid
    fractional indices (a0, a10, a34), which make the browser tab render nothing."""
    scene = json.loads(run(["export"]))
    for e in scene["elements"]:
        e.pop("index", None)
    run(["import", "-", "--replace"], json.dumps(scene))


def run(args, data=None):
    r = subprocess.run(CLI + args, capture_output=True, text=True, input=data)
    if r.returncode:
        sys.exit(f"{args[0]} failed: {r.stderr}")
    return r.stdout
