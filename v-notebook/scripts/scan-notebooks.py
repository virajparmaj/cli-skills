#!/usr/bin/env python3
"""Scan Jupyter notebooks for hygiene violations and promotable logic.

Deterministic half of the v-notebook skill. Parses every .ipynb as plain JSON
(no nbformat dependency) and reports, per notebook:

- detected section order vs the config -> data -> preprocessing -> modeling
  convention (inferred from markdown headers and cell content)
- committed output bytes per cell (outputs that bloat git diffs)
- import statements appearing mid-notebook instead of an early config cell
- presence of end-of-block success prints
- an RNG census: every random call site and whether a seed reaches it
- sha1 of normalized code cells, to flag logic duplicated across notebooks or
  already present in src/*.py

Pure stdlib, Python 3.11+. Read-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build",
             "dist", ".ipynb_checkpoints", ".mypy_cache", ".pytest_cache"}

SECTION_HINTS = {
    "config": re.compile(r"\b(config|imports?|setup|constants?|params?)\b", re.I),
    "data": re.compile(r"\b(load|read_csv|read_parquet|fetch|data\b|dataset)\b", re.I),
    "preprocessing": re.compile(r"\b(clean|preprocess|feature|scal|encod|impute|transform|split)\b", re.I),
    "modeling": re.compile(r"\b(fit|train|model|predict|score|evaluat|cross_val|xgb|sklearn)\b", re.I),
}
SECTION_ORDER = ["config", "data", "preprocessing", "modeling"]

RNG_PAT = re.compile(r"(np\.random\.|numpy\.random\.|\brandom\.|random_state\s*=|"
                     r"default_rng\(|torch\.manual_seed|tf\.random)")
SEED_PAT = re.compile(r"(seed\s*=|random_state\s*=\s*\d|np\.random\.seed\(|"
                      r"default_rng\(\s*\d|manual_seed\(\s*\d|set_seed\()")
IMPORT_PAT = re.compile(r"^\s*(import\s+\w|from\s+\w[\w.]*\s+import)", re.M)
SUCCESS_PRINT = re.compile(r"print\(.*(✅|success|loaded|done|complete)", re.I)


def iter_notebooks(repo: Path):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".ipynb"):
                yield Path(root) / f


def normalize_code(src: str) -> str:
    lines = []
    for ln in src.splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        s = re.sub(r"\s+", " ", s)
        lines.append(s)
    return "\n".join(lines)


def cell_source(cell: dict) -> str:
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else str(src)


def output_bytes(cell: dict) -> int:
    total = 0
    for out in cell.get("outputs", []) or []:
        for key in ("text", "data"):
            val = out.get(key)
            if isinstance(val, list):
                total += sum(len(x) for x in val if isinstance(x, str))
            elif isinstance(val, dict):
                for v in val.values():
                    if isinstance(v, list):
                        total += sum(len(x) for x in v if isinstance(x, str))
                    elif isinstance(v, str):
                        total += len(v)
            elif isinstance(val, str):
                total += len(val)
    return total


def detect_section(text: str) -> str | None:
    for name in SECTION_ORDER:
        if SECTION_HINTS[name].search(text):
            return name
    return None


def src_code_hashes(repo: Path) -> dict[str, str]:
    """Map normalized-code sha1 -> 'file:funcname' for src/*.py definitions."""
    out: dict[str, str] = {}
    src = repo / "src"
    if not src.exists():
        return out
    for py in src.rglob("*.py"):
        try:
            text = py.read_text(errors="ignore")
        except OSError:
            continue
        norm = normalize_code(text)
        if norm:
            h = hashlib.sha1(norm.encode()).hexdigest()[:12]
            out.setdefault(h, str(py.relative_to(repo)))
    return out


def scan_notebook(nb_path: Path, repo: Path, src_hashes: dict[str, str],
                  seen_hashes: dict[str, str]) -> dict:
    try:
        nb = json.loads(nb_path.read_text(errors="ignore"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"path": str(nb_path.relative_to(repo)), "error": str(exc)}

    cells = nb.get("cells", [])
    seq: list[str] = []
    total_out = 0
    mid_imports = 0
    has_success = False
    rng_sites: list[str] = []
    dup_notes: list[str] = []
    first_code_seen = False

    for i, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            if cell.get("cell_type") == "markdown":
                sec = detect_section(cell_source(cell))
                if sec and (not seq or seq[-1] != sec):
                    seq.append(sec)
            continue
        code = cell_source(cell)
        total_out += output_bytes(cell)
        if IMPORT_PAT.search(code):
            if first_code_seen:
                mid_imports += 1
        first_code_seen = True
        if SUCCESS_PRINT.search(code):
            has_success = True
        if RNG_PAT.search(code) and not SEED_PAT.search(code):
            rng_sites.append(f"cell {i}")
        sec = detect_section(code)
        if sec and (not seq or seq[-1] != sec):
            seq.append(sec)
        norm = normalize_code(code)
        if len(norm) > 80:  # only meaningful cells
            h = hashlib.sha1(norm.encode()).hexdigest()[:12]
            if h in src_hashes:
                dup_notes.append(f"cell {i} duplicates {src_hashes[h]} (already in src/)")
            elif h in seen_hashes:
                dup_notes.append(f"cell {i} duplicates {seen_hashes[h]}")
            else:
                seen_hashes[h] = f"{nb_path.name}:cell{i}"

    ordered = [s for s in seq if s in SECTION_ORDER]
    canonical = [s for s in SECTION_ORDER if s in ordered]
    order_ok = ordered == canonical
    return {
        "path": str(nb_path.relative_to(repo)),
        "cells": len(cells),
        "section_sequence": ordered,
        "order_ok": order_ok,
        "output_bytes": total_out,
        "mid_notebook_imports": mid_imports,
        "has_success_prints": has_success,
        "unseeded_rng_sites": rng_sites,
        "duplication": dup_notes,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_path", nargs="?", default=".", help="target repo (default .)")
    ap.add_argument("--json", action="store_true", help="emit raw JSON")
    args = ap.parse_args()

    repo = Path(args.repo_path).resolve()
    if not repo.exists():
        print(f"no such path: {repo}", file=sys.stderr)
        return 1

    src_hashes = src_code_hashes(repo)
    seen: dict[str, str] = {}
    reports = [scan_notebook(nb, repo, src_hashes, seen) for nb in sorted(iter_notebooks(repo))]

    if args.json:
        print(json.dumps(reports, indent=1))
        return 0

    if not reports:
        print("No .ipynb notebooks found.")
        return 0

    print(f"=== notebook hygiene scan ({len(reports)} notebooks) ===\n")
    for r in reports:
        print(f"# {r['path']}")
        if "error" in r:
            print(f"  ERROR parsing: {r['error']}\n")
            continue
        order = " -> ".join(r["section_sequence"]) or "(no sections detected)"
        print(f"  sections: {order}   [{'OK' if r['order_ok'] else 'OUT OF ORDER'}]")
        kb = r["output_bytes"] / 1024
        flag = "  <-- committed outputs bloat git" if r["output_bytes"] > 20000 else ""
        print(f"  committed output: {kb:.1f} KB{flag}")
        if r["mid_notebook_imports"]:
            print(f"  mid-notebook imports: {r['mid_notebook_imports']} (move to config cell)")
        if not r["has_success_prints"]:
            print("  no end-of-block success prints (convention: print('✅ ...'))")
        if r["unseeded_rng_sites"]:
            print(f"  UNSEEDED randomness: {', '.join(r['unseeded_rng_sites'])}")
        for d in r["duplication"]:
            print(f"  DUP: {d}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
