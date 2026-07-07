#!/usr/bin/env bash
#
# vercel-divergence.sh — gather deterministic evidence for why a Vite/React app
# works locally but breaks on Vercel. Read-only against the target repo except
# for the optional build in a temp dir (see --build). Never edits repo files.
#
# Emits four evidence blocks the model turns into a divergence table:
#   1) env-key diff (code references vs .env* files vs `vercel env ls`)
#   2) vercel.json config dump (rewrites / headers / functions / build)
#   3) build chunk sizes (optional; extracts every chunk over the threshold)
#   4) API base URL + CORS grep (frontend clients and serverless/FastAPI)
#
# Usage: vercel-divergence.sh [repo-path] [--build] [--chunk-kb N]
#   repo-path   target repo (default: .)
#   --build     run the project build and extract oversized chunks (slow)
#   --chunk-kb  chunk-size threshold in KB (default: 500)

set -euo pipefail

repo_path="."
do_build=0
chunk_kb=500

# ---- arg parsing (positional repo path + flags, any order) ----
while [ $# -gt 0 ]; do
  case "$1" in
    --build) do_build=1; shift ;;
    --chunk-kb)
      shift
      [ $# -gt 0 ] || { echo "--chunk-kb needs a number" >&2; exit 2; }
      chunk_kb="$1"; shift ;;
    --chunk-kb=*) chunk_kb="${1#*=}"; shift ;;
    -h|--help)
      # print only the leading header comment block (stop at first blank/non-# line)
      awk 'NR>1 && /^#/ {sub(/^# ?/,""); print; next} NR>1 {exit}' "$0"; exit 0 ;;
    -*) echo "Unknown flag: $1" >&2; exit 2 ;;
    *) repo_path="$1"; shift ;;
  esac
done

if ! [ -d "$repo_path" ]; then
  echo "Not a directory: $repo_path" >&2
  exit 1
fi
cd "$repo_path"

# grep -R over source, excluding heavy dirs. Prints file:line:match.
src_grep() {
  grep -REn "$1" . \
    --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' \
    --include='*.mjs' --include='*.cjs' --include='*.py' \
    --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
    --exclude-dir=build --exclude-dir=.next --exclude-dir=.vercel \
    --exclude-dir=coverage --exclude-dir=.venv --exclude-dir=venv \
    2>/dev/null || true
}

echo "=== repo ==="
echo "path: $(pwd)"
echo "chunk threshold: ${chunk_kb} KB"
echo "build requested: $([ "$do_build" -eq 1 ] && echo yes || echo no)"
echo

# ---------------------------------------------------------------------------
# 1) ENV-KEY DIVERGENCE
# ---------------------------------------------------------------------------
echo "=== env keys referenced in code (with file:line) ==="
# Vite client vars: import.meta.env.VITE_*  and process.env.* (serverless/node)
src_grep 'import\.meta\.env\.[A-Za-z_][A-Za-z0-9_]*' | grep -Ev 'env\.(MODE|DEV|PROD|SSR|BASE_URL)\b' || true
src_grep 'process\.env\.[A-Za-z_][A-Za-z0-9_]*' || true
echo

echo "=== env keys used in code (deduped) ==="
{
  src_grep 'import\.meta\.env\.[A-Za-z_][A-Za-z0-9_]*' \
    | grep -oE 'import\.meta\.env\.[A-Za-z_][A-Za-z0-9_]*' \
    | sed 's/import\.meta\.env\.//'
  src_grep 'process\.env\.[A-Za-z_][A-Za-z0-9_]*' \
    | grep -oE 'process\.env\.[A-Za-z_][A-Za-z0-9_]*' \
    | sed 's/process\.env\.//'
} 2>/dev/null \
  | grep -Ev '^(MODE|DEV|PROD|SSR|BASE_URL|NODE_ENV)$' \
  | sort -u > /tmp/.vd_code_keys.$$ || true
if [ -s /tmp/.vd_code_keys.$$ ]; then cat /tmp/.vd_code_keys.$$; else echo "(none found)"; fi
echo

