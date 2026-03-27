#!/usr/bin/env bash

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $(basename "$0") <repo-root>" >&2
  exit 1
fi

cd "$1"
repo="$(pwd)"

section() {
  printf '\n== %s ==\n' "$1"
}

print_or_none() {
  if [ -n "${1:-}" ]; then
    printf '%s\n' "$1"
  else
    printf '(none)\n'
  fi
}

build_targets() {
  local targets=()
  for path in \
    "$repo/src" \
    "$repo/api" \
    "$repo/package.json" \
    "$repo/index.html" \
    "$repo/vercel.json" \
    "$repo/vite.config.ts" \
    "$repo/vite.config.js" \
    "$repo/vite.config.mts" \
    "$repo/vitest.config.ts" \
    "$repo/vitest.config.js" \
    "$repo/.size-limit.json"
  do
    if [ -e "$path" ]; then
      targets+=("$path")
    fi
  done
  printf '%s\n' "${targets[@]}"
}

build_font_targets() {
  local targets=()
  for path in "$repo/src" "$repo/index.html"; do
    if [ -e "$path" ]; then
      targets+=("$path")
    fi
  done
  printf '%s\n' "${targets[@]}"
}

build_delivery_targets() {
  local targets=()
  for path in "$repo/vercel.json" "$repo/api"; do
    if [ -e "$path" ]; then
      targets+=("$path")
    fi
  done
  printf '%s\n' "${targets[@]}"
}

section "Repo"
printf '%s\n' "$repo"

section "Prior context"
prior_context="$(
  {
    [ -f "$repo/CLAUDE.md" ] && printf '%s\n' "$repo/CLAUDE.md"
    if [ -d "$repo/notes" ]; then
      find "$repo/notes" -maxdepth 1 -type f \
        \( -iname '*known*' -o -iname '*perf*' -o -name '03_architecture.md' -o -name '13_prompt_context.md' \) \
        | sort
    fi
    find "$repo" -maxdepth 2 -type f \
      \( -name '.size-limit.json' -o -name 'bundlewatch.config.*' -o -name 'lighthouserc*' -o -name 'vitest.config.*' \) \
      | sort
  } 2>/dev/null
)"
print_or_none "$prior_context"

section "Core files"
core_files="$(
  find "$repo" -maxdepth 2 \
    ! -path "$repo/dist" ! -path "$repo/dist/*" \
    ! -path "$repo/node_modules" ! -path "$repo/node_modules/*" \
    \( -name 'package.json' -o -name 'vite.config.*' -o -name 'index.html' -o -name 'vercel.json' \
       -o -path '*/src/App.*' -o -path '*/src/main.*' -o -path '*/src/contexts' \
       -o -path '*/src/store' -o -path '*/src/providers' -o -path '*/src/services' \
       -o -path '*/src/lib' -o -path '*/public' -o -path '*/api' \) \
    | sort
)"
print_or_none "$core_files"

targets=()
while IFS= read -r line; do
  [ -n "$line" ] && targets+=("$line")
done < <(build_targets)

font_targets=()
while IFS= read -r line; do
  [ -n "$line" ] && font_targets+=("$line")
done < <(build_font_targets)

delivery_targets=()
while IFS= read -r line; do
  [ -n "$line" ] && delivery_targets+=("$line")
done < <(build_delivery_targets)

section "Route, state, and data markers"
if [ ${#targets[@]} -gt 0 ]; then
  markers="$(
    rg -n -F --glob '!**/node_modules/**' \
      -e 'manualChunks' \
      -e 'lazy(' \
      -e 'React.lazy' \
      -e '<Route' \
      -e 'QueryClient' \
      -e 'createContext' \
      -e 'useShallow' \
      -e 'useVirtualizer' \
      -e '.from(' \
      -e '.select(' \
      -e "select('*')" \
      -e 'Promise.all' \
      -e 'setInterval(' \
      "${targets[@]}" || true
  )"
  print_or_none "$markers"
else
  print_or_none ""
fi

section "Font and delivery markers"
font_markers=""
delivery_markers=""

if [ ${#font_targets[@]} -gt 0 ]; then
  font_markers="$(
    rg -n -F --glob '!**/node_modules/**' \
      -e '@import url(' \
      -e 'fonts.googleapis.com' \
      -e 'fonts.gstatic.com' \
      -e 'preconnect' \
      -e 'rel="preload"' \
      -e 'font-display:' \
      "${font_targets[@]}" || true
  )"
fi

if [ ${#delivery_targets[@]} -gt 0 ]; then
  delivery_markers="$(
    rg -n -F --glob '!**/node_modules/**' \
      -e 'Cache-Control' \
      -e 'Content-Security-Policy' \
      -e 'rewrites' \
      "${delivery_targets[@]}" || true
  )"
fi

if [ -n "$font_markers" ] || [ -n "$delivery_markers" ]; then
  [ -n "$font_markers" ] && printf '%s\n%s\n' '-- Fonts --' "$font_markers"
  [ -n "$delivery_markers" ] && printf '%s\n%s\n' '-- Delivery --' "$delivery_markers"
else
  print_or_none ""
fi

section "Large public assets (>200 KB)"
if [ -d "$repo/public" ]; then
  large_assets="$(find "$repo/public" -type f -size +200k -exec ls -lh {} + | sort -k5 -h || true)"
  print_or_none "$large_assets"
else
  print_or_none ""
fi
