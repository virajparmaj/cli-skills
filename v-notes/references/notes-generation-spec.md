# Notes Generation Spec

Use this reference after `v-notes` triggers. It defines the exact documentation contract for `notes/` output.

## Purpose

Generate a repo-specific `notes/` folder that captures product reality from code, not assumptions.

## Status labels (required)

Every uncertain claim must be labeled as one of:

- `Confirmed from code`
- `Strongly inferred`
- `Not found in repository`

Use these labels inline or in short evidence bullets within each notes file.

## Scope constraints

- Inspect code and config first.
- Do not modify product code.
- Only create or update markdown files under `notes/`.
- Do not invent routes, APIs, auth flows, or DB entities.
- Keep writing practical and concise.

## Required repository inspection order

1. `README*`
2. `package.json` and language/runtime manifests (`pyproject.toml`, `requirements*.txt`, etc.)
3. app source directories (`src/`, `app/`, `pages/`, `components/`, `lib/`, `hooks/`, `services/`)
4. backend or API directories (`api/`, `server/`, `backend/`, `ml/`)
5. auth and DB surfaces (`supabase/`, `prisma/`, `drizzle/`, migrations, schema files)
6. deployment files (`render.yaml`, `vercel.json`, `netlify.toml`, `Dockerfile`, CI workflows)
7. env templates (`.env.example`, `.env.local.example`)
8. route definitions, API client code, and integration boundaries

Use `scripts/discover-repo-surface.sh` first, then confirm manually.

## Required output files

Create these files exactly:

- `notes/00_overview.md`
- `notes/01_features.md`
- `notes/02_design_system.md`
- `notes/03_architecture.md`
- `notes/04_auth_and_roles.md`
- `notes/05_database_schema.md`
- `notes/06_api_contracts.md`
- `notes/07_user_flows.md`
- `notes/08_pages_and_routes.md`
- `notes/09_dev_setup.md`
- `notes/10_deployment.md`
- `notes/11_known_issues.md`
- `notes/12_roadmap.md`
- `notes/13_prompt_context.md`

## File content expectations

For each non-empty file, use this structure where relevant:

- Purpose
- Status
- Confirmed from code
- Inferred / proposed
- Important details
- Open issues / gaps
- Recommended next steps

Keep sections that are not applicable short rather than forcing filler.

### `00_overview.md`

Include:

- what the product is
- who it serves
- primary problem solved
- core user journey
- current maturity
- `Repo reality` (implemented vs aspirational)

### `01_features.md`

Group features as:

- Confirmed implemented
- Partially implemented
- Not implemented but implied
- Nice-to-have / future

Each item should include where it appears in code.

### `02_design_system.md`

Document current design language from code:

- aesthetic and visual direction
- colors and tokens
- typography patterns
- spacing/card/radius/shadow patterns
- interaction and animation usage
- consistency issues

If no formal design system exists, state that explicitly.

### `03_architecture.md`

Document:

- frontend and backend stack
- hosting and deployment model
- data/state management
- API/data flow
- third-party services
- auth/DB/storage/ML integrations

Include a simple text diagram.

### `04_auth_and_roles.md`

Decision logic:

- Auth implemented: document exact flow and roles.
- Auth needed but missing: document implementation plan only (no code changes).
- Auth not needed: leave file empty.

If auth is needed but missing, include:

- why auth is required
- recommended provider based on stack (prefer Supabase when already present)
- role model
- route protection plan
- session lifecycle plan
- signup/login/reset flows
- DB tables and RLS/policies (if applicable)
- likely files to add/change
- env vars required
- step-by-step implementation checklist

### `05_database_schema.md`

Decision logic:

- DB exists: document actual schema, relationships, ownership links, security notes.
- DB needed but missing: provide `Proposed, not implemented` schema.
- DB not needed: leave file empty.

### `06_api_contracts.md`

Document actual contracts:

- endpoints and methods
- request/response shape
- error states
- loading and timeout behavior
- frontend-backend integration path
- external service dependencies

If backend API is needed but absent, include `Proposed contract` section.

### `07_user_flows.md`

Document practical step-by-step flows relevant to the repo, such as:

- landing/discovery
- auth/onboarding (if applicable)
- primary task flow
- create/save/edit/delete behavior
- upload/prediction/inference flow (if applicable)
- dashboard/profile/admin paths

Call out mocked, broken, or incomplete steps.

### `08_pages_and_routes.md`

Build a route map with:

- path
- purpose
- auth needed
- key components
- data dependencies
- status

Infer from router config and file conventions when needed.

### `09_dev_setup.md`

Include:

- stack/runtime versions if detectable
- install/run/test commands
- required env var names and purpose
- local setup steps
- common setup pitfalls
- service linking notes (Supabase/Vercel/Render/etc.)

Do not invent secret values.

### `10_deployment.md`

Document:

- frontend and backend deployment targets
- build commands
- environment separation clues
- deployment dependencies/order
- risks and failure points

### `11_known_issues.md`

List by severity (`critical`, `medium`, `low`):

- bugs and broken flows
- missing integrations
- security risks
- state/data consistency issues
- UX friction
- performance risks
- maintainability concerns

### `12_roadmap.md`

Create practical phases:

- immediate fixes
- short-term improvements
- medium-term improvements
- long-term enhancements
- auth/data/infra hardening
- product polish

### `13_prompt_context.md`

Write reusable AI context for future agents:

- app purpose and goals
- stack
- design rules
- architecture guardrails
- behaviors to preserve
- weak points to watch
- editing expectations for future agents

## Empty-file policy

If a required file is not relevant, create it as an empty file and explicitly report that decision in the final summary.

- If auth is not needed: `04_auth_and_roles.md` must be empty.
- If DB is not needed: `05_database_schema.md` must be empty.

## Quality bar

- Prefer concrete file evidence over generic advice.
- Keep notes high-signal and skimmable.
- Distinguish implemented behavior from proposals.
- Do not hide unknowns; label them.

## Final response contract

After writing notes, summarize in chat:

1. files created
2. files intentionally left empty
3. auth status (`exists`, `missing but needed`, `not needed`)
4. DB status (`exists`, `missing but needed`, `not needed`)
5. major surprises or architecture risks
