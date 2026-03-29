#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from shared_paths import resolve_datathon_paths


PATHS = resolve_datathon_paths()
RAW_DIR = PATHS["raw_dir"]


def safe_float(value: str | float | int) -> float:
    text = str(value).strip() if value is not None else ""
    return float(text) if text else 0.0


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(int(q * (len(ordered) - 1)), len(ordered) - 1)
    return ordered[index]


def interval_to_slot(label: str) -> int:
    cleaned = label.strip()
    if not cleaned:
        raise ValueError("blank interval label")
    parts = cleaned.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    return hours * 2 + (1 if minutes >= 30 else 0)


def load_forecast_rows(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, object]] = []
        for raw in reader:
            month = str(raw["Month"]).strip()
            day = int(float(raw["Day"]))
            interval = str(raw["Interval"]).strip()
            slot = interval_to_slot(interval)
            for portfolio in ["A", "B", "C", "D"]:
                calls = safe_float(raw[f"Calls_Offered_{portfolio}"])
                abandoned_calls = safe_float(raw[f"Abandoned_Calls_{portfolio}"])
                rate = safe_float(raw[f"Abandoned_Rate_{portfolio}"])
                cct = safe_float(raw[f"CCT_{portfolio}"])
                rows.append(
                    {
                        "portfolio": portfolio,
                        "month": month,
                        "day": day,
                        "slot_index": slot,
                        "interval": interval,
                        "calls_offered": calls,
                        "abandoned_calls": abandoned_calls,
                        "abandoned_rate": rate,
                        "cct": cct,
                        "workload": calls * cct,
                    }
                )
        return rows


