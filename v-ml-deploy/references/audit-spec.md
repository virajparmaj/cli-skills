# ML Inference & Serving Reliability Audit

Use this reference when auditing repositories in this workspace for inference correctness, serving reliability, and operational safety.

## Workspace patterns that shaped this audit

These checks were tuned against common Vite + React + FastAPI ML project patterns.

### ML / inference architecture

- All sampled ML backends use FastAPI with `joblib`-loaded sklearn/XGBoost artifacts.
- Model artifacts live under `backend/artifacts/` as `.joblib` files.
- Models are commonly loaded at module scope on startup.
- Feature metadata comes from `model.feature_names_in_` or `model_info*.json`.
- Frontends are React/Vite apps that preprocess data and send structured JSON to the backend.
- Some projects include a client-side fallback heuristic that can diverge from the live model.
- Multi-model projects may load parallel models with separate metadata files.
- Some projects keep post-processing logic in backend server code, separate from the model artifact.

### Recurring failure modes

- No backend input validation beyond Pydantic type coercion; range checks and out-of-distribution guards are typically missing.
- Artifact paths are often relative and assume `CWD == backend/`.
- Health endpoints often return static success without proving the model loaded.
- Feature-order or feature-subset mismatches are possible when metadata exists but runtime assertions do not.
- Fallback scoring can diverge from the production model.
- Model artifacts are typically unversioned `.joblib` files with no hash or model-card linkage.
- Dependency pinning is partial or absent around model-serving packages.
- Automated test coverage is usually missing for scoring endpoints.
- Frontend API calls usually have no explicit timeout handling.
- Render free-tier cold starts can delay first inference by 10-30 seconds.
- Some repos contain dead inference code, legacy helpers, or production `console.log` calls.
- Post-processing can live outside the model in backend or frontend code, so thresholds and transforms may drift.

### Frontend / backend contract patterns

- `VITE_API_URL` is commonly the frontend contract boundary, with a baked-in Render fallback URL.
- API layers usually live in `src/services/api.ts` or `src/lib/api.ts`.
- TypeScript types are often defined but not enforced at runtime.
- Error handling is usually catch-all with generic toasts.
- CSV upload flows often look like: Papa Parse -> `alignFeatures()` -> batch POST -> client-side analytics.

### Auth / security patterns

- No sampled scoring endpoint has real auth.
- CORS origins are hardcoded in Python source instead of being environment-driven.
- Rate limiting and request logging are typically absent.
- Role-based access is often cosmetic UI hiding rather than backend enforcement.

### Deployment patterns

- Frontends are typically on Vercel; ML backends are typically on Render free tier.
- `Dockerfile`, `render.yaml`, staging splits, and `.env.example` files are usually missing.
- Narrow CORS allowlists can block Vercel preview deployments.

## Required audit workflow

Stay in review mode. Do not edit files unless the user explicitly asks.

### Step 0: Load project context

Before inspecting code, read these files in order when present:

1. `CLAUDE.md`
2. `README.md`
3. `notes/13_prompt_context.md`
4. `notes/03_architecture.md`
5. `notes/06_api_contracts.md`
6. `notes/11_known_issues.md`
7. `notes/10_deployment.md`
8. `.env.example` or `.env`

These files often contain confirmed architecture decisions, known gaps, API contracts, and deployment constraints. Do not duplicate findings already documented as known issues. Reference them and assess whether they have been resolved.

### Step 1: Map the ML path

Trace the full inference path from model artifact to user-facing output by inspecting:

| What to find | Where to look |
| --- | --- |
| Model artifacts | `backend/artifacts/`, `models/`, `*.joblib`, `*.pkl`, `*.onnx`, `*.pt` |
| Model metadata | `model_info*.json`, `model_card*.json`, `model.feature_names_in_` in loading code |
| Model loading code | `backend/*.py` with `joblib.load()`, `pickle.load()`, `torch.load()`, or module-level globals |
| Scoring endpoints | FastAPI routes that call `model.predict()` or `model.predict_proba()` |
| Feature engineering | DataFrame construction, feature subsetting, and column reordering before prediction |
| Pre/post-processing | Threshold logic, temperature scaling, probability transforms, tier assignment, recommendation rules |
| Frontend consumption | `src/services/api.ts`, `src/lib/api.ts`, `src/lib/api/adapter.ts` |
| Frontend preprocessing | CSV parsing, `alignFeatures()`, data coercion before API calls |
| Fallback or heuristic paths | Client-side scoring when the API is unavailable, often in contexts or pages |
| Response types | `src/types/model.ts`, `src/types/`, or inline TS interfaces |
| Health checks | `/health` endpoints and whether they verify model readiness |
| Environment config | `VITE_API_URL`, `MODEL_PATH`, or hardcoded Render/Railway/Fly URLs |

