---
name: v-notes-update
description: "Update existing `notes/` documentation from current repository reality by reading code and recent changes, then revising outdated content, removing redundant sections, and preserving canonical note order. Use when asked to refresh notes, sync docs after code changes, clean stale notes, or maintain `notes/00-13` without rewriting everything. Default behavior is modify-in-place; do not create new files unless a canonical notes file is missing and required. If creation is needed, follow the same sequence and naming convention (`00_overview.md` ... `13_prompt_context.md`)."
---

# Notes Update and Drift Cleanup

Use this skill when notes already exist and must be updated to reflect current code.

## CRITICAL constraints

- Inspect repository and notes first; do not rewrite blindly.
- Modify existing files in `notes/` whenever possible.
- Do not add new files unless absolutely necessary.
- If adding is necessary, only add missing canonical notes files using the exact sequence and naming pattern.
- Remove redundant, obsolete, or contradictory statements when evidence shows they are stale.
- Do not change product code, styling, or runtime config.
- Keep claims evidence-backed and label uncertainty as:
  - `Confirmed from code`
  - `Strongly inferred`
  - `Not found in repository`

## Quick start

1. Run `scripts/discover-notes-drift.sh /absolute/path/to/repo`.
2. Read existing `notes/` files before touching any content.
3. Follow
   [references/notes-update-spec.md](references/notes-update-spec.md).

## Workflow

1. Build a delta map.
   - Compare existing `notes/` content against current code, config, routes, API layers, auth, DB, env, and deployment clues.
   - Use recent file changes (git diff/status when available) to prioritize note updates.
2. Update in place.
   - Revise outdated sections.
   - Add newly confirmed behavior where missing.
   - Delete redundant or irrelevant content.
3. Preserve structure.
   - Keep canonical file names and order.
   - Only create missing canonical files when required for coverage.
   - Do not add ad-hoc extra note files unless user explicitly requests them.
4. Validate outputs.
   - Ensure docs remain concise, practical, and repo-specific.
   - Ensure removed content is actually obsolete.
   - Ensure no invented features are introduced.

## Output expectations in chat

After updates, summarize:

1. files modified
2. files created (should usually be none)
3. files intentionally left unchanged
4. stale/redundant sections removed
5. unresolved unknowns needing manual confirmation

## Guardrails

- Prefer surgical edits over full rewrites.
- Keep wording high-signal; avoid fluff.
- Preserve useful historical context only when still relevant.
- If auth/DB status changes, update related notes consistently across `03`, `04`, `05`, `06`, `09`, and `10` as needed.

## Bundled resources

- `scripts/discover-notes-drift.sh`: surfaces canonical coverage, missing/extra notes, changed code areas, and likely impacted notes.
- `references/notes-update-spec.md`: update policy, staleness cleanup rules, and canonical-file creation constraints.
