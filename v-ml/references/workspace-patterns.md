# Workspace Patterns

This skill was tuned against common Vite + React + TypeScript frontend and FastAPI ML backend projects.

## Confirmed Conventions

- Frontends are usually Vite, React, and TypeScript SPAs.
- Shared API code usually lives in `src/services/api.ts`, `src/lib/api.ts`, or page-level fetch helpers.
- ML backends usually live in `backend/`.
- Model artifacts are usually committed under `backend/artifacts/`.
- FastAPI and `joblib` are the common serving stack for live models.
- Some repos keep context docs under `notes/`, especially:
  - `notes/03_architecture.md`
  - `notes/06_api_contracts.md`
  - `notes/10_deployment.md`
  - `notes/11_known_issues.md`
  - `notes/13_prompt_context.md`
- Frontends often use `VITE_API_URL` with a hardcoded hosted fallback URL in source.
- Runtime response validation is uncommon even when TypeScript interfaces exist.

## ML / Inference Architecture Patterns

- Live ML backends in this stack are FastAPI services that load serialized models with `joblib`.
- Model artifacts are checked into git under `backend/artifacts/` as `.joblib` files.
- Models are commonly loaded at module scope instead of lazily per request.
- Feature metadata usually comes from either `model.feature_names_in_` or separate `model_info*.json` files.
- Frontends commonly preprocess data locally, send structured JSON to the backend, and then render the returned prediction.
- Some projects include fallback or demo scoring behavior alongside the live model flow.
- Multi-model projects may load parallel models with separate feature metadata files.
- Some projects keep meaningful post-processing logic in server code instead of inside the serialized artifact.

## Repeated Failure Patterns Worth Checking

- Module-level model loads are common, so startup failures matter.
- Artifact path handling is inconsistent:
  - Some projects use `MODEL_PATH` plus a relative default.
  - Some use bare `open("artifacts/...")` and `joblib.load("artifacts/...")`.
  - Some resolve artifacts from `Path(__file__).parent`.
- `/health` routes often return static success JSON instead of proving model readiness.
- Frontend fetch calls commonly omit timeouts and retry logic.
- CSV alignment may coerce missing or invalid values to `0`, which can hide training-serving drift.
- Some flows include demo or fallback behavior that can diverge from production scoring.
- Multi-model routing exists and should be audited as a first-class concern, not as a simple single-model app.
- Post-processing can live outside the artifact and still change predictions materially.
- Demo-only projects may present "models" as interactive UI components without any backend.
- Hardcoded CORS origins and baked-in deployment URLs are common operational constraints.
- Backend validation is often limited to Pydantic type coercion rather than real range or out-of-distribution checks.
- Feature-order and feature-subset mismatch risk is real when metadata files define expected features but runtime assertions are absent.
- Model version pinning is weak or missing, with unversioned `.joblib` files and little artifact provenance.
- Python dependency pinning is often partial rather than exact.
- Scoring endpoints generally lack automated tests.
- Legacy or unused inference helpers can remain in the codebase and confuse audits.
- Frontend code may log deployment config or API URLs in production.

## Cross-Project Operational Context

- Scoring endpoints are commonly unauthenticated.
- CORS policies are usually hardcoded in Python source instead of env-driven.
- Rate limiting and request logging are usually absent.
- Dockerfiles, `render.yaml`, and explicit staging or production separation are often missing.
- Preview deployments can fail because CORS allowlists are too narrow.
- `.env.example` is often missing even when env vars are required.

## Frontend-Backend Contract Patterns

- `VITE_API_URL` is the usual configuration hook, often paired with a hardcoded hosted fallback URL in source.
- API service layers usually live in `src/services/api.ts` or `src/lib/api.ts`.
- TypeScript interfaces exist in some repos, but runtime schema validation is uncommon.
- Error handling tends to collapse to generic toast or message behavior instead of structured retry and degraded-mode UX.
- CSV upload flows typically parse locally, align features, batch POST to the backend, and then compute analytics client-side.

## Security & Access Patterns

- No scoring service reviewed here includes real request authentication.
- Role-based access, where present, is usually a frontend visibility pattern rather than enforced authorization.
- Rate limiting and request logging are generally absent from inference endpoints.

## Deployment Patterns

- Hosted backends commonly target free-tier platforms, so cold starts are part of the real production behavior.
- Infra is usually configured in dashboards rather than codified in repo files.
- Separate staging and production environments are uncommon.
- Preview deploy behavior is fragile when CORS is narrow and URLs are hardcoded.

## Why The Playbook Emphasizes These Checks

- `Step 0: Load Project Context`: repos often include `notes/` documents with already-confirmed architecture and known issues, so audits should start from those facts rather than rediscover them.
- `Concrete where-to-look guidance`: these projects repeatedly use `backend/artifacts/`, `backend/*.py`, `src/services/api.ts`, `src/lib/api.ts`, and `src/types/`.
- `Inference topology classification`: some projects are demo-only, so a normal live-serving audit would misread the repo without this step.
- `Fallback scoring divergence`: some projects include fallback and demo paths that can drift from the live model.
- `Artifact path fragility`: relative path patterns break when the process starts from a different working directory.
- `Health check honesty`: backends commonly return static success without verifying models loaded.
- `Cold start and free-tier latency`: frontends assume hosted APIs and need explicit handling for slow wake-ups.
- `Post-processing outside the model`: server-side transforms can be just as important as the serialized artifact.
- `Dependency pinning specificity`: artifact loading is version-sensitive, but pinning is often incomplete.
- `CORS and env configuration`: hardcoded origins and source-level fallback URLs recur.
- `Verified vs unverified split`: some concerns require training code, deployment history, or profiling and should not be overstated.
- `Specific missing tests`: scoring paths and frontend-backend contracts generally lack dedicated automated coverage.
- `Do not duplicate known issues`: some repos already track known problems in `notes/11_known_issues.md`.
- `Scope boundary`: this skill is about inference correctness and serving reliability, not general frontend critique or auth cleanup unless those directly affect the inference path.
