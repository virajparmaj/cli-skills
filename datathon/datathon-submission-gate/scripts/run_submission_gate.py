#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from shared_paths import resolve_datathon_paths


PATHS = resolve_datathon_paths()
TEMPLATE_PATH = PATHS["template_path"]
RAW_DIR = PATHS["raw_dir"]
PORTFOLIOS = ["A", "B", "C", "D"]
TARGET_YEAR = 2025
TARGET_MONTH = 8
MAX_REPORT_ITEMS = 100


def safe_float(value: str | float | int) -> float:
    text = str(value).strip() if value is not None else ""
    if not text:
        raise ValueError("blank numeric value")
    return float(text)


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(int(q * (len(ordered) - 1)), len(ordered) - 1)
    return ordered[index]


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def load_historical_thresholds(raw_dir: Path) -> tuple[dict[tuple[str, int], dict[str, float]], dict[str, float]]:
    slot_values: dict[tuple[str, int], list[float]] = defaultdict(list)
    daily_values: dict[str, list[float]] = defaultdict(list)

    for portfolio in PORTFOLIOS:
        interval_path = raw_dir / f"{portfolio}___Interval.csv"
        daily_workload: dict[tuple[str, str], float] = defaultdict(float)
        with interval_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                interval = str(row["Interval"]).strip()
                if not interval:
                    continue
                hours, minutes = interval.split(":")[:2]
                slot = int(hours) * 2 + (1 if int(minutes) >= 30 else 0)
                calls = float(str(row["Call Volume"]).strip() or 0.0)
                cct = float(str(row["CCT"]).strip() or 0.0)
                workload = calls * cct
                slot_values[(portfolio, slot)].append(workload)
                daily_workload[(str(row["Month"]).strip(), str(row["Day"]).strip())] += workload
        daily_values[portfolio].extend(daily_workload.values())

    slot_thresholds = {
        key: {"workload_p99": quantile(values, 0.99)}
        for key, values in slot_values.items()
    }
    daily_thresholds = {
        portfolio: quantile(values, 0.99)
        for portfolio, values in daily_values.items()
    }
    return slot_thresholds, daily_thresholds


def parse_daily_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%m/%d/%y %a").date()


def load_august_daily_targets(raw_dir: Path) -> dict[tuple[str, int], int]:
    targets: dict[tuple[str, int], int] = {}

    for portfolio in PORTFOLIOS:
        daily_path = raw_dir / f"{portfolio}___Daily.csv"
        observed: dict[int, float] = {}
        by_dow: dict[int, list[float]] = defaultdict(list)
        overall_values: list[float] = []

        with daily_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                record_date = parse_daily_date(str(row["Date"]))
                if record_date.year != TARGET_YEAR or record_date.month != TARGET_MONTH:
                    continue
                calls_text = str(row.get("Call Volume", "")).strip()
                if not calls_text:
                    continue
                calls = float(calls_text)
                observed[record_date.day] = calls
                by_dow[record_date.weekday()].append(calls)
                overall_values.append(calls)

        fallback = sum(overall_values) / len(overall_values) if overall_values else 0.0
        for day_num in range(1, 32):
            if day_num in observed:
                targets[(portfolio, day_num)] = int(round(observed[day_num]))
                continue
            weekday = date(TARGET_YEAR, TARGET_MONTH, day_num).weekday()
            dow_values = by_dow.get(weekday, [])
            fill_value = sum(dow_values) / len(dow_values) if dow_values else fallback
            targets[(portfolio, day_num)] = int(round(fill_value))

    return targets


