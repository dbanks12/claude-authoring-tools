#!/usr/bin/env python3
"""Build <dirname>.html from slides.md + figures/.

The slides.md syntax reference lives in SYNTAX_HEADER below; build.py keeps it
present and current as a comment at the top of slides.md.
"""
import base64
import html as H
import re
from pathlib import Path

ROOT = Path(__file__).parent

SYNTAX_HEADER = """<!-- slides.md syntax (this block is maintained by build.py; edits to it are overwritten)
- slides are separated by lines containing only ---
- "# Title": slide title (first slide renders extra large)
- "## Subtitle": optional subtitle
- "fig: name": embeds figures/fig-<name>.png at that position (before, between, or after content; several per slide allowed)
- "- bullet": list row with separator lines; inline: **bold**, *em*, `code`, !!kicker!!
- "* bullet": regular disc bullet. NOTE: markdown formatters rewrite * to -, so prefer:
- "bullets: plain": switches all "- " lists on this slide to regular disc bullets
- inline emphasis: *em* or _em_ both work
- ":: Title :: body": card in a grid
- "~ text": muted footnote paragraph
- plain text: paragraph; -> becomes a right arrow
-->"""
OUT = ROOT / f"{ROOT.resolve().name}.html"


def inline(s: str) -> str:
    s = H.escape(s, quote=False)
    s = s.replace("-&gt;", "→").replace("->", "→")
    s = re.sub(r"!!(.+?)!!", r'<span class="kicker">\1</span>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"(?<![\w_])_([^_]+)_(?![\w_])", r"<em>\1</em>", s)
    return s


def fig_tag(name: str) -> str:
    data = base64.b64encode((ROOT / "figures" / f"fig-{name}.png").read_bytes()).decode()
    return f'<figure class="fig"><img src="data:image/png;base64,{data}" alt="{name} diagram"></figure>'


def render_slide(block: str, num: int, total: int, first: bool) -> str:
    title = sub = None
    body: list[str] = []
    lis: list[str] = []
    lis_class = ""
    default_lis_class = ""
    cards: list[str] = []

    def flush_lists():
        nonlocal lis, cards
        if lis:
            cls = f' class="{lis_class}"' if lis_class else ""
            body.append(f"<ul{cls}>" + "".join(f"<li>{x}</li>" for x in lis) + "</ul>")
            lis = []
        if cards:
            body.append('<div class="cols">' + "".join(cards) + "</div>")
            cards = []

    for line in block.strip().splitlines():
        line = line.rstrip()
        if not line:
            continue
        if line.startswith("## "):
            sub = inline(line[3:])
        elif line.startswith("# "):
            title = inline(line[2:])
        elif line.startswith("fig: "):
            flush_lists()
            body.append(fig_tag(line[5:].strip()))
        elif line.startswith("bullets: "):
            default_lis_class = "plain" if line[9:].strip() == "plain" else ""
        elif line.startswith("- ") or line.startswith("* "):
            cls = "plain" if line.startswith("* ") else default_lis_class
            if lis and cls != lis_class:
                flush_lists()
            lis_class = cls
            lis.append(inline(line[2:]))
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

    tag = "h1" if first else "h2"
    style = ' style="font-size:clamp(48px,7vw,84px)"' if first else ""
    parts = [f'<section class="slide"><span class="num">{num} / {total}</span><div class="inner">']
    parts.append(f'<{tag} class="title"{style}>{title}</{tag}>')
    if sub:
        parts.append(f'<p class="sub">{sub}</p>')
    parts.extend(body)
    parts.append("</div></section>")
    return "\n  ".join(parts)


STYLE_AND_SCRIPT_SRC = ROOT / "template.html"


def main() -> None:
    tpl = STYLE_AND_SCRIPT_SRC.read_text()
    src_path = ROOT / "slides.md"
    text = src_path.read_text()
    m = re.match(r"\s*<!--.*?-->\n?", text, re.S)
    content = text[m.end() :] if m else text
    if not m or m.group(0).strip() != SYNTAX_HEADER.strip():
        src_path.write_text(SYNTAX_HEADER + "\n\n" + content.lstrip("\n"))
        content = src_path.read_text()[len(SYNTAX_HEADER) + 2 :]
        print("refreshed syntax header in slides.md")
    blocks = re.split(r"^---$", content, flags=re.M)
    total = len(blocks)
    slides = "\n\n".join(render_slide(b, i + 1, total, i == 0) for i, b in enumerate(blocks))
    OUT.write_text(tpl.replace("<!--SLIDES-->", slides))
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes, {total} slides)")


if __name__ == "__main__":
    main()
