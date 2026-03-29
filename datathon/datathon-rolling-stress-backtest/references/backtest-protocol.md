# Backtest Protocol

## Repo anchor

- Code root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Canonical notebook: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/notebooks/05_independent_optimization_loop.ipynb`
- Raw interval files: `data/raw/A___Interval.csv` through `data/raw/D___Interval.csv`
- Raw daily files: `data/raw/A___Daily.csv` through `data/raw/D___Daily.csv`

## Validation stance for v08

- Score month is August 2025.
- Daily totals are already anchored, so the main question is interval-shape transfer.
- Compare June-only, June-heavier, and baseline share profiles on the exact same windows.
- Treat abandon-rate variation and tighter CCT blending as secondary levers that must prove they help, not just look plausible.

## Window design

- Build windows from the 2025 interval history.
- Prefer 28 training days, 7 evaluation days, 7 day step.
- Use dates common to all four portfolios when ranking candidates.
- Keep all variants on the exact same window plan.

## Notebook export contract

Export a single comparison CSV with:

- `window_id`
- `portfolio`
- `date`
- `slot_index`
- `forecast_calls_offered`
- `actual_calls_offered`
- `forecast_cct`
- `actual_cct`
- `forecast_abandoned_rate`
- `actual_abandoned_rate`

Optional columns:

- `candidate`
- `interval_label`
- `forecast_abandoned_calls`
- `actual_abandoned_calls`

## Stress slices to always inspect

- worst windows by workload penalty
- worst portfolios
- worst weekdays
- worst dayparts
- worst dates
- top-decile actual workload rows
- low-volume rows
- underforecast rows
- overforecast rows
