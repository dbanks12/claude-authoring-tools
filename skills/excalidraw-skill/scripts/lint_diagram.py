#!/usr/bin/env python3
"""Check a diagram against the skill's budgets. Exit 1 on any FAIL.

Usage:
  python3 lint_diagram.py scene.excalidraw
  npx -y mcp-excalidraw-server@2.1.2 export | python3 lint_diagram.py -
  python3 lint_diagram.py scene.excalidraw --box 0,0,900,400   (one diagram on a shared canvas)

A node is a shape with a label. A zone is a shape without one.
Raise a limit with a flag only when the brief says why.
"""
import argparse
import json
import sys

SHAPES = {"rectangle", "ellipse", "diamond"}
NEUTRAL = {"#1e1e1e", "#000000", "#495057", "#868e96", "transparent"}


def words(s):
    return len(s.split())


def bbox(e):
    return e["x"], e["y"], e["x"] + e.get("width", 0), e["y"] + e.get("height", 0)


def segments(e):
    pts = [(e["x"] + p[0], e["y"] + p[1]) for p in e.get("points", [])]
    if (e.get("customData") or {}).get("connect"):
        pts = pts[:-3]  # arrow_doctor connector: drop the arrowhead wings
    return list(zip(pts, pts[1:]))


def cross(s, t):
    """Proper intersection of two segments (shared endpoints do not count)."""
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return (v > 1e-9) - (v < -1e-9)
    (p, q), (r, u) = s, t
    return orient(p, q, r) * orient(p, q, u) < 0 and orient(r, u, p) * orient(r, u, q) < 0


def hits_box(seg, box, pad=4):
    """Segment passes through the box interior (shrunk by pad)."""
    x0, y0, x1, y1 = box[0] + pad, box[1] + pad, box[2] - pad, box[3] - pad
    (ax, ay), (bx, by) = seg
    for i in range(21):
        t = i / 20
        x, y = ax + (bx - ax) * t, ay + (by - ay) * t
        if x0 < x < x1 and y0 < y < y1:
            return True
    return False


def near(pt, box, gap=16):
    x, y = pt
    return box[0] - gap <= x <= box[2] + gap and box[1] - gap <= y <= box[3] + gap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene", help=".excalidraw file, or - for stdin")
    ap.add_argument("--box", help="x0,y0,x1,y1: lint only elements inside this scene region")
    ap.add_argument("--max-nodes", type=int, default=12)
    ap.add_argument("--max-words", type=int, default=40, help="total words in the drawing")
    ap.add_argument("--max-label-words", type=int, default=5, help="words per line of a node label")
    ap.add_argument("--max-arrow-words", type=int, default=3)
    ap.add_argument("--max-note-words", type=int, default=12, help="words in one free text element")
    ap.add_argument("--max-colors", type=int, default=5, help="distinct non-gray stroke colors")
    args = ap.parse_args()

    scene = json.load(sys.stdin if args.scene == "-" else open(args.scene))
    els = [e for e in scene["elements"] if not e.get("isDeleted")]
    if args.box:
        x0, y0, x1, y1 = map(float, args.box.split(","))
        els = [e for e in els if x0 <= bbox(e)[0] and bbox(e)[2] <= x1 and y0 <= bbox(e)[1] and bbox(e)[3] <= y1]
    by_id = {e["id"]: e for e in els}

    texts = [e for e in els if e["type"] == "text"]
    labels = {t["containerId"]: t for t in texts if t.get("containerId") in by_id}
    shapes = [e for e in els if e["type"] in SHAPES]
    nodes = [s for s in shapes if s["id"] in labels]
    edges = [e for e in els if e["type"] == "arrow"
             or (e["type"] == "line" and (e.get("customData") or {}).get("connect"))]
    fails, warns = [], []

    if len(nodes) > args.max_nodes:
        fails.append(f"nodes={len(nodes)} (max {args.max_nodes}). Split the diagram.")

    total = sum(words(t.get("originalText") or t["text"]) for t in texts)
    if total > args.max_words:
        fails.append(f"words={total} (max {args.max_words}). Move sentences to the caption.")

    for nid, t in labels.items():
        kind = by_id[nid]["type"]
        for line in (t.get("originalText") or t["text"]).splitlines():
            limit = args.max_arrow_words if kind == "arrow" else args.max_label_words
            if words(line) > limit:
                fails.append(f"{nid}: '{line}' has {words(line)} words (max {limit}).")
        if kind in SHAPES and t.get("height", 0) > by_id[nid].get("height", 0):
            fails.append(f"{nid}: label is taller than its box. Widen the box or cut words.")

    for t in texts:
        if t.get("containerId"):
            continue
        n = words(t["text"])
        if n > args.max_note_words:
            fails.append(f"{t['id']}: free text has {n} words (max {args.max_note_words}).")

    colors = {s.get("strokeColor", "").lower() for s in shapes + edges} - NEUTRAL - {""}
    if len(colors) > args.max_colors:
        fails.append(f"colors={len(colors)} (max {args.max_colors}): {', '.join(sorted(colors))}")

    segs = {e["id"]: segments(e) for e in edges}
    ids = list(segs)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if any(cross(s, t) for s in segs[a] for t in segs[b]):
                fails.append(f"crossing: {a} x {b}")

    for e in edges:
        if not segs[e["id"]]:
            continue
        ends = (segs[e["id"]][0][0], segs[e["id"]][-1][1])
        for n in nodes:
            box = bbox(n)
            if any(near(p, box) for p in ends):
                continue  # an endpoint box
            if any(hits_box(s, box) for s in segs[e["id"]]):
                fails.append(f"{e['id']} passes through {n['id']}")
        labelled = e["id"] in labels or any(t["id"].startswith(e["id"] + "-") for t in texts)
        if not labelled:
            warns.append(f"{e['id']}: arrow has no label.")

    for line in fails:
        print("FAIL ", line)
    for line in warns:
        print("WARN ", line)
    print(f"{'FAIL' if fails else 'PASS'}  nodes={len(nodes)} words={total} edges={len(edges)} colors={len(colors)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
