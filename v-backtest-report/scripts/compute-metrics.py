#!/usr/bin/env python3
"""Compute deterministic backtest metrics from a returns file.

Reads a strategy's returns (and optionally weights) from CSV or Parquet and
emits a metrics JSON plus a ready-to-paste Markdown table. Every number the
v-backtest-report skill puts in a report comes from here, so the model never
estimates a metric it could compute.

Usage:
    compute-metrics.py RETURNS_FILE [options]

Metrics: CAGR, annualized volatility, Sharpe, Sortino, Calmar, max drawdown +
duration, VaR95/CVaR95 of period returns, hit rate, best/worst period, sample
dates, and turnover if a weights file is supplied.

Stdlib-first: falls back to the csv module when pandas/pyarrow are absent, so it
still runs on a bare Python 3.11 interpreter (returns CSV only in that mode).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

# Optional heavy deps. Guarded so the script degrades to stdlib CSV parsing.
try:
    import pandas as pd  # type: ignore

    _HAVE_PANDAS = True
except ImportError:  # pragma: no cover - environment dependent
    pd = None  # type: ignore
    _HAVE_PANDAS = False

# Periods-per-year presets for common return frequencies.
FREQ_PERIODS = {
    "daily": 252.0,
    "weekly": 52.0,
    "monthly": 12.0,
    "quarterly": 4.0,
    "yearly": 1.0,
    "annual": 1.0,
}

# Candidate column names we will auto-detect (case-insensitive).
DATE_ALIASES = ("date", "timestamp", "time", "dt", "period")
RETURN_ALIASES = ("return", "returns", "ret", "pnl", "r", "strategy_return")


@dataclass
class Series:
    """A parsed returns series with optional aligned weights rows."""

    dates: list[str]
    returns: list[float]
    # weights_rows[i] = list of asset weights at date i, or None if absent.
    weights_rows: list[list[float]] | None = field(default=None)


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def _norm(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_")


def _pick_column(headers: list[str], aliases: tuple[str, ...]) -> str | None:
    lowered = {_norm(h): h for h in headers}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    # Suffix/substring match as a fallback (e.g. "daily_return").
    for norm_h, original in lowered.items():
        if any(norm_h == a or norm_h.endswith("_" + a) for a in aliases):
            return original
    return None


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if text == "" or text.lower() in {"nan", "na", "none", "null"}:
        return None
    if text.endswith("%"):
        try:
            return float(text[:-1]) / 100.0
        except ValueError:
            return None
    try:
        return float(text)
    except ValueError:
        return None


def _maybe_pct_scale(values: list[float], as_percent: bool) -> list[float]:
    """Convert percent-style returns (e.g. 1.5 meaning 1.5%) to decimals."""
    if as_percent:
        return [v / 100.0 for v in values]
    return values


def load_with_pandas(
    path: Path,
    date_col: str | None,
    return_col: str | None,
    weights_path: Path | None,
    as_percent: bool,
) -> Series:
    if path.suffix.lower() in {".parquet", ".pq"}:
        frame = pd.read_parquet(path)
    else:
        frame = pd.read_csv(path)
    headers = [str(c) for c in frame.columns]
    dcol = date_col or _pick_column(headers, DATE_ALIASES)
    rcol = return_col or _pick_column(headers, RETURN_ALIASES)
    if rcol is None:
        raise ValueError(
            "Could not find a returns column. Use --return-col to name it. "
            f"Columns seen: {headers}"
        )
    frame = frame.dropna(subset=[rcol])
    returns = [float(x) for x in frame[rcol].tolist()]
    returns = _maybe_pct_scale(returns, as_percent)
    if dcol is not None:
        dates = [str(x) for x in frame[dcol].tolist()]
    else:
        dates = [str(i) for i in range(len(returns))]

    weights_rows = None
    if weights_path is not None:
        weights_rows = _load_weights_pandas(weights_path)
    return Series(dates=dates, returns=returns, weights_rows=weights_rows)


def _load_weights_pandas(path: Path) -> list[list[float]]:
    if path.suffix.lower() in {".parquet", ".pq"}:
        frame = pd.read_parquet(path)
    else:
        frame = pd.read_csv(path)
    headers = [str(c) for c in frame.columns]
    dcol = _pick_column(headers, DATE_ALIASES)
    asset_cols = [h for h in headers if h != dcol]
    rows: list[list[float]] = []
    for _, row in frame.iterrows():
        rows.append([float(_to_float(row[c]) or 0.0) for c in asset_cols])
    return rows


def load_with_stdlib(
    path: Path,
    date_col: str | None,
    return_col: str | None,
    weights_path: Path | None,
    as_percent: bool,
) -> Series:
    if path.suffix.lower() in {".parquet", ".pq"}:
        raise RuntimeError(
            "Parquet input requires pandas + pyarrow. Install with: "
            "pip install pandas pyarrow"
        )
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        dcol = date_col or _pick_column(headers, DATE_ALIASES)
        rcol = return_col or _pick_column(headers, RETURN_ALIASES)
        if rcol is None:
            raise ValueError(
                "Could not find a returns column. Use --return-col to name it. "
                f"Columns seen: {headers}"
            )
        dates: list[str] = []
        returns: list[float] = []
        for i, row in enumerate(reader):
            value = _to_float(row.get(rcol))
            if value is None:
                continue
            returns.append(value)
            dates.append(str(row.get(dcol)) if dcol else str(i))
    returns = _maybe_pct_scale(returns, as_percent)

    weights_rows = None
    if weights_path is not None:
        weights_rows = _load_weights_stdlib(weights_path)
    return Series(dates=dates, returns=returns, weights_rows=weights_rows)


def _load_weights_stdlib(path: Path) -> list[list[float]]:
    if path.suffix.lower() in {".parquet", ".pq"}:
        raise RuntimeError(
            "Parquet weights require pandas + pyarrow. Install with: "
            "pip install pandas pyarrow"
        )
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        dcol = _pick_column(headers, DATE_ALIASES)
        asset_cols = [h for h in headers if h != dcol]
        rows: list[list[float]] = []
        for row in reader:
            rows.append([float(_to_float(row.get(c)) or 0.0) for c in asset_cols])
    return rows


def load_series(
    path: Path,
    date_col: str | None,
    return_col: str | None,
    weights_path: Path | None,
    as_percent: bool,
) -> tuple[Series, str]:
    """Return (series, loader_name). Prefers pandas, falls back to stdlib."""
    if _HAVE_PANDAS:
        return (
            load_with_pandas(path, date_col, return_col, weights_path, as_percent),
            "pandas",
        )
    return (
        load_with_stdlib(path, date_col, return_col, weights_path, as_percent),
        "stdlib-csv",
    )


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float], ddof: int = 1) -> float:
    n = len(values)
    if n <= ddof:
        return 0.0
    mu = _mean(values)
    var = sum((v - mu) ** 2 for v in values) / (n - ddof)
    return math.sqrt(var)


def _percentile(sorted_vals: list[float], pct: float) -> float:
    """Linear-interpolation percentile on an already-sorted list."""
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    rank = pct / 100.0 * (len(sorted_vals) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return sorted_vals[low]
    frac = rank - low
    return sorted_vals[low] * (1 - frac) + sorted_vals[high] * frac


def _equity_curve(returns: list[float]) -> list[float]:
    equity = []
    level = 1.0
    for r in returns:
        level *= 1.0 + r
        equity.append(level)
    return equity


def _max_drawdown(equity: list[float]) -> tuple[float, int, int, int]:
    """Return (max_drawdown, trough_index, peak_index, longest_underwater)."""
    if not equity:
        return (0.0, 0, 0, 0)
    peak = equity[0]
    peak_idx = 0
    best_peak_idx = 0
    max_dd = 0.0
    trough_idx = 0
    # Underwater duration: longest run below a prior peak.
    underwater = 0
    longest_underwater = 0
    for i, level in enumerate(equity):
        if level >= peak:
            peak = level
            peak_idx = i
            underwater = 0
        else:
            underwater += 1
            longest_underwater = max(longest_underwater, underwater)
        dd = level / peak - 1.0 if peak > 0 else 0.0
        if dd < max_dd:
            max_dd = dd
            trough_idx = i
            best_peak_idx = peak_idx
    return (max_dd, trough_idx, best_peak_idx, longest_underwater)


def _turnover(weights_rows: list[list[float]] | None) -> float | None:
    """Average one-sided turnover: mean of 0.5 * sum|w_t - w_{t-1}| over time."""
    if not weights_rows or len(weights_rows) < 2:
        return None
    width = len(weights_rows[0])
    deltas = []
    for prev, cur in zip(weights_rows, weights_rows[1:]):
        if len(prev) != width or len(cur) != width:
            continue
        turnover = 0.5 * sum(abs(c - p) for p, c in zip(prev, cur))
        deltas.append(turnover)
    return _mean(deltas) if deltas else None


def compute_metrics(
    series: Series, periods_per_year: float, risk_free_annual: float
) -> dict:
    returns = series.returns
    n = len(returns)
    if n == 0:
        raise ValueError("No return observations found after parsing.")

    mean_r = _mean(returns)
    vol_period = _std(returns, ddof=1)
    equity = _equity_curve(returns)
    total_return = equity[-1] - 1.0
    years = n / periods_per_year if periods_per_year > 0 else 0.0

    cagr = (equity[-1] ** (1.0 / years) - 1.0) if years > 0 and equity[-1] > 0 else 0.0
    ann_vol = vol_period * math.sqrt(periods_per_year)

    rf_period = risk_free_annual / periods_per_year if periods_per_year > 0 else 0.0
    excess = [r - rf_period for r in returns]
    excess_mean = _mean(excess)
    sharpe = (
        (excess_mean / vol_period) * math.sqrt(periods_per_year)
        if vol_period > 0
        else 0.0
    )

    downside = [min(0.0, r - rf_period) for r in returns]
    downside_dev = math.sqrt(_mean([d * d for d in downside]))
    sortino = (
        (excess_mean / downside_dev) * math.sqrt(periods_per_year)
        if downside_dev > 0
        else 0.0
    )

    max_dd, trough_idx, peak_idx, underwater = _max_drawdown(equity)
    calmar = (cagr / abs(max_dd)) if max_dd < 0 else 0.0

    ordered = sorted(returns)
    var95 = _percentile(ordered, 5.0)  # 5th percentile of returns
    tail = [r for r in returns if r <= var95]
    cvar95 = _mean(tail) if tail else var95

    wins = sum(1 for r in returns if r > 0)
    hit_rate = wins / n

    turnover = _turnover(series.weights_rows)

    return {
        "observations": n,
        "start_date": series.dates[0] if series.dates else None,
        "end_date": series.dates[-1] if series.dates else None,
        "years": round(years, 4),
        "periods_per_year": periods_per_year,
        "total_return": total_return,
        "cagr": cagr,
        "mean_period_return": mean_r,
        "annualized_vol": ann_vol,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "max_drawdown": max_dd,
        "max_drawdown_trough_date": (
            series.dates[trough_idx] if series.dates else trough_idx
        ),
        "max_drawdown_peak_date": (
            series.dates[peak_idx] if series.dates else peak_idx
        ),
        "max_drawdown_underwater_periods": underwater,
        "var_95": var95,
        "cvar_95": cvar95,
        "hit_rate": hit_rate,
        "best_period": max(returns),
        "worst_period": min(returns),
        "annual_turnover": (
            turnover * periods_per_year if turnover is not None else None
        ),
        "avg_period_turnover": turnover,
        "risk_free_annual": risk_free_annual,
    }


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.2f}%"


def _num(value: float | None, digits: int = 2) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def render_markdown(m: dict) -> str:
    rows = [
        ("CAGR", _pct(m["cagr"])),
        ("Total return", _pct(m["total_return"])),
        ("Annualized volatility", _pct(m["annualized_vol"])),
        ("Sharpe ratio", _num(m["sharpe"])),
        ("Sortino ratio", _num(m["sortino"])),
        ("Calmar ratio", _num(m["calmar"])),
        ("Max drawdown", _pct(m["max_drawdown"])),
        ("Max DD underwater (periods)", str(m["max_drawdown_underwater_periods"])),
        ("VaR 95% (period)", _pct(m["var_95"])),
        ("CVaR 95% (period)", _pct(m["cvar_95"])),
        ("Hit rate", _pct(m["hit_rate"])),
        ("Best period", _pct(m["best_period"])),
        ("Worst period", _pct(m["worst_period"])),
    ]
    if m["avg_period_turnover"] is not None:
        rows.append(("Avg period turnover", _pct(m["avg_period_turnover"])))
        rows.append(("Annualized turnover", _pct(m["annual_turnover"])))
    else:
        rows.append(("Turnover", "n/a (no weights supplied)"))

    lines = ["| Metric | Value |", "| --- | --- |"]
    for label, value in rows:
        lines.append(f"| {label} | {value} |")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute deterministic backtest metrics from a returns file."
    )
    parser.add_argument(
        "returns_file", help="Path to returns CSV or Parquet (one row per period)."
    )
    parser.add_argument(
        "--weights-file",
        default=None,
        help="Optional CSV/Parquet of per-period asset weights for turnover.",
    )
    parser.add_argument("--return-col", default=None, help="Returns column name.")
    parser.add_argument("--date-col", default=None, help="Date/timestamp column name.")
    parser.add_argument(
        "--freq",
        default="daily",
        choices=sorted(FREQ_PERIODS.keys()),
        help="Return frequency preset (default: daily).",
    )
    parser.add_argument(
        "--periods-per-year",
        type=float,
        default=None,
        help="Override annualization factor; wins over --freq if given.",
    )
    parser.add_argument(
        "--risk-free",
        type=float,
        default=0.0,
        help="Annual risk-free rate as a decimal (e.g. 0.04). Default 0.",
    )
    parser.add_argument(
        "--as-percent",
        action="store_true",
        help="Treat return values as percent points (1.5 => 0.015).",
    )
    parser.add_argument(
        "--format",
        default="both",
        choices=("json", "markdown", "both"),
        help="Output format (default: both).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    returns_path = Path(args.returns_file)
    if not returns_path.exists():
        print(f"Returns file not found: {returns_path}", file=sys.stderr)
        return 2
    weights_path = Path(args.weights_file) if args.weights_file else None
    if weights_path is not None and not weights_path.exists():
        print(f"Weights file not found: {weights_path}", file=sys.stderr)
        return 2

    periods = (
        args.periods_per_year
        if args.periods_per_year is not None
        else FREQ_PERIODS[args.freq]
    )

    try:
        series, loader = load_series(
            returns_path,
            args.date_col,
            args.return_col,
            weights_path,
            args.as_percent,
        )
        metrics = compute_metrics(series, periods, args.risk_free)
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    metrics["_meta"] = {
        "returns_file": str(returns_path),
        "weights_file": str(weights_path) if weights_path else None,
        "loader": loader,
        "generated_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "freq": args.freq if args.periods_per_year is None else "custom",
    }

    if args.format in ("json", "both"):
        print("=== metrics json ===")
        print(json.dumps(metrics, indent=2, default=str))
        print()
    if args.format in ("markdown", "both"):
        print("=== metrics markdown ===")
        print(render_markdown(metrics))

    print("✅ Metrics computed successfully", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
