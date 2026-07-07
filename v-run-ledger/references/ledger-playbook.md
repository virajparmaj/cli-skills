# Experiment Ledger & Model Card Playbook

Zero-infra experiment tracking: an append-only `experiments/runs.csv` plus
generated model cards. No MLflow, no server. Matches the immutability rule —
rows are only ever appended, never edited.

## Logging a run

```bash
scripts/log-run.py <repo> \
  --data data/train.parquet \
  --model XGBClassifier \
  --params '{"max_depth": 6, "n_estimators": 400, "learning_rate": 0.05}' \
  --metric roc_auc --mean 0.842 --std 0.011 \
  --note "added funding-rate momentum features"
```

Captured per row: `run_id`, UTC time, git SHA + dirty flag, data-file sha256,
model class, params JSON + hash, metric name/mean/std, note. The appended row is
echoed back verbatim (the output contract).

## Answering "which run was best"

Always from the ledger, never from memory:

```bash
scripts/log-run.py <repo> --best roc_auc --top 5        # higher is better
scripts/log-run.py <repo> --best rmse --minimize --top 5 # lower is better
```

## Model card

On "generate a model card", read the winning ledger row plus the training script
and write `models/<run-id>-card.md`:

```markdown
# Model Card: <model> @ <run_id>

- **Run:** <run_id>  (<utc_time>, git <sha> <dirty/clean>)
- **Intended use:** <what this model is for>
- **Data:** <file> (sha256 <data_hash>), provenance -> see data/PROVENANCE/
- **CV protocol:** <splitter, folds, seed>   (Confirmed from code @ file:line)
- **Metrics:** <metric> = <mean> ± <std>
- **Hyperparameters:** <params_json>
- **Assumptions:** <documented assumptions>
- **Known limitations:** <failure modes, out-of-distribution behavior>
```

Every claim labeled **Confirmed from code**, **Strongly inferred**, or **Not
found — fill in manually**, per Veer's documentation rules.

## Output contract

- On log: echo the single appended row verbatim + the ledger path and row count.
- On card: the card path and a one-line summary; never fabricate metrics — pull
  them from the ledger row.
- Refuse to edit or delete existing rows; if a correction is needed, append a new
  row with a note explaining it.

## Pairs with

- `v-baselines` appends its results here when the ledger exists, so baseline vs
  tuned-model comparisons persist across sessions.
- `v-provenance` supplies the data card the model card links to.
