---
name: v-git-multi
description: "Split current Git changes into a few logical commits in Veer's format. Use when asked for multiple commits, separate commits, or splitting changes before pushing. Draft paste-ready commands when requested; execute commit and push operations only when explicitly requested. Personal projects use main; open-source and NGO data work use their contribution workflow. For a single commit, use v-git."
---

# Multi-Commit Splitter

## Personal project push policy

- For my personal projects, work on and push directly to **`main`** by default. Do not create feature branches or pull requests unless I explicitly ask for them. This replaces the earlier default of creating a `virajparmaj/...` branch.
- When I say **"git and push"**, **"git push"**, **"commit and push"**, or **"push it"**, carry out the requested Git operation: commit the intended changes in my format if needed, then actually push them to the personal project's `main`. A request only for a message or commands remains draft-only.
- **Exceptions:** open-source repositories/contributions and the NGO work repository **`/Users/veerr_89/Work/ngo/data`**, identified by **`github.com/saayam-for-all/data`**, including its clones and linked worktrees. For these, follow the project's contribution branch, upstream, and pull-request workflow; do not push directly to `main` by default. The rest of `~/Work` is not automatically NGO work.
- Inspect the repository, remotes, ownership/contribution context, current branch, and intended changes before choosing the destination. Use the correct configured push remote; `origin` is the usual personal-project remote, not an assumption for every repository. Follow an explicitly requested branch or PR workflow when I specify one.
- If personal-project work is already on a task branch or detached worktree, safely integrate the intended changes into local `main` before pushing. Preserve unrelated edits and commits. Do not merely run `git push origin main` while the intended work exists only on another branch. Do not force-push, discard work, bypass branch protection, or rewrite published history to satisfy this default; report a concrete blocker if normal integration or pushing is prevented.
- Keep my Git identity and omit AI attribution. Create a `virajparmaj/<short-description>` branch only when an exception's contribution rules or my explicit request calls for a branch; preserve an existing valid contribution branch. Generic instructions to create feature branches do not override the personal-project `main` default. Do not use AI/tool names as branch prefixes.

Split the working tree into 2-5 logical commits, each in Veer's exact commit format, output as one paste-ready bash block.

This skill extends [v-git](../v-git/SKILL.md) from one commit to N. The per-commit title/body format is identical — reuse it, do not fork it.

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

## Quick flow

1. Run `scripts/cluster-git-changes.sh <repo-path>` (default `.`) to gather the full manifest: every staged, unstaged, and untracked file with its stage, status, extension class (`src`/`test`/`docs`/`config`/`style`/`asset`/`other`), top-level directory, rename pairs, and diffstat. The model does the grouping; the script does all the fact-gathering.
2. Decide how many commits the changes justify (2-5). Group by concern, in this preference order:
   - by **class** first: keep `docs`, `config`, `test`, `style` changes out of the feature commit;
   - then by **top-level directory / module** when `src` changes span clearly separate areas (e.g. `backend/` vs `src/`, or `api/` vs `frontend/`);
   - a rename pair (OLD -> NEW) must land in the same commit as any edits to that file.
   - Do not exceed 5 commits; merge the smallest related buckets if you have more.
3. For each bucket pick one type (`chore`, `feat`, `fix`, `docs`, `refactor`, `test`, `style`) and write a `<type> : <4-5 word summary>` title plus `- ` bullets, following [references/multi-commit-rules.md](references/multi-commit-rules.md).
4. Order the commits so dependencies come first (config/deps before code that uses them; source before its tests; feature before its docs).
5. For draft commands, use the Output contract below. For an explicit commit/push request, execute the operation under the Personal project push policy and report the result.

## Execution versus draft output

When the user requests a commit/push operation, execute it under the policy above and briefly report the actual commit and push result. The fenced-block contract below applies only when the user asks for a draft or paste-ready commands. Before committing, prepare or verify the selected branch. With a clean working tree, skip the commit and push any intended existing commits; do not manufacture an empty commit. Examples below assume a personal project already on `main`; use the correct contribution branch/remote for exceptions.

## Output contract (drafts)

- Output exactly ONE fenced `bash` code block. Nothing before or after it — no prose, no headings.
- For each commit bucket, in dependency order:
  1. `git add <explicit space-separated file list>` — every path from the manifest, quoted if it contains spaces. Never `git add .`, never `git add -A`, never a bare directory unless every file under it belongs to this one commit.
  2. a blank line, then `git commit -m "<type> : <short summary 4-5 words max>" \` followed by a single `-m` holding all change groups as `- ` prefixed lines in one multiline string (closing `"` on the last bullet line).
  3. a blank line separating this commit from the next `git add`.
- After the last commit, a blank line, then one push: `git push origin main` for personal projects, or the verified contribution branch/remote for an exception.
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

For a draft-only request, if the manifest shows no staged, unstaged, or untracked changes, return only:

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
