#!/usr/bin/env python3
"""Inventory every signal defined vs every metric reported, and compute the
multiple-testing (deflated Sharpe) threshold deterministically.

Read-only. This turns "how many signals did we actually try?" and "does this
Sharpe survive correction for N trials?" into counted facts, not judgment.

What it does:
  1. Walks *.py/*.ipynb and counts distinct signal definitions (registry entries,
     def signal_*/compute_*/factor_* functions, add_signal("...") calls, SIGNALS dicts).
  2. Extracts reported metrics (sharpe/ic/sortino/cagr/hit_rate) and their literals.
  3. Extracts declared split dates so in-sample vs out-of-sample can be judged.
  4. Given N signals tried and a reported Sharpe, prints the Deflated-Sharpe /
     Bonferroni thresholds that Sharpe must beat to be plausibly real.
  5. If a returns series (csv/parquet with a 'return'/'pnl' column) is found,
     computes naive Sharpe vs autocorrelation-adjusted (Newey-West style) Sharpe.

Usage:
    scripts/signal-inventory.py [repo_path] [--reported-sharpe X] [--trials N]
    # repo_path defaults to "."; --trials overrides the auto-counted signal count.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ipynb_checkpoints", "venv", ".venv", "env", ".env",
    "site-packages", "dist", "build", ".next", ".cache", "target",
}

# Ways a signal/factor gets defined in a research repo.
SIGNAL_DEF_PATTERNS = [
    re.compile(r"\bdef\s+(signal_[A-Za-z0-9_]+)\s*\("),
    re.compile(r"\bdef\s+(compute_[A-Za-z0-9_]+)\s*\("),
    re.compile(r"\bdef\s+(factor_[A-Za-z0-9_]+)\s*\("),
    re.compile(r"\bdef\s+(alpha_[A-Za-z0-9_]+)\s*\("),
    re.compile(r"add_signal\(\s*['\"]([A-Za-z0-9_\- ]+)['\"]"),
    re.compile(r"register_signal\(\s*['\"]([A-Za-z0-9_\- ]+)['\"]"),
    re.compile(r"@signal\b"),  # decorator form, counted separately below
]

# SIGNALS = {"a": ..., "b": ...} style registries — count the string keys.
REGISTRY_BLOCK = re.compile(
    r"(SIGNALS|FACTORS|ALPHAS|SIGNAL_REGISTRY)\s*[:=]\s*[\{\[]", re.IGNORECASE
)

METRIC_PATTERNS = [
    re.compile(r"\b(sharpe(?:_ratio)?)\b\s*[=:]\s*(-?\d+\.?\d*)", re.IGNORECASE),
    re.compile(r"\b(sortino)\b\s*[=:]\s*(-?\d+\.?\d*)", re.IGNORECASE),
    re.compile(r"\b(information[_ ]?coefficient|\bic\b)\b\s*[=:]\s*(-?\d+\.?\d*)",
               re.IGNORECASE),
    re.compile(r"\b(cagr|annual[_ ]?return)\b\s*[=:]\s*(-?\d+\.?\d*)", re.IGNORECASE),
    re.compile(r"\b(hit[_ ]?rate|win[_ ]?rate)\b\s*[=:]\s*(-?\d+\.?\d*)", re.IGNORECASE),
    re.compile(r"\b(max[_ ]?drawdown|maxdd)\b\s*[=:]\s*(-?\d+\.?\d*)", re.IGNORECASE),
]

DATE_ASSIGN = re.compile(
    r"(train_end|test_start|train_start|test_end|split_date|cutoff|is_end|oos_start)"
    r"\s*=\s*['\"]?(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)

TURNOVER = re.compile(r"\b(turnover|capacity|adv|avg_daily_volume)\b", re.IGNORECASE)
NW_ADJUST = re.compile(r"\b(newey|newey_west|neweywest|block_bootstrap|hac)\b",
                       re.IGNORECASE)


@dataclass
class Inventory:
    signal_names: set[str] = field(default_factory=set)
    decorator_signals: int = 0
    registry_keys: set[str] = field(default_factory=set)
    metrics: list[tuple[str, str, str, float]] = field(default_factory=list)  # file,line,name,val
    split_dates: list[tuple[str, int, str, str]] = field(default_factory=list)
    turnover_mentions: int = 0
    nw_mentions: int = 0


def iter_source(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_dir() or any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.suffix == ".py":
            yield path, False
        elif path.suffix == ".ipynb":
            yield path, True


def notebook_source(path: Path) -> str:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return ""
    parts = []
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", "")
        parts.append("".join(src) if isinstance(src, list) else str(src))
    return "\n".join(parts)


def collect_registry_keys(text: str) -> set[str]:
    """Find SIGNALS = {...} blocks and pull out the top-level string keys."""
    keys: set[str] = set()
    for m in REGISTRY_BLOCK.finditer(text):
        start = m.end() - 1
        depth = 0
        block_chars = []
        for ch in text[start:start + 20000]:
            block_chars.append(ch)
            if ch in "{[":
                depth += 1
            elif ch in "}]":
                depth -= 1
                if depth == 0:
                    break
        block = "".join(block_chars)
        keys.update(re.findall(r"['\"]([A-Za-z0-9_\- ]+)['\"]\s*:", block))
    return keys


def scan(root: Path) -> Inventory:
    inv = Inventory()
    for path, is_nb in iter_source(root):
        rel = str(path.relative_to(root))
        text = notebook_source(path) if is_nb else _safe_read(path)
        if not text:
            continue

        for pat in SIGNAL_DEF_PATTERNS:
            for m in pat.finditer(text):
                if m.re.pattern == r"@signal\b":
                    inv.decorator_signals += 1
                elif m.groups():
                    inv.signal_names.add(m.group(1))

        inv.registry_keys |= collect_registry_keys(text)

        for i, line in enumerate(text.splitlines(), start=1):
            for pat in METRIC_PATTERNS:
                for m in pat.finditer(line):
                    name = m.group(1).lower().replace(" ", "_")
                    try:
                        val = float(m.group(2))
                    except (TypeError, ValueError):
                        continue
                    inv.metrics.append((rel, i, name, val))
            for m in DATE_ASSIGN.finditer(line):
                inv.split_dates.append((rel, i, m.group(1).lower(), m.group(2)))

        inv.turnover_mentions += len(TURNOVER.findall(text))
        inv.nw_mentions += len(NW_ADJUST.findall(text))
    return inv


def deflated_sharpe_threshold(n_trials: int, n_obs: int | None = None) -> float:
    """Expected maximum Sharpe under the null of zero skill across n_trials.

    Uses the Bailey/Lopez de Prado expected-max approximation for iid N(0,1)
    Sharpe estimates: E[max] ~ (1-g)*z(1-1/N) + g*z(1-1/(N*e)), g = Euler-Mascheroni.
    A reported (annualized-to-per-trial-normalized) Sharpe must exceed this to be
    distinguishable from the best of N pure-noise strategies.
    """
    if n_trials <= 1:
        return 0.0
    gamma = 0.5772156649015329  # Euler-Mascheroni
    z1 = _inv_norm_cdf(1.0 - 1.0 / n_trials)
    z2 = _inv_norm_cdf(1.0 - 1.0 / (n_trials * math.e))
    e_max = (1.0 - gamma) * z1 + gamma * z2
    # e_max is in units of the standard error of the Sharpe estimate. When we know
    # the sample length we can scale to a per-period Sharpe; otherwise return e_max
    # in SE units and let the model contextualize.
    if n_obs and n_obs > 1:
        return e_max / math.sqrt(n_obs)
    return e_max


def bonferroni_z(n_trials: int, alpha: float = 0.05) -> float:
    """Two-sided Bonferroni-corrected critical z for n_trials tests at family alpha."""
    if n_trials < 1:
        n_trials = 1
    per = alpha / n_trials
    return _inv_norm_cdf(1.0 - per / 2.0)


def _inv_norm_cdf(p: float) -> float:
    """Acklam's rational approximation of the inverse standard normal CDF (stdlib only)."""
    if p <= 0.0:
        return -math.inf
    if p >= 1.0:
        return math.inf
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def find_returns_series(root: Path):
    """Return (path, values:list[float]) for the first return/pnl column found. pandas optional."""
    try:
        import pandas as pd
    except ImportError:
        return None
    for path in sorted(root.rglob("*")):
        if path.is_dir() or any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.suffix.lower() not in {".csv", ".parquet", ".feather"}:
            continue
        if path.stat().st_size > 100_000_000:
            continue
        try:
            if path.suffix.lower() == ".csv":
                df = pd.read_csv(path, nrows=500_000)
            elif path.suffix.lower() == ".parquet":
                df = pd.read_parquet(path)
            else:
                df = pd.read_feather(path)
        except Exception:
            continue
        for col in df.columns:
            name = str(col).lower()
            if any(k in name for k in ("return", "ret", "pnl", "strategy")):
                s = pd.to_numeric(df[col], errors="coerce").dropna()
                if len(s) >= 30 and s.abs().mean() < 1.0:  # looks like fractional returns
                    return str(path.relative_to(root)), col, s.tolist()
    return None


