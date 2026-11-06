#!/usr/bin/env bash
#
# Gather Python environment facts for a per-project venv on Apple Silicon.
#
# Read-only. Reports: whether a project-local venv exists and is active vs the
# global interpreter, interpreter architecture (arm64 vs x86_64 under Rosetta),
# Python version, dependency drift against requirements.txt and an opt-in historical ML
# stack, xgboost/libomp status, and packages built from sdist instead of arm64
# wheels. The v-venv-doctor skill turns these facts into a ranked fix list.

set -uo pipefail   # not -e: probes are allowed to fail and be reported

repo_path="${1:-.}"
historical_stack="${2:-}"
if [ -n "$historical_stack" ] && [ "$historical_stack" != "--historical-stack" ]; then
  echo "usage: $0 [repo] [--historical-stack]" >&2
  exit 2
fi
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
"$PY" - "$repo/pyproject.toml" <<'PYEOF'
import platform, sys
from pathlib import Path
print("python:", sys.version.split()[0])
print("machine:", platform.machine())   # arm64 = native, x86_64 = Rosetta on M-series
print("executable:", sys.executable)
if platform.machine() != "arm64":
    print("WARNING: not arm64 — likely running under Rosetta; native arm64 is faster and avoids wheel mismatches")
print("Compare this version to the project's requires-python or lockfile; no global version is assumed.")
manifest = Path(sys.argv[1])
if manifest.is_file():
    try:
        import tomllib
        try:
            from packaging.specifiers import SpecifierSet
        except ImportError:
            from pip._vendor.packaging.specifiers import SpecifierSet
        requirement = tomllib.loads(manifest.read_text()).get("project", {}).get("requires-python")
        if requirement:
            status = "PASS" if SpecifierSet(requirement).contains(platform.python_version(), prereleases=True) else "FAIL"
            print(f"requires-python {requirement}: {status}")
    except (ImportError, ValueError, OSError) as exc:
        print(f"requires-python UNVERIFIED: {exc}")
PYEOF

section "pip drift vs requirements.txt"
if [ -f "$repo/requirements.txt" ]; then
  "$PY" - "$repo/requirements.txt" <<'PYEOF'
import importlib.metadata as metadata
from pathlib import Path
import sys
try:
    from packaging.requirements import Requirement
except ImportError:
    try:
        from pip._vendor.packaging.requirements import Requirement
    except ImportError:
        print("UNVERIFIED: packaging parser unavailable; compare requirements manually")
        raise SystemExit(0)
for line in Path(sys.argv[1]).read_text().splitlines():
    line = line.split(" #", 1)[0].strip()
    if not line or line.startswith("#"):
        continue
    try:
        requirement = Requirement(line)
    except ValueError:
        print(f"UNVERIFIED requirement/directive: {line}")
        continue
    if requirement.marker and not requirement.marker.evaluate():
        continue
    try:
        installed = metadata.version(requirement.name)
    except metadata.PackageNotFoundError:
        print(f"MISSING: {requirement}")
        continue
    if requirement.url:
        print(f"UNVERIFIED source URL: {requirement.name} ({installed})")
    elif requirement.specifier and not requirement.specifier.contains(installed, prereleases=True):
        print(f"DRIFT: want '{requirement}' have '{requirement.name}=={installed}'")
PYEOF
  echo "(blank above = in sync)"
else
  echo "no requirements.txt in repo"
fi

if [ "$historical_stack" = "--historical-stack" ]; then
section "historical ML stack comparison (explicitly requested)"
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
fi

if "$PY" -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('xgboost') else 1)"; then
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
else
  printf '\nxgboost not installed; no libomp repair inferred (check project requirements above).\n'
fi

section "import smoke test (core stack)"
"$PY" - <<'PYEOF'
for mod in ("numpy", "pandas", "scipy", "sklearn", "statsmodels"):
    try:
        __import__(mod)
        print(f"{mod}: OK")
    except ModuleNotFoundError as exc:
        if exc.name == mod:
            print(f"{mod}: not installed (check project requirements; no optional package is required by this probe)")
        else:
            print(f"{mod}: FAIL -> {type(exc).__name__}: {exc}")
    except Exception as exc:
        print(f"{mod}: FAIL -> {type(exc).__name__}: {exc}")
PYEOF

printf '\n(facts only; the skill produces the ordered fix commands)\n'
