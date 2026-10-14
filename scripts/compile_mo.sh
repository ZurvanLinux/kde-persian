#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/Users/mohammad/Documents/GitHub/kde-persian"
WORK_FA="$BASE_DIR/work/fa"
OUT_LOCALE="$BASE_DIR/build/locale/fa/LC_MESSAGES"

mkdir -p "$OUT_LOCALE"

count=0
while IFS= read -r -d '' po_file; do
    base_name="$(basename "${po_file%.po}.mo")"
    msgfmt --check "$po_file" -o "$OUT_LOCALE/$base_name"
    count=$((count + 1))
done < <(find "$WORK_FA" -name "*.po" -print0)

echo "✓ Compiled $count binary .mo files into $OUT_LOCALE"
echo "To test inside a KDE Plasma 6 session, copy $OUT_LOCALE/*.mo to /usr/share/locale/fa/LC_MESSAGES/"