echo "=== env files present ==="
env_files=""
for f in .env .env.local .env.development .env.development.local \
         .env.production .env.production.local .env.example; do
  if [ -f "$f" ]; then
    echo "$f"
    env_files="$env_files $f"
  fi
done
[ -n "$env_files" ] || echo "(no .env* files found)"
echo

echo "=== env keys declared in .env* files (deduped) ==="
if [ -n "$env_files" ]; then
  # shellcheck disable=SC2086
  grep -hE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=' $env_files 2>/dev/null \
    | sed -E 's/^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*).*/\1/' \
    | sort -u > /tmp/.vd_file_keys.$$ || true
  if [ -s /tmp/.vd_file_keys.$$ ]; then cat /tmp/.vd_file_keys.$$; else echo "(none)"; fi
else
  : > /tmp/.vd_file_keys.$$
  echo "(no env files to read)"
fi
echo

echo "=== env keys in code but NOT in any local .env* (likely missing on Vercel too) ==="
if [ -s /tmp/.vd_code_keys.$$ ]; then
  comm -23 /tmp/.vd_code_keys.$$ /tmp/.vd_file_keys.$$ 2>/dev/null \
    | sed 's/^/MISSING_LOCALLY: /' || true
  missing=$(comm -23 /tmp/.vd_code_keys.$$ /tmp/.vd_file_keys.$$ 2>/dev/null | wc -l | tr -d ' ')
  [ "$missing" = "0" ] && echo "(all code-referenced keys have a local declaration)"
else
  echo "(no code-referenced keys to compare)"
fi
echo

echo "=== env keys in .env.example but NOT in .env / .env.local (unset locally) ==="
if [ -f .env.example ]; then
  grep -hE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=' .env.example 2>/dev/null \
    | sed -E 's/^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*).*/\1/' | sort -u > /tmp/.vd_example.$$ || true
  local_env=""
  for f in .env .env.local .env.production; do [ -f "$f" ] && local_env="$local_env $f"; done
  if [ -n "$local_env" ]; then
    # shellcheck disable=SC2086
    grep -hE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=' $local_env 2>/dev/null \
      | sed -E 's/^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*).*/\1/' | sort -u > /tmp/.vd_localonly.$$ || true
  else
    : > /tmp/.vd_localonly.$$
  fi
  comm -23 /tmp/.vd_example.$$ /tmp/.vd_localonly.$$ 2>/dev/null | sed 's/^/EXAMPLE_ONLY: /' || true
  rm -f /tmp/.vd_example.$$ /tmp/.vd_localonly.$$
else
  echo "(no .env.example)"
fi
echo

echo "=== vercel env ls (Production) — only if Vercel CLI is authed & project linked ==="
if command -v vercel >/dev/null 2>&1; then
  if [ -f .vercel/project.json ]; then
    # `vercel env ls production` lists keys without decrypting values.
    if vercel env ls production >/tmp/.vd_vercel.$$ 2>/tmp/.vd_vercel_err.$$; then
      cat /tmp/.vd_vercel.$$
      echo
      # Extract candidate key names from the listing (first column tokens).
      grep -oE '^[A-Za-z_][A-Za-z0-9_]*' /tmp/.vd_vercel.$$ 2>/dev/null \
        | grep -Ev '^(Vercel|Environment|Variables|name|Created|Retrieving)$' \
        | sort -u > /tmp/.vd_vercel_keys.$$ || true
      echo "--- code-referenced keys NOT found in Vercel Production ---"
      if [ -s /tmp/.vd_code_keys.$$ ]; then
        comm -23 /tmp/.vd_code_keys.$$ /tmp/.vd_vercel_keys.$$ 2>/dev/null \
          | sed 's/^/MISSING_ON_VERCEL: /' || true
        m=$(comm -23 /tmp/.vd_code_keys.$$ /tmp/.vd_vercel_keys.$$ 2>/dev/null | wc -l | tr -d ' ')
        [ "$m" = "0" ] && echo "(all code-referenced keys exist on Vercel Production)"
      fi
      rm -f /tmp/.vd_vercel_keys.$$
    else
      echo "vercel env ls failed (not authed or project not linked):"
      sed 's/^/  /' /tmp/.vd_vercel_err.$$ 2>/dev/null | head -5
      echo "  -> compare code keys against the Vercel dashboard Environment Variables manually."
    fi
    rm -f /tmp/.vd_vercel.$$ /tmp/.vd_vercel_err.$$
  else
    echo "(no .vercel/project.json — run 'vercel link' first, or check the dashboard manually)"
  fi
