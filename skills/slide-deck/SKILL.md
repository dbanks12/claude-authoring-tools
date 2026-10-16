---
name: slide-deck
description: Build an HTML slide deck (Aztec-styled) from a design doc or topic, with an Excalidraw helper canvas whose diagrams are cropped and inlined into the slides. Use when the user asks for presentation slides, a deck, or "distill X into slides".
---

# Slide deck builder

Distill a document or topic into a minimal HTML slide deck plus an Excalidraw helper canvas, then inline cropped diagrams into the slides. Follow the structure and theme below; both came from iterating with the user and are deliberate.

## Source-file workflow (do this, never hand-edit HTML)

The deck is generated, not authored, so the user always has a human-readable file to edit. A deck directory (e.g. `~/<name>-deck/`, ideally its own private repo) holds only content:

- `slides.md` - the single source of truth the user edits
- `figures/fig-<name>.png` - the diagram crops as plain files
- `canvas/` - optional: the `.excalidraw` file and a `diagrams.py` that draws the diagrams as code with `assets/draw.py`
- `slidegen/` - this tool repo as a git submodule (in a repo) - never copy the scripts into the deck

The scripts in `assets/` take the deck directory as their argument (default: the current directory):

- `build.py DECK` assembles `DECK/<dirname>.html` with figures inlined as data URIs; publish that output as the artifact (pass `url:` to keep an existing artifact URL when the output path changes)
- `pdf.py DECK` renders that HTML to a 16:9 PDF, one slide per page (headless Chromium)
- `watch.py DECK` rebuilds both on every save; `ci-build.sh DECK` is one build exactly as CI runs it
- `trim.py FIGURES_DIR [names]` trims figure PNGs to their ink after `render_figures.py`

CI and releases for deck repos: follow `README-ci.md` (submodule, workflow template in `ci/deck.yml`, read-only deploy key). `examples/demo-deck` in this repo shows every slides.md feature and runs the same pipeline.

Without an Artifact tool (Codex, for example), skip every publish step and open `<deck>.html` locally. Without a session scratchpad, use a deck-local `tmp/`. The canvas works through the CLI or the MCP tools; see the excalidraw-skill.

`slides.md` format, one slide per `---`-separated block. The full, current reference is `SYNTAX_HEADER` in `assets/build.py`, which build.py also keeps as a comment at the top of every slides.md. It adds file-wide settings (`bullets: plain`, `titles: top`), sub-bullets, `{red: }`/`{green: }` text, `||` column splits, and figure modes (`fig: name` fills the slide, `natural`, `mega`). The basics:

```
# Title                slide title (first slide renders extra large)
## Subtitle            optional
fig: name              embeds figures/fig-<name>.png at that position (anywhere in the slide, several allowed)
- bullet               list row (separated lines); **bold**, *em*, `code`, !!kicker!! inline
* bullet               regular disc bullet; NOTE markdown formatters rewrite * to -, so prefer:
bullets: plain         switches all "- " lists on this slide to regular disc bullets
:: Title :: body       card in a grid
~ text                 muted paragraph
plain text             paragraph; -> becomes a right arrow
```

After any canvas edit: re-crop into `figures/`, rebuild, republish. After any user edit to `slides.md`: rebuild, republish. The template carries the whole theme and the settle-navigation script. A deck may override it with its own `template.html`; improvements that should apply to all decks belong in `assets/template.html` here. The page `<title>` comes from the first slide.

## Deck structure

- One idea per slide. A slide is: big accent-colored **title**, a short bold **subtitle** underneath, then at most 4-5 short lines (borderless list rows) or a small card grid. No walls of text.
- The title is the section name (e.g. "Assumptions", "Core idea", "Withdrawal"), NOT a clever headline. The clever/summary line goes in the subtitle. Titles are large and accent-colored so the deck can be skimmed by title alone.
- Use plain product terms in prose ("enclave" not "TEE"); keep code identifiers verbatim in `code` spans (`registerTee`, `teeNotes`).
- Do not cite the source file path on slides.
- Prefer concrete named examples where they help ("User deposits 100 DAI", "spends A, creates B"), but actor cards stay generic ("User", not Alice/Bob).
- Scroll-snap vertical deck: each `section.slide` is `min-height:100vh; scroll-snap-align:start`, slide counter `N / total` top-right in monospace, arrow-key plus j/k navigation via a small script. Do NOT use CSS scroll-snap (mandatory jumps wildly on slides taller than the viewport; proximity lets extension-driven small scrolls strand mid-slide). Instead let JS own settling: track a `settled` index, keydown (capture phase, preventDefault + stopPropagation) moves it by one, and a debounced scroll listener (~160ms) settles ANY scroll to whole slides: nearest slide by `offsetTop` if it changed, else a >40px nudge in a direction advances one slide. This makes vim-extension j/k (which the page cannot intercept) still land on slide boundaries. Never compute position as `scrollY / innerHeight`.
- Never use em dashes anywhere in the copy. No semicolons in slide copy either, split into two sentences or use commas. Short active sentences.

## Helper canvas (Excalidraw)

Build ONE mega canvas as an auxiliary/navigation resource, separate from the deck:

