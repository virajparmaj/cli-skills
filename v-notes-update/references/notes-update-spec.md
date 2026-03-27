# Notes Update Spec

Use this reference when the repository already has `notes/` and the task is to keep them current with minimal churn.

## Purpose

Update existing `notes/` documentation to match current repository behavior, while removing stale or redundant content.

## Update mode defaults

- `Modify existing notes files first`.
- `Do not add new files unless absolutely necessary`.
- If creation is required, only create missing canonical files using existing naming sequence.

Canonical sequence:

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

## Evidence labels (required)

When certainty is not absolute, label statements using:

- `Confirmed from code`
- `Strongly inferred`
- `Not found in repository`

## Required process

1. Discover drift.
   - Run `scripts/discover-notes-drift.sh /absolute/path/to/repo`.
   - Read existing `notes/*.md` and compare with current code and config.
2. Build an update map.
   - What remains correct and should stay unchanged.
   - What is stale and should be edited or removed.
   - What is newly implemented and should be added.
3. Apply surgical edits.
   - Prefer patching existing sections over rewriting whole files.
   - Remove duplicated statements and contradictory claims.
   - Keep concise structure and high signal.
4. Validate consistency.
   - Ensure cross-file alignment when shared facts change (auth/DB/API/deployment).
   - Ensure file references match real paths.
   - Ensure unknowns are explicit, not guessed.

## Staleness cleanup rules

Treat content as stale when:

- it references deleted routes/components/APIs
- it claims auth/DB/deploy behavior no longer present
- it duplicates information already maintained in a more suitable notes file
- it contains placeholders (`TODO`, `TBD`, `coming soon`) that are outdated

When removing stale content:

- delete only obsolete lines/sections, not useful context
- replace with updated evidence-backed statements when available
- if evidence is incomplete, mark as `Not found in repository`

## File creation policy

Only add files when one of the canonical `notes/00-13` files is missing and the update task requires complete sequence coverage.

- Never create non-canonical extra files by default.
- If a canonical file is still irrelevant after review, create it as empty only when sequence completeness is required.

## Cross-file synchronization checklist

When these areas change, update corresponding notes:

- routes/pages: `00`, `01`, `07`, `08`
- design/UI system: `01`, `02`
- architecture/data flow: `03`, `06`
- auth/roles: `03`, `04`, `07`, `08`, `09`, `10`
- database/schema: `03`, `05`, `06`
- API/backend contracts: `03`, `06`, `07`
- dev setup/env vars: `09`, `10`, `13`
- deployment topology: `03`, `10`, `11`

## Final response contract

After updating notes, report:

1. modified files
2. created files (ideally none)
3. unchanged files intentionally left as-is
4. removed stale/redundant content categories
5. unresolved gaps requiring manual or runtime verification
