#!/usr/bin/env bash
#
# scaffold-py.sh — Bootstrap a Python 3.11 ML/data project in Veer's exact
# conventions: per-project venv, pyproject with Black (line-length 100) + isort,
# his pinned ML stack, src/ layout, and a clean starter notebook following the
# config -> data -> preprocessing -> modeling cell order with success prints.
#
# Does NOT git commit (the caller decides when). venv creation is opt-out via
# --no-venv for environments where Python 3.11 is unavailable.
#
# Usage: scaffold-py.sh <target-dir> [package-name] [--no-venv] [--no-notebook] [--force]
#   <target-dir>    directory to scaffold into (created if missing)
#   [package-name]  importable package under src/ (default: basename, sanitized)
#   --no-venv       skip venv creation (still writes all files)
#   --no-notebook   skip the starter notebook
#   --force         overwrite existing convention files instead of skipping them
#
# Prints a "=== manifest ===" section listing every file created or skipped.

set -euo pipefail

# --- Veer's pinned ML stack (single source of truth) ----------------------
PINNED_STACK=(
  "numpy==2.1.2"
  "pandas==2.2.3"
  "scipy==1.14.1"
  "scikit-learn==1.5.2"
  "xgboost==2.1.0"
  "statsmodels==0.14.4"
  "matplotlib==3.9.2"
  "seaborn==0.13.2"
  "structlog"
)
DEV_STACK=(
  "black==24.10.0"
  "isort==5.13.2"
  "ipykernel"
)

# --- args -----------------------------------------------------------------
if [[ $# -lt 1 ]]; then
  echo "usage: scaffold-py.sh <target-dir> [package-name] [--no-venv] [--no-notebook] [--force]" >&2
  exit 2
fi

target_dir=""
package_name=""
make_venv=1
make_notebook=1
force=0

for arg in "$@"; do
  case "$arg" in
    --no-venv) make_venv=0 ;;
    --no-notebook) make_notebook=0 ;;
    --force) force=1 ;;
    *)
      if [[ -z "$target_dir" ]]; then
        target_dir="$arg"
      elif [[ -z "$package_name" ]]; then
        package_name="$arg"
      fi
      ;;
  esac
done

if [[ -z "$target_dir" ]]; then
  echo "error: target-dir is required" >&2
  exit 2
fi

mkdir -p "$target_dir"
target_dir="$(cd "$target_dir" && pwd)"
[[ -z "$package_name" ]] && package_name="$(basename "$target_dir")"
# sanitize package name to a valid Python identifier
package_name="$(printf '%s' "$package_name" | tr '[:upper:]-' '[:lower:]_' | tr -cd 'a-z0-9_')"
[[ -z "$package_name" ]] && package_name="app"
[[ "$package_name" =~ ^[0-9] ]] && package_name="pkg_$package_name"

created=()
skipped=()

write_file() {
  local rel="$1"
  local abs="$target_dir/$rel"
  if [[ -e "$abs" && $force -eq 0 ]]; then
    skipped+=("$rel")
    cat >/dev/null
    return 0
  fi
  mkdir -p "$(dirname "$abs")"
  cat >"$abs"
  created+=("$rel")
}

# --- pyproject.toml (Black line-length 100 + isort black profile) ---------
# Build the pinned deps list as a TOML array.
deps_toml=""
for dep in "${PINNED_STACK[@]}"; do
  deps_toml+="  \"$dep\","$'\n'
done
dev_toml=""
for dep in "${DEV_STACK[@]}"; do
  dev_toml+="  \"$dep\","$'\n'
done

write_file "pyproject.toml" <<EOF
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "$package_name"
version = "0.1.0"
description = "Add a one-line description."
requires-python = ">=3.11,<3.12"
dependencies = [
$deps_toml]

[project.optional-dependencies]
dev = [
$dev_toml]

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.isort]
profile = "black"
line_length = 100
src_paths = ["src", "tests"]
EOF

# --- requirements files (belt-and-suspenders for non-pyproject workflows) -
req_lines=""
for dep in "${PINNED_STACK[@]}"; do
  req_lines+="$dep"$'\n'
done
write_file "requirements.txt" <<EOF
$req_lines
EOF

dev_lines=""
for dep in "${DEV_STACK[@]}"; do
  dev_lines+="$dep"$'\n'
done
write_file "requirements-dev.txt" <<EOF
-r requirements.txt
$dev_lines
EOF

# --- src/ layout ----------------------------------------------------------
write_file "src/$package_name/__init__.py" <<EOF
"""$package_name package."""

__version__ = "0.1.0"
EOF

