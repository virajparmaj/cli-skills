---
name: v-baselines
description: "Compare Dummy, Linear, RandomForest, and optional XGBoost models under shared, fold-local preprocessing and cross-validation. Use to establish an honest baseline on a tabular dataset with a target column."
---

# Honest Baseline Harness

Prove the tuned model earns its complexity — beat a dummy and a linear baseline under one fair CV protocol, or don't bother.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Keep learned preprocessing inside each cross-validation fold. Use the same rows, folds, scoring convention, and random seed for every model; report errors or non-finite scores. The one-standard-deviation rule below is a descriptive heuristic, not a significance test.

## Quick flow

1. Read repo context if present: `AGENTS.md`, `CLAUDE.md`, `README.md`, and the training data location.
2. Run `scripts/run-baselines.py <data> <target>` — add `--datetime-col <col>` to force walk-forward, `--folds N`, `--task classification|regression` for ambiguous targets, `--gap N` for temporal label overlap, and `--repo .` to append to the ledger.
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
