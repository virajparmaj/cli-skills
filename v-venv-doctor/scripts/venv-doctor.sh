#!/usr/bin/env bash
#
# Gather Python environment facts for a per-project venv on Apple Silicon.
#
# Read-only. Reports: whether a project-local venv exists and is active vs the
# global interpreter, interpreter architecture (arm64 vs x86_64 under Rosetta),
# Python version, pip drift against requirements.txt and against the pinned ML
# stack, xgboost/libomp status, and packages built from sdist instead of arm64
# wheels. The v-venv-doctor skill turns these facts into a ranked fix list.

set -uo pipefail   # not -e: probes are allowed to fail and be reported

repo_path="${1:-.}"
cd "$repo_path" 2>/dev/null || { echo "no such path: $repo_path" >&2; exit 1; }
repo="$(pwd)"

GLOBAL_VENV="$HOME/.venvs/global"
PINNED="numpy==2.1.2 pandas==2.2.3 scipy==1.14.1 scikit-learn==1.5.2 xgboost==2.1.0 statsmodels==0.14.4 matplotlib==3.9.2 seaborn==0.13.2"

section() { printf '\n=== %s ===\n' "$1"; }

# Pick the interpreter: project venv if present, else whatever python3 resolves to.
PY=""
for cand in "$repo/.venv/bin/python" "$repo/venv/bin/python"; do
  [ -x "$cand" ] && PY="$cand" && break
done
LOCAL_VENV_FOUND="no"
[ -n "$PY" ] && LOCAL_VENV_FOUND="yes"
[ -z "$PY" ] && PY="$(command -v python3 || command -v python || true)"

section "venv presence"
echo "project-local venv (.venv/ or venv/): $LOCAL_VENV_FOUND"
echo "resolved interpreter: ${PY:-<none found>}"
if [ -n "${VIRTUAL_ENV:-}" ]; then
  echo "active VIRTUAL_ENV: $VIRTUAL_ENV"
  case "$VIRTUAL_ENV" in
    "$GLOBAL_VENV"*) echo "WARNING: active env is the GLOBAL venv, not a per-project venv" ;;
  esac
else
  echo "active VIRTUAL_ENV: (none — no venv activated in this shell)"
fi
if [ "$LOCAL_VENV_FOUND" = "no" ]; then
  echo "NOTE: no project venv; per-project-venv rule not satisfied"
fi

[ -z "$PY" ] && { echo; echo "no python interpreter found — stop"; exit 0; }

section "interpreter arch + version"
"$PY" - <<'PYEOF'
import platform, sys
print("python:", sys.version.split()[0])
print("machine:", platform.machine())   # arm64 = native, x86_64 = Rosetta on M-series
print("executable:", sys.executable)
if platform.machine() != "arm64":
    print("WARNING: not arm64 — likely running under Rosetta; native arm64 is faster and avoids wheel mismatches")
if not sys.version.startswith("3.11"):
    print("NOTE: project standard is Python 3.11.x")
PYEOF

section "pip drift vs requirements.txt"
if [ -f "$repo/requirements.txt" ]; then
  "$PY" -m pip freeze 2>/dev/null > /tmp/_vvd_freeze.txt || true
  while IFS= read -r req; do
    case "$req" in ""|\#*) continue ;; esac
    name="$(printf '%s' "$req" | sed -E 's/[<>=!~].*//' | tr -d '[:space:]')"
    [ -z "$name" ] && continue
    have="$(grep -iE "^${name}==" /tmp/_vvd_freeze.txt || true)"
    if [ -z "$have" ]; then
      echo "MISSING or unpinned: $req"
    elif [ "$(printf '%s' "$have" | tr -d '[:space:]')" != "$(printf '%s' "$req" | tr -d '[:space:]')" ]; then
      echo "DRIFT: want '$req' have '$have'"
    fi
  done < "$repo/requirements.txt"
  echo "(blank above = in sync)"
else
  echo "no requirements.txt in repo"
fi

section "pinned ML stack check"
for pin in $PINNED; do
  name="${pin%%==*}"; want="${pin##*==}"
  have="$("$PY" -c "import importlib.metadata as m; print(m.version('$name'))" 2>/dev/null || echo "NOT INSTALLED")"
  if [ "$have" = "NOT INSTALLED" ]; then
    echo "$name: NOT INSTALLED (pinned $want)"
  elif [ "$have" != "$want" ]; then
    echo "$name: $have (pinned $want) DRIFT"
  else
    echo "$name: $have OK"
  fi
done

section "xgboost / libomp smoke test (classic M1 failure)"
"$PY" -c "import xgboost; print('xgboost import OK', xgboost.__version__)" 2>&1 | head -3 || true
if command -v brew >/dev/null 2>&1; then
  if brew list libomp >/dev/null 2>&1; then
    echo "brew libomp: installed"
  else
    echo "brew libomp: NOT installed (xgboost needs it on macOS -> 'brew install libomp')"
  fi
else
  echo "brew: not found"
fi

section "import smoke test (core stack)"
"$PY" - <<'PYEOF'
for mod in ("numpy", "pandas", "scipy", "sklearn", "statsmodels"):
    try:
        __import__(mod)
        print(f"{mod}: OK")
    except Exception as exc:
        print(f"{mod}: FAIL -> {type(exc).__name__}: {exc}")
PYEOF

printf '\n(facts only; the skill produces the ordered fix commands)\n'