else
  echo "(vercel CLI not installed — install with 'npm i -g vercel', or check the dashboard manually)"
fi
echo

# ---------------------------------------------------------------------------
# 2) vercel.json CONFIG
# ---------------------------------------------------------------------------
echo "=== vercel.json ==="
if [ -f vercel.json ]; then
  echo "found: vercel.json"
  cat vercel.json
  echo
  echo "--- config presence flags ---"
  for key in rewrites redirects headers routes functions builds trailingSlash cleanUrls framework buildCommand outputDirectory installCommand regions crons; do
    if grep -q "\"$key\"" vercel.json 2>/dev/null; then
      echo "HAS: $key"
    fi
  done
  # SPA rewrite check: Vite SPAs need a catch-all rewrite to index.html or "/".
  if grep -Eq '"rewrites"' vercel.json 2>/dev/null; then
    echo "SPA_REWRITE: present (good for client-side routing)"
  else
    echo "SPA_REWRITE: MISSING — deep links / refresh on sub-routes may 404 on Vercel"
  fi
else
  echo "(no vercel.json)"
  # For a Vite SPA with client routing, absence of a rewrite is a common 404-on-refresh cause.
  if [ -f vite.config.ts ] || [ -f vite.config.js ]; then
    if src_grep 'react-router' | head -1 >/dev/null 2>&1 && \
       [ -n "$(src_grep 'react-router')" ]; then
      echo "NOTE: Vite + react-router detected and no vercel.json — deep links likely 404 on refresh."
    fi
  fi
fi
echo

echo "=== build config (package.json / vite.config) ==="
if [ -f package.json ]; then
  echo "--- package.json scripts ---"
  grep -A30 '"scripts"' package.json 2>/dev/null | grep -E '":' | head -20 || true
  echo "--- build-relevant fields ---"
  grep -E '"(type|packageManager|engines)"' package.json 2>/dev/null || true
fi
for vc in vite.config.ts vite.config.js vite.config.mjs; do
  if [ -f "$vc" ]; then
    echo "--- $vc (base / build / manualChunks) ---"
    grep -nE 'base:|outDir|manualChunks|chunkSizeWarningLimit|rollupOptions|build:' "$vc" 2>/dev/null || echo "(no explicit build/chunk config — using Vite defaults)"
  fi
done
echo

# ---------------------------------------------------------------------------
# 3) BUILD + CHUNK SIZES
# ---------------------------------------------------------------------------
echo "=== oversized chunks (> ${chunk_kb} KB) ==="
if [ "$do_build" -eq 1 ]; then
  if [ -f package.json ] && grep -q '"build"' package.json 2>/dev/null; then
    echo "running build (npm run build)... this can take a minute"
    if npm run build >/tmp/.vd_build.$$ 2>&1; then
      echo "build: OK"
    else
      echo "build: FAILED — a local build failure will also fail the Vercel build"
      echo "--- last 25 lines of build output ---"
      tail -25 /tmp/.vd_build.$$ 2>/dev/null || true
    fi
    # Find emitted JS/CSS assets and report those over the threshold.
    out_dir="dist"
    grep -q 'outDir' vite.config.* 2>/dev/null && out_dir="$(grep -hoE "outDir:[^,}]*" vite.config.* 2>/dev/null | head -1 | grep -oE "'[^']*'|\"[^\"]*\"" | tr -d "'\"" || echo dist)"
    [ -n "$out_dir" ] || out_dir="dist"
    if [ -d "$out_dir" ]; then
      thresh_bytes=$((chunk_kb * 1024))
      found_big=0
      # -size uses 512-byte blocks; compare with stat for accuracy.
      while IFS= read -r asset; do
        bytes=$(wc -c < "$asset" 2>/dev/null | tr -d ' ')
        [ -n "$bytes" ] || continue
        if [ "$bytes" -gt "$thresh_bytes" ]; then
          kb=$((bytes / 1024))
          echo "BIG_CHUNK: ${kb} KB  ${asset}"
          found_big=1
        fi
      done < <(find "$out_dir" -type f \( -name '*.js' -o -name '*.css' \) 2>/dev/null)
      [ "$found_big" -eq 0 ] && echo "(no assets over ${chunk_kb} KB)"
    else
      echo "(build output dir '$out_dir' not found)"
    fi
    rm -f /tmp/.vd_build.$$
  else
    echo "(no 'build' script in package.json)"
  fi
