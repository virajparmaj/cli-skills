# Time-Series Leakage Audit Playbook

One skill for the whole leakage family: statistic contamination (fit before
split), temporal ordering (shuffle / lookahead windows), and the domain-specific
regime traps. Verdict per pipeline: **LEAKING / CLEAN / UNVERIFIED**.

## Leakage classes

### 1. Fit-on-full-data contamination
`StandardScaler`/`imputer`/`encoder`/`PCA`/`SelectKBest` `.fit` or
`.fit_transform` executed **before** `train_test_split`, or on the full `X`.
The test set's statistics leak into training.
- Fix: wrap transforms in a `sklearn.Pipeline` and fit only inside CV, or fit on
  train and `transform` test.

### 2. Temporal ordering violations
- `train_test_split(..., shuffle=True)` (the default) on datetime-indexed data.
- plain `KFold`/`StratifiedKFold` where `TimeSeriesSplit` is required.
- features from `.shift(-n)` (future rows), `rolling(center=True)`, or
  `resample` that aggregates across the split boundary.
- Fix: `shuffle=False`, `TimeSeriesSplit` (or walk-forward with an embargo gap),
  and only backward-looking windows.

### 3. Regime / credit-risk domain traps (statsmodels)
- `smoothed_marginal_probabilities` used as historical features — smoothing
  conditions on the **full sample**; use **filtered** probabilities for features.
- HMM/KMeans regimes fit on the whole history then mapped backward — refit with
  an expanding window.
- macro variables joined at publication-lag-zero (using GDP the quarter it
  describes, not when it was released) — add a release-lag column before the join.
- Fix direction is always "make the feature only see the past".

## Flow

1. Run `scripts/find-split-leakage.py <repo>`. It emits HIGH-SIGNAL FLAGS plus a
   per-file inventory: split calls and their `shuffle`, CV type, `.fit` lines
   relative to the split, forward-reaching windows, regime signatures, and
   whether a stationarity check exists.
2. For each pipeline, trace the flagged lines in context and decide the verdict.
3. Report findings with file:line, the exact statistic/row that leaks, why the
   score is optimistic, and the smallest fix.

## Output contract

- Per pipeline: one verdict line — `LEAKING` / `CLEAN` / `UNVERIFIED` (couldn't
  trace the data flow).
- Then severity-ranked findings: `file:line | class | what leaks | smallest fix`.
- Label **Confirmed from code** (you traced the flow) vs **Strongly inferred**
  (flag only). A `shuffle=DEFAULT` on datetime data is Confirmed once you verify
  the frame is time-indexed.
- Include one ready-to-paste corrected split/pipeline snippet where a fix is
  non-trivial.
- If a pipeline is clean, say so explicitly — do not manufacture leakage.

## Not this skill's job

- Data cleanliness (nulls, dupes, class imbalance) → `v-dataset`.
- Whether the metric math is right → `v-metric-math`.
- Regression inference validity (p-values, robust SEs) → `v-regression-diagnostics`.
- Serving/inference skew → `v-ml` / `v-ml-deploy`.
