#!/usr/bin/env bash
# Read-only phase inventory; one pruned walk, with line-qualified paths supported.
set -euo pipefail
exec python3 "$(dirname "$0")/phase-status.py" "$@"
