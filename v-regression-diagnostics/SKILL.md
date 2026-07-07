---
name: v-regression-diagnostics
description: "Audit whether regression and hypothesis-test inference is statistically valid — are the p-values, standard errors, and confidence intervals trustworthy. Use for statsmodels/scipy analysis in notebooks and scripts (Macroeconomic-Regime-Analysis-Credit-Risk, Meals-Academic-Outcomes) where results are read off summary() output. Key capabilities: inventory every OLS/GLM/Logit fit and t-test/Mann-Whitney/chi2 test with its cov_type, flag classical SEs on heteroskedastic or autocorrelated data (time series needs HAC/Newey-West), detect missing diagnostics (Breusch-Pagan, Durbin-Watson, VIF, Jarque-Bera), multicollinearity among regressors, wrong-test-for-the-data choices, and p-hacking smells (many fits, few reported). Emits severity-ranked findings with one-line fixes like cov_type='HC3' or 'HAC' and a missing-diagnostics checklist per model. Trigger phrases: audit my regressions, are these p-values trustworthy, check the stats in this notebook, review regression diagnostics, do I need robust standard errors."
---

# Regression Diagnostics Audit

Check that the inference itself is valid — robust SEs, run diagnostics, honest p-values — not just that the model fits.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

<!-- skill-operating-standard -->
## Operating standard — run at maximum capability

Run this skill in your highest-effort mode, whatever model you are. Prefer correctness and completeness over speed or brevity; if you support extended thinking or an adjustable reasoning effort, raise it for this work. Do not guess when you can verify.

- **Think first.** Before acting, plan: what the skill must produce, which files or scripts give ground truth, and where the likely failure modes are. Reason step by step internally before writing the answer.
- **Facts before judgment.** Run this skill's `scripts/` first (when it has them) and treat their output as the only ground truth. Never invent file paths, line numbers, metrics, or data a script did not produce. If a script cannot run, say so and mark every dependent conclusion UNVERIFIED.
- **Evidence discipline.** Label every claim `Confirmed from code` (you read the exact file:line and traced the logic), `Strongly inferred` (a pattern implies it but a runtime path could exonerate it), or `Not found — fill in manually`. A scanner/grep hit is not a finding until you open the file and confirm it in context.
- **Adversarial self-check.** After a first draft, run a second pass whose only job is to refute each finding: what input, config, or code path would make it false? Drop or downgrade anything you cannot defend. For subtle calls (leakage, statistics, security, correctness, money) reason from at least two independent angles before asserting.
- **Exhaust the search.** For discovery, keep going until two consecutive passes surface nothing new; do not stop at the first plausible batch. Never silently cap coverage — state what you skipped and why.
- **Use every tool you have.** When a capability (code execution, file read, web or docs lookup, subagents, parallel calls) is available and would raise accuracy, use it instead of answering from memory or a single pass.
- **Honesty.** If a category is clean, say so; do not pad with generic best-practice filler that has no evidence in this repo. State assumptions, gaps, and anything unverified plainly.
- **Contract.** Follow this skill's output contract exactly — strict format, severity ranks, verdict labels, smallest viable fix. For generator skills, every emitted value must trace to a computed fact or a cited line; label anything else inferred.

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
