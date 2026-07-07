# Honest Baseline Harness Playbook

The cheapest form of "validate against a known benchmark": before trusting a
tuned XGBoost, prove it beats a dummy and a linear model under one fair CV
protocol.

## The protocol (fixed, so comparisons are honest)

- One splitter shared by every model, one seed (42).
- Classification → `StratifiedKFold(shuffle, seed)`; regression → `KFold`;
  datetime index → `TimeSeriesSplit` (auto-selected, or forced with
  `--datetime-col`).
- Every model wrapped in a `Pipeline` (scaler inside CV for linear models) so no
  preprocessing leaks across folds.
- Metric: binary → `roc_auc`; multiclass → `accuracy`; regression → `r2`.

## The zoo

`dummy` (most-frequent / mean) → `linear` (LogisticRegression / Ridge) →
`forest` (RandomForest) → `xgboost` (if installed). The dummy is the floor; the
linear model is the "do you even need a nonlinear model" check.

## Run it

```bash
scripts/run-baselines.py data/train.parquet target_col            # auto CV
scripts/run-baselines.py data/train.csv label --datetime-col ts   # walk-forward
scripts/run-baselines.py data/train.csv label --repo .            # append to ledger
```

## Reading the verdict

- **Best == dummy** → features carry no signal under this CV; stop tuning.
- **Best beats dummy by ≤ one CV std** → not a convincing win; the lift is noise.
- **Best (forest/xgboost) doesn't beat linear** → ship the simpler model.
- **Best beats dummy by > CV std and beats linear** → the nonlinear model earns
  its complexity.

## Output contract

- One markdown table: `model | metric mean ± std | fit time`.
- One-paragraph verdict using the rules above — always compared against dummy and
  linear, never a bare "XGBoost got 0.84".
- If `experiments/runs.csv` exists, append one row per baseline so the comparison
  persists (pairs with `v-run-ledger`).

## Not this skill's job

- Data cleanliness before the run → `v-dataset`.
- Whether the CV protocol itself leaks (this harness uses a safe one, but the
  user's own code may not) → `v-timeseries-leakage`.
- Durable run tracking + model cards → `v-run-ledger`.
