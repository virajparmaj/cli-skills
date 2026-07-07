#!/usr/bin/env bash
#
# cluster-git-changes.sh — emit a per-file manifest of the working tree so the
# model can group changes into logical commits. Read-only: never stages,
# commits, or writes to the target repo.
#
# Usage: cluster-git-changes.sh [repo-path]   (default repo-path: .)
#
# Output sections (each fenced with "=== name ==="):
#   summary            counts of staged / unstaged / untracked / renames
#   file manifest      one row per changed file: STATUS  CLASS  TOPDIR  PATH
#   rename pairs       OLD -> NEW for detected renames
#   diffstat           per-file added/deleted line counts (tracked changes)
#   untracked sizes    line count per untracked text file (best effort)
#
# CLASS is a coarse bucket derived from path/extension:
#   src | test | docs | config | style | asset | other

set -euo pipefail

repo_path="${1:-.}"

if [[ ! -d "$repo_path" ]]; then
  echo "Not a directory: $repo_path" >&2
  exit 1
fi

cd "$repo_path"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repository: $repo_path" >&2
  exit 1
fi

# Classify a path into a coarse bucket used for grouping hints.
classify() {
  local p="$1"
  local lower
  lower="$(printf '%s' "$p" | tr '[:upper:]' '[:lower:]')"

  case "$lower" in
    *.test.*|*.spec.*|*_test.py|*_test.go|test/*|tests/*|*/test/*|*/tests/*|*/__tests__/*|*.test.ts|*.test.tsx|*.test.js)
      echo "test"; return ;;
  esac

  # Config filenames must win over the generic *.txt docs rule below, so
  # match config before docs.
  case "$lower" in
    package.json|package-lock.json|pnpm-lock.yaml|yarn.lock|tsconfig*.json|vite.config.*|vercel.json|*.env|*.env.*|.env*|requirements*.txt|pyproject.toml|poetry.lock|setup.cfg|setup.py|makefile|dockerfile|docker-compose*|*.dockerfile|.eslintrc*|.prettierrc*|.gitignore|.github/*|*/.github/*|*.yml|*.yaml|*.toml|*.ini|*.cfg|supabase/config.*)
      echo "config"; return ;;
  esac

  case "$lower" in
    *.md|*.mdx|*.rst|*.txt|docs/*|*/docs/*|readme*|changelog*|license*|notes/*|*/notes/*)
      echo "docs"; return ;;
  esac

  case "$lower" in
    *.css|*.scss|*.sass|*.less|tailwind.config.*|postcss.config.*|*.stylelintrc*)
      echo "style"; return ;;
  esac

  case "$lower" in
    *.png|*.jpg|*.jpeg|*.gif|*.svg|*.webp|*.ico|*.woff|*.woff2|*.ttf|*.otf|*.mp4|*.webm|*.pdf|public/*|*/public/*|assets/*|*/assets/*)
      echo "asset"; return ;;
  esac

  case "$lower" in
    *.ts|*.tsx|*.js|*.jsx|*.py|*.go|*.rs|*.c|*.cc|*.cpp|*.h|*.hpp|*.java|*.rb|*.php|src/*|*/src/*|backend/*|app/*|lib/*|*/lib/*)
      echo "src"; return ;;
  esac

  echo "other"
}

# Top-level directory of a path (or "(root)" for repo-root files).
topdir() {
  local p="$1"
  if [[ "$p" == */* ]]; then
    printf '%s' "${p%%/*}"
  else
    printf '%s' "(root)"
  fi
}

# Collect status codes for a path across staged + unstaged views.
# git status --short gives us both index (col 1) and worktree (col 2) state.

# Detect renames with -M so OLD -> NEW pairs surface.
staged_ns="$(git diff --staged --name-status -M 2>/dev/null || true)"
unstaged_ns="$(git diff --name-status -M 2>/dev/null || true)"
untracked="$(git ls-files --others --exclude-standard 2>/dev/null || true)"

staged_count="$(printf '%s' "$staged_ns" | grep -c . || true)"
unstaged_count="$(printf '%s' "$unstaged_ns" | grep -c . || true)"
untracked_count="$(printf '%s' "$untracked" | grep -c . || true)"
rename_count="$(printf '%s\n%s' "$staged_ns" "$unstaged_ns" | grep -cE '^R[0-9]*'$'\t' || true)"

echo "=== summary ==="
echo "repo: $(git rev-parse --show-toplevel 2>/dev/null || echo "$repo_path")"
echo "branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "(unknown)")"
echo "staged entries: ${staged_count:-0}"
echo "unstaged entries: ${unstaged_count:-0}"
echo "untracked files: ${untracked_count:-0}"
echo "renames detected: ${rename_count:-0}"
echo

# Build the unified manifest. Emit one row per file with a stable schema so the
# model can group deterministically:  STAGE  STATUS  CLASS  TOPDIR  PATH
echo "=== file manifest ==="
echo "STAGE   STATUS  CLASS   TOPDIR          PATH"

emit_ns_rows() {
  local stage="$1"
  local data="$2"
  [[ -z "$data" ]] && return 0
  # Each line: STATUS<TAB>PATH   (rename: STATUS<TAB>OLD<TAB>NEW)
  while IFS=$'\t' read -r status a b; do
    [[ -z "$status" ]] && continue
    local path="$a"
    # For renames/copies the meaningful (new) path is the second field.
    if [[ "$status" =~ ^[RC][0-9]* ]] && [[ -n "$b" ]]; then
      path="$b"
    fi
    local cls td
    cls="$(classify "$path")"
    td="$(topdir "$path")"
    printf '%-7s %-7s %-7s %-15s %s\n' "$stage" "$status" "$cls" "$td" "$path"
  done <<< "$data"
}

emit_ns_rows "staged" "$staged_ns"
emit_ns_rows "worktree" "$unstaged_ns"

if [[ -n "$untracked" ]]; then
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    cls="$(classify "$path")"
    td="$(topdir "$path")"
    printf '%-7s %-7s %-7s %-15s %s\n' "new" "??" "$cls" "$td" "$path"
  done <<< "$untracked"
fi
echo

echo "=== rename pairs ==="
rename_lines="$(printf '%s\n%s' "$staged_ns" "$unstaged_ns" | grep -E '^[RC][0-9]*'$'\t' || true)"
if [[ -z "$rename_lines" ]]; then
  echo "(none)"
else
  while IFS=$'\t' read -r status old new; do
    [[ -z "$status" ]] && continue
    echo "$old -> $new  ($status)"
  done <<< "$rename_lines"
fi
echo

echo "=== diffstat (tracked changes) ==="
{
  git diff --staged --stat -M 2>/dev/null || true
  git diff --stat -M 2>/dev/null || true
} | sed '/^$/d' || true
if ! git diff --staged --quiet 2>/dev/null || ! git diff --quiet 2>/dev/null; then
  :
else
  echo "(no tracked changes)"
fi
echo

echo "=== untracked sizes (best effort) ==="
if [[ -z "$untracked" ]]; then
  echo "(none)"
else
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    if [[ -f "$path" ]] && LC_ALL=C grep -Iq . "$path" 2>/dev/null; then
      lines="$(wc -l <"$path" 2>/dev/null | tr -d ' ' || echo '?')"
      printf '%6s lines  %s\n' "$lines" "$path"
    else
      printf '%6s        %s\n' "binary" "$path"
    fi
  done <<< "$untracked"
fi
