# Deflated Sharpe & Multiple Testing

The statistical-inflation half of the audit. A Sharpe ratio is not evidence on
its own: it is inflated by how many strategies were tried, by autocorrelation in
returns, and by short samples. This reference is loaded when the audit touches
signal counting, deflated Sharpe, or overlapping samples.

## Why a raw Sharpe lies

- **Multiple testing** — try enough signals and one clears any bar by luck. The
  more trials `N`, the higher the Sharpe you need to believe the best one.
- **Autocorrelation** — positively autocorrelated returns understate volatility,
  inflating the annualized Sharpe.
- **Short samples** — the Sharpe estimator has large variance; a high point
  estimate over 200 observations can be indistinguishable from zero.
- **Overlapping samples** — overlapping return windows inflate t-stats by
  reducing the effective number of independent observations.

## The numbers the script computes

`scripts/signal-inventory.py` prints:

- **signals tried vs reported** — count of distinct signals/parameterizations
  defined in the repo vs the number whose metrics are reported. A large gap is
  the multiple-testing exposure.
- **deflated / Bonferroni threshold** — the Sharpe bar the best signal must clear
  given `N` trials. Read it as: "with N signals tried, a Sharpe below this bar is
  consistent with luck."
- **autocorrelation-adjusted Sharpe** — the naive Sharpe re-estimated with a
  Newey-West / Lo adjustment for serial correlation.

## Deflated Sharpe Ratio (DSR) — the idea

DSR asks: given `N` trials, the observed Sharpe `SR`, the sample length `T`, and
the skew/kurtosis of returns, what is the probability the true Sharpe is > 0?

- Inputs: `SR_observed`, number of trials `N`, sample length `T`, returns skew
  `γ3`, kurtosis `γ4`.
- The expected maximum Sharpe under the null grows with `N` — that expected
  maximum is the bar. Report DSR as a probability; below ~0.95 is not convincing.
- When the script cannot compute the full DSR (missing returns series), fall back
  to the Bonferroni-style bar and label the finding **Strongly inferred**.

## How to grade it

- **P0** — the reported Sharpe fails the deflated bar: results invalid on
  statistical grounds alone.
- **P1** — autocorrelation-inflated Sharpe with no adjustment, or in-sample
  metrics reported as out-of-sample.
- **P2** — overlapping samples inflating t-stats; many trials with no correction
  mentioned but the best signal still clears the bar.
- **P3** — trials count not recoverable from the repo; note it as a provenance
  gap and ask the developer for the true `N`.

## Smallest fixes

- Report the deflated Sharpe / DSR alongside the raw Sharpe.
- Pre-register the signal set, or apply a Bonferroni/BH correction to the trial
  set.
- Use Lo's autocorrelation-adjusted Sharpe for serially correlated returns.
- Use non-overlapping windows, or correct the effective sample size.

## Boundary

This reference is about whether the *number* survives scrutiny. The mechanical
bugs (lookahead, leakage, fantasy fills) are in [audit-playbook.md](audit-playbook.md).