Classify the inference topology:

- `backend-only`: model runs server-side and the frontend only consumes JSON
- `hybrid`: the frontend does preprocessing and/or fallback work while the backend scores
- `frontend-only/demo`: the repo uses mock data or hardcoded predictions with no real backend

If the repo is demo-only, state this clearly and limit the audit to:

- whether the mock data structure matches a plausible model contract
- whether the demo is ready for real model integration
- what will break when a real backend is connected

### Step 2: Inspect for ML-specific failure modes

Check every category below. For each confirmed finding, cite the exact file path and line range. If a category is clean, say so explicitly.

#### Correctness risks

1. **Training/serving feature skew**
   - Does model metadata match the features constructed at request time?
   - If multiple models exist, does each one get the correct feature subset?
   - Are features reordered to training order or just assumed to arrive correctly?
2. **Fallback scoring divergence**
   - If a client-side heuristic or fallback exists, does it use the same features and logic as the production model?
   - Flag any case where the fallback uses features the model deliberately excludes, such as leakage-prone cost fields.
3. **Preprocessing parity**
   - Is feature coercion consistent, especially around `0` vs `NaN` vs other imputation behavior?
   - Are categorical encodings consistent between training and serving?
4. **Post-processing correctness**
   - Are thresholds, tiers, or probability cutoffs hardcoded in multiple places, and do they agree?
   - If probabilities are transformed or calibrated, is that documented and tested?
5. **Batch vs single-item divergence**
   - If both single and batch endpoints exist, do they behave identically for the same input?
   - Does the batch path handle empty arrays, a single item, and very large payloads?

#### Serving and operational risks

6. **Model initialization**
   - Is the model loaded once at startup or per request?
   - If multiple models are loaded, what is the combined memory footprint?
   - What happens if an artifact is missing or corrupt?
7. **Artifact path fragility**
   - Are artifact and metadata paths relative or resolved from `__file__` / `pathlib`?
   - Is `MODEL_PATH` configurable via env var, or hardcoded?
   - What happens if the process starts from project root instead of `backend/`?
8. **Health check honesty**
   - Does `/health` verify that the model object is loaded and callable?
   - Or does it return static success regardless of model state?
9. **Cold start and memory pressure**
   - Does Render or Railway free-tier cold start affect first-request latency?
   - Does the frontend handle that latency with loading, retry, or timeout behavior?
   - Are API URLs or internal details logged in production?
10. **Dependency version drift**
    - Is `scikit-learn` pinned when `joblib` artifacts depend on it?
    - Are `xgboost`, `pandas`, `numpy`, and `joblib` pinned when they touch model loading or feature handling?
    - Does the frontend validate response shapes or trust them blindly?
11. **Timeout, retry, and degraded mode**
    - Do frontend fetch calls use explicit timeouts?
    - Is there retry logic for transient failures?
    - If the model cannot load, does the backend return a structured error or just crash?
    - Is there a circuit breaker or degraded-mode path?
12. **CORS and env configuration**
    - Are CORS origins hardcoded or environment-driven?
    - Will Vercel preview deployments be blocked?
    - Does the frontend bake in a Render fallback URL?

#### Security and data risks

13. **Input validation**
    - Does the backend validate input ranges beyond type coercion?
    - Can out-of-distribution inputs produce nonsense predictions silently?
    - In CSV flows, are file size and column-name constraints enforced?
14. **Response contract stability**
    - Are response shapes typed on both sides?
    - If the backend renames a field, will the frontend fail gracefully or silently render bad data?
15. **Sensitive data in logs or responses**
    - Are raw inputs or predictions logged?
    - Are model internals exposed when they should not be public?

#### Dead code and maintenance

16. **Unused inference code**
    - Are there legacy scoring helpers, old load paths, commented-out endpoints, or unused ML UI components?
    - Examples to watch for include orphaned analytics helpers, dead scoring functions, and unused parameter or summary components.

### Step 3: Produce the audit report

Use this exact report structure:

#### A. ML Path Summary

- Inference topology
- Model type, artifact location, and loading mechanism
- Endpoint inventory with request and response shapes
- Frontend consumption pattern

#### B. Verified Findings

For each finding, use:

`[P0-P3] Title — file_path:line_range`

- What fails: concrete production failure scenario
- Evidence: the code path or logic that proves it
- Smallest fix: the minimal change that resolves it
- Test to add: a specific case that would catch it

Severity guide:

