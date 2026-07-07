# Formula-to-Code Traceability (pre-flight check)

Absorbed from the derivation-trace idea: when a phase doc or an accompanying
report states a formula, verify the code implements that exact formula before
declaring the phase (or a prior phase) done. Same contract serves coursework
writeups graded on derivation-code agreement (Meals-Academic-Outcomes,
`coursecode/`) and vee-cee phase contracts where a spec formula must map to an
engine implementation.

This is a pre-flight sub-check of the phase workflow, not a standalone audit. Run
it only when the docs actually contain math.

## When to run

Run the harvester when the target phase doc, a linked report `.md`, or a notebook
markdown cell contains `$$...$$`, `\begin{align}`, or inline `$...$` math that the
phase is supposed to implement.

```
scripts/extract-equations.py <repo-path> --doc <phase-doc-or-report.md>
scripts/extract-equations.py <repo-path>          # scan every .md and .ipynb
scripts/extract-equations.py <repo-path> --json   # machine-readable pairing
```

The script emits two lists:

- `=== equations extracted ===` — every numbered math block `[eq N]` with its
  source file and LaTeX.
- `=== candidate math-bearing code lines ===` — `file:line: code` for lines
  calling numpy/scipy/statsmodels/pandas/torch or carrying operator-heavy stats.

`.ipynb` parsing prefers `nbformat`; without it the script falls back to a
tolerant JSON reader and prints a one-line install hint. Both paths work in a
bare Python 3.11 venv.

## Build the trace table

Pair each equation to the code line that implements it:

```
## Formula trace

| eq | statement (from doc) | code | verdict |
| --- | --- | --- | --- |
| eq 1 | sample variance, ddof = 1 | src/stats/var.py:22 uses np.var(x, ddof=1) | MATCH |
| eq 2 | population variance, 1/N | src/stats/var.py:31 uses np.var(x) (ddof=0) | MATCH |
| eq 3 | z = (x - mu) / sigma | (not implemented) | MISSING |
| — | src/stats/scale.py:14 divides by (n-1) | (no stated equation) | ORPHAN |
```

## Defect types to flag

- **MISMATCH** — the code computes something different from the stated formula.
  Quote the exact discrepancy: "doc says population variance (divide by N), code
  uses `np.var(x, ddof=1)` (divide by N-1) at `src/stats/var.py:22`."
- **MISSING** — a derivation step or formula the phase promises is never
  implemented in code.
- **ORPHAN** — math in the code with no corresponding stated equation; note it so
  the writeup can be reconciled, but it does not by itself fail a phase.

## Feed the verdicts back into the phase table

- Any **MISMATCH** or **MISSING** on a prior phase's stated formula makes that
  phase `MISSING` in the Step 2 pre-flight table, not `CONFIRMED`.
- For the phase being implemented, resolve every MISMATCH/MISSING as part of the
  work — the implementation must match the doc's math exactly.

## Suggest grep-cheap anchors

For each confirmed pairing, suggest an equation-number comment anchor so future
traceability is a one-line grep:

```python
variance = np.var(returns, ddof=1)  # eq. (1): sample variance
```

Only suggest anchors; do not rewrite code during the pre-flight. Add them as part
of the Step 4 implementation if the user wants them.

## Common `ddof` and estimator traps

- Sample vs population variance/std: `ddof=1` (n-1) vs `ddof=0` (N).
- `statsmodels` OLS includes an intercept only if you add a constant column.
- `scipy.stats` t-tests default to two-sided; a one-sided derivation needs
  `alternative=`.
- Correlation vs covariance: `np.corrcoef` normalizes, `np.cov` does not.
- Log base: `np.log` is natural log; a `log10`/`log2` derivation needs the right
  call.
