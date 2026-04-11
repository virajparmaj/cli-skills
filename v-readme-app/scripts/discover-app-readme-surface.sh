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
       -path '*/.pytest_cache' -o \
       -path '*/__pycache__' -o \
       -path '*/node_modules' -o \
       -path '*/dist' -o \
       -path '*/build' -o \
       -path '*/.build' -o \
       -path '*/target' -o \
       -path '*/venv' -o \
       -path '*/.venv' \) -prune -o \
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
pyproject_toml="$(find_first pyproject.toml)"
cargo_toml="$(find_first Cargo.toml)"
package_swift="$(find_first Package.swift)"
go_mod="$(find_first go.mod)"
makefile_path="$(find_first Makefile)"

entrypoints="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.build' -o \
     -path '*/target' -o \
     -path '*/venv' -o \
     -path '*/.venv' \) -prune -o \
  -maxdepth 4 -type f \( \
  -name main.py -o \
  -name __main__.py -o \
  -name app.py -o \
  -name App.tsx -o \
  -name App.jsx -o \
  -name '*App.swift' -o \
  -name main.swift -o \
  -name main.tsx -o \
  -name main.jsx -o \
  -name index.tsx -o \
  -name index.jsx -o \
  -name main.rs \
  \) -print 2>/dev/null | sort | head -n 12)"

ui_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.build' -o \
     -path '*/target' -o \
     -path '*/venv' -o \
     -path '*/.venv' -o \
     -path '*/.claude' \) -prune -o \
  -maxdepth 5 -type f \( \
  \( -name '*.swift' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.py' -o -name '*.rs' \) -a \( \
  -iname '*settings*' -o \
  -iname '*preferences*' -o \
  -iname '*menu*' -o \
  -iname '*window*' -o \
  -iname '*screen*' -o \
  -iname '*dialog*' \) \
  \) -print 2>/dev/null | sort | head -n 20)"

install_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.build' -o \
     -path '*/target' -o \
     -path '*/venv' -o \
     -path '*/.venv' \) -prune -o \
  -maxdepth 3 -type f \( \
  -name 'install.sh' -o \
  -name 'uninstall.sh' -o \
  -name 'build.sh' -o \
  -name 'build_app.sh' -o \
  -name 'setup.py' -o \
  -name 'requirements.txt' -o \
  -name 'requirements-dev.txt' -o \
  -name '.nvmrc' -o \
  -name '.python-version' \
  \) -print 2>/dev/null | sort | head -n 20)"

test_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.build' -o \
     -path '*/target' -o \
     -path '*/venv' -o \
     -path '*/.venv' \) -prune -o \
  -maxdepth 3 -type f \( \
  -path '*/tests/*' -o \
  -path '*/Tests/*' -o \
  -name 'pytest.ini' -o \
  -name 'vitest.config.*' -o \
  -name 'playwright.config.*' -o \
  -name 'jest.config.*' \
  \) -print 2>/dev/null | sort | head -n 20)"

branding_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.build' -o \
     -path '*/target' -o \
     -path '*/venv' -o \
     -path '*/.venv' \) -prune -o \
  -maxdepth 4 -type f \( \
  -iname '*logo*.png' -o \
  -iname '*logo*.jpg' -o \
  -iname '*logo*.jpeg' -o \
  -iname '*logo*.svg' -o \
  -iname '*icon*.png' -o \
  -iname '*icon*.jpg' -o \
  -iname '*icon*.jpeg' -o \
  -iname '*icon*.svg' -o \
  -iname '*appicon*.icns' \
  \) -print 2>/dev/null | sort | head -n 24)"

screenshot_dirs="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.build' -o \
     -path '*/target' -o \
     -path '*/venv' -o \
     -path '*/.venv' \) -prune -o \
  -maxdepth 4 -type d \( \
  -path '*/docs/images' -o \
  -path '*/docs/screenshots' -o \
  -path '*/assets/readme' -o \
  -path '*/assets/screenshots' -o \
  -path '*/screenshots' \
  \) -print 2>/dev/null | sort)"

