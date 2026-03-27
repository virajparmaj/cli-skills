#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <repo-path>" >&2
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required." >&2
  exit 1
fi

repo_input=$1
if [ ! -d "$repo_input" ]; then
  echo "Repo not found: $repo_input" >&2
  exit 1
fi

repo="$(cd "$repo_input" && pwd)"

exclude_globs=(
  -g '!**/node_modules/**'
  -g '!**/dist/**'
  -g '!**/build/**'
  -g '!**/out/**'
  -g '!**/.next/**'
  -g '!**/.nuxt/**'
  -g '!**/.git/**'
  -g '!**/.venv/**'
  -g '!**/venv/**'
  -g '!**/coverage/**'
  -g '!**/__pycache__/**'
  -g '!**/.turbo/**'
  -g '!**/.cache/**'
)

print_section() {
  printf '\n## %s\n' "$1"
}

print_block() {
  local title=$1
  local body=$2
  printf '\n### %s\n' "$title"
  if [ -n "$body" ]; then
    printf '%s\n' "$body"
  else
    printf '(none found)\n'
  fi
}

run_rg() {
  local pattern=$1
  shift || true
  rg -n --no-heading --color never "${exclude_globs[@]}" "$pattern" "$repo" "$@" 2>/dev/null | sed -n '1,60p' || true
}

run_find() {
  find "$repo" \
    \( -path '*/node_modules/*' -o -path '*/dist/*' -o -path '*/build/*' -o -path '*/out/*' -o -path '*/.next/*' -o -path '*/.nuxt/*' -o -path '*/.git/*' -o -path '*/.venv/*' -o -path '*/venv/*' -o -path '*/coverage/*' -o -path '*/__pycache__/*' -o -path '*/.turbo/*' -o -path '*/.cache/*' \) -prune -o \
    "$@" 2>/dev/null
}

docs="$(run_find -maxdepth 3 \( -name 'CLAUDE.md' -o -iname 'README*' -o -path '*/docs/*.md' -o -path '*/notes/*.md' \) -print | sort | sed -n '1,80p')"
manifests="$(run_find -maxdepth 3 \( -name 'package.json' -o -name 'package-lock.json' -o -name 'pnpm-lock.yaml' -o -name 'yarn.lock' -o -name 'bun.lockb' -o -name 'tsconfig.json' -o -name 'tsconfig.*.json' -o -name 'pyproject.toml' -o -name 'poetry.lock' -o -name 'requirements*.txt' -o -name 'Pipfile' -o -name 'Pipfile.lock' -o -name 'go.mod' -o -name 'go.sum' -o -name 'Cargo.toml' -o -name 'Cargo.lock' -o -name 'Gemfile' -o -name 'Gemfile.lock' -o -name 'composer.json' -o -name 'composer.lock' \) -print | sort | sed -n '1,120p')"
tooling="$(run_find -maxdepth 3 \( -name 'vite.config.*' -o -name 'next.config.*' -o -name 'nuxt.config.*' -o -name 'webpack.config.*' -o -name 'rollup.config.*' -o -name 'esbuild.*' -o -name 'turbo.json' -o -name 'nx.json' -o -name 'vercel.json' -o -name 'netlify.toml' -o -name 'render.yaml' -o -name 'fly.toml' -o -name 'Dockerfile' -o -name 'Dockerfile.*' -o -name 'docker-compose*.yml' -o -name 'docker-compose*.yaml' -o -path '*/.github/workflows/*.yml' -o -path '*/.github/workflows/*.yaml' \) -print | sort | sed -n '1,120p')"
scripts="$(run_find -maxdepth 4 \( -path '*/scripts/*' -o -path '*/bin/*' -o -name '*.sh' -o -name 'Makefile' -o -name 'justfile' \) -type f -print | sort | sed -n '1,120p')"
tests="$(run_find \( -path '*/__tests__/*' -o -path '*/tests/*' -o -name '*.test.*' -o -name '*.spec.*' \) -print | sort | sed -n '1,120p')"
entrypoints="$(run_find -maxdepth 4 \( -name 'main.ts' -o -name 'main.tsx' -o -name 'main.js' -o -name 'main.jsx' -o -name 'index.ts' -o -name 'index.tsx' -o -name 'index.js' -o -name 'index.jsx' -o -name 'server.ts' -o -name 'server.js' -o -name 'app.ts' -o -name 'app.js' -o -name 'cli.ts' -o -name 'cli.js' \) -print | sort | sed -n '1,120p')"
package_scripts="$(run_rg '\"(dev|start|build|test|lint|typecheck|prepare|postinstall|release|deploy|analyze|bench|perf)\"\\s*:' | sed -n '1,80p')"
sync_refs="$(run_rg 'readFileSync|writeFileSync|readdirSync|statSync|execSync|spawnSync|globSync|rmSync|cpSync' | sed -n '1,80p')"
polling_refs="$(run_rg 'setInterval\\(|refetchInterval|pollInterval|fs\\.watch|watch\\(|chokidar|watchman' | sed -n '1,80p')"
io_refs="$(run_rg 'readFile\\(|writeFile\\(|readdir\\(|stat\\(|copyFile\\(|createReadStream\\(|createWriteStream\\(|fetch\\(|axios\\.|got\\(|request\\(' | sed -n '1,80p')"
reparse_refs="$(run_rg 'JSON\\.parse\\(|JSON\\.stringify\\(|yaml\\.parse\\(|safeLoad\\(|parse\\(' | sed -n '1,80p')"
background_refs="$(run_rg 'cron|scheduleJob|queue|worker|bullmq|agenda|retry|backoff|debounce|throttle' | sed -n '1,80p')"
dup_candidates="$(run_rg 'TODO|FIXME|deprecated|legacy|unused|dead code|remove me|temporary' | sed -n '1,80p')"
large_files="$(run_find -type f -exec stat -f '%z %N' {} + | sort -nr | sed -n '1,25p')"

printf '# Repo Surface Map\n'
printf -- '- Repo: %s\n' "$repo"

print_section "Project Context"
print_block "Priority docs" "$docs"
print_block "Dependency manifests and lockfiles" "$manifests"
print_block "Build, deploy, and CI files" "$tooling"
print_block "Scripts and task runners" "$scripts"
print_block "Entrypoints and startup files" "$entrypoints"
print_block "Tests" "$tests"

print_section "Likely Audit Hotspots"
print_block "Package scripts" "$package_scripts"
print_block "Synchronous filesystem or process work" "$sync_refs"
print_block "Polling, watchers, and repeated refresh" "$polling_refs"
print_block "File and network I/O" "$io_refs"
print_block "Repeated parsing or serialization patterns" "$reparse_refs"
print_block "Background jobs, queues, and retries" "$background_refs"
print_block "Legacy or cleanup markers" "$dup_candidates"

print_section "Size Clues"
print_block "Largest files outside generated folders" "$large_files"
