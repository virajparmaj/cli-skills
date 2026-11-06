# Notebook Hygiene & Promotion Playbook

Enforces Veer's notebook convention and moves stable logic into `src/`, ending
with a single paste-ready cleanup command.

## The convention (from CLAUDE.md)

Cell order: **config → data → preprocessing → modeling**. Stable logic belongs
in `src/`, not the notebook. Major blocks end with a success print
(`print("✅ Data loaded successfully")`). Notebooks stay clean; committed
outputs do not bloat git.

## Flow

1. Run `scripts/scan-notebooks.py <repo>`. It reports per notebook: detected
   section order, committed output bytes, mid-notebook imports, success-print
   presence, an unseeded-RNG census, and code-cell duplication (across notebooks
   and against `src/*.py`).
2. Build a violations table and a promotion plan (below).
3. End with exactly one bash block of cleanup commands.

## Violations table

```
notebook | violation | severity | smallest fix
```

- **Duplication** findings (a cell whose normalized code matches another
  notebook or an existing `src/` function) are **Confirmed from code** — the
  hashes matched.
- **Order drift**, **mid-notebook imports**, and **missing success prints** are
  **Strongly inferred** from headers/content heuristics; confirm by eye before
  asserting.
- **Unseeded randomness** is a candidate until seed handling is traced through
  the executed path. Shared setup or a passed generator may seed the call; rate
  the actual reproducibility effect rather than assigning severity by pattern.

## Promotion plan

For each block of stable logic that should leave the notebook:

- name the `src/` module and function it becomes (with type hints + Google
  docstring per Veer's Python standards),
- give the rewritten import cell for the notebook,
- note the config cell the imports consolidate into.

## Output contract (ends in one bash block)

After the tables, emit exactly one fenced `bash` block for mechanical cleanup —
strip outputs and (optionally) stage — nothing after it:

```bash
# clear outputs from the selected notebooks (requires nbconvert)
jupyter nbconvert --clear-output --inplace notebooks/*.ipynb

# Alternative when nbconvert is unavailable: use this skill's stdlib helper.
# python3 "<loaded-skill-directory>/scripts/strip-outputs.py" notebooks/*.ipynb
```

Adjust the glob to the repo's actual notebook location. If nothing needs
cleanup, say so and skip the bash block.

Use one cleanup method. The bundled helper reads and validates each notebook
before writing, clears only code-cell outputs and execution counts, preserves
other content and permissions, and atomically replaces changed files. Never
open a notebook for writing before reading its JSON. Cleanup and staging remain
separate actions; stage only when requested.

## Not this skill's job

- Whether the *data* is clean (nulls, dupes, leakage) → `v-dataset`.
- Whether train/test split leaks → `v-timeseries-leakage`.
- Whether metric math is correct → `v-metric-math`.
- This skill is about notebook structure, git hygiene, and promoting logic to
  `src/`.