else
  echo "(skipped — pass --build to run the build and measure chunks)"
  # Report any already-built assets from a prior build so the run is still useful.
  for od in dist build; do
    if [ -d "$od" ]; then
      echo "--- existing $od assets over ${chunk_kb} KB (from a prior build) ---"
      thresh_bytes=$((chunk_kb * 1024))
      any=0
      while IFS= read -r asset; do
        bytes=$(wc -c < "$asset" 2>/dev/null | tr -d ' ')
        [ -n "$bytes" ] || continue
        if [ "$bytes" -gt "$thresh_bytes" ]; then
          echo "BIG_CHUNK: $((bytes / 1024)) KB  ${asset}"
          any=1
        fi
      done < <(find "$od" -type f \( -name '*.js' -o -name '*.css' \) 2>/dev/null)
      [ "$any" -eq 0 ] && echo "(no existing assets over ${chunk_kb} KB)"
    fi
  done
fi
echo

# ---------------------------------------------------------------------------
# 4) API BASE URL + CORS
# ---------------------------------------------------------------------------
echo "=== API base URLs referenced in code (file:line) ==="
# Hardcoded localhost / 127.0.0.1 in frontend is a top cause of prod breakage.
src_grep 'localhost:[0-9]+' || true
src_grep '127\.0\.0\.1' || true
echo "--- hardcoded remote backend hosts (Render/Railway/Fly/ngrok/http) ---"
src_grep 'https?://[A-Za-z0-9.-]+\.(onrender\.com|up\.railway\.app|fly\.dev|ngrok[.-][A-Za-z0-9.-]+|vercel\.app|herokuapp\.com)' || true
echo "--- API base URL / fetch base assignments ---"
src_grep '(API_URL|API_BASE|BASE_URL|baseURL|apiUrl|VITE_API_URL|axios\.create)' || true
echo

echo "=== CORS configuration (serverless / FastAPI) ==="
# FastAPI CORS middleware
src_grep 'CORSMiddleware|allow_origins|allow_methods|allow_headers|allow_credentials' || true
echo "--- serverless / Vercel function CORS headers ---"
src_grep 'Access-Control-Allow-Origin|Access-Control-Allow-Methods|Access-Control-Allow-Headers' || true
echo "--- api/ serverless functions present ---"
if [ -d api ]; then
  find api -type f \( -name '*.ts' -o -name '*.js' -o -name '*.py' -o -name '*.mjs' \) 2>/dev/null | head -30
else
  echo "(no api/ directory)"
fi
echo

echo "=== wildcard vs explicit CORS origins (production risk) ==="
wildcard_hits="$(src_grep 'allow_origins=\[[[:space:]]*["'\'']\*' ; src_grep 'Access-Control-Allow-Origin.{0,12}\*')"
if [ -n "$wildcard_hits" ]; then
  echo "WILDCARD_CORS: '*' origin found — fine for open APIs, but blocks credentialed requests (allow_credentials=True + '*' is rejected by browsers)."
  printf '%s\n' "$wildcard_hits"
else
  echo "(no wildcard '*' CORS origin detected — check that the Vercel prod + preview domains are in the allow-list)"
fi
echo

# cleanup temp files
rm -f /tmp/.vd_code_keys.$$ /tmp/.vd_file_keys.$$ 2>/dev/null || true

echo "=== done ==="
echo "Next: hand this output to the v-vercel-doctor skill to produce the divergence table."
