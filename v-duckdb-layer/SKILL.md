---
name: v-duckdb-layer
description: "Review DuckDB and Parquet storage for schema drift, timestamp semantics, duplicate keys, and ingest idempotency. Use for storage/query correctness audits; requires inspecting the actual data and writer paths."
---

# DuckDB / Parquet Data-Layer Audit

Catch the cross-phase data-layer bugs — schema drift, naive timestamps, duplicate keys, non-idempotent ingest — before a downstream backtest silently trusts them.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Distinguish measured or traced facts from unresolved hypotheses. Never report an audit scanner hit as proof on its own.

## Quick flow

1. Read repo context first if present: `AGENTS.md`, `CLAUDE.md`, `notes/03_architecture.md`, `notes/11_known_issues.md`, and any phase docs describing the data layer.
2. Run `scripts/parquet-facts.py <repo>` to gather per-file schema fingerprints, timestamp metadata, min/max dates, duplicate-key counts, row-group sizes, and file hashes. A hash is a snapshot, not proof of ingest idempotency.
3. Read the code the facts flag — connectors/writers for tz and dedup, query/scan sites for `SELECT *`, missing `ORDER BY`, and string-typed dates.
4. Load [references/audit-playbook.md](references/audit-playbook.md) for the anti-pattern table, severity grading, and the assertion-query format.

## Output rules

- Cite exact file paths / parquet paths and line ranges for verified findings.
- Severity-rank findings (P0–P3); keep **Confirmed from code** separate from **Strongly inferred**.
- Every finding gets a smallest viable fix (usually one `CREATE VIEW`, one dedup key, or one tz cast) and a pinned DuckDB assertion query the user can drop into tests.
- Check the declared timestamp convention before calling naive timestamps a bug. Verify duplicate effects and ingest behavior in a disposable copy; do not rerun live ingestion during a review.
- If a category is clean, say so explicitly. Do not report generic database advice with no evidence in this store.

## Scope boundary

- Is each dataset's *origin* documented (source/date/methodology)? → `v-provenance`.
- Model training data hygiene (leakage, imbalance, target leakage)? → `v-dataset`.
- Serving/inference reliability? → `v-ml`.
- This skill only audits the DuckDB/Parquet storage and query layer.

## No parquet / no DuckDB

If the repo has no `.parquet` files and no DuckDB database, say so and stop — there is no data layer to audit here. Point the user at `v-provenance` or `v-dataset` if they have loose CSVs instead.

See [references/audit-playbook.md](references/audit-playbook.md) for the anti-pattern table, severity grading, and assertion-query templates.
