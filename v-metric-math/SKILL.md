---
name: v-metric-math
description: "Prove hand-rolled metric code matches its textbook definition by diffing it against known-answer benchmarks. Use for repos with custom Sharpe, Sortino, max drawdown, VaR/CVaR, volatility, AUC, Brier, log-loss, or calibration/ECE implementations across finance and ML projects (risk-stability-insights, vee-cee signal-eval, funding-rate and macro-regime models). Key capabilities: discover metric functions and their convention signals (ddof, annualization constant, quantile method, simple-vs-log returns), run closed-form fixtures (normal VaR95=1.645, CVaR95=2.063, perfect AUC=1.0) through the repo's own functions, report PASS/FAIL/ERROR with observed-vs-expected, diagnose whether a mismatch is a convention bug or a math bug, and generate a permanent pytest file. Trigger phrases: verify my Sharpe/VaR math, does this formula match the textbook definition, benchmark-check the risk metrics module, validate the metric calculations, are these risk numbers right."
---

# Metric-Math Benchmark Audit

Prove every hand-rolled metric in the repo against a known-answer ground truth, and turn the passing checks into a permanent test.

Stay in review mode. Do not edit the repo's metric code unless the user explicitly asks for fixes. Writing the pytest file (an additive artifact) is allowed when requested.

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
