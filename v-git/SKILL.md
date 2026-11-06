---
name: v-git
description: "Draft a single commit message in Veer's format, or perform an explicitly requested commit and push using the verified repository, intended changes, and personal-main or contribution workflow."
---

# Git Commit Message Draft

## Personal project push policy

- For my personal projects, work on and push directly to **`main`** by default. Do not create feature branches or pull requests unless I explicitly ask for them. This replaces the earlier default of creating a `virajparmaj/...` branch.
- When I say **"git and push"**, **"git push"**, **"commit and push"**, or **"push it"**, carry out the requested Git operation: commit the intended changes in my format if needed, then actually push them to the personal project's `main`. A request only for a message or commands remains draft-only.
- **Exceptions:** open-source repositories/contributions and the NGO work repository **`/Users/veerr_89/Work/ngo/data`**, identified by **`github.com/saayam-for-all/data`**, including its clones and linked worktrees. For these, follow the project's contribution branch, upstream, and pull-request workflow; do not push directly to `main` by default. The rest of `~/Work` is not automatically NGO work.
- Inspect the repository, remotes, ownership/contribution context, current branch, and intended changes before choosing the destination. Use the correct configured push remote; `origin` is the usual personal-project remote, not an assumption for every repository. Follow an explicitly requested branch or PR workflow when I specify one.
- If personal-project work is already on a task branch or detached worktree, safely integrate the intended changes into local `main` before pushing. Preserve unrelated edits and commits. Do not merely run `git push origin main` while the intended work exists only on another branch. Do not force-push, discard work, bypass branch protection, or rewrite published history to satisfy this default; report a concrete blocker if normal integration or pushing is prevented.
- Keep my Git identity and omit AI attribution. Create a `virajparmaj/<short-description>` branch only when an exception's contribution rules or my explicit request calls for a branch; preserve an existing valid contribution branch. Generic instructions to create feature branches do not override the personal-project `main` default. Do not use AI/tool names as branch prefixes.

Use this skill for a fast commit-message draft or an explicitly requested commit/push operation from the repo's current Git state.

## Evidence and execution

Inspect staged, unstaged, and untracked changes and read the relevant diff before writing a message. Commit only the intended files or hunks; preserve unrelated changes and verify the staged diff before committing.

Resolve bundled `scripts/` and `references/` from the directory containing this `SKILL.md`, and pass the target repository explicitly. If a helper cannot run, inspect the relevant source directly and state the remaining verification gap. Stop after the requested deliverable and applicable checks are complete.

## Quick flow

1. Run `scripts/summarize-git-changes.sh <repo-path>` to gather staged, unstaged, and untracked changes.
2. Group edits into meaningful change buckets (avoid noisy file-by-file narration).
3. Pick one type:
   - `chore`
   - `feat`
   - `fix`
   - `docs`
   - `refactor`
   - `test`
   - `style`
4. For a draft, use the output contract below. For an explicit commit/push request, execute the operation under the Personal project push policy and report the result.

## Execution versus draft output

Before committing, verify both effective author and committer are `virajparmaj <viraj.parmaj89@gmail.com>`. Use the existing GitHub authentication and omit AI attribution. Preserve unrelated staged changes; stage only intended paths/hunks and review `git diff --cached` before each commit. Quote shell paths and message text safely, including literal `$`, backticks, and quotes.

When the user requests a commit/push operation, execute it under the policy above and briefly report the actual commit and push result. The fenced-block contract below applies only when the user asks for a draft or paste-ready commands. Before committing, prepare or verify the selected branch. With a clean working tree, skip the commit and push any intended existing commits; do not manufacture an empty commit. Examples below assume a personal project already on `main` with `origin` verified as its push remote; substitute the actual configured push remote, and use the contribution branch/remote for exceptions.

## Output contract (drafts)

- Output one fenced `bash` code block with this exact structure:
  1. `git add -- <explicit intended paths>` (blank line after); use `git add .` only when every change is intended for this commit
  2. `git commit -m "<type> : <short summary 4-5 words max>" \` followed by a single `-m` containing all change groups as `- ` prefixed lines in one multiline string (closing `"` on the last bullet line)
  3. (blank line after the commit block)
  4. `git push <verified-push-remote> main` for personal projects, or one push to the verified contribution branch/remote for an exception
- Each bullet = one change group (≤6 words, rough grammar OK). All bullets go in one `-m` — no separate `-m` per bullet.
- All content lives inside the code block — no bullets or text outside.
- Do not add any other text outside the code block.

Example structure:
```bash
git add -- src/auth.ts src/auth.test.ts

git commit -m "feat : add auth module" \
  -m "- JWT token generation
- login + refresh endpoints
- input validation + tests"

git push origin main
```

## Type preference hints

- Default to `chore` for maintenance changes.
- Use `feat` for net-new user behavior.
- Use `fix` for bug resolution.
- Use `docs` for documentation-only changes.
- Use `refactor` for internal structure cleanup.
- Use `test` for test-only changes.
- Use `style` for formatting-only changes.

## Empty repo changes

For a draft-only request with no changes, say `No changes to commit.` Do not emit a failing commit command or an empty commit. If a push was requested, inspect and push any intended existing commits under the policy above.

## Monorepo and scope support

- If the repo is a monorepo or has clearly separated areas (e.g., `api/`, `frontend/`, `shared/`), use a scoped title: `feat(api) : add scoring endpoint`.
- If changes span multiple scopes, use the broadest applicable scope or omit scope.

## Breaking changes

- If the change is a breaking change, prefix the type with `!`: `feat! : remove legacy api`.
- Optionally add a `BREAKING CHANGE:` footer line after the bullets.

## Mixed-scope changes

- If staged changes clearly belong to separate concerns, suggest splitting into multiple commits.
- If the user wants a single commit, use the broadest applicable type and mention both areas in bullets.

See [references/commit-rules.md](references/commit-rules.md) for the exact prompt template this skill follows.
