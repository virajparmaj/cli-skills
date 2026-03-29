---
name: datathon-tail-risk-guardrails
description: "Control extreme-value and tail-risk behavior for Team095's Illinois Statistics Datathon forecasts. Use when `forecast_v08` shows unsafe CCT, abandon-rate, abandoned-call, or workload spikes, especially in low-volume or overnight intervals."
---

# Datathon Tail Risk Guardrails

Use this skill when the main danger is operational implausibility, not missing one more feature.

## Current mission

- Team: `Team095`
- Candidate focus: `forecast_v08`
- Main tail risks right now:
  1. low-volume abandon spikes after adding interval variation
  2. CCT jumps after stronger daily blending
  3. isolated workload spikes that can erase a volume win

## Workspace split

- Implementation root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Use root `src/`, `scripts/`, and `outputs/` for implementation.
- Use `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/*.md` for the current rules and math notes.

## Quick start

1. Read only the repo context that defines risk:
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/data.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/math.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/rules.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/src/baseline_model.py`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/src/postprocessing.py`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/scripts/generate_v08.py`
2. Scan the candidate forecast with `scripts/scan_tail_risk.py`.
3. Group flags by:
   - portfolio
   - daypart
   - metric type
   - repeated pattern vs one-off anomaly
4. Prefer the smallest guardrail that reduces risk:
   - bounded uplift
   - profile smoothing
   - rate stabilization in low volume
   - CCT shrinkage toward portfolio-slot baseline

## Hard rules

- Underforecast-heavy workload tails are more dangerous than symmetric noise.
- Do not smooth abandoned calls directly; derive them from volume and abandon rate after any guardrail.
- Do not hide a broken forecast with aggressive clipping.
- If a tail is caused by a narrow slice, fix that slice instead of flattening the whole profile.
- Treat abandon rates above `0.50` as high-severity unless there is very strong evidence.

## Output rules

- Show exact flagged rows or recurring patterns.
- Separate submission blockers from watch-list warnings.
- Say whether the risk is likely to affect Volume Score, Workload Penalty, or only realism.

Read `references/tail-risk-rules.md` when you need the repo-specific thresholds, default paths, or preferred guardrail order.
