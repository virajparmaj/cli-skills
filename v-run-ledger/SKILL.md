---
name: v-run-ledger
description: "Append training-run facts to an immutable CSV ledger, compare recorded runs, and generate sourced model cards. Use for lightweight experiment tracking without a server; corrections are new rows."
---

# Experiment Ledger & Model Cards

Lightweight, durable experiment tracking — one append-only CSV and generated model cards — so run comparisons survive between sessions.

This skill writes only under `experiments/` and `models/`. It is append-only: existing ledger rows are never edited or deleted.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Log measured run facts and supplied parameters. Do not manufacture metrics, overwrite existing model cards, or rewrite earlier rows. Disclose incompatible datasets, split protocols, or scoring conventions when comparing runs.

## Quick flow

1. Read repo context if present: `AGENTS.md`, `CLAUDE.md`, `README.md`, the training script, and any existing `experiments/runs.csv`.
2. Log a run: `scripts/log-run.py <repo> --data <file> --model <cls> --params '<json>' --metric <name> --mean <m> --std <s> --note "<what changed>"`. The appended row is echoed back verbatim.
3. Compare: `scripts/log-run.py <repo> --best <metric> [--minimize] [--top N]` answers "which run was best" from the ledger only.
4. Model card: read the winning row + training script and write `models/<run-id>-card.md` per the template.
5. Load [references/ledger-playbook.md](references/ledger-playbook.md) for the schema, card template, and output contract.

## Output contract

- On log: echo the single appended row verbatim, then the ledger path and total row count. No other text.
- On "which run was best": print the sorted top rows from the ledger; never answer from memory.
- On model card: write the card, print its path and a one-line summary; pull metrics from the ledger row, never fabricate them. Label every card claim **Confirmed from code**, **Strongly inferred**, or **Not found — fill in manually**.
- Never edit or delete a row; corrections are new appended rows with an explanatory note.

## Scope boundary

- Where the data came from → `v-provenance` (the model card links to its data card).
- Running the baseline model zoo → `v-baselines` (which appends here when the ledger exists).
- This skill is the durable record of runs and their model cards.

See [references/ledger-playbook.md](references/ledger-playbook.md) for the schema, best-run queries, and model-card template.
