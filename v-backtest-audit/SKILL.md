---
name: v-backtest-audit
description: "Audit a backtesting or signal-evaluation repo for the classic invalidators, ending with a verdict: results plausible / inflated / invalid. Use for DuckDB/Parquet backtest engines, quant research notebooks (funding-rate, macro-regime), pandas time-series ML, and any signal-eval layer reporting Sharpe or IC. Detects lookahead (shift(-n), centered rolling, same-bar fills), leakage (fit before the time split, target in features, shuffle=True split on datetime data), survivorship, fantasy fills (zero cost/slippage/funding), and statistical inflation (multiple testing without deflated Sharpe, autocorrelation-inflated Sharpe). Runs scanner + signal-inventory scripts, counts signals tried vs reported, computes the deflated-Sharpe threshold, then reports severity-ranked findings with fixes. Trigger phrases: audit my backtest, check for lookahead or leakage, is this backtest result real, is this Sharpe real after multiple testing, deflate my backtest results, review the backtest engine before phase sign-off."
---

# Backtest Validity Audit

Decide whether a backtest's reported performance is real, inflated, or a mirage — before it drives a decision or a phase sign-off.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

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

## Scope and boundaries

This is the umbrella backtest-validity skill. It covers three overlapping failure families in one pass:

- **Lookahead / leakage / survivorship / fantasy fills** — mechanical bugs that let the backtest see the future or trade at impossible prices.
- **Signal-evaluation hygiene** — how many signals were tried vs reported, whether metrics are truly out-of-sample, turnover/capacity, benchmark choice.
- **Statistical inflation** — multiple-testing exposure (deflated Sharpe), autocorrelation-inflated Sharpe, overlapping samples inflating t-stats.

Boundaries: for general time-series ML pipeline correctness that is not backtest-specific, and for live model *serving* reliability, use **v-ml** / **v-ml-deploy**. For repo-wide performance and dead-code audits use **v-scripts**. This skill judges whether the *numbers* can be trusted, not deployment.

## Quick start

Run the scripts first so the leakage hits, signal counts, split dates, and the deflated-Sharpe bar are deterministic facts before any judgment. Then open the flagged files and confirm each in context.

1. Read repo context if present, in this order, and skip missing files:
   - `CLAUDE.md`
   - `README.md`
   - `notes/13_prompt_context.md`
   - `notes/03_architecture.md`
   - `notes/11_known_issues.md`
   - any phase/spec docs (`*phase*.md`, `docs/`, `specs/`) that state the intended methodology
2. Run the leakage scanner:
   - `scripts/scan-leakage.py <repo-path>`
   - It flags `shift(-n)`, centered rolling, bfill/interpolate, `train_test_split(shuffle=True)`, `fit_transform`/scaler-fit-before-split, target-in-features overlap, as-of-today universe, zero-cost/same-bar fills, and prints each dataset's date span next to the declared split boundaries.
3. Run the signal inventory + multiple-testing facts:
   - `scripts/signal-inventory.py <repo-path> [--reported-sharpe X] [--trials N]`
   - It counts distinct signals defined vs metrics reported, extracts split dates, prints the deflated-Sharpe / Bonferroni threshold for N signals tried, and computes naive vs autocorrelation-adjusted Sharpe from any returns series.
4. Classify the repo before deep analysis:
   - `vectorized-backtest` (pandas/numpy frames), `event-driven engine` (DuckDB/Parquet, per-bar loop), `notebook research`, or `signal-eval-only` (metrics reported, no full engine).
5. Load [Audit Playbook](references/audit-playbook.md) and work its checklist for what to inspect, how to grade severity, and the report format.
6. For anything statistical — deflated Sharpe, signal ledger, autocorrelation adjustment, overlapping samples — load [Deflated Sharpe and Multiple Testing](references/deflated-sharpe.md).

## Output rules

- Cite exact file paths and line ranges for every verified finding.
- Label each finding **Confirmed from code** (you saw the bug in context) vs **Strongly inferred** (the scanner flagged it and the surrounding logic makes it very likely, but a runtime path could exonerate it). Never blur the two.
- Severity-rank findings P0–P3:
  - **P0** — invalidates results: lookahead into the traded signal, `shuffle=True` split on time data, target leaking into features, zero-cost fills, a reported Sharpe that fails the deflated-Sharpe bar.
  - **P1** — materially inflates results: scaler/model fit before the split, in-sample metrics reported as out-of-sample, missing transaction costs, autocorrelation-inflated Sharpe with no adjustment.
  - **P2** — biases results in a knowable direction: survivorship via blanket dropna or as-of-today universe, same-bar execution without decision lag, overlapping samples inflating t-stats.
  - **P3** — hygiene/provenance: missing turnover/capacity, unstated benchmark, no split-date literals, weak data provenance.
- Give each finding a **smallest viable fix** (the one-line-ish change, e.g. `shift(1)` after the rolling stat, `TimeSeriesSplit`, fit the scaler inside the train fold) and a **regression test** that pins it.
- If a category is clean, say so explicitly — e.g. "No lookahead patterns matched and every rolling stat is `+1`-shifted; lookahead: clean."
- Do not report generic quant best practices unless they tie to code or numbers in this repo.
- Do not duplicate issues already in `notes/11_known_issues.md`; reference them and assess whether they are resolved.

## Verdict (required last section)

End every audit with exactly one verdict and a one-line justification tied to the findings:

- **results plausible** — no P0/P1 survived; the reported Sharpe clears the deflated bar; costs and out-of-sample split are honest.
- **results inflated** — no hard invalidator, but P1/P2 issues (in-sample metrics, missing costs, autocorrelation, multiple testing) mean the true numbers are lower; state the direction and, where the scripts computed it, the deflated/adjusted re-estimate.
- **results invalid** — at least one P0 (lookahead into the signal, leaked target, shuffled time split, fantasy fills) means the numbers do not measure what they claim; the backtest must be re-run after the fix.

## Empty / not-applicable repo

- If the scanner scans zero source files or finds no backtest, signal, or metric code, say: "No backtest or signal-evaluation code found under `<repo-path>` — nothing to audit," and stop. Do not invent findings.
- If code exists but no datasets are present, still audit the code paths; note that date-span and returns-series facts could not be computed and mark related concerns **Strongly inferred**, not Confirmed.
- If pandas/pyarrow are unavailable, the scripts degrade gracefully and print install hints; rely on the code-level hits and flag the missing numeric facts as a gap the developer should fill.

See [references/audit-playbook.md](references/audit-playbook.md) for the full inspection checklist, severity guide, and report template.
