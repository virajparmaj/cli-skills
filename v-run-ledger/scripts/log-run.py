#!/usr/bin/env python3
"""Append-only experiment ledger: one row per training run.

Deterministic half of the v-run-ledger skill. Appends a row to
experiments/runs.csv capturing run id, UTC timestamp, git SHA + dirty flag,
data-file hash, model class, params JSON + hash, CV metric mean/std, and a note.
Strictly append-only: the script refuses to edit or delete existing rows
(matches the immutability rule). --best <metric> prints the top rows sorted,
answering "which run was best" from the ledger, never from memory.

Pure stdlib, Python 3.11+. Writes only under experiments/.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ["run_id", "utc_time", "git_sha", "git_dirty", "data_hash", "model",
          "params_json", "params_hash", "metric_name", "metric_mean",
          "metric_std", "note"]


def git_state(repo: Path) -> tuple[str, str]:
    def _git(*a):
        return subprocess.run(["git", "-C", str(repo), *a], capture_output=True,
                              text=True).stdout.strip()
    sha = _git("rev-parse", "--short", "HEAD") or "no-git"
    dirty = "dirty" if _git("status", "--porcelain") else "clean"
    return sha, dirty


def file_hash(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def ledger_path(repo: Path) -> Path:
    return repo / "experiments" / "runs.csv"


def ensure_ledger(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as fh:
            csv.writer(fh).writerow(FIELDS)


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def cmd_log(args) -> int:
    repo = Path(args.repo_path).resolve()
    path = ledger_path(repo)
    ensure_ledger(path)

    try:
        params = json.loads(args.params) if args.params else {}
    except json.JSONDecodeError as exc:
        print(f"--params must be valid JSON: {exc}", file=sys.stderr)
        return 1
    params_json = json.dumps(params, sort_keys=True)
    params_hash = hashlib.sha256(params_json.encode()).hexdigest()[:12]
    sha, dirty = git_state(repo)
    row = {
        "run_id": uuid.uuid4().hex[:10],
        "utc_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_sha": sha, "git_dirty": dirty,
        "data_hash": file_hash(Path(args.data)) if args.data else "",
        "model": args.model or "",
        "params_json": params_json, "params_hash": params_hash,
        "metric_name": args.metric or "",
        "metric_mean": args.mean if args.mean is not None else "",
        "metric_std": args.std if args.std is not None else "",
        "note": args.note or "",
    }
    with path.open("a", newline="") as fh:
        csv.DictWriter(fh, fieldnames=FIELDS).writerow(row)
    print("=== appended run ===")
    for k in FIELDS:
        print(f"  {k}: {row[k]}")
    print(f"\nledger: {path}  ({len(read_rows(path))} rows total)")
    return 0


def cmd_best(args) -> int:
    repo = Path(args.repo_path).resolve()
    rows = read_rows(ledger_path(repo))
    rows = [r for r in rows if r.get("metric_name") == args.best and r.get("metric_mean") not in ("", None)]
    if not rows:
        print(f"No runs logged for metric '{args.best}'.")
        return 0
    reverse = not args.minimize
    rows.sort(key=lambda r: float(r["metric_mean"]), reverse=reverse)
    print(f"=== top runs by {args.best} ({'max' if reverse else 'min'} first) ===")
    for r in rows[:args.top]:
        print(f"  {r['metric_mean']:>10}  ±{r['metric_std'] or '?':<8}  "
              f"{r['model']:<16} {r['run_id']}  {r['git_sha']}({r['git_dirty']})  {r['note']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_path", nargs="?", default=".", help="repo root (default .)")
    ap.add_argument("--data", help="path to the training data file (hashed)")
    ap.add_argument("--model", help="model class name, e.g. XGBClassifier")
    ap.add_argument("--params", help="hyperparameters as a JSON string")
    ap.add_argument("--metric", help="CV metric name, e.g. roc_auc")
    ap.add_argument("--mean", type=float, help="CV metric mean")
    ap.add_argument("--std", type=float, help="CV metric std")
    ap.add_argument("--note", help="free-text note")
    ap.add_argument("--best", help="instead of logging, print top runs for this metric")
    ap.add_argument("--minimize", action="store_true", help="with --best, lower is better")
    ap.add_argument("--top", type=int, default=10, help="with --best, how many rows")
    args = ap.parse_args()

    if args.best:
        return cmd_best(args)
    return cmd_log(args)


if __name__ == "__main__":
    raise SystemExit(main())
