#!/usr/bin/env bash
#
# locate-error.sh — extract file:line frames, module tokens, and error codes from
# a pasted stack trace / build error, map frames to real repo files, and print
# code context + git-blame recency for the top frames.
#
# Usage:
#   pbpaste | scripts/locate-error.sh [repo-path]
#   scripts/locate-error.sh [repo-path] < error.txt
#   scripts/locate-error.sh [repo-path] error.txt
#
# Reads the error text from stdin, OR from a file passed as $2 (or $1 if $1 is a
# readable file rather than a directory). Read-only against the target repo.

set -euo pipefail

# ---- resolve args -----------------------------------------------------------
repo_path="."
error_file=""

for arg in "$@"; do
  if [[ -d "$arg" ]]; then
    repo_path="$arg"
  elif [[ -f "$arg" ]]; then
    error_file="$arg"
  fi
done

if [[ ! -d "$repo_path" ]]; then
  echo "Not a directory: $repo_path" >&2
  exit 1
fi

# Read error text: from file if given, else stdin.
if [[ -n "$error_file" ]]; then
  err_text="$(cat "$error_file")"
elif [[ ! -t 0 ]]; then
  err_text="$(cat)"
else
  echo "No error text provided. Pipe a stack trace on stdin or pass a file." >&2
  echo "Example: pbpaste | $0 $repo_path" >&2
  exit 1
fi

if [[ -z "${err_text// }" ]]; then
  echo "=== empty input ==="
  echo "No error text received on stdin."
  exit 0
fi

cd "$repo_path"
repo_abs="$(pwd)"

is_git=false
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  is_git=true
fi

CONTEXT="${TRIAGE_CONTEXT:-15}"   # lines of context above/below each frame
MAX_FRAMES="${TRIAGE_MAX_FRAMES:-4}"

echo "=== target repo ==="
echo "$repo_abs"
[[ "$is_git" == true ]] && echo "git: yes" || echo "git: no"
echo

# ---- 1. classify the error family ------------------------------------------
# Heuristic family detection based on signature tokens. The model refines this.
echo "=== likely error family ==="
family="unknown"
if grep -qiE 'error TS[0-9]{3,5}|tsc |type .* is not assignable|has no exported member|Cannot find (name|module)' <<<"$err_text"; then
  family="typescript-build"
elif grep -qiE 'rollup|vite|esbuild|Failed to resolve import|\[plugin:|Pre-transform error|does not provide an export' <<<"$err_text"; then
  family="vite-rollup-build"
elif grep -qiE 'Traceback \(most recent call last\)|File \".*\.py\", line|ModuleNotFoundError|ImportError|pydantic|uvicorn|fastapi|joblib|sklearn|xgboost' <<<"$err_text"; then
  family="python-fastapi-traceback"
elif grep -qiE 'PGRST[0-9]+|supabase|row-level security|JWT (expired|malformed)|new row violates|violates foreign key|duplicate key value' <<<"$err_text"; then
  family="supabase"
elif grep -qiE 'Error: Command .* exited|vercel|ENOENT.*vercel|Build Failed|Deployment|serverless function|FUNCTION_INVOCATION|exceeded the maximum' <<<"$err_text"; then
  family="vercel-deploy"
elif grep -qiE 'Uncaught |React|Minified React error|Rendered (more|fewer) hooks|Cannot read propert|is not a function|Maximum update depth|Hydration' <<<"$err_text"; then
  family="react-runtime"
fi
echo "$family"
echo "(heuristic; the skill confirms the family from code)"
echo

# ---- 2. extract error codes / signatures -----------------------------------
echo "=== error codes / signatures ==="
{
  grep -oiE 'error TS[0-9]{3,5}' <<<"$err_text" || true
  grep -oiE 'PGRST[0-9]+' <<<"$err_text" || true
  grep -oiE '(ModuleNotFoundError|ImportError|TypeError|ValueError|KeyError|AttributeError|IndexError|RuntimeError|FileNotFoundError|ConnectionError|ValidationError|AssertionError)' <<<"$err_text" || true
  grep -oiE '(ENOENT|EADDRINUSE|ECONNREFUSED|ETIMEDOUT|ERR_MODULE_NOT_FOUND|MODULE_NOT_FOUND)' <<<"$err_text" || true
  grep -oiE 'Minified React error #[0-9]+' <<<"$err_text" || true
  grep -oiE 'HTTP [45][0-9][0-9]|status(Code)?[:= ]+[45][0-9][0-9]' <<<"$err_text" || true
} | sort -u | sed 's/^/  /' || true
echo

