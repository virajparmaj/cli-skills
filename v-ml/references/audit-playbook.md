# ML Inference & Serving Reliability Audit

You are an ML platform engineer auditing a repository for inference correctness, serving reliability, and operational safety. Stay in review mode and do not edit files unless explicitly asked.

## Step 0: Load Project Context

Before inspecting code, read any existing context files in this order and skip missing files:

1. `CLAUDE.md`
2. `README.md`
3. `notes/13_prompt_context.md`
4. `notes/03_architecture.md`
5. `notes/06_api_contracts.md`
6. `notes/11_known_issues.md`
7. `notes/10_deployment.md`
8. `.env.example` or `.env`

These files often contain confirmed architecture decisions, known gaps, API contracts, and deployment constraints that should inform the audit. Do not duplicate findings already documented as known issues. Reference them and assess whether they appear resolved.

## Step 1: Map the ML Path

Trace the full inference path from model artifact to user-facing output by inspecting:

| What to find | Where to look |
| --- | --- |
| Model artifacts | `backend/artifacts/`, `models/`, `*.joblib`, `*.pkl`, `*.onnx`, `*.pt` |
| Model metadata | `model_info*.json`, `model_card*.json`, or `model.feature_names_in_` in loading code |
| Model loading code | `backend/*.py` and any files calling `joblib.load()`, `pickle.load()`, or `torch.load()` |
| Scoring endpoints | FastAPI routes (`@app.post`, `@app.get`) that call `model.predict()` or `model.predict_proba()` |
| Feature engineering | DataFrame construction before prediction, feature subsetting, column reordering, request-to-model coercion |
| Pre or post-processing | Threshold logic, temperature scaling, probability transforms, tier or label assignment, server-side sampling |
| Frontend consumption | `src/services/api.ts`, `src/lib/api.ts`, `src/lib/api/adapter.ts`, and route components that fetch predictions |
| Frontend preprocessing | CSV parsing, `alignFeatures()`, coercion, schema alignment, batching, and analytics before or after scoring |
| Fallback or heuristic paths | Client-side scoring or demo behavior when the API is unavailable |
| Response types | `src/types/`, inline TypeScript interfaces, and backend response models |
| Health checks | `/health` endpoints and whether they prove model readiness or only return static JSON |
| Environment config | `VITE_API_URL`, `MODEL_PATH`, and hardcoded Render, Railway, Fly, or localhost URLs |

Classify the inference topology before auditing:

- `backend-only`: model runs server-side and the frontend consumes JSON
- `hybrid`: frontend does preprocessing or fallback work and backend does scoring
- `frontend-only / demo`: mock data or hardcoded predictions with no real backend model

If the repo is demo-only, say so clearly and limit the audit to:

- whether the mock data structure matches a plausible model contract
- whether the demo is ready for real model integration
- what will break when a real backend is connected

## Step 2: Inspect for ML-Specific Failure Modes

For every finding, cite the exact file path and line range. If a category is clean, say so explicitly instead of skipping it.

### Correctness Risks

1. **Training or serving feature skew**
   - Does the feature list in model metadata (`model_info*.json` or `feature_names_in_`) match the features constructed at request time?
   - If multiple models exist, does each receive the correct feature subset?
   - Are features reordered to match training order, or only assumed to arrive correctly?

2. **Fallback scoring divergence**
   - If a client-side heuristic or fallback exists, does it use the same features and logic as the production model?
   - Flag any case where the fallback uses features the model deliberately excludes, such as leakage-prone cost fields.

3. **Preprocessing parity**
   - Is feature coercion consistent?
   - If alignment code replaces missing values with `0`, does the model actually expect `0` rather than `NaN`, null, or imputation?
   - Are categorical encodings consistent between training and serving?

4. **Post-processing correctness**
   - Are thresholds, tiers, or probability cutoffs hardcoded in multiple places, and do they agree?
   - If post-processing transforms probabilities through calibration or temperature scaling, is that behavior documented and testable?

5. **Batch vs single-item divergence**
   - If both single and batch scoring routes exist, do they produce identical results for the same input?
   - Does the batch path handle empty payloads, single-item payloads, and large batches safely?

### Serving & Operational Risks

6. **Model initialization**
   - Is the model loaded once at startup or reloaded per request?
   - If multiple models are loaded, what is the likely combined memory footprint?
   - What happens if an artifact file is missing or corrupt at startup?

7. **Artifact path fragility**
   - Are paths relative and dependent on the current working directory, or resolved from `__file__` and `pathlib`?
   - Is `MODEL_PATH` configurable via env var or hardcoded?
   - For `open("artifacts/...")` patterns, what happens when the process starts from the project root instead of `backend/`?

8. **Health check honesty**
   - Does `/health` actually verify the model object is loaded and callable?
   - Or does it return static success JSON even if model loading failed or was never checked?

9. **Cold start and memory pressure**
   - On free-tier hosting, the first request after spin-down may need to load all models from disk. How is that risk surfaced?
   - Does the frontend handle cold-start latency with loading states, retry logic, or helpful hints?
   - Are there `console.log` statements leaking API URLs or internal state in production?

10. **Dependency version drift**
    - Is `scikit-learn` pinned in `requirements.txt`?
    - Are `xgboost`, `pandas`, `numpy`, and `joblib` pinned when they affect artifact loading or feature handling?
    - Does the frontend validate response shapes at runtime, or does it trust backend JSON blindly?

