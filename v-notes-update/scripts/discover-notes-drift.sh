#!/usr/bin/env bash

set -euo pipefail

usage() {
  echo "Usage: $0 /absolute/path/to/repo" >&2
  exit 1
}

if [ "${1:-}" = "" ]; then
  usage
fi

repo_input="$1"

if [ ! -d "$repo_input" ]; then
  echo "Repository not found: $repo_input" >&2
  exit 1
fi

repo="$(cd "$repo_input" && pwd)"
notes_dir="$repo/notes"

canonical=(
  "00_overview.md"
  "01_features.md"
  "02_design_system.md"
  "03_architecture.md"
  "04_auth_and_roles.md"
  "05_database_schema.md"
  "06_api_contracts.md"
  "07_user_flows.md"
  "08_pages_and_routes.md"
  "09_dev_setup.md"
  "10_deployment.md"
  "11_known_issues.md"
  "12_roadmap.md"
  "13_prompt_context.md"
)

section() {
  printf '\n== %s ==\n' "$1"
}

is_git_repo() {
  git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1
}

contains() {
  local needle="$1"
  shift
  for item in "$@"; do
    if [ "$item" = "$needle" ]; then
      return 0
    fi
  done
  return 1
}

append_once() {
  local value="$1"
  shift
  local -n arr_ref="$1"
  for existing in "${arr_ref[@]:-}"; do
    if [ "$existing" = "$value" ]; then
      return
    fi
  done
  arr_ref+=("$value")
}

section "Repo"
printf '%s\n' "$repo"

section "Notes directory"
if [ -d "$notes_dir" ]; then
  printf '%s\n' "$notes_dir"
else
  echo "(notes directory not found)"
fi

section "Canonical notes coverage"
missing=()
for file in "${canonical[@]}"; do
  if [ -f "$notes_dir/$file" ]; then
    printf 'present: %s\n' "$file"
  else
    printf 'missing: %s\n' "$file"
    missing+=("$file")
  fi
done

section "Extra notes files (non-canonical)"
if [ -d "$notes_dir" ]; then
  extras_found=0
  while IFS= read -r path; do
    base="$(basename "$path")"
    if ! contains "$base" "${canonical[@]}"; then
      printf '%s\n' "$base"
      extras_found=1
    fi
  done < <(find "$notes_dir" -maxdepth 1 -type f -name '*.md' | sort)

  if [ "$extras_found" -eq 0 ]; then
    echo "(none found)"
  fi
else
  echo "(notes directory not found)"
fi

section "Stale marker scan in notes"
if [ -d "$notes_dir" ]; then
  rg -n -i --glob '*.md' 'TODO|TBD|coming soon|placeholder|mock|to be implemented|later|WIP|not finalized' "$notes_dir" | sed -n '1,200p' || echo "(no stale markers found)"
else
  echo "(notes directory not found)"
fi

section "Changed files (git working tree)"
changed=()
if is_git_repo; then
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    file_path="${line:3}"
    changed+=("$file_path")
    printf '%s\n' "$file_path"
  done < <(git -C "$repo" status --porcelain)

  if [ "${#changed[@]}" -eq 0 ]; then
    echo "(no local changes)"
  fi
else
  echo "(not a git repository)"
fi

section "Likely impacted notes from changed files"
impacted=()

for file in "${changed[@]:-}"; do
  case "$file" in
    notes/*)
      base="$(basename "$file")"
      append_once "$base" impacted
      ;;
    src/pages/*|src/views/*|app/*|pages/*)
      append_once "00_overview.md" impacted
      append_once "01_features.md" impacted
      append_once "07_user_flows.md" impacted
      append_once "08_pages_and_routes.md" impacted
      ;;
    src/components/*|src/styles/*|src/theme/*|tailwind.config.*)
      append_once "01_features.md" impacted
      append_once "02_design_system.md" impacted
      ;;
    src/lib/*|src/services/*|src/hooks/*|src/store/*|src/context/*)
      append_once "01_features.md" impacted
      append_once "03_architecture.md" impacted
      append_once "06_api_contracts.md" impacted
      ;;
    api/*|backend/*|server/*|ml/*)
      append_once "03_architecture.md" impacted
      append_once "06_api_contracts.md" impacted
      append_once "10_deployment.md" impacted
      append_once "11_known_issues.md" impacted
      ;;
    supabase/*|prisma/*|drizzle/*|migrations/*|*migration*.sql|*.sql)
      append_once "03_architecture.md" impacted
      append_once "04_auth_and_roles.md" impacted
      append_once "05_database_schema.md" impacted
      append_once "06_api_contracts.md" impacted
      ;;
    vercel.json|render.yaml|netlify.toml|Dockerfile|docker-compose.yml|.github/workflows/*)
      append_once "03_architecture.md" impacted
      append_once "09_dev_setup.md" impacted
      append_once "10_deployment.md" impacted
      ;;
    package.json|pnpm-lock.yaml|yarn.lock|package-lock.json|bun.lockb|bun.lock|README.md|CLAUDE.md|.env.example|.env.local.example)
      append_once "00_overview.md" impacted
      append_once "09_dev_setup.md" impacted
      append_once "13_prompt_context.md" impacted
      ;;
  esac
done

if [ "${#impacted[@]}" -gt 0 ]; then
  printf '%s\n' "${impacted[@]}" | sort -u
else
  echo "(no impacted notes inferred from local git changes)"
fi

section "Core repo surface (quick pointers)"
for path in \
  "$repo/README.md" \
  "$repo/package.json" \
  "$repo/src" \
  "$repo/app" \
  "$repo/pages" \
  "$repo/components" \
  "$repo/api" \
  "$repo/backend" \
  "$repo/server" \
  "$repo/supabase" \
  "$repo/vercel.json" \
  "$repo/render.yaml" \
  "$repo/netlify.toml" \
  "$repo/Dockerfile" \
  "$repo/.env.example"
do
  if [ -e "$path" ]; then
    printf '%s\n' "$path"
  fi
done

section "Suggested update order"
echo "1. Read existing notes files that the impacted list points to"
echo "2. Verify each claim against current code and configs"
echo "3. Edit stale sections in place, remove redundancy"
echo "4. Create missing canonical notes files only if required"
echo "5. Keep sequence and naming unchanged"
