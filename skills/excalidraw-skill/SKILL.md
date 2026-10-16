---
name: excalidraw-skill
description: Excalidraw diagrams that explain code, code changes, designs, and concepts, drawn on a live canvas. Use when an agent needs to (1) draw or lay out a diagram, (2) refine one by rendering and critiquing its own work, (3) export/import .excalidraw files or PNG/SVG images, (4) save/restore canvas snapshots, (5) convert Mermaid to Excalidraw, or (6) perform element-level CRUD, alignment, grouping, or locking. Drives the mcp-excalidraw-server CLI, which auto-starts the canvas server; MCP tools and a REST API are equivalent alternatives.
---

# Excalidraw diagrams

A diagram earns its place when a cold reader sees a mechanism faster than prose could tell it: where data flows, what a change adds or removes, which parts talk. Every step below serves one **claim**, the sentence the picture must prove.

Canvas mechanics (CLI, element format, arrows, snapshots, file I/O, errors) live in `references/mechanics.md`. Read it before the first canvas command in a session. Use `npx -y mcp-excalidraw-server@2.1.2` or later; screenshots and `render` work headless, with no browser tab.

## 1. Decide what to draw

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
| What should I do in my case? | Decision tree: questions as diamonds or boxes, answers on the arrows |

Then pick the scope:

- **Overview plus deep dive** for architecture, design, state, data-flow, and concept requests. The **overview** shows the whole idea in at most 7 boxes, readable in five seconds. The **deep dive** sits to its right and adds the parts, groups, and rules a person needs to work on it. Reuse the overview's names, colors, and relative positions in the deep dive, so the reader carries one map into the other.
- **One diagram** for a code change, a sequence, or a decision tree.
- **A sentence instead** when the claim has no spatial relationship (a rename, a list, a one-line fix, a regex).

Done when: you named a type and a scope.

## 2. Write the brief

Write four lines before any canvas command, and show them to the user with the result:

```text
Reader:   reviewer of PR #412, knows the service, not this module
Question: what does the retry queue change about write ordering?
Claim:    writes now pass through RetryQueue, so a failed write retries after newer writes.
Type:     code change, one diagram
```

Read the code first. Use the names the code uses, and draw only parts that exist.

Done when: the claim is one sentence that names what the picture shows.

## 3. Compose the drawing

Every drawing has these parts:

- **A title** at the top left, fontSize 28: the subject and scope, such as "Standup jobs: task_attempt lifecycle".
- **Color with meaning.** Color by kind, layer, or outcome: success green, failure red, waiting or external gray, the claim's subject in the accent. Color families: `../slide-deck/references/style-system.md`. A drawing in one gray says nothing with color.
- **Short box labels.** A name of at most 4 words, plus an optional second line with a file path or type.
- **Labeled arrows** that say what moves or happens (`claims`, `error, timeout`, `emits OrderCreated`). Leave an arrow unlabeled only when the label adds nothing, such as a parent link in a commit graph.
- **One rules panel** in a deep dive, for the detail that does not fit on a mark: invariants, timeouts, edge cases. Draw it as a dashed rectangle with a free text title ("Rules") and short bullet lines, below or beside the picture.
- **Dotted groups** for real boundaries (a process, a package, a trust zone), so the reader sees the high level and the parts at once.
- **A compact shape.** Aim for 4:3 to 16:9. Lint fails a panel wider than 3:1. Wrap a long flow into two rows, or switch to top-down.

Sizes: at most 7 boxes in an overview, at most 15 in a deep dive. Split above that.

## 4. Place the shapes

**ELK layout** suits pipelines, data flows, and long chains. Write a graph spec, and `layout.mjs` places it. One-time setup: `npm install --prefix <skill>/scripts`.

```json
{
  "title": "Orders: writes now go through RetryQueue",
  "direction": "RIGHT",
  "nodes": [
    {"id": "api", "label": "API handler", "sub": "src/api/orders.ts", "change": "context"},
    {"id": "q", "label": "RetryQueue", "sub": "src/queue/retry.ts", "change": "added"},
    {"id": "db", "label": "Postgres", "fam": "blue"}
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

The header of `scripts/layout.mjs` lists every field. Nodes and edges take a color family in `fam`. Back edges (a retry, a reply) bend the whole layout, so draw a retry as a separate "next attempt" node or place that diagram by hand.

**Hand placement** suits hub architectures, state machines, sequences, comparisons, and trees. Lay out a grid first:

- Put the hub or the main path in the middle row, and the start at the left.
- Leave 80–120px between boxes, and 130px or more where an arrow carries a 3-word label.
- Sequence: lanes 220px apart, lifelines as dashed lines, one message every 60px, each label just above its arrow.
- Set `"roundness": {"type": 3, "value": 0}` on every rectangle. An omitted roundness exports rounded.
- Give a free text element `"textAlign": "left", "verticalAlign": "top"`.

On a shared canvas, give every id a per-diagram prefix (`optA-api`). A repeated id replaces the earlier element. Apply style-system textures after layout with `update <id> --set '{"fillStyle": "cross-hatch"}'`.

Done when: the drawing is on the canvas.

## 5. Lint, render, critique

1. Export the scene, then run `python3 <skill>/scripts/lint_diagram.py scene.excalidraw`. Lint each panel of an overview plus deep dive with `--box x0,y0,x1,y1`. Fix every FAIL, then rerun.
2. Render the exported file: `timeout 120 npx -y mcp-excalidraw-server@2.1.2 render scene.excalidraw --scale 2 --out view-N.png`. Use a new file name for each render, so you never view a stale image. View it.
3. Write the critique, three lines:
   - **Squint:** what the eye lands on first. It should be the claim's subject.
   - **Remove:** one box, arrow, or word that can go. Remove it, or say why it stays.
   - **Claim:** restate the claim from the picture alone. It should match the brief.
4. Check hygiene in the same image: no clipped or wrapped label, no overlap, no label on a line or arrowhead.

Fix, then repeat from step 1.

Done when: lint passes, and all three critique lines match the brief.

## 6. Code-change diagrams

Draw the change inside its unchanged neighbors, in one layout. Set `change` on nodes and edges:

| `change` | Look |
|---|---|
| `added` | green stroke, green fill |
| `changed` | amber stroke, amber fill |
| `removed` | red dashed stroke, no fill |
| `context` | gray stroke, no fill |

Put the file path in `sub` on changed nodes, or in the group label when every node shares one file. Put the one-sentence claim in the title. Keep detail that exists only in the lines (a condition, an off-by-one, a regex) in the diff.

## Canvas gotchas

- **Own canvas:** set `PORT=<p> EXPRESS_SERVER_URL=http://127.0.0.1:<p>` on every command to run a private canvas. The default port 3000 is often the user's live canvas.
- **Glyphs:** the hand font lacks `→`, `≤`, `§`, `•`, and subscripts. These fall back to another font. Write `->`, `<=`, `-`, and `n1`.
- **Arrows:** a bound arrow (`startElementId`/`endElementId`) ignores `points` and runs straight. Use an unbound arrow for a routed path.
- **Patches:** `apply` runs deletes after creates. Do not delete and recreate one id in a single patch.
- **Deletes:** deleting a shape leaves its bound arrows. Delete them too.
