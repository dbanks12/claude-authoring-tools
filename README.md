# claude-authoring-tools

Personal Claude Code skills and scripts for building presentations and diagrams.

## Contents

- `skills/slide-deck/` - skill for distilling a design doc into a minimal HTML slide deck
  (Aztec all-hands theme) with an Excalidraw helper canvas. Includes the deck build tooling:
  - `assets/build.py` - assembles `<dirname>.html` from a human-editable `slides.md` plus
    `figures/*.png` (inlined as base64 data URIs). Maintains a syntax-reference comment at
    the top of `slides.md`. Markdown-lite syntax is documented in the SKILL.md and that header.
  - `assets/template.html` - the deck chrome: theme tokens (light + dark), the lavender
    chevron brand strip, and the JS whole-slide settle navigation.
- `skills/excalidraw-skill/` - canvas workflow skill (drawing, iterating, cropping, exporting).

## Runtime dependency: the Excalidraw canvas server

The excalidraw skill drives a live canvas via the `mcp-excalidraw-server` npm package
(CLI: `npx -y mcp-excalidraw-server <command>`; it can also be registered as an MCP server).
The canvas serves at `http://127.0.0.1:3000`; screenshots/exports need that page open in a
browser tab. Diagram crops are produced with Pillow
(`pip install --user --break-system-packages pillow`).

## Installing the skills

Copy (or symlink) each skill directory into `~/.claude/skills/` so Claude Code picks them up:

    cp -r skills/slide-deck skills/excalidraw-skill ~/.claude/skills/
