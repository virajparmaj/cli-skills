# Main Notebook Outline

## 1. Run context

- project root detection
- bundle-root notes detection
- raw data paths
- template path
- output directories
- candidate version and parameter cell

## 2. Raw data load

- read the nine competition datasets
- inspect row counts and column presence
- load notes-driven constants
- pin `target_year = 2025`

## 3. Cleaning and rebuild

- daily cleanup
- D portfolio same-day-of-week fill for missing August 27-31 daily anchors
- interval densification to 48 slots
- hierarchical fill
- derive abandoned calls after volume and rate

## 4. Feature and baseline layer

- daily trend features
- interval shape features
- June-only or June-heavier intraday profile experiments
- CCT and abandon stabilization inputs

## 5. Candidate controls

- share-profile mode (`apr-jun`, `june-only`, weighted)
- smoothing knobs
- abandon multiplier vs direct-rate toggle
- CCT blend weight and caps
- tail-risk thresholds

## 6. Backtest loop

- rolling window plan load
- candidate prediction over windows
- export `forecast_vNN_backtest_rows.csv`

## 7. Forecast generation

- August 2025 forecast creation
- exact daily-total anchoring to August 2025 daily actuals
- template alignment
- export `forecast_vNN.csv`

## 8. Validation loop

- run score-lens summary
- run rolling stress report
- run tail-risk scan
- run submission gate

## 9. Decision cell

- keep / reject / revise
- short candidate notes
