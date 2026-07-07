---
name: v-regression-diagnostics
description: "Audit whether regression and hypothesis-test inference is statistically valid — are the p-values, standard errors, and confidence intervals trustworthy. Use for statsmodels/scipy analysis in notebooks and scripts (Macroeconomic-Regime-Analysis-Credit-Risk, Meals-Academic-Outcomes) where results are read off summary() output. Key capabilities: inventory every OLS/GLM/Logit fit and t-test/Mann-Whitney/chi2 test with its cov_type, flag classical SEs on heteroskedastic or autocorrelated data (time series needs HAC/Newey-West), detect missing diagnostics (Breusch-Pagan, Durbin-Watson, VIF, Jarque-Bera), multicollinearity among regressors, wrong-test-for-the-data choices, and p-hacking smells (many fits, few reported). Emits severity-ranked findings with one-line fixes like cov_type='HC3' or 'HAC' and a missing-diagnostics checklist per model. Trigger phrases: audit my regressions, are these p-values trustworthy, check the stats in this notebook, review regression diagnostics, do I need robust standard errors."
---

# Regression Diagnostics Audit

Check that the inference itself is valid — robust SEs, run diagnostics, honest p-values — not just that the model fits.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Quick flow

1. Read repo context if present: `CLAUDE.md`, `README.md`, `notes/`, and the analysis notebooks.
2. Run `scripts/inventory-model-fits.py <repo>` for deterministic facts: model types, `cov_type`, hypothesis tests, diagnostics present/missing, time-series signal, and a fit-vs-report p-hacking proxy.
3. Load [references/diagnostics-playbook.md](references/diagnostics-playbook.md) for the diagnostic checklist and output contract.
4. Judge each model and write the findings.

## Output rules

- Severity-ranked findings table: `model @ file:line | validity threat | evidence | smallest fix`.
- Label **Confirmed from code** (fit and cov_type/missing-diagnostic read) vs **Strongly inferred** (grep signal only).
- Fixes are one-liners where possible (`cov_type='HC3'`, `cov_type='HAC'` with `maxlags`, add VIF, switch to a non-parametric test).
- Include a missing-diagnostics checklist per model.
- Time-series regressions without HAC/Newey-West SEs are High by default; p-hacking smells (many fits, few reported) are flagged with the count evidence.
- If the inference is sound, say so — do not invent statistical problems.

## Scope boundary

- Metric math correctness (Sharpe, VaR, AUC) → `v-metric-math`.
- Train/test leakage and regime *feature* leakage → `v-timeseries-leakage`.
- Serving/inference reliability → `v-ml` / `v-ml-deploy`.
- This skill answers only: are the reported statistical results valid?

## No models found

If no statsmodels/scipy fits or hypothesis tests exist, say so and stop.

See [references/diagnostics-playbook.md](references/diagnostics-playbook.md) for the diagnostic checklist and full output contract.
