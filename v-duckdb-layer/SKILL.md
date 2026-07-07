---
name: v-duckdb-layer
description: "Audit a DuckDB/Parquet data layer for schema drift, timezone rot, duplicate keys, and non-idempotent ingest. Built for vee-cee's local-first offline store and any repo backing analytics on Parquet files or a DuckDB database. Key capabilities: fingerprint each parquet schema and diff across partitions of the same table, flag naive TIMESTAMP vs TIMESTAMPTZ columns in market data, count duplicate entity keys, check row-group/file sizing, probe ingest idempotency (re-running a connector doubling rows), and review the query layer for SELECT * over wide parquet, order-dependence without ORDER BY, string-typed dates, and missing dedup. Emits severity-ranked findings with a smallest fix (one CREATE VIEW, one dedup key, one tz cast) and a pinned DuckDB assertion query per finding. Trigger phrases: audit the duckdb layer, check the parquet store for drift, why do I have duplicate rows after re-ingest, review the data layer before phase 10, is my timestamp column timezone-aware."
---

# DuckDB / Parquet Data-Layer Audit

Catch the cross-phase data-layer bugs — schema drift, naive timestamps, duplicate keys, non-idempotent ingest — before a downstream backtest silently trusts them.

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

1. Read repo context first if present: `CLAUDE.md`, `notes/03_architecture.md`, `notes/11_known_issues.md`, and any phase docs describing the data layer.
2. Run `scripts/parquet-facts.py <repo>` to gather deterministic facts: per-file schema fingerprints grouped by table, timezone-awareness of each timestamp column, min/max dates, duplicate-key counts, row-group sizes, and an idempotency hash.
3. Read the code the facts flag — connectors/writers for tz and dedup, query/scan sites for `SELECT *`, missing `ORDER BY`, and string-typed dates.
4. Load [references/audit-playbook.md](references/audit-playbook.md) for the anti-pattern table, severity grading, and the assertion-query format.

## Output rules

- Cite exact file paths / parquet paths and line ranges for verified findings.
- Severity-rank findings (P0–P3); keep **Confirmed from code** separate from **Strongly inferred**.
- Every finding gets a smallest viable fix (usually one `CREATE VIEW`, one dedup key, or one tz cast) and a pinned DuckDB assertion query the user can drop into tests.
- Naive timestamps in a market-data store and non-idempotent ingest are P0/P1 by default.
- If a category is clean, say so explicitly. Do not report generic database advice with no evidence in this store.

## Scope boundary

- Is each dataset's *origin* documented (source/date/methodology)? → `v-provenance`.
- Model training data hygiene (leakage, imbalance, target leakage)? → `v-dataset`.
- Serving/inference reliability? → `v-ml` / `v-ml-deploy`.
- This skill only audits the DuckDB/Parquet storage and query layer.

## No parquet / no DuckDB

If the repo has no `.parquet` files and no DuckDB database, say so and stop — there is no data layer to audit here. Point the user at `v-provenance` or `v-dataset` if they have loose CSVs instead.

See [references/audit-playbook.md](references/audit-playbook.md) for the anti-pattern table, severity grading, and assertion-query templates.
