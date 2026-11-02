---
name: v-declutter
description: "Audit and streamline local repository file architecture, directory hierarchy, naming redundancy, fragmented patch sprawl, and dead code while strictly preserving functionality and test suites. Use when asked to audit or declutter project structure, flatten unnecessary directory nesting, consolidate fragmented data files or seeds, clean up historical patch sprawl, streamline file names, remove wrapper boilerplate, merge redundant indirection layers, eliminate duplicate logic, or prune dead code without breaking tests. Triggers include 'v-declutter', 'v-structure', 'audit and declutter', 'declutter project structure', 'clean up patch sprawl', 'flatten directory nesting', 'streamline file names', 'remove wrapper boilerplate'."
---

# Codebase Declutter & Architecture Streamliner

Audit, beautify, and reorganize repository file architecture, directory hierarchy, naming redundancy, fragmented patch sprawl, and dead code while strictly preserving test suites, data integrity, and runtime behavior.

This skill **EXECUTES** structural cleanups end to end: it audits the repository, presents a deterministic restructuring plan, safely moves files and remaps imports, unwraps redundant wrapper layers, consolidates patch sprawl, deduplicates logic into helpers, and verifies zero regressions via test suites and production builds.

<!-- skill-operating-standard -->
## Operating standard — run at maximum capability

Run this skill in your highest-effort mode, whatever model you are. Prefer correctness and completeness over speed or brevity; if you support extended thinking or an adjustable reasoning effort, raise it for this work. Do not guess when you can verify.

- **Think first.** Before acting, plan: what the skill must produce, which files or scripts give ground truth, and where the likely failure modes are. Reason step by step internally before writing the answer.
- **Facts before judgment.** Run this skill's `scripts/` first (when it has them) and treat their output as the only ground truth. Never invent file paths, line numbers, metrics, or data a script did not produce. If a script cannot run, say so and mark every dependent conclusion UNVERIFIED.
- **Evidence discipline.** Label every claim `Confirmed from code` (you read the exact file:line and traced the logic), `Strongly inferred` (a pattern implies it but a runtime path could exonerate it), or `Not found — fill in manually`. A scanner/grep hit is not a finding until you open the file and confirm it in context.
- **Adversarial self-check.** After a first draft, run a second pass whose only job is to refute each finding: what input, config, or code path would make it false? Drop or downgrade anything you cannot defend. For subtle calls (leakage, statistics, security, correctness, money) reason from at least two independent angles before asserting.
- **Bound the review.** Cover the requested scope and verify plausible findings. Stop once that scope is covered and required checks pass; expand or repeat only for changed code, failed checks, or unresolved evidence. State coverage gaps; do not chase speculative cases to fill a report.
- **Use every tool you have.** When a capability (code execution, file read, web or docs lookup, subagents, parallel calls) is available and would raise accuracy, use it instead of answering from memory or a single pass.
- **Honesty.** If a category is clean, say so; do not pad with generic best-practice filler that has no evidence in this repo. State assumptions, gaps, and anything unverified plainly.
- **Contract.** Follow this skill's output contract exactly — strict format, severity ranks, verdict labels, smallest viable fix. For generator skills, every emitted value must trace to a computed fact or a cited line; label anything else inferred.

---

## The 4 Core Focus Areas

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

4. **Non-Negotiable Quality Gates**:
   - Preserve 100% data integrity and existing test contracts.
   - Verify external contracts: environment variables, URL routes, API endpoints, and persistence (`localStorage`, database schemas) must remain completely untouched.
   - Run the full test suite and production build to guarantee zero regressions.

---

## Workflow

### Step 1: Pre-Flight Baseline Verification
1. Inspect repo root: detect package manager (`npm`, `pnpm`, `yarn`, `bun`, `uv`, `poetry`, `pip`).
2. Run baseline tests to verify the starting state is green:
   - JavaScript/TypeScript: `npm test` or `npm run test` or `npx vitest run`
   - Python: `pytest`
3. Run baseline build:
   - `npm run build`
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

### Step 3: Formulate Restructuring Plan
Draft the Action Plan Table before mutating the filesystem:
- List every file to be moved, renamed, unwrapped, consolidated, or deleted.
- Identify all dependent files whose `import` statements must be remapped.

### Step 4: Execute Restructuring & Import Remapping
1. **Atomic File Moves**: Use `git mv` when inside git to preserve commit history.
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
5. If tests or build fail, diagnose and fix the import/type issue immediately. If unfixable, roll back using `git checkout -- .`.

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

- `Category`: `Single-child nesting`, `Stuttering path`, `Pass-through wrapper`, `Patch sprawl`, `Logic duplicate`, or `Dead code`.
- `Action Taken`: Specific concise description of the refactoring step.
- `Status`: `APPLIED`, `KEPT (with reason)`, or `SKIPPED`.

### 2. Structural Delta Summary

A concise bulleted summary of structural metrics:
- **Directories flattened**: `X`
- **Files moved / consolidated**: `Y`
- **Redundant wrappers eliminated**: `Z`
- **Dead files / orphan code pruned**: `W`
- **Data integrity**: `100% verified (0 lost records/keys)`

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
- `v-delovable`: Specifically targets Lovable / GPT-Engineer boilerplate, tags, and README cleanup.
- `v-scripts`: Engineering audit for runtime latency, bundle size, and dead scripts.
- `v-declutter`: The active structural reorganizer that simplifies directory trees, un-nests single-child folders, consolidates fragmented data patches, unwraps indirection shells, and eliminates logic duplication.
