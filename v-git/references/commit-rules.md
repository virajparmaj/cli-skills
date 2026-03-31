# Commit Message Rules

Review this repository's current git changes (staged + unstaged + untracked) and write a short GitHub commit message.

Rules:

- Output one fenced `bash` code block with this structure: `git add .` (blank line), then `git commit -m "<type> : <short summary 4-5 words max>" \` followed by 1–4 additional `-m "<change group>"` lines (each line except the last ends with ` \`), then a blank line, then `git push origin main`.
- Each extra `-m` line is one change group (≤6 words, rough grammar OK).
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
