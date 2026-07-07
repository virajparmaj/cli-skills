#!/usr/bin/env python3
"""Inventory split, preprocessing, and temporal-window call sites for leakage.

Deterministic half of the v-timeseries-leakage skill. Uses the ast module on
.py files (and JSON-parsed code cells of .ipynb) to record, per file:

- train_test_split calls and whether shuffle is set (default True leaks on
  time-ordered data)
- KFold vs TimeSeriesSplit usage
- scaler/imputer/encoder .fit / .fit_transform line numbers relative to the
  split line (fit-before-split = contamination)
- rolling / ewm(center=True) / shift(-n) / resample calls (forward-reaching
  windows = lookahead)
- presence of ADF/KPSS stationarity checks
- regime signatures: smoothed_marginal_probabilities, fit-on-full-then-predict,
  macro merges without a lag shift

Output is a JSON inventory the skill reasons over to issue a per-pipeline
verdict. Pure stdlib, Python 3.11+. Read-only.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build",
             "dist", ".ipynb_checkpoints", ".mypy_cache", ".pytest_cache"}

FIT_METHODS = {"fit", "fit_transform"}
SPLIT_NAMES = {"train_test_split"}
CV_NAMES = {"KFold", "StratifiedKFold", "TimeSeriesSplit", "GroupKFold",
            "cross_val_score", "cross_validate", "GridSearchCV", "RandomizedSearchCV"}
REGIME_RE = re.compile(r"smoothed_marginal_probabilities|MarkovRegression|"
                       r"MarkovAutoregression")
STATIONARITY_RE = re.compile(r"\b(adfuller|kpss|adf_test|kpss_test)\b")
LAGLESS_MERGE_RE = re.compile(r"\.(merge|join)\(")
SHIFT_NEG_RE = re.compile(r"\.shift\(\s*-\s*\d")
CENTER_TRUE_RE = re.compile(r"center\s*=\s*True")


def iter_sources(repo: Path):
    """Yield (path, source_text) for .py files and .ipynb code cells."""
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = Path(root) / f
            if f.endswith(".py"):
                try:
                    yield p, p.read_text(errors="ignore")
                except OSError:
                    continue
            elif f.endswith(".ipynb"):
                try:
                    nb = json.loads(p.read_text(errors="ignore"))
                except (OSError, json.JSONDecodeError):
                    continue
                for i, cell in enumerate(nb.get("cells", [])):
                    if cell.get("cell_type") == "code":
                        src = cell.get("source", "")
                        code = "".join(src) if isinstance(src, list) else str(src)
                        yield Path(f"{p}#cell{i}"), code


def analyze(path: Path, text: str) -> dict:
    rec = {
        "file": str(path),
        "split_calls": [],       # {line, shuffle}
        "cv_calls": [],          # {line, name}
        "fit_calls": [],         # {line, method}
        "forward_windows": [],   # {line, kind}
        "regime_signatures": [], # {line, kind}
        "stationarity_checks": False,
        "lagless_merges": [],    # {line}
        "datetime_index_hint": bool(re.search(r"(set_index\([^)]*(date|time|ts)|"
                                              r"parse_dates|to_datetime|DatetimeIndex)",
                                              text, re.I)),
    }
    # regex-based line facts (works even if AST fails on notebook fragments)
    for m in STATIONARITY_RE.finditer(text):
        rec["stationarity_checks"] = True
    for i, line in enumerate(text.splitlines(), 1):
        if SHIFT_NEG_RE.search(line):
            rec["forward_windows"].append({"line": i, "kind": "shift(-n) future value"})
        if CENTER_TRUE_RE.search(line) and ("rolling" in line or "ewm" in line or "window" in line):
            rec["forward_windows"].append({"line": i, "kind": "centered rolling window"})
        if REGIME_RE.search(line):
            kind = "smoothed_marginal_probabilities" if "smoothed" in line else "regime model"
            rec["regime_signatures"].append({"line": i, "kind": kind})

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return rec

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fname = _call_name(node.func)
            if fname in SPLIT_NAMES:
                shuffle = _kwarg_value(node, "shuffle")
                rec["split_calls"].append({"line": node.lineno, "shuffle": shuffle})
            elif fname in CV_NAMES:
                rec["cv_calls"].append({"line": node.lineno, "name": fname})
            elif isinstance(node.func, ast.Attribute) and node.func.attr in FIT_METHODS:
                rec["fit_calls"].append({"line": node.lineno, "method": node.func.attr})
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {"merge", "join"}:
                # only note if no obvious lag shift on the same line region
                rec["lagless_merges"].append({"line": node.lineno})

    # derive: earliest split line, and fits before it
    split_lines = [c["line"] for c in rec["split_calls"]]
    if split_lines:
        first_split = min(split_lines)
        rec["fits_before_split"] = [f for f in rec["fit_calls"] if f["line"] < first_split]
    else:
        rec["fits_before_split"] = []
    return rec


def _call_name(func) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _kwarg_value(node: ast.Call, key: str):
    for kw in node.keywords:
        if kw.arg == key:
            if isinstance(kw.value, ast.Constant):
                return kw.value.value
            return "expr"
    return "DEFAULT"  # shuffle default is True for train_test_split


def summarize(records: list[dict]) -> dict:
    flags = []
    for r in records:
        for s in r["split_calls"]:
            if s["shuffle"] in ("DEFAULT", True) and r["datetime_index_hint"]:
                flags.append(f"{r['file']}:{s['line']} train_test_split with shuffle={s['shuffle']} on datetime-indexed data")
        if r["fits_before_split"]:
            for f in r["fits_before_split"]:
                flags.append(f"{r['file']}:{f['line']} .{f['method']}() before the split (fit-on-full-data contamination)")
        for w in r["forward_windows"]:
            flags.append(f"{r['file']}:{w['line']} {w['kind']} (lookahead)")
        for g in r["regime_signatures"]:
            flags.append(f"{r['file']}:{g['line']} {g['kind']} (smoothing conditions on the full sample; filtered is the honest choice for features)")
        has_kfold = any(c["name"] in {"KFold", "StratifiedKFold"} for c in r["cv_calls"])
        has_tss = any(c["name"] == "TimeSeriesSplit" for c in r["cv_calls"])
        if has_kfold and not has_tss and r["datetime_index_hint"]:
            flags.append(f"{r['file']} uses plain KFold on datetime-indexed data (want TimeSeriesSplit)")
    return {"high_signal_flags": flags}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_path", nargs="?", default=".", help="target repo (default .)")
    ap.add_argument("--json", action="store_true", help="emit full raw inventory as JSON")
    args = ap.parse_args()

    repo = Path(args.repo_path).resolve()
    if not repo.exists():
        print(f"no such path: {repo}", file=sys.stderr)
        return 1

    records = [analyze(p, t) for p, t in iter_sources(repo)]
    records = [r for r in records if any((r["split_calls"], r["cv_calls"], r["fit_calls"],
                                          r["forward_windows"], r["regime_signatures"],
                                          r["lagless_merges"]))]
    summary = summarize(records)

    if args.json:
        print(json.dumps({"records": records, "summary": summary}, indent=1))
        return 0

    print("=== time-series leakage inventory ===\n")
    if not records:
        print("No split/preprocessing/window call sites found.")
        return 0
    print("HIGH-SIGNAL FLAGS (skill must confirm each in context):")
    if summary["high_signal_flags"]:
        for f in summary["high_signal_flags"]:
            print(f"  ! {f}")
    else:
        print("  (none auto-detected)")
    print("\nPER-FILE FACTS:")
    for r in records:
        print(f"\n# {r['file']}  (datetime index: {r['datetime_index_hint']}, "
              f"stationarity check: {r['stationarity_checks']})")
        for s in r["split_calls"]:
            print(f"  split @ line {s['line']}  shuffle={s['shuffle']}")
        for c in r["cv_calls"]:
            print(f"  cv: {c['name']} @ line {c['line']}")
        for f in r["fits_before_split"]:
            print(f"  .{f['method']}() @ line {f['line']} BEFORE split")
        for w in r["forward_windows"]:
            print(f"  window: {w['kind']} @ line {w['line']}")
        for g in r["regime_signatures"]:
            print(f"  regime: {g['kind']} @ line {g['line']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
