# CLI skills

45 reusable skills: 40 primary workflows and 5 UI specialists. This checkout is the source; installed symlinks keep local improvements available across projects.

The [latest skill-by-skill review](reviews/2026-11-06-skills.md) records robustness fixes, current-source updates, measured efficiency, and validation limits. A [JSON version](reviews/2026-11-06-skills.json) includes resource and change coverage for every skill.

## Install into your workflow

Requires Python 3.9 or newer. Preview the installation, then apply it:

```bash
python3 scripts/install-skills.py
python3 scripts/install-skills.py --apply
python3 scripts/install-skills.py --check
```

The installer uses `${CODEX_HOME:-~/.codex}/skills` and any existing Claude, Gemini, OpenCode, and legacy Gemini skill folders. It includes nested UI skills, preserves unrelated installations, and stops before changing anything if a skill name conflicts with another source or a real directory. Retired aliases are removed only when their symlinks belong to this checkout. No network download is needed for a local install.

Use an exact directory to select a different scope or host, including the [shared Codex user directory](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills):

```bash
python3 scripts/install-skills.py --target ~/.agents/skills --apply
```

Repeat `--target` for multiple directories. Add `--report /tmp/skills-install.json` to keep the action plan and original link targets. Without `--apply`, the installer only previews changes. Installed skills are available on the next turn; restart the host if its skill list has not refreshed.

## Choose a skill

Invoke a skill by name, such as `$v-auth`, `$v-readme`, or `$v-git`, with the task you want performed. [GEMINI.md](GEMINI.md) lists the collection. Reviews stay read-only; commit, push, and external publication require the corresponding user request. Personal Git work uses `main` and the configured human identity.

## Conservative housekeeping

Invoke `$v-reset-usage` in a repository for one unattended maintenance pass. It applies only small, verified internal dead-code removal or trivial deduplication, with a clean baseline, required checks, and a cumulative limit of five source files and 100 changed lines. Dependencies, schedules, sessions, and worktrees are audited without mutation; uncertain or protected changes are skipped. It does not reset account usage, commit, or push.

## Validate the collection

Use a local development environment for the YAML validator:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/check-skills.py
```

This checks every skill's frontmatter, duplicate names, local reference links, invocation metadata, and Python/shell/Node syntax. It prunes dependency and generated folders before scanning. Bash and Node must be available for their corresponding syntax checks.

Run all regression suites as well:

```bash
.venv/bin/python scripts/check-skills.py --tests \
  --skill-test-python /path/to/ml-project/.venv/bin/python
```

Repository tests use the validator's interpreter. Skill tests use `--skill-test-python` (the same interpreter by default); choose an existing environment with the dependencies required by those skills, including pandas, NumPy, and scikit-learn for baseline tests. Skipped tests produce an incomplete-check error instead of a successful validation. Add `--report /tmp/skills-check.json` for a machine-readable result, or `--json` for JSON output. Syntax checks run concurrently with a default of four workers; use `--jobs 1` for sequential execution.

To run just the repository tooling tests:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The tests cover collection validation, skipped-test detection, installation, repeat runs, nested skill discovery, conflict preservation, retired-link ownership, and source/destination isolation. The Skill Creator's `quick_validate.py` can additionally validate skill frontmatter. Domain helpers use the target project's Python or Node dependencies; avoid installing model or browser packages globally.
