---
name: v-timeseries-leakage
description: "Review forecasting pipelines for temporal lookahead, test-set contamination, publication lags, and regime-probability leakage. Use for split and preprocessing audits; report LEAKING, CLEAN, or UNVERIFIED per pipeline."
---

# Time-Series Leakage Audit

Catch the leakage that makes in-sample numbers lie — fit-before-split contamination, temporal lookahead, and statsmodels regime traps — with a clear verdict per pipeline.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Distinguish measured or traced facts from unresolved hypotheses. Never report an audit scanner hit as proof on its own.

## Quick flow

1. Read repo context if present: `AGENTS.md`, `CLAUDE.md`, `README.md`, `notes/`, and any modeling notebooks or `src/` training code.
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
- Serving/inference skew → `v-ml`.
- This skill answers only: does information from the future or the test set leak into training?

## No pipelines found

If no split/preprocessing/CV call sites exist, say so and stop.

See [references/leakage-playbook.md](references/leakage-playbook.md) for the leakage classes, verdict rules, and full output contract.
