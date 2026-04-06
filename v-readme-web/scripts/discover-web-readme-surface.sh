#!/usr/bin/env bash

set -euo pipefail

if [ "${1:-}" = "" ]; then
  echo "Usage: $0 /absolute/path/to/repo" >&2
  exit 1
fi

repo_root="$1"

if [ ! -d "$repo_root" ]; then
  echo "Repository path not found: $repo_root" >&2
  exit 1
fi

if [ "${repo_root#/}" = "$repo_root" ]; then
  echo "Pass an absolute repo path." >&2
  exit 1
fi

find_first() {
  local pattern="$1"
  find "$repo_root" \
    \( -path '*/.git' -o \
       -path '*/node_modules' -o \
       -path '*/.next' -o \
       -path '*/dist' -o \
       -path '*/build' -o \
       -path '*/.turbo' -o \
       -path '*/coverage' -o \
       -path '*/.cache' -o \
       -path '*/.parcel-cache' -o \
       -path '*/.vite' -o \
       -path '*/.pytest_cache' -o \
       -path '*/__pycache__' \) -prune -o \
    -maxdepth 3 -type f -name "$pattern" -print 2>/dev/null | sort | head -n 1
}

print_matches() {
  local label="$1"
  shift
  echo "$label"
  if [ "$#" -eq 0 ]; then
    echo "  - none found"
    return
  fi
  local any=0
  local path
  for path in "$@"; do
    if [ -n "$path" ]; then
      echo "  - $path"
      any=1
    fi
  done
  if [ "$any" -eq 0 ]; then
    echo "  - none found"
  fi
}

print_block() {
  local label="$1"
  local lines="$2"
  echo "$label"
  if [ -n "$lines" ]; then
    printf '%s\n' "$lines" | sed 's/^/  - /'
  else
    echo "  - none found"
  fi
}

readme_path=""
if [ -f "$repo_root/README.md" ]; then
  readme_path="$repo_root/README.md"
else
  readme_path="$(find_first README.md)"
fi

claude_md="$(find_first CLAUDE.md)"
package_json="$(find_first package.json)"
pnpm_lock="$(find_first pnpm-lock.yaml)"
yarn_lock="$(find_first yarn.lock)"
package_lock="$(find_first package-lock.json)"
next_config="$(find_first 'next.config.*')"
vite_config="$(find_first 'vite.config.*')"
astro_config="$(find_first 'astro.config.*')"
nuxt_config="$(find_first 'nuxt.config.*')"
makefile_path="$(find_first Makefile)"
justfile_path="$(find_first justfile)"
turbo_json="$(find_first turbo.json)"
playwright_config="$(find_first 'playwright.config.*')"
vitest_config="$(find_first 'vitest.config.*')"
jest_config="$(find_first 'jest.config.*')"
cypress_config="$(find_first 'cypress.config.*')"
vercel_json="$(find_first vercel.json)"
netlify_toml="$(find_first netlify.toml)"

route_surfaces="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/node_modules' -o \
     -path '*/.next' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.turbo' -o \
     -path '*/coverage' -o \
     -path '*/.cache' -o \
     -path '*/.parcel-cache' -o \
     -path '*/.vite' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' \) -prune -o \
  -maxdepth 4 \( \
  -type d \( \
    -path '*/src/app' -o \
    -path '*/src/pages' -o \
    -path '*/app' -o \
    -path '*/pages' -o \
    -path '*/src/routes' \
  \) -o \
  -type f \( \
    -name 'main.ts' -o \
    -name 'main.tsx' -o \
    -name 'main.js' -o \
    -name 'main.jsx' -o \
    -name 'src/main.ts' -o \
    -name 'src/main.tsx' -o \
    -name 'src/main.js' -o \
    -name 'src/main.jsx' \
  \) \
  \) -print 2>/dev/null | sort | head -n 20)"

ui_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/node_modules' -o \
     -path '*/.next' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.turbo' -o \
     -path '*/coverage' -o \
     -path '*/.cache' -o \
     -path '*/.parcel-cache' -o \
     -path '*/.vite' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/.claude' \) -prune -o \
  -maxdepth 4 -type f \( \
  -iname '*layout*' -o \
  -iname '*nav*' -o \
  -iname '*navbar*' -o \
  -iname '*header*' -o \
  -iname '*footer*' -o \
  -iname '*menu*' -o \
  -iname '*sidebar*' -o \
  -iname '*shell*' \
  \) -print 2>/dev/null | sort | head -n 24)"

screenshot_dirs="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/node_modules' -o \
     -path '*/.next' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.turbo' -o \
     -path '*/coverage' -o \
     -path '*/.cache' -o \
     -path '*/.parcel-cache' -o \
     -path '*/.vite' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' \) -prune -o \
  -maxdepth 4 -type d \( \
  -path '*/docs/images' -o \
  -path '*/docs/screenshots' -o \
  -path '*/assets/readme' -o \
  -path '*/assets/screenshots' -o \
  -path '*/public' -o \
  -path '*/static' \
  \) -print 2>/dev/null | sort | head -n 24)"

branding_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/node_modules' -o \
     -path '*/.next' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.turbo' -o \
     -path '*/coverage' -o \
     -path '*/.cache' -o \
     -path '*/.parcel-cache' -o \
     -path '*/.vite' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' \) -prune -o \
  -maxdepth 4 -type f \( \
  -iname '*logo*.png' -o \
  -iname '*logo*.jpg' -o \
  -iname '*logo*.jpeg' -o \
  -iname '*logo*.svg' -o \
  -iname '*brand*.png' -o \
  -iname '*brand*.jpg' -o \
  -iname '*brand*.jpeg' -o \
  -iname '*brand*.svg' -o \
  -iname '*icon*.png' -o \
  -iname '*icon*.jpg' -o \
  -iname '*icon*.jpeg' -o \
  -iname '*icon*.svg' \
  \) -print 2>/dev/null | sort | head -n 24)"

notes_dir=""
if [ -d "$repo_root/notes" ]; then
  notes_dir="$repo_root/notes"
fi

claude_dir=""
if [ -d "$repo_root/.claude" ]; then
  claude_dir="$repo_root/.claude"
fi

echo "Website README Surface"
echo "Repo: $repo_root"
echo

print_matches "Primary docs" \
  "$readme_path" \
  "$claude_md" \
  "$notes_dir" \
  "$claude_dir"
echo

print_matches "Package and lock files" \
  "$package_json" \
  "$pnpm_lock" \
  "$yarn_lock" \
  "$package_lock"
echo

print_matches "Framework config" \
  "$next_config" \
  "$vite_config" \
  "$astro_config" \
  "$nuxt_config"
echo

print_block "Main entrypoints and route surfaces" "$route_surfaces"
echo

print_block "UI, layout, and navigation files" "$ui_files"
echo

print_block "Screenshot and image asset directories" "$screenshot_dirs"
echo

print_block "Branding assets" "$branding_files"
echo

print_matches "Install, build, and test files" \
  "$package_json" \
  "$makefile_path" \
  "$justfile_path" \
  "$turbo_json" \
  "$playwright_config" \
  "$vitest_config" \
  "$jest_config" \
  "$cypress_config" \
  "$vercel_json" \
  "$netlify_toml"
