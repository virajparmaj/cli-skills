---
name: v-git
description: "Write a short commit message from current git changes (staged, unstaged, untracked) in a strict low-effort format. Use for prompts like write commit message, summarize my git changes, make a conventional commit title, or draft a quick GitHub commit note."
---

# Git Commit Message Draft

Use this skill when the user wants a fast commit message from the repo's current git state.

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
  2. `git commit -m "<type> : <short summary 4-5 words max>" \` followed by 1–4 additional `-m "<change group>"` lines, each line except the last ending with ` \`
  3. (blank line after the commit block)
  4. `git push origin main`
- Each extra `-m` line = one change group (≤6 words, rough grammar OK).
- All content lives inside the code block — no bullets or text outside.
- Do not add any other text outside the code block.

Example structure:
```bash
git add .

git commit -m "feat : add auth module" \
  -m "JWT token generation" \
  -m "login + refresh endpoints" \
  -m "input validation + tests"

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

git commit -m "chore : no changes detected"

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
