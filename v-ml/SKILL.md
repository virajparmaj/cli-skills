---
name: v-ml
description: "Audit ML inference paths for correctness, serving reliability, and operational safety. Use for FastAPI or Python model backends with Vite, React, and TypeScript frontends, scoring endpoints, model-card services, CSV-to-score flows, fallback heuristics, multi-model routing, or demo-only apps preparing for real inference. Key capabilities include classifying inference topology (backend-only, hybrid, demo-only), tracing artifacts, loaders, endpoints, and frontend consumers, detecting training-serving feature skew, fallback divergence, preprocessing or post-processing drift, artifact path fragility, dishonest health checks, cold start, CORS, env, and dependency risks, and producing a severity-ranked audit with concrete fixes and tests. Trigger on requests like audit ML inference reliability, review scoring endpoint correctness, check model serving risks, find training-serving skew, assess demo-to-production readiness, or write an ML audit report for this repo."
---

# ML Inference Audit

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

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
