---
name: v-notebook
description: "Enforce the config-then-data-then-preprocessing-then-modeling notebook convention, strip git-bloating outputs, catch unseeded randomness, and promote stable logic from notebooks into src/. Use for Jupyter/.ipynb ML repos where notebooks should stay clean and reusable logic belongs in modules. Key capabilities: JSON-parse every notebook with no nbformat dependency, report section order vs the convention, committed output bytes, mid-notebook imports, missing end-of-block success prints, an unseeded-RNG census (the usual cause of results changing between runs), and code-cell duplication across notebooks and against src/*.py; then produce a violations table plus a promotion plan (which cells become typed, docstringed src/ functions) and end with one paste-ready cleanup bash block. Trigger phrases: clean my notebooks, promote this notebook to src/, enforce my notebook convention, strip outputs and check notebook hygiene, why do my notebook results change between runs, move stable logic out of the notebook."
---

# Notebook Hygiene & Promotion

Enforce the notebook convention, kill output bloat and unseeded randomness, and move stable logic into `src/` — ending with one paste-ready cleanup command.

Stay in review mode for the analysis. The only edits this skill makes are the promotion refactor and output strip, and only when the user asks.

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
