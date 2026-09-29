<!-- slides.md syntax (this block is maintained by build.py; edits to it are overwritten)
- slides are separated by lines containing only ---
- "# Title": slide title (first slide renders extra large)
- "## Subtitle": optional subtitle
- "fig: name": embeds figures/fig-<name>.png at that position, filling the rest of the slide (width or height, whichever runs out first)
- "fig: name natural": the same figure at its capped natural size instead of filling the slide
- "fig: name mega": fills the full slide height, flush to the top, bottom and right edges; only in the right column of a "||" split (the title moves into the left column) or on a slide with no "#" title
- "- bullet": list row with separator lines; inline: **bold**, *em*, `code`, !!kicker!!
- "  - sub-bullet": indented under the bullet above it; deeper indents nest further
- "* bullet": regular disc bullet. NOTE: markdown formatters rewrite * to -, so prefer:
- "bullets: plain": switches all "- " lists on this slide to regular disc bullets
- "bullets: plain" at the top of the file, before the first slide: makes it the default for every slide
- "titles: top": title block at the top-left of the slide, so titles line up across slides; "titles: center" (default) centers the slide content vertically. Put it before the first slide for the whole file, or inside a slide for that slide only
- inline emphasis: *em* or _em_ both work
- inline "{red: text}" or "{green: text}": colored text (works around **bold** too)
- ":: Title :: body": card in a grid
- "~ text": muted footnote paragraph
- "||" on its own line: vertical split; content above goes in the left column, below in the right (more "||" lines add columns)
- plain text: paragraph; -> becomes a right arrow
-->

bullets: plain
titles: top

# Demo deck
## A slides.md that shows every feature
titles: center

---

# Bullets
## Plain disc bullets, set once for the whole file

- A top-level bullet with **bold**, *em* and `code`
- {red: **Red emphasis**} for the problem
- {green: **Green emphasis**} for the fix
    - An indented sub-bullet
- !!Kicker!! emphasis in the theme's orange

---

# Split with a figure
## Text left, figure right

- `||` on its own line starts the next column
- A column with only a figure gets twice the width
- The figure fills the column
||
fig: flow

---

# Mega figure
## Right column, flush to the edges

- The title moves into the left column
- The figure runs the full slide height
||
fig: flow mega

---

# Natural size
## The figure keeps its capped natural size

fig: flow natural

---

# Cards
## A small grid

:: Build :: `build.py` turns slides.md into one self-contained HTML file
:: Print :: `pdf.py` renders that file to a 16:9 PDF
:: Watch :: `watch.py` rebuilds both on every save

~ Muted footnote text.
