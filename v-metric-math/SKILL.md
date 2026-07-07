---
name: v-metric-math
description: "Prove hand-rolled metric code matches its textbook definition by diffing it against known-answer benchmarks. Use for repos with custom Sharpe, Sortino, max drawdown, VaR/CVaR, volatility, AUC, Brier, log-loss, or calibration/ECE implementations across finance and ML projects (risk-stability-insights, vee-cee signal-eval, funding-rate and macro-regime models). Key capabilities: discover metric functions and their convention signals (ddof, annualization constant, quantile method, simple-vs-log returns), run closed-form fixtures (normal VaR95=1.645, CVaR95=2.063, perfect AUC=1.0) through the repo's own functions, report PASS/FAIL/ERROR with observed-vs-expected, diagnose whether a mismatch is a convention bug or a math bug, and generate a permanent pytest file. Trigger phrases: verify my Sharpe/VaR math, does this formula match the textbook definition, benchmark-check the risk metrics module, validate the metric calculations, are these risk numbers right."
---

# Metric-Math Benchmark Audit

Prove every hand-rolled metric in the repo against a known-answer ground truth, and turn the passing checks into a permanent test.

Stay in review mode. Do not edit the repo's metric code unless the user explicitly asks for fixes. Writing the pytest file (an additive artifact) is allowed when requested.

## Quick flow

1. Read repo context first if present: `CLAUDE.md`, `README.md`, `notes/03_architecture.md`, any `risk`/`metrics`/`eval` module names.
2. Run `scripts/discover-metric-surface.sh <repo>` to list metric function definitions and the convention signals near them (annualization constants, `ddof=`, `.quantile`/`.percentile`, simple-vs-log return math).
3. Run `scripts/run-metric-benchmarks.py <repo>` to diff the repo's functions against the known-answer fixtures in [references/benchmarks.json](references/benchmarks.json). Add `--module path/to/metrics.py` to pin discovery to one file. The harness prints PASS / FAIL / ERROR / MISSING per fixture with observed vs expected.
4. For each FAIL, read the fixture's `recompute_note` — it maps the observed number to the convention it implies (e.g. "~4.47 → ddof=1+sqrt(252); ~0.28 → not annualized").
5. Load [references/audit-playbook.md](references/audit-playbook.md) for the convention-trap table and the output contract.
6. If the user wants the validation to stick, run `scripts/run-metric-benchmarks.py <repo> --emit-pytest tests/test_metric_benchmarks.py`.

## Output rules

- Emit one table, most-severe first: `metric | file:line | convention detected | benchmark | smallest fix`.
- Label each finding **Confirmed from code** (implementation read and benchmark ran) or **Strongly inferred** (discovery grep only).
- `smallest fix` is a one-liner wherever possible (`ddof=1`, `* np.sqrt(252)`, sign flip, quantile `method=`, swap `roc_auc_score` arg order).
- Say explicitly when a metric uses a library implementation (sklearn/numpy) and needs no benchmark — do not invent problems.
- Never edit a fixture's `expected` to make a test pass; a failure means the code diverges from the stated convention.
- End with the exact `--emit-pytest` command so the benchmarks become permanent, per Veer's "validate against known benchmarks" rule.

## Scope boundary

- Serving/inference correctness of a deployed model → use `v-ml` or `v-ml-deploy`.
- Statistical validity of a regression/hypothesis test (p-values, robust SEs, VIF) → use `v-regression-diagnostics`.
- This skill only answers: does the metric's *number* match its definition?

## No metrics found

If discovery and the harness find no hand-rolled metrics (everything uses sklearn/numpy directly), report that plainly: "No custom metric implementations to benchmark; the repo relies on library functions X, Y." Do not fabricate findings.

See [references/audit-playbook.md](references/audit-playbook.md) for the convention-trap table, benchmark contract, and full output format.
