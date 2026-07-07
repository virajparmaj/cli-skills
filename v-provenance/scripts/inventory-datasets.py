#!/usr/bin/env python3
"""Inventory data files, diff against provenance cards, and emit pre-filled stubs.

Deterministic half of the v-provenance skill. For every data file under the
target repo this computes: sha256, byte size, row/column counts, column names,
per-column null rate, and min/max of datetime-like columns. It then diffs those
facts against existing provenance cards (data/PROVENANCE/*.md and data/DATA.md)
and classifies each dataset as OK, STALE (bytes changed since its card), or
ORPHANED (no card). In --emit mode it writes a pre-filled provenance stub per
orphan so only the human judgment fields remain.

DuckDB and pandas are optional accelerators. When neither is installed the
script degrades to a stdlib CSV profiler and still reports hashes, sizes, row
counts, and null rates. Parquet requires pyarrow or duckdb; without them a
parquet file is hashed and sized but not profiled (reported PARTIAL).

Python 3.11+. Read-only against the repo except when --emit writes stubs under
data/PROVENANCE/.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- optional accelerators -------------------------------------------------

_DUCKDB = None
try:
    import duckdb as _DUCKDB  # type: ignore
except Exception:  # pragma: no cover - environment dependent
    _DUCKDB = None

_PYARROW = None
try:
    import pyarrow.parquet as _PYARROW  # type: ignore
except Exception:  # pragma: no cover - environment dependent
    _PYARROW = None

DATA_DIRS = ("data",)
DATA_EXTS = (".csv", ".tsv", ".parquet")
CARD_DIR = "data/PROVENANCE"
LEGACY_CARD = "data/DATA.md"
SKIP_PARTS = {".git", "node_modules", "__pycache__", ".venv", "venv", "PROVENANCE"}
DATE_HINT = re.compile(r"(date|time|timestamp|dt|_at|_ts)$", re.IGNORECASE)
HASH_LINE = re.compile(r"sha256[`:\s]+([0-9a-f]{64})", re.IGNORECASE)
SAMPLE_ROWS = 50000  # cap stdlib profiling so huge CSVs stay fast


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_data_files(repo: Path) -> list[Path]:
    out: list[Path] = []
    for base in DATA_DIRS:
        root = repo / base
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in DATA_EXTS:
                continue
            if any(part in SKIP_PARTS for part in p.relative_to(repo).parts):
                continue
            out.append(p)
    return out


def profile_delimited(path: Path, delimiter: str) -> dict:
    """stdlib CSV/TSV profiler: rows, columns, null rates, datetime ranges."""
    facts: dict = {"engine": "stdlib-csv", "partial": False}
    with path.open("r", newline="", encoding="utf-8", errors="replace") as fh:
        reader = csv.reader(fh, delimiter=delimiter)
        try:
            header = next(reader)
        except StopIteration:
            return {**facts, "columns": [], "rows": 0, "nulls": {}, "dates": {}}
        cols = [c.strip() for c in header]
        nulls = {c: 0 for c in cols}
        date_idx = [i for i, c in enumerate(cols) if DATE_HINT.search(c)]
        date_min: dict[int, str] = {}
        date_max: dict[int, str] = {}
        rows = 0
        truncated = False
        for row in reader:
            rows += 1
            for i, c in enumerate(cols):
                val = row[i].strip() if i < len(row) else ""
                if val == "" or val.lower() in ("na", "nan", "null", "none"):
                    nulls[c] += 1
                elif i in date_idx:
                    if i not in date_min or val < date_min[i]:
                        date_min[i] = val
                    if i not in date_max or val > date_max[i]:
                        date_max[i] = val
            if rows >= SAMPLE_ROWS:
                truncated = True
                break
    denom = rows or 1
    null_rates = {c: round(nulls[c] / denom, 4) for c in cols}
    dates = {
        cols[i]: {"min": date_min[i], "max": date_max[i]}
        for i in date_idx
        if i in date_min
    }
    facts.update(
        {
            "columns": cols,
            "rows": rows,
            "rows_sampled": truncated,
            "nulls": null_rates,
            "dates": dates,
        }
    )
    return facts


def profile_with_duckdb(path: Path) -> dict:
    con = _DUCKDB.connect(database=":memory:")
    src = str(path).replace("'", "''")
    if path.suffix.lower() == ".parquet":
        reader = f"read_parquet('{src}')"
    else:
        delim = "\\t" if path.suffix.lower() == ".tsv" else ","
        reader = f"read_csv_auto('{src}', delim='{delim}', sample_size=-1)"
    rel = con.sql(f"SELECT * FROM {reader}")
    cols = list(rel.columns)
    types = {c: str(t) for c, t in zip(rel.columns, rel.types)}
    total = con.sql(f"SELECT count(*) FROM {reader}").fetchone()[0]
    nulls: dict[str, float] = {}
    dates: dict[str, dict] = {}
    denom = total or 1
    for c in cols:
        q = c.replace('"', '""')
        n = con.sql(
            f'SELECT count(*) FROM {reader} WHERE "{q}" IS NULL'
        ).fetchone()[0]
        nulls[c] = round(n / denom, 4)
        if "date" in types[c].lower() or "timestamp" in types[c].lower() or DATE_HINT.search(c):
            try:
                mn, mx = con.sql(
                    f'SELECT min("{q}"), max("{q}") FROM {reader}'
                ).fetchone()
                if mn is not None:
                    dates[c] = {"min": str(mn), "max": str(mx)}
            except Exception:
                pass
    con.close()
    return {
        "engine": "duckdb",
        "partial": False,
        "columns": cols,
        "types": types,
        "rows": total,
        "rows_sampled": False,
        "nulls": nulls,
        "dates": dates,
    }


def profile_parquet_pyarrow(path: Path) -> dict:
    pf = _PYARROW.ParquetFile(str(path))
    schema = pf.schema_arrow
    cols = list(schema.names)
    rows = pf.metadata.num_rows
    return {
        "engine": "pyarrow",
        "partial": True,  # null rates + date ranges not computed via metadata-only path
        "columns": cols,
        "types": {n: str(schema.field(n).type) for n in cols},
        "rows": rows,
        "rows_sampled": False,
        "nulls": {},
        "dates": {},
    }


def profile(path: Path) -> dict:
    ext = path.suffix.lower()
    if _DUCKDB is not None:
        try:
            return profile_with_duckdb(path)
        except Exception as exc:  # fall through to stdlib
            note = f"duckdb failed: {exc}"
    else:
        note = None
    if ext == ".parquet":
        if _PYARROW is not None:
            f = profile_parquet_pyarrow(path)
            if note:
                f["note"] = note
            return f
        return {
            "engine": "none",
            "partial": True,
            "columns": [],
            "rows": None,
            "nulls": {},
            "dates": {},
            "note": "parquet profiling needs duckdb or pyarrow (pip install duckdb)",
        }
    delim = "\t" if ext == ".tsv" else ","
    f = profile_delimited(path, delim)
    if note:
        f["note"] = note
    return f


def read_existing_cards(repo: Path) -> dict[str, str]:
    """Map data-file relative path -> recorded sha256 from existing cards."""
    recorded: dict[str, str] = {}
    card_dir = repo / CARD_DIR
    texts: list[str] = []
    if card_dir.exists():
        for card in card_dir.rglob("*.md"):
            texts.append(card.read_text(encoding="utf-8", errors="replace"))
    legacy = repo / LEGACY_CARD
    if legacy.exists():
        texts.append(legacy.read_text(encoding="utf-8", errors="replace"))
    for text in texts:
        # Associate every recorded hash with the file path it appears near.
        current_file: str | None = None
        for line in text.splitlines():
            fmatch = re.search(r"(data/[\w./\- ]+\.(?:csv|tsv|parquet))", line)
            if fmatch:
                current_file = fmatch.group(1).strip()
            hmatch = HASH_LINE.search(line)
            if hmatch and current_file:
                recorded[current_file] = hmatch.group(1).lower()
    return recorded


def classify(rel: str, digest: str, recorded: dict[str, str]) -> str:
    if rel not in recorded:
        return "ORPHANED"
    return "OK" if recorded[rel] == digest else "STALE"


def stub_text(rel: str, facts: dict, digest: str, size: int) -> str:
    cols = facts.get("columns") or []
    nulls = facts.get("nulls") or {}
    dates = facts.get("dates") or {}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = []
    lines.append(f"# Provenance — `{rel}`")
    lines.append("")
    lines.append("## Human fields (fill these in)")
    lines.append("")
    lines.append("- **Source:** <where did this come from: URL, API, vendor, exchange>")
    lines.append("- **Retrieval date:** <YYYY-MM-DD you pulled it>")
    lines.append("- **Query / API call used:** <exact query, endpoint, or download script + file:line>")
    lines.append("- **Methodology / transformations:** <what raw data became this file; file:line evidence>")
    lines.append("- **License / terms:** <license or usage terms of the source>")
    lines.append("- **Known gaps / caveats:** <survivorship bias, missing periods, imputation, sampling>")
    lines.append("")
    lines.append("## Computed facts (auto-filled — do not edit by hand)")
    lines.append("")
    lines.append(f"- Card generated: {today}")
    lines.append(f"- sha256: `{digest}`")
    lines.append(f"- Size: {size:,} bytes")
    rows = facts.get("rows")
    if rows is not None:
        suffix = " (sampled)" if facts.get("rows_sampled") else ""
        lines.append(f"- Rows: {rows:,}{suffix}")
    lines.append(f"- Columns ({len(cols)}): {', '.join(cols) if cols else '(not profiled)'}")
    if facts.get("engine"):
        lines.append(f"- Profiling engine: {facts['engine']}")
    if facts.get("partial") or facts.get("note"):
        lines.append(f"- Note: {facts.get('note', 'partial profile — some facts unavailable')}")
    if dates:
        lines.append("- Datetime ranges:")
        for c, rng in dates.items():
            lines.append(f"  - `{c}`: {rng['min']} → {rng['max']}")
    hot = {c: r for c, r in nulls.items() if r > 0}
    if hot:
        lines.append("- Null rates (non-zero):")
        for c, r in sorted(hot.items(), key=lambda kv: -kv[1]):
            lines.append(f"  - `{c}`: {r:.1%}")
    elif nulls:
        lines.append("- Null rates: all columns 0% null")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo_path", nargs="?", default=".", help="target repo (default .)")
    ap.add_argument("--emit", action="store_true", help="write provenance stubs for orphans under data/PROVENANCE/")
    ap.add_argument("--verify", action="store_true", help="only report STALE/OK diff vs existing cards; never write")
    ap.add_argument("--json", action="store_true", help="dump raw facts as JSON instead of text tables")
    args = ap.parse_args()

    repo = Path(args.repo_path).resolve()
    if not repo.exists():
        print(f"Path not found: {repo}", file=sys.stderr)
        return 1

    files = find_data_files(repo)
    recorded = read_existing_cards(repo)

    print("=== environment ===")
    print(f"duckdb: {'yes' if _DUCKDB else 'no'}   pyarrow: {'yes' if _PYARROW else 'no'}")
    if not _DUCKDB and not _PYARROW:
        print("hint: pip install duckdb  (for full parquet + fast profiling)")
    print()

    if not files:
        print("=== inventory ===")
        print("No data files found under data/ (looked for .csv/.tsv/.parquet).")
        print("Not applicable: nothing to stamp.")
        return 0

    records: list[dict] = []
    for path in files:
        rel = str(path.relative_to(repo))
        digest = sha256_of(path)
        size = path.stat().st_size
        facts = profile(path)
        status = classify(rel, digest, recorded)
        records.append(
            {
                "file": rel,
                "status": status,
                "sha256": digest,
                "size": size,
                "recorded_sha256": recorded.get(rel),
                **facts,
            }
        )

    if args.json:
        print(json.dumps(records, indent=2, default=str))
        return 0

    print("=== inventory ===")
    print(f"{'status':<9} {'rows':>10} {'cols':>5} {'size':>12}  file")
    for r in records:
        rows = r.get("rows")
        rows_s = f"{rows:,}" if isinstance(rows, int) else "?"
        cols_s = str(len(r.get("columns") or []))
        print(f"{r['status']:<9} {rows_s:>10} {cols_s:>5} {r['size']:>12,}  {r['file']}")
    print()

    orphaned = [r for r in records if r["status"] == "ORPHANED"]
    stale = [r for r in records if r["status"] == "STALE"]
    ok = [r for r in records if r["status"] == "OK"]

    print("=== classification ===")
    print(f"OK: {len(ok)}   STALE: {len(stale)}   ORPHANED: {len(orphaned)}")
    if stale:
        print("\nSTALE (bytes changed since card was written — provenance may be wrong):")
        for r in stale:
            print(f"  {r['file']}")
            print(f"    recorded: {r['recorded_sha256']}")
            print(f"    current : {r['sha256']}")
    if orphaned:
        print("\nORPHANED (no provenance card):")
        for r in orphaned:
            print(f"  {r['file']}")
    print()

    if args.verify:
        rc = 1 if stale else 0
        print("=== verify result ===")
        print("STALE datasets found — cards are out of date." if stale else "All recorded hashes match. Provenance is current.")
        return rc

    if args.emit and orphaned:
        out_dir = repo / CARD_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        print("=== emitted stubs ===")
        for r in orphaned:
            slug = re.sub(r"[^\w.-]+", "_", r["file"])
            dest = out_dir / f"{slug}.md"
            dest.write_text(stub_text(r["file"], r, r["sha256"], r["size"]), encoding="utf-8")
            print(f"wrote {dest.relative_to(repo)}")
        print("\nComputed facts are pre-filled. Fill only the Human fields section per card.")
    elif orphaned:
        print("=== stub preview (first orphan) ===")
        r = orphaned[0]
        print(stub_text(r["file"], r, r["sha256"], r["size"]))
        print("Re-run with --emit to write stubs for all orphans under data/PROVENANCE/.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
