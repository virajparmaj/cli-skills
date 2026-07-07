---
name: v-git-multi
description: "Split the working tree into N logical commits in Veer's strict commit format, ready to paste. Runs scripts/cluster-git-changes.sh to gather every staged, unstaged, and untracked file with status, diffstat, top-level directory, extension class, and rename pairs, then groups files into 2-5 logical buckets (feature vs docs vs config vs tests vs style, or per-module) and emits ONE fenced bash block: for each bucket an explicit `git add <file list>` followed by a `git commit -m \"<type> : <4-5 word summary>\" -m \"- bullets\"` in the exact v-git format, ending with a single `git push origin main`. Never uses `git add .` — every file is assigned to exactly one commit. Falls back to a single v-git-style commit when changes do not justify a split. Use when asked to: split this into multiple commits, multiple commits in my format, commit these separately, break the working tree into logical commits, or make N commits from my changes. For a single commit message use v-git."
---

# Multi-Commit Splitter

Split the working tree into 2-5 logical commits, each in Veer's exact commit format, output as one paste-ready bash block.

This skill extends [v-git](../v-git/SKILL.md) from one commit to N. The per-commit title/body format is identical — reuse it, do not fork it.

## Quick flow

1. Run `scripts/cluster-git-changes.sh <repo-path>` (default `.`) to gather the full manifest: every staged, unstaged, and untracked file with its stage, status, extension class (`src`/`test`/`docs`/`config`/`style`/`asset`/`other`), top-level directory, rename pairs, and diffstat. The model does the grouping; the script does all the fact-gathering.
2. Decide how many commits the changes justify (2-5). Group by concern, in this preference order:
   - by **class** first: keep `docs`, `config`, `test`, `style` changes out of the feature commit;
   - then by **top-level directory / module** when `src` changes span clearly separate areas (e.g. `backend/` vs `src/`, or `api/` vs `frontend/`);
   - a rename pair (OLD -> NEW) must land in the same commit as any edits to that file.
   - Do not exceed 5 commits; merge the smallest related buckets if you have more.
3. For each bucket pick one type (`chore`, `feat`, `fix`, `docs`, `refactor`, `test`, `style`) and write a `<type> : <4-5 word summary>` title plus `- ` bullets, following [references/multi-commit-rules.md](references/multi-commit-rules.md).
4. Order the commits so dependencies come first (config/deps before code that uses them; source before its tests; feature before its docs).
5. Emit the answer using the Output contract below.

## Output contract (strict)

- Output exactly ONE fenced `bash` code block. Nothing before or after it — no prose, no headings.
- For each commit bucket, in dependency order:
  1. `git add <explicit space-separated file list>` — every path from the manifest, quoted if it contains spaces. Never `git add .`, never `git add -A`, never a bare directory unless every file under it belongs to this one commit.
  2. a blank line, then `git commit -m "<type> : <short summary 4-5 words max>" \` followed by a single `-m` holding all change groups as `- ` prefixed lines in one multiline string (closing `"` on the last bullet line).
  3. a blank line separating this commit from the next `git add`.
- After the last commit, a blank line, then a single `git push origin main`.
- Every changed file from the manifest appears in exactly one `git add` — no file dropped, no file in two commits.
- Each bullet = one change group (<=6 words, rough grammar OK). All bullets for a commit go in ONE `-m`.

Example structure (two commits):
```bash
git add src/lib/api.ts src/services/scoring.ts

git commit -m "feat : add scoring endpoint client" \
  -m "- typed api wrapper
- scoring service call
- error handling"

git add README.md notes/06_api_contracts.md

git commit -m "docs : document scoring api" \
  -m "- usage example
- request response shapes"

git push origin main
```

## Single-commit fallback

If the manifest shows the changes are one coherent concern (all same class, one module, or too small to split meaningfully), do NOT force a split. Emit exactly one line of plain text saying so, then fall back to the single v-git block:

`Changes are one coherent concern — single commit is cleaner:`
```bash
git add src/lib/api.ts src/services/scoring.ts

git commit -m "feat : add scoring endpoint client" \
  -m "- typed api wrapper
- scoring service call
- error handling"

git push origin main
```

Even in the fallback, list files explicitly rather than `git add .`, since the manifest gives you the exact set.

## Empty repo changes

If the manifest shows no staged, unstaged, or untracked changes, return only:

```bash
git commit --allow-empty -m "chore : no changes detected" \
  -m "- nothing to commit"
```

## Edge cases

- **Renames:** put the OLD -> NEW pair in one commit; `git add` the new path (and the old path if `git status` still lists it) so the rename is recorded atomically.
- **Untracked binaries/assets:** group under an `asset`/`chore` commit unless they are integral to a feature bucket.
- **Deleted files:** stage them in the commit that removes the related feature; `git add <path>` also stages deletions.
- **Lockfiles:** keep `package-lock.json` / `pnpm-lock.yaml` / `poetry.lock` in the same commit as the manifest change that caused them, or a lone `chore : update lockfile`.

## Boundary with other skills

- For a **single** commit message, use `v-git`.
- This skill is the only one that assigns files to multiple commits and sequences them. It reuses v-git's title/body format verbatim via [references/multi-commit-rules.md](references/multi-commit-rules.md).

See [references/multi-commit-rules.md](references/multi-commit-rules.md) for the exact per-commit format and grouping rubric this skill follows.
