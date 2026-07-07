# Metric-Math Audit Playbook

The job: prove each hand-rolled metric in the repo matches its textbook
definition, and make the convention choices explicit so a wrong number is
diagnosed as a *convention* bug or a *math* bug, not just "looks off".

## Convention traps (the usual cause of a mismatch)

| Metric | Convention that silently changes the result |
|---|---|
| Sharpe / Sortino | `ddof=0` (numpy) vs `ddof=1` (pandas); annualize by `sqrt(252)` daily, `sqrt(12)` monthly, `sqrt(365)`/`sqrt(8760)` crypto; excess vs raw return; simple vs log returns |
| Max drawdown | computed on prices vs cumulative returns; reported as negative vs positive magnitude; peak via `cummax` vs global max |
| VaR | historical (empirical quantile) vs parametric-normal (`mu + z*sigma`, z_0.95=1.645, z_0.99=2.326); loss-positive vs return-negative sign; quantile interpolation method; horizon scaling by `sqrt(t)` on fat tails is wrong |
| CVaR / ES | mean of the tail beyond VaR vs the quantile itself; same sign convention as the VaR it pairs with |
| Volatility | `ddof`; annualization; population vs sample; log vs simple returns |
| AUC / ROC | arg order `(y_true, y_score)`; a value of 0.0 usually means the args are swapped (should have been ~1.0) |
| Brier / log-loss | probability vs class label input; clipping of 0/1 probabilities before `log` |
| ECE / calibration | bin count and bin edges (equal-width vs equal-frequency) change the number |

## Flow

1. Run `scripts/discover-metric-surface.sh <repo>` to list metric defs and the
   convention signals near them (annualization constants, `ddof`, quantile calls,
   return math).
2. Run `scripts/run-metric-benchmarks.py <repo>` (optionally `--module <file>`)
   to diff each function against `references/benchmarks.json`. Read the
   `recompute_note` on any FAIL — it tells you which convention the observed
   value implies (e.g. "~4.47 = ddof=1+sqrt(252); ~0.28 = did not annualize").
3. For each function, state the textbook definition, the convention the code
   actually uses (from the discovery grep + benchmark shape), and whether they
   agree.
4. Offer `--emit-pytest <out>` so the passing benchmarks become a permanent test.

## Output contract

One table, best-first by severity:

```
metric | file:line | convention detected | benchmark | smallest fix
```

- `benchmark` is one of PASS / FAIL / ERROR / MISSING (function not found) /
  N/A (no fixture for this metric).
- Label each finding **Confirmed from code** (you read the implementation and
  the benchmark ran) or **Strongly inferred** (discovery grep only).
- `smallest fix` is a one-liner where possible: `ddof=1`, `cov`/sign flip,
  `* np.sqrt(252)`, `method="lower"` on the quantile, swap `roc_auc_score` args.
- If a metric has no hand-rolled implementation (uses sklearn/numpy directly),
  say so and move on — do not invent problems.
- Close with the exact command to regenerate the pytest file so validation is
  permanent, per Veer's "validate against known benchmarks" rule.

## benchmarks.json contract

- Every `expected` is a hand-computed or closed-form ground truth. A failing
  test means the code diverges from the stated `convention` — never "fix" an
  expected value to make a test pass.
- If a fixture carries `expected_override`, that is the corrected value and the
  harness uses it in preference to `expected`.
- `abs_tol` is an absolute tolerance on the metric value; fall back to `1e-6`.

## Not this skill's job

- Serving/inference correctness of a deployed model → `v-ml` / `v-ml-deploy`.
- Whether the metric is the *right* metric for the business question → judgment
  call for the modeller, not a benchmark.