# ---- 3. extract module / package tokens ------------------------------------
echo "=== module / package tokens ==="
{
  # "Cannot find module 'x'" / "Failed to resolve import "x"" / from 'x'
  grep -oiE "(Cannot find module|Failed to resolve import|Module not found|No module named)[^'\"]*['\"][^'\"]+['\"]" <<<"$err_text" \
    | grep -oiE "['\"][^'\"]+['\"]" | tr -d "\"'" || true
  # bare python "No module named x" without quotes
  grep -oiE "No module named [A-Za-z0-9_.]+" <<<"$err_text" | awk '{print $4}' || true
} | sed "s/^/  /" | sort -u || true
echo

# ---- 4. extract file:line frames -------------------------------------------
# Match common frame shapes:
#   src/foo/bar.tsx:12:8
#   File "backend/app.py", line 42
#   at Object.<anonymous> (/abs/path/file.js:10:5)
#   ./src/x.ts (5:3)
echo "=== raw file:line frames (in order seen) ==="
frames="$(
  {
    # path:line[:col]
    grep -oiE '(/?[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+\.(tsx?|jsx?|mjs|cjs|py|json|css|scss|vue|svelte):[0-9]+(:[0-9]+)?' <<<"$err_text" || true
    # Python: File "path", line N  -> rewrite to path:N
    grep -oiE 'File "[^"]+\.py", line [0-9]+' <<<"$err_text" \
      | sed -E 's/File "([^"]+)", line ([0-9]+)/\1:\2/' || true
    # Vite/rollup: ./src/x.ts (5:3)
    grep -oiE '(\./)?([A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+\.(tsx?|jsx?|mjs|cjs|py|css|scss|vue|svelte) \([0-9]+:[0-9]+\)' <<<"$err_text" \
      | sed -E 's/ \(([0-9]+):[0-9]+\)/:\1/' || true
  } | awk '!seen[$0]++'
)"

if [[ -z "$frames" ]]; then
  echo "  (none found — no file:line frames in the pasted text)"
  echo
  echo "=== note ==="
  echo "No frames to resolve. Diagnose from the message + codes above, or ask for the full trace ONLY if no signature is present."
  exit 0
fi
echo "$frames" | sed 's/^/  /'
echo

# ---- 5. resolve frames to real repo files ----------------------------------
# Strip build noise, keep frames that actually exist in the repo, dedupe by file.
resolve_frame() {
  local raw="$1"
  local file line trailing candidate
  # split off :line:col -> file, line (drop col). The trailing group is the
  # 1 or 2 numbers after the final colon(s); the line number is the first of them.
  file="$(sed -E 's/:[0-9]+(:[0-9]+)?$//' <<<"$raw")"
  trailing="${raw#"$file":}"          # e.g. "42:8" or "42"
  line="${trailing%%:*}"              # first number = line

  # drop build-output / dependency noise
  case "$file" in
    *node_modules/*|*/dist/*|dist/*|*/build/*|build/*|*/.next/*|*/.vite/*|*/coverage/*)
      return 1 ;;
  esac

  # 1) exact / relative match
  candidate="${file#./}"
  if [[ -f "$candidate" ]]; then echo "$candidate:$line"; return 0; fi

  # 2) absolute path that lives under the repo
  if [[ "$file" == "$repo_abs"/* && -f "$file" ]]; then
    echo "${file#$repo_abs/}:$line"; return 0
  fi

  # 3) find by basename (handles /abs, dist mapping, cwd differences)
  local base matches
  base="$(basename "$file")"
  matches="$(find . \
    -path ./node_modules -prune -o \
    -path ./dist -prune -o \
    -path ./build -prune -o \
    -path './.git' -prune -o \
    -type f -name "$base" -print 2>/dev/null | sed 's|^\./||' | head -n 5)"
  if [[ -n "$matches" ]]; then
    # prefer a match whose tail matches the frame's directory suffix
    local suffix pick
    suffix="$(sed -E 's|^.*/([^/]+/[^/]+)$|\1|' <<<"$candidate")"
    pick="$(grep -F "$suffix" <<<"$matches" | head -n1 || true)"
    [[ -z "$pick" ]] && pick="$(head -n1 <<<"$matches")"
    echo "$pick:$line"
    return 0
  fi
  return 1
}

