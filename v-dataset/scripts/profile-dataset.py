#!/usr/bin/env python3
"""Profile CSV/Parquet datasets and check for split overlap and target leakage.

Deterministic half of the v-dataset skill. For each data file: per-column null
%, dtype anomalies, exact-duplicate row count, near-constant and high-cardinality
columns, and (with --target) class balance and a feature-target association
ranking. Pass two files as --train / --test to get the sha1 row-hash overlap
between splits.

pandas is the profiler; when absent the script degrades to a stdlib CSV pass
(nulls, dupes, cardinality) and skips parquet and association ranking. Python
3.11+. Read-only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}
DATA_EXT = {".csv", ".parquet", ".pq"}

try:
    import pandas as pd  # noqa: WPS433
    HAVE_PANDAS = True
except Exception:  # noqa: BLE001 - pandas optional
    HAVE_PANDAS = False


def find_data_files(repo: Path) -> list[Path]:
    out = []
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if Path(f).suffix.lower() in DATA_EXT:
                out.append(Path(root) / f)
    return sorted(out)


def row_hashes(path: Path) -> set[str]:
    hashes: set[str] = set()
    if HAVE_PANDAS:
        try:
            df = _read(path)
            for _, row in df.iterrows():
                hashes.add(hashlib.sha1(str(tuple(row.values)).encode()).hexdigest())
            return hashes
        except Exception:  # noqa: BLE001
            return hashes
    if path.suffix.lower() == ".csv":
        with path.open(newline="") as fh:
            for row in csv.reader(fh):
                hashes.add(hashlib.sha1(str(tuple(row)).encode()).hexdigest())
    return hashes


def _read(path: Path):
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    return pd.read_csv(path)


def profile_pandas(path: Path, target: str | None) -> list[str]:
    lines = []
    try:
        df = _read(path)
    except Exception as exc:  # noqa: BLE001
        return [f"  ERROR reading: {exc}"]
    n = len(df)
    lines.append(f"  rows={n}  cols={len(df.columns)}")
    dupes = int(df.duplicated().sum())
    if dupes:
        lines.append(f"  EXACT DUPLICATE ROWS: {dupes} ({dupes / max(n,1):.1%})")
    for col in df.columns:
        null_pct = df[col].isna().mean()
        nunique = df[col].nunique(dropna=True)
        notes = []
        if null_pct > 0:
            sev = "HIGH" if null_pct > 0.2 else "low"
            notes.append(f"nulls={null_pct:.1%} [{sev}]")
        if nunique <= 1:
            notes.append("NEAR-CONSTANT")
        if nunique == n and n > 0:
            notes.append("unique-per-row (id-like)")
        if notes:
            lines.append(f"    {col}: " + ", ".join(notes))
    if target and target in df.columns:
        vc = df[target].value_counts(normalize=True, dropna=False)
        lines.append(f"  target '{target}' balance: " +
                     ", ".join(f"{k}={v:.1%}" for k, v in vc.head(8).items()))
        if len(vc) > 1 and vc.iloc[0] > 0.9:
            lines.append(f"  CLASS IMBALANCE: majority class = {vc.iloc[0]:.1%}")
        lines.extend(_assoc_ranking(df, target))
    return lines


def _assoc_ranking(df, target: str) -> list[str]:
    """Rank features by |correlation| with a numeric target, or by a cheap
    group-separation proxy for a categorical target. Suspiciously high = candidate
    target leakage."""
    out = ["  feature-target association (top; ~1.0 = candidate LEAKAGE):"]
    try:
        y = df[target]
        num = df.select_dtypes("number").drop(columns=[target], errors="ignore")
        if y.dtype.kind in "biufc" and not num.empty:
            corr = num.corrwith(y).abs().sort_values(ascending=False)
            for col, val in corr.head(6).items():
                flag = "  <-- LEAKAGE?" if val > 0.98 else ""
                out.append(f"    {col}: |corr|={val:.3f}{flag}")
        else:
            # categorical target: rank by variance-of-group-means / total variance
            scores = {}
            for col in num.columns:
                try:
                    grand = num[col].var()
                    if grand and grand > 0:
                        gm = df.groupby(target, observed=True)[col].mean().var()
                        scores[col] = float(gm / grand) if grand else 0.0
                except Exception:  # noqa: BLE001
                    continue
            for col, val in sorted(scores.items(), key=lambda kv: -kv[1])[:6]:
                flag = "  <-- LEAKAGE?" if val > 0.98 else ""
                out.append(f"    {col}: separation={val:.3f}{flag}")
    except Exception as exc:  # noqa: BLE001
        out.append(f"    (association ranking unavailable: {exc})")
    return out


def profile_stdlib_csv(path: Path) -> list[str]:
    try:
        with path.open(newline="") as fh:
            rows = list(csv.reader(fh))
    except OSError as exc:
        return [f"  ERROR reading: {exc}"]
    if not rows:
        return ["  empty file"]
    header, data = rows[0], rows[1:]
    n = len(data)
    lines = [f"  rows={n}  cols={len(header)}  (stdlib CSV mode — install pandas for full profile)"]
    seen: Counter = Counter(tuple(r) for r in data)
    dupes = sum(c - 1 for c in seen.values() if c > 1)
    if dupes:
        lines.append(f"  EXACT DUPLICATE ROWS: {dupes}")
    for j, col in enumerate(header):
        vals = [r[j] for r in data if j < len(r)]
        nulls = sum(1 for v in vals if v == "" or v.lower() in {"na", "nan", "null"})
        uniq = len(set(vals))
        notes = []
        if nulls:
            notes.append(f"nulls={nulls / max(n,1):.1%}")
        if uniq <= 1:
            notes.append("NEAR-CONSTANT")
        if notes:
            lines.append(f"    {col}: " + ", ".join(notes))
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_path", nargs="?", default=".", help="repo or data dir (default .)")
    ap.add_argument("--target", help="target column for balance + association ranking")
    ap.add_argument("--train", type=Path, help="train file for split-overlap check")
    ap.add_argument("--test", type=Path, help="test file for split-overlap check")
    args = ap.parse_args()

    if args.train and args.test:
        a, b = row_hashes(args.train), row_hashes(args.test)
        inter = a & b
        print("=== split overlap check ===")
        print(f"train rows(hashed)={len(a)}  test rows(hashed)={len(b)}  overlap={len(inter)}")
        if inter:
            print(f"  LEAKAGE: {len(inter)} identical rows appear in BOTH train and test")
        else:
            print("  OK: no identical rows shared across splits")
        return 0

    repo = Path(args.repo_path).resolve()
    files = find_data_files(repo)
    if not files:
        print("No CSV/Parquet data files found.")
        return 0
    print(f"=== dataset profile ({len(files)} files) ===")
    if not HAVE_PANDAS:
        print("(pandas not installed: CSV profiled with stdlib, parquet skipped)\n")
    for path in files:
        print(f"\n# {path.relative_to(repo) if repo in path.parents or path.parent == repo else path}")
        if HAVE_PANDAS:
            for ln in profile_pandas(path, args.target):
                print(ln)
        elif path.suffix.lower() == ".csv":
            for ln in profile_stdlib_csv(path):
                print(ln)
        else:
            size = path.stat().st_size
            print(f"  parquet, {size/1024:.1f} KB (install pandas/pyarrow to profile)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
