---
name: v-provenance
description: "Stamp every dataset with source, date, methodology, and content hash, and flag the ones with no provenance record. Use for finance and ML repos with data/ folders of CSV/Parquet (funding-rate, macro-regime, credit-risk projects) and for vee-cee's no-edge-without-provenance knowledge-graph invariant. Key capabilities: DuckDB/pandas inventory of every data file (sha256, rows, columns, null rates, datetime range), classify each as OK / STALE (bytes changed since its card) / ORPHANED (no card), trace lineage from acquisition code, generate pre-filled provenance cards under data/PROVENANCE/ with only human-judgment fields left blank, a --verify mode that re-hashes and catches stale cards, and edge-sampling to prove the no-edge-without-provenance invariant. Trigger phrases: stamp provenance on the datasets, which data files have no provenance, document data provenance, where did this dataset come from, verify the data hashes still match, verify the no-edge-without-provenance invariant."
---

# Data Provenance Stamp & Audit

Give every dataset a durable origin record, and flag the ones that have none or whose bytes have drifted from their card.

This skill both audits and generates. It writes provenance cards under `data/PROVENANCE/` (or `data/DATA.md`) only in `--emit` mode or when the user asks; it never modifies the datasets themselves.

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
