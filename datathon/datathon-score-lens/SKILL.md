---
name: datathon-score-lens
description: "Decompose Team095 forecast candidates for the Illinois Statistics Datathon. Use when comparing `forecast_v07` vs `forecast_v08`, isolating August 2025 interval-shape misses, and prioritizing Volume Score and workload fixes before CCT churn."
---

# Datathon Score Lens

Use this skill when the job is diagnosis, ranking, or next-step selection.

## Current mission

- Team: `Team095`
- Competition month: August 2025
- Current standing: rank `29 / 72`
- Improvement order:
  1. intraday volume distribution
  2. interval-level abandon variation
  3. CCT refinements that preserve workload realism

## Workspace split

- Implementation root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Use root `config/`, `src/`, `scripts/`, and `outputs/` for implementation.
- Use `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/*.md` for the current notes set.
- Raw CSVs are duplicated in both `data/raw/` locations; prefer root `data/raw/` when running code.

## Quick start

1. Read only the repo context that changes the diagnosis:
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/math.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/rules.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/src/local_scoring.py`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/config/project_config.yaml`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/scripts/generate_v07.py`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/scripts/generate_v08.py`
2. Prefer a row-level comparison CSV with one row per `portfolio x date x slot`.
3. Run `scripts/decompose_score.py` before recommending model changes.
4. Report findings in this order:
   - where interval-shape volume error is concentrated
   - where workload penalty is concentrated
   - underforecast vs overforecast split
   - abandon behavior
   - only then CCT behavior
5. Recommend the smallest next change that targets the dominant slice.

## What to look for right now

- Daily totals already match August 2025 actuals, so the remaining volume gap is mostly intraday distribution.
- Check whether the largest residuals cluster in morning, afternoon, or evening blocks.
- Compare v07 share profiles against June-only or June-heavier variants before touching global volume logic.
- Separate verified findings from hypotheses.

## Input expectations

Best input is a CSV with the columns already used by `src/local_scoring.py`:

- `portfolio`
- `date`
- `slot_index`
- `forecast_calls_offered`
- `actual_calls_offered`
- `forecast_cct`
- `actual_cct`
- `forecast_abandoned_rate`
- `actual_abandoned_rate`

Optional columns such as `window_id`, `candidate`, or `interval_label` are welcome.

## Output rules

- Keep the answer evidence-first and repo-specific.
- Treat Volume Score and Workload Penalty as the primary decision surface.
- Explicitly say whether the main issue is:
  - interval shape miss
  - workload amplification from CCT
  - abandon instability
  - a narrow portfolio or date slice
- If only aggregate metrics exist, say that the diagnosis is weak and ask for or create row-level exports from the main notebook.

Read `references/score-priority.md` when you need segment definitions, repo path conventions, or the exact decision order for this competition.
