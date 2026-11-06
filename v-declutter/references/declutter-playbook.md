# Codebase Declutter & Architecture Streamliner Playbook

## Operating Posture

This playbook provides concrete refactoring rules and recipes to audit and streamline file architecture, directory hierarchy, naming redundancy, historical patch sprawl, and dead code.

Non-negotiable rule: **Zero regressions, 100% data integrity, and passing test suites**.

---

## 1. Core Dimensions & Refactoring Patterns

### Dimension A: Redundant Files & Directory Nesting

#### 1. Single-Child Directory Flattening
- **The Antipattern**: Deep directory nesting where a directory contains only one subfolder or a single isolated file (e.g., `src/components/companies/CompaniesTable/CompaniesTable.tsx` where no other files exist in either directory).
- **Remedy**: Flatten single-child directories:
  - If a folder contains only one file, lift that file up to the parent directory:
    - `src/components/companies/CompaniesTable/CompaniesTable.tsx` -> `src/components/companies/CompaniesTable.tsx`
  - If a feature has only 2-3 components, keep them flat within `src/components/<feature>/` rather than sub-nesting each component in its own folder.
- **Exception**: Preserve directory nesting if the directory contains sibling files like `.module.css`, `.test.tsx`, `types.ts`, and `index.ts`.

#### 2. Stuttering Paths & Naming Redundancy
- **The Antipattern**: The folder name repeats unnecessarily in the filename:
  - `src/features/billing/billing-service.ts` (inside `billing/`)
  - `src/components/companies/CompaniesList.tsx`
  - `models/UserModel.py` (inside `models/`)
- **Remedy**:
  - Within domain folders, simplify names to be concise and natural:
    - `src/components/companies/List.tsx` or `src/components/companies/CompaniesList.tsx` -> `src/components/companies/List.tsx` (if consumed via domain import) OR flatten to `src/components/CompaniesList.tsx`.
    - Avoid stuttering like `Billing/BillingModal/BillingModalHeader.tsx`.

#### 3. Redundant Pass-Through Wrapper Layers
- **The Antipattern**: Artificial indirection layers that simply pass props through without adding behavior, state, styling, or context:
  - `Root.tsx` that merely imports and renders `<App />` with no router, providers, or error boundaries.
  - Middleman containers that only forward props to an inner component.
- **Remedy**:
  - Merge the pass-through wrapper into its consumer or parent:
    - If `main.tsx` mounts `<Root />` which only renders `<App />`, mount `<App />` directly in `main.tsx` and delete `Root.tsx`.
  - Check for: Router configs, React Query/Context Providers, ThemeProviders, and ErrorBoundaries. If the wrapper contains a Provider, rename it to reflect its true responsibility (e.g., `AppProviders.tsx`) or consolidate into `App.tsx`.

#### 4. Circular & Cross-Coupling Extraction
- **The Antipattern**: Two feature components importing directly from each other's internal folders, or shared modal shells duplicated across features.
- **Remedy**:
  - Extract common modals, dialog shells, or drawer containers to `src/components/shared/` or `src/components/ui/`.
  - Ensure features depend inward on shared modules, never cross-feature sideways.

---

### Dimension B: Historical Data & Patch Sprawl

#### 1. Dated & Incremental Patch Files
- **The Antipattern**: Leftover files from sequential fixes, experiments, or date-stamped additions:
  - `seed_2024_01.json`, `seed_2024_02_patch.json`, `seed_v2_final.ts`
  - `temp_fix.py`, `export_patch.ts`, `data_backup.csv`
- **Remedy**:
  - Consolidate multiple partial seed files into canonical, domain-driven seed modules:
    - `data/seeds/users.json`
    - `data/seeds/companies.json`
    - `data/seeds/transactions.json`
  - Ensure data in the consolidated file has no duplicate IDs or conflicting primary keys.
  - Remove obsolete scratch/patch files after verifying their contents are subsumed by canonical files.
- **Database Migrations Note**: Never consolidate applied database migrations (e.g. `supabase/migrations/`) unless explicitly requested, as production migration history must remain immutable.

---

### Dimension C: Logic Deduplication & Dead Code

#### 1. Deduplicating Repetitive Logic
- **The Antipattern**:
  - Repeated data transformation loops across multiple API endpoints or components.
  - Copy-pasted pagination, filtering, or date formatting routines.
  - Identical error handling or toast notification blocks.
- **Remedy**:
  - Extract shared transformation logic into pure, parameterized utility functions in a centralized helper module (e.g., `src/lib/transformers.ts` or `src/utils/formatters.ts`).
  - Parameterize variables (e.g., page size, sort field, currency code) rather than duplicating the function body.

#### 2. Dead Code, Types, and Unused Imports
- **The Antipattern**:
  - Unreferenced TypeScript interfaces and type aliases.
  - Exported functions or constants never imported by any active module.
  - Leftover debugging logs, commented-out dead code blocks, or orphan component files.
- **Remedy**:
  - Verify zero usage using full-codebase search across code, tests, and config.
  - Prune unreferenced exports and unused imports.
  - Delete orphan files that are neither entrypoints nor dynamically imported.

---

## 2. Refactoring Execution Protocol

### Step 1: Pre-Flight Baseline
Before modifying any files:
1. Verify git status is clean or note existing uncommitted changes:
   ```bash
   git status --short
   ```
2. Run test suite:
   ```bash
   npm test  # or pytest, cargo test, etc.
   ```
3. Run build:
   ```bash
   npm run build
   ```
If the baseline build or tests fail, **STOP** and report the baseline failure to the user before touching files.

### Step 2: Atomic File Restructuring & Import Remapping
When renaming or moving files:
1. Move only planned files after recording existing changes. Git detects renames from content; use `git mv` only when staging is authorized, without altering unrelated staged selections.
2. Immediately update all import references across the codebase:
   - Relative imports (`./`, `../`)
   - Path aliases (`@/components/...`)
   - Re-exports in barrel files (`index.ts`)
3. Clean up empty parent directories after moving children:
   ```bash
   rmdir src/components/foo 2>/dev/null || true
   ```

### Step 3: Verification & Zero-Regression Quality Gate
After applying restructuring and code changes:
1. Re-run tests:
   ```bash
   npm test  # or pytest
   ```
2. Re-run production build:
   ```bash
   npm run build
   ```
3. Type check (if TypeScript):
   ```bash
   npx tsc --noEmit
   ```
4. Verify external contracts:
   - Check that route URLs have not changed.
   - Check that localStorage/sessionStorage keys remain identical.
   - Check that environment variable access is intact.

---

## 3. Rollback Protocol

If a refactor causes unresolvable build or test regressions:
1. Restore only the edits introduced by this task, using the recorded pre-task contents and action table. Reverse task-owned moves individually and remove only files created by this task. Preserve pre-existing staged, unstaged, and untracked work. Do not run repository-wide checkout, reset, or clean commands.
2. Isolate the specific change that broke the contract.
3. Propose a smaller, targeted restructuring step instead of bulk moves.
