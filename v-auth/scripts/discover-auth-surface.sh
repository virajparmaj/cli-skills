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
# No workspace restriction — this script works on any repo path.

print_if_exists() {
  local label="$1"
  shift
  local found=0

  echo "== $label =="
  for path in "$@"; do
    if [ -e "$path" ]; then
      found=1
      printf '%s\n' "$path"
    fi
  done

  if [ "$found" -eq 0 ]; then
    echo "(none found)"
  fi

  echo
}

search_files() {
  local label="$1"
  local pattern="$2"
  shift 2
  local tmp

  tmp="$(mktemp)"
  rg -l --hidden \
    --glob '!node_modules/**' \
    --glob '!dist/**' \
    --glob '!.git/**' \
    --glob '!.vercel/**' \
    --glob '!.claude/**' \
    --glob '!.venv/**' \
    --glob '!.pytest_cache/**' \
    --glob '!coverage/**' \
    "$pattern" "$@" 2>/dev/null | sort -u > "$tmp" || true

  echo "== $label =="
  if [ -s "$tmp" ]; then
    sed -n '1,200p' "$tmp"
  else
    echo "(no matches)"
  fi
  echo

  rm -f "$tmp"
}

echo "== Repo =="
printf '%s\n' "$repo"
echo

priority_context=(
  "$repo/CLAUDE.md"
  "$repo/notes/04_auth_and_roles.md"
  "$repo/notes/03_architecture.md"
  "$repo/notes/13_prompt_context.md"
  "$repo/README.md"
  "$repo/.env.example"
  "$repo/.env.local.example"
  "$repo/notes/10_deployment.md"
)

print_if_exists "Priority context (read in this order)" "${priority_context[@]}"

project_shape=(
  "$repo/package.json"
  "$repo/pyproject.toml"
  "$repo/requirements.txt"
  "$repo/backend/requirements.txt"
  "$repo/vercel.json"
  "$repo/api"
  "$repo/backend"
  "$repo/supabase/migrations"
  "$repo/src/lib/api"
  "$repo/src/providers"
  "$repo/src/contexts"
  "$repo/src/services"
  "$repo/src/hooks"
  "$repo/src/test"
  "$repo/test"
  "$repo/tests"
)

print_if_exists "Project shape" "${project_shape[@]}"

auth_search_paths=(
  "$repo/src"
  "$repo/api"
  "$repo/backend"
  "$repo/supabase"
  "$repo/notes"
  "$repo/CLAUDE.md"
  "$repo/README.md"
  "$repo/.env.example"
  "$repo/.env.local.example"
)

search_files \
  "Auth surface candidates" \
  'AuthProvider|AuthContext|useAuth|ProtectedRoute|RoleContext|supabase\.auth|onAuthStateChange|flowType|storageKey|persistSession|detectSessionInUrl|admin_token|JWT_SECRET|Authorization|Bearer|allow_origins|allow_credentials|VITE_DEMO_MODE|raw_user_meta_data|enable row level security|create policy|storage\.foldername|rate.?limit|resetPasswordForEmail|signOut' \
  "${auth_search_paths[@]}"

search_files \
  "Router and route-shell candidates" \
  'createBrowserRouter|BrowserRouter|Routes|Route|ProtectedRoute|StudioLayout|AppSidebar|TopBar|navigate\(|redirect\(' \
  "$repo/src" "$repo/notes" "$repo/README.md" "$repo/CLAUDE.md"

test_search_paths=()
for path in \
  "$repo/src/test" \
  "$repo/test" \
  "$repo/tests" \
  "$repo/backend/tests" \
  "$repo/api/tests"
do
  if [ -e "$path" ]; then
    test_search_paths+=("$path")
  fi
done

if [ "${#test_search_paths[@]}" -gt 0 ]; then
  search_files \
    "Auth and boundary tests" \
    'auth|session|ProtectedRoute|role|login|logout|token|cookie|rls|policy|bearer|rate.?limit|password reset' \
    "${test_search_paths[@]}"
else
  echo "== Auth and boundary tests =="
  echo "(no dedicated test directories found)"
  echo
fi

echo "== Suggested next reads =="
echo "1. Priority context files from the first section"
echo "2. Router entrypoints such as App.tsx and any layout-level guard files"
echo "3. Auth providers, services, hooks, or role context files"
echo "4. Backend auth helpers, API routes, and any serverless proxies"
echo "5. Supabase migrations, storage policies, and auth-related tests"
