# Commit Message Rules

Review this repository's current git changes (staged + unstaged + untracked) and write a short GitHub commit message.

Rules:

- Output one fenced `bash` code block with this structure: `git add .` (blank line), then `git commit -m "<type> : <short summary 4-5 words max>" \` followed by a single `-m` containing all change groups as `- ` prefixed bullet lines in one multiline string (closing `"` on the last bullet line), then a blank line, then `git push origin main`.
- All change groups go in ONE `-m` argument — do not use separate `-m` per bullet. Each bullet starts with `- ` (≤6 words, rough grammar OK).
- All content lives inside the code block — no bullets or text outside.
- Focus on meaningful change groups, not file-by-file noise.
- Do not add any other text outside the code block.

Allowed types:

- `chore`
- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `style`
