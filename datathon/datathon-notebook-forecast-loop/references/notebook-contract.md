# Notebook Contract

## Canonical paths

- Code root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Canonical notebook: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/notebooks/05_independent_optimization_loop.ipynb`
- Earlier pipeline notebook: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/notebooks/04_single_pipeline.ipynb`
- Legacy notebook/source material: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notebooks/A.ipynb`
- Raw data for pipeline runs: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/data/raw/`
- Template: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/data/template_forecast_v00.csv`
- Forecast outputs: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/outputs/forecasts/`
- Report outputs: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/outputs/reports/`

## Candidate export expectations

For candidate `vNN` export:

- `outputs/forecasts/forecast_vNN.csv`
- `outputs/reports/forecast_vNN_backtest_rows.csv`
- `outputs/reports/forecast_vNN_summary.md`

## Notebook behavior

- One section for path and config setup
- One section for August 2025 target handling
- One section for loading raw datasets and notes-driven constants
- One section for intraday profile experiments
- One section for candidate parameters
- One section for backtest export
- One section for forecast export
- One section for score, tail-risk, and submission-gate calls

## Do not

- invent a new notebook name for the canonical workflow
- split daily and interval modeling into separate notebooks by default
- keep silent notebook-only logic that cannot be reproduced on the next run
- compare candidates without exporting artifacts
