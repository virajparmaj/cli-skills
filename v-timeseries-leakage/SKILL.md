---
name: v-timeseries-leakage
description: "Find temporal and statistical leakage in ML pipelines before the model looks suspiciously good, issuing a LEAKING/CLEAN/UNVERIFIED verdict per pipeline. Use for time-series and forecasting repos (funding-rate, macro-regime) and any sklearn/xgboost/statsmodels project where CV scores seem too good or the model dies out of sample. Key capabilities: AST-scan .py and .ipynb for shuffle defaults on datetime data, KFold vs TimeSeriesSplit, scaler/imputer/encoder fit before the split (fit-on-full-data contamination), forward-reaching windows (shift(-n), centered rolling, cross-boundary resample), missing stationarity checks, and statsmodels regime traps (smoothed vs filtered probabilities, macro publication-lag joins). Emits per-file facts, high-signal flags, and smallest fixes. Trigger phrases: check for leakage, is my train/test split valid for time series, why is my model too good, audit the forecasting pipeline, review walk-forward validation, review the regime model, are my macro lags aligned."
---

# Time-Series Leakage Audit

Catch the leakage that makes in-sample numbers lie — fit-before-split contamination, temporal lookahead, and statsmodels regime traps — with a clear verdict per pipeline.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Quick flow

1. Read repo context if present: `CLAUDE.md`, `README.md`, `notes/`, and any modeling notebooks or `src/` training code.
2. Run `scripts/find-split-leakage.py <repo>` for deterministic facts: split calls and their `shuffle`, CV type, `.fit`/`.fit_transform` lines relative to the split, forward-reaching windows, regime signatures, and stationarity-check presence.
3. Load [references/leakage-playbook.md](references/leakage-playbook.md) for the three leakage classes, the verdict rules, and the output contract.
4. Trace each flagged line in context, decide the per-pipeline verdict, and write the findings.

## Output rules

- Give each pipeline one verdict: **LEAKING** / **CLEAN** / **UNVERIFIED**.
- Then severity-ranked findings: `file:line | class | what leaks | smallest fix`.
- Label **Confirmed from code** (data flow traced) vs **Strongly inferred** (flag only).
- Smallest fixes are one-liners where possible (`shuffle=False`, move `.fit()` inside a Pipeline, `TimeSeriesSplit`, filtered instead of smoothed probabilities, add a release-lag column).
- Include one corrected split/pipeline snippet where the fix is non-trivial.
- If a pipeline is clean, say so — do not manufacture leakage.

## Scope boundary

- Data cleanliness (nulls, dupes, imbalance) → `v-dataset`.
- Metric math correctness → `v-metric-math`.
- Regression inference validity (p-values, robust SEs, VIF) → `v-regression-diagnostics`.
- Serving/inference skew → `v-ml` / `v-ml-deploy`.
- This skill answers only: does information from the future or the test set leak into training?

## No pipelines found

If no split/preprocessing/CV call sites exist, say so and stop.

See [references/leakage-playbook.md](references/leakage-playbook.md) for the leakage classes, verdict rules, and full output contract.