11. **Timeout, retry, and degraded mode**
    - Do frontend fetch calls use timeouts?
    - Is there retry logic for transient failures?
    - If the model cannot load, does the backend return a structured error or crash?
    - Is there a circuit breaker, graceful degraded mode, or explicit fallback behavior?

12. **CORS and env configuration**
    - Are CORS origins hardcoded in source or loaded from env?
    - Will preview deployments be blocked?
    - Is `VITE_API_URL` the only way to configure the backend URL, and is a production fallback baked into the bundle?

### Security & Data Risks

13. **Input validation**
    - Does the backend validate input ranges beyond Pydantic type coercion?
    - Can extreme out-of-distribution inputs produce nonsense predictions silently?
    - For CSV upload flows, is file size limited and are column names validated against the expected model schema?

14. **Response contract stability**
    - Are prediction response shapes typed on both sides, for example Pydantic on the backend and interfaces or schemas on the frontend?
    - If the backend changes a field name, will the frontend fail gracefully or silently show `undefined`?

15. **Sensitive data in logs or responses**
    - Are raw inputs or predictions logged?
    - Could they contain PII or sensitive features?
    - Are model internals exposed in responses that should remain private?

### Dead Code & Maintenance

16. **Unused inference code**
    - Are there legacy scoring functions, old model-loading paths, or commented-out endpoints?
    - Are there frontend components or helpers that still reference ML outputs but are no longer imported?

## Step 3: Produce the Audit Report

Organize the result into these sections:

### A. ML Path Summary

- Inference topology
- Model type, artifact location, and loading mechanism
- Endpoint inventory with request and response shapes
- Frontend consumption pattern

### B. Verified Findings

Use this format for every confirmed issue:

`[P0-P3] Title — file_path:line_range`

- What fails: the concrete production failure scenario
- Evidence: the code path, behavior, or logic that proves it
- Smallest fix: the minimal change that resolves it
- Test to add: the specific test case that would catch it

Severity guide:

- `P0`: incorrect predictions in production, data corruption, or a security vulnerability
- `P1`: silent failure that degrades results without error, or missing validation on user-facing input
- `P2`: operational fragility such as deploy breakage, cold-start crash risk, or missing observability
- `P3`: code quality, hardcoded config, dead code, missing types, or maintenance debt

### C. Unverified Concerns

Use this for issues that are suspicious but not provable from code alone:

- Concern: what might be wrong
- Why suspicious: what code pattern triggered the concern
- How to verify: the concrete check the developer should run

Good examples include training/serving parity you cannot confirm without training code, model staleness you cannot assess without deployment history, and performance issues you cannot confirm without profiling.

### D. Missing Tests

List concrete missing tests such as:

- model loading with missing, corrupt, or incompatible artifacts
- feature alignment with missing, extra, reordered, or wrongly typed columns
- scoring endpoints with valid input, malformed input, edge cases, and empty batches
- backend response schema matching frontend expectations
- fallback scoring matching production behavior for representative inputs
- threshold and post-processing boundaries
- cold-start latency staying within an acceptable budget
- CORS coverage for preview deployment domains

### E. Correctness Risks vs Operational Risks

Split the findings into two ranked lists:

1. correctness risks that produce wrong answers
2. operational risks that produce downtime, crashes, or silent degradation

### F. Reusable Audit Patterns

Call out patterns that can become reusable checks or future skills, such as:

- model-loading safety checks
- feature parity verification
- frontend-backend contract validation
- scoring endpoint smoke-test templates
- dependency pinning policy for ML repos

## Constraints

- Do not report generic ML best practices unless tied to code in the repo.
- Do not duplicate findings already documented in `notes/11_known_issues.md`; reference them and assess whether they are resolved.
- Do not drift into general frontend polish, auth review, or UI critique unless those directly affect inference correctness or serving reliability.
- Favor file-level, production-facing findings over academic commentary.
- If the repo lacks enough evidence to confirm training or serving parity, say so explicitly in the unverified section.

## Optional Stronger Variants

### Variant A: Multi-Model Audit

Use this when the repo serves multiple models, such as band-specific, ensemble, or A/B variants:

- verify that each model has its own metadata file with the correct feature list
- check that routing logic is explicit and testable
- confirm that all models are loaded at startup and that combined memory cost is considered
- look for missing assertions that prove model-to-feature-list parity

### Variant B: CSV Upload Scoring Path

Use this when the repo accepts CSV uploads for batch scoring:

- trace parse -> column validation -> feature alignment -> coercion -> API call -> result merge
- check behavior for missing columns, extra columns, non-numeric values, empty files, and oversized uploads
- verify that alignment logic matches the model's missing-value expectations
- check whether aligned rows are logged or persisted, which may create privacy risk

### Variant C: Demo-to-Production Readiness

Use this when the repo uses mock or static data and has no real backend:

- audit whether mock structures match a plausible future API contract
- identify hardcoded model outputs that must become real API calls
- look for async assumptions that will break when live fetches replace sync mock data
- list the minimum integration surface: endpoints, shared types, error states, and loading states

### Variant D: Strict Dependency Pinning

Use this when Python artifacts depend on serialized model compatibility:

- all packages that touch the model artifact should be pinned to exact versions, especially `scikit-learn`, `xgboost`, `joblib`, `numpy`, and `pandas`
- flag unpinned ML dependencies as an operational risk because serialization formats and feature handling drift across versions
- when possible, verify that the runtime version matches the version used to create the artifact
