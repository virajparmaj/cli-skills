# DuckDB / Parquet Data-Layer Audit Playbook

Purpose-built for vee-cee's local-first DuckDB/Parquet store, where the engine is
built phase-by-phase from markdown contracts and drift creeps in between phases
(a connector from an early phase writing naive timestamps that a later backtest
reads as UTC).

## What the script gathers

`scripts/parquet-facts.py <repo>` walks every `.parquet` (and DuckDB file when
`duckdb` is importable) and reports, grouped by logical table:

- **Schema fingerprint** per file, and a diff across files of the same table
  (schema drift = the same table with different columns/types across partitions).
- **Timezone awareness** per timestamp column: `TIMESTAMP` (naive) vs
  `TIMESTAMPTZ`. Naive timestamps in a market-data store are a bug.
- **Date range** (min/max) per timestamp column.
- **Duplicate-key counts** on candidate entity keys.
- **Row-group / file sizing** (tiny files or one giant row group).
- **Idempotency probe**: a stable hash of sorted keys so re-ingesting the same
  source twice is visible as a row-count doubling.

## Judgment layer (the skill reads the flagged code)

Review the query/ingest layer for:

| Anti-pattern | Why it bites | Smallest fix |
|---|---|---|
| Naive `TIMESTAMP` in a market store | reader assumes UTC, silent offset | one `AT TIME ZONE`/`::TIMESTAMPTZ` cast at write |
| `SELECT *` over wide parquet | reads columns the query never uses | project explicit columns |
| Order-dependence with no `ORDER BY` | non-deterministic across engine versions | add explicit `ORDER BY` |
| String-typed dates | breaks range filters and joins | cast to date/timestamp at ingest |
| No dedup on ingest | re-run doubles rows | dedup key / `INSERT ... ON CONFLICT` / `CREATE OR REPLACE` |
| Schema drift across partitions | union/scan fails or coerces silently | pin a schema or a `CREATE VIEW` with casts |

## Output contract

- Findings severity-ranked (P0–P3), each labeled **Confirmed from code**
  (the fact is in the parquet metadata or a file:line) vs **Strongly inferred**.
- Each finding gets a smallest viable fix — usually one `CREATE VIEW`, one
  dedup key, or one tz cast.
- Each finding ships a **pinned DuckDB assertion query** the user can drop into
  tests, e.g.:

  ```sql
  -- no naive timestamps in the funding table
  SELECT count(*) = 0 AS ok
  FROM information_schema.columns
  WHERE table_name = 'funding' AND data_type = 'TIMESTAMP';
  ```

  ```sql
  -- ingest is idempotent: no duplicate (exchange, ts) keys
  SELECT count(*) = 0 AS ok FROM (
    SELECT exchange, ts, count(*) c FROM funding GROUP BY 1,2 HAVING c > 1
  );
  ```
- If a category is clean, say so explicitly.

## Not this skill's job

- Whether each dataset's *origin* is documented → `v-provenance` (shares
  `parquet-facts.py`-style facts but answers a different question).
- Model training data hygiene (leakage, imbalance) → `v-dataset`.
- Serving/inference reliability → `v-ml` / `v-ml-deploy`.
