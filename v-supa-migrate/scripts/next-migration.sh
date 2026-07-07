#!/usr/bin/env bash
#
# next-migration.sh — deterministic facts for drafting the next Supabase migration.
#
# Read-only. Given a repo path, it locates supabase/migrations/, reports the
# existing migration history and its naming style, reconstructs a rough current
# table inventory from CREATE TABLE statements across all migrations, emits the
# next filename to use, and locates the typed-client types file to keep in sync.
#
# Usage: next-migration.sh [repo-path]   (default: .)

set -euo pipefail

repo_path="${1:-.}"

if [[ ! -d "$repo_path" ]]; then
  echo "Not a directory: $repo_path" >&2
  exit 1
fi

cd "$repo_path"

# --- Locate the migrations directory -----------------------------------------
mig_dir=""
for cand in supabase/migrations db/migrations migrations; do
  if [[ -d "$cand" ]]; then
    mig_dir="$cand"
    break
  fi
done

if [[ -z "$mig_dir" ]]; then
  # Fall back to a search so nested/monorepo layouts still resolve.
  mig_dir="$(find . -type d -path '*supabase/migrations' 2>/dev/null | head -1 | sed 's|^\./||')"
fi

echo "=== migrations directory ==="
if [[ -z "$mig_dir" || ! -d "$mig_dir" ]]; then
  echo "NONE FOUND — no supabase/migrations/ in this repo."
  echo "Create one at: supabase/migrations/"
  mig_dir=""
else
  echo "$mig_dir"
fi
echo

# --- Existing migration history ----------------------------------------------
echo "=== existing migrations (chronological) ==="
existing=()
if [[ -n "$mig_dir" ]]; then
  while IFS= read -r f; do
    [[ -n "$f" ]] && existing+=("$f")
  done < <(find "$mig_dir" -maxdepth 1 -name '*.sql' -type f 2>/dev/null | sort)
fi
if [[ ${#existing[@]} -eq 0 ]]; then
  echo "(none — this would be the first migration)"
else
  for f in "${existing[@]}"; do
    echo "$(basename "$f")"
  done
fi
echo

# --- Detect naming style ------------------------------------------------------
echo "=== naming style ==="
naming="timestamp"
if [[ ${#existing[@]} -gt 0 ]]; then
  last_base="$(basename "${existing[${#existing[@]}-1]}")"
  if [[ "$last_base" =~ ^[0-9]{14}_ ]]; then
    naming="timestamp"
    echo "timestamp (UTC YYYYMMDDHHMMSS_)  — matches last file: $last_base"
  elif [[ "$last_base" =~ ^[0-9]{3,4}_ ]]; then
    naming="sequential"
    echo "sequential (NNN_)  — matches last file: $last_base"
  else
    naming="timestamp"
    echo "unrecognized last file ($last_base) — defaulting to timestamp"
  fi
else
  echo "no history — defaulting to timestamp (UTC YYYYMMDDHHMMSS_)"
fi
echo

# --- Emit the next filename ---------------------------------------------------
echo "=== next filename ==="
ts="$(date -u +%Y%m%d%H%M%S)"
if [[ "$naming" == "sequential" ]]; then
  # Preserve the existing zero-pad width; step the highest numeric prefix by one.
  max=0
  width=3
  for f in "${existing[@]}"; do
    b="$(basename "$f")"
    num="${b%%_*}"
    if [[ "$num" =~ ^[0-9]+$ ]]; then
      width=${#num}
      n=$((10#$num))
      (( n > max )) && max=$n
    fi
  done
  next=$((max + 1))
  printf "sequential: %0*d_<slug>.sql\n" "$width" "$next"
  printf "timestamp alt: %s_<slug>.sql\n" "$ts"
else
  echo "timestamp: ${ts}_<slug>.sql"
fi
echo "  (replace <slug> with a snake_case summary, e.g. add_saved_reports_table)"
echo

# --- Current table inventory (rough, from migration history) ------------------
echo "=== current table inventory (from CREATE TABLE across history) ==="
if [[ ${#existing[@]} -gt 0 ]]; then
  grep -rhiE 'create table' "$mig_dir" 2>/dev/null \
    | sed -E 's/create table[[:space:]]+(if not exists[[:space:]]+)?//I' \
    | sed -E 's/[[:space:]]*\(.*$//' \
    | sed -E 's/[[:space:]]*;.*$//' \
    | sed -E 's/^"?public"?\.//I' \
    | tr -d '"' \
    | sed -E 's/[[:space:]]+//g' \
    | grep -vE '^$' \
    | sort -u \
    || echo "(no CREATE TABLE statements found)"
else
  echo "(no history to inventory)"
fi
echo

echo "=== updated_at trigger function present? ==="
if [[ ${#existing[@]} -gt 0 ]] && grep -rqiE 'function[[:space:]]+public\.update_updated_at_column' "$mig_dir" 2>/dev/null; then
  echo "YES — reuse existing public.update_updated_at_column(); only add the CREATE TRIGGER."
else
  echo "NO — include the CREATE OR REPLACE FUNCTION block if the new table needs updated_at."
fi
echo

# --- Typed client location ----------------------------------------------------
echo "=== typed client types file ==="
types_file=""
for cand in \
  src/integrations/supabase/types.ts \
  src/lib/supabase.ts \
  src/types/supabase.ts \
  src/types/database.types.ts \
  src/lib/database.types.ts \
  src/lib/supabase/types.ts; do
  if [[ -f "$cand" ]]; then
    types_file="$cand"
    break
  fi
done
if [[ -z "$types_file" ]]; then
  types_file="$(find src -type f \( -name 'types.ts' -path '*supabase*' -o -name 'database.types.ts' \) 2>/dev/null | head -1 | sed 's|^\./||')"
fi
if [[ -n "$types_file" ]]; then
  echo "$types_file"
  echo "  regenerate after applying the migration."
else
  echo "NONE FOUND — no typed Supabase client file detected under src/."
fi
echo

# --- Project ref for type regeneration ---------------------------------------
echo "=== supabase project ref ==="
if [[ -f supabase/config.toml ]]; then
  grep -E '^[[:space:]]*project_id' supabase/config.toml 2>/dev/null | head -1 || echo "(project_id not in config.toml)"
else
  echo "(no supabase/config.toml — supply project ref manually for gen types)"
fi
