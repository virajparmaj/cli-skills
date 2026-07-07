---
name: v-ml-deploy
description: Audit a Vite/React + FastAPI ML product for inference correctness, serving reliability, and operational safety. Use when reviewing ML-serving repos for model artifacts, joblib/XGBoost/sklearn loading, feature parity, fallback scoring divergence, CSV batch scoring, health-check honesty, cold starts, CORS or VITE_API_URL drift, or demo-to-production readiness. Trigger phrases include "audit the ML path", "review model serving", "check inference reliability", "training/serving skew", "fallback scorer mismatch", "batch scoring contract", and "is this demo ready for a real backend?".
---

# ML Serving Audit

Use this skill for review-only audits of the ML inference path in projects with this common stack:

- Frontend: React 18 + TypeScript + Vite + Tailwind/shadcn
- Backend: FastAPI with `joblib`-loaded sklearn/XGBoost artifacts
- Common layout: `backend/artifacts/`, `src/services/api.ts` or `src/lib/api.ts`, `src/lib/alignFeatures.ts`, `notes/*.md`
- Common deploy shape: Vercel frontend + hosted backend (Render, Railway, Fly, etc.)

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

## Before you audit

1. Stay in review mode. Do not edit files unless the user explicitly asks.
2. Read project context in this order when present:
   - `CLAUDE.md`
   - `README.md`
   - `notes/13_prompt_context.md`
   - `notes/03_architecture.md`
   - `notes/06_api_contracts.md`
   - `notes/11_known_issues.md`
   - `notes/10_deployment.md`
   - `.env.example` or `.env`
3. Run `python3 scripts/map_ml_repo.py /absolute/path/to/project` to map the likely ML files before deeper inspection.
4. Read `references/audit-spec.md` and follow its workflow, failure-mode checklist, report format, severity guide, and add-on clauses.

## Audit workflow

1. Classify the repo first: `backend-only`, `hybrid`, or `frontend-only/demo`.
2. Trace artifact -> model load -> scoring endpoint -> frontend consumption -> fallback/demo path.
3. Check every category in `references/audit-spec.md`. If a category is clean, say so explicitly.
4. Cite exact file paths and line ranges for every confirmed finding.
5. Separate output into:
   - `ML Path Summary`
   - `Verified Findings`
   - `Unverified Concerns`
   - `Missing Tests`
   - ranked `Correctness Risks` vs `Operational Risks`
6. If `notes/11_known_issues.md` already documents a problem, reference it and assess whether the current code still matches it instead of re-reporting it as new.

## Stack-specific expectations

- Treat `src/lib/alignFeatures.ts`, `src/contexts/*.tsx`, demo snapshot builders, and batch upload pages as part of the model contract, not just UI helpers.
- Watch for `VITE_API_URL` defaults pointing at hosted backends and CORS allowlists hardcoded in backend Python.
- Check `backend/requirements.txt` or `pyproject.toml` for partial pinning of model-adjacent dependencies.
- If the repo has multiple models, CSV uploads, or no backend at all, use the matching add-on clause in `references/audit-spec.md`.
- Check for ONNX Runtime or TensorFlow Serving compatibility when non-joblib model formats are present.
- Verify model A/B testing infrastructure and traffic splitting correctness if applicable.
- Check for data drift monitoring or concept drift detection mechanisms.
- Verify model explainability endpoints (SHAP, LIME) match the production model if present.

## Deliverable

Return a review-only report using the section order and severity model from `references/audit-spec.md`. Favor production-facing findings over generic ML commentary.
