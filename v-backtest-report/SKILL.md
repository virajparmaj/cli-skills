---
name: v-backtest-report
description: "Generate a sourced strategy report from CSV or Parquet period returns, computing risk and performance metrics with explicit frequency and cost assumptions. Use to document a run; use v-backtest-audit to review validity."
---

# Backtest Report Generator

Turn a strategy's returns file into one standardized, assumption-honest backtest report where every metric is script-computed and only the judgment fields are yours to write.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Compute metrics from the supplied returns and record return units, observation frequency, and risk-free convention. Distinguish computed values from interpretation; do not estimate missing metrics or modify strategy code or source data.

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
- Label factual provenance as `Computed from returns` or `Confirmed from code`, as appropriate; any inference (e.g. attributing a drawdown to a regime) is `Strongly inferred`; if a fact cannot be found, write `Not found`.
- The final `## Known Gaps` section is a prioritized checklist (`- [ ]` items, most launch-blocking first) in Veer's task-list style.
- Do not add commentary, chat, or files outside the single report. See [references/metrics-glossary.md](references/metrics-glossary.md) for what each metric means and its caveats before writing the interpretation lines.

## Edge cases

- **Metric computation fails:** do not fabricate a table. Put the actual error or missing input in the metrics section and Known Gaps. Say `no return observations` only when that is the verified cause.
- **No weights supplied:** turnover renders as `n/a (no weights supplied)`; note in Known Gaps that turnover/transaction-cost realism is unverified.
- **No provenance/notes:** mark data provenance fields `Not found` and add a top-priority Known Gaps item; never guess the data source or date range.
- **Single in-sample period only:** if there is no out-of-sample split, say so explicitly in the boundaries section and flag it as a robustness gap rather than implying validation happened.

See [references/report-template.md](references/report-template.md) for the exact report structure this skill fills.
