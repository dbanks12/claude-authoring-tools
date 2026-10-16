---
name: excalidraw-skill
description: Excalidraw diagrams that explain code, code changes, designs, and concepts, drawn on a live canvas. Use when an agent needs to (1) draw or lay out a diagram, (2) refine one by rendering and critiquing its own work, (3) export/import .excalidraw files or PNG/SVG images, (4) save/restore canvas snapshots, (5) convert Mermaid to Excalidraw, or (6) perform element-level CRUD, alignment, grouping, or locking. Drives the mcp-excalidraw-server CLI, which auto-starts the canvas server; MCP tools and a REST API are equivalent alternatives.
---

# Excalidraw diagrams

A diagram earns its place when a cold reader sees a mechanism faster than prose could tell it: where data flows, what a change adds or removes, which parts talk. Every step below serves one **claim**, the sentence the picture must prove.

Canvas mechanics (CLI, element format, arrows, snapshots, file I/O, errors) live in `references/mechanics.md`. Read it before the first canvas command in a session. Use `npx -y mcp-excalidraw-server@2.1.2` or later; screenshots and `render` work headless, with no browser tab.

## 1. Decide whether to draw

Pick the type from the reader's question:

| Reader's question | Type |
|---|---|
| Where does this system sit? | Context: the system as one box, its neighbors around it |
| What are the parts and how do they talk? | Container or component boxes with labeled arrows |
| In what order do things happen across parts? | Sequence: one lane per actor, time runs down |
| Where does data go, and what boundaries does it cross? | Data flow with zones for trust or process boundaries |
| What did this change do? | Code change, one layout (see section 6) |
| Which of two designs? | Same layout twice, with the differing edge in the accent color |
| What states can this be in? | State machine |

When the claim has no spatial relationship (a rename, a list, a one-line fix, a regex), write the sentence instead and stop.

Done when: you named one type, or chose a sentence.

## 2. Write the brief

Write four lines before any canvas command, and show them to the user with the result:

```text
Reader:   reviewer of PR #412, knows the service, not this module
Question: what does the retry queue change about write ordering?
Claim:    writes now pass through RetryQueue, so a failed write retries after newer writes.
Type:     code change, one layout
```

Read the code first. Use the names the code uses, and draw only parts that exist.

Done when: the claim is one sentence that names what the picture shows.

## 3. Stay inside the budget

| Budget | Default | Lint flag |
|---|---|---|
| Nodes | 3–7, at most 12; split above that | `--max-nodes` |
| Words per node label line | ≤ 5. Line one is a name of ≤ 4 words, line two an optional file path or type | `--max-label-words` |
| Arrow label | verb first, ≤ 3 words (`writes`, `polls 30s`, `emits OrderCreated`) | `--max-arrow-words` |
| Free notes | ≤ 2, ≤ 12 words each, placed beside the element they explain | `--max-note-words` |
| Total words | ≤ 40; sentences go in the caption or surrounding prose | `--max-words` |
| Colors with meaning | ≤ 5 plus gray; one accent on the 1–2 elements the claim is about | `--max-colors` |
| Edge crossings | 0 | none |

Raise a limit only when the brief says why. A field-list diagram that must show every field is a valid reason.

## 4. Lay it out from a spec

For any boxes-and-arrows diagram, write a graph spec and let ELK place it. One-time setup: `npm install --prefix <skill>/scripts`.

```json
{
  "direction": "RIGHT",
  "nodes": [
    {"id": "api", "label": "API handler", "sub": "src/api/orders.ts", "change": "context"},
    {"id": "q", "label": "RetryQueue", "sub": "src/queue/retry.ts", "change": "added"},
    {"id": "db", "label": "Postgres", "change": "context"}
  ],
  "edges": [
    {"from": "api", "to": "q", "label": "enqueues", "change": "added"},
    {"from": "q", "to": "db", "label": "writes", "change": "added"},
    {"from": "api", "to": "db", "label": "writes", "change": "removed"}
  ],
  "groups": [{"id": "svc", "label": "orders service", "members": ["api", "q"]}]
}
```

```bash
node <skill>/scripts/layout.mjs spec.json | npx -y mcp-excalidraw-server@2.1.2 add
```

The header of `scripts/layout.mjs` lists every spec field. Use `"direction": "RIGHT"` for flows and pipelines, and `"DOWN"` for layers. Use `"origin": [x, y]` to place a diagram on a shared canvas. Use a group only for a real boundary: a process, a package, a trust zone.

To change the diagram, edit the spec. Delete the old elements (`query --bbox x0,y0,x1,y1`, then `delete` those ids), and rerun. ELK is deterministic, so an unchanged graph keeps its positions.

Place coordinates by hand only for shapes ELK cannot express, such as a sequence diagram, a merkle tree, or a field layout inside a box. Then keep the **spine**: the main path on one straight axis, with side branches above or below it.

Done when: the diagram is on the canvas.

## 5. Lint, render, critique

1. Run `python3 <skill>/scripts/lint_diagram.py scene.excalidraw`, or pipe `export` into it with `-`. On a shared canvas, add `--box x0,y0,x1,y1`. Fix every FAIL, then rerun.
2. Render with `screenshot --scale 2 --out view.png`, and view the image.
3. Write the critique, three lines:
   - **Squint:** what the eye lands on first. It should be the claim's subject.
   - **Remove:** one node, arrow, or word that can go. Remove it, or say why it stays.
   - **Claim:** restate the claim from the picture alone. It should match the brief.
4. Check hygiene in the same image: no clipped text, no overlaps, no label on a line, ≥ 40px between shapes.

Fix, then repeat from step 1.

Done when: lint passes, and all three critique lines match the brief.

## 6. Code-change diagrams

Draw the change inside its unchanged neighbors, in one layout. Set `change` on nodes and edges in the spec:

| `change` | Look |
|---|---|
| `added` | green stroke, green fill |
| `changed` | amber stroke, amber fill |
| `removed` | red dashed stroke, no fill |
| `context` | gray stroke, no fill |

Put the file path in `sub` on each changed node. Put the one-sentence claim above the figure. Keep detail that exists only in the lines (a condition, an off-by-one, a regex) in the diff.

## Style

- Square corners on every box. Omit `roundness`.
- Color families and textures for domain diagrams: `../slide-deck/references/style-system.md`. Code-change diagrams use only the section 6 palette.
- Add a legend only when an encoding repeats and its meaning is not written on the mark itself.