- `P0`: incorrect predictions in production, data corruption, or security vulnerability
- `P1`: silent correctness degradation or missing validation on user-facing input
- `P2`: operational fragility, deploy breakage, cold-start reliability, or missing observability
- `P3`: maintenance debt, hardcoded config, dead code, or type drift

#### C. Unverified Concerns

For each concern, use:

- Concern: what might be wrong
- Why suspicious: the code pattern that triggered the concern
- How to verify: the specific check the developer should run

Use this section when the repo lacks enough evidence to prove parity, staleness, deployment behavior, or performance.

#### D. Missing Tests

List concrete missing tests such as:

- model loading with missing, corrupt, or version-incompatible artifacts
- feature alignment with missing, extra, reordered, or malformed columns
- scoring endpoints with valid input, malformed input, empty batch, and large batch cases
- response-schema compatibility between backend output and frontend expectations
- fallback scoring parity against the live model
- threshold and post-processing behavior
- cold-start behavior within acceptable latency
- CORS coverage for Vercel preview domains

#### E. Correctness Risks vs Operational Risks

Provide two ranked lists:

1. Correctness risks: issues that produce wrong answers
2. Operational risks: issues that produce downtime, crashes, or silent degradation

#### F. Reusable Audit Patterns

Call out patterns that should become reusable checklists or future skills, such as:

- model-loading safety checks
- feature parity verification
- frontend-backend contract validation
- scoring-endpoint smoke tests
- dependency-pinning policy for ML repos

## Scope constraints

- Do not report generic ML best practices unless they are tied to code in the repo.
- Do not duplicate `notes/11_known_issues.md`; reference it and assess resolution status.
- Do not drift into general frontend quality, auth strategy, or UI/UX reviews unless they directly affect the ML path.
- Favor file-level, production-facing findings over academic commentary.
- If training code or deployment history is missing, say so explicitly instead of over-claiming certainty.

## Why this audit is shaped this way

- Step 0 exists because repos often include `notes/` documents with already-confirmed architecture and known issues.
- The file-location table exists because these projects repeatedly use the same ML layout: `backend/artifacts/`, `src/services/api.ts`, `src/lib/api.ts`, `src/lib/alignFeatures.ts`, and `src/types/`.
- Topology classification matters because some repos are hybrid and some are demo-only.
- Fallback divergence is explicit because some projects have a real local heuristic path that differs from the backend model contract.
- Artifact path fragility is explicit because some projects use relative `open("artifacts/...")` and `joblib.load("artifacts/...")`.
- Health-check honesty is explicit because sampled backends commonly return static success.
- Cold-start handling is explicit because these projects commonly use hosted free-tier backends.
- Post-processing drift is explicit because transforms and thresholds can live outside the model artifact, including in backend server code and frontend recommendation logic.
- Strict dependency pinning is explicit because artifact loading is version-sensitive and many repos show partial pinning.
- Verified vs unverified findings are separate to reduce false confidence.
- The report structure includes a concrete missing-tests section because ML repos commonly have little or no automated coverage.

## Optional add-on clauses

### Variant A: Multi-model audit

Use when the repo serves multiple models, such as band-specific routing, ensembles, or A/B variants.

- Verify each model has its own metadata file and correct feature list.
- Check that routing logic for model selection is explicit and tested.
- Confirm all models are loaded at startup and their combined memory footprint is at least reasoned about.
- Look for assertion code that validates feature parity across shared paths. If equivalent guardrails are absent, consider a `P1`.

### Variant B: CSV upload scoring path

Use when the repo accepts CSV uploads for batch scoring.

- Trace parse -> column validation -> feature alignment -> coercion -> API call -> result merge.
- Check behavior when columns are missing, columns are extra, values are non-numeric, the file is empty, or the file exceeds size limits.
- Verify `alignFeatures()` or equivalent logic matches model expectations for missing values.
- Check whether aligned rows are logged or persisted, which can become a privacy risk.

### Variant C: Demo-to-production readiness

Use when the repo has mock data or no real backend.

- Audit whether the mock data shape matches a plausible backend contract.
- Identify hardcoded mock arrays and what should become API calls.
- Check whether React Query or TanStack Query is instantiated but unused.
- List the minimum integration surface: endpoints, shared types, and error states.
- Flag UI logic that assumes synchronous mock data and will break with async fetching.

### Variant D: Strict dependency pinning clause

Use when reviewing `requirements.txt` or `pyproject.toml`.

- All packages that touch the model artifact should be pinned exactly: `scikit-learn`, `xgboost`, `joblib`, `numpy`, `pandas`.
- Treat unpinned model-adjacent dependencies as at least a `P2`.
- If the artifact was created with a known sklearn version, verify the serving environment pins that exact version.
- Remember that `joblib` artifact loading is sklearn-version-sensitive.
