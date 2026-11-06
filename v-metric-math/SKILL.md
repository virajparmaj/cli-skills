---
name: v-metric-math
description: "Benchmark custom financial and ML metric functions against explicit known-answer conventions. Use for Sharpe, drawdown, VaR, AUC, calibration, and related math checks; distinguish adapter errors from formula bugs."
---

# Metric-Math Benchmark Audit

Prove every hand-rolled metric in the repo against a known-answer ground truth, and identify the conventions each result assumes.

Stay in review mode. Do not edit the repo's metric code unless the user explicitly asks for fixes. Writing the pytest file (an additive artifact) is allowed when requested.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Distinguish measured or traced facts from unresolved hypotheses. Never report an audit scanner hit as proof on its own.

## Quick flow

1. Read repo context first if present: `AGENTS.md`, `CLAUDE.md`, `README.md`, `notes/03_architecture.md`, any `risk`/`metrics`/`eval` module names.
2. Run `scripts/discover-metric-surface.sh <repo>` to list metric function definitions and the convention signals near them (annualization constants, `ddof=`, `.quantile`/`.percentile`, simple-vs-log return math).
3. Run `scripts/run-metric-benchmarks.py <repo>` to diff the repo's functions against the known-answer fixtures in [references/benchmarks.json](references/benchmarks.json). Add `--module path/to/metrics.py` to pin discovery to one file. The harness prints PASS / FAIL / ERROR / MISSING per fixture with observed vs expected.
4. For each FAIL, read the fixture's `recompute_note` — it maps the observed number to the convention it implies (e.g. "~4.47 → ddof=1+sqrt(252); ~0.28 → not annualized").
5. Load [references/audit-playbook.md](references/audit-playbook.md) for the convention-trap table and the output contract.
6. If requested, generate executable known-answer tests with `scripts/run-metric-benchmarks.py <repo> --emit-pytest tests/test_metric_benchmarks.py`.

## Output rules

- Emit one table, most-severe first: `metric | file:line | convention detected | benchmark | smallest fix`.
- Label each finding **Confirmed from code** (implementation read and benchmark ran) or **Strongly inferred** (discovery grep only).
- `smallest fix` is a one-liner wherever possible (`ddof=1`, `* np.sqrt(252)`, sign flip, quantile `method=`, swap `roc_auc_score` arg order).
- Say explicitly when a metric uses a library implementation (sklearn/numpy) and needs no benchmark — do not invent problems.
- Never edit a fixture's `expected` to make a test pass; a failure means the code diverges from the stated convention.
- `--emit-pytest` writes real assertions for callable fixtures that produced a scalar; adapter/import errors stay in the report and are not emitted. Run the generated tests. Existing files are preserved unless replacement is explicitly requested with `--overwrite`. Inspect module top-level side effects before importing; use an isolated adapter when the module trains, downloads, or mutates on import.

## Scope boundary

- Serving/inference correctness of a deployed model → use `v-ml`.
- Statistical validity of a regression/hypothesis test (p-values, robust SEs, VIF) → use `v-regression-diagnostics`.
- This skill only answers: does the metric's *number* match its definition?

## No metrics found

If discovery and the harness find no hand-rolled metrics (everything uses sklearn/numpy directly), report that plainly: "No custom metric implementations to benchmark; the repo relies on library functions X, Y." Do not fabricate findings.

See [references/audit-playbook.md](references/audit-playbook.md) for the convention-trap table, benchmark contract, and full output format.
