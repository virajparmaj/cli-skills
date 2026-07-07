#!/usr/bin/env bash
#
# find-lovable-traces.sh — enumerate every Lovable / gpt-engineer trace in a repo.
#
# Read-only. Prints deterministic, sectioned facts the model turns into a
# removal table. No edits are made here; the skill applies removals separately.
#
# Usage: find-lovable-traces.sh [repo-path]   (default: current directory)

set -euo pipefail

repo_path="${1:-.}"

if [ ! -d "$repo_path" ]; then
  echo "Not a directory: $repo_path" >&2
  exit 1
fi

cd "$repo_path"

# grep across source-ish files, always excluding heavy/generated trees.
# Lockfiles are excluded on purpose: they regenerate from package.json after
# `npm install`, so they are never a manual removal target (only noise).
scan() {
  grep -rniI "$1" . \
    --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
    --include="*.mjs" --include="*.cjs" --include="*.json" --include="*.html" \
    --include="*.md" --include="*.mdx" --include="*.css" \
    --exclude=package-lock.json --exclude=bun.lock --exclude=bun.lockb \
    --exclude=pnpm-lock.yaml --exclude=yarn.lock \
    --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
    --exclude-dir=build --exclude-dir=.next --exclude-dir=coverage \
    2>/dev/null || true
}

echo "=== repo ==="
echo "$repo_path"
echo

echo "=== lovable-tagger / componentTagger (vite plugin) ==="
scan "lovable-tagger"
scan "componentTagger"
echo

echo "=== lovable.dev / gpt-engineer / gptengineer URLs and script tags ==="
scan "lovable\.dev"
scan "gpt-engineer"
scan "gptengineer"
scan "cdn\.gpteng\.co"
echo

echo "=== Lovable meta tags in index.html ==="
if [ -f index.html ]; then
  grep -niE 'lovable|opengraph-image-p98pqg|@Lovable|gpteng' index.html 2>/dev/null || echo "(no lovable meta tags in index.html)"
else
  echo "(no index.html at repo root)"
fi
echo

echo "=== generated README boilerplate headings ==="
readme="$(ls README.md README.MD readme.md 2>/dev/null | head -1 || true)"
if [ -n "$readme" ]; then
  echo "readme: $readme"
  grep -niE 'welcome to your lovable project|## project info|how can i edit this code|use lovable|use github codespaces|REPLACE_WITH_PROJECT_ID|lovable\.dev/projects' "$readme" 2>/dev/null || echo "(no obvious Lovable README boilerplate)"
else
  echo "(no README found)"
fi
echo

echo "=== other lovable string hits (catch-all) ==="
# Anything else mentioning lovable that the targeted scans above missed.
scan "lovable" | grep -viE 'lovable-tagger|componentTagger|lovable\.dev' || echo "(none)"
echo

echo "=== leftover placeholder / generated assets ==="
for f in public/placeholder.svg public/placeholder.png src/assets/placeholder.svg public/opengraph-image-p98pqg.png public/favicon.ico; do
  [ -f "$f" ] && echo "present: $f"
done
echo "(favicon.ico is often the default Lovable favicon — confirm before deleting)"
echo

echo "=== never-imported files under src/ (declared but not referenced) ==="
# Deterministic, conservative import-graph check:
# a file is "never imported" if its module basename never appears in any
# import/require/lazy specifier anywhere in src/. Entrypoints are excluded.
if [ -d src ]; then
  # Collect every import/reference specifier used anywhere in src PLUS the root
  # build/test config files. Including configs prevents false orphans for files
  # referenced only from vite.config / vitest.config (e.g. test setupFiles).
  config_globs="vite.config.* vitest.config.* index.html"
  # shellcheck disable=SC2086
  specifiers="$( { grep -rhoE "(import[^\"']*|require\(|lazy\()[[:space:]]*[\"'][^\"']+[\"']" src 2>/dev/null; \
    grep -hoE "[\"'][^\"']+[\"']" $config_globs 2>/dev/null; } \
    | grep -oE "[\"'][^\"']+[\"']" | tr -d "\"'" || true)"
  entrypoints_re='^\./src/(main|index|App|vite-env|setupTests|env)\.(t|j)sx?$'
  found_orphan=0
  # Portable file walk (no mapfile — must work on bash 3.2 / macOS default).
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    # Skip common entrypoints and type/declaration/test files.
    if printf '%s' "$f" | grep -qE "$entrypoints_re"; then continue; fi
    case "$f" in
      *.d.ts|*.test.ts|*.test.tsx|*.spec.ts|*.spec.tsx) continue ;;
    esac
    base="$(basename "$f")"
    stem="${base%.*}"          # strip one extension: Button.tsx -> Button
    stem="${stem%.*}"          # strip a second if .d etc. (harmless otherwise)
    # Match the stem as the final path segment of any specifier, tolerating an
    # optional file extension (import "./x/setup" or "./x/setup.ts" both count).
    if ! printf '%s\n' "$specifiers" | grep -qE "(^|/)$stem(\.[a-z]+)?$"; then
      echo "orphan?: $f"
      found_orphan=1
    fi
  done < <(find ./src -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) 2>/dev/null | sort)
  [ "$found_orphan" -eq 0 ] && echo "(no obvious never-imported files under src/)"
  echo
  echo "NOTE: 'orphan?' is a heuristic. Confirm each is truly unused before deleting"
  echo "      (dynamic imports, glob imports, and re-exports can hide real usage)."
else
  echo "(no src/ directory)"
fi
echo

echo "=== dependency + config residue ==="
if [ -f package.json ]; then
  grep -niE '"lovable-tagger"|"gpt-engineer"|componentTagger' package.json 2>/dev/null || echo "(no lovable deps in package.json)"
else
  echo "(no package.json)"
fi
for lock in package-lock.json bun.lockb bun.lock pnpm-lock.yaml yarn.lock; do
  [ -f "$lock" ] && echo "lockfile present: $lock (regenerate after removing deps, do not hand-edit)"
done
echo

echo "=== build command probe ==="
if [ -f package.json ]; then
  grep -nE '"(build|dev|preview)"[[:space:]]*:' package.json 2>/dev/null || echo "(no build/dev/preview scripts found)"
else
  echo "(no package.json — cannot determine build command)"
fi
