---
name: v-git
description: "Draft a short commit message in Veer's format or execute an explicitly requested commit and push. Use for write commit message, summarize my git changes, git and push, commit and push, or push it. Personal projects use main directly; open-source and NGO data work follow their contribution workflow."
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

When the user requests a commit/push operation, execute it under the policy above and briefly report the actual commit and push result. The fenced-block contract below applies only when the user asks for a draft or paste-ready commands. Before committing, prepare or verify the selected branch. With a clean working tree, skip the commit and push any intended existing commits; do not manufacture an empty commit. Examples below assume a personal project already on `main`; use the correct contribution branch/remote for exceptions.

## Output contract (drafts)

- Output one fenced `bash` code block with this exact structure:
  1. `git add .` (blank line after)
  2. `git commit -m "<type> : <short summary 4-5 words max>" \` followed by a single `-m` containing all change groups as `- ` prefixed lines in one multiline string (closing `"` on the last bullet line)
  3. (blank line after the commit block)
  4. `git push origin main` for personal projects, or one push to the verified contribution branch/remote for an exception
- Each bullet = one change group (≤6 words, rough grammar OK). All bullets go in one `-m` — no separate `-m` per bullet.
- All content lives inside the code block — no bullets or text outside.
- Do not add any other text outside the code block.

Example structure:
```bash
git add .

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

For a draft-only request, if no staged, unstaged, or untracked changes exist, return:

```bash
git add .

git commit -m "chore : no changes detected" \
  -m "- nothing to commit"

git push origin main
```

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