echo "=== resolved repo frames (top $MAX_FRAMES, deduped) ==="
resolved=""
count=0
while IFS= read -r raw; do
  [[ -z "$raw" ]] && continue
  if r="$(resolve_frame "$raw")"; then
    rfile="${r%:*}"
    if ! grep -qxF "$rfile" <<<"$resolved" 2>/dev/null; then
      resolved="$resolved"$'\n'"$rfile"
      echo "  $raw  ->  $r"
      count=$((count + 1))
    fi
  else
    echo "  $raw  ->  (unresolved: build/dep noise or not in repo)"
  fi
  [[ $count -ge $MAX_FRAMES ]] && break
done <<<"$frames"
echo

if [[ $count -eq 0 ]]; then
  echo "=== note ==="
  echo "No frames resolved to files in this repo. The top frame is likely in a dependency,"
  echo "generated output, or a different working directory. Diagnose from the message + codes."
  exit 0
fi

# ---- 6. print context + git recency per resolved frame ---------------------
resolved="$(sed '/^$/d' <<<"$resolved")"
while IFS= read -r rfile; do
  [[ -z "$rfile" ]] && continue
  # recover the line number for this file from the resolved list order
  ln="$(
    while IFS= read -r raw; do
      [[ -z "$raw" ]] && continue
      if r="$(resolve_frame "$raw" 2>/dev/null)"; then
        [[ "${r%:*}" == "$rfile" ]] && { echo "${r##*:}"; break; }
      fi
    done <<<"$frames"
  )"
  [[ -z "$ln" ]] && ln=1

  echo "=== frame: $rfile:$ln ==="

  total="$(wc -l <"$rfile" | tr -d ' ')"
  start=$((ln - CONTEXT)); [[ $start -lt 1 ]] && start=1
  end=$((ln + CONTEXT)); [[ $end -gt $total ]] && end=$total

  # print with line numbers, marking the offending line
  awk -v s="$start" -v e="$end" -v hit="$ln" 'NR>=s && NR<=e {
    marker = (NR==hit) ? ">>" : "  ";
    printf "%s %5d| %s\n", marker, NR, $0
  }' "$rfile"
  echo

  if [[ "$is_git" == true ]]; then
    echo "--- git recency (last commit touching line $ln) ---"
    if blame_out="$(git --no-pager blame -L "$ln,$ln" --line-porcelain --date=short -- "$rfile" 2>/dev/null)"; then
      b_hash="$(head -n1 <<<"$blame_out" | awk '{print substr($1,1,8)}')"
      b_author="$(grep -m1 '^author ' <<<"$blame_out" | cut -d' ' -f2-)"
      b_date="$(grep -m1 '^author-time ' <<<"$blame_out" | awk '{print $2}')"
      [[ -n "$b_date" ]] && b_date="$(date -r "$b_date" +%Y-%m-%d 2>/dev/null || echo "$b_date")"
      echo "  commit $b_hash  by ${b_author:-unknown}  on ${b_date:-unknown}"
    else
      echo "  (blame unavailable — line may be uncommitted)"
    fi
    echo "--- file last modified ---"
    git --no-pager log -1 --date=short --format='  %h  %ad  %an  %s' -- "$rfile" 2>/dev/null \
      || echo "  (no git history for this file)"
    echo
  fi
done <<<"$resolved"

echo "=== done ==="
