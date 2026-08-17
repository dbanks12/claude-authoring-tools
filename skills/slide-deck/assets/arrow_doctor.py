#!/usr/bin/env python3
"""Arrow doctor for the mcp-excalidraw-server canvas.

Why this exists: the canvas server does NOT route arrows. A bound arrow created
without explicit points is stored with stub geometry ([[0,0],[100,0]]) and the
routing is delegated to whatever browser tab renders next. Tab writeback then
races CLI `apply` batches and can collapse arrows to zero length. The cure is to
never depend on the tab: give every bound arrow explicit edge-to-edge geometry
whose bindings (focus/gap) agree with it, so the frontend has nothing to re-route.

Usage:
  python3 arrow_doctor.py --check    # list degenerate / suspicious arrows
  python3 arrow_doctor.py --fix      # rewrite geometry of every bound arrow

Idempotent. Run --fix after any batch of shape edits, then screenshot.
"""
import argparse
import json
import subprocess

CLI = ["npx", "-y", "mcp-excalidraw-server"]
GAP = 6


def sh(args, data=None):
    r = subprocess.run(CLI + args, capture_output=True, text=True, input=data)
    out = r.stdout[r.stdout.index("{"):] if "{" in r.stdout else r.stdout
    return json.loads(out)


def scene():
    els = sh(["export"])["elements"]
    return {e["id"]: e for e in els if not e.get("isDeleted")}


def bbox(e):
    return e["x"], e["y"], e["x"] + (e.get("width") or 0), e["y"] + (e.get("height") or 0)


def degenerate(a):
    pts = a.get("points") or []
    if len(pts) < 2:
        return True
    dx = pts[-1][0] - pts[0][0]
    dy = pts[-1][1] - pts[0][1]
    return abs(dx) < 5 and abs(dy) < 5


def route(s_el, e_el):
    """Straight edge-midpoint-to-edge-midpoint segment between two boxes.

    Returns (start_xy, end_xy, s_focus, e_focus) or None for overlapping boxes.
    Cross-axis attachment targets the centre of the SMALLER extent, clamped into
    the other box's range, so tall-vs-short pairs get a horizontal arrow at the
    short box's midline (the `focus` value encodes that offset for Excalidraw).
    """
    sx0, sy0, sx1, sy1 = bbox(s_el)
    ex0, ey0, ex1, ey1 = bbox(e_el)
    scx, scy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
    ecx, ecy = (ex0 + ex1) / 2, (ey0 + ey1) / 2

    horiz_gap = max(ex0 - sx1, sx0 - ex1)
    vert_gap = max(ey0 - sy1, sy0 - ey1)
    if horiz_gap < 0 and vert_gap < 0:
        return None  # boxes overlap; leave to manual routing

    if horiz_gap >= vert_gap:  # horizontal arrow
        y = min(max(scy if (sy1 - sy0) <= (ey1 - ey0) else ecy, max(sy0, ey0)), min(sy1, ey1)) \
            if min(sy1, ey1) > max(sy0, ey0) else (scy + ecy) / 2
        if ecx >= scx:
            start, end = (sx1 + GAP, y), (ex0 - GAP, y)
        else:
            start, end = (sx0 - GAP, y), (ex1 + GAP, y)
        s_focus = (y - scy) / ((sy1 - sy0) / 2 or 1)
        e_focus = (y - ecy) / ((ey1 - ey0) / 2 or 1)
    else:  # vertical arrow: center of source edge to center of target edge (angled when centers differ)
        if ecy >= scy:
            start, end = (scx, sy1 + GAP), (ecx, ey0 - GAP)
        else:
            start, end = (scx, sy0 - GAP), (ecx, ey1 + GAP)
        s_focus = 0.0
        e_focus = 0.0
    return start, end, s_focus, e_focus


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    els = scene()
    arrows = [e for e in els.values() if e.get("type") == "arrow"]
    updates, report = [], []
    for a in arrows:
        sb, eb = a.get("startBinding") or {}, a.get("endBinding") or {}
        s_el, e_el = els.get(sb.get("elementId")), els.get(eb.get("elementId"))
        if degenerate(a):
            report.append(f"DEGENERATE {a['id']}")
        if not (s_el and e_el):
            if not (sb or eb):
                report.append(f"UNBOUND    {a['id']} (will collapse eventually; bind it)")
            continue
        r = route(s_el, e_el)
        if r is None:
            report.append(f"OVERLAP    {a['id']} ({s_el['id']} / {e_el['id']}), skipped")
            continue
        (sx, sy), (ex, ey), sf, ef = r
        updates.append({"id": a["id"], "set": {
            "x": sx, "y": sy,
            "points": [[0, 0], [ex - sx, ey - sy]],
            "width": abs(ex - sx), "height": abs(ey - sy),
            "startBinding": {"elementId": s_el["id"], "focus": round(sf, 3), "gap": GAP},
            "endBinding": {"elementId": e_el["id"], "focus": round(ef, 3), "gap": GAP},
        }})

    for line in report:
        print(line)
    if args.fix and updates:
        sh(["apply"], json.dumps({"update": updates}))
        print(f"rewrote geometry of {len(updates)} bound arrows")
    elif args.check:
        print(f"{len(arrows)} arrows, {len(updates)} bound and reroutable")


if __name__ == "__main__":
    main()
