---
name: v-provenance
description: "Inventory dataset provenance and content hashes, detect missing or stale source records, and generate cards when requested. Use to document or verify CSV/Parquet lineage without changing source datasets."
---

# Data Provenance Stamp & Audit

Give every dataset a durable origin record, and flag the ones that have none or whose bytes have drifted from their card.

This skill both audits and generates. It writes provenance cards under `data/PROVENANCE/` (or `data/DATA.md`) only in `--emit` mode or when the user asks; it never modifies the datasets themselves.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Hash dataset bytes and trace source claims to acquisition code or existing records. Never infer a source merely from its filename. Create cards only when requested, preserving existing lineage and source data.

## Quick flow

1. Read repo context first if present: `AGENTS.md`, `CLAUDE.md`, `README.md`, `notes/`, and any existing `data/PROVENANCE/` or `data/DATA.md`.
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
