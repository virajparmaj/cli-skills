---
name: v-backtest-audit
description: "Review backtests and signal evaluation for lookahead, leakage, execution realism, and statistical inflation. Use when validating reported strategy performance; returns a plausible, inflated, or invalid verdict."
---

# Backtest Validity Audit

Decide whether a backtest's reported performance is real, inflated, or a mirage — before it drives a decision or a phase sign-off.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Distinguish measured or traced facts from unresolved hypotheses. Never report an audit scanner hit as proof on its own.

## Scope and boundaries

This is the umbrella backtest-validity skill. It covers three overlapping failure families in one pass:

- **Lookahead / leakage / survivorship / fantasy fills** — mechanical bugs that let the backtest see the future or trade at impossible prices.
- **Signal-evaluation hygiene** — how many signals were tried vs reported, whether metrics are truly out-of-sample, turnover/capacity, benchmark choice.
- **Statistical inflation** — multiple-testing exposure (deflated Sharpe), autocorrelation-inflated Sharpe, overlapping samples inflating t-stats.

Boundaries: for forecasting split correctness use **v-timeseries-leakage**; for live model *serving* reliability use **v-ml**. For repo-wide performance and dead-code audits use **v-scripts**. This skill judges whether the *numbers* can be trusted, not deployment.

## Quick start

Run relevant scripts to gather scanner candidates and statistical estimates, then inspect the flagged files in context. Confirm the actual trial count, sample length, and annualization before interpreting thresholds.

1. Read repo context if present, in this order, and skip missing files:
   - `AGENTS.md` and `CLAUDE.md`
   - `README.md`
   - `notes/13_prompt_context.md`
   - `notes/03_architecture.md`
   - `notes/11_known_issues.md`
   - any phase/spec docs (`*phase*.md`, `docs/`, `specs/`) that state the intended methodology
2. Run the leakage scanner:
   - `scripts/scan-leakage.py <repo-path>`
   - It flags `shift(-n)`, centered rolling, bfill/interpolate, `train_test_split(shuffle=True)`, `fit_transform`/scaler-fit-before-split, target-in-features overlap, as-of-today universe, zero-cost/same-bar fills, and prints each dataset's date span next to the declared split boundaries.
3. Run the signal inventory + multiple-testing facts:
   - `scripts/signal-inventory.py <repo-path> [--reported-sharpe X] [--trials N] [--n-obs T] [--periods-per-year F]`
   - It counts distinct signals defined vs metrics reported, extracts split dates, prints the deflated-Sharpe / Bonferroni threshold for N signals tried, and computes naive vs autocorrelation-adjusted Sharpe from any returns series.
4. Classify the repo before deep analysis:
   - `vectorized-backtest` (pandas/numpy frames), `event-driven engine` (DuckDB/Parquet, per-bar loop), `notebook research`, or `signal-eval-only` (metrics reported, no full engine).
5. Load [Audit Playbook](references/audit-playbook.md) and work its checklist for what to inspect, how to grade severity, and the report format.
6. For anything statistical — deflated Sharpe, signal ledger, autocorrelation adjustment, overlapping samples — load [Deflated Sharpe and Multiple Testing](references/deflated-sharpe.md).

## Output rules

- Cite exact file paths and line ranges for every verified finding.
- Label each finding **Confirmed from code** (you saw the bug in context) vs **Strongly inferred** (the scanner flagged it and the surrounding logic makes it very likely, but a runtime path could exonerate it). Never blur the two.
- Severity-rank findings P0–P3:
  - **P0** — invalidates results: lookahead into the traded signal, `shuffle=True` split on time data, target leaking into features, or impossible fills. A failed statistical threshold alone does not prove a mechanical invalidator.
  - **P1** — materially inflates results: scaler/model fit before the split, in-sample metrics reported as out-of-sample, missing transaction costs, autocorrelation-inflated Sharpe with no adjustment.
  - **P2** — biases results in a knowable direction: survivorship via blanket dropna or as-of-today universe, same-bar execution without decision lag, overlapping samples inflating t-stats.
  - **P3** — hygiene/provenance: missing turnover/capacity, unstated benchmark, no split-date literals, weak data provenance.
- Give each finding a **smallest viable fix** (the one-line-ish change, e.g. `shift(1)` after the rolling stat, `TimeSeriesSplit`, fit the scaler inside the train fold) and a **regression test** that pins it.
- If a category is clean, say so explicitly — e.g. "No lookahead patterns matched and every rolling stat is `+1`-shifted; lookahead: clean."
- Do not report generic quant best practices unless they tie to code or numbers in this repo.
- Do not duplicate issues already in `notes/11_known_issues.md`; reference them and assess whether they are resolved.

## Verdict (required last section)

End every audit with exactly one verdict and a one-line justification tied to the findings:

- **results plausible** — no material invalidator was verified and supported costs/splits are honest. State missing statistical inputs; passing a threshold does not establish profitability.
- **results inflated** — no hard invalidator, but P1/P2 issues (in-sample metrics, missing costs, autocorrelation, multiple testing) mean the true numbers are lower; state the direction and, where the scripts computed it, the deflated/adjusted re-estimate.
- **results invalid** — at least one P0 (lookahead into the signal, leaked target, shuffled time split, fantasy fills) means the numbers do not measure what they claim; the backtest must be re-run after the fix.

## Empty / not-applicable repo

- If the scanner scans zero source files or finds no backtest, signal, or metric code, say: "No backtest or signal-evaluation code found under `<repo-path>` — nothing to audit," and stop. Do not invent findings.
- If code exists but no datasets are present, still audit the code paths; note that date-span and returns-series facts could not be computed and mark related concerns **Strongly inferred**, not Confirmed.
- If pandas/pyarrow are unavailable, the scripts degrade gracefully and print install hints; rely on the code-level hits and report the missing numeric facts as unverified.

See [references/audit-playbook.md](references/audit-playbook.md) for the full inspection checklist, severity guide, and report template.