def validate_forecast(
    template_header: list[str],
    template_rows: list[dict[str, str]],
    forecast_header: list[str],
    forecast_rows: list[dict[str, str]],
    slot_thresholds: dict[tuple[str, int], dict[str, float]],
    daily_thresholds: dict[str, float],
    daily_targets: dict[tuple[str, int], int],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if forecast_header != template_header:
        errors.append("Header does not match the template exactly.")

    if len(forecast_rows) != len(template_rows):
        errors.append(f"Row count mismatch. expected={len(template_rows)} actual={len(forecast_rows)}")

    days_seen: set[int] = set()
    intervals_per_day: dict[int, int] = defaultdict(int)
    daily_workload: dict[tuple[str, str], float] = defaultdict(float)
    daily_calls: dict[tuple[str, int], int] = defaultdict(int)

    for index, (template_row, forecast_row) in enumerate(zip(template_rows, forecast_rows), start=1):
        template_key = (template_row["Month"], template_row["Day"], template_row["Interval"])
        forecast_key = (forecast_row.get("Month", ""), forecast_row.get("Day", ""), forecast_row.get("Interval", ""))
        if template_key != forecast_key:
            errors.append(f"Key mismatch at row {index}. expected={template_key} actual={forecast_key}")
            continue

        day_number = int(float(forecast_row["Day"]))
        days_seen.add(day_number)
        intervals_per_day[day_number] += 1

        interval = str(forecast_row["Interval"]).strip()
        hours, minutes = interval.split(":")[:2]
        slot = int(hours) * 2 + (1 if int(minutes) >= 30 else 0)

        for portfolio in PORTFOLIOS:
            prefix = f"row {index} {portfolio}"
            try:
                calls = safe_float(forecast_row[f"Calls_Offered_{portfolio}"])
                abandoned_calls = safe_float(forecast_row[f"Abandoned_Calls_{portfolio}"])
                rate = safe_float(forecast_row[f"Abandoned_Rate_{portfolio}"])
                cct = safe_float(forecast_row[f"CCT_{portfolio}"])
            except ValueError as exc:
                errors.append(f"{prefix}: {exc}")
                continue

            if calls < 0 or abandoned_calls < 0 or cct < 0:
                errors.append(f"{prefix}: negative output detected.")
            if round(calls) != calls:
                errors.append(f"{prefix}: Calls_Offered must be integer-valued.")
            if round(abandoned_calls) != abandoned_calls:
                errors.append(f"{prefix}: Abandoned_Calls must be integer-valued.")
            if not 0.0 <= rate <= 1.0:
                errors.append(f"{prefix}: abandoned rate out of bounds.")
            if calls == 0 and (abandoned_calls != 0 or rate != 0 or cct != 0):
                errors.append(f"{prefix}: zero-volume row has non-zero dependent values.")

            expected_abandoned = min(int(round(calls)), int(round(calls * rate)))
            if int(round(abandoned_calls)) != expected_abandoned:
                errors.append(
                    f"{prefix}: abandoned calls must equal min(calls, round(calls * rate)). expected={expected_abandoned} actual={int(round(abandoned_calls))}"
                )
            if rate > 0.50:
                warnings.append(f"{prefix}: abandon rate above 0.50.")

            workload = calls * cct
            daily_workload[(portfolio, forecast_row["Day"])] += workload
            daily_calls[(portfolio, day_number)] += int(round(calls))
            slot_threshold = slot_thresholds.get((portfolio, slot), {}).get("workload_p99", 0.0)
            if slot_threshold and workload > slot_threshold * 1.50:
                warnings.append(f"{prefix}: workload tail warning at interval {interval}.")
            if cct > 900:
                warnings.append(f"{prefix}: very high CCT={cct:.2f}.")
            if rate > 0.35 and calls < 25:
                warnings.append(f"{prefix}: high abandon rate on low volume.")

    expected_days = set(range(1, 32))
    missing_days = expected_days - days_seen
    extra_days = days_seen - expected_days
    if missing_days:
        errors.append(f"Missing days: {sorted(missing_days)}")
    if extra_days:
        errors.append(f"Unexpected days: {sorted(extra_days)}")

    bad_interval_days = sorted(day for day, count in intervals_per_day.items() if count != 48)
    if bad_interval_days:
        errors.append(f"Days with wrong interval count: {bad_interval_days}")

    for (portfolio, day_num), expected_calls in sorted(daily_targets.items()):
        actual_calls = daily_calls.get((portfolio, day_num), 0)
        if actual_calls != expected_calls:
            errors.append(
                f"{portfolio} day {day_num}: daily calls must match Aug 2025 target. expected={expected_calls} actual={actual_calls}"
            )

    for (portfolio, day_value), workload in sorted(daily_workload.items()):
        threshold = daily_thresholds.get(portfolio, 0.0)
        if threshold and workload > threshold * 1.25:
            warnings.append(f"{portfolio} day {day_value}: daily workload tail warning.")

    return errors, warnings


def render_report(errors: list[str], warnings: list[str]) -> str:
    lines = [
        "# Submission Gate",
        "",
        f"- Hard failures: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        f"- Verdict: {'safe to submit' if not errors else 'do not submit'}",
        "",
        "## Failures",
    ]
    if errors:
        lines.extend(f"- {item}" for item in errors[:MAX_REPORT_ITEMS])
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings"])
    if warnings:
        lines.extend(f"- {item}" for item in warnings[:MAX_REPORT_ITEMS])
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a datathon submission-format forecast.")
    parser.add_argument("--forecast", type=Path, required=True, help="Submission-format forecast CSV.")
    parser.add_argument("--template", type=Path, default=TEMPLATE_PATH)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--output", type=Path, help="Optional markdown output path.")
    args = parser.parse_args()

    template_header, template_rows = load_csv(args.template)
    forecast_header, forecast_rows = load_csv(args.forecast)
    slot_thresholds, daily_thresholds = load_historical_thresholds(args.raw_dir)
    daily_targets = load_august_daily_targets(args.raw_dir)
    errors, warnings = validate_forecast(
        template_header,
        template_rows,
        forecast_header,
        forecast_rows,
        slot_thresholds,
        daily_thresholds,
        daily_targets,
    )
    report = render_report(errors, warnings)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
