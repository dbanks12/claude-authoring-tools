# Agent guide

This repo is agent-neutral. The single source of truth for how to build slide decks and
drive the Excalidraw canvas is the two skill documents. Do not duplicate their content;
read and follow them directly:

- `skills/slide-deck/SKILL.md` - deck structure, slides.md source format, build workflow,
  theme, canvas conventions, crop pipeline, and hard-won gotchas (arrows, bound labels).
- `skills/excalidraw-skill/SKILL.md` - what to draw, composition, placement, lint, and critique.
  Its `references/mechanics.md` covers canvas interfaces and the element format.

## Adaptations for non-Claude agents (Codex etc.)

- **No Skill tool**: where the docs say a skill is "invoked", just read the file and follow it.
- **Canvas access**: the CLI is the universal interface and needs no setup:
  `npx -y mcp-excalidraw-server <command>`. Optionally register the MCP server instead
  (Codex `~/.codex/config.toml`):

      [mcp_servers.excalidraw]
      command = "npx"
      args = ["-y", "mcp-excalidraw-server"]

  Ignore `mcp__excalidraw__*` tool names in the docs; every operation has a 1:1 CLI command.
- **No Artifact tool**: skip any "publish/republish the artifact" step. The built deck is a
  single self-contained HTML file; open it locally or serve it statically.
- **Paths**: where the docs mention a session scratchpad, use a repo-local `tmp/` instead.

## Claude Code

Claude Code loads these skills from `~/.claude/skills/` (see README for the install copy)
and additionally publishes built decks as claude.ai artifacts.
