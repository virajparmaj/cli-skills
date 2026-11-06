---
name: v-ml
description: "Review model-serving paths for feature parity, artifact loading, fallback behavior, and inference reliability. Use for scoring endpoint or training-serving skew audits; keep findings tied to the deployed path."
---

# ML Inference Audit

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Evidence and scope

- Read project instructions and relevant context first. Resolve `scripts/` and `references/` from this skill's directory; run helpers with the project's interpreter. Use scanner output as leads, then verify the source, data, active configuration, and reachable trigger. Disclose checks that could not run; direct inspection can still establish independent evidence.
- For each verified bug, give frequency **1–10** and impact **1–10**, show **frequency x impact = score**, and briefly justify both ratings. Confidence is separate from occurrence frequency. Checklist entries and statistical warning signs are inspection prompts, not automatic bugs.
- Fix threshold: **5**, unless the user changes it. Below 5, leave code alone and record one deduplicated item in an existing authorized backlog or **Deferred issues**; do not create remote issues without authorization. At 5 or above, propose the smallest fix and implement only when the task authorizes changes. A review request stays review-only.
- Preserve the requested report format, adding evidence and scores to findings. Pass the trigger, evidence, ratings, threshold, and deferrals to any fixer. Stop after scoped work and required checks pass; revisit only affected paths, failed checks, or unresolved evidence.

Distinguish measured or traced facts from unresolved hypotheses. Never report an audit scanner hit as proof on its own.

## Quick start

1. Inspect the repo before judging it. Read these if present, in order:
   - `AGENTS.md` and `CLAUDE.md`
   - `README.md`
   - `notes/13_prompt_context.md`
   - `notes/03_architecture.md`
   - `notes/06_api_contracts.md`
   - `notes/11_known_issues.md`
   - `notes/10_deployment.md`
   - `.env.example` and environment-variable names; inspect private values only if needed and never print secrets
2. Run `python3 scripts/map_ml_repo.py /absolute/path/to/project` to map the likely ML files and feature paths before deeper inspection.
3. Classify the inference topology before deep analysis:
   - `backend-only`
   - `hybrid`
   - `frontend-only / demo`
4. Map the full inference path from model artifact to user-facing output. Start with:
   - `backend/artifacts/`, `models/`, `*.joblib`, `*.pkl`, `*.onnx`, `*.pt`
   - FastAPI loaders and routes in `backend/*.py`
   - frontend API code in `src/services/api.ts`, `src/lib/api.ts`, or adapter files
   - feature alignment, CSV parsing, and fallback logic in `src/lib/`, `src/utils/`, `src/contexts/`, and route components
5. Load [Audit Playbook](references/audit-playbook.md) and [Audit Spec](references/audit-spec.md) and follow checklists for what to inspect, how to grade severity, and how to format the report.
6. If the repo uses a Vite + FastAPI ML stack, read [Workspace Patterns](references/workspace-patterns.md) before finalizing the audit.

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
- Model A/B testing and traffic splitting correctness, if currently implemented
- Existing data-drift monitoring where it affects the requested serving path
- Model explainability endpoints (SHAP, LIME) if present — verify they match the production model
