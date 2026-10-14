#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/Users/mohammad/Documents/GitHub/kde-persian"
SVN_BASE="svn://anonsvn.kde.org/home/kde/trunk/l10n-kf6"

echo "==> [1/2] Syncing KDE6 POT Templates (upstream/templates)..."
if [ -d "$BASE_DIR/upstream/templates/.svn" ]; then
    svn update "$BASE_DIR/upstream/templates"
else
    svn co "$SVN_BASE/templates/messages" "$BASE_DIR/upstream/templates"
fi

echo "==> [2/2] Syncing Legacy KDE6 Persian PO Files (upstream/fa-legacy)..."
if [ -d "$BASE_DIR/upstream/fa-legacy/.svn" ]; then
    svn update "$BASE_DIR/upstream/fa-legacy"
else
    svn co "$SVN_BASE/fa/messages" "$BASE_DIR/upstream/fa-legacy"
fi

echo "==> SVN synchronization complete."
