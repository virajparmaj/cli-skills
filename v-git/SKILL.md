---
name: v-git
description: "Write a short commit message from current git changes (staged, unstaged, untracked) in a strict low-effort format. Use for prompts like write commit message, summarize my git changes, make a conventional commit title, or draft a quick GitHub commit note."
---

# Git Commit Message Draft

Use this skill when the user wants a fast commit message from the repo's current git state.

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
4. Generate the final answer using the output contract below.

## Output contract (strict)

- Output one fenced `bash` code block with this exact structure:
  1. `git add .` (blank line after)
  2. `git commit -m "<type> : <short summary 4-5 words max>" \` followed by a single `-m` containing all change groups as `- ` prefixed lines in one multiline string (closing `"` on the last bullet line)
  3. (blank line after the commit block)
  4. `git push origin main`
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

If no staged, unstaged, or untracked changes exist, return:

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
