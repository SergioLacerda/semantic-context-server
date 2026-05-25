#!/bin/bash
# Install all repository git hooks from tools/git-hooks into .git/hooks.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SOURCE_DIR="$REPO_ROOT/tools/git-hooks"
TARGET_DIR="$REPO_ROOT/.git/hooks"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "ERROR: Hook source directory not found: $SOURCE_DIR"
    exit 1
fi

mkdir -p "$TARGET_DIR"

installed=0
for hook_file in "$SOURCE_DIR"/*; do
    [ -f "$hook_file" ] || continue
    hook_name="$(basename "$hook_file")"
    target_file="$TARGET_DIR/$hook_name"

    if [ -f "$target_file" ]; then
        cp "$target_file" "$target_file.backup"
        echo "backup: $target_file.backup"
    fi

    cp "$hook_file" "$target_file"
    chmod +x "$target_file"
    echo "installed: $hook_name"
    installed=$((installed + 1))
done

echo "Done. Installed $installed hook(s) from tools/git-hooks."
