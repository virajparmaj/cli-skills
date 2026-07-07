---
name: v-run-ledger
description: "Zero-infra experiment tracking: append one row per training run to experiments/runs.csv and generate model cards, with no MLflow or server. Use for ML repos where training runs are compared by scrolling notebook outputs and results evaporate between sessions. Key capabilities: append-only ledger (refuses to edit existing rows, matching the immutability rule) capturing run id, UTC time, git SHA + dirty flag, data-file sha256, model class, params JSON + hash, and CV metric mean/std; answer which-run-was-best from the ledger rather than memory; and generate models/<run-id>-card.md covering intended use, data provenance, CV protocol, metrics, assumptions, and limitations. Trigger phrases: log this training run, add this to the experiment ledger, generate a model card for this run, which run was best so far, track my experiments without mlflow, record this model result."
---

# Experiment Ledger & Model Cards

Lightweight, durable experiment tracking — one append-only CSV and generated model cards — so run comparisons survive between sessions.

This skill writes only under `experiments/` and `models/`. It is append-only: existing ledger rows are never edited or deleted.

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

1. Read repo context if present: `CLAUDE.md`, `README.md`, the training script, and any existing `experiments/runs.csv`.
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
