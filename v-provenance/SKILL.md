---
name: v-provenance
description: "Stamp every dataset with source, date, methodology, and content hash, and flag the ones with no provenance record. Use for finance and ML repos with data/ folders of CSV/Parquet (funding-rate, macro-regime, credit-risk projects) and for vee-cee's no-edge-without-provenance knowledge-graph invariant. Key capabilities: DuckDB/pandas inventory of every data file (sha256, rows, columns, null rates, datetime range), classify each as OK / STALE (bytes changed since its card) / ORPHANED (no card), trace lineage from acquisition code, generate pre-filled provenance cards under data/PROVENANCE/ with only human-judgment fields left blank, a --verify mode that re-hashes and catches stale cards, and edge-sampling to prove the no-edge-without-provenance invariant. Trigger phrases: stamp provenance on the datasets, which data files have no provenance, document data provenance, where did this dataset come from, verify the data hashes still match, verify the no-edge-without-provenance invariant."
---

# Data Provenance Stamp & Audit

Give every dataset a durable origin record, and flag the ones that have none or whose bytes have drifted from their card.

This skill both audits and generates. It writes provenance cards under `data/PROVENANCE/` (or `data/DATA.md`) only in `--emit` mode or when the user asks; it never modifies the datasets themselves.

## Quick flow

1. Read repo context first if present: `CLAUDE.md`, `README.md`, `notes/`, and any existing `data/PROVENANCE/` or `data/DATA.md`.
2. Run `scripts/inventory-datasets.py <repo>` to profile every data file and diff it against existing cards. Each dataset is reported `OK`, `STALE`, or `ORPHANED`.
   - `--emit` writes pre-filled provenance stubs for orphans.
   - `--verify` only re-hashes and reports STALE/OK; never writes.
   - `--json` dumps the raw facts.
3. Trace lineage: grep the code for acquisition points (`read_csv`/`read_parquet` URLs, API clients, download/connector scripts) to fill the source, query, and methodology fields with file:line evidence.
4. For vee-cee, run `scripts/sample-edge-provenance.py <repo>` to check the no-edge-without-provenance invariant.
5. Load [references/provenance-playbook.md](references/provenance-playbook.md) for the card template and output contract.

## Output rules

- One inventory table: `dataset | rows | date range | null hotspots | card status`.
- Every human-judgment claim in a card is labeled **Confirmed from code** (with file:line), **Strongly inferred**, or **Not found — fill in manually** — never silently guessed.
- Computed facts (hash, size, rows, date range) are filled automatically so only judgment fields remain for the human.
- A `STALE` card is a finding: the data changed but its provenance did not; report it, don't trust it.
- For vee-cee, a single edge without provenance is a P0 invariant violation.
- Close with counts: how many datasets OK / STALE / ORPHANED, and whether the invariant holds.

## Scope boundary

- Is the data *clean enough to train on* (nulls, dupes, split leakage)? → `v-dataset`.
- DuckDB/Parquet schema drift, timezone rot, ingest idempotency? → `v-duckdb-layer`.
- This skill answers only: is each dataset's origin documented and current?

## No data folder

If the repo has no `data/` directory and no data files, say so plainly and stop — there is nothing to stamp. Do not create empty provenance scaffolding.

See [references/provenance-playbook.md](references/provenance-playbook.md) for the card template, the vee-cee invariant check, and the full output contract.