write_file "src/$package_name/data.py" <<'EOF'
"""Data loading utilities.

Move stable data logic out of notebooks and into this module.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV into a DataFrame.

    Args:
        path: Path to the CSV file.

    Returns:
        The loaded DataFrame.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    return pd.read_csv(path)
EOF

# --- tests/ ---------------------------------------------------------------
write_file "tests/__init__.py" <<'EOF'
EOF

write_file "tests/test_data.py" <<EOF
"""Tests for $package_name.data."""

from pathlib import Path

import pandas as pd
import pytest

from $package_name.data import load_csv


def test_load_csv_roundtrip(tmp_path: Path) -> None:
    csv = tmp_path / "sample.csv"
    csv.write_text("a,b\\n1,2\\n3,4\\n")
    df = load_csv(csv)
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_load_csv_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "nope.csv")
EOF

# --- data directory placeholder -------------------------------------------
write_file "data/.gitkeep" <<'EOF'
EOF

# --- starter notebook (config -> data -> preprocessing -> modeling) -------
if [[ $make_notebook -eq 1 ]]; then
  write_file "notebooks/01_explore.ipynb" <<'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": ["# Exploration\n", "\n", "Config -> Data -> Preprocessing -> Modeling. Move stable logic into `src/`."]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# --- config ---\n",
    "from pathlib import Path\n",
    "\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "\n",
    "pd.set_option(\"display.max_columns\", 50)\n",
    "RANDOM_STATE = 42\n",
    "DATA_DIR = Path(\"..\") / \"data\"\n",
    "print(\"✅ Config loaded\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# --- data ---\n",
    "# df = pd.read_csv(DATA_DIR / \"raw.csv\")\n",
    "df = pd.DataFrame({\"feature\": [1, 2, 3], \"target\": [0, 1, 0]})\n",
    "print(\"✅ Data loaded:\", df.shape)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# --- preprocessing ---\n",
    "X = df.drop(columns=[\"target\"])\n",
    "y = df[\"target\"]\n",
    "print(\"✅ Preprocessing done:\", X.shape, y.shape)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# --- modeling ---\n",
    "from sklearn.linear_model import LogisticRegression\n",
    "\n",
    "model = LogisticRegression(random_state=RANDOM_STATE)\n",
    "# model.fit(X, y)\n",
    "print(\"✅ Model ready\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
  "language_info": {"name": "python", "version": "3.11"}
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
EOF
fi

# --- .gitignore -----------------------------------------------------------
write_file ".gitignore" <<'EOF'
# venv
.venv/
venv/

# python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.ipynb_checkpoints/

# data (keep dir, ignore contents)
data/*
!data/.gitkeep

# env / os
.env
.DS_Store
EOF

# --- README stub ----------------------------------------------------------
write_file "README.md" <<EOF
# $package_name

Python 3.11 ML/data project. Black (line-length 100) + isort, pinned ML stack.

## Setup

\`\`\`bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
\`\`\`

## Layout

- \`src/$package_name/\` — importable package (stable logic lives here)
- \`notebooks/\` — exploration; keep clean, move stable code to \`src/\`
- \`tests/\` — pytest suite
- \`data/\` — local data (gitignored)
EOF

# --- venv creation --------------------------------------------------------
venv_status="skipped (--no-venv)"
if [[ $make_venv -eq 1 ]]; then
  py311=""
  for cand in python3.11 python3; do
    if command -v "$cand" >/dev/null 2>&1; then
      ver="$("$cand" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null || echo "")"
      if [[ "$ver" == "3.11" ]]; then
        py311="$cand"
        break
      fi
    fi
  done

  if [[ -z "$py311" ]]; then
    venv_status="NOT created: no Python 3.11 found on PATH (tried python3.11, python3). Install 3.11, then: python3.11 -m venv .venv"
  elif [[ -d "$target_dir/.venv" && $force -eq 0 ]]; then
    venv_status="skipped: .venv already exists (use --force to recreate)"
  else
    if "$py311" -m venv "$target_dir/.venv"; then
      venv_status="created with $py311 at .venv"
    else
      venv_status="FAILED: '$py311 -m venv .venv' returned nonzero"
    fi
  fi
fi

# --- manifest -------------------------------------------------------------
echo "=== scaffold-py summary ==="
echo "target: $target_dir"
echo "package name: $package_name"
echo "notebook: $([[ $make_notebook -eq 1 ]] && echo yes || echo no)"
echo "venv: $venv_status"
echo

echo "=== pinned stack ==="
printf '%s\n' "${PINNED_STACK[@]}"
echo

echo "=== manifest (created) ==="
if [[ ${#created[@]} -eq 0 ]]; then
  echo "(none)"
else
  printf '%s\n' "${created[@]}" | sort
fi
echo

echo "=== manifest (skipped, already existed) ==="
if [[ ${#skipped[@]} -eq 0 ]]; then
  echo "(none)"
else
  printf '%s\n' "${skipped[@]}" | sort
fi
echo

echo "=== next steps ==="
echo "1. cd $target_dir"
echo "2. source .venv/bin/activate   # if venv was created"
echo "3. pip install -e \".[dev]\"    # installs pinned stack + Black/isort"
echo "4. python -m ipykernel install --user --name $package_name"
echo "then: git init && git add . && commit in Veer's format"
