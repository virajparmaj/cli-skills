#!/usr/bin/env python3
"""Check crypto funding/price time-series for interval, timezone, and gap quirks.

Absorbed from the v-funding-data idea. Loads a funding or price file and reports
the interval-delta histogram (does it sit on the expected 8h funding grid, or did
the exchange switch to 4h/1h mid-sample?), gaps, duplicate timestamps, and
timezone awareness. Also greps the repo for annualization constants and ffill/
resample calls touching funding columns.

pandas is required for the data analysis; without it the grep half still runs.
Python 3.11+. Read-only.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}

try:
    import pandas as pd  # noqa: WPS433
    HAVE_PANDAS = True
except Exception:  # noqa: BLE001
    HAVE_PANDAS = False


def analyze_file(path: Path, tscol: str | None) -> None:
    if not HAVE_PANDAS:
        print("  (pandas not installed — skipping data analysis; run pip install pandas pyarrow)")
        return
    try:
        df = pd.read_parquet(path) if path.suffix.lower() in {".parquet", ".pq"} else pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001
        print(f"  ERROR reading: {exc}")
        return
    # find the timestamp column
    if tscol is None:
        for c in df.columns:
            if re.search(r"(time|date|ts|timestamp)", str(c), re.I):
                tscol = c
                break
    if tscol is None or tscol not in df.columns:
        print(f"  no timestamp column found (columns: {list(df.columns)[:10]})")
        return
    ts = pd.to_datetime(df[tscol], errors="coerce", utc=False)
    tz = "tz-aware" if getattr(ts.dt, "tz", None) is not None else "NAIVE (no timezone — assumed local? bug risk)"
    print(f"  timestamp col: {tscol}  [{tz}]")
    ts = ts.dropna().sort_values()
    print(f"  range: {ts.min()} .. {ts.max()}  ({len(ts)} rows)")
    dupes = int(ts.duplicated().sum())
    if dupes:
        print(f"  DUPLICATE timestamps: {dupes}")
    deltas = ts.diff().dropna()
    if len(deltas):
        hist = Counter(deltas.dt.total_seconds().astype("int64"))
        print("  interval histogram (seconds -> count):")
        for secs, cnt in sorted(hist.items(), key=lambda kv: -kv[1])[:6]:
            hrs = secs / 3600
            print(f"    {secs}s (~{hrs:.2f}h): {cnt}")
        modal = max(hist, key=hist.get)
        off_grid = sum(c for s, c in hist.items() if s != modal)
        if off_grid:
            print(f"  OFF-GRID intervals: {off_grid} rows not on the modal {modal}s grid "
                  f"(exchange interval change or gaps)")


def grep_repo(repo: Path) -> None:
    ann = re.compile(r"\b(365|1095|8760|252|3\s*\*\s*365)\b")
    ffill = re.compile(r"\.(ffill|bfill|resample|reindex)\(")
    ann_hits, ffill_hits = [], []
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not (f.endswith(".py") or f.endswith(".ipynb")):
                continue
            p = Path(root) / f
            try:
                text = p.read_text(errors="ignore")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                low = line.lower()
                if ann.search(line) and ("annual" in low or "funding" in low or "sqrt" in low or "*" in line):
                    ann_hits.append(f"{p}:{i}  {line.strip()[:120]}")
                if ffill.search(line) and "fund" in low:
                    ffill_hits.append(f"{p}:{i}  {line.strip()[:120]}")
    print("\n=== annualization constants near funding/annual/sqrt ===")
    for h in ann_hits[:20] or ["  (none)"]:
        print(f"  {h}")
    print("=== ffill/resample touching funding columns (forward-fill = leakage risk) ===")
    for h in ffill_hits[:20] or ["  (none)"]:
        print(f"  {h}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_path", nargs="?", default=".", help="target repo (default .)")
    ap.add_argument("--file", type=Path, help="specific funding/price data file to analyze")
    ap.add_argument("--tscol", help="timestamp column name (auto-detected if omitted)")
    args = ap.parse_args()

    repo = Path(args.repo_path).resolve()
    if args.file:
        print(f"=== {args.file} ===")
        analyze_file(args.file, args.tscol)
    else:
        print("(no --file given; running repo grep only. Pass --file <data> for grid analysis)")
    grep_repo(repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
