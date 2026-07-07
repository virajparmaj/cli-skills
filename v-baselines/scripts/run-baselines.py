#!/usr/bin/env python3
"""Run a fixed baseline model zoo under one honest CV protocol.

Deterministic half of the v-baselines skill. Takes a data file and target
column, auto-detects task type (classification vs regression) and whether the
index is datetime (-> TimeSeriesSplit instead of StratifiedKFold), then runs
Dummy, Linear (LogisticRegression/Ridge), RandomForest, and XGBoost (if
installed) -- each wrapped in a Pipeline sharing one splitter and a fixed seed.
Prints a results table and a verdict on whether the fancy model beats the
baselines by more than CV noise. Appends to experiments/runs.csv when it exists
(v-run-ledger).

Requires scikit-learn and pandas; xgboost is optional. Python 3.11+. Read-only
except the optional ledger append.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

SEED = 42


def _need(mod: str):
    try:
        return __import__(mod)
    except Exception:  # noqa: BLE001
        print(f"'{mod}' is required. Install with: pip install {mod}", file=sys.stderr)
        raise SystemExit(2)


def load_xy(path: Path, target: str, datetime_col: str | None):
    pd = _need("pandas")
    df = pd.read_parquet(path) if path.suffix.lower() in {".parquet", ".pq"} else pd.read_csv(path)
    if target not in df.columns:
        print(f"target '{target}' not in columns: {list(df.columns)}", file=sys.stderr)
        raise SystemExit(1)
    is_temporal = False
    if datetime_col and datetime_col in df.columns:
        df = df.sort_values(datetime_col)
        is_temporal = True
    else:
        for c in df.columns:
            if c != target and ("date" in c.lower() or "time" in c.lower()):
                try:
                    df = df.sort_values(c)
                    is_temporal = True
                    break
                except Exception:  # noqa: BLE001
                    pass
    y = df[target]
    X = df.drop(columns=[target]).select_dtypes("number")
    X = X.fillna(X.median(numeric_only=True))
    return X, y, is_temporal


def build_models(task: str):
    from sklearn.dummy import DummyClassifier, DummyRegressor
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    def pipe(est, scale=False):
        steps = []
        if scale:
            steps.append(("scale", StandardScaler()))
        steps.append(("est", est))
        return Pipeline(steps)

    models = {}
    if task == "classification":
        models["dummy"] = pipe(DummyClassifier(strategy="most_frequent"))
        models["linear"] = pipe(LogisticRegression(max_iter=1000, random_state=SEED), scale=True)
        models["forest"] = pipe(RandomForestClassifier(n_estimators=200, random_state=SEED))
    else:
        models["dummy"] = pipe(DummyRegressor(strategy="mean"))
        models["linear"] = pipe(Ridge(random_state=SEED), scale=True)
        models["forest"] = pipe(RandomForestRegressor(n_estimators=200, random_state=SEED))
    try:
        import xgboost as xgb  # noqa: WPS433
        est = (xgb.XGBClassifier(random_state=SEED, n_estimators=300, eval_metric="logloss")
               if task == "classification"
               else xgb.XGBRegressor(random_state=SEED, n_estimators=300))
        models["xgboost"] = pipe(est)
    except Exception:  # noqa: BLE001
        print("(xgboost not installed — skipping it in the zoo)", file=sys.stderr)
    return models


def run(path: Path, target: str, datetime_col: str | None, folds: int):
    _need("sklearn")
    from sklearn.model_selection import (StratifiedKFold, TimeSeriesSplit,
                                         cross_val_score)

    X, y, is_temporal = load_xy(path, target, datetime_col)
    task = "classification" if (y.nunique() <= 20 and y.dtype.kind in "biuO") else "regression"
    scoring = "roc_auc" if (task == "classification" and y.nunique() == 2) else \
              ("accuracy" if task == "classification" else "r2")
    if is_temporal:
        splitter = TimeSeriesSplit(n_splits=folds)
        split_name = f"TimeSeriesSplit({folds})"
    elif task == "classification":
        splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=SEED)
        split_name = f"StratifiedKFold({folds}, shuffle, seed={SEED})"
    else:
        from sklearn.model_selection import KFold
        splitter = KFold(n_splits=folds, shuffle=True, random_state=SEED)
        split_name = f"KFold({folds}, shuffle, seed={SEED})"

    print(f"=== baselines: {path.name} ===")
    print(f"task={task}  scoring={scoring}  cv={split_name}  n={len(X)}  features={X.shape[1]}\n")

    import time
    results = {}
    for name, model in build_models(task).items():
        t0 = time.perf_counter()
        try:
            scores = cross_val_score(model, X, y, cv=splitter, scoring=scoring)
            dt = time.perf_counter() - t0
            results[name] = (float(scores.mean()), float(scores.std()), dt)
        except Exception as exc:  # noqa: BLE001
            print(f"  {name}: ERROR {type(exc).__name__}: {exc}")
    return task, scoring, split_name, results


def verdict(scoring: str, results: dict) -> str:
    if "dummy" not in results or not results:
        return "no dummy baseline to compare against"
    dummy = results["dummy"][0]
    best_name = max(results, key=lambda k: results[k][0])
    best, best_std = results[best_name][0], results[best_name][1]
    lift = best - dummy
    if best_name in ("dummy",):
        return "the dummy baseline is the best model — features carry no signal under this CV"
    if lift <= best_std:
        return (f"best model '{best_name}' beats dummy by {lift:.4f}, within one CV std "
                f"({best_std:.4f}) — NOT a convincing win")
    lin = results.get("linear", (None,))[0]
    extra = ""
    if lin is not None and best_name in ("forest", "xgboost") and (best - lin) <= best_std:
        extra = f"; but it does NOT clearly beat the linear baseline ({lin:.4f}) — prefer the simpler model"
    return f"best model '{best_name}'={best:.4f} beats dummy={dummy:.4f} by {lift:.4f} (> CV std){extra}"


def append_ledger(repo: Path, path: Path, task: str, scoring: str, results: dict) -> None:
    ledger = repo / "experiments" / "runs.csv"
    if not ledger.exists():
        return
    import hashlib
    import json
    import uuid
    from datetime import datetime, timezone
    with ledger.open(newline="") as fh:
        fields = next(csv.reader(fh), [])
    if not fields:
        return
    with ledger.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        for name, (mean, std, _dt) in results.items():
            row = {k: "" for k in fields}
            row.update({
                "run_id": uuid.uuid4().hex[:10],
                "utc_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": f"baseline:{name}", "metric_name": scoring,
                "metric_mean": f"{mean:.6f}", "metric_std": f"{std:.6f}",
                "note": f"v-baselines on {path.name}",
            })
            w.writerow({k: row.get(k, "") for k in fields})
    print(f"\n(appended {len(results)} baseline rows to {ledger})")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", type=Path, help="CSV/Parquet data file")
    ap.add_argument("target", help="target column name")
    ap.add_argument("--datetime-col", help="datetime column (forces TimeSeriesSplit)")
    ap.add_argument("--folds", type=int, default=5, help="CV folds (default 5)")
    ap.add_argument("--repo", type=Path, default=Path("."), help="repo root for ledger append")
    args = ap.parse_args()

    if not args.data.exists():
        print(f"no such file: {args.data}", file=sys.stderr)
        return 1

    task, scoring, _split, results = run(args.data, args.target, args.datetime_col, args.folds)
    print(f"{'model':10} {'mean':>10} {'std':>10} {'fit_s':>8}")
    print("-" * 42)
    for name, (mean, std, dt) in sorted(results.items(), key=lambda kv: -kv[1][0]):
        print(f"{name:10} {mean:>10.4f} {std:>10.4f} {dt:>8.2f}")
    print("\nVERDICT:", verdict(scoring, results))
    append_ledger(args.repo.resolve(), args.data, task, scoring, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
