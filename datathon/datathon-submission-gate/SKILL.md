---
name: datathon-submission-gate
description: "Run the final pre-upload safety gate for Team095's Illinois Statistics Datathon forecast. Use when checking `forecast_v08.csv` for exact template compliance, integer call counts, August 2025 daily-total alignment, and final realism risk before upload."
---

# Datathon Submission Gate

Use this skill as the last stop before upload.

## Current mission

- Team: `Team095`
- Final artifact: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/outputs/forecasts/forecast_v08.csv`
- Hard requirement: the submission still targets August 2025 even though the config file says 2026 by default.

## Workspace split

- Implementation root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Use root `outputs/` and root template path for final artifacts.
- Use `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/*.md` for current rules and overview notes.

## Quick start

1. Read only the repo rules that define the contract:
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/overview.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/rules.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/pipeline.md`
   - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/data/template_forecast_v00.csv`
2. Run `scripts/run_submission_gate.py --forecast ...`.
3. Fail closed on hard violations.
4. Report warnings separately from blockers.

## Hard failures

- wrong columns or column order
- wrong row count or key order
- blank or non-numeric forecast values
- negative outputs
- non-integer `Calls_Offered_*` or `Abandoned_Calls_*`
- abandon rate outside `[0, 1]`
- zero-volume rows with non-zero dependents
- `Abandoned_Calls_*` not equal to `min(calls, round(calls * rate))`
- daily call totals that do not match August 2025 daily targets
- anything other than `1488` rows (`31 x 48`)

## Warnings

- unusually high slot-level CCT, rate, or workload
- unusually high daily workload by portfolio
- abandon rates above `0.50`
- concentrated issues in one portfolio or daypart

## Output rules

- Show exact failing rows and columns when possible.
- Say `safe to submit` only when hard checks pass.
- Do not silently fix a submission in this skill; surface the problem first.

Read `references/submission-contract.md` when you need the repo-specific path defaults or the exact check order.
