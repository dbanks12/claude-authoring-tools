#!/usr/bin/env python3
"""Build <deck>/<deck-dirname>.html from <deck>/slides.md + <deck>/figures/.

Usage: python3 build.py [DECK_DIR]   (default: the current directory)

The theme comes from this directory's template.html unless the deck has its own
template.html. The page <title> is the first slide's title. The slides.md syntax
reference lives in SYNTAX_HEADER below; build.py keeps it present and current as a
comment at the top of slides.md.
"""
import base64
import html as H
import re
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent
DECK = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

SYNTAX_HEADER = """<!-- slides.md syntax (this block is maintained by build.py; edits to it are overwritten)
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
-->"""
OUT = DECK / f"{DECK.name}.html"


def inline(s: str) -> str:
    s = H.escape(s, quote=False)
    s = s.replace("-&gt;", "→").replace("->", "→")
    s = re.sub(r"!!(.+?)!!", r'<span class="kicker">\1</span>', s)
    s = re.sub(r"\{(red|green): (.+?)\}", r'<span class="\1">\2</span>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"(?<![\w_])_([^_]+)_(?![\w_])", r"<em>\1</em>", s)
    return s


def fig_tag(spec: str) -> str:
    """spec is "name" (fill the slide), "name natural" (capped natural size) or "name mega" (full height)."""
    name, _, mode = spec.partition(" ")
    cls = {"natural": "fig", "mega": "fig fill mega"}.get(mode.strip(), "fig fill")
    data = base64.b64encode((DECK / "figures" / f"fig-{name}.png").read_bytes()).decode()
    return f'<figure class="{cls}"><img src="data:image/png;base64,{data}" alt="{name} diagram"></figure>'


def nested_items(items: list[tuple[int, str]]) -> str:
    """<li> markup for (depth, html) items; a deeper item nests inside the one above it."""
    out, depth = "", 0
    for i, (d, x) in enumerate(items):
        d = min(d, depth + 1)
        if i and d > depth:
            out += "<ul>" * (d - depth)
        elif i:
            out += "</li>" + "</ul></li>" * (depth - d)
        out += f"<li>{x}"
        depth = d
    return out + "</li>" + "</ul></li>" * depth


def render_slide(block: str, num: int, total: int, first: bool, default_bullets: str = "",
                 default_titles: str = "center") -> str:
    title = sub = None
    body: list[str] = []
    lis: list[tuple[int, str]] = []  # (depth, html)
    indents = [0]  # indent width of each open nesting level
    lis_class = ""
    default_lis_class = default_bullets
    titles = default_titles
    cards: list[str] = []
    columns: list[list[str]] = []  # finished columns when the slide uses "||" splits

    def flush_lists():
        nonlocal lis, cards
        if lis:
            cls = f' class="{lis_class}"' if lis_class else ""
            body.append(f"<ul{cls}>" + nested_items(lis) + "</ul>")
            lis = []
        if cards:
            body.append('<div class="cols">' + "".join(cards) + "</div>")
            cards = []

    for line in block.strip().splitlines():
        line = line.rstrip()
        if not line:
            continue
        if line.strip() == "||":
            flush_lists()
            columns.append(body)
            body = []
        elif line.startswith("## "):
            sub = inline(line[3:])
        elif line.startswith("# "):
            title = inline(line[2:])
        elif line.startswith("fig: "):
            flush_lists()
            body.append(fig_tag(line[5:].strip()))
        elif line.startswith("titles: "):
            titles = "top" if line[8:].strip() == "top" else "center"
        elif line.startswith("bullets: "):
            default_lis_class = "plain" if line[9:].strip() == "plain" else ""
        elif lis and line[0] in " \t" and line.lstrip()[:2] in ("- ", "* "):
            indent = len(line) - len(line.lstrip())
            if indent > indents[-1]:
                indents.append(indent)
            while indent < indents[-1]:
                indents.pop()
            lis.append((len(indents) - 1, inline(line.lstrip()[2:])))
        elif line.startswith("- ") or line.startswith("* "):
            cls = "plain" if line.startswith("* ") else default_lis_class
            if lis and cls != lis_class:
                flush_lists()
            lis_class = cls
            indents[:] = [0]
            lis.append((0, inline(line[2:])))
        elif line.startswith(":: "):
            t, _, b = line[3:].partition(" :: ")
            cards.append(f'<div class="card"><h3>{inline(t)}</h3><p>{inline(b)}</p></div>')
        elif line.startswith("~ "):
            flush_lists()
            body.append(f'<p class="muted">{inline(line[2:])}</p>')
        else:
            flush_lists()
            body.append(f"<p>{inline(line)}</p>")
    flush_lists()
    # mega figures need the full slide height: allowed in the last split column or on a title-less slide
    MEGA = 'class="fig fill mega"'
    mega_ok = (columns and any(MEGA in x for x in body)) or (not columns and title is None)
    for group in columns + [body]:
        for i, x in enumerate(group):
            if MEGA in x and not (mega_ok and group is body):
                print(f"slide {num}: 'mega' needs the right column of a split or no title; using fill",
                      file=sys.stderr)
                group[i] = x.replace(MEGA, 'class="fig fill"')
    mega = any(MEGA in x for x in body)

    if columns:
        cols = columns + [body]
        if mega and title is not None:  # the title joins the left column so the figure can reach the top
            tag = "h1" if first else "h2"
            cols[0] = [f'<{tag} class="title">{title}</{tag}>'] + ([f'<p class="sub">{sub}</p>'] if sub else []) + cols[0]
            title = sub = None
        if sub:  # the subtitle heads the first column, so other columns start right under the title
            cols[0] = [f'<p class="sub">{sub}</p>'] + cols[0]
            sub = None
        # a column holding only a filling figure gets twice the width of a text column
        widths = " ".join("minmax(0,2fr)" if c and all('class="fig fill' in x for x in c) else "minmax(0,1fr)"
                          for c in cols)
        body = [f'<div class="split" style="grid-template-columns:{widths}">'
                + "".join(f'<div class="col">{"".join(c)}</div>' for c in cols) + "</div>"]

    tag = "h1" if first else "h2"
    style = ' style="font-size:clamp(48px,7vw,84px)"' if first else ""
    wide = " wide" if columns else ""
    fill = " hasfill" if any('class="fig fill' in b for b in body) else ""
    fill += " hasmega" if mega else ""
    fill += " top" if titles == "top" else ""
    parts = [f'<section class="slide{fill}"><span class="num">{num} / {total}</span><div class="inner{wide}">']
    if title is not None:
        parts.append(f'<{tag} class="title"{style}>{title}</{tag}>')
    if sub:
        parts.append(f'<p class="sub">{sub}</p>')
    parts.extend(body)
    parts.append("</div></section>")
    return "\n  ".join(parts)


STYLE_AND_SCRIPT_SRC = DECK / "template.html" if (DECK / "template.html").exists() else TOOL / "template.html"


def main() -> None:
    tpl = STYLE_AND_SCRIPT_SRC.read_text()
    src_path = DECK / "slides.md"
    text = src_path.read_text()
    m = re.match(r"\s*<!--.*?-->\n?", text, re.S)
    content = text[m.end() :] if m else text
    if not m or m.group(0).strip() != SYNTAX_HEADER.strip():
        src_path.write_text(SYNTAX_HEADER + "\n\n" + content.lstrip("\n"))
        content = src_path.read_text()[len(SYNTAX_HEADER) + 2 :]
        print("refreshed syntax header in slides.md")
    # file-wide settings: "bullets: ..." and "titles: ..." lines before the first slide
    default_bullets, default_titles = "", "center"
    while m := re.match(r"\s*(bullets|titles): *(\S*) *\n", content):
        if m.group(1) == "bullets":
            default_bullets = "plain" if m.group(2) == "plain" else ""
        else:
            default_titles = "top" if m.group(2) == "top" else "center"
        content = content[m.end():]
    blocks = re.split(r"^---$", content, flags=re.M)
    total = len(blocks)
    slides = "\n\n".join(render_slide(b, i + 1, total, i == 0, default_bullets, default_titles) for i, b in enumerate(blocks))
    first_title = re.search(r"(?m)^# (.+)$", content)
    page_title = H.escape(re.sub(r"[*`!{}]|red: |green: ", "", first_title.group(1)) if first_title else DECK.name)
    tpl = re.sub(r"<title>.*?</title>", f"<title>{page_title}</title>", tpl, count=1)
    OUT.write_text(tpl.replace("<!--SLIDES-->", slides))
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes, {total} slides)")


if __name__ == "__main__":
    main()
