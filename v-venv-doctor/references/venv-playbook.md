# venv Doctor Playbook (Apple Silicon)

Diagnose per-project Python environments on an M-series Mac and emit an ordered
fix list. Veer's rule: always a per-project venv; global interpreter is
`~/.venvs/global/bin/python` (3.11.14) and should not be the active env for
project work.

## What the script gathers

`scripts/venv-doctor.sh <repo>` reports: project venv presence and whether the
active env is the global one, interpreter arch (arm64 vs x86_64/Rosetta) and
Python version, pip drift vs `requirements.txt` and vs the pinned ML stack,
xgboost import + brew libomp status, and a core-stack import smoke test.

## Common M1 failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `xgboost` import fails: `Library not loaded: libomp` | libomp missing | `brew install libomp` |
| numpy/scipy compiling from source (slow install) | pip fetching sdist not arm64 wheel | upgrade pip; `pip install --only-binary=:all: <pkg>` |
| `machine() == x86_64` on an M-series | shell/Python under Rosetta | reinstall a native arm64 Python; check terminal "Open using Rosetta" is off |
| accidental global interpreter | no project venv activated | `python3 -m venv .venv && source .venv/bin/activate` |
| version drift vs pinned stack | ad-hoc installs | reinstall the pinned versions |

## Pinned ML stack

```
numpy==2.1.2  pandas==2.2.3  scipy==1.14.1
scikit-learn==1.5.2  xgboost==2.1.0  statsmodels==0.14.4
matplotlib==3.9.2  seaborn==0.13.2  structlog
```

## Output contract (strict)

1. One status table — nothing fancy:

   ```
   check                     | result            | pass/fail
   project venv present      | .venv/            | PASS
   interpreter arch          | arm64             | PASS
   python version            | 3.11.14           | PASS
   xgboost import            | libomp missing    | FAIL
   pinned stack              | 2 drifted         | WARN
   ```

2. Then exactly one fenced `bash` code block of ordered fix commands — most
   fundamental first (create/activate venv → brew libomp → reinstall pinned
   stack) — and nothing after it:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   brew install libomp
   pip install numpy==2.1.2 pandas==2.2.3 scipy==1.14.1 \
     scikit-learn==1.5.2 xgboost==2.1.0 statsmodels==0.14.4 \
     matplotlib==3.9.2 seaborn==0.13.2 structlog
   ```

Only include commands that address a real FAIL/WARN from the table. If
everything passes, say "environment healthy" and emit no bash block.
