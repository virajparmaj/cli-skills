#!/usr/bin/env bash

# phase-status.sh — gather deterministic phase-doc evidence for the v-phase skill.
#
# Finds phase-*.md contract docs, extracts their status markers and acceptance
# checklists, harvests every file path each doc promises, and greps the repo to
# prove those paths exist. Output is machine-readable sectioned text the model
# reads to build the pre-flight verification table. Read-only against the repo.

set -euo pipefail

repo_path="${1:-.}"

if [[ ! -d "$repo_path" ]]; then
  echo "Not a directory: $repo_path" >&2
  echo "Usage: $0 [repo-path]" >&2
  exit 1
fi

cd "$repo_path"

# Directories we never search for phase docs or referenced files.
prune='-name node_modules -o -name .git -o -name dist -o -name build -o -name .next -o -name .venv -o -name venv -o -name __pycache__ -o -name coverage'

echo "=== repo root ==="
pwd
echo

# ---------------------------------------------------------------------------
# 1. Locate phase docs. Match phase-NN.md, phase_NN.md, phaseNN.md, and common
#    variants under any docs/ or plans/ folder, case-insensitively.
# ---------------------------------------------------------------------------
echo "=== phase docs found ==="
phase_docs=$(find . \( $prune \) -prune -o -type f \
  \( -iname 'phase-*.md' -o -iname 'phase_*.md' -o -iname 'phase[0-9]*.md' \) \
  -print 2>/dev/null | sort)

if [[ -z "$phase_docs" ]]; then
  echo "NONE — no phase-*.md contract docs found in $repo_path"
  echo
  echo "=== hint ==="
  echo "This skill expects phase-NN.md docs (e.g. docs/phase-01.md ... phase-10.md)."
  echo "If phase contracts live under a different name, point the user at them explicitly."
  exit 0
fi
echo "$phase_docs"
echo

doc_count=$(printf '%s\n' "$phase_docs" | grep -c .)
echo "count: $doc_count"
echo

# ---------------------------------------------------------------------------
# 2. Per-doc summary: status line, acceptance checkboxes, referenced paths.
# ---------------------------------------------------------------------------
while IFS= read -r doc; do
  [[ -z "$doc" ]] && continue
  echo "=== doc: $doc ==="

  echo "--- status markers ---"
  # Lines that look like status/state/implemented/done/complete markers.
  grep -nEi '(^|[[:space:]#*-])(status|state|implemented|done|complete[d]?|shipped|in progress|todo|pending)[[:space:]]*[:—-]' "$doc" 2>/dev/null \
    | head -n 20 || true
  # Explicit "Implemented — <date>" stamp this skill appends on completion.
  grep -nEi 'implemented[[:space:]]*(—|-|:)[[:space:]]*[0-9]{4}' "$doc" 2>/dev/null | head -n 5 || true
  echo

  echo "--- acceptance checkboxes ---"
  # Markdown task-list items, both checked and unchecked.
  grep -nE '^[[:space:]]*[-*][[:space:]]+\[[ xX]\]' "$doc" 2>/dev/null | head -n 60 || true
  # Count checked vs unchecked for a quick completion ratio.
  checked=$(grep -cE '^[[:space:]]*[-*][[:space:]]+\[[xX]\]' "$doc" 2>/dev/null || true)
  unchecked=$(grep -cE '^[[:space:]]*[-*][[:space:]]+\[[[:space:]]\]' "$doc" 2>/dev/null || true)
  echo "checkbox tally: checked=${checked:-0} unchecked=${unchecked:-0}"
  echo

  echo "--- referenced file paths (existence check) ---"
  # Harvest candidate paths: backtick-quoted tokens and bare path-looking tokens
  # containing a slash or a known source extension.
  refs=$(grep -oE '`[^`]+`|[A-Za-z0-9_./-]+\.(ts|tsx|js|jsx|py|json|sql|md|css|sh|toml|yaml|yml)' "$doc" 2>/dev/null \
    | tr -d '`' \
    | grep -E '/|\.' \
    | grep -vE '^https?://' \
    | sort -u || true)
  if [[ -z "$refs" ]]; then
    echo "(none referenced)"
  else
    while IFS= read -r ref; do
      [[ -z "$ref" ]] && continue
      # Strip a leading ./ and any trailing punctuation the grep may have caught.
      clean=$(printf '%s' "$ref" | sed -E 's#^\./##; s/[),.:;]+$//')
      [[ -z "$clean" ]] && continue
      if [[ -e "$clean" ]]; then
        echo "EXISTS   $clean"
      elif compgen -G "*/$clean" >/dev/null 2>&1 || find . \( $prune \) -prune -o -type f -name "$(basename "$clean")" -print 2>/dev/null | grep -q .; then
        found=$(find . \( $prune \) -prune -o -type f -name "$(basename "$clean")" -print 2>/dev/null | head -n 1)
        echo "BASENAME $clean  ->  ${found#./}"
      else
        echo "MISSING  $clean"
      fi
    done <<< "$refs"
  fi
  echo
done <<< "$phase_docs"

# ---------------------------------------------------------------------------
# 3. Context files that describe prior-phase truth, if the repo keeps them.
# ---------------------------------------------------------------------------
echo "=== context files present ==="
for f in CLAUDE.md README.md notes/00_overview.md notes/03_architecture.md \
         notes/06_api_contracts.md notes/11_known_issues.md TASKS.md TODO.md; do
  if [[ -f "$f" ]]; then
    echo "PRESENT $f"
  fi
done
echo

echo "=== done ==="
