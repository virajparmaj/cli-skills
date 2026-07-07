#!/usr/bin/env python3
"""Scan a backtesting repo for lookahead, leakage, survivorship, and fantasy-fill patterns.

Read-only. Walks *.py and *.ipynb, greps for the classic backtest invalidators, and
prints deterministic date-span facts so split violations are mechanical, not judgment.

The model reads this output first, then opens the flagged files to confirm each hit
in context (some patterns are legitimate; this script surfaces candidates, not verdicts).

Usage:
    scripts/scan-leakage.py [repo_path]   # repo_path defaults to "."
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

# Directories that never contain the code under audit.
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ipynb_checkpoints", "venv", ".venv", "env", ".env",
    "site-packages", "dist", "build", ".next", ".cache", "target",
}

# Each pattern: (regex, severity_hint, short_label, why_it_matters).
# severity_hint is advisory for the model; it still confirms severity in context.
PATTERNS: list[tuple[str, str, str, str]] = [
    # --- Lookahead bias -----------------------------------------------------
    (r"\.shift\(\s*-\s*\d+", "P0", "negative-shift",
     "shift(-n) pulls FUTURE bars into a feature/signal (lookahead)"),
    (r"\.shift\(\s*periods\s*=\s*-\s*\d+", "P0", "negative-shift-kw",
     "shift(periods=-n) pulls future bars into the present (lookahead)"),
    (r"\.rolling\([^)]*center\s*=\s*True", "P0", "centered-rolling",
     "center=True rolling window uses future bars in every value (lookahead)"),
    (r"\.iloc\[[^\]]*\bi\s*\+\s*\d+", "P1", "forward-iloc",
     "iloc[i+k] indexes forward in a loop — possible future access"),
    (r"\.rolling\([^)]*\)\.(mean|std|sum)\(\)[^\n]*\.shift\(\s*0", "P2", "rolling-noshift",
     "rolling stat without a +1 shift may include the current (unfinished) bar"),
    (r"\bffill\(\)|\.fillna\([^)]*method\s*=\s*['\"]ffill", "P3", "ffill",
     "forward-fill is fine forward, but bfill/interpolate near it can leak"),
    (r"\bbfill\(\)|\.fillna\([^)]*method\s*=\s*['\"]bfill", "P1", "bfill",
     "backward-fill copies FUTURE values backward (leakage into the past)"),
    (r"\.interpolate\(", "P2", "interpolate",
     "interpolate() uses both neighbors — future information bleeds backward"),
    (r"\.resample\(", "P2", "resample",
     "resample can right-label a bar; confirm alignment does not expose the close early"),
    # --- Data leakage / bad splits -----------------------------------------
    (r"train_test_split\([^)]*shuffle\s*=\s*True", "P0", "shuffle-split",
     "shuffle=True destroys time order — trains on the future, tests on the past"),
    (r"train_test_split\((?![^)]*shuffle)", "P1", "default-split",
     "train_test_split defaults to shuffle=True — invalid for time series"),
    (r"\b(KFold|cross_val_score|cross_validate|StratifiedKFold)\b", "P1", "random-cv",
     "plain KFold/cross_val shuffles folds — use TimeSeriesSplit for temporal data"),
    (r"\.fit_transform\(", "P1", "fit_transform",
     "fit_transform on the full frame fits the scaler on test data (leakage)"),
    (r"(StandardScaler|MinMaxScaler|RobustScaler|Normalizer)\(\)[^\n]*\.fit\(", "P1",
     "scaler-fit",
     "scaler .fit() — confirm it runs on TRAIN ONLY, before the split leaks stats"),
    (r"\.fit\([^)]*\)[^\n]*#.*full|full.*\.fit\(", "P2", "fit-full",
     "model/scaler fit on the full dataset comment — verify split precedes fit"),
    # --- Survivorship -------------------------------------------------------
    (r"(current|latest|today|active)[_ ]?(tickers|symbols|universe|constituents)",
     "P1", "asof-universe",
     "universe named 'current/latest/active' suggests as-of-today survivorship bias"),
    (r"\.dropna\(\s*\)", "P2", "blanket-dropna",
     "blanket dropna() can silently drop delisted/missing rows (survivorship)"),
    (r"yf\.download|yfinance|Ticker\(", "P2", "yfinance-universe",
     "yfinance returns only currently-listed symbols — delisted names are missing"),
    # --- Transaction-cost realism / fantasy fills --------------------------
    (r"(cost|fee|commission|slippage|spread|funding)\s*=\s*0(\.0+)?\b", "P0",
     "zero-cost",
     "explicit zero cost/fee/slippage/funding — fills are frictionless (inflated PnL)"),
    (r"price\s*\[[^\]]*\]\s*(==|=)\s*[^\n]*close", "P2", "close-fill",
     "executing at the same-bar close you used to generate the signal (same-bar fill)"),
    (r"signal[^\n]*\bclose\b[^\n]*\n[^\n]*execut", "P2", "same-bar-exec",
     "signal and execution both reference the same bar's close (no decision lag)"),
    (r"return[s]?\s*=\s*[^\n]*\.pct_change\(\)[^\n]*\bsignal", "P2", "signal-times-return",
     "returns * signal on the SAME row assumes instant fill at signal time"),
]

COMPILED = [(re.compile(rx), sev, label, why) for rx, sev, label, why in PATTERNS]

# Column names that strongly imply the target/label — leaking these into features is fatal.
TARGET_TOKENS = re.compile(
    r"\b(y|label|labels|target|targets|y_true|future_return|fwd_return|fwd_ret|"
    r"next_return|next_ret|ret_fwd|forward_ret)\b",
    re.IGNORECASE,
)

DATE_ASSIGN = re.compile(
    r"(train_end|test_start|train_start|test_end|split_date|cutoff|val_start|val_end)"
    r"\s*=\s*['\"]?(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)


@dataclass
class Hit:
    path: str
    line: int
    severity: str
    label: str
    why: str
    snippet: str


@dataclass
class FileResult:
    path: str
    hits: list[Hit] = field(default_factory=list)
    declared_dates: list[tuple[int, str, str]] = field(default_factory=list)


def iter_source_files(root: Path):
    """Yield (path, is_notebook) for every *.py and *.ipynb under root, skipping junk."""
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix == ".py":
            yield path, False
        elif path.suffix == ".ipynb":
            yield path, True


def notebook_source(path: Path) -> str:
    """Concatenate code-cell source from a notebook into one text blob.

    Falls back gracefully if nbformat is unavailable or the file is malformed.
    """
    try:
        import nbformat  # optional; stdlib json fallback below
    except ImportError:
        nbformat = None

    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

    if nbformat is not None:
        try:
            nb = nbformat.reads(raw, as_version=4)
            return "\n".join(
                "".join(cell.get("source", ""))
                if isinstance(cell.get("source"), list)
                else str(cell.get("source", ""))
                for cell in nb.cells
                if cell.get("cell_type") == "code"
            )
        except Exception:
            pass  # fall through to raw json parse

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return ""
    parts: list[str] = []
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", "")
        parts.append("".join(src) if isinstance(src, list) else str(src))
    return "\n".join(parts)


def strip_comment(line: str) -> str:
    """Best-effort removal of trailing # comments so we don't match commented-out code."""
    try:
        toks = tokenize.generate_tokens(io.StringIO(line).readline)
        out = []
        for tok in toks:
            if tok.type == tokenize.COMMENT:
                break
            out.append(tok.string)
        rebuilt = "".join(out).strip()
        return rebuilt if rebuilt else line
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return line


