#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /absolute/path/to/repo" >&2
  exit 1
fi

repo="$1"
if [ ! -d "$repo" ]; then
  echo "Error: directory not found: $repo" >&2
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "Error: rg is required but not installed" >&2
  exit 1
fi

cd "$repo"

echo "== Repo =="
echo "$repo"

manifests=()
while IFS= read -r manifest; do
  [ -n "$manifest" ] && manifests+=("$manifest")
done < <(
  rg --files \
    -g '**/manifest.json' \
    -g '!**/node_modules/**' \
    -g '!**/.git/**' \
    -g '!**/dist/**' \
    -g '!**/build/**'
)

echo
echo "== Manifest Files =="
if [ "${#manifests[@]}" -eq 0 ]; then
  echo "No manifest.json files found."
  exit 2
fi
printf '%s\n' "${manifests[@]}"

echo
echo "== Manifest Key Fields =="
for manifest in "${manifests[@]}"; do
  echo
  echo "-- ${manifest} --"
  rg -n '"manifest_version"|"name"|"version"|"permissions"|"host_permissions"|"optional_permissions"|"background"|"content_scripts"|"action"|"externally_connectable"|"web_accessible_resources"' "$manifest" || true
done

echo
echo "== Risky Permission Signals =="
for manifest in "${manifests[@]}"; do
  echo
  echo "-- ${manifest} --"
  rg -n '"\*://\*/\*"|"tabs"|"cookies"|"webRequest"|"declarativeNetRequest"|"scripting"|"history"|"downloads"|"management"|"clipboard(Read|Write)"' "$manifest" || true
done

echo
echo "== Privacy / Policy / Listing Artifacts =="
rg --files \
  -g '*privacy*' \
  -g '*policy*' \
  -g '*terms*' \
  -g '*store*' \
  -g '*listing*' \
  -g '*icon*' \
  -g '*screenshot*' \
  -g 'README*' | head -n 300 || true

echo
echo "== Security Risk Patterns =="
rg -n --hidden \
  --glob '!**/node_modules/**' \
  --glob '!**/.git/**' \
  --glob '!**/dist/**' \
  --glob '!**/build/**' \
  '(eval\s*\(|new\s+Function\s*\(|setTimeout\s*\(\s*["'"'"'`]|setInterval\s*\(\s*["'"'"'`]|innerHTML\s*=|document\.write\s*\(|chrome\.scripting\.executeScript|chrome\.tabs\.executeScript|atob\s*\(|btoa\s*\(|fetch\s*\(\s*["'"'"'`]http://|XMLHttpRequest\s*\()' \
  | head -n 500 || true

echo
echo "== External Endpoint Signals =="
rg -n --hidden \
  --glob '!**/node_modules/**' \
  --glob '!**/.git/**' \
  --glob '!**/dist/**' \
  --glob '!**/build/**' \
  'https?://[A-Za-z0-9._~:/?#\[\]@!$&'"'"'()*+,;=%-]+' \
  | head -n 500 || true

echo
echo "== Potential Secrets / Sensitive Tokens =="
rg -n --hidden \
  --glob '!**/node_modules/**' \
  --glob '!**/.git/**' \
  --glob '!**/dist/**' \
  --glob '!**/build/**' \
  '(AIza[0-9A-Za-z\-_]{20,}|sk_live_[0-9A-Za-z]{10,}|xox[baprs]-[0-9A-Za-z-]+|-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----|api[_-]?key|access[_-]?token|client[_-]?secret)' \
  | head -n 300 || true

echo
echo "== Tests And Quality Signals =="
rg --files \
  -g '*test*' \
  -g '*spec*' \
  -g '*e2e*' \
  -g '*playwright*' \
  -g '*cypress*' \
  -g '*vitest*' \
  -g '*jest*' | head -n 300 || true

echo
echo "== Performance Signal Patterns =="
rg -n --hidden \
  --glob '!**/node_modules/**' \
  --glob '!**/.git/**' \
  --glob '!**/dist/**' \
  --glob '!**/build/**' \
  '(setInterval\s*\(|MutationObserver|addEventListener\s*\(|chrome\.alarms\.create|chrome\.tabs\.onUpdated|chrome\.runtime\.onMessage|Promise\.all|while\s*\(|for\s*\()' \
  | head -n 500 || true
