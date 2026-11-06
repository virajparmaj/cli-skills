---
name: v-dataset
description: "Review CSV or Parquet training data for missingness, duplicates, class balance, split overlap, and potential target leakage. Use for dataset readiness audits; reports measured data loss separately from code patterns."
---

# Pre-Training Dataset Audit

Enforce clean, honest training data — explicit missingness, no duplicates, no split overlap, no target leakage — before a single model is fit.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Distinguish measured or traced facts from unresolved hypotheses. Never report an audit scanner hit as proof on its own.

## Quick flow

1. Read repo context if present: `AGENTS.md`, `CLAUDE.md`, `README.md`, `notes/`, and any data dictionary.
2. Profile: `scripts/profile-dataset.py <repo> --target <col>` for nulls, dupes, cardinality, class balance, and the feature-target association ranking.
3. Split overlap: `scripts/profile-dataset.py --train <a> --test <b>` for row-hash leakage between splits.
4. Data-loss ledger: `scripts/find-silent-drops.py <repo>` for every row-affecting operation.
5. Crypto/time-series data: `scripts/funding-grid-check.py <repo> --file <data>` for interval grid, tz, gaps, and annualization constants.
6. Load [references/dataset-playbook.md](references/dataset-playbook.md) for the judgment table and output contract.

## Output rules

- Severity-ranked findings, each labeled **Confirmed from data** (profiler measured it) or **Strongly inferred** (code pattern only).
- Each finding ships the one pandas snippet for its smallest fix.
- Include a data-loss ledger table: `step | file:line | rows in→out (measured/"unmeasured") | verdict`.
- Confirm split overlap against the intended entity/time keys and trace high feature-target association to prediction-time availability. Correlation alone does not establish leakage.
- Report silent data loss with measured row counts or mark its effect unmeasured; distinguish intended exclusions from demonstrated bias or information loss.
- If a dimension is clean, say so. Optionally emit a paste-ready missing-data statement for notes/README.

## Scope boundary

- Where the data came from (source/date/methodology) → `v-provenance`.
- Storage-layer schema drift / timezone rot in DuckDB/Parquet → `v-duckdb-layer`.
- Whether the split *protocol* leaks temporally (shuffle, lookahead windows) → `v-timeseries-leakage`.
- This skill answers: is this data clean and honest enough to train on?

## No data files

If no CSV/Parquet files exist, say so and stop.

See [references/dataset-playbook.md](references/dataset-playbook.md) for the judgment table, ledger format, and full output contract.
