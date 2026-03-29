---
name: datathon-notebook-forecast-loop
description: "Run Team095's Illinois Statistics Datathon forecasting workflow through one canonical notebook. Use when consolidating the August 2025 workflow, keeping v08 experimentation in one place, and avoiding the root-vs-1 notebook confusion."
---

# Datathon Notebook Forecast Loop

Use this skill when the main need is disciplined iteration inside one notebook.

## Current mission

- Team: `Team095`
- Competition month: August 2025
- Current candidate: `forecast_v08`
- Do not drift back to a 2026 target month. `target_year` must stay `2025`.

## Workspace split

- Implementation root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Use root `config/`, `src/`, `scripts/`, `outputs/`, and root `notebooks/` for implementation.
- Use `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/*.md` as the current notes set.
- Raw CSVs exist in both `data/raw/` locations; prefer root `data/raw/` when running pipeline code because `config/paths.yaml` points there.

## Canonical notebook

- Main notebook path: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/notebooks/05_independent_optimization_loop.ipynb`
- Earlier pipeline notebook: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/notebooks/04_single_pipeline.ipynb`
- Legacy source notebook: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notebooks/A.ipynb`

Treat `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notebooks/A.ipynb` as source material, not the final workflow surface.

## Core rule

Keep the modeling loop in one notebook. Small helper functions or stable utilities are fine, but do not spread candidate logic across a fragmented multi-file experiment tree.

## Iteration loop

1. State the hypothesis in the notebook.
2. Change one modeling lever at a time.
3. Preserve the v07 fixes before trying anything new:
   - `target_year = 2025`
   - daily totals anchored to August 2025 daily actuals
   - D days 27-31 filled from same-day-of-week averages
   - daypart CCT corrections, caps, and low-volume smoothing
4. Export:
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/outputs/forecasts/forecast_vNN.csv`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/outputs/reports/forecast_vNN_backtest_rows.csv`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/outputs/reports/forecast_vNN_summary.md`
5. Run the companion skills in this order:
   - `datathon-score-lens`
   - `datathon-rolling-stress-backtest`
   - `datathon-tail-risk-guardrails`
   - `datathon-submission-gate`
6. Keep or reject the candidate based on evidence.

## Repo context to load

- `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/overview.md`
- `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/pipeline.md`
- `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/scripts/generate_v07.py`
- `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/scripts/generate_v08.py`
- `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/docs/modeling_plan.md`

Read `references/notebook-contract.md` for file conventions and `assets/main-notebook-outline.md` when scaffolding or refactoring the notebook.

## Output rules

- Keep cells ordered around the end-to-end workflow, not around ad hoc experiments.
- Preserve a clear candidate section for parameters and toggles.
- Do not invent a new notebook name for the main workflow; the root `05_independent_optimization_loop.ipynb` is the canonical notebook.
- Do not create extra notebooks unless the user explicitly asks for a throwaway scratch pad.
