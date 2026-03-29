#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable


SKILL_ROOT = Path(__file__).resolve().parents[2]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from shared_paths import resolve_datathon_paths


PATHS = resolve_datathon_paths()
DEFAULT_INPUT = PATHS["reports_dir"] / "backtest_rows.csv"
WEIGHTS = {"E_V": 0.35, "E_C": 0.25, "E_B": 0.15, "P_t": 0.25}
REQUIRED_COLUMNS = {
    "portfolio",
    "date",
    "forecast_calls_offered",
    "actual_calls_offered",
    "forecast_cct",
    "actual_cct",
    "forecast_abandoned_rate",
    "actual_abandoned_rate",
}


def safe_float(value: str | float | int) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    return float(text)


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.strip())


def slot_index_from_row(row: dict[str, str]) -> int:
    if str(row.get("slot_index", "")).strip():
        return int(float(row["slot_index"]))
    label = row.get("interval_label") or row.get("Interval") or ""
    if not label:
        return -1
    hours, minutes = label.strip().split(":")[:2]
    return int(hours) * 2 + (1 if int(minutes) >= 30 else 0)


def daypart(slot_index: int) -> str:
    if slot_index < 0:
        return "unknown"
    if slot_index <= 11:
        return "overnight"
    if slot_index <= 23:
        return "morning"
    if slot_index <= 35:
        return "afternoon"
    return "evening"


def load_rows(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        rows: list[dict[str, object]] = []
        for raw in reader:
            record_date = parse_date(str(raw["date"]))
            slot = slot_index_from_row(raw)
            record = {
                "portfolio": str(raw["portfolio"]).strip(),
                "date": record_date.date().isoformat(),
                "weekday": record_date.strftime("%a"),
                "slot_index": slot,
                "daypart": daypart(slot),
                "forecast_calls_offered": safe_float(raw["forecast_calls_offered"]),
                "actual_calls_offered": safe_float(raw["actual_calls_offered"]),
                "forecast_cct": safe_float(raw["forecast_cct"]),
                "actual_cct": safe_float(raw["actual_cct"]),
                "forecast_abandoned_rate": safe_float(raw["forecast_abandoned_rate"]),
                "actual_abandoned_rate": safe_float(raw["actual_abandoned_rate"]),
            }
            rows.append(record)
    return rows


def summarize(rows: Iterable[dict[str, object]], alpha: float, beta: float) -> dict[str, float]:
    ev_num = 0.0
    ev_den = 0.0
    ec_num = 0.0
    ec_den = 0.0
    eb_num = 0.0
    eb_den = 0.0
    pt_num = 0.0
    pt_den = 0.0
    under_num = 0.0
    over_num = 0.0
    count = 0

    for row in rows:
        count += 1
        actual_calls = float(row["actual_calls_offered"])
        forecast_calls = float(row["forecast_calls_offered"])
        actual_cct = float(row["actual_cct"])
        forecast_cct = float(row["forecast_cct"])
        actual_rate = float(row["actual_abandoned_rate"])
        forecast_rate = float(row["forecast_abandoned_rate"])

        ev_num += abs(actual_calls - forecast_calls)
        ev_den += abs(actual_calls)
        ec_num += abs(actual_cct - forecast_cct) * actual_calls
        ec_den += actual_calls
        eb_num += abs(actual_rate - forecast_rate)
        eb_den += 1.0

        actual_workload = actual_calls * actual_cct
        forecast_workload = forecast_calls * forecast_cct
        pt_den += actual_workload
        if actual_workload >= forecast_workload:
            penalty = alpha * (actual_workload - forecast_workload)
            under_num += penalty
        else:
            penalty = beta * (forecast_workload - actual_workload)
            over_num += penalty
        pt_num += penalty

    e_v = ev_num / ev_den if ev_den else 0.0
    e_c = ec_num / ec_den if ec_den else 0.0
    e_b = eb_num / eb_den if eb_den else 0.0
    p_t = pt_num / pt_den if pt_den else 0.0
    composite = (
        WEIGHTS["E_V"] * e_v
        + WEIGHTS["E_C"] * e_c
        + WEIGHTS["E_B"] * e_b
        + WEIGHTS["P_t"] * p_t
    )
    return {
        "rows": count,
        "E_V": e_v,
        "E_C": e_c,
        "E_B": e_b,
        "P_t": p_t,
        "composite": composite,
        "under_penalty_share": under_num / pt_num if pt_num else 0.0,
        "over_penalty_share": over_num / pt_num if pt_num else 0.0,
    }


def top_group_metrics(
    rows: list[dict[str, object]],
    key_name: str,
    alpha: float,
    beta: float,
) -> list[tuple[str, dict[str, float]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key_name])].append(row)
    ranked: list[tuple[str, dict[str, float]]] = []
    for group_key, group_rows in grouped.items():
        ranked.append((group_key, summarize(group_rows, alpha, beta)))
    ranked.sort(key=lambda item: item[1]["composite"], reverse=True)
    return ranked


