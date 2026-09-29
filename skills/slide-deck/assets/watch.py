#!/usr/bin/env python3
"""Rebuild <deck>/<deck-dirname>.html and .pdf whenever the deck sources change.

Usage: python3 watch.py [DECK_DIR]   (default: the current directory). Runs forever.
Watches slides.md, figures/*.png and an optional template.html every 2 seconds.
"""
import subprocess
import sys
import time
from pathlib import Path

TOOL = Path(__file__).resolve().parent
DECK = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
POLL_SECONDS = 2


def snapshot():
    paths = [DECK / "slides.md", DECK / "template.html"]
    paths += sorted((DECK / "figures").glob("*.png"))
    return {str(p): p.stat().st_mtime for p in paths if p.exists()}


def rebuild():
    for script in ("build.py", "pdf.py"):
        r = subprocess.run([sys.executable, str(TOOL / script), str(DECK)], capture_output=True, text=True)
        stamp = time.strftime("%H:%M:%S")
        print(f"{stamp} {script}: {(r.stdout or r.stderr).strip()}", flush=True)
        if r.returncode:
            return False
    return True


def main():
    print(f"watching {DECK}", flush=True)
    base = snapshot()
    while True:
        time.sleep(POLL_SECONDS)
        if snapshot() == base:
            continue
        time.sleep(1)  # let an editor's burst of writes settle
        # build.py rewrites slides.md's header comment, so snapshot after the rebuild
        rebuild()
        base = snapshot()


if __name__ == "__main__":
    main()
