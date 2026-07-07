---
name: v-notebook
description: "Enforce the config-then-data-then-preprocessing-then-modeling notebook convention, strip git-bloating outputs, catch unseeded randomness, and promote stable logic from notebooks into src/. Use for Jupyter/.ipynb ML repos where notebooks should stay clean and reusable logic belongs in modules. Key capabilities: JSON-parse every notebook with no nbformat dependency, report section order vs the convention, committed output bytes, mid-notebook imports, missing end-of-block success prints, an unseeded-RNG census (the usual cause of results changing between runs), and code-cell duplication across notebooks and against src/*.py; then produce a violations table plus a promotion plan (which cells become typed, docstringed src/ functions) and end with one paste-ready cleanup bash block. Trigger phrases: clean my notebooks, promote this notebook to src/, enforce my notebook convention, strip outputs and check notebook hygiene, why do my notebook results change between runs, move stable logic out of the notebook."
---

# Notebook Hygiene & Promotion

Enforce the notebook convention, kill output bloat and unseeded randomness, and move stable logic into `src/` — ending with one paste-ready cleanup command.

Stay in review mode for the analysis. The only edits this skill makes are the promotion refactor and output strip, and only when the user asks.

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

1. Read repo context if present: `CLAUDE.md` (the convention lives there), `README.md`, and the `src/` layout.
2. Run `scripts/scan-notebooks.py <repo>` for deterministic facts: section order, committed output bytes, mid-notebook imports, success-print presence, unseeded-RNG sites, and duplicate code cells (across notebooks and vs `src/`).
3. Load [references/notebook-playbook.md](references/notebook-playbook.md) for the convention, the violations-table format, the promotion-plan format, and the output contract.
4. Produce the violations table and promotion plan, then end with exactly one bash cleanup block.

## Output rules

- Violations table: `notebook | violation | severity | smallest fix`.
- Label **duplication** findings **Confirmed from code** (hashes matched); label order/import/success-print findings **Strongly inferred** (heuristic) and confirm by eye.
- Unseeded randomness is High severity — it is the usual cause of "results changed between runs".
- The promotion plan names the `src/` module + function each stable cell becomes, with type hints and Google docstrings per Veer's Python standards, plus the rewritten import cell.
- End with exactly one fenced `bash` block for cleanup (strip outputs); nothing after it. If nothing needs cleanup, say so and omit the block.

## Scope boundary

- Data cleanliness (nulls, dupes, leakage) → `v-dataset`.
- Train/test temporal leakage → `v-timeseries-leakage`.
- Metric correctness → `v-metric-math`.
- This skill governs notebook structure, git hygiene, reproducibility, and src/ promotion.

## No notebooks

If the repo has no `.ipynb` files, say so and stop.

See [references/notebook-playbook.md](references/notebook-playbook.md) for the convention, tables, and the cleanup bash-block contract.