def sharpe_naive_and_adjusted(returns: list[float], lags: int = 5):
    """Return (naive_sharpe_annualized, nw_adjusted_sharpe, autocorr_lag1)."""
    n = len(returns)
    if n < 2:
        return None
    mean = sum(returns) / n
    var = sum((r - mean) ** 2 for r in returns) / (n - 1)
    if var <= 0:
        return None
    sd = math.sqrt(var)
    naive = (mean / sd) * math.sqrt(252)

    # Newey-West HAC variance inflation using Bartlett kernel on the return series.
    def autocov(k: int) -> float:
        return sum((returns[t] - mean) * (returns[t - k] - mean)
                   for t in range(k, n)) / n

    g0 = autocov(0)
    if g0 <= 0:
        return naive, naive, 0.0
    lag1 = autocov(1) / g0
    hac = g0
    max_lag = min(lags, n - 1)
    for k in range(1, max_lag + 1):
        w = 1.0 - k / (max_lag + 1)
        hac += 2.0 * w * autocov(k)
    if hac <= 0:
        return naive, naive, lag1
    adj_sd = math.sqrt(hac)
    adjusted = (mean / adj_sd) * math.sqrt(252)
    return naive, adjusted, lag1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_path", nargs="?", default=".")
    parser.add_argument("--reported-sharpe", type=float, default=None,
                        help="the headline Sharpe to test against the deflated threshold")
    parser.add_argument("--trials", type=int, default=None,
                        help="override the auto-counted number of signals tried")
    args = parser.parse_args()

    root = Path(args.repo_path).resolve()
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 1

    inv = scan(root)

    defined = set(inv.signal_names) | set(inv.registry_keys)
    n_defined = len(defined) + inv.decorator_signals
    n_trials = args.trials if args.trials is not None else max(n_defined, 1)

    print("=== signal inventory ===")
    print(f"repo: {root}")
    print(f"distinct signal/factor definitions: {len(defined)}")
    if defined:
        print("  " + ", ".join(sorted(defined)[:40]))
    if inv.decorator_signals:
        print(f"@signal-decorated functions (names not captured): {inv.decorator_signals}")
    print(f"signals tried (N used for multiple-testing): {n_trials}")
    print()

    print("=== reported metrics (file:line name = value) ===")
    if not inv.metrics:
        print("none — no sharpe/ic/sortino/cagr literals found in code")
    for rel, line, name, val in inv.metrics:
        print(f"{rel}:{line} {name} = {val}")
    reported_sharpes = [v for (_, _, n, v) in inv.metrics if "sharpe" in n]
    print()

    print("=== tried vs reported ===")
    n_reported_metrics = len(inv.metrics)
    print(f"signals defined: {len(defined)}   metric literals reported: {n_reported_metrics}")
    if len(defined) > max(len(reported_sharpes), 1) * 3 and reported_sharpes:
        print("WARNING: many signals defined but few Sharpes reported — possible")
        print("         cherry-picking / silent multiple testing. Confirm how many")
        print("         signals were evaluated before the reported one was chosen.")
    print()

    print("=== declared split boundaries (in-sample vs out-of-sample) ===")
    if not inv.split_dates:
        print("none found — cannot confirm metrics were computed out-of-sample")
    for rel, line, name, val in inv.split_dates:
        print(f"{rel}:{line} {name} = {val}")
    print()

    print("=== hygiene mentions ===")
    print(f"turnover/capacity references: {inv.turnover_mentions} "
          f"({'present' if inv.turnover_mentions else 'MISSING — cost/capacity unmodeled?'})")
    print(f"Newey-West / block-bootstrap references: {inv.nw_mentions} "
          f"({'present' if inv.nw_mentions else 'MISSING — Sharpe likely autocorr-inflated?'})")
    print()

    print("=== deflated-Sharpe threshold (multiple testing) ===")
    ds_se = deflated_sharpe_threshold(n_trials)
    bonf = bonferroni_z(n_trials)
    print(f"N (signals tried) = {n_trials}")
    print(f"expected max Sharpe under the null (best of N noise strategies):")
    print(f"  ~ {ds_se:.3f} standard errors of the Sharpe estimate")
    print(f"Bonferroni critical z at family alpha=0.05: {bonf:.3f}")
    print("  A reported Sharpe's t-stat (Sharpe * sqrt(n_obs)) must exceed this z,")
    print("  and the Sharpe itself must clear the expected-max bar above, to survive.")

    candidate = args.reported_sharpe
    if candidate is None and reported_sharpes:
        candidate = max(reported_sharpes)
        print(f"(using max reported Sharpe from code: {candidate})")
    if candidate is not None:
        verdict = "CLEARS expected-max noise bar" if candidate > ds_se \
            else "DOES NOT clear expected-max noise bar — likely a false discovery"
        print(f"reported Sharpe {candidate}: {verdict}")
        print("  Note: the SE-unit bar needs sample length n_obs to become a Sharpe")
        print("  number. Provide n_obs from the dataset span to finish the comparison.")
    else:
        print("no reported Sharpe supplied or found — pass --reported-sharpe X to test.")
    print()

    print("=== autocorrelation-adjusted Sharpe (from returns series if found) ===")
    found = find_returns_series(root)
    if not found:
        print("no returns/pnl series found (or pandas unavailable).")
        print("hint: pip install pandas pyarrow  # to enable Newey-West adjustment")
    else:
        rel, col, vals = found
        res = sharpe_naive_and_adjusted(vals)
        if res is None:
            print(f"{rel} column '{col}': could not compute (zero variance / too short)")
        else:
            naive, adjusted, lag1 = res
            print(f"{rel} column '{col}' (n={len(vals)}):")
            print(f"  naive annualized Sharpe:            {naive:.3f}")
            print(f"  Newey-West adjusted Sharpe:         {adjusted:.3f}")
            print(f"  lag-1 autocorrelation of returns:   {lag1:.3f}")
            if abs(naive) > 1e-9:
                shrink = (1 - adjusted / naive) * 100
                print(f"  autocorrelation inflation removed:  {shrink:.1f}% of the Sharpe")
            if lag1 > 0.1:
                print("  WARNING: positive return autocorrelation inflates naive Sharpe;")
                print("           the adjusted number is the honest one.")
    print()

    print("=== how to read this ===")
    print("- 'signals tried' (N) drives every multiple-testing bar. If sessions kept")
    print("  adding signals, the real N is larger than what one file shows — ask.")
    print("- A Sharpe that beats the naive t-stat but not the deflated/Bonferroni bar")
    print("  is consistent with pure luck across N trials, not skill.")
    print("- Missing split dates => metrics may be in-sample; treat them as upper bounds.")
    print("- Missing turnover/Newey-West handling => costs and autocorrelation likely")
    print("  unaccounted for; the honest Sharpe is lower than reported.")
    return 0


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


if __name__ == "__main__":
    raise SystemExit(main())
