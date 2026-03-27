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

section() {
  printf '\n== %s ==\n' "$1"
}

print_list_or_none() {
  local printed=0
  for item in "$@"; do
    if [ -e "$item" ]; then
      printf '%s\n' "$item"
      printed=1
    fi
  done

  if [ "$printed" -eq 0 ]; then
    echo "(none found)"
  fi
}

search_files() {
  local label="$1"
  local pattern="$2"
  shift 2

  local targets=()
  for path in "$@"; do
    if [ -e "$path" ]; then
      targets+=("$path")
    fi
  done

  section "$label"

  if [ "${#targets[@]}" -eq 0 ]; then
    echo "(no searchable paths)"
    return
  fi

  local tmp
  tmp="$(mktemp)"

  rg -n --hidden \
    --glob '!node_modules/**' \
    --glob '!dist/**' \
    --glob '!.git/**' \
    --glob '!.venv/**' \
    --glob '!coverage/**' \
    --glob '!.next/**' \
    --glob '!build/**' \
    "$pattern" "${targets[@]}" 2>/dev/null | sed -n '1,200p' > "$tmp" || true

  if [ -s "$tmp" ]; then
    cat "$tmp"
  else
    echo "(no matches)"
  fi

  rm -f "$tmp"
}

collect_env_names() {
  local out
  out="$(rg -o --no-filename --hidden \
    --glob '!node_modules/**' \
    --glob '!.git/**' \
    --glob '!dist/**' \
    --glob '!build/**' \
    --glob '!.next/**' \
    '(VITE|NEXT_PUBLIC|NUXT_PUBLIC|REACT_APP|SUPABASE|DATABASE|POSTGRES|MYSQL|MONGO|REDIS|JWT|AUTH|OPENAI|ANTHROPIC|STRIPE|SENTRY|VERCEL|NETLIFY|RENDER|CLOUDINARY|AWS)_[A-Z0-9_]+' \
    "$repo" 2>/dev/null | sort -u | sed -n '1,200p' || true)"

  if [ -n "$out" ]; then
    printf '%s\n' "$out"
  else
    echo "(none found)"
  fi
}

section "Repo"
printf '%s\n' "$repo"

section "Primary docs and manifests"
print_list_or_none \
  "$repo/README.md" \
  "$repo/README.mdx" \
  "$repo/CLAUDE.md" \
  "$repo/package.json" \
  "$repo/pyproject.toml" \
  "$repo/requirements.txt" \
  "$repo/requirements-dev.txt" \
  "$repo/go.mod" \
  "$repo/Cargo.toml"

section "Core app and backend directories"
print_list_or_none \
  "$repo/src" \
  "$repo/app" \
  "$repo/components" \
  "$repo/pages" \
  "$repo/api" \
  "$repo/lib" \
  "$repo/hooks" \
  "$repo/services" \
  "$repo/supabase" \
  "$repo/server" \
  "$repo/backend" \
  "$repo/ml"

section "Deployment and environment files"
print_list_or_none \
  "$repo/render.yaml" \
  "$repo/vercel.json" \
  "$repo/netlify.toml" \
  "$repo/Dockerfile" \
  "$repo/docker-compose.yml" \
  "$repo/.env.example" \
  "$repo/.env.local.example" \
  "$repo/.env"

section "Auth/DB schema and migration clues"
find "$repo" -maxdepth 4 -type f \
  \( -name '*.sql' -o -name 'schema.prisma' -o -name '*migration*' -o -name '*migrations*' -o -name 'drizzle.config.*' -o -name '*supabase*' \) \
  ! -path '*/node_modules/*' \
  ! -path '*/dist/*' \
  ! -path '*/build/*' \
  2>/dev/null | sort | sed -n '1,200p' || true

search_files \
  "Route definition clues" \
  'createBrowserRouter|BrowserRouter|Routes|Route|useRoutes|next/navigation|next/router|app\.get\(|router\.|APIRouter|FastAPI\(' \
  "$repo/src" "$repo/app" "$repo/pages" "$repo/api" "$repo/backend" "$repo/server"

search_files \
  "Auth clues" \
  'AuthProvider|AuthContext|useAuth|ProtectedRoute|supabase\.auth|next-auth|clerk|firebase/auth|signIn|signUp|resetPassword|jwt|bearer|session|role|RLS|policy' \
  "$repo/src" "$repo/app" "$repo/pages" "$repo/api" "$repo/backend" "$repo/server" "$repo/supabase" "$repo/lib"

search_files \
  "Database access clues" \
  'createClient\(|supabase\.from\(|prisma\.|drizzle\.|knex\(|sequelize|mongoose|sqlalchemy|TypeORM|SELECT |INSERT INTO|UPDATE ' \
  "$repo/src" "$repo/app" "$repo/pages" "$repo/api" "$repo/backend" "$repo/server" "$repo/lib" "$repo/services" "$repo/supabase"

search_files \
  "Frontend API call clues" \
  'fetch\(|axios\.|ky\.|graphql|/api/|onrender\.com|vercel\.app|supabase\.rpc' \
  "$repo/src" "$repo/app" "$repo/pages" "$repo/components" "$repo/lib" "$repo/services" "$repo/hooks"

section "Environment variable names used in repository"
collect_env_names

search_files \
  "Deployment clues in code and config" \
  'vercel|netlify|render|docker|fly\.io|railway|supabase|CORS|origin|process\.env|import\.meta\.env' \
  "$repo/package.json" "$repo/vercel.json" "$repo/netlify.toml" "$repo/render.yaml" "$repo/Dockerfile" "$repo/src" "$repo/api" "$repo/backend" "$repo/server"

section "Suggested next reads for note generation"
echo "1. README + runtime manifest files"
echo "2. Router entry files and page/component tree"
echo "3. API client files and backend route handlers"
echo "4. Auth/session modules and role checks"
echo "5. DB schema/migration files and storage policies"
echo "6. Deployment config and env templates"
