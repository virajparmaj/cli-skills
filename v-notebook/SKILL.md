---
name: v-notebook
description: "Review or clean Jupyter notebooks for section order, output bloat, reproducibility, and reusable-code promotion into src/. Use for notebook hygiene or requested refactors; changes require an implementation request."
---

# Notebook Hygiene & Promotion

Enforce the notebook convention, kill output bloat and unseeded randomness, and move stable logic into `src/` — ending with one paste-ready cleanup command.

Stay in review mode for the analysis. The only edits this skill makes are the promotion refactor and output strip, and only when the user asks.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Confirm the effect of section-order, seed, and duplicate-cell scanner results before proposing changes. Identical text alone does not prove a shared abstraction is appropriate.

## Quick flow

1. Read repo context if present: `CLAUDE.md` (the convention lives there), `README.md`, and the `src/` layout.
2. Run `scripts/scan-notebooks.py <repo>` for deterministic facts: section order, committed output bytes, mid-notebook imports, success-print presence, unseeded-RNG sites, and duplicate code cells (across notebooks and vs `src/`).
3. Load [references/notebook-playbook.md](references/notebook-playbook.md) for the convention, the violations-table format, the promotion-plan format, and the output contract.
4. Produce the violations table and promotion plan, then end with exactly one bash cleanup block.

For an authorized output cleanup without nbconvert, run `scripts/strip-outputs.py <explicit notebook paths>`. It validates before writing and replaces changed files atomically. Quote paths and select only notebooks in the requested scope.

## Output rules

- Violations table: `notebook | violation | severity | smallest fix`.
- Label **duplication** findings **Confirmed from code** (hashes matched); label order/import/success-print findings **Strongly inferred** (heuristic) and confirm by eye.
- Trace seed handling across the executed path before calling randomness uncontrolled; shared setup may seed it. Rate the observed reproducibility effect.
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
