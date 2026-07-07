---
name: v-notes
description: "Generate a repo-specific `notes/` documentation set by inspecting real code, routes, APIs, auth, database, env, and deployment files before writing. Use when asked to document a project, create `notes/00-13`, map architecture and user flows, assess auth/database status, or produce high-signal onboarding docs for future AI agents. Enforces evidence labels (`Confirmed from code`, `Strongly inferred`, `Not found in repository`), creates empty files only when explicitly not needed, and summarizes what exists vs missing. Trigger phrases: create notes folder, document this repo, map pages and routes, write architecture notes, generate prompt context, audit auth/db docs." 
---

# Repo Notes Generator

Use this skill when the user wants high-quality project notes generated from code evidence.

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
