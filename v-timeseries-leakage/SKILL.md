---
name: v-timeseries-leakage
description: "Find temporal and statistical leakage in ML pipelines before the model looks suspiciously good, issuing a LEAKING/CLEAN/UNVERIFIED verdict per pipeline. Use for time-series and forecasting repos (funding-rate, macro-regime) and any sklearn/xgboost/statsmodels project where CV scores seem too good or the model dies out of sample. Key capabilities: AST-scan .py and .ipynb for shuffle defaults on datetime data, KFold vs TimeSeriesSplit, scaler/imputer/encoder fit before the split (fit-on-full-data contamination), forward-reaching windows (shift(-n), centered rolling, cross-boundary resample), missing stationarity checks, and statsmodels regime traps (smoothed vs filtered probabilities, macro publication-lag joins). Emits per-file facts, high-signal flags, and smallest fixes. Trigger phrases: check for leakage, is my train/test split valid for time series, why is my model too good, audit the forecasting pipeline, review walk-forward validation, review the regime model, are my macro lags aligned."
---

# Time-Series Leakage Audit

Catch the leakage that makes in-sample numbers lie — fit-before-split contamination, temporal lookahead, and statsmodels regime traps — with a clear verdict per pipeline.

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
