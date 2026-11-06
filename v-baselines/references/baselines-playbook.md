# Honest Baseline Harness Playbook

The cheapest form of "validate against a known benchmark": before trusting a
tuned XGBoost, prove it beats a dummy and a linear model under one fair CV
protocol.

## The shared comparison protocol

- One splitter shared by every model, one seed (42).
- Classification → `StratifiedKFold(shuffle, seed)`; regression → `KFold`;
  datetime index → `TimeSeriesSplit` (auto-selected, or forced with
  `--datetime-col`).
- Every model wrapped in a `Pipeline` (median imputer inside CV for every model; scaler inside CV for linear models) so no
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

One CV standard deviation is a descriptive heuristic, not a hypothesis test or proof of no signal. Interpret the result only for the supplied rows and split protocol.

- **Best == dummy** → none of the evaluated models improved the observed mean under this protocol; this alone does not prove the features have no signal.
- **Best beats dummy by ≤ one CV std** → the observed lift is small relative to fold variation; this does not establish statistical significance or prove noise.
- **Best (forest/xgboost) does not improve on linear** → consider the simpler model, subject to task and deployment requirements.
- **Best beats dummy by > CV std and beats linear** → the nonlinear model earns
  further evaluation of its complexity; cross-validation alone is not release approval.

## Output contract

- One markdown table: `model | metric mean ± std | fit time`.
- One-paragraph verdict using the rules above — always compared against dummy and
  linear, never a bare "XGBoost got 0.84".
- If `experiments/runs.csv` exists, append one row per baseline so the comparison
  persists (pairs with `v-run-ledger`).

## Not this skill's job

- Data cleanliness before the run → `v-dataset`.
- Whether the CV protocol itself leaks (the harness still requires task-appropriate time, group, and horizon settings) → `v-timeseries-leakage`.
- Durable run tracking + model cards → `v-run-ledger`.

## Explicit protocol controls

Use `--task regression` for integer-valued regression targets or `--task classification` when automatic inference is ambiguous. For overlapping forecast labels, choose an evidence-based `--gap N` matching the horizon; the harness cannot infer label availability from the CSV. TimeSeriesSplit assumes observations are equally spaced for comparable fold durations; inspect the timestamp grid first. [Official cross-validation guidance](https://scikit-learn.org/stable/modules/cross_validation.html).
