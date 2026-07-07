#!/usr/bin/env bash
#
# Discover hand-rolled metric implementations and their convention signals.
#
# Read-only. Greps the target repo for metric function definitions and the
# convention choices that silently change their results: annualization
# constants, ddof arguments, quantile calls, and simple-vs-log return math.
# The v-metric-math skill reads this output to decide which functions to
# benchmark and which convention a mismatch points to.

set -euo pipefail

repo_path="${1:-.}"
cd "$repo_path"

if ! command -v grep >/dev/null 2>&1; then
  echo "grep not available" >&2
  exit 1
fi

# Prefer ripgrep when present; fall back to grep -r.
if command -v rg >/dev/null 2>&1; then
  SEARCH() { rg --no-heading --line-number --color never "$@" 2>/dev/null || true; }
else
  SEARCH() {
    # shellcheck disable=SC2068
    local pat="$1"; shift
    grep -rEn --include='*.py' --include='*.ipynb' "$pat" . $@ 2>/dev/null || true
  }
fi

section() { printf '\n=== %s ===\n' "$1"; }

section "metric function definitions"
SEARCH 'def[[:space:]]+([a-z_]*(sharpe|sortino|drawdown|calmar|var|cvar|vol|volatility|beta|alpha|auc|roc|brier|calibrat|log_?loss|rmse|mae|mape|r2|accuracy|precision|recall|f1)[a-z_]*)[[:space:]]*\('

section "annualization constants (252 equity / 12 monthly / 365 / 8760 crypto)"
SEARCH '(\* *|sqrt\(|\*\* *0?\.5.*)(252|365|8760|1095|12)\b'

section "ddof / degrees-of-freedom choices (population vs sample std)"
SEARCH 'ddof[[:space:]]*='

section "quantile / percentile calls (VaR interpolation method matters)"
SEARCH '\.(quantile|percentile)\(|np\.(quantile|percentile)\('

section "return-type math (simple pct_change vs log returns)"
SEARCH 'pct_change\(|np\.log\(.*(/|shift)|diff\(\)'

section "sign / clipping conventions on losses"
SEARCH '(abs\(|-1[[:space:]]*\*|\.clip\(|np\.minimum\(|np\.maximum\()'

section "cumulative / drawdown base (prices vs cumulative returns)"
SEARCH 'cummax\(|cumprod\(|cumsum\(|running_max|peak'

printf '\n(discovery is a lead list, not a verdict; the skill confirms each hit in context)\n'
