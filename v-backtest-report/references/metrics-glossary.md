# Backtest Metrics Glossary

What each metric in the report means, its convention, and the caveat to state
when you interpret it. Numbers come from `scripts/compute-metrics.py` — never
retype them; this glossary is only for the interpretation lines.

## Return / risk

- **Total return** — cumulative return over the sample. Caveat: says nothing
  about the path; pair with drawdown.
- **CAGR** — geometric annualized return. Convention: `(1+total)^(252/n_days)-1`
  for daily data. Caveat: sensitive to start/end dates (period dependence).
- **Volatility (annualized)** — std of returns × √(periods/yr). Convention:
  √252 daily equity, √365/√8760 crypto. Caveat: assumes iid; autocorrelated
  returns understate it.
- **Sharpe** — excess-return mean / std, annualized. Caveat: inflated by
  autocorrelation and by multiple testing; a Sharpe with no deflation is a
  headline, not a verdict — see `v-backtest-audit`.
- **Sortino** — like Sharpe but downside deviation only. Caveat: unstable when
  few negative returns.
- **Calmar** — CAGR / |max drawdown|. Caveat: dominated by the single worst
  drawdown; period dependent.

## Drawdown / path

- **Max drawdown** — largest peak-to-trough decline. Convention: on the equity
  curve (cumulative), reported as a negative number or magnitude — state which.
- **Time in drawdown / recovery** — how long underwater. Caveat: the metric most
  investors actually feel; report it.

## Trading realism

- **Turnover** — traded notional / capital per period. Caveat: high turnover +
  omitted costs is the usual source of a fantasy Sharpe.
- **Transaction costs / slippage assumed** — state the bps used and whether
  funding (for perps) is included. Caveat: zero-cost fills invalidate the result.
- **Hit rate / avg win-loss** — descriptive only; a high hit rate with negative
  expectancy still loses.

## Benchmark / attribution

- **Benchmark return** — what buy-and-hold or the index did over the same window.
  Caveat: a strategy that trails its benchmark is not "profitable" in any useful
  sense.
- **Information ratio** — active return / tracking error vs the benchmark.

## Interpretation labels (use per line)

- `Confirmed from code` — the number is from the metrics script or a cited file
  line.
- `Strongly inferred` — a reasoned reading of the computed numbers.
- `Not found` — could not be located; do not guess.

For whether the Sharpe survives multiple testing and autocorrelation, this skill
only *reports* the number; the validity judgment is `v-backtest-audit`'s job.