def render_markdown(rows: list[dict[str, object]], alpha: float, beta: float, top_n: int) -> str:
    overall = summarize(rows, alpha, beta)
    by_portfolio = top_group_metrics(rows, "portfolio", alpha, beta)
    by_weekday = top_group_metrics(rows, "weekday", alpha, beta)
    by_daypart = top_group_metrics(rows, "daypart", alpha, beta)
    by_date = top_group_metrics(rows, "date", alpha, beta)

    lines = [
        "# Score Decomposition",
        "",
        f"- Rows: {int(overall['rows'])}",
        f"- Composite: {overall['composite']:.6f}",
        f"- E_V: {overall['E_V']:.6f}",
        f"- P_t: {overall['P_t']:.6f}",
        f"- E_C: {overall['E_C']:.6f}",
        f"- E_B: {overall['E_B']:.6f}",
        (
            f"- Workload penalty split: under={overall['under_penalty_share']:.2%}, "
            f"over={overall['over_penalty_share']:.2%}"
        ),
        "",
        "## Worst portfolios",
    ]
    lines.extend(
        (
            f"- {name}: composite={metrics['composite']:.6f}, "
            f"E_V={metrics['E_V']:.6f}, P_t={metrics['P_t']:.6f}, "
            f"under_share={metrics['under_penalty_share']:.2%}"
        )
        for name, metrics in by_portfolio[:top_n]
    )
    lines.extend(["", "## Worst weekdays"])
    lines.extend(
        f"- {name}: composite={metrics['composite']:.6f}, E_V={metrics['E_V']:.6f}, P_t={metrics['P_t']:.6f}"
        for name, metrics in by_weekday[:top_n]
    )
    lines.extend(["", "## Worst dayparts"])
    lines.extend(
        f"- {name}: composite={metrics['composite']:.6f}, E_V={metrics['E_V']:.6f}, P_t={metrics['P_t']:.6f}"
        for name, metrics in by_daypart[:top_n]
    )
    lines.extend(["", "## Worst dates"])
    lines.extend(
        (
            f"- {name}: composite={metrics['composite']:.6f}, E_V={metrics['E_V']:.6f}, "
            f"P_t={metrics['P_t']:.6f}, under_share={metrics['under_penalty_share']:.2%}"
        )
        for name, metrics in by_date[:top_n]
    )
    lines.extend(
        [
            "",
            "## Interpretation cues",
            "- If E_V and P_t rise together after daily totals have been anchored, the remaining issue is usually interval shape.",
            "- If P_t is under-heavy while E_V is moderate, test a targeted daypart or portfolio uplift before global changes.",
            "- If abandon error moves without helping volume or workload, keep it small and local.",
            "- If E_C is large but P_t is stable, avoid broad CCT churn unless walk-forward transfer supports it.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Decompose datathon score drivers from a row-level comparison CSV.")
    parser.add_argument("--comparisons", type=Path, default=DEFAULT_INPUT, help="Row-level comparison CSV.")
    parser.add_argument("--alpha", type=float, default=2.0, help="Underforecast workload penalty weight.")
    parser.add_argument("--beta", type=float, default=1.0, help="Overforecast workload penalty weight.")
    parser.add_argument("--top-n", type=int, default=5, help="Number of worst groups to show.")
    parser.add_argument("--output", type=Path, help="Optional markdown output path.")
    args = parser.parse_args()

    if not args.comparisons.exists():
        raise SystemExit(f"Comparison file not found: {args.comparisons}")

    rows = load_rows(args.comparisons)
    if not rows:
        raise SystemExit("Comparison file has no rows.")

    report = render_markdown(rows, args.alpha, args.beta, args.top_n)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
