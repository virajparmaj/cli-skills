# Pre-Training Dataset Audit Playbook

The start-of-every-ML-project check. Enforces Veer's hard rules — missing data
handled explicitly (never silently dropped), no rows shared across splits — and
flags suspiciously predictive columns as candidate target leakage.

## Flow

1. `scripts/profile-dataset.py <repo> [--target <col>]` — per-column null %,
   dtype anomalies, exact-duplicate rows, near-constant / id-like columns, class
   balance, and a feature-target association ranking (a feature with ~1.0
   association is candidate target leakage).
2. Split overlap: `scripts/profile-dataset.py --train <a> --test <b>` — sha1
   row-hash intersection between the two files. Any overlap is leakage.
3. Data-loss ledger: `scripts/find-silent-drops.py <repo>` — every `dropna`,
   `fillna`, `errors='coerce'`, inner merge/join, reindex, resample, and
   `drop_duplicates` site, with biasing operations called out.
4. Time-series / crypto extension: `scripts/funding-grid-check.py <repo> --file
   <data>` — interval histogram (8h grid?), gaps, duplicate timestamps, timezone
   awareness, plus a grep for annualization constants and funding ffill/resample.

## Judgment layer

| Signal | Verdict question | Smallest fix |
|---|---|---|
| Column with 20%+ nulls | is it dropped, imputed, or ignored? | explicit `fillna`/`dropna` with a documented reason |
| Exact duplicate rows | dedupe before or after split? | `drop_duplicates()` before the split |
| Feature ~1.0 assoc with target | leakage or legitimately strong? | drop it, or prove it's available at predict time |
| Row hashes shared across splits | leakage | split by time/group, not randomly |
| `fillna(0)` on returns / `ffill` across regimes | biases downstream stats | impute with a justified value or mask |
| inner merge eating a third of rows | silent sample loss | count rows in→out; switch to left join or document |
| off-grid funding intervals | exchange changed cadence mid-sample | resample to a fixed grid or segment the sample |

## Output contract

- Severity-ranked findings, each labeled **Confirmed from data** (the profiler
  measured it) or **Strongly inferred** (a code pattern, not yet measured).
- Each finding: the one pandas snippet to apply the smallest fix.
- A short data-loss ledger table: `step | file:line | rows in→out (measured or
  "unmeasured") | verdict`.
- Optionally a ready-to-paste missing-data statement paragraph for README/notes,
  per Veer's provenance rule.
- If the data is clean on a dimension, say so explicitly.

## Not this skill's job

- Where the data *came from* (source/date/methodology) → `v-provenance`.
- DuckDB/Parquet schema drift / timezone rot at the storage layer → `v-duckdb-layer`.
- Whether the train/test *split protocol* leaks temporally → `v-timeseries-leakage`.
- This skill answers: is this data clean and honest enough to train on?
