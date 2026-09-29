#!/usr/bin/env python3
"""Render <deck>/<deck-dirname>.html to .pdf, one 16:9 page per slide (13.333 x 7.5 in).

Usage: python3 pdf.py [DECK_DIR]   (default: the current directory). Run build.py first. Uses headless Chromium with print CSS added to a temporary copy.
Slides whose figure is tall get a two-column page: text left, figure right.
"""
import os
import re
import shutil
import sys
import subprocess
from pathlib import Path

from PIL import Image

DECK = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
NAME = DECK.name
TALL = 1.6  # figures narrower than this width/height ratio go in the right column

PRINT_CSS = """
@page { size: 13.333in 7.5in; margin: 0; }
html, body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.slide { height: 7.5in; min-height: 0; padding: 0.45in 0.8in; border-bottom: none;
         break-after: page; break-inside: avoid; }
.slide:last-child { break-after: auto; }
.slide.hasfill { height: 7.5in; }  /* vh is not the page height in print */
.slide.hasmega .split .col:first-child { padding-top: 0.45in; }
.inner { max-width: 100%; }
.fig:not(.fill) img { max-height: 3.6in; }
.sub { max-width: none; }
.num { top: 0.3in; right: 0.5in; }
.slide.tall .inner { display: grid; grid-template-columns: 36% 1fr; column-gap: 0.4in;
                     grid-template-rows: auto auto 1fr; align-items: start; }
.slide.tall .title, .slide.tall .sub, .slide.tall ul { grid-column: 1; }
.slide.tall .sub { max-width: 34ch; }
.slide.tall .fig { grid-column: 2; grid-row: 1 / 4; margin: 0; justify-self: end; }
.slide.tall .fig img { max-height: 6.3in; width: auto; max-width: 100%; }
"""


def chromium():
    for name in ("chromium", "chromium-browser", "google-chrome"):
        if path := shutil.which(name):
            return path
    raise SystemExit("no chromium found")


def mark_tall(html):
    """Add class "tall" to slides whose figure is tall."""
    def tag(m):
        section = m.group(0)
        figs = re.findall(r'alt="([\w-]+) diagram"', section)
        if figs and 'class="split"' not in section:  # split slides already lay out side by side
            w, h = Image.open(DECK / "figures" / f"fig-{figs[0]}.png").size
            if w / h < TALL:
                return section.replace('<section class="slide', '<section class="slide tall', 1)
        return section
    return re.sub(r'<section class="slide[ "].*?</section>', tag, html, flags=re.S)


def main():
    html = mark_tall((DECK / f"{NAME}.html").read_text())
    # the template has no <head>; append after its first style block so these rules win
    html = html.replace("</style>", f"</style><style>{PRINT_CSS}</style>", 1)
    # keep the temp file inside the deck dir: snap chromium cannot read /tmp
    tmp = DECK / f".{NAME}-print.html"
    tmp.write_text(html)
    out = DECK / f"{NAME}.pdf"
    try:
        # CI runners often block Chrome's sandbox; the runner is a throwaway VM, so skip it there
        sandbox = ["--no-sandbox"] if os.environ.get("CI") else []
        subprocess.run([chromium(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", *sandbox,
                        f"--print-to-pdf={out}", tmp.as_uri()], check=True, capture_output=True)
    finally:
        tmp.unlink(missing_ok=True)
    print(f"wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
