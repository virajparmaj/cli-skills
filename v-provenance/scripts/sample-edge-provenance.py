#!/usr/bin/env python3
"""Sample knowledge-graph edges and report any lacking a provenance record.

Deterministic helper for the "no edge without provenance" invariant (vee-cee
and similar graph repos). It locates edge records and provenance records, then
samples edges and reports how many reference a provenance id / source that
actually resolves. It never asserts the invariant holds — it surfaces counts
and concrete offenders so the model can label findings Confirmed vs Strongly
inferred.

Supported edge stores (auto-detected, best-effort, read-only):
  - JSON / JSONL / NDJSON files under graph/, data/, or the repo root whose
    records look like edges (have source+target, or src+dst, or from+to, or a
    "type"/"relation" plus endpoints).
  - CSV edge lists with source/target-style columns.
  - SQLite (.db/.sqlite/.sqlite3) tables named like edge/edges/relation(ship)s.

Provenance is considered present on an edge when it carries a non-empty
provenance-like field (provenance, provenance_id, source, source_id, evidence,
citation, derived_from, retrieved_from) AND, when a provenance store is found,
that reference resolves to a known provenance id.

Python 3.11+, stdlib only (sqlite3 is stdlib). Read-only.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from pathlib import Path

SKIP_PARTS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
SEARCH_DIRS = ("graph", "data", ".")
PROV_FIELDS = (
    "provenance",
    "provenance_id",
    "provenanceId",
    "source",
    "source_id",
    "sourceId",
    "evidence",
    "citation",
    "derived_from",
    "retrieved_from",
)
ID_FIELDS = ("id", "_id", "uid", "provenance_id", "provenanceId", "source_id", "sourceId")
EDGE_ENDPOINTS = (
    ("source", "target"),
    ("src", "dst"),
    ("from", "to"),
    ("from_id", "to_id"),
    ("head", "tail"),
    ("subject", "object"),
)
EDGE_TABLE_HINT = re.compile(r"(edge|edges|relation|relations|relationship|relationships|triple|triples)$", re.IGNORECASE)
PROV_TABLE_HINT = re.compile(r"(provenance|provenances|source|sources|evidence|citation|citations)$", re.IGNORECASE)
MAX_SAMPLE = 500
MAX_OFFENDERS = 25


def iter_files(repo: Path, exts: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()
    for base in SEARCH_DIRS:
        root = repo / base
        if not root.exists():
            continue
        for p in sorted(root.rglob("*") if base != "." else root.glob("*")):
            if not p.is_file() or p.suffix.lower() not in exts:
                continue
            if any(part in SKIP_PARTS for part in p.relative_to(repo).parts):
                continue
            if p in seen:
                continue
            seen.add(p)
            out.append(p)
    return out


def endpoints_of(rec: dict) -> tuple[object, object] | None:
    for a, b in EDGE_ENDPOINTS:
        if a in rec and b in rec:
            return rec[a], rec[b]
    return None


def prov_ref(rec: dict) -> object | None:
    for f in PROV_FIELDS:
        if f in rec and rec[f] not in (None, "", [], {}):
            return rec[f]
    return None


def record_id(rec: dict) -> object | None:
    for f in ID_FIELDS:
        if f in rec and rec[f] not in (None, ""):
            return rec[f]
    return None


def load_json_records(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    recs: list[dict] = []
    if path.suffix.lower() in (".jsonl", ".ndjson"):
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                recs.append(obj)
        return recs
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return []
    if isinstance(obj, list):
        return [o for o in obj if isinstance(o, dict)]
    if isinstance(obj, dict):
        for key in ("edges", "links", "relationships", "relations", "triples"):
            val = obj.get(key)
            if isinstance(val, list):
                return [o for o in val if isinstance(o, dict)]
    return []


def load_csv_records(path: Path) -> list[dict]:
    delim = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open("r", newline="", encoding="utf-8", errors="replace") as fh:
        return list(csv.DictReader(fh, delimiter=delim))


def collect_prov_ids(repo: Path) -> set[str]:
    """Gather provenance record ids from JSON files that look like provenance stores."""
    ids: set[str] = set()
    for path in iter_files(repo, (".json", ".jsonl", ".ndjson")):
        name = path.stem.lower()
        if not PROV_TABLE_HINT.search(name):
            continue
        for rec in load_json_records(path):
            rid = record_id(rec)
            if rid is not None:
                ids.add(str(rid))
    return ids


def scan_edge_file(path: Path) -> tuple[list[dict], str] | None:
    ext = path.suffix.lower()
    if ext in (".json", ".jsonl", ".ndjson"):
        recs = load_json_records(path)
    elif ext in (".csv", ".tsv"):
        recs = load_csv_records(path)
    else:
        return None
    edges = [r for r in recs if isinstance(r, dict) and endpoints_of(r) is not None]
    if not edges:
        return None
    return edges, ext


def report_edges(source: str, edges: list[dict], prov_ids: set[str]) -> dict:
    total = len(edges)
    sample = edges[:MAX_SAMPLE]
    missing: list[dict] = []
    unresolved: list[dict] = []
    for e in sample:
        ref = prov_ref(e)
        if ref is None:
            missing.append(e)
        elif prov_ids and str(ref) not in prov_ids and not isinstance(ref, (list, dict)):
            unresolved.append(e)
    return {
        "source": source,
        "total": total,
        "sampled": len(sample),
        "missing": missing,
        "unresolved": unresolved,
    }


def print_report(rep: dict) -> None:
    src, total, sampled = rep["source"], rep["total"], rep["sampled"]
    miss, unres = rep["missing"], rep["unresolved"]
    print(f"--- {src} ---")
    print(f"edges: {total} (sampled {sampled})")
    print(f"missing provenance field: {len(miss)}")
    print(f"provenance ref does not resolve: {len(unres)}")
    for label, rows in (("MISSING", miss), ("UNRESOLVED", unres)):
        for e in rows[:MAX_OFFENDERS]:
            ep = endpoints_of(e)
            print(f"  [{label}] {ep[0]} -> {ep[1]}")
        if len(rows) > MAX_OFFENDERS:
            print(f"  ... and {len(rows) - MAX_OFFENDERS} more {label}")
    print()


def scan_sqlite(path: Path, prov_ids: set[str]) -> list[dict]:
    reports: list[dict] = []
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error:
        return reports
    try:
        con.row_factory = sqlite3.Row
        tables = [
            r[0]
            for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        for t in tables:
            if not EDGE_TABLE_HINT.search(t):
                continue
            rows = [dict(r) for r in con.execute(f'SELECT * FROM "{t}" LIMIT {MAX_SAMPLE}')]
            edges = [r for r in rows if endpoints_of(r) is not None]
            if not edges:
                continue
            reports.append(report_edges(f"{path.name}::{t}", edges, prov_ids))
    except sqlite3.Error as exc:
        print(f"sqlite error on {path}: {exc}", file=sys.stderr)
    finally:
        con.close()
    return reports


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo_path", nargs="?", default=".", help="target repo (default .)")
    args = ap.parse_args()

    repo = Path(args.repo_path).resolve()
    if not repo.exists():
        print(f"Path not found: {repo}", file=sys.stderr)
        return 1

    prov_ids = collect_prov_ids(repo)
    print("=== provenance store ===")
    if prov_ids:
        print(f"found {len(prov_ids)} provenance record ids")
    else:
        print("no provenance-id store found — refs cannot be resolved, only presence is checked")
    print()

    reports: list[dict] = []
    for path in iter_files(repo, (".json", ".jsonl", ".ndjson", ".csv", ".tsv")):
        found = scan_edge_file(path)
        if found:
            edges, _ = found
            reports.append(report_edges(str(path.relative_to(repo)), edges, prov_ids))
    for path in iter_files(repo, (".db", ".sqlite", ".sqlite3")):
        reports.extend(scan_sqlite(path, prov_ids))

    print("=== edge provenance sampling ===")
    if not reports:
        print("No edge-like records found (source/target, src/dst, from/to, head/tail, subject/object).")
        print("Not applicable: this repo has no detectable knowledge graph.")
        return 0

    for rep in reports:
        print_report(rep)

    total_missing = sum(len(r["missing"]) for r in reports)
    total_unres = sum(len(r["unresolved"]) for r in reports)
    print("=== invariant summary ===")
    if total_missing == 0 and total_unres == 0:
        print("No sampled edge lacks a provenance field. Invariant holds across the sample.")
    else:
        print(f"Sampled edges violating 'no edge without provenance': "
              f"{total_missing} missing field, {total_unres} unresolved ref.")
    return 1 if (total_missing or total_unres) else 0


if __name__ == "__main__":
    raise SystemExit(main())
