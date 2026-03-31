# Commit Message Rules

Review this repository's current git changes (staged + unstaged + untracked) and write a short GitHub commit message.

Rules:

- Output one fenced `bash` code block with exactly three lines: `git add .`, `git commit -m "<type> : <short summary 4-5 words max>"`, `git push origin main`.
- After the bash code block, add `1` to `4` plain markdown bullets using `- ` summarizing change groups (outside the code block, for context).
- Keep each bullet under `6` words.
- Grammar does not need to be perfect.
- Focus on meaningful change groups, not file-by-file noise.
- Do not add any other text outside the code block and bullets.

Allowed types:

- `chore`
- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `style`
