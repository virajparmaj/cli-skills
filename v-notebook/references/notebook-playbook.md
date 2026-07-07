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
- **Unseeded randomness** is Confirmed (a random call site with no seed reaching
  it) and is the usual cause of "results changed between runs" — flag as High.

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
# strip committed outputs from all notebooks (requires nbconvert)
jupyter nbconvert --clear-output --inplace notebooks/*.ipynb

# or, stdlib-only strip if nbconvert is unavailable:
# python -c "import json,glob;[open(f,'w').write(json.dumps({**json.load(open(f)),'cells':[{**c,'outputs':[],'execution_count':None} if c.get('cell_type')=='code' else c for c in json.load(open(f))['cells']]},indent=1)) for f in glob.glob('notebooks/*.ipynb')]"
```

Adjust the glob to the repo's actual notebook location. If nothing needs
cleanup, say so and skip the bash block.

## Not this skill's job

- Whether the *data* is clean (nulls, dupes, leakage) → `v-dataset`.
- Whether train/test split leaks → `v-timeseries-leakage`.
- Whether metric math is correct → `v-metric-math`.
- This skill is about notebook structure, git hygiene, and promoting logic to
  `src/`.
