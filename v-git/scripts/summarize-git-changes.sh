#!/usr/bin/env bash

set -euo pipefail

repo_path="${1:-.}"
cd "$repo_path"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repository: $repo_path" >&2
  exit 1
fi

echo "=== git status --short ==="
git status --short
echo

echo "=== staged files ==="
git diff --staged --name-status
echo

echo "=== unstaged files ==="
git diff --name-status
echo

echo "=== untracked files ==="
git ls-files --others --exclude-standard
echo

echo "=== staged diffstat ==="
git diff --staged --stat
echo

echo "=== unstaged diffstat ==="
git diff --stat
