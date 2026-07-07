# Backtest Validity Audit Playbook

You are a quant researcher auditing a backtesting or signal-evaluation repository to decide whether its reported performance is real, inflated, or invalid. Stay in review mode and do not edit files unless explicitly asked.

Work the scanner output first (`scripts/scan-leakage.py`, `scripts/signal-inventory.py`), then open the flagged files and confirm each hit in context. A regex hit is a candidate, not a verdict — some `shift(-1)` calls build labels intentionally and are fine as long as the label never enters the feature set.

## Step 0: Load context and the intended methodology

Read, in order, skipping what is absent:

1. `CLAUDE.md`, `README.md`
2. `notes/13_prompt_context.md`, `notes/03_architecture.md`, `notes/11_known_issues.md`
3. Any phase/spec docs (`*phase*.md`, `docs/`, `specs/`) — these often state the *intended* train/test split, cost model, and universe. An audit is measuring reality against that stated intent.

Capture: the claimed methodology (split dates, cost assumptions, universe, benchmark) and the headline numbers being claimed (Sharpe, IC, CAGR, drawdown).

## Step 1: Classify the repo

- `vectorized-backtest` — signals and returns are pandas/numpy columns; leakage hides in `.shift`, rolling windows, and split ordering.
- `event-driven engine` — DuckDB/Parquet + a per-bar loop; leakage hides in forward index access and same-bar fills; costs hide in the fill model.
- `notebook research` — cells run top-to-bottom; leakage hides in a scaler `fit` cell that runs before the split cell, and in re-run cells that quietly change N.
- `signal-eval-only` — metrics reported, no full engine; focus shifts to the signal ledger and multiple testing (see the deflated-Sharpe reference).

## Step 2: Inspect for the four invalidator families

For every finding cite `file:line`. If a family is clean, say so explicitly.

### A. Lookahead bias — the backtest sees the future

1. **Negative shift into a feature.** `shift(-n)` / `shift(periods=-n)` pulls future bars into the present. It is *only* acceptable when building a label that never re-enters the feature matrix. Trace where the shifted column goes.
2. **Centered / non-lagged rolling stats.** `rolling(...).mean()` with `center=True`, or any rolling stat used on the same bar it closes, includes the current (unfinished) bar. The honest pattern is `rolling(w).mean().shift(1)`.
3. **Resample-then-align.** `resample('1D')` right-labels the bar at the close; joining that back to intraday rows can expose the daily close before it happened. Confirm the alignment lags the resampled value.
4. **Backfill / interpolate.** `bfill()` and `interpolate()` copy future values backward — always leakage in a time series. `ffill()` is directionally safe but check it is not paired with a later bfill.
5. **Forward index access.** In an event loop, `df.iloc[i+k]` or `prices[t+1]` inside the decision step reads a bar that has not occurred.
6. **Same-bar signal + execution.** If the signal is computed from bar `t`'s close and the fill also happens at bar `t`'s close, there is no decision lag — you traded on information you only had at the close. Execution should be at `t+1` open (or `t` close with the signal from `t-1`).

### B. Data leakage — training on information from the test period

1. **Fit before split.** Any `StandardScaler/MinMaxScaler/model.fit(...)` or `fit_transform(...)` on the *full* frame fits on test data. The scaler must be fit inside the train fold and only `transform` applied to test.
2. **Shuffled split on time data.** `train_test_split(..., shuffle=True)` (or the default, which is `shuffle=True`) on datetime-indexed data trains on the future and tests on the past. Same for plain `KFold`/`cross_val_score` — temporal data needs `TimeSeriesSplit`.
3. **Target in features.** A column that is the label (or a monotone transform of it, or a future return) sitting in the feature matrix. The scanner flags obvious name overlaps; also check for near-duplicates (`return` used as both target and a feature via a lag of the wrong sign).
4. **Group leakage.** The same entity/day appearing in both train and test (e.g. multiple rows per timestamp split randomly).
5. **Preprocessing statistics computed globally.** Winsorization bounds, z-score means, PCA components, or feature selection computed on all data then applied per-fold.

### C. Survivorship and universe bias

