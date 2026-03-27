---
name: v-ml
description: "Audit ML inference paths for correctness, serving reliability, and operational safety. Use for FastAPI or Python model backends with Vite, React, and TypeScript frontends, scoring endpoints, model-card services, CSV-to-score flows, fallback heuristics, multi-model routing, or demo-only apps preparing for real inference. Key capabilities include classifying inference topology (backend-only, hybrid, demo-only), tracing artifacts, loaders, endpoints, and frontend consumers, detecting training-serving feature skew, fallback divergence, preprocessing or post-processing drift, artifact path fragility, dishonest health checks, cold start, CORS, env, and dependency risks, and producing a severity-ranked audit with concrete fixes and tests. Trigger on requests like audit ML inference reliability, review scoring endpoint correctness, check model serving risks, find training-serving skew, assess demo-to-production readiness, or write an ML audit report for this repo."
---

# ML Inference Audit

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Quick start

1. Inspect the repo before judging it. Read these if present, in order:
   - `CLAUDE.md`
   - `README.md`
   - `notes/13_prompt_context.md`
   - `notes/03_architecture.md`
   - `notes/06_api_contracts.md`
   - `notes/11_known_issues.md`
   - `notes/10_deployment.md`
   - `.env.example` or `.env`
2. Classify the inference topology before deep analysis:
   - `backend-only`
   - `hybrid`
   - `frontend-only / demo`
3. Map the full inference path from model artifact to user-facing output. Start with:
   - `backend/artifacts/`, `models/`, `*.joblib`, `*.pkl`, `*.onnx`, `*.pt`
   - FastAPI loaders and routes in `backend/*.py`
   - frontend API code in `src/services/api.ts`, `src/lib/api.ts`, or adapter files
   - feature alignment, CSV parsing, and fallback logic in `src/lib/`, `src/utils/`, `src/contexts/`, and route components
4. Load [Audit Playbook](references/audit-playbook.md) and follow its checklist for what to inspect, how to grade severity, and how to format the report.
5. If the repo uses a Vite + FastAPI ML stack, read [Workspace Patterns](references/workspace-patterns.md) before finalizing the audit.

## Output rules

- Cite exact file paths and line ranges for verified findings.
- Keep verified findings separate from unverified concerns.
- If a category is clean, say so explicitly.
- Do not report generic ML best practices unless they tie to code evidence in the repo.
- Do not duplicate issues already documented in `notes/11_known_issues.md`; reference them and assess whether they are resolved.
- Separate correctness risks from operational risks in the final report.
- End with specific missing tests, not vague "add tests" advice.

## Variant triggers

Read the matching section in [Audit Playbook](references/audit-playbook.md) when the repo has:

- multiple models or band-specific routing
- CSV upload or batch scoring paths
- demo or mock models with no backend
- Python model artifacts whose dependency versions must stay exact

## Additional checks

- ONNX Runtime or TensorFlow Serving compatibility when non-joblib formats are present
- Model A/B testing infrastructure and traffic splitting correctness
- Data drift monitoring or concept drift detection mechanisms
- Model explainability endpoints (SHAP, LIME) if present — verify they match the production model
