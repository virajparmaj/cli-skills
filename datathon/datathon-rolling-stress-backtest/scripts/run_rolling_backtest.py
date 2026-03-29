#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from shared_paths import resolve_datathon_paths


PATHS = resolve_datathon_paths()
RAW_DIR = PATHS["raw_dir"]
DEFAULT_PLAN_OUT = PATHS["reports_dir"] / "rolling_backtest_plan.csv"
MONTH_TO_NUMBER = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def safe_float(value: str | float | int) -> float:
    text = str(value).strip() if value is not None else ""
    return float(text) if text else 0.0


def parse_interval_history_dates(raw_dir: Path) -> dict[str, list[date]]:
    by_portfolio: dict[str, set[date]] = {}
    for portfolio in ["A", "B", "C", "D"]:
        path = raw_dir / f"{portfolio}___Interval.csv"
        dates: set[date] = set()
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                month = MONTH_TO_NUMBER[str(row["Month"]).strip()]
                day = int(float(row["Day"]))
                dates.add(date(2025, month, day))
        by_portfolio[portfolio] = dates
    return {portfolio: sorted(values) for portfolio, values in by_portfolio.items()}


def build_windows(
    raw_dir: Path,
    train_days: int,
    eval_days: int,
    step_days: int,
) -> list[dict[str, str]]:
    by_portfolio = parse_interval_history_dates(raw_dir)
    common_dates = sorted(set.intersection(*(set(values) for values in by_portfolio.values())))
    if len(common_dates) < train_days + eval_days:
        raise ValueError("Not enough common dates to build rolling windows.")

    first_date = common_dates[0]
    common_lookup = set(common_dates)
    windows: list[dict[str, str]] = []
    window_number = 1
    anchor = first_date + timedelta(days=train_days)
    last_eval_end = common_dates[-1]

    while anchor + timedelta(days=eval_days - 1) <= last_eval_end:
        train_start = anchor - timedelta(days=train_days)
        train_end = anchor - timedelta(days=1)
        eval_start = anchor
        eval_end = anchor + timedelta(days=eval_days - 1)
        if all(day in common_lookup for day in date_range(train_start, eval_end)):
            windows.append(
                {
                    "window_id": f"W{window_number:02d}",
                    "train_start": train_start.isoformat(),
                    "train_end": train_end.isoformat(),
                    "eval_start": eval_start.isoformat(),
                    "eval_end": eval_end.isoformat(),
                    "train_days": str(train_days),
                    "eval_days": str(eval_days),
                }
            )
            window_number += 1
        anchor += timedelta(days=step_days)

    if not windows:
        raise ValueError("No complete rolling windows were produced from the common date grid.")
    return windows


def date_range(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.strip())


def slot_index_from_row(row: dict[str, str]) -> int:
    if str(row.get("slot_index", "")).strip():
        return int(float(row["slot_index"]))
    label = row.get("interval_label") or row.get("Interval") or ""
    hours, minutes = label.strip().split(":")[:2]
    return int(hours) * 2 + (1 if int(minutes) >= 30 else 0)


def daypart(slot_index: int) -> str:
    if slot_index <= 11:
        return "overnight"
    if slot_index <= 23:
        return "morning"
    if slot_index <= 35:
        return "afternoon"
    return "evening"


def load_comparison_rows(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, object]] = []
        for raw in reader:
            parsed_date = parse_date(str(raw["date"]))
            slot = slot_index_from_row(raw)
            actual_calls = safe_float(raw["actual_calls_offered"])
            actual_cct = safe_float(raw["actual_cct"])
            forecast_calls = safe_float(raw["forecast_calls_offered"])
            forecast_cct = safe_float(raw["forecast_cct"])
            rows.append(
                {
                    "window_id": str(raw.get("window_id", "")).strip() or "W00",
                    "portfolio": str(raw["portfolio"]).strip(),
                    "date": parsed_date.date().isoformat(),
                    "weekday": parsed_date.strftime("%a"),
                    "slot_index": slot,
                    "daypart": daypart(slot),
                    "actual_calls_offered": actual_calls,
                    "forecast_calls_offered": forecast_calls,
                    "actual_cct": actual_cct,
                    "forecast_cct": forecast_cct,
                    "actual_abandoned_rate": safe_float(raw["actual_abandoned_rate"]),
                    "forecast_abandoned_rate": safe_float(raw["forecast_abandoned_rate"]),
                    "actual_workload": actual_calls * actual_cct,
                    "forecast_workload": forecast_calls * forecast_cct,
                }
            )
    return rows


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(int(q * (len(ordered) - 1)), len(ordered) - 1)
    return ordered[index]


