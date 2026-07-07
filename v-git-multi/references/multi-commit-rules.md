# Multi-Commit Split Rules

Group the working tree's current changes (staged + unstaged + untracked) into 2-5 logical commits, each in Veer's strict commit format, and emit them as one paste-ready bash sequence. This extends the single-commit contract in [v-git/references/commit-rules.md](../../v-git/references/commit-rules.md) to N commits — the per-commit title and body format is identical.

## Per-commit format (reused from v-git, unchanged)

Each commit is:

```
git commit -m "<type> : <short summary 4-5 words max>" \
  -m "- change group one
- change group two
- change group three"
```

- Title: `<type> : <summary>` — exactly one space on each side of the colon, summary 4-5 words max.
- All change groups go in ONE `-m` argument — do not use a separate `-m` per bullet. Each bullet starts with `- ` (<=6 words, rough grammar OK).
- Focus on meaningful change groups, not file-by-file noise.

Allowed types (same as v-git):

- `chore` — maintenance (default for housekeeping)
- `feat` — net-new user behavior
- `fix` — bug resolution
- `docs` — documentation-only
- `refactor` — internal structure cleanup
- `test` — test-only changes
- `style` — formatting-only changes

Scoped titles are allowed when a commit is confined to one area: `feat(api) : add scoring endpoint`. Breaking changes prefix the type with `!`: `feat! : remove legacy api`.

## Grouping rubric

Read the `=== file manifest ===` section from `scripts/cluster-git-changes.sh`. Each row is `STAGE STATUS CLASS TOPDIR PATH`. Group rows into buckets using this priority:

1. **Separate by class.** Never bury docs, config, tests, or style-only churn inside a feature commit. Typical natural buckets:
   - `feat`/`fix`/`refactor` — the `src` changes that are the point of the session
   - `test` — files classed `test`
   - `docs` — files classed `docs` (`.md`, `notes/`, README, CHANGELOG)
   - `config`/`chore` — files classed `config` (lockfiles, tsconfig, vite/vercel config, `.env.example`, CI, Dockerfiles)
   - `style` — formatting-only or `.css`/tailwind changes with no logic
2. **Then split `src` by module** when source changes span clearly separate top-level dirs or areas (`backend/` vs `src/`, `api/` vs `frontend/`, distinct feature folders). Use scoped titles for these.
3. **Keep coupled files together.** A rename pair (OLD -> NEW), a component and its test, a migration and its generated types, a lockfile and the manifest that changed it — these belong in the same commit.
4. **Order by dependency.** Emit commits so prerequisites land first:
   - config/dependency changes before source that relies on them
   - source before its tests
   - feature/source before its docs
5. **Cap at 5 commits.** If natural buckets exceed 5, merge the smallest related ones (e.g. fold `style` into the nearest source commit, or `config` into `chore`). Aim for 2-4 in most sessions.

## Assignment invariants (hard)

- Every changed file from the manifest is assigned to **exactly one** commit — none dropped, none duplicated.
- Each commit stages files with an **explicit** `git add <file list>`. Never `git add .`, never `git add -A`. A bare directory is only acceptable if every file under it belongs to that single commit.
- Quote any path containing spaces or shell metacharacters.
- Deletions and renames are staged with `git add <path>` too (git records removals when the path is added).

## Output shape

One fenced `bash` block, nothing outside it:

```bash
git add <files for commit 1>

git commit -m "<type> : <summary>" \
  -m "- group
- group"

git add <files for commit 2>

git commit -m "<type> : <summary>" \
  -m "- group
- group"

git push origin main
```

- Exactly one `git push origin main` at the very end, after all commits.
- Blank line between each `git commit` and the next `git add`.

## When NOT to split

If the manifest shows the changes are a single coherent concern (all one class, one module, or too small to split meaningfully), do not manufacture buckets. Output one plain sentence saying it is cleaner as a single commit, then a single v-git-style block (still with an explicit `git add` file list). Forcing 3 tiny commits out of one logical change is worse than one honest commit.

## Worked example

Manifest (abridged):

```
STAGE   STATUS  CLASS   TOPDIR          PATH
worktree M      src     backend         backend/main.py
worktree M      src     backend         backend/scoring.py
new     ??      test    backend         backend/tests/test_scoring.py
worktree M      src     src             src/services/api.ts
worktree M      docs    (root)          README.md
new     ??      config  (root)          requirements.txt
```

Reasoning: two source areas (`backend/` scoring logic, `src/` frontend client), plus new tests, docs, and a deps file. Deps first, then backend + its tests, then frontend, then docs.

```bash
git add requirements.txt

git commit -m "chore : pin scoring deps" \
  -m "- add requirements file
- pin runtime versions"

git add backend/main.py backend/scoring.py backend/tests/test_scoring.py

git commit -m "feat(api) : add scoring endpoint" \
  -m "- scoring route + logic
- input validation
- unit tests"

git add src/services/api.ts

git commit -m "feat : call scoring from client" \
  -m "- typed api wrapper
- error handling"

git add README.md

git commit -m "docs : document scoring api" \
  -m "- usage example
- request response shapes"

git push origin main
```
