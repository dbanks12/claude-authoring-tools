#!/usr/bin/env bash
# Build a deck's HTML and PDF. Used by CI; works locally too.
# Usage: ci-build.sh [DECK_DIR]   (default: the current directory)
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
deck="$(cd "${1:-.}" && pwd)"
python3 -c "import PIL" 2>/dev/null || python3 -m pip install --quiet pillow
python3 "$here/build.py" "$deck"
python3 "$here/pdf.py" "$deck"
