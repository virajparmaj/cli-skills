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
  rg -n --no-heading --color never \
    -g '!**/node_modules/**' \
    -g '!**/dist/**' \
    -g '!**/build/**' \
    -g '!**/coverage/**' \
    -g '!**/.claude/**' \
    -g '!**/.vercel/**' \
    -g '!**/*.tsbuildinfo' \
    "$pattern" "$repo" 2>/dev/null | sed -n '1,40p' || true
}

run_rg_server() {
  local pattern=$1
  local paths=()
  [ -d "$repo/api" ] && paths+=("$repo/api")
  [ -d "$repo/backend" ] && paths+=("$repo/backend")
  [ -d "$repo/supabase/functions" ] && paths+=("$repo/supabase/functions")

  if [ ${#paths[@]} -eq 0 ]; then
    return 0
  fi

  rg -n --no-heading --color never "$pattern" "${paths[@]}" 2>/dev/null | sed -n '1,40p' || true
}

docs="$(find "$repo" -maxdepth 2 \( -name 'CLAUDE.md' -o -name 'README.md' -o -name '.env.example' -o -path '*/notes/*.md' \) 2>/dev/null | sort | sed -n '1,80p')"
manifests="$(find "$repo" -maxdepth 2 \( -name 'package.json' -o -name 'pyproject.toml' -o -name 'vercel.json' -o -name 'render.yaml' -o -name 'Dockerfile' -o -name 'fly.toml' \) 2>/dev/null | sort | sed -n '1,40p')"
server_dirs="$(find "$repo" \( -path "$repo/api" -o -path "$repo/backend" -o -path "$repo/supabase/functions" -o -path "$repo/supabase/migrations" \) -type d 2>/dev/null | sort | sed -n '1,40p')"

env_refs="$(run_rg 'VITE_[A-Z0-9_]+|import\.meta\.env\.[A-Z0-9_]+|process\.env\.[A-Z0-9_]+' )"
endpoint_refs="$(
  {
    run_rg_server '@app\.(get|post|put|patch|delete)|app\.(get|post|put|patch|delete)|router\.(get|post|put|patch|delete)|export default async function handler|export default function handler'
    run_rg 'supabase\.functions\.invoke'
  } | sed -n '1,40p'
)"
auth_refs="$(run_rg 'supabase\.auth|ProtectedRoute|PrivateRoute|RoleContext|canAccess|persistSession|localStorage|sessionStorage' )"
storage_refs="$(run_rg 'supabase\.storage\.from|CREATE POLICY|ENABLE ROW LEVEL SECURITY|WITH CHECK|type=\"file\"|type=.file.|FormData|Blob' )"
headers_refs="$(run_rg 'Content-Security-Policy|Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Referrer-Policy|Permissions-Policy|CORSMiddleware|allow_origins|allow_methods|allow_headers|helmet' )"
validation_refs="$(run_rg 'z\.object|from .+ import BaseModel|BaseModel|pydantic|validation|sanitize|dangerouslySetInnerHTML|innerHTML|eval\(|new Function\(' )"
test_refs="$(
  find "$repo" \
    \( -path '*/node_modules/*' -o -path '*/.claude/*' -o -path '*/dist/*' -o -path '*/build/*' \) -prune -o \
    \( -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.ts' -o -name '*.spec.tsx' -o -path '*/__tests__/*' -o -path '*/tests/*' \) \
    -print 2>/dev/null | sort | sed -n '1,60p'
)"

printf '# Attack Surface Inputs\n'
printf -- '- Repo: %s\n' "$repo"

print_section "Project Context"
print_block "Priority docs" "$docs"
print_block "Manifests and deployment files" "$manifests"
print_block "Server and policy directories" "$server_dirs"

print_section "Security-Relevant References"
print_block "Env vars and secret boundaries" "$env_refs"
print_block "Public endpoints and handlers" "$endpoint_refs"
print_block "Auth, sessions, and route protection" "$auth_refs"
print_block "RLS, storage, and upload paths" "$storage_refs"
print_block "Headers, CORS, and deployment" "$headers_refs"
print_block "Validation and injection sinks" "$validation_refs"
print_block "Tests" "$test_refs"
