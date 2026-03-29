---
name: datathon-rolling-stress-backtest
description: "Run walk-forward and stress validation for Team095's Illinois Statistics Datathon workflow. Use when testing `forecast_v08`, comparing June-only or June-weighted profile variants, and checking whether interval-shape gains actually transfer across 2025 windows."
---

# Datathon Rolling Stress Backtest

Use this skill when you need validation discipline, not just another model idea.

## Current mission

- Team: `Team095`
- Target month: August 2025
- Candidate focus: `forecast_v08`
- Priority questions:
  1. Does a June-only or June-heavier profile improve interval shape?
  2. Do abandon-rate multipliers help without creating unstable low-volume slices?
  3. Do tighter CCT bounds and stronger daily blending hold up in walk-forward tests?

## Workspace split

- Implementation root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Use root `src/`, `scripts/`, `outputs/`, and root `notebooks/` for implementation.
- Use `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/*.md` for the current data and rules notes.

## Quick start

1. Keep the modeling loop in one notebook:
   - target notebook: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/notebooks/05_independent_optimization_loop.ipynb`
2. Read the repo context that defines the protocol:
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/data.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/pipeline.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/src/baseline_model.py`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/scripts/generate_v07.py`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/scripts/generate_v08.py`
3. Build or refresh the window plan with `scripts/run_rolling_backtest.py --mode plan`.
4. Have the notebook or script export one row-level comparison CSV across all validation windows.
5. Run `scripts/run_rolling_backtest.py --mode report --comparisons ...` before deciding whether a candidate is better.

## Required slices

- portfolio
- weekday
- daypart
- worst dates
- peak actual workload dates
- low-volume intervals
- underforecast-heavy rows
- overforecast-heavy rows

## Rules

- Do not declare a winner from one holdout slice.
- Do not trust a lower average metric if it gets there by concentrating underforecast damage in peaks.
- Treat interval-level residual analysis as the main validation surface because daily totals are already anchored.
- If a fix helps one portfolio and hurts the others, say that explicitly.
- Prefer keep / reject / targeted retest, not vague optimism.

## Output rules

- Separate plan generation from performance interpretation.
- If the comparison export is missing `portfolio`, `date`, or slot-level fields, say the validation surface is incomplete.
- Call out whether the gain came from volume shape, abandon behavior, or CCT behavior.
- Always end with a keep / reject / needs another targeted test recommendation.

Read `references/backtest-protocol.md` when you need the exact file conventions, window design, or stress-slice definitions.
