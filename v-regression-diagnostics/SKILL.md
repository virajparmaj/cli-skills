---
name: v-regression-diagnostics
description: "Review regression and hypothesis-test inference for justified standard errors, model assumptions, and multiple-testing risks. Use for statistical validity audits of statsmodels/scipy analyses, rather than prediction accuracy."
---

# Regression Diagnostics Audit

Check that the inference itself is valid — robust SEs, run diagnostics, honest p-values — not just that the model fits.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Distinguish measured or traced facts from unresolved hypotheses. Never report an audit scanner hit as proof on its own.

## Quick flow

1. Read repo context if present: `AGENTS.md`, `CLAUDE.md`, `README.md`, `notes/`, and the analysis notebooks.
2. Run `scripts/inventory-model-fits.py <repo>` for deterministic facts: model types, `cov_type`, hypothesis tests, diagnostics present/missing, time-series signal, and a fit-vs-report p-hacking proxy.
3. Load [references/diagnostics-playbook.md](references/diagnostics-playbook.md) for the diagnostic checklist and output contract.
4. Judge each model and write the findings.

## Output rules

- Severity-ranked findings table: `model @ file:line | validity threat | evidence | smallest fix`.
- Label **Confirmed from code** (fit and cov_type/missing-diagnostic read) vs **Strongly inferred** (grep signal only).
- Fixes are one-liners where possible (`cov_type='HC3'`, `cov_type='HAC'` with `maxlags`, add VIF, switch to a non-parametric test).
- Include a missing-diagnostics checklist per model.
- Classical standard errors require justified assumptions; temporal inputs alone do not prove residual autocorrelation. Show the covariance choice and diagnostic evidence. Many fits with few reported results are a selection-risk lead, not proof of p-hacking.
- If the inference is sound, say so — do not invent statistical problems.

## Scope boundary

- Metric math correctness (Sharpe, VaR, AUC) → `v-metric-math`.
- Train/test leakage and regime *feature* leakage → `v-timeseries-leakage`.
- Serving/inference reliability → `v-ml`.
- This skill answers only: are the reported statistical results valid?

## No models found

If no statsmodels/scipy fits or hypothesis tests exist, say so and stop.

See [references/diagnostics-playbook.md](references/diagnostics-playbook.md) for the diagnostic checklist and full output contract.
