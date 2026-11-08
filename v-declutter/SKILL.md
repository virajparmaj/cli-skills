---
name: v-declutter
description: "Review or simplify repository structure, hidden dependencies, change boundaries, redundant wrappers, duplicate logic, dead files, and Lovable/GPT-Engineer artifacts while preserving behavior and data. Use for requested decluttering or structural cleanup; an audit-only request stays read-only."
---

# Codebase Declutter & Architecture Streamliner

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.

Audit, beautify, and reorganize repository file architecture, directory hierarchy, naming redundancy, fragmented patch sprawl, AI-generator/Lovable boilerplate, and dead code while strictly preserving test suites, data integrity, and runtime behavior.

For a cleanup request, inventory candidates, prepare a concrete action table, apply scoped moves and import updates, and verify behavior. For a review request, stop at the action table. Before editing, record existing changes so unrelated work and staged selections survive.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

## The 5 Core Focus Areas

1. **Redundant Files & Directories**:
   - Flatten single-child or redundant directory nesting (e.g., `src/components/companies/CompaniesTable/CompaniesTable.tsx` -> `src/components/companies/CompaniesTable.tsx`).
   - Merge redundant wrapper layers (e.g., `Root.tsx` wrapping `App.tsx` without purpose, pure pass-through containers).
   - Break circular/cross coupling (e.g., extracting shared modal shells or drawers into their own reusable component in `src/components/shared/` or `src/components/ui/`).
   - Eliminate naming redundancy / stuttering (`Foo/FooBar.tsx`, `Button/Button.tsx`).

2. **Historical Data & Patch Sprawl**:
   - Consolidate incremental/dated patch files (e.g., date-stamped additions, multiple partial seed files like `seed_v1.json`, `seed_2024_03.json`) into clean, domain-driven modules (`seeds/users.json`, `seeds/companies.json`).
   - Remove obsolete scratch/patch files, temp scripts, and abandoned experiments.

3. **Logic Deduplication & Dead Code**:
   - Deduplicate repetitive loops, copy-pasted data transformers, or formatting routines into parameterized helpers.
   - Prune unreferenced exports, dead types, and unused imports.

4. **Change Boundaries & Hidden Dependencies**:
   - Trace code that must change together but has duplicated policy, implicit global/file state, or undocumented call order.
   - Check callers coupled to implementation details and interfaces containing vocabulary for only one workflow.
   - Use actual callers and current requirements to distinguish unnecessary special cases from required behavior.
   - For an untangling request or verified coupling candidate, read [references/change-boundaries.md](references/change-boundaries.md). Group related evidence under the smallest common fix before editing.

5. **Non-Negotiable Quality Gates**:
   - Preserve 100% data integrity and existing test contracts.
   - Verify external contracts: environment variables, URL routes, API endpoints, and persistence (`localStorage`, database schemas) must remain completely untouched.
   - Run the full test suite and production build to guarantee zero regressions.

---

## Workflow

### Step 1: Pre-Flight Baseline Verification
1. Inspect repo root: detect package manager (`npm`, `pnpm`, `yarn`, `bun`, `uv`, `poetry`, `pip`).
2. Run baseline tests to verify the starting state is green:
   - Use the repository’s configured non-watch test command and installed package manager. Do not download a new test runner to manufacture a baseline.
   - For Python, use the project environment and configured test command.
3. Run the configured build when the project has one; mark absent checks N/A.
4. If baseline tests or build fail, stop and flag the pre-existing error before making any changes.

### Step 2: Deterministic Inventory & Redundancy Scan
1. Run `python3 scripts/scan_declutter.py <repo-path>` to enumerate structural facts:
   - Single-child directories
   - Stuttering naming paths
   - Historical patch and dated files
   - Pass-through wrapper layers
   - Duplicate utility filenames
   - Potential orphan source files
2. Read [references/declutter-playbook.md](references/declutter-playbook.md) for domain-specific refactoring recipes and rules.
3. If stripping AI-generator or Lovable traces, run `bash scripts/find-lovable-traces.sh <repo-path>` and follow [references/lovable-removal-playbook.md](references/lovable-removal-playbook.md).

### Step 3: Formulate Restructuring Plan
For untangling work, record the current dependency path and the concrete change that would need synchronized edits. Keep a compact decision log grouping affected sites under each proposed fix; distinguish verified bugs from structural improvements. A directory shape, retry, exception handler, or single-caller parameter alone is not a finding. Preserve comments and test coverage unless their cleanup is requested. Recheck affected callers once after each fix; repeat only for regressions, failed checks, or unresolved evidence under the practical review policy.

Draft the Action Plan Table before mutating the filesystem:
- List every file to be moved, renamed, unwrapped, consolidated, or deleted.
- Identify all dependent files whose `import` statements must be remapped.