1. **As-of-today universe.** A ticker/symbol list named `current_/latest_/active_` or pulled from `yfinance`/an API that only returns live names. Delisted, merged, or bankrupt names are missing, so the backtest only trades survivors.
2. **Blanket `dropna()`.** Dropping all rows with NaNs can silently remove the exact rows where a name delisted — the worst outcomes vanish.
3. **Point-in-time joins.** For fundamentals or index membership, confirm the join is as-of the decision date, not the latest revision (restated financials leak).

### D. Transaction-cost realism — fantasy fills

1. **Zero cost/slippage/funding.** Explicit `cost=0`, `fee=0`, `slippage=0`, or `funding=0`, or the total absence of any cost term. For the funding-rate project specifically, funding drag is the strategy's main cost and must be charged every interval.
2. **Fill at an impossible price.** Filling at the exact close/open you used to decide, filling with no spread, or assuming unlimited size at the touch. Real fills pay the spread and move with size.
3. **Turnover ignored.** High-turnover signals die on costs. If turnover/capacity is never computed (scanner reports this), the net-of-cost Sharpe is unknown and the gross number is an upper bound.

## Step 3: Statistical inflation

Load [Deflated Sharpe and Multiple Testing](deflated-sharpe.md) and build the **signal ledger**, then judge:

- **Multiple testing.** N signals tried means the best one's Sharpe must beat the expected maximum of N noise strategies (deflated Sharpe / Bonferroni). The `signal-inventory.py` script prints N and the bar.
- **Autocorrelation-inflated Sharpe.** Positive return autocorrelation understates volatility and inflates the naive Sharpe. The script prints naive vs Newey-West-adjusted Sharpe; report the adjusted number.
- **In-sample masquerading as out-of-sample.** If there are no split-date literals, or metrics are computed before the split cell, treat every metric as in-sample (an upper bound).
- **Overlapping samples.** Overlapping return windows (e.g. 20-day forward returns sampled daily) inflate t-stats; effective sample size is far below the row count.

## Step 4: Report

Organize the audit as:

### 1. Summary

Repo classification, claimed methodology and headline numbers, and the scanner facts (files scanned, hit counts by severity, signals tried, deflated-Sharpe bar, naive vs adjusted Sharpe, dataset spans vs declared splits).

### 2. Signal ledger

One table (from the deflated-Sharpe reference): `signal | sample period | metric | in/out-of-sample | adjusted? | verdict`.

### 3. Findings (severity-ranked, P0 first)

Use this block per finding:

```
[P0] Lookahead: momentum signal uses shift(-1) close — src/signals.py:42
Confirmed from code
- What fails: the 1-bar-ahead close is fed into the feature matrix at features.py:88, so every trade knows the next bar.
- Evidence: signals.py:42 computes fwd = close.shift(-1); features.py:88 includes 'fwd' in FEATURE_COLS.
- Smallest fix: drop 'fwd' from FEATURE_COLS; keep it only as the label y.
- Regression test: assert set(FEATURE_COLS).isdisjoint(LABEL_COLS); assert model has no access to any negative-shift column.
```

Label every finding **Confirmed from code** or **Strongly inferred**. State direction of bias (inflates / deflates).

### 4. Clean categories

Explicitly list every family that passed: e.g. "Survivorship: clean — universe is a fixed historical list loaded from data/universe_2015.csv."

### 5. Missing tests

Be specific, not "add tests." Examples:
- a leakage guard asserting `FEATURE_COLS` is disjoint from every negative-shift / label column;
- a split-order test asserting the scaler is fit only on rows before `train_end`;
- a golden test: shuffle the input rows and assert the reported metric collapses toward zero (a real out-of-sample metric should not survive shuffling if the pipeline is honest — if it does, the split is leaking);
- a cost-sensitivity test asserting Sharpe drops monotonically as the cost parameter rises from 0;
- a deflated-Sharpe test asserting the reported Sharpe exceeds the expected-max bar for the recorded N.

### 6. Verdict

Exactly one of **results plausible / results inflated / results invalid**, with a one-line justification tied to the findings and, where computed, the deflated or cost-adjusted re-estimate.

## Constraints

- Confirm scanner hits in context before ranking them P0 — regex catches candidates.
- Do not drift into general code style, frontend, or deployment review; this skill judges whether the numbers are trustworthy.
- Prefer file-level, number-level evidence over academic commentary.
- Honor Veer's rules: validate against benchmarks, never silently drop data — a blanket `dropna()` that removes rows is itself a finding, and missing data must be handled explicitly.
