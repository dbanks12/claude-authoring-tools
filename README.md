# claude-authoring-tools

Personal Claude Code skills and scripts for building presentations and diagrams.

## Contents

- `skills/slide-deck/` - skill for distilling a design doc into a minimal HTML slide deck
  (lavender theme) with an Excalidraw helper canvas. Includes the deck build tooling:
  - `assets/build.py DECK` - assembles `DECK/<dirname>.html` from a human-editable `slides.md`
    plus `figures/*.png` (inlined as base64 data URIs). Maintains a syntax-reference comment at
    the top of `slides.md`; that header is the full syntax reference.
  - `assets/pdf.py DECK` - renders the HTML to a 16:9 PDF, one slide per page (headless Chromium).
  - `assets/watch.py DECK` - rebuilds HTML and PDF on every save. `assets/ci-build.sh DECK` - one CI-style build.
  - `assets/draw.py`, `assets/trim.py` - write canvas diagrams as code; trim rendered figures.
  - `assets/template.html` - the deck chrome: theme tokens (light + dark) and the JS
    whole-slide settle navigation.
- `skills/excalidraw-skill/` - diagram skill, a submodule of the public
  [dbanks12/excalidraw-skill](https://github.com/dbanks12/excalidraw-skill) repo. Edit it there,
  then commit the new submodule pointer here.
- `examples/demo-deck/` - a deck that uses every slides.md feature, with its diagram drawn as code.
  CI (`.github/workflows/example-deck.yml`) builds it to HTML and PDF and attaches both to the
  `example-latest` release.

## Using the tooling from a deck repo

Keep each deck in its own private repo with this repo as a `slidegen/` submodule. Copy the CI
workflow from `skills/slide-deck/ci/deck.yml`. Step-by-step setup, including the read-only deploy
key CI needs, is in [`skills/slide-deck/README-ci.md`](skills/slide-deck/README-ci.md).

Local loop: `python3 slidegen/skills/slide-deck/assets/watch.py .` rebuilds the HTML and PDF on
every save.

## Runtime dependency: the Excalidraw canvas server

The excalidraw skill drives a live canvas via the `mcp-excalidraw-server` npm package
(CLI: `npx -y mcp-excalidraw-server <command>`; it can also be registered as an MCP server).
The canvas serves at `http://127.0.0.1:3000`. Since 2.1, screenshots and exports render headless;
open the page only to watch or edit. Diagram crops are produced with Pillow
(`pip install --user --break-system-packages pillow`).

## Installing the skills

Fetch the excalidraw-skill submodule, then symlink each skill directory so this repo stays the single source of truth:

    git submodule update --init

    # Claude Code
    ln -s $(pwd)/skills/slide-deck $(pwd)/skills/excalidraw-skill ~/.claude/skills/
    # Codex (same SKILL.md format, native support)
    ln -s $(pwd)/skills/slide-deck $(pwd)/skills/excalidraw-skill ~/.codex/skills/

For Codex also register the canvas MCP server (optional, the CLI works without it):

    codex mcp add excalidraw -- npx -y mcp-excalidraw-server

Agent-specific adaptations live in `AGENTS.md` (which `CLAUDE.md` symlinks to).
