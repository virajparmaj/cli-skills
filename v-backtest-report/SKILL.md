---
name: v-backtest-report
description: "Generate a standardized, assumption-honest backtest report from a strategy's returns file. Use for quant-finance strategy runs — funding-rate and volatility strategies, credit-risk or macro-regime backtests, or any CSV/Parquet of period returns. Deterministically computes the full metrics block (CAGR, annualized vol, Sharpe, Sortino, Calmar, max drawdown + underwater duration, VaR95/CVaR95, hit rate, turnover) via scripts/compute-metrics.py, then writes one reports/backtest-<name>.md against a strict template: strategy spec, data provenance, cost model, in/out-of-sample boundaries, computed metrics table, robustness checks, and a prioritized Known Gaps section. Every number traces to a computed value or code; anything else is labeled Strongly inferred. Trigger phrases: write the backtest report, document this strategy run, generate a report for this returns file, make the phase 10 backtest write-up. To review an existing report's correctness instead, use v-backtest-audit."
---

# Backtest Report Generator

Turn a strategy's returns file into one standardized, assumption-honest backtest report where every metric is script-computed and only the judgment fields are yours to write.

## Boundary

- This skill **generates** a report. To review or grade an existing backtest for correctness and hidden bugs, use `v-backtest-audit` (the sibling that shares the same metrics contract).
- It documents finance/strategy runs, not repo architecture. For general project docs use `v-notes` / `v-notes-update`.

## Quick flow

1. Locate the inputs and context before writing anything:
   - the returns file (CSV/Parquet with one row per period) and any weights/trades file
   - `notes/` docs if present (`notes/00_overview.md`, `notes/13_prompt_context.md`) and any `provenance`/`data` stamp for source lineage
   - the strategy code or notebook that produced the returns, to fill the spec and cost-model fields
2. Compute every number deterministically. Run the helper first — never estimate a metric:
   ```
   scripts/compute-metrics.py <returns_file> [--weights-file <w>] [--freq daily|weekly|monthly|quarterly|yearly] [--return-col <c>] [--date-col <c>] [--risk-free 0.04] [--as-percent]
   ```
   It prints a `=== metrics json ===` block and a ready-to-paste `=== metrics markdown ===` table. Pick `--freq` (or `--periods-per-year`) to match the data; pass `--as-percent` if returns are in percent points; pass `--weights-file` to get turnover.
3. Copy the script's Markdown table verbatim into the report's metrics section. Do not round, retype, or "improve" the numbers.
4. Fill only the judgment fields from code and provenance evidence: strategy spec, data provenance, cost model and assumptions, in/out-of-sample boundaries, robustness checks, and Known Gaps.
5. Write exactly one file, `reports/backtest-<name>.md`, using [references/report-template.md](references/report-template.md). Create `reports/` if it does not exist. Emit no prose outside the template.

## Output contract (strict)

- Produce **one** report file per invocation at `reports/backtest-<strategy-name>.md`. `<strategy-name>` is a lowercase kebab slug of the strategy.
- The file's structure must match [references/report-template.md](references/report-template.md) exactly: same H2 section order, same headings.
- The metrics table is the script's `=== metrics markdown ===` output pasted verbatim. Every quantitative claim elsewhere in the report must reference a value from the metrics JSON or a specific line of strategy code.
- Label provenance on each factual line: numbers straight from the script or a cited file line are `Confirmed from code`; any inference (e.g. attributing a drawdown to a regime) is `Strongly inferred`; if a fact cannot be found, write `Not found` — never invent it.
- The final `## Known Gaps` section is a prioritized checklist (`- [ ]` items, most launch-blocking first) in Veer's task-list style.
- Do not add commentary, chat, or files outside the single report. See [references/metrics-glossary.md](references/metrics-glossary.md) for what each metric means and its caveats before writing the interpretation lines.

## Edge cases

- **No returns / empty file:** if `scripts/compute-metrics.py` exits non-zero or finds zero observations, do not fabricate a table. Write the report with the metrics section replaced by `Not computable — no return observations in <file>` and a Known Gaps entry to supply valid returns.
- **No weights supplied:** turnover renders as `n/a (no weights supplied)`; note in Known Gaps that turnover/transaction-cost realism is unverified.
- **No provenance/notes:** mark data provenance fields `Not found` and add a top-priority Known Gaps item; never guess the data source or date range.
- **Single in-sample period only:** if there is no out-of-sample split, say so explicitly in the boundaries section and flag it as a robustness gap rather than implying validation happened.

See [references/report-template.md](references/report-template.md) for the exact report structure this skill fills.
