#!/usr/bin/env node
// Lay out a small graph spec with ELK and print Excalidraw elements for `add`.
//
// Usage: node layout.mjs spec.json | npx -y mcp-excalidraw-server@2.1.2 add
//        (spec on stdin when no file is given)
// One-time setup: npm install --prefix <this directory>
//
// Spec:
// {
//   "direction": "RIGHT" | "DOWN",           default RIGHT
//   "origin": [x, y],                        default [0, 0]
//   "nodes":  [{"id", "label", "sub"?, "fam"?, "change"?}],
//   "edges":  [{"from", "to", "label"?, "change"?, "dashed"?}],
//   "groups": [{"id", "label", "members": [node ids]}]
// }
// fam: gray | blue | green | orange | purple | red | teal (default gray)
// change: added | changed | removed | context (overrides fam)
import { readFileSync } from "node:fs";
import ELK from "elkjs/lib/elk.bundled.js";

const FAM = {
  gray: ["#495057", "#e9ecef"],
  blue: ["#1971c2", "#e3f2fd"],
  green: ["#2f9e44", "#d3f9d8"],
  orange: ["#f08c00", "#fff9db"],
  purple: ["#9c36b5", "#f3d9fa"],
  red: ["#e03131", "#ffe3e3"],
  teal: ["#0ca678", "#e6fcf5"],
};
// [stroke, fill, strokeStyle]
const CHANGE = {
  added: ["#2f9e44", "#d3f9d8", "solid"],
  changed: ["#f08c00", "#fff9db", "solid"],
  removed: ["#e03131", "transparent", "dashed"],
  context: ["#868e96", "transparent", "solid"],
};
const FS = 18; // node label font size
const CHAR = 0.6; // hand font width per char per font size unit (same as draw.py)

const textWidth = (s, fs) => Math.max(...s.split("\n").map((l) => l.length)) * CHAR * fs;
const style = (item) =>
  CHANGE[item.change] ?? [...(FAM[item.fam ?? "gray"] ?? FAM.gray), "solid"];

const spec = JSON.parse(readFileSync(process.argv[2] ?? 0, "utf8"));
const [ox, oy] = spec.origin ?? [0, 0];
const groupOf = {};
for (const g of spec.groups ?? []) for (const m of g.members) groupOf[m] = g.id;

const elkNode = (n) => {
  const text = n.sub ? `${n.label}\n${n.sub}` : n.label;
  return { id: n.id, width: Math.max(140, Math.round(textWidth(text, FS) + 48)), height: n.sub ? 84 : 64 };
};
const graph = {
  id: "root",
  layoutOptions: {
    "elk.algorithm": "layered",
    "elk.direction": spec.direction ?? "RIGHT",
    "elk.edgeRouting": "ORTHOGONAL",
    "elk.hierarchyHandling": "INCLUDE_CHILDREN",
    "elk.spacing.nodeNode": "60",
    "elk.layered.spacing.nodeNodeBetweenLayers": "100",
    "elk.spacing.edgeLabel": "8",
    "elk.spacing.edgeEdge": "24",
    "elk.layered.spacing.edgeEdgeBetweenLayers": "24",
  },
  children: [
    ...(spec.groups ?? []).map((g) => ({
      id: g.id,
      layoutOptions: { "elk.padding": "[top=56,left=28,bottom=28,right=28]" },
      children: spec.nodes.filter((n) => groupOf[n.id] === g.id).map(elkNode),
    })),
    ...spec.nodes.filter((n) => !groupOf[n.id]).map(elkNode),
  ],
  // Edges live on the root, so ELK reports their points in root coordinates.
  edges: (spec.edges ?? []).map((e, i) => ({
    id: `e${i}`,
    sources: [e.from],
    targets: [e.to],
    labels: e.label ? [{ text: e.label, width: textWidth(e.label, 16) + 8, height: 22 }] : [],
  })),
};

const out = await new ELK().layout(graph);
const els = [];
const nodes = Object.fromEntries(spec.nodes.map((n) => [n.id, n]));

for (const top of out.children) {
  const group = (spec.groups ?? []).find((g) => g.id === top.id);
  if (!group) {
    pushNode(top, 0, 0);
    continue;
  }
  const [x, y] = [ox + top.x, oy + top.y];
  els.push({ id: group.id, type: "rectangle", x, y, width: top.width, height: top.height,
    strokeColor: "#868e96", backgroundColor: "transparent", strokeStyle: "dotted" });
  els.push({ id: `${group.id}-label`, type: "text", x: x + 16, y: y + 12, text: group.label,
    fontSize: 16, strokeColor: "#868e96", textAlign: "left", verticalAlign: "top" });
  for (const child of top.children) pushNode(child, top.x, top.y);
}

function pushNode(ln, dx, dy) {
  const n = nodes[ln.id];
  const [stroke, fill, strokeStyle] = style(n);
  els.push({ id: n.id, type: "rectangle", x: ox + dx + ln.x, y: oy + dy + ln.y,
    width: ln.width, height: ln.height, strokeColor: stroke, backgroundColor: fill,
    fillStyle: "solid", strokeStyle, text: n.sub ? `${n.label}\n${n.sub}` : n.label, fontSize: FS });
}

(spec.edges ?? []).forEach((e, i) => {
  const sec = out.edges[i].sections[0];
  const pts = [sec.startPoint, ...(sec.bendPoints ?? []), sec.endPoint];
  const [stroke, , strokeStyle] = e.change ? style(e) : ["#1e1e1e", null, "solid"];
  const a = { id: `${e.from}--${e.to}`, type: "arrow", strokeColor: stroke,
    strokeStyle: e.dashed ? "dashed" : strokeStyle, customData: { from: e.from, to: e.to } };
  if (pts.length === 2) {
    // Straight edges bind to their boxes, so they follow when a person moves a box.
    Object.assign(a, { x: 0, y: 0, startElementId: e.from, endElementId: e.to });
  } else {
    // The server drops bend points on bound arrows, so routed edges stay unbound.
    const [x0, y0] = [ox + pts[0].x, oy + pts[0].y];
    Object.assign(a, { x: x0, y: y0, points: pts.map((p) => [ox + p.x - x0, oy + p.y - y0]) });
  }
  els.push(a);
  // ELK reserved room beside the edge for its label. Excalidraw would center an
  // arrow label on the polyline midpoint instead, often on top of a bend.
  const lab = out.edges[i].labels?.[0];
  if (lab) els.push({ id: `${a.id}-label`, type: "text", x: ox + lab.x, y: oy + lab.y, text: e.label,
    fontSize: 16, strokeColor: stroke, textAlign: "left", verticalAlign: "top" });
});

process.stdout.write(JSON.stringify(els, null, 1) + "\n");
