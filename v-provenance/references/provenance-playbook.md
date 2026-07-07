# Data Provenance Playbook

The job: every dataset carries a durable record of where it came from (source,
retrieval date, methodology, transformations, content hash), and any dataset
without one is flagged. The deterministic facts are gathered by scripts; the
skill supplies the human-judgment fields and the lineage traced from code.

## Flow

1. Run `scripts/inventory-datasets.py <repo>` to profile every data file under
   the repo (sha256, size, rows, columns, per-column null rate, datetime
   min/max) and diff it against existing cards. Each dataset is classified:
   - `OK` — a card exists and its recorded hash still matches the bytes.
   - `STALE` — a card exists but the file changed since it was written.
   - `ORPHANED` — no card exists.
2. Trace lineage from code: grep for acquisition points — `read_csv`/`read_parquet`
   URLs, API clients, download scripts, connector modules — to reconstruct where
   each dataset came from and what transformed it.
3. Write or update a card per dataset (see template below), filling the
   computed facts automatically and labeling every human claim:
   - **Confirmed from code** — the source/transform is visible in a file:line.
   - **Strongly inferred** — implied by surrounding code but not explicit.
   - **Not found — fill in manually** — no evidence; the human must supply it.
4. `scripts/inventory-datasets.py <repo> --emit` writes pre-filled stubs for
   orphans under `data/PROVENANCE/`. `--verify` re-hashes and reports STALE/OK
   without writing anything.

## vee-cee: no-edge-without-provenance

For the knowledge-graph invariant, run
`scripts/sample-edge-provenance.py <repo>`. It samples graph edges and reports
any lacking a provenance record. Report violations labeled Confirmed (an edge
row with a null/absent provenance FK) vs Strongly inferred (schema allows it but
sample was clean). One violating edge is a P0 — the invariant is "no edge
without provenance", not "most edges".

## Provenance card template

```markdown
# Provenance: <dataset name>

- **File:** data/<path>
- **Content hash (sha256):** <computed>
- **Size / rows / columns:** <computed>
- **Date range:** <computed min>..<max>   (Confirmed from data)
- **Source:** <where it came from>   (Confirmed from code @ file:line | Strongly inferred | Not found — fill in manually)
- **Retrieval date:** <when pulled>   (Not found — fill in manually)
- **Query / API / endpoint used:** <exact call>   (Confirmed from code @ file:line)
- **Methodology / transformations:** <cleaning, joins, resampling applied>   (Confirmed from code @ file:line)
- **License / terms:** <license or usage terms>   (Not found — fill in manually)
- **Known gaps / caveats:** <missing periods, outages, quirks>
```

## Output contract

- One inventory table: `dataset | rows | date range | null hotspots | card status`.
- One generated or updated card per orphan/stale dataset under `data/PROVENANCE/`
  (or `data/DATA.md` if the repo already uses a single-file convention).
- A short verdict: how many datasets are OK / STALE / ORPHANED, and (vee-cee)
  whether the no-edge-without-provenance invariant holds.

## Not this skill's job

- Auditing whether the data is *clean enough to train on* (nulls, dupes,
  leakage) → `v-dataset`.
- DuckDB/Parquet schema drift, timezone rot, ingest idempotency → `v-duckdb-layer`.
- This skill answers only: is the origin of each dataset documented and current?