def scan_text(rel_path: str, text: str) -> FileResult:
    result = FileResult(path=rel_path)
    lines = text.splitlines()

    # Track feature-column and target-column vocabulary for overlap detection.
    feature_cols: set[str] = set()
    target_cols: set[str] = set()

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")
        code = strip_comment(line)
        if not code.strip():
            continue

        for regex, sev, label, why in COMPILED:
            if regex.search(code):
                result.hits.append(
                    Hit(rel_path, idx, sev, label, why, code.strip()[:160])
                )

        for m in DATE_ASSIGN.finditer(code):
            result.declared_dates.append((idx, m.group(1).lower(), m.group(2)))

        # Heuristic feature/target column capture from list assignments.
        low = code.lower()
        if "feature" in low and ("=" in code) and ("[" in code):
            feature_cols.update(re.findall(r"['\"]([A-Za-z0-9_]+)['\"]", code))
        if TARGET_TOKENS.search(low) and "[" in code:
            target_cols.update(
                t for t in re.findall(r"['\"]([A-Za-z0-9_]+)['\"]", code)
                if TARGET_TOKENS.search(t)
            )

    overlap = feature_cols & target_cols
    if overlap:
        result.hits.append(
            Hit(
                rel_path,
                0,
                "P0",
                "target-in-features",
                "target/label column appears in the feature set: "
                + ", ".join(sorted(overlap)),
                "columns=" + ", ".join(sorted(overlap)),
            )
        )
    return result


