#!/usr/bin/env bash
# Membuat docs/PANDUAN.pdf dari docs/PANDUAN.md.
# Butuh: pandoc 3.x dan Google Chrome (atau Chromium). Font dimuat dari Google Fonts, jadi perlu internet.
#
# Pakai:  bash docs/pdf/build.sh
# Ganti browser:  CHROME=/path/ke/chromium bash docs/pdf/build.sh
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS="$(dirname "$DIR")"
SRC="$DOCS/PANDUAN.md"
OUT="$DOCS/PANDUAN.pdf"

if [[ -z "${CHROME:-}" ]]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           google-chrome google-chrome-stable chromium chromium-browser; do
    if [[ -x "$c" ]] || command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
  done
fi
[[ -n "${CHROME:-}" ]] || { echo "Chrome/Chromium tidak ditemukan. Set variabel CHROME." >&2; exit 1; }
command -v pandoc >/dev/null || { echo "pandoc tidak ditemukan (brew install pandoc)." >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp "$DIR/style.css" "$TMP/"
[[ -d "$DOCS/img" ]] && cp -R "$DOCS/img" "$TMP/"

pandoc "$SRC" -f gfm -t html5 -s \
  --syntax-highlighting=none \
  --lua-filter="$DIR/links.lua" \
  --css=style.css \
  -B "$DIR/sampul.html" \
  --metadata title="Panduan Pintu Kuliah" --metadata lang=id \
  -o "$TMP/panduan.html"

"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=15000 \
  --print-to-pdf="$OUT" "file://$TMP/panduan.html" 2>/dev/null

echo "Selesai: $OUT"
