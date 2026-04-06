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
go_mod="$(find_first go.mod)"
makefile_path="$(find_first Makefile)"

entrypoints="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
     -path '*/venv' -o \
     -path '*/.venv' \) -prune -o \
  -maxdepth 3 -type f \( \
  -name main.py -o \
  -name __main__.py -o \
  -name app.py -o \
  -name App.tsx -o \
  -name App.jsx -o \
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
     -path '*/venv' -o \
     -path '*/.venv' -o \
     -path '*/.claude' \) -prune -o \
  -maxdepth 4 -type f \( \
  -iname '*settings*' -o \
  -iname '*preferences*' -o \
  -iname '*menu*' -o \
  -iname '*window*' -o \
  -iname '*screen*' -o \
  -iname '*dialog*' \
  \) -print 2>/dev/null | sort | head -n 20)"

install_files="$(find "$repo_root" \
  \( -path '*/.git' -o \
     -path '*/.pytest_cache' -o \
     -path '*/__pycache__' -o \
     -path '*/node_modules' -o \
     -path '*/dist' -o \
     -path '*/build' -o \
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
     -path '*/venv' -o \
     -path '*/.venv' \) -prune -o \
  -maxdepth 3 -type f \( \
  -path '*/tests/*' -o \
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
     -path '*/venv' -o \
     -path '*/.venv' \) -prune -o \
  -maxdepth 4 -type d \( \
  -path '*/docs/images' -o \
  -path '*/docs/screenshots' -o \
  -path '*/assets/readme' -o \
  -path '*/assets/screenshots' -o \
  -path '*/screenshots' \
  \) -print 2>/dev/null | sort)"

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

print_matches "Secondary context" \
  "$notes_dir" \
  "$claude_dir"
