# Tail Risk Rules

## Repo anchor

- Code root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Historical raw data: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/data/raw/`
- Submission template: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/data/template_forecast_v00.csv`

## What counts as risky here

- low or moderate volume paired with extreme CCT
- low-volume intervals with unstable abandon rate
- abandon rates above `0.50`
- abrupt slot-to-slot spikes not supported by neighboring intervals
- portfolio-day workload totals far beyond historical daily behavior
- tails that are concentrated in one portfolio but hidden by overall averages

## Preferred guardrail order

1. Diagnose whether the tail comes from volume, CCT, or rate.
2. Compare against historical portfolio-slot behavior.
3. Use localized smoothing or shrinkage.
4. Recompute abandoned calls after any rate change.
5. Re-run score and submission checks.

## Avoid

- global flattening
- direct abandoned-calls clipping
- fixing every outlier if only one repeated pattern matters
