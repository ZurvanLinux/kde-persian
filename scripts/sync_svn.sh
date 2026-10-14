#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/Users/mohammad/Documents/GitHub/kde-persian"
SVN_BASE="svn://anonsvn.kde.org/home/kde/trunk/l10n-kf6"
TEMPLATES_GIT="https://invent.kde.org/localization/l10n-templates.git"

echo "==> [1/2] Syncing KDE6 POT Templates (upstream/l10n-templates -> trunk6/messages)..."
mkdir -p "$BASE_DIR/upstream"

if [ -d "$BASE_DIR/upstream/l10n-templates/.git" ]; then
    echo "Updating existing l10n-templates..."
    git -C "$BASE_DIR/upstream/l10n-templates" pull
else
    echo "Cloning sparse l10n-templates (trunk6/messages)..."
    git clone --depth 1 --filter=blob:none --sparse "$TEMPLATES_GIT" "$BASE_DIR/upstream/l10n-templates"
    git -C "$BASE_DIR/upstream/l10n-templates" sparse-checkout set trunk6/messages
fi

if [ ! -L "$BASE_DIR/upstream/templates" ]; then
    rm -rf "$BASE_DIR/upstream/templates"
    ln -s l10n-templates/trunk6/messages "$BASE_DIR/upstream/templates"
fi

echo "==> [2/2] Syncing Legacy KDE6 Persian PO Files (upstream/fa-legacy)..."
if [ -d "$BASE_DIR/upstream/fa-legacy/.svn" ]; then
    svn update "$BASE_DIR/upstream/fa-legacy"
else
    svn co "$SVN_BASE/fa/messages" "$BASE_DIR/upstream/fa-legacy"
fi

echo "==> Upstream synchronization complete."
