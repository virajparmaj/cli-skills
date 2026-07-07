#!/usr/bin/env python3
"""Gather deterministic facts about a DuckDB/Parquet data layer.

Read-only. Walks a repo for .parquet files (and .duckdb databases), groups
files by inferred table, and reports the facts that expose cross-phase drift:

  - schema fingerprint per file (column name + type)
  - schema-drift diffs across files of the same table
  - timezone awareness per timestamp column (naive TIMESTAMP is flagged)
  - date range (min/max) per timestamp column
  - duplicate-key counts on candidate entity keys
  - row-group / file sizing
  - ingestion idempotency signal (hash of sorted candidate-key values)

The model reads this output and applies judgment; this script does not judge.

Heavy readers (pyarrow, duckdb, pandas) are optional. Metadata-only facts come
from pyarrow when present; full duplicate/idempotency facts need duckdb or
pandas. When a reader is missing the script degrades gracefully and prints a
one-line install hint instead of crashing.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

# --- optional heavy imports, guarded ---------------------------------------

try:
    import pyarrow.parquet as pq  # type: ignore

    HAVE_PYARROW = True
except Exception:  # pragma: no cover - environment dependent
    HAVE_PYARROW = False

try:
    import duckdb  # type: ignore

    HAVE_DUCKDB = True
except Exception:  # pragma: no cover - environment dependent
    HAVE_DUCKDB = False

try:
    import pandas as pd  # type: ignore

    HAVE_PANDAS = True
except Exception:  # pragma: no cover - environment dependent
    HAVE_PANDAS = False


SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
}

# Column names that commonly form an entity/event key in a market-data store.
CANDIDATE_KEY_HINTS = (
    "id",
    "symbol",
    "ticker",
    "instrument",
    "asset",
    "pair",
    "date",
    "day",
    "ts",
    "timestamp",
    "time",
    "datetime",
    "event_time",
    "open_time",
    "close_time",
    "exchange",
    "venue",
    "source",
)

# Type tokens that indicate a temporal column.
TS_TYPE_TOKENS = ("timestamp", "datetime", "date", "time")

MAX_KEY_COLS = 4  # cap composite-key probing so wide tables stay cheap


def hint_missing_readers() -> None:
    """Print install hints for whichever readers are absent."""
    if not HAVE_PYARROW:
        print("[hint] pyarrow missing -> pip install pyarrow  (schema/tz/row-group facts)")
    if not HAVE_DUCKDB and not HAVE_PANDAS:
        print(
            "[hint] duckdb and pandas both missing -> pip install duckdb  "
            "(needed for duplicate-key and idempotency facts)"
        )


def find_parquet_files(root: Path) -> list[Path]:
    """Return all .parquet files under root, skipping vendored/build dirs."""
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".parquet"):
                out.append(Path(dirpath) / name)
    return sorted(out)


def find_duckdb_files(root: Path) -> list[Path]:
    """Return DuckDB database files under root."""
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith((".duckdb", ".ddb")):
                out.append(Path(dirpath) / name)
    return sorted(out)


def table_name_for(path: Path, root: Path) -> str:
    """Infer a logical table name for grouping partitioned files.

    Strategy: strip Hive-style partition segments (key=value) and trailing
    numeric/date-looking filename shards, then use the remaining leaf dir or
    stem. Files that share a table but sit in different partitions collapse to
    the same name so schema drift across partitions surfaces.
    """
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    parts = list(rel.parts)
    stem = rel.stem
    # Drop Hive partition segments like symbol=BTCUSDT / date=2024-01-01 from
    # the directory chain; the remaining leaf dir is the dataset/table name.
    non_partition = [p for p in parts[:-1] if "=" not in p]
    # A shard-like filename (part-0001, numeric, date-like) is not a table name;
    # a dataset dir named e.g. "ohlcv" or "trades" is a better group key.
    if _looks_like_shard(stem) and non_partition:
        return non_partition[-1]
    return stem


def _looks_like_shard(stem: str) -> bool:
    """True if a filename stem looks like a shard/partition, not a table name."""
    low = stem.lower()
    if low.startswith(("part", "chunk", "shard", "data-", "file-")):
        return True
    # Pure numbers or date-like stems are shards.
    compact = low.replace("-", "").replace("_", "")
    return compact.isdigit()


def is_ts_type(type_str: str) -> bool:
    low = type_str.lower()
    return any(tok in low for tok in TS_TYPE_TOKENS)


def tz_awareness(type_str: str) -> str:
    """Classify a pyarrow/duckdb type string as tz-aware, naive, or n/a."""
    if not is_ts_type(type_str):
        return "n/a"
    low = type_str.lower()
    # pyarrow: timestamp[us, tz=UTC] ; duckdb: TIMESTAMP WITH TIME ZONE / TIMESTAMPTZ
    if "tz=" in low or "timestamptz" in low or "with time zone" in low:
        return "aware"
    if low.startswith("date") and "time" not in low:
        return "date-only"
    return "NAIVE"


def read_schema_pyarrow(path: Path) -> list[tuple[str, str]]:
    """Return [(column, type_str)] using pyarrow metadata (no full read)."""
    schema = pq.read_schema(path)
    return [(field.name, str(field.type)) for field in schema]


def schema_fingerprint(columns: list[tuple[str, str]]) -> str:
    joined = ";".join(f"{name}:{typ}" for name, typ in columns)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:12]


def candidate_key_columns(columns: list[tuple[str, str]]) -> list[str]:
    """Pick up to MAX_KEY_COLS columns that plausibly form an entity key."""
    names = [c[0] for c in columns]
    picked: list[str] = []
    for name in names:
        low = name.lower()
        if any(h == low or h in low for h in CANDIDATE_KEY_HINTS):
            picked.append(name)
        if len(picked) >= MAX_KEY_COLS:
            break
    return picked


def parquet_file_meta(path: Path) -> dict:
    """Row count and row-group sizing via pyarrow metadata."""
    meta = pq.read_metadata(path)
    rg_rows = [meta.row_group(i).num_rows for i in range(meta.num_row_groups)]
    return {
        "num_rows": meta.num_rows,
        "num_row_groups": meta.num_row_groups,
        "row_group_rows": rg_rows,
        "size_bytes": path.stat().st_size,
    }


def _sql_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def dup_and_idempotency_duckdb(path: Path, key_cols: list[str]) -> dict:
    """Duplicate-key count + idempotency hash using DuckDB (streaming)."""
    con = duckdb.connect(database=":memory:")
    try:
        key_expr = ", ".join(_sql_ident(k) for k in key_cols)
        total = con.execute(f"SELECT count(*) FROM read_parquet({_sql_literal(path)})").fetchone()[0]
        distinct = con.execute(
            f"SELECT count(*) FROM (SELECT DISTINCT {key_expr} "
            f"FROM read_parquet({_sql_literal(path)}))"
        ).fetchone()[0]
        # Idempotency signal: md5 over sorted concatenated key tuples. Re-running
        # an idempotent connector must not change this hash.
        concat = " || '|' || ".join(f"CAST({_sql_ident(k)} AS VARCHAR)" for k in key_cols)
        idem = con.execute(
            f"SELECT md5(string_agg(k, ',' ORDER BY k)) FROM "
            f"(SELECT {concat} AS k FROM read_parquet({_sql_literal(path)}))"
        ).fetchone()[0]
        return {"total": total, "distinct_keys": distinct, "dupes": total - distinct, "idem": idem}
    finally:
        con.close()


def _sql_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def dup_and_idempotency_pandas(path: Path, key_cols: list[str]) -> dict:
    """Fallback duplicate/idempotency facts using pandas (loads the file)."""
    df = pd.read_parquet(path, columns=key_cols)
    total = len(df)
    distinct = len(df.drop_duplicates(subset=key_cols))
    keys = df[key_cols].astype(str).agg("|".join, axis=1).sort_values()
    idem = hashlib.md5(",".join(keys.tolist()).encode("utf-8")).hexdigest()
    return {"total": total, "distinct_keys": distinct, "dupes": total - distinct, "idem": idem}


def date_range_pandas(path: Path, ts_cols: list[str]) -> dict:
    """min/max per timestamp column via pandas (loads only ts columns)."""
    if not ts_cols:
        return {}
    df = pd.read_parquet(path, columns=ts_cols)
    out: dict[str, tuple[str, str]] = {}
    for col in ts_cols:
        s = df[col].dropna()
        if len(s) == 0:
            out[col] = ("empty", "empty")
        else:
            out[col] = (str(s.min()), str(s.max()))
    return out


def print_file_section(path: Path, root: Path) -> tuple[str, str, list[tuple[str, str]]]:
    """Print one file's facts. Returns (table, fingerprint, columns)."""
    rel = path.relative_to(root) if _is_relative(path, root) else path
    print(f"--- {rel} ---")
    if not HAVE_PYARROW:
        print("  schema: unavailable (pyarrow missing)")
        return (table_name_for(path, root), "", [])

    columns = read_schema_pyarrow(path)
    fp = schema_fingerprint(columns)
    table = table_name_for(path, root)
    meta = parquet_file_meta(path)

    print(f"  table (inferred): {table}")
    print(f"  schema fingerprint: {fp}")
    print(f"  rows: {meta['num_rows']:,}   size: {meta['size_bytes']:,} bytes")
    rg = meta["row_group_rows"]
    if rg:
        print(
            f"  row groups: {meta['num_row_groups']}  "
            f"(min {min(rg):,} / max {max(rg):,} rows per group)"
        )
    print("  columns:")
    ts_cols: list[str] = []
    for name, typ in columns:
        tz = tz_awareness(typ)
        if is_ts_type(typ):
            ts_cols.append(name)
        flag = ""
        if tz == "NAIVE":
            flag = "  <-- NAIVE timestamp (no tz)"
        elif _looks_string_dated(name, typ):
            flag = "  <-- string-typed date/time"
        print(f"    {name}: {typ}{flag}")

    key_cols = candidate_key_columns(columns)
    print(f"  candidate key cols: {', '.join(key_cols) if key_cols else '(none inferred)'}")

    if HAVE_PANDAS and ts_cols:
        try:
            ranges = date_range_pandas(path, ts_cols)
            for col, (lo, hi) in ranges.items():
                print(f"  range[{col}]: {lo}  ->  {hi}")
        except Exception as exc:  # pragma: no cover
            print(f"  range: unavailable ({exc})")

    if key_cols and (HAVE_DUCKDB or HAVE_PANDAS):
        try:
            if HAVE_DUCKDB:
                d = dup_and_idempotency_duckdb(path, key_cols)
            else:
                d = dup_and_idempotency_pandas(path, key_cols)
            dup_flag = "  <-- DUPLICATE KEYS" if d["dupes"] > 0 else ""
            print(
                f"  keys: {d['total']:,} rows / {d['distinct_keys']:,} distinct "
                f"/ {d['dupes']:,} dupes{dup_flag}"
            )
            print(f"  idempotency hash (sorted keys): {d['idem']}")
        except Exception as exc:  # pragma: no cover
            print(f"  dup/idempotency: unavailable ({exc})")
    elif key_cols:
        print("  dup/idempotency: skipped (need duckdb or pandas)")

    print()
    return (table, fp, columns)


