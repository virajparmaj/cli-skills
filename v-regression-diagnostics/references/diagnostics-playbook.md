# Regression Diagnostics Playbook

Audits whether the *inference* is valid — are the p-values and confidence
intervals trustworthy — not whether the model predicts well.

## What the script gathers

`scripts/inventory-model-fits.py <repo>` lists every statsmodels/scipy fit and
test with: model type, `cov_type` (robust vs classical SEs), which diagnostics
appear in the file, hypothesis tests used, whether the code looks like time
series, and a fit-count-vs-reported-summary proxy for p-hacking.

## Diagnostic checklist per model

| Issue | Symptom / signal | Smallest fix |
|---|---|---|
| Heteroskedasticity | no Breusch-Pagan/White; classical SEs on cross-section | `cov_type='HC3'` |
| Autocorrelation | time-series data, no Durbin-Watson, classical SEs | `cov_type='HAC', cov_kwds={'maxlags': L}` (Newey-West) |
| Multicollinearity | many correlated macro regressors, no VIF | drop/combine regressors; report VIF |
| Non-normal residuals | inference on small n, no Jarque-Bera | check residuals; bootstrap or robust inference |
| Wrong test for data | t-test on non-normal/ordinal; parametric on tiny n | Mann-Whitney/Wilcoxon; exact tests |
| p-hacking | 30 fits in the notebook, 2 significant in the writeup | pre-register, correct for multiple comparisons (Bonferroni/BH) |
| Look-ahead in features | regressor uses contemporaneous unreleased data | align to release date |

## Flow

1. Run the inventory script.
2. For each model, judge: is the SE type appropriate for the data (cross-section
   vs time series)? Are the required diagnostics run? Is the reported result a
   cherry-pick of many fits?
3. Report findings with file:line, the specific validity threat, and the
   one-line fix.

## Output contract

- Severity-ranked findings table: `model @ file:line | validity threat | evidence
  | smallest fix`.
- Label **Confirmed from code** (you read the fit and its cov_type / missing
  diagnostic) vs **Strongly inferred** (grep signal only).
- A missing-diagnostics checklist per model (which of Breusch-Pagan /
  Durbin-Watson / VIF / Jarque-Bera are absent).
- Time-series regressions without HAC/Newey-West SEs are High by default.
- If the inference is sound, say so — do not invent statistical problems.

## Not this skill's job

- Whether the metric math (Sharpe, AUC) is right → `v-metric-math`.
- Whether the train/test split leaks → `v-timeseries-leakage`.
- Regime-model *feature* leakage (smoothed vs filtered probs) → `v-timeseries-leakage`
  (its regime section). This skill covers inference validity of the fits.