def find_data_files(root: Path) -> list[Path]:
    exts = {".csv", ".parquet", ".feather"}
    out = []
    for path in sorted(root.rglob("*")):
        if path.is_dir() or any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.suffix.lower() in exts and path.stat().st_size < 200_000_000:
            out.append(path)
    return out[:50]


def dataset_date_span(path: Path) -> str | None:
    """Return 'min .. max' for the first datetime-like column, or None. pandas optional."""
    try:
        import pandas as pd
    except ImportError:
        return None
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, nrows=200_000)
        elif path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            df = pd.read_feather(path)
    except Exception:
        return None

    for col in df.columns:
        name = str(col).lower()
        if any(k in name for k in ("date", "time", "timestamp", "dt")):
            try:
                s = pd.to_datetime(df[col], errors="coerce").dropna()
                if len(s):
                    return f"{col}: {s.min().date()} .. {s.max().date()} (n={len(s)})"
            except Exception:
                continue
    # Fall back to a DatetimeIndex if the file was saved with one.
    try:
        idx = pd.to_datetime(df.index, errors="coerce")
        idx = idx.dropna()
        if len(idx):
            return f"<index>: {idx.min().date()} .. {idx.max().date()} (n={len(idx)})"
    except Exception:
        pass
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_path", nargs="?", default=".", help="repo root (default .)")
    args = parser.parse_args()

    root = Path(args.repo_path).resolve()
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 1

    results: list[FileResult] = []
    scanned = 0
    for path, is_nb in iter_source_files(root):
        rel = str(path.relative_to(root))
        text = notebook_source(path) if is_nb else _safe_read(path)
        if not text:
            continue
        scanned += 1
        res = scan_text(rel, text)
        if res.hits or res.declared_dates:
            results.append(res)

    print("=== scan summary ===")
    print(f"repo: {root}")
    print(f"source files scanned: {scanned}")
    total_hits = sum(len(r.hits) for r in results)
    print(f"candidate hits: {total_hits}")
    print()

    # Group hits by severity for a fast triage read.
    by_sev: dict[str, list[Hit]] = {}
    for r in results:
        for h in r.hits:
            by_sev.setdefault(h.severity, []).append(h)

    print("=== hit counts by severity hint ===")
    for sev in ("P0", "P1", "P2", "P3"):
        print(f"{sev}: {len(by_sev.get(sev, []))}")
    print("(severity is advisory — confirm each in context; some hits are legitimate)")
    print()

    print("=== flagged patterns (file:line — label — why) ===")
    if total_hits == 0:
        print("none — no lookahead/leakage/survivorship/cost patterns matched")
    for sev in ("P0", "P1", "P2", "P3"):
        for h in sorted(by_sev.get(sev, []), key=lambda x: (x.path, x.line)):
            loc = f"{h.path}:{h.line}" if h.line else h.path
            print(f"[{h.severity}] {loc} — {h.label} — {h.why}")
            if h.snippet:
                print(f"        > {h.snippet}")
    print()

    print("=== declared split boundaries (from code) ===")
    any_dates = False
    for r in results:
        for line, name, val in r.declared_dates:
            any_dates = True
            print(f"{r.path}:{line} — {name} = {val}")
    if not any_dates:
        print("none found — no train_end/test_start/split_date literals in code")
    print()

    print("=== dataset date spans (compare against split boundaries above) ===")
    data_files = find_data_files(root)
    if not data_files:
        print("no csv/parquet/feather data files found under repo")
    else:
        got_any = False
        for f in data_files:
            span = dataset_date_span(f)
            if span:
                got_any = True
                print(f"{f.relative_to(root)} — {span}")
        if not got_any:
            print("data files present but pandas unavailable or no datetime column detected")
            print("hint: pip install pandas pyarrow  # to enable date-span facts")
    print()

    print("=== how to read this ===")
    print("- P0 hits are likely invalidators (lookahead, shuffle split, zero cost,")
    print("  target-in-features). Open each and confirm before calling the result invalid.")
    print("- Cross-check declared split dates against dataset spans: a split_date that")
    print("  sits outside a dataset's min..max means the split silently did nothing.")
    print("- Absence of cost/slippage hits with a nonzero declared cost is GOOD; absence")
    print("  of any cost handling at all is itself a fantasy-fill finding.")
    return 0


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


if __name__ == "__main__":
    raise SystemExit(main())