def _looks_string_dated(name: str, typ: str) -> bool:
    low_t = typ.lower()
    low_n = name.lower()
    is_stringish = "string" in low_t or "utf8" in low_t or low_t in ("object", "varchar")
    is_date_named = any(tok in low_n for tok in ("date", "time", "day", "ts"))
    return is_stringish and is_date_named


def _is_relative(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def print_drift(groups: dict[str, list[tuple[Path, str, list[tuple[str, str]]]]], root: Path) -> None:
    """Compare schema fingerprints within each table group and diff columns."""
    print("=== schema drift across files of the same table ===")
    any_drift = False
    for table, entries in sorted(groups.items()):
        fps = {fp for _, fp, _ in entries if fp}
        if len(entries) < 2:
            continue
        if len(fps) <= 1:
            print(f"  {table}: OK ({len(entries)} files, single schema)")
            continue
        any_drift = True
        print(f"  {table}: DRIFT ({len(entries)} files, {len(fps)} distinct schemas)")
        # Show column-set differences against the first file as baseline.
        base_path, _, base_cols = entries[0]
        base_map = dict(base_cols)
        base_rel = base_path.relative_to(root) if _is_relative(base_path, root) else base_path
        print(f"    baseline: {base_rel}")
        for path, fp, cols in entries[1:]:
            cur_map = dict(cols)
            added = [c for c in cur_map if c not in base_map]
            removed = [c for c in base_map if c not in cur_map]
            retyped = [
                f"{c}: {base_map[c]} -> {cur_map[c]}"
                for c in cur_map
                if c in base_map and cur_map[c] != base_map[c]
            ]
            rel = path.relative_to(root) if _is_relative(path, root) else path
            if not (added or removed or retyped):
                continue
            print(f"    vs {rel}:")
            if added:
                print(f"      + added:   {', '.join(added)}")
            if removed:
                print(f"      - removed: {', '.join(removed)}")
            if retyped:
                print(f"      ~ retyped: {'; '.join(retyped)}")
    if not any_drift:
        print("  no multi-file tables with drift detected")
    print()


def print_duckdb_files(files: list[Path], root: Path) -> None:
    print("=== duckdb database files ===")
    if not files:
        print("  none found")
        print()
        return
    for f in files:
        rel = f.relative_to(root) if _is_relative(f, root) else f
        print(f"  {rel}  ({f.stat().st_size:,} bytes)")
        if HAVE_DUCKDB:
            try:
                con = duckdb.connect(database=str(f), read_only=True)
                try:
                    tables = con.execute("SHOW TABLES").fetchall()
                    for (tname,) in tables:
                        print(f"    table: {tname}")
                finally:
                    con.close()
            except Exception as exc:  # pragma: no cover
                print(f"    (could not open read-only: {exc})")
        else:
            print("    (duckdb not installed; skipping table listing)")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Gather DuckDB/Parquet data-layer facts (read-only).")
    parser.add_argument("repo_path", nargs="?", default=".", help="Repo root to scan (default: .)")
    args = parser.parse_args()

    root = Path(args.repo_path).resolve()
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 1

    print("=== reader availability ===")
    print(f"  pyarrow: {'yes' if HAVE_PYARROW else 'no'}")
    print(f"  duckdb:  {'yes' if HAVE_DUCKDB else 'no'}")
    print(f"  pandas:  {'yes' if HAVE_PANDAS else 'no'}")
    hint_missing_readers()
    print()

    parquet_files = find_parquet_files(root)
    duckdb_files = find_duckdb_files(root)

    print("=== inventory ===")
    print(f"  root: {root}")
    print(f"  parquet files: {len(parquet_files)}")
    print(f"  duckdb files:  {len(duckdb_files)}")
    print()

    if not parquet_files and not duckdb_files:
        print("=== result ===")
        print("  No .parquet or .duckdb files found. Data layer not present or lives elsewhere.")
        print("  If the store is generated at runtime, run the connector first, then re-run.")
        return 0

    print("=== per-file facts ===")
    groups: dict[str, list[tuple[Path, str, list[tuple[str, str]]]]] = {}
    for path in parquet_files:
        try:
            table, fp, cols = print_file_section(path, root)
            groups.setdefault(table, []).append((path, fp, cols))
        except Exception as exc:  # pragma: no cover
            rel = path.relative_to(root) if _is_relative(path, root) else path
            print(f"--- {rel} ---")
            print(f"  ERROR reading file: {exc}")
            print()

    print_drift(groups, root)
    print_duckdb_files(duckdb_files, root)

    print("=== next ===")
    print("  Hand this to the v-duckdb-layer skill. It reads NAIVE timestamps,")
    print("  DRIFT blocks, DUPLICATE KEYS, and idempotency hashes as evidence,")
    print("  then produces the severity-ranked audit and pinned assertion queries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
