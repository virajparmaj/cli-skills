#!/usr/bin/env python3
"""Inventory row-dropping operations to build a data-loss ledger.

Absorbed from the v-missing-data idea. Scans .py and .ipynb code for every site
that can silently remove or alter rows: dropna, fillna, errors='coerce', merge/
join (esp. how='inner'), reindex/align, resample, and drop_duplicates. Reports
each with context so the skill can classify it EXPLICIT (counted/justified) vs
SILENT (rows vanish unaccounted).

Pure stdlib, Python 3.11+. Read-only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build",
             "dist", ".ipynb_checkpoints"}

PATTERNS = {
    "dropna": re.compile(r"\.dropna\("),
    "fillna": re.compile(r"\.fillna\("),
    "coerce": re.compile(r"errors\s*=\s*['\"]coerce['\"]"),
    "merge/join": re.compile(r"\.(merge|join)\("),
    "inner-merge": re.compile(r"how\s*=\s*['\"]inner['\"]"),
    "reindex/align": re.compile(r"\.(reindex|align)\("),
    "resample": re.compile(r"\.resample\("),
    "drop_duplicates": re.compile(r"\.drop_duplicates\("),
    "query/filter": re.compile(r"\.query\(|\.loc\[|\.filter\("),
    "ffill/bfill": re.compile(r"\.(ffill|bfill|pad)\("),
}
BIASING = {"fillna", "ffill/bfill", "inner-merge", "coerce"}


def iter_sources(repo: Path):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = Path(root) / f
            if f.endswith(".py"):
                try:
                    for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
                        yield p, i, line
                except OSError:
                    continue
            elif f.endswith(".ipynb"):
                try:
                    nb = json.loads(p.read_text(errors="ignore"))
                except (OSError, json.JSONDecodeError):
                    continue
                for ci, cell in enumerate(nb.get("cells", [])):
                    if cell.get("cell_type") == "code":
                        src = cell.get("source", "")
                        code = "".join(src) if isinstance(src, list) else str(src)
                        for i, line in enumerate(code.splitlines(), 1):
                            yield Path(f"{p}#cell{ci}"), i, line


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_path", nargs="?", default=".", help="target repo (default .)")
    ap.add_argument("--json", action="store_true", help="emit raw hits as JSON")
    args = ap.parse_args()

    repo = Path(args.repo_path).resolve()
    if not repo.exists():
        print(f"no such path: {repo}", file=sys.stderr)
        return 1

    hits = []
    for path, lineno, line in iter_sources(repo):
        for kind, pat in PATTERNS.items():
            if pat.search(line):
                hits.append({
                    "file": str(path), "line": lineno, "kind": kind,
                    "biasing": kind in BIASING, "code": line.strip()[:160],
                })

    if args.json:
        print(json.dumps(hits, indent=1))
        return 0

    print(f"=== data-loss ledger candidates ({len(hits)} sites) ===\n")
    if not hits:
        print("No row-dropping / imputation / merge sites found.")
        return 0
    print("Classify each: EXPLICIT (counted before/after + justified) vs SILENT.\n")
    biasing = [h for h in hits if h["biasing"]]
    if biasing:
        print("BIASING OPERATIONS (imputation / inner-merge / coerce — verify they don't distort stats):")
        for h in biasing:
            print(f"  ! {h['file']}:{h['line']}  [{h['kind']}]  {h['code']}")
        print()
    print("ALL ROW-AFFECTING SITES:")
    for h in hits:
        print(f"  {h['file']}:{h['line']}  [{h['kind']}]  {h['code']}")
    print("\nTip: import the pipeline and print len(df) before/after each step to "
          "turn 'unmeasured' into measured row-in->row-out counts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
