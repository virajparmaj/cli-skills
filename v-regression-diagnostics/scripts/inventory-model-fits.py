#!/usr/bin/env python3
"""Inventory statsmodels/scipy fits and tests for diagnostic coverage.

Deterministic half of the v-regression-diagnostics skill. Scans .py and .ipynb
for regression/test call sites and records, per file: model type (OLS/GLM/Logit/
etc.), the cov_type argument (robust vs classical SEs), which diagnostic tests
appear anywhere in the file (Breusch-Pagan, Durbin-Watson, VIF, Jarque-Bera),
the hypothesis tests used (ttest, mannwhitneyu, chi2), and a fit-count vs
reported-result proxy for p-hacking smells.

Pure stdlib, Python 3.11+. Read-only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build",
             "dist", ".ipynb_checkpoints"}

MODELS = re.compile(r"\b(OLS|GLM|Logit|Probit|WLS|GLS|MixedLM|Poisson|"
                    r"NegativeBinomial|QuantReg|RLM|MarkovRegression)\b")
FIT_CALL = re.compile(r"\.fit\(")
COV_TYPE = re.compile(r"cov_type\s*=\s*['\"]([A-Za-z0-9_]+)['\"]")
DIAGNOSTICS = {
    "Breusch-Pagan (heterosk.)": re.compile(r"het_breuschpagan|het_white"),
    "Durbin-Watson (autocorr.)": re.compile(r"durbin_watson"),
    "VIF (multicollinearity)": re.compile(r"variance_inflation_factor|\bVIF\b"),
    "Jarque-Bera (normality)": re.compile(r"jarque_bera|jarquebera"),
    "ACF/PACF": re.compile(r"\b(acf|pacf|plot_acf|plot_pacf)\b"),
}
HYP_TESTS = re.compile(r"\b(ttest_ind|ttest_rel|ttest_1samp|mannwhitneyu|"
                       r"wilcoxon|chi2_contingency|chisquare|f_oneway|pearsonr|spearmanr)\b")
SUMMARY = re.compile(r"\.summary\(\)|\.summary2\(\)|\.pvalues|\.tvalues")
HAC = re.compile(r"HAC|Newey|maxlags")


def iter_sources(repo: Path):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = Path(root) / f
            if f.endswith(".py"):
                try:
                    yield p, p.read_text(errors="ignore")
                except OSError:
                    continue
            elif f.endswith(".ipynb"):
                try:
                    nb = json.loads(p.read_text(errors="ignore"))
                except (OSError, json.JSONDecodeError):
                    continue
                cells = []
                for cell in nb.get("cells", []):
                    if cell.get("cell_type") == "code":
                        src = cell.get("source", "")
                        cells.append("".join(src) if isinstance(src, list) else str(src))
                yield p, "\n".join(cells)


def analyze(path: Path, text: str) -> dict | None:
    models = sorted(set(MODELS.findall(text)))
    hyp = sorted(set(HYP_TESTS.findall(text)))
    if not models and not hyp:
        return None
    fits = len(FIT_CALL.findall(text))
    summaries = len(SUMMARY.findall(text))
    cov = sorted(set(COV_TYPE.findall(text)))
    diags = [name for name, pat in DIAGNOSTICS.items() if pat.search(text)]
    is_timeseries = bool(re.search(r"(to_datetime|DatetimeIndex|parse_dates|resample|"
                                   r"\.shift\(|lag)", text))
    return {
        "file": str(path.name if path.suffix == ".ipynb" else path),
        "models": models,
        "hypothesis_tests": hyp,
        "fit_calls": fits,
        "summary_calls": summaries,
        "cov_type": cov or (["(classical default)"] if models else []),
        "has_HAC": bool(HAC.search(text)),
        "diagnostics_present": diags,
        "looks_timeseries": is_timeseries,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_path", nargs="?", default=".", help="target repo (default .)")
    ap.add_argument("--json", action="store_true", help="emit raw JSON")
    args = ap.parse_args()

    repo = Path(args.repo_path).resolve()
    if not repo.exists():
        print(f"no such path: {repo}", file=sys.stderr)
        return 1

    records = []
    for path, text in iter_sources(repo):
        rec = analyze(path, text)
        if rec:
            records.append(rec)

    if args.json:
        print(json.dumps(records, indent=1))
        return 0

    print(f"=== regression/test inventory ({len(records)} files) ===\n")
    if not records:
        print("No statsmodels/scipy model fits or hypothesis tests found.")
        return 0
    for r in records:
        print(f"# {r['file']}")
        if r["models"]:
            print(f"  models: {', '.join(r['models'])}   cov_type: {', '.join(r['cov_type'])}")
        if r["hypothesis_tests"]:
            print(f"  tests: {', '.join(r['hypothesis_tests'])}")
        print(f"  fit calls: {r['fit_calls']}   summary/pvalue reads: {r['summary_calls']}")
        if r["fit_calls"] > 2 * max(r["summary_calls"], 1):
            print(f"  P-HACKING SMELL: {r['fit_calls']} fits but few reported summaries")
        missing = [d for d in DIAGNOSTICS if d not in r["diagnostics_present"]]
        if r["models"]:
            print(f"  diagnostics present: {', '.join(r['diagnostics_present']) or '(none)'}")
            if missing:
                print(f"  diagnostics MISSING: {', '.join(missing)}")
            if r["looks_timeseries"] and not r["has_HAC"]:
                print("  TIME SERIES without HAC/Newey-West SEs -> autocorrelated residuals likely under-corrected")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