def summarize_rows(rows: list[dict[str, object]], alpha: float, beta: float) -> dict[str, float]:
    volume_num = volume_den = 0.0
    cct_num = cct_den = 0.0
    abd_num = abd_den = 0.0
    penalty_num = penalty_den = 0.0
    under_num = over_num = 0.0
    for row in rows:
        actual_calls = float(row["actual_calls_offered"])
        forecast_calls = float(row["forecast_calls_offered"])
        actual_cct = float(row["actual_cct"])
        forecast_cct = float(row["forecast_cct"])
        actual_rate = float(row["actual_abandoned_rate"])
        forecast_rate = float(row["forecast_abandoned_rate"])
        actual_workload = float(row["actual_workload"])
        forecast_workload = float(row["forecast_workload"])

        volume_num += abs(actual_calls - forecast_calls)
        volume_den += abs(actual_calls)
        cct_num += abs(actual_cct - forecast_cct) * actual_calls
        cct_den += actual_calls
        abd_num += abs(actual_rate - forecast_rate)
        abd_den += 1.0
        penalty_den += actual_workload
        if actual_workload >= forecast_workload:
            penalty = alpha * (actual_workload - forecast_workload)
            under_num += penalty
        else:
            penalty = beta * (forecast_workload - actual_workload)
            over_num += penalty
        penalty_num += penalty

    return {
        "rows": len(rows),
        "E_V": volume_num / volume_den if volume_den else 0.0,
        "E_C": cct_num / cct_den if cct_den else 0.0,
        "E_B": abd_num / abd_den if abd_den else 0.0,
        "P_t": penalty_num / penalty_den if penalty_den else 0.0,
        "under_share": under_num / penalty_num if penalty_num else 0.0,
        "over_share": over_num / penalty_num if penalty_num else 0.0,
    }


def rank_groups(rows: list[dict[str, object]], key_name: str, alpha: float, beta: float) -> list[tuple[str, dict[str, float]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key_name])].append(row)
    ranked = [(name, summarize_rows(group_rows, alpha, beta)) for name, group_rows in grouped.items()]
    ranked.sort(key=lambda item: (item[1]["P_t"], item[1]["E_V"], item[1]["E_B"]), reverse=True)
    return ranked