def load_historical_profiles(raw_dir: Path) -> tuple[dict[tuple[str, int], dict[str, float]], dict[str, dict[str, float]]]:
    slot_values: dict[tuple[str, int], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    daily_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for portfolio in ["A", "B", "C", "D"]:
        interval_path = raw_dir / f"{portfolio}___Interval.csv"
        with interval_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            daily_workload: dict[tuple[str, str], float] = defaultdict(float)
            for row in reader:
                try:
                    slot = interval_to_slot(str(row["Interval"]).strip())
                except ValueError:
                    continue
                calls = safe_float(row["Call Volume"])
                rate = safe_float(row["Abandoned Rate"])
                cct = safe_float(row["CCT"])
                workload = calls * cct
                slot_values[(portfolio, slot)]["calls"].append(calls)
                slot_values[(portfolio, slot)]["rate"].append(rate)
                slot_values[(portfolio, slot)]["cct"].append(cct)
                slot_values[(portfolio, slot)]["workload"].append(workload)
                daily_workload[(str(row["Month"]).strip(), str(row["Day"]).strip())] += workload
            for value in daily_workload.values():
                daily_values[portfolio]["workload"].append(value)

    slot_profiles: dict[tuple[str, int], dict[str, float]] = {}
    for key, metric_map in slot_values.items():
        slot_profiles[key] = {
            "calls_p50": quantile(metric_map["calls"], 0.50),
            "calls_p95": quantile(metric_map["calls"], 0.95),
            "calls_p99": quantile(metric_map["calls"], 0.99),
            "cct_p50": quantile(metric_map["cct"], 0.50),
            "cct_p95": quantile(metric_map["cct"], 0.95),
            "cct_p99": quantile(metric_map["cct"], 0.99),
            "rate_p50": quantile(metric_map["rate"], 0.50),
            "rate_p95": quantile(metric_map["rate"], 0.95),
            "rate_p99": quantile(metric_map["rate"], 0.99),
            "workload_p50": quantile(metric_map["workload"], 0.50),
            "workload_p95": quantile(metric_map["workload"], 0.95),
            "workload_p99": quantile(metric_map["workload"], 0.99),
        }

    daily_profiles: dict[str, dict[str, float]] = {}
    for portfolio, metric_map in daily_values.items():
        workloads = metric_map["workload"]
        daily_profiles[portfolio] = {
            "daily_workload_p95": quantile(workloads, 0.95),
            "daily_workload_p99": quantile(workloads, 0.99),
        }
    return slot_profiles, daily_profiles


def scan_rows(
    rows: list[dict[str, object]],
    slot_profiles: dict[tuple[str, int], dict[str, float]],
    daily_profiles: dict[str, dict[str, float]],
) -> list[dict[str, object]]:
    flags: list[dict[str, object]] = []

    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    daily_workload: dict[tuple[str, int], float] = defaultdict(float)
    for row in rows:
        grouped[(str(row["portfolio"]), int(row["day"]))].append(row)
        daily_workload[(str(row["portfolio"]), int(row["day"]))] += float(row["workload"])

    for (portfolio, day), day_rows in grouped.items():
        day_rows.sort(key=lambda item: int(item["slot_index"]))
        for idx, row in enumerate(day_rows):
            slot = int(row["slot_index"])
            profile = slot_profiles.get((portfolio, slot), {})
            calls = float(row["calls_offered"])
            abandoned_calls = float(row["abandoned_calls"])
            rate = float(row["abandoned_rate"])
            cct = float(row["cct"])
            workload = float(row["workload"])
            label = f"{portfolio} day {day} {row['interval']}"

            if abandoned_calls > calls:
                flags.append({
                    "severity": "high",
                    "metric": "abandoned_calls",
                    "label": label,
                    "detail": "abandoned calls exceed offered calls",
                })
            if rate > 0.50:
                flags.append({
                    "severity": "high",
                    "metric": "abandoned_rate",
                    "label": label,
                    "detail": f"rate={rate:.4f} exceeds the 0.50 guardrail",
                })

            if profile:
                if calls > max(profile["calls_p99"] * 1.35, profile["calls_p50"] * 4.0, 25.0):
                    flags.append({"severity": "high", "metric": "calls", "label": label, "detail": f"calls={calls:.2f} above slot tail"})
                if cct > max(profile["cct_p99"] * 1.35, profile["cct_p50"] * 3.0, 600.0):
                    flags.append({"severity": "high", "metric": "cct", "label": label, "detail": f"cct={cct:.2f} above slot tail"})
                if workload > max(profile["workload_p99"] * 1.35, profile["workload_p50"] * 4.0, 10000.0):
                    flags.append({"severity": "high", "metric": "workload", "label": label, "detail": f"workload={workload:.2f} above slot tail"})
                if rate > max(0.25, profile["rate_p99"] * 1.50) and calls <= max(25.0, profile["calls_p95"]):
                    flags.append({"severity": "medium", "metric": "abandoned_rate", "label": label, "detail": f"rate={rate:.4f} unstable for low-to-mid volume"})

            if slot <= 11 and calls < 5 and (cct > 450 or rate > 0.20):
                flags.append({
                    "severity": "medium",
                    "metric": "overnight_tail",
                    "label": label,
                    "detail": "overnight low-volume interval has sharp CCT or abandon spike",
                })

            if 0 < idx < len(day_rows) - 1:
                prev_cct = float(day_rows[idx - 1]["cct"])
                next_cct = float(day_rows[idx + 1]["cct"])
                local_cct = max(prev_cct, next_cct, 1.0)
                if cct > local_cct * 2.75 and calls < 0.5 * max(float(day_rows[idx - 1]["calls_offered"]), float(day_rows[idx + 1]["calls_offered"]), 10.0):
                    flags.append({"severity": "medium", "metric": "cct_jump", "label": label, "detail": "slot-to-slot CCT jump is too sharp for the local volume context"})
                prev_rate = float(day_rows[idx - 1]["abandoned_rate"])
                next_rate = float(day_rows[idx + 1]["abandoned_rate"])
                local_rate = max(prev_rate, next_rate, 0.01)
                if rate > local_rate * 3.0 and rate > 0.05 and calls < 30:
                    flags.append({"severity": "medium", "metric": "rate_jump", "label": label, "detail": "slot-to-slot abandon-rate jump is too sharp for low volume"})

        profile = daily_profiles.get(portfolio, {})
        daily_total = daily_workload[(portfolio, day)]
        if profile and daily_total > max(profile["daily_workload_p99"] * 1.20, profile["daily_workload_p95"] * 1.35):
            flags.append(
                {
                    "severity": "high",
                    "metric": "daily_workload",
                    "label": f"{portfolio} day {day}",
                    "detail": f"daily workload={daily_total:.2f} above historical daily tail",
                }
            )
    return flags


def render_report(flags: list[dict[str, object]]) -> str:
    by_metric: dict[str, int] = defaultdict(int)
    by_severity: dict[str, int] = defaultdict(int)
    for flag in flags:
        by_metric[str(flag["metric"])] += 1
        by_severity[str(flag["severity"])] += 1

    lines = [
        "# Tail Risk Scan",
        "",
        f"- Total flags: {len(flags)}",
        f"- High: {by_severity.get('high', 0)}",
        f"- Medium: {by_severity.get('medium', 0)}",
        "",
        "## Flags by metric",
    ]
    lines.extend(f"- {metric}: {count}" for metric, count in sorted(by_metric.items()))
    lines.extend(["", "## Top flags"])
    for flag in flags[:20]:
        lines.append(f"- [{flag['severity']}] {flag['metric']} | {flag['label']} | {flag['detail']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a datathon forecast for extreme-value and tail-risk issues.")
    parser.add_argument("--forecast", type=Path, required=True, help="Wide submission-format forecast CSV.")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="Raw historical CSV directory.")
    parser.add_argument("--output", type=Path, help="Optional markdown output path.")
    args = parser.parse_args()

    rows = load_forecast_rows(args.forecast)
    slot_profiles, daily_profiles = load_historical_profiles(args.raw_dir)
    flags = scan_rows(rows, slot_profiles, daily_profiles)
    report = render_report(flags)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
