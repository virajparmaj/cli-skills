#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /absolute/path/to/repo" >&2
  exit 1
fi

repo="$1"
if [ ! -d "$repo" ]; then
  echo "Error: directory not found: $repo" >&2
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "Error: rg is required but not installed" >&2
  exit 1
fi

cd "$repo"

echo "== Repo =="
echo "$repo"

echo
echo "== Context Files =="
rg --files -g 'README*' -g 'CLAUDE.md' -g 'notes/**' -g '.env*' | head -n 200 || true

echo
echo "== UI Error And Fallback Signals =="
rg --files | rg -i '(error|fallback|empty|skeleton|spinner|loading|retry|boundary|toast|alert|placeholder)' | head -n 300 || true

echo
echo "== API And Network Signals =="
rg --files | rg -i '(api|client|fetch|axios|request|service|http|query|mutation|gateway)' | head -n 300 || true

echo
echo "== Third-Party Integration Signals =="
rg --files | rg -i '(stripe|sentry|segment|intercom|slack|twilio|firebase|supabase|auth0|clerk|webhook)' | head -n 300 || true

echo
echo "== Error-Handling Code Patterns =="
rg -n --hidden --glob '!node_modules/**' --glob '!.git/**' --glob '!dist/**' --glob '!build/**' \
  '(try\s*\{|catch\s*\(|throw\s+new|error\.|onError|ErrorBoundary|retry|timeout|AbortController|Promise\.allSettled|console\.error)' \
  | head -n 400 || true

echo
echo "== Test Files For Failure Paths =="
rg --files | rg -i '(test|spec|e2e|playwright|cypress|vitest|jest)' | head -n 300 || true