def render_report(rows: list[dict[str, object]], alpha: float, beta: float, top_n: int) -> str:
    overall = summarize_rows(rows, alpha, beta)
    by_window = rank_groups(rows, "window_id", alpha, beta)
    by_portfolio = rank_groups(rows, "portfolio", alpha, beta)
    by_weekday = rank_groups(rows, "weekday", alpha, beta)
    by_daypart = rank_groups(rows, "daypart", alpha, beta)
    by_date = rank_groups(rows, "date", alpha, beta)

    actual_workloads = [float(row["actual_workload"]) for row in rows if float(row["actual_workload"]) > 0]
    peak_cutoff = quantile(actual_workloads, 0.9)
    low_volume_values = [float(row["actual_calls_offered"]) for row in rows if float(row["actual_calls_offered"]) > 0]
    low_volume_cutoff = max(5.0, quantile(low_volume_values, 0.25)) if low_volume_values else 5.0

    peak_rows = [row for row in rows if float(row["actual_workload"]) >= peak_cutoff]
    low_volume_rows = [row for row in rows if float(row["actual_calls_offered"]) <= low_volume_cutoff]
    under_rows = [row for row in rows if float(row["actual_workload"]) >= float(row["forecast_workload"])]
    over_rows = [row for row in rows if float(row["actual_workload"]) < float(row["forecast_workload"])]

    lines = [
        "# Rolling Backtest Report",
        "",
        f"- Rows: {int(overall['rows'])}",
        f"- E_V: {overall['E_V']:.6f}",
        f"- P_t: {overall['P_t']:.6f}",
        f"- E_C: {overall['E_C']:.6f}",
        f"- E_B: {overall['E_B']:.6f}",
        f"- Workload penalty split: under={overall['under_share']:.2%}, over={overall['over_share']:.2%}",
        "",
        "## Worst windows",
    ]
    lines.extend(
        f"- {name}: rows={int(metrics['rows'])}, E_V={metrics['E_V']:.6f}, P_t={metrics['P_t']:.6f}, under_share={metrics['under_share']:.2%}"
        for name, metrics in by_window[:top_n]
    )
    lines.extend(["", "## Worst portfolios"])
    lines.extend(
        f"- {name}: rows={int(metrics['rows'])}, E_V={metrics['E_V']:.6f}, P_t={metrics['P_t']:.6f}"
        for name, metrics in by_portfolio[:top_n]
    )
    lines.extend(["", "## Worst weekdays"])
    lines.extend(
        f"- {name}: rows={int(metrics['rows'])}, E_V={metrics['E_V']:.6f}, P_t={metrics['P_t']:.6f}"
        for name, metrics in by_weekday[:top_n]
    )
    lines.extend(["", "## Worst dayparts"])
    lines.extend(
        f"- {name}: rows={int(metrics['rows'])}, E_V={metrics['E_V']:.6f}, P_t={metrics['P_t']:.6f}"
        for name, metrics in by_daypart[:top_n]
    )
    lines.extend(["", "## Worst dates"])
    lines.extend(
        f"- {name}: rows={int(metrics['rows'])}, E_V={metrics['E_V']:.6f}, P_t={metrics['P_t']:.6f}, under_share={metrics['under_share']:.2%}"
        for name, metrics in by_date[:top_n]
    )
    lines.extend(["", "## Stress slices"])
    for label, subset in [
        ("peak_actual_workload", peak_rows),
        ("low_volume_intervals", low_volume_rows),
        ("underforecast_rows", under_rows),
        ("overforecast_rows", over_rows),
    ]:
        metrics = summarize_rows(subset, alpha, beta) if subset else {"rows": 0, "E_V": 0.0, "P_t": 0.0, "under_share": 0.0}
        lines.append(
            f"- {label}: rows={int(metrics['rows'])}, E_V={metrics['E_V']:.6f}, P_t={metrics['P_t']:.6f}, under_share={metrics['under_share']:.2%}"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a rolling backtest plan or summarize rolling comparison results.")
    parser.add_argument("--mode", choices=["plan", "report"], required=True)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--comparisons", type=Path, help="Row-level comparison CSV exported by the notebook.")
    parser.add_argument("--plan-output", type=Path, default=DEFAULT_PLAN_OUT)
    parser.add_argument("--report-output", type=Path)
    parser.add_argument("--train-days", type=int, default=28)
    parser.add_argument("--eval-days", type=int, default=7)
    parser.add_argument("--step-days", type=int, default=7)
    parser.add_argument("--alpha", type=float, default=2.0)
    parser.add_argument("--beta", type=float, default=1.0)
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args()

    if args.mode == "plan":
        windows = build_windows(args.raw_dir, args.train_days, args.eval_days, args.step_days)
        args.plan_output.parent.mkdir(parents=True, exist_ok=True)
        with args.plan_output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(windows[0].keys()))
            writer.writeheader()
            writer.writerows(windows)
        print(f"Wrote {len(windows)} rolling windows to {args.plan_output}")
        return 0

    if not args.comparisons or not args.comparisons.exists():
        raise SystemExit("Report mode requires --comparisons pointing to a row-level comparison CSV.")
    rows = load_comparison_rows(args.comparisons)
    report = render_report(rows, args.alpha, args.beta, args.top_n)
    if args.report_output:
        args.report_output.parent.mkdir(parents=True, exist_ok=True)
        args.report_output.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
