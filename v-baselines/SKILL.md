---
name: v-baselines
description: "Run an honest baseline model zoo — Dummy, Linear, RandomForest, XGBoost — under one shared CV protocol and report whether the fancy model actually beats the baselines. Use before trusting a tuned model on any CSV/Parquet dataset with a target column. Key capabilities: auto-detect classification vs regression and datetime index (TimeSeriesSplit vs StratifiedKFold), wrap every model in a Pipeline sharing one splitter and seed so preprocessing never leaks, pick the right metric (roc_auc / accuracy / r2), print a model-by-model results table with fit times, and give a verdict grounded in CV noise (does the best model beat dummy by more than one std, does it beat the linear baseline). Appends results to experiments/runs.csv when present. Trigger phrases: run baselines on this dataset, compare xgboost against sklearn baselines, is my model actually beating a dummy, set up a model comparison harness, does this model beat a simple baseline, what's my baseline score."
---

# Honest Baseline Harness

Prove the tuned model earns its complexity — beat a dummy and a linear baseline under one fair CV protocol, or don't bother.

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

## Quick flow

1. Read repo context if present: `CLAUDE.md`, `README.md`, and the training data location.
2. Run `scripts/run-baselines.py <data> <target>` — add `--datetime-col <col>` to force walk-forward, `--folds N`, and `--repo .` to append to the ledger.
3. Load [references/baselines-playbook.md](references/baselines-playbook.md) for the protocol, the zoo, and how to read the verdict.
4. Report the results table and verdict.

## Output contract

- One markdown table: `model | metric mean ± std | fit time`.
- One-paragraph verdict, always relative to the dummy and linear baselines (never a bare "XGBoost got 0.84"):
  - best == dummy → features carry no signal;
  - best beats dummy by ≤ one CV std → not convincing;
  - best (forest/xgboost) doesn't beat linear → ship the simpler model;
  - best beats dummy by > CV std and beats linear → complexity earned.
- If `experiments/runs.csv` exists, append one row per baseline (pairs with `v-run-ledger`).

## Protocol guarantees

- One splitter and seed shared across models; datetime index → `TimeSeriesSplit`.
- Every model in a `Pipeline` so scalers fit inside CV, not on full data.
- Metric auto-picked: binary → roc_auc, multiclass → accuracy, regression → r2.

## Scope boundary

- Data cleanliness before the run → `v-dataset`.
- Whether the user's *own* CV code leaks → `v-timeseries-leakage`.
- Durable run tracking and model cards → `v-run-ledger`.
- This skill answers only: does the model beat a simple baseline?

## Missing dependencies

Requires scikit-learn and pandas; xgboost is optional (skipped with a note if absent). If scikit-learn is missing, the script prints the install command and exits — relay it.

See [references/baselines-playbook.md](references/baselines-playbook.md) for the protocol, zoo, and verdict rules.
