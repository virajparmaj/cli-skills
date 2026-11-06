#!/usr/bin/env bash
# Read-only inventory; Python preserves Git NUL-delimited filenames.
set -euo pipefail
exec python3 "$(dirname "$0")/cluster-git-changes.py" "$@"