### Step 4: Execute Restructuring & Import Remapping
1. **File Moves**: Move only planned files; Git detects renames from content. Use `git mv` only when staging those changes is authorized, and preserve existing staged selections.
2. **Remap Imports**: Update both relative (`./`, `../`) and path alias (`@/`) imports across the codebase.
3. **Consolidate Seeds/Data**: Merge fragmented seed files into canonical domain files without duplicate keys or data loss.
4. **Unwrap Pass-Through Wrappers**: Inline simple pass-through layers into parent consumers, preserving any context providers or error boundaries.
5. **Deduplicate Logic**: Extract repeated parsing, transformations, or formatting into centralized helpers in `lib/` or `utils/`.
6. **Clean Empty Directories**: Remove directories emptied by file lifting.

### Step 5: Verification & Zero-Regression Quality Gate
1. Run type check:
   - TypeScript: `npx tsc --noEmit`
   - Python: `mypy` or `pyright` (if configured)
2. Run test suite:
   - `npm test` or `pytest`
3. Run production build:
   - `npm run build`
4. Verify chunk sizes if frontend: ensure no bundle chunks exceed 500 kB without explanation.
5. If verification fails, isolate the regression and undo only this task’s affected edits from the recorded baseline. Never use repository-wide reset, checkout, or clean commands; preserve unrelated and pre-existing work. Report unresolved failures.

---

## Output Contract (Strict)

Produce exactly these three parts in order:

### 1. Declutter Inventory & Action Table

```markdown
| Target / Path | Category | Action Taken | Status |
| ------------- | -------- | ------------ | ------ |
| src/components/companies/CompaniesTable/CompaniesTable.tsx | Single-child nesting | Flatten to src/components/companies/CompaniesTable.tsx | APPLIED |
| src/Root.tsx | Pass-through wrapper | Unwrapped into src/main.tsx, removed Root.tsx | APPLIED |
| src/data/seed_2024_01.json, seed_2024_02.json | Patch sprawl | Consolidated into src/data/seeds/companies.json | APPLIED |
| src/utils/formatDateDuplicate.ts | Logic duplicate | Extracted to shared formatters in src/lib/format.ts | APPLIED |
| src/types/deprecatedTypes.ts | Dead code | Pruned unreferenced types | APPLIED |
```

- `Category`: `Single-child nesting`, `Stuttering path`, `Pass-through wrapper`, `Patch sprawl`, `Logic duplicate`, `Dead code`, or `Change boundary`.
- `Action Taken`: Specific concise description of the refactoring step.
- `Status`: `APPLIED`, `KEPT (with reason)`, or `SKIPPED`.

### 2. Structural Delta Summary

A concise bulleted summary of structural metrics:
- **Directories flattened**: `X`
- **Files moved / consolidated**: `Y`
- **Redundant wrappers eliminated**: `Z`
- **Dead files / orphan code pruned**: `W`
- **Data integrity**: measured record/key comparison, or `N/A` / `UNVERIFIED` with reason

### 3. Quality Gate & Zero-Regression Verdict

A strict 3-line verdict block:

```markdown
Build: PASS — production build succeeded (largest chunk: <name> XXX kB).
Tests: PASS — X/X tests passing (0 regressions).
Contracts: PRESERVED — routes, environment variables, and persistence verified intact.
```

If the build or tests fail, report:
```markdown
Build: FAIL — <exact error line>. No success claimed; fix required before shipping.
```

---

## Guardrails

- **Never mutate applied migrations**: Database migrations in directories like `supabase/migrations/` or `alembic/versions/` represent historical database revisions; do not consolidate or rename them unless explicitly requested.
- **Never break public contracts or routes**: In file-system routing frameworks (Next.js `app/` or `pages/`, Remix, Astro), do not rename or move route files without explicit instructions.
- **Preserve Context Providers**: When unwrapping pass-through components, ensure React Context Providers, ErrorBoundaries, and ThemeProviders are preserved and mounted in the parent.
- **Never hand-edit lockfiles**: If dependencies are touched, use the project's package manager to regenerate lockfiles.
- **100% Data Integrity**: When consolidating partial seed files, verify no primary keys, foreign keys, or unique identifiers are omitted or duplicated.

---

## Boundary with Adjacent Skills

- `v-vibe`: Read-only post-vibe audit that inspects architecture debt and slop without modifying files. Use `v-vibe` for review only; use `v-declutter` when you want active restructuring.
- Lovable / GPT-Engineer cleanup is included here via [references/lovable-removal-playbook.md](references/lovable-removal-playbook.md); `v-delovable` is a retired name.
- `v-scripts`: Engineering audit for runtime latency, bundle size, and dead scripts.
- `v-declutter`: The active structural reorganizer that simplifies directory trees, un-nests single-child folders, consolidates fragmented data patches, unwraps indirection shells, and eliminates logic duplication.