route_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.build' -o \
     -path '*/target' -o \
     -path '*/venv' -o \
     -path '*/.venv' -o \
     -path '*/.next' -o \
     -path '*/.turbo' -o \
     -path '*/coverage' -o \
     -path '*/.cache' -o \
     -path '*/.parcel-cache' -o \
     -path '*/.vite' -o \
     -path '*/tests' -o \
     -path '*/Tests' -o \
     -path '*/notes' \) -prune -o \
  -maxdepth 5 -type f \( \
  -iname '*router*.ts' -o \
  -iname '*router*.tsx' -o \
  -iname '*router*.js' -o \
  -iname '*router*.jsx' -o \
  -iname '*router*.swift' -o \
  -iname '*routes*.ts' -o \
  -iname '*routes*.tsx' -o \
  -iname '*routes*.js' -o \
  -iname '*routes*.jsx' -o \
  -iname '*routes*.swift' -o \
  -path '*/app/*/page.*' -o \
  -path '*/app/page.*' -o \
  -path '*/src/app/*/page.*' -o \
  -path '*/src/app/page.*' -o \
  -path '*/pages/*.tsx' -o \
  -path '*/pages/*.ts' -o \
  -path '*/pages/*.jsx' -o \
  -path '*/pages/*.js' \
  \) -print 2>/dev/null | sort | head -n 30)"

modal_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.build' -o \
     -path '*/target' -o \
     -path '*/venv' -o \
     -path '*/.venv' -o \
     -path '*/.next' -o \
     -path '*/.turbo' -o \
     -path '*/coverage' -o \
     -path '*/.cache' -o \
     -path '*/.parcel-cache' -o \
     -path '*/.vite' \) -prune -o \
  -maxdepth 5 -type f \( \
  -iname '*modal*' -o \
  -iname '*dialog*' -o \
  -iname '*drawer*' -o \
  -iname '*popover*' -o \
  -iname '*sheet*' \
  \) -print 2>/dev/null | sort | head -n 30)"

dark_mode_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/.build' -o \
     -path '*/target' -o \
     -path '*/venv' -o \
     -path '*/.venv' -o \
     -path '*/.next' -o \
     -path '*/.turbo' -o \
     -path '*/coverage' -o \
     -path '*/.cache' -o \
     -path '*/.parcel-cache' -o \
     -path '*/.vite' \) -prune -o \
  -maxdepth 5 -type f \( \
  -name '*.js' -o \
  -name '*.jsx' -o \
  -name '*.ts' -o \
  -name '*.tsx' -o \
  -name '*.css' -o \
  -name '*.scss' -o \
  -name '*.py' -o \
  -name '*.swift' -o \
  -name '*.rs' \
  \) -print0 2>/dev/null | xargs -0 grep -Eil 'dark|ThemeProvider|prefers-color-scheme' 2>/dev/null | sort | head -n 20 || true)"

existing_screenshots=""
if [ -n "$screenshot_dirs" ]; then
  existing_screenshots="$(while IFS= read -r screenshot_dir; do
    [ -d "$screenshot_dir" ] || continue
    find "$screenshot_dir" -maxdepth 2 -type f \( \
      -iname '*.png' -o \
      -iname '*.jpg' -o \
      -iname '*.jpeg' -o \
      -iname '*.gif' -o \
      -iname '*.webp' \
    \) -print 2>/dev/null
  done <<EOF
$screenshot_dirs
EOF
)"
  existing_screenshots="$(printf '%s\n' "$existing_screenshots" | sed '/^$/d' | sort | head -n 40)"
fi

notes_dir=""
if [ -d "$repo_root/notes" ]; then
  notes_dir="$repo_root/notes"
fi

claude_dir=""
if [ -d "$repo_root/.claude" ]; then
  claude_dir="$repo_root/.claude"
fi

echo "App README Surface"
echo "Repo: $repo_root"
echo

print_matches "Primary docs" \
  "$readme_path" \
  "$claude_md"
echo

print_matches "Manifests and build files" \
  "$package_json" \
  "$pyproject_toml" \
  "$cargo_toml" \
  "$package_swift" \
  "$go_mod" \
  "$makefile_path"
echo

echo "Likely entrypoints"
if [ -n "$entrypoints" ]; then
  printf '%s\n' "$entrypoints" | sed 's/^/  - /'
else
  echo "  - none found"
fi
echo

echo "Likely user-facing UI files"
if [ -n "$ui_files" ]; then
  printf '%s\n' "$ui_files" | sed 's/^/  - /'
else
  echo "  - none found"
fi
echo

echo "Install, build, and setup files"
if [ -n "$install_files" ]; then
  printf '%s\n' "$install_files" | sed 's/^/  - /'
else
  echo "  - none found"
fi
echo

echo "Test and verification files"
if [ -n "$test_files" ]; then
  printf '%s\n' "$test_files" | sed 's/^/  - /'
else
  echo "  - none found"
fi
echo

echo "Branding assets"
if [ -n "$branding_files" ]; then
  printf '%s\n' "$branding_files" | sed 's/^/  - /'
else
  echo "  - none found"
fi
echo

echo "Stable screenshot directories"
if [ -n "$screenshot_dirs" ]; then
  printf '%s\n' "$screenshot_dirs" | sed 's/^/  - /'
else
  echo "  - none found"
fi
echo

print_block "Router and route files" "$route_files"
echo

print_block "Modal, dialog, and overlay files" "$modal_files"
echo

print_block "Dark mode indicators" "$dark_mode_files"
echo

print_block "Existing screenshot files" "$existing_screenshots"
echo

print_matches "Secondary context" \
  "$notes_dir" \
  "$claude_dir"
