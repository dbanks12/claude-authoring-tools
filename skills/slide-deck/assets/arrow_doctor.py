#!/usr/bin/env python3
"""Connector doctor for the mcp-excalidraw-server canvas.

Excalidraw `arrow` elements are unusable for precise diagrams here: the browser
tab re-derives bound-arrow geometry from focus/gap with its own algorithm on
every render and syncs the result back, so CLI-written arrow geometry never
survives. Plain `line` elements have no binding machinery and are never touched.

Therefore connectors are LINES with a polyline arrowhead (shaft + two wing
segments) and the logical link stored in customData.connect = {from, to}.
The doctor recomputes their geometry from the connected boxes' bboxes.

Usage:
  python3 arrow_doctor.py --convert  # one-time: replace every `arrow` with a connector line
  python3 arrow_doctor.py --fix      # re-route all connector lines from their boxes
  python3 arrow_doctor.py --check    # report degenerate or unlinked connectors

Routing: horizontal pairs join at the shorter box's midline. Vertical pairs run
from the source's edge center to the target's edge center (angled when centers
differ), which draws Merkle trees correctly. Static lines (no customData.connect)
are never modified.
"""
import argparse
import json
import math
import subprocess

CLI = ["npx", "-y", "mcp-excalidraw-server"]
GAP = 6
HEAD = 12
HEAD_ANGLE = math.radians(26)


def sh(args, data=None):
    r = subprocess.run(CLI + args, capture_output=True, text=True, input=data)
    out = r.stdout[r.stdout.index("{"):] if "{" in r.stdout else r.stdout
    return json.loads(out)


def scene():
    els = sh(["export"])["elements"]
    return {e["id"]: e for e in els if not e.get("isDeleted")}


def bbox(e):
    return e["x"], e["y"], e["x"] + (e.get("width") or 0), e["y"] + (e.get("height") or 0)


def route(s_el, e_el):
    sx0, sy0, sx1, sy1 = bbox(s_el)
    ex0, ey0, ex1, ey1 = bbox(e_el)
    scx, scy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
    ecx, ecy = (ex0 + ex1) / 2, (ey0 + ey1) / 2
    horiz_gap = max(ex0 - sx1, sx0 - ex1)
    vert_gap = max(ey0 - sy1, sy0 - ey1)
    if horiz_gap < 0 and vert_gap < 0:
        return None
    if horiz_gap >= vert_gap:  # horizontal: meet at the shorter box's midline
        y = min(max(scy if (sy1 - sy0) <= (ey1 - ey0) else ecy, max(sy0, ey0)), min(sy1, ey1)) \
            if min(sy1, ey1) > max(sy0, ey0) else (scy + ecy) / 2
        if ecx >= scx:
            return (sx1 + GAP, y), (ex0 - GAP, y)
        return (sx0 - GAP, y), (ex1 + GAP, y)
    else:  # vertical: edge center to edge center, angled when centers differ
        if ecy >= scy:
            return (scx, sy1 + GAP), (ecx, ey0 - GAP)
        return (scx, sy0 - GAP), (ecx, ey1 + GAP)


def polyline(points):
    """Relative points list -> same list with arrowhead wings appended at the tip."""
    (px, py), (tx, ty) = points[-2], points[-1]
    dx, dy = tx - px, ty - py
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    c, s = math.cos(HEAD_ANGLE), math.sin(HEAD_ANGLE)
    w1 = [tx - HEAD * (ux * c - uy * s), ty - HEAD * (ux * s + uy * c)]
    w2 = [tx - HEAD * (ux * c + uy * s), ty - HEAD * (-ux * s + uy * c)]
    return points + [w1, [tx, ty], w2]


def connector_element(cid, start, end, style, from_id=None, to_id=None, mid_points=None):
    sx, sy = start
    rel = [[0, 0]] + [[mx - sx, my - sy] for (mx, my) in (mid_points or [])] + [[end[0] - sx, end[1] - sy]]
    e = {"id": cid, "type": "line", "x": sx, "y": sy, "points": polyline(rel),
         "strokeColor": style.get("strokeColor", "#1e1e1e"),
         "strokeWidth": style.get("strokeWidth", 1)}
    if style.get("strokeStyle"):
        e["strokeStyle"] = style["strokeStyle"]
    if from_id and to_id:
        e["customData"] = {"connect": {"from": from_id, "to": to_id}}
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--convert", action="store_true")
    args = ap.parse_args()
    els = scene()

    if args.convert:
        arrows = [e for e in els.values() if e.get("type") == "arrow"]
        creates, deletes = [], []
        for a in arrows:
            style = {k: a.get(k) for k in ("strokeColor", "strokeStyle", "strokeWidth")}
            sb = (a.get("startBinding") or {}).get("elementId")
            eb = (a.get("endBinding") or {}).get("elementId")
            deletes.append(a["id"])
            if sb in els and eb in els:
                r = route(els[sb], els[eb])
                if r:
                    creates.append(connector_element(a["id"], r[0], r[1], style, sb, eb))
                    continue
            pts = a.get("points") or [[0, 0], [50, 0]]
            abs_pts = [(a["x"] + p[0], a["y"] + p[1]) for p in pts]
            creates.append(connector_element(a["id"], abs_pts[0], abs_pts[-1], style,
                                             mid_points=[list(p) for p in abs_pts[1:-1]]))
        sh(["apply"], json.dumps({"delete": deletes}))
        sh(["apply"], json.dumps({"create": creates}))
        print(f"converted {len(creates)} arrows to connector lines")
        return

    connectors = [e for e in els.values()
                  if e.get("type") == "line" and (e.get("customData") or {}).get("connect")]
    updates, report = [], []
    for c in connectors:
        link = c["customData"]["connect"]
        s_el, e_el = els.get(link["from"]), els.get(link["to"])
        if not (s_el and e_el):
            report.append(f"ORPHAN     {c['id']} -> {link}")
            continue
        r = route(s_el, e_el)
        if r is None:
            report.append(f"OVERLAP    {c['id']}")
            continue
        (sx, sy), (ex, ey) = r
        pts = polyline([[0, 0], [ex - sx, ey - sy]])
        updates.append({"id": c["id"], "set": {
            "x": sx, "y": sy, "points": pts,
            "width": max(p[0] for p in pts) - min(p[0] for p in pts),
            "height": max(p[1] for p in pts) - min(p[1] for p in pts),
        }})
    for e in els.values():
        if e.get("type") == "arrow":
            report.append(f"RAW ARROW  {e['id']} (run --convert)")
    for line in report:
        print(line)
    if args.fix and updates:
        sh(["apply"], json.dumps({"update": updates}))
        print(f"re-routed {len(updates)} connector lines")
    elif args.check:
        print(f"{len(connectors)} connectors, {len(updates)} routable")


if __name__ == "__main__":
    main()
