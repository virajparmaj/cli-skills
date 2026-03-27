---
name: v-notes
description: "Generate a repo-specific `notes/` documentation set by inspecting real code, routes, APIs, auth, database, env, and deployment files before writing. Use when asked to document a project, create `notes/00-13`, map architecture and user flows, assess auth/database status, or produce high-signal onboarding docs for future AI agents. Enforces evidence labels (`Confirmed from code`, `Strongly inferred`, `Not found in repository`), creates empty files only when explicitly not needed, and summarizes what exists vs missing. Trigger phrases: create notes folder, document this repo, map pages and routes, write architecture notes, generate prompt context, audit auth/db docs." 
---

# Repo Notes Generator

Use this skill when the user wants high-quality project notes generated from code evidence.

## CRITICAL constraints

- Inspect first; do not write notes from assumptions.
- Do not change product code, styling, or runtime config.
- Only create or update markdown files under `notes/` in the target repo.
- Never invent features that are not present.
- Label uncertain items explicitly as:
  - `Confirmed from code`
  - `Strongly inferred`
  - `Not found in repository`
- If a required notes file is irrelevant, leave it empty and mention that in the final summary.

## Quick start

1. Run `scripts/discover-repo-surface.sh /absolute/path/to/repo`.
2. Read the files reported by the script, then verify key runtime paths manually.
3. Follow the full output contract in
   [references/notes-generation-spec.md](references/notes-generation-spec.md).

## Workflow

1. Build repo reality from code.
   - Inspect `README`, `package.json`, app source folders, route definitions, API clients, backend/server folders, DB or migration files, env examples, and deployment config.
   - Validate what is implemented versus planned or mocked.
2. Classify findings by certainty.
   - Use `Confirmed from code` for direct evidence.
   - Use `Strongly inferred` for architecture or behavior implied by multiple files.
   - Use `Not found in repository` when evidence is absent.
3. Generate `notes/00_overview.md` through `notes/13_prompt_context.md` exactly, using the reference spec.
4. Handle auth and database carefully.
   - If auth exists: document exact implementation.
   - If auth is needed but missing: provide practical implementation guidance only (no code changes).
   - If auth is not needed: leave `notes/04_auth_and_roles.md` empty.
   - If DB exists: document actual schema and relationships.
   - If DB is needed but missing: provide clearly marked proposed schema.
   - If DB is not needed: leave `notes/05_database_schema.md` empty.
5. Validate before final response.
   - Ensure all 14 notes files exist.
   - Confirm every non-empty file is concise, structured, and repo-specific.
   - Confirm empty files are intentional and explained in the final summary.

## Output expectations in chat

After writing the files, provide a concise summary with:

1. files created
2. files intentionally left empty
3. auth status (`exists`, `missing but needed`, or `not needed`)
4. DB status (`exists`, `missing but needed`, or `not needed`)
5. major surprises or architecture risks

## Guardrails

- Prefer facts over generic best practices.
- Cite file paths while analyzing so conclusions stay auditable.
- Keep notes practical for future engineers and coding agents.
- If the repo already has `notes/`, update carefully instead of rewriting blindly.

## Bundled resources

- `scripts/discover-repo-surface.sh`: deterministic repo discovery for product, routes, API, auth, DB, env, and deploy clues.
- `references/notes-generation-spec.md`: required 14-file structure, per-file expectations, certainty labeling, and empty-file policy.