- Stack diagrams vertically with generous gaps (~150px+). Each diagram gets a large plain-text label (fontSize 36, uppercase) in a left margin column so zooming out reads as a table of contents. No numbering on the labels, and no abbreviations: write full words (ENCLAVE REGISTRATION, SIGNATURE STRUCTURE, L1 SIGNATURE VERIFICATION), never shorthand like SIG, I/O, or REG. Break long labels across lines rather than shortening them.
- Keep each diagram to 3-8 boxes. Styling follows the two-axis system in `references/style-system.md` (hue = domain family, texture = kind of thing): solid tint fill = concrete data, cross-hatch fill with solid stroke = hash/commitment (nullifiers are red cross-hatch plus the crack glyph), hachure + dashed = elided filler only, dotted stroke = conceptual groupings (zones, phases, bundles, tree frames), zigzag fill = secrets. Dashed is NEVER used for hashes or data.
- Make diagrams self-explanatory: put checklists and conditions INSIDE the picture (dotted sub-box under the actor) rather than as caption text below.
- Box sizing: the hand-drawn font runs ~6.8px per character at fontSize 10, wider than intuition. NEVER hardcode a parent box width from mental arithmetic: compute it as sum of measured child widths plus gaps plus 16px side margins, and leave at least 12px of right padding after the last child (excalidraw's rough strokes overshoot corners, so a flush fit reads as overflow). After any layout pass, query actual child extents and verify last_child_end + 12 <= parent_end, widening the parent (recentered if it anchors a vertical link) when it fails.
- Connectors: since `mcp-excalidraw-server` 2.1.1, CLI-written arrows survive an open browser tab. Bound arrows follow moved boxes, and unbound arrows keep their bend points (tested 2026-10-16 on 2.1.2). Draw new diagrams with the excalidraw-skill `place.py` helper, or with bound arrows. Canvases already drawn with connector lines keep using `assets/arrow_doctor.py`: `--fix` after any box move or batch edit, `--check` before cropping. Its routing: horizontal pairs meet at the shorter box's midline, vertical pairs run edge-center to edge-center (angled, correct for trees). Process labels are free text placed at connector midpoint + 14px right, recomputed after every re-route.
- Corner style is a per-canvas-set choice and must be coherent across the whole set: the current canvases use SQUARE corners (no `roundness`) on every rectangle. Do not introduce rounded boxes into a square-cornered set or vice versa.
- Bound labels ignore a `fontSize` passed on the rectangle and default to 20; after creating small labeled boxes, query the bound text elements and set their fontSize explicitly.
- Newly created standalone text elements may default to `textAlign: center` / `verticalAlign: middle`, which the browser tab renders displaced from the intended left-anchored position. Always set `"textAlign": "left", "verticalAlign": "top"` explicitly when creating free text, and if a fresh diagram renders with text drifting off its boxes, patch those two fields on every standalone text and re-render.
- Snapshot (`snapshot save`) before destructive canvas changes; export `.excalidraw` + `.png` to the scratchpad after every change.

## Inlining diagrams into slides

Artifact CSP blocks external images, so crops must be data URIs:

1. `screenshot --out full.png` the canvas.
2. Compute the canvas→pixel mapping: get the scene bbox from `export` (min/max over element x/y/width/height), then solve padding `p = (W*bh - H*bw) / (2*(H - W))` and scale `s = W/(bw + 2p)` from the PNG dimensions.
3. Crop each diagram region EXCLUDING the left nav labels (the slide already has a title), with Pillow (`pip install --user --break-system-packages pillow` if missing).
4. Embed as `<figure class="fig"><img src="data:image/png;base64,...">` with `max-height:34vh; object-fit:contain` so no slide overflows. Keep the figure card white in both themes (the PNGs have white grounds).
5. Crops are snapshots: after any canvas edit, re-crop and republish. Keep the crop boxes scripted.

## Theme (Aztec all-hands)

Extracted from the company deck (`ppt/theme/theme1.xml` of an Aztec .pptx). Font is Arial everywhere; monospace only for slide numbers and code.

Light: bg `#e8e7ea` (light grey), ink `#121118`, accent (titles, code, card headings) periwinkle `#6f5fd8` (theme `#8D7DFF` deepened for contrast), orange pop `#d05a2e` (theme `#ED7A4F` deepened) for the one emphasized phrase per slide; list lead-ins are plain bold ink, never a colored accent, line `#cfccd8`, card `#f7f6f9`.

Dark: bg `#16151b`, ink `#eceaf2`, accent `#B0A6FF`, pop `#ED7A4F`, line `#363344`, card `#1f1e26`. Do not use the theme's green as a text accent (David dislikes it); it stays only in the Excalidraw color language for success/L2 boxes.

Brand mark: the lavender double-chevron (two rounded `<` strokes) right-anchored on every slide, as an inline SVG data-URI background (`#d8d3ef` light / `#232030` dark). Confine it to a `.slide::before` strip of the rightmost ~60% of the screen (`width:60%; background-size:cover; background-position:left center; pointer-events:none`, content above via z-index); it must never intrude further than ~60% into the slide. Soft-rounded (10px) cards.

Theme the CSS token-level for all three viewer states: full light palette on bare `:root`; dark overrides under `@media (prefers-color-scheme: dark)` guarded `:root:not([data-theme="light"])`; repeated under `:root[data-theme="dark"]`. Body background always from a token.

## Iteration protocol

Screenshot after every canvas batch and actually look at it: check label wrapping in small boxes (bound labels default to fontSize 20; set the bound text element's fontSize explicitly), caption/box collisions, and that Unicode subscripts are NOT used (the hand-drawn font lacks the glyphs; use plain digits n1, n2). Republish the artifact to the same URL by re-publishing the same file path.
