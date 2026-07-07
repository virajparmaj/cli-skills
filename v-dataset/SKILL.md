---
name: v-dataset
description: "Pre-training dataset audit: missingness, duplicates, class imbalance, split overlap, and target leakage, plus a data-loss ledger and crypto time-series checks. Use at the start of any ML project on CSV/Parquet data (funding-rate, macro-regime, credit-risk) to enforce handle-missing-data-explicitly and no-rows-shared-across-splits. Key capabilities: profile per-column null rates, dtype anomalies, exact-duplicate rows, near-constant and id-like columns, class balance, and a feature-target association ranking that flags ~1.0 columns as candidate target leakage; sha1 row-hash overlap between train/test files; a data-loss ledger of every dropna/fillna/coerce/inner-merge/resample site with biasing operations called out; and a crypto extension checking funding-interval grid and timezone alignment. Trigger phrases: audit this dataset before training, check for leakage between my splits, profile the training data, is this data clean enough to train on, where am I silently dropping rows, check the 8h funding grid."
---

# Pre-Training Dataset Audit

Enforce clean, honest training data — explicit missingness, no duplicates, no split overlap, no target leakage — before a single model is fit.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Quick flow

1. Read repo context if present: `CLAUDE.md`, `README.md`, `notes/`, and any data dictionary.
2. Profile: `scripts/profile-dataset.py <repo> --target <col>` for nulls, dupes, cardinality, class balance, and the feature-target association ranking.
3. Split overlap: `scripts/profile-dataset.py --train <a> --test <b>` for row-hash leakage between splits.
4. Data-loss ledger: `scripts/find-silent-drops.py <repo>` for every row-affecting operation.
5. Crypto/time-series data: `scripts/funding-grid-check.py <repo> --file <data>` for interval grid, tz, gaps, and annualization constants.
6. Load [references/dataset-playbook.md](references/dataset-playbook.md) for the judgment table and output contract.

## Output rules

- Severity-ranked findings, each labeled **Confirmed from data** (profiler measured it) or **Strongly inferred** (code pattern only).
- Each finding ships the one pandas snippet for its smallest fix.
- Include a data-loss ledger table: `step | file:line | rows in→out (measured/"unmeasured") | verdict`.
- Split-overlap leakage and ~1.0 feature-target association are P0/P1 by default.
- Missing data that is silently dropped violates Veer's explicit-handling rule — always flag it.
- If a dimension is clean, say so. Optionally emit a paste-ready missing-data statement for notes/README.

## Scope boundary

- Where the data came from (source/date/methodology) → `v-provenance`.
- Storage-layer schema drift / timezone rot in DuckDB/Parquet → `v-duckdb-layer`.
- Whether the split *protocol* leaks temporally (shuffle, lookahead windows) → `v-timeseries-leakage`.
- This skill answers: is this data clean and honest enough to train on?

## No data files

If no CSV/Parquet files exist, say so and stop.

See [references/dataset-playbook.md](references/dataset-playbook.md) for the judgment table, ledger format, and full output contract.
