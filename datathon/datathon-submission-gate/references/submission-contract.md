# Submission Contract

## Repo anchor

- Code root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Template: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/data/template_forecast_v00.csv`
- Forecast outputs: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/outputs/forecasts/`

## Required format

- Exact header match to `template_forecast_v00.csv`
- Exact row order and key order
- Exactly `1488` rows for August (`31 x 48`)
- Metrics for portfolios `A`, `B`, `C`, `D`

## Required checks

1. template and header match
2. key row match
3. null and numeric parse
4. non-negativity
5. integer call and abandon counts
6. rate bounds
7. zero-volume dependency behavior
8. `abandoned_calls == min(calls, round(calls * rate))`
9. daily totals match August 2025 daily targets
10. daily workload warning scan
11. slot-level tail warning scan

## Submission posture

Fail on the hard contract. Warn on realism risk. Let the user decide whether to submit a warning-only candidate.
