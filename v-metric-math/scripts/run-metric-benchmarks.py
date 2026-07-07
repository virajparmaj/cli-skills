#!/usr/bin/env python3
"""Run known-answer benchmarks against a repo's own metric functions.

Deterministic half of the v-metric-math skill. Loads hand-computed fixtures
from references/benchmarks.json, discovers metric functions in the target repo
by name/alias, imports them, feeds each fixture through the repo's function, and
reports PASS / FAIL / ERROR against the expected value within tolerance.

The point is not to reimplement the metrics here -- it is to diff the repo's
implementation against a ground truth so convention bugs (ddof, annualization,
sign, quantile method) surface as observed-vs-expected numbers the skill can
diagnose.

Usage:
  run-metric-benchmarks.py <repo_path> [--module path/to/metrics.py]
                           [--emit-pytest <out.py>] [--json]

Without --module the script scans the repo for python files defining a function
whose name matches a fixture alias and imports the first match per alias.

numpy is an optional accelerator for building array inputs; when absent, plain
lists are passed and most well-written metric functions still accept them.
Python 3.11+. Read-only except when --emit-pytest writes a test file.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build",
             "dist", ".mypy_cache", ".pytest_cache", ".ipynb_checkpoints"}


def _benchmarks_path() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "benchmarks.json"


def load_fixtures() -> list[dict]:
    data = json.loads(_benchmarks_path().read_text())
    out: list[dict] = []
    for group in ("financial", "ml"):
        for fx in data.get(group, []):
            fx = dict(fx)
            fx["_group"] = group
            out.append(fx)
    return out


def expected_value(fx: dict) -> float:
    # A fixture may carry a corrected expected_override; prefer it when present.
    if "expected_override" in fx:
        return float(fx["expected_override"])
    return float(fx["expected"])


def iter_py_files(repo: Path):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".py"):
                yield Path(root) / f


def discover_functions(repo: Path, aliases: set[str]) -> dict[str, tuple[Path, str]]:
    """Map alias -> (file, funcname) for the first repo definition found."""
    found: dict[str, tuple[Path, str]] = {}
    pat = re.compile(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.M)
    for py in iter_py_files(repo):
        try:
            text = py.read_text(errors="ignore")
        except OSError:
            continue
        for m in pat.finditer(text):
            name = m.group(1)
            if name in aliases and name not in found:
                found[name] = (py, name)
    return found


def load_callable(py: Path, funcname: str):
    spec = importlib.util.spec_from_file_location(f"_vmm_{funcname}_{abs(hash(py))}", py)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load spec for {py}")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(py.parent))
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    finally:
        if sys.path and sys.path[0] == str(py.parent):
            sys.path.pop(0)
    fn = getattr(mod, funcname, None)
    if not callable(fn):
        raise AttributeError(f"{funcname} not callable in {py}")
    return fn


def _as_array(x):
    try:
        import numpy as np  # noqa: WPS433
        return np.asarray(x, dtype=float)
    except Exception:  # noqa: BLE001 - numpy optional
        return list(x)


def call_with_fixture(fn, fx: dict):
    """Try a few calling conventions; return (observed, convention_used)."""
    inp = fx.get("input", {})
    attempts: list[tuple[tuple, dict, str]] = []

    if "returns" in inp:
        r = _as_array(inp["returns"])
        kw = {}
        for k in ("risk_free", "periods_per_year", "ddof", "alpha", "confidence"):
            if k in inp:
                kw[k] = inp[k]
        attempts.append(((r,), kw, "returns+kwargs"))
        attempts.append(((r,), {}, "returns-only"))
    if "prices" in inp:
        p = _as_array(inp["prices"])
        attempts.append(((p,), {}, "prices-only"))
    if "y_true" in inp and "y_score" in inp:
        yt, ys = _as_array(inp["y_true"]), _as_array(inp["y_score"])
        attempts.append(((yt, ys), {}, "y_true,y_score"))
        attempts.append(((ys, yt), {}, "y_score,y_true"))
    if "y_true" in inp and "y_pred" in inp:
        yt, yp = _as_array(inp["y_true"]), _as_array(inp["y_pred"])
        attempts.append(((yt, yp), {}, "y_true,y_pred"))
    if not attempts:
        # last resort: pass all list-valued inputs positionally
        pos = tuple(_as_array(v) if isinstance(v, list) else v for v in inp.values())
        attempts.append((pos, {}, "positional-all"))

    last_err = None
    for pos_args, kwargs, label in attempts:
        try:
            val = fn(*pos_args, **kwargs)
            try:
                return float(val), label
            except (TypeError, ValueError):
                # metric may return a tuple/array; take first scalar-ish element
                try:
                    return float(list(val)[0]), label + "[0]"
                except Exception:  # noqa: BLE001
                    last_err = f"non-scalar result: {val!r}"
        except Exception as exc:  # noqa: BLE001 - probing signatures
            last_err = f"{type(exc).__name__}: {exc}"
    raise RuntimeError(last_err or "no calling convention worked")


def run(repo: Path, module: Path | None):
    fixtures = load_fixtures()
    aliases: set[str] = set()
    for fx in fixtures:
        aliases.update(fx.get("aliases", []))
        aliases.add(fx["metric"])

    if module is not None:
        catalog: dict[str, tuple[Path, str]] = {}
        text = module.read_text(errors="ignore")
        for m in re.finditer(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text, re.M):
            if m.group(1) in aliases:
                catalog[m.group(1)] = (module, m.group(1))
    else:
        catalog = discover_functions(repo, aliases)

    rows = []
    for fx in fixtures:
        cand = None
        for a in fx.get("aliases", []) + [fx["metric"]]:
            if a in catalog:
                cand = catalog[a]
                break
        exp = expected_value(fx)
        tol = float(fx.get("abs_tol", 1e-6))
        if cand is None:
            rows.append({"id": fx["id"], "metric": fx["metric"], "status": "MISSING",
                         "file": "", "expected": exp, "observed": None,
                         "convention": fx.get("convention", ""), "note": "no matching function found"})
            continue
        py, fn_name = cand
        try:
            fn = load_callable(py, fn_name)
            observed, how = call_with_fixture(fn, fx)
            ok = math.isfinite(observed) and abs(observed - exp) <= tol
            rows.append({"id": fx["id"], "metric": fx["metric"],
                         "status": "PASS" if ok else "FAIL",
                         "file": f"{py}:{fn_name}", "expected": exp,
                         "observed": observed, "convention": fx.get("convention", ""),
                         "note": ("" if ok else fx.get("recompute_note", "")) + f" [{how}]"})
        except Exception as exc:  # noqa: BLE001
            rows.append({"id": fx["id"], "metric": fx["metric"], "status": "ERROR",
                         "file": f"{py}:{fn_name}", "expected": exp, "observed": None,
                         "convention": fx.get("convention", ""), "note": str(exc)})
    return rows


def print_table(rows: list[dict]) -> None:
    print("=== metric benchmark results ===")
    print(f"{'status':7} {'metric':13} {'expected':>14} {'observed':>16}  fixture / where")
    print("-" * 90)
    for r in rows:
        obs = "-" if r["observed"] is None else f"{r['observed']:.8g}"
        exp = f"{r['expected']:.8g}"
        print(f"{r['status']:7} {r['metric']:13} {exp:>14} {obs:>16}  {r['id']}")
        if r["file"]:
            print(f"        at {r['file']}  ({r['convention']})")
        if r["note"].strip():
            print(f"        note: {r['note'].strip()}")
    n = len(rows)
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in
              ("PASS", "FAIL", "ERROR", "MISSING")}
    print("-" * 90)
    print(f"total {n}: " + "  ".join(f"{k}={v}" for k, v in counts.items()))


def emit_pytest(rows: list[dict], out: Path) -> None:
    lines = [
        '"""Auto-generated metric benchmarks (v-metric-math). Passing = code matches',
        'the hand-computed ground truth in benchmarks.json. Regenerate, do not hand-edit."""',
        "import math",
        "import pytest",
        "",
        "# Only fixtures that currently resolve to a repo function are emitted.",
        "",
    ]
    emitted = 0
    for r in rows:
        if r["status"] in ("MISSING",):
            continue
        emitted += 1
        safe = re.sub(r"[^0-9a-zA-Z_]", "_", r["id"])
        lines.append(f"def test_{safe}():")
        lines.append(f"    # {r['convention']}")
        lines.append(f"    # expected {r['expected']} from fixture {r['id']}")
        lines.append("    pytest.skip('wire this to your metric import; template from v-metric-math')")
        lines.append("")
    if emitted == 0:
        lines.append("def test_no_metrics_discovered():")
        lines.append("    pytest.skip('no metric functions discovered in repo')")
    out.write_text("\n".join(lines) + "\n")
    print(f"\nwrote pytest template with {emitted} cases -> {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_path", nargs="?", default=".", help="target repo (default .)")
    ap.add_argument("--module", type=Path, default=None,
                    help="limit discovery to a single metrics module")
    ap.add_argument("--emit-pytest", type=Path, default=None,
                    help="write a pytest template of the resolved benchmarks")
    ap.add_argument("--json", action="store_true", help="emit raw rows as JSON")
    args = ap.parse_args()

    repo = Path(args.repo_path).resolve()
    if not repo.exists():
        print(f"no such path: {repo}", file=sys.stderr)
        return 1

    rows = run(repo, args.module)
    if args.json:
        print(json.dumps(rows, indent=1, default=str))
    else:
        print_table(rows)
    if args.emit_pytest:
        emit_pytest(rows, args.emit_pytest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
