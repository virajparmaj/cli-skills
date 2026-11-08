---
name: v-reset-usage
description: "Perform one conservative repository housekeeping pass: apply only small, verified internal dead-code removals or trivial deduplication, and audit dependencies, scheduled work, and storage without changing them. Use for unattended maintenance with minimal disruption; not broad refactoring or account-quota resets."
---

# Conservative repository housekeeping

Finish one useful maintenance pass without routine approval questions. Apply only the narrow changes permitted below; skip uncertainty and report it once. A successful run can make no changes. This skill does not reset account usage, exhaust a quota, or guarantee the absence of regressions.

Invoking this skill to clean a repository authorizes its small source edits. Discussing the skill or requesting a review does not. An explicit audit-only request overrides the editing workflow. Do not create a Goal unless the user explicitly asks; if a Goal already applies, keep its finish line to this single pass.

## Scope and defaults

- Target the explicitly named repository, otherwise the current repository. Never interpret `~/Work` as authorization to clean every project. No repository or an ambiguous multi-repository target means report the missing scope and make no changes.
- Read applicable AGENTS.md, repository instructions, manifests, documented checks, and supported entry points. The user's current instructions take precedence. Resolve helpers relative to this skill and pass the target separately.
- Respect Veer's stack as discovered: React/Vite/TypeScript/Tailwind/shadcn, FastAPI/Supabase/Vercel, Python/ML/statistics, or C/C++. Do not migrate stacks, replace project conventions, or assume old version pins are current requirements.
- Follow the personal `main` default, with contribution exceptions for open-source work and `github.com/saayam-for-all/data` (including clones/worktrees). Do not switch branches, create worktrees, or integrate history during housekeeping. If the checkout is not already appropriate under that policy, finish in audit mode. The rest of `~/Work` is not NGO work.
- No staging, commits, pushes, PRs, stashes, resets, branch deletion, deployment, remote submissions, or changes to Git identity. Separate explicit authorization for Git operations is handled through the user's Git workflow after cleanup.

## Allowlist for automatic edits

All conditions must hold: clean eligible checkout; passing baseline; established supported configuration; verified non-use or equivalence; existing adequate validation; small local change; no protected responsibility affected.

| Category | Permitted automatically | Otherwise |
| --- | --- | --- |
| Dead code | Remove a private, internal, unused definition or module with no loading/initialization effects; remove an unused type-only import or truly inert commented-out implementation | Keep and report |
| Duplication | Redirect local callers to an existing equivalent internal implementation and remove the redundant definition | Keep and report |
| Dependencies | Inspect direct declarations and actual tooling/runtime usage | No package, manifest, lockfile, environment, or install changes |
| Scheduled work | Inspect this project's schedules and available execution evidence | No triggering, disabling, rescheduling, or new automations |
| Storage | Inspect allowed metadata and estimate reclaimable space | No deleting, moving, archiving, pruning, or truncating anything |

No new abstraction, replacement library, compatibility shim, file move/rename, new file, formatting sweep, or broad refactor. Deduplication must have existing tests covering the relied-on contract; without them, retain both implementations. Do not modify tests to make cleanup pass. Removing an apparently unused value import is unsafe if module initialization might matter.

Default cumulative ceiling per invocation: **5 changed source files and 100 added + deleted lines**, including all batches. This is an extra limit, never proof that a small change is safe. Do not split work into more invocations or raise the ceiling to get around it. Leave additional candidates alone.

Protected responsibilities remain unchanged even when a removal looks small:

- Public exports/APIs, package interfaces, entry points, routes/URLs, feature behavior, UI structure/styling/accessibility, framework lifecycle, and configuration-driven registration.
- Authentication, authorization, Supabase RLS/storage policies, validation/security boundaries, secrets, environment variables, payments, and user permissions.
- Schemas, migrations, seeds, databases, persisted state, user files/assets, backups, datasets and provenance, notebooks and results, model artifacts, numerical/financial formulas, preprocessing, splits, backtests, or hardware/timing behavior.
- Tests/fixtures, dependency/build/toolchain configuration, CI/release/deployment settings, scheduler definitions, shared caches/environments, and applied history.

Do not call broader restructuring or audit skills in a way that widens this allowlist. A serious issue outside it gets reported, not silently fixed.

## One-pass workflow

### 1. Establish eligibility

Read [references/evidence.md](references/evidence.md) for the relevant candidate categories. Check current ownership, branch, worktree state, and known active tasks or unexpected file changes. Known concurrent editing or unstable checkout state means audit only. A checkpoint is not a lock; stable observations do not guarantee that no other process can write later.

Use a unique checkpoint in the host's temporary/scratch directory outside the target checkout. The helper writes that checkpoint only and does not change repository contents:

```bash
python3 <skill-dir>/scripts/guard.py capture --repo <repo> --output <new-checkpoint.json>
```

Inspect its JSON and exit status. A dirty/staged/untracked checkout, detached HEAD, pending Git operation, lock, or unavailable evidence prevents automatic source edits. Preserve all prior work; do not clean or stash it to obtain eligibility. Audit-only mode still completes the other accessible inspections. The helper is a structural guard, not a semantic safety verdict.

### 2. Inventory and validate the starting state

Inventory once with targeted searches and existing tooling; omit vendor/dependency/generated trees and Git history unless a specific candidate needs them. Delegating independent read-only inspection is useful; keep all edits serialized and pass the scope, allowlist, threshold, evidence, and deferrals to collaborators.

Identify repository-required build/type/lint/test checks and inspect their effects before running them. Use existing project environments and installed tools in non-watch mode. Do not run commands that deploy, train models, contact production, mutate real data, or execute scheduled jobs. Do not install packages or repair environments to manufacture a baseline.

Run all applicable required baseline checks once. Record commands and results. Missing, unsafe, failing, skipped, or materially inadequate required checks mean audit only. A genuinely inapplicable check is N/A with a reason; an unavailable one is not PASS. Do not fix unrelated baseline failures under this skill.

### 3. Select and apply verified candidates

Record the evidence, concrete maintenance benefit, supported roots/configurations checked, and exact permitted source paths before editing. No required minimum number of findings. Keep ambiguous dynamic/external consumers and near-duplicates unchanged.

Before each batch, verify that HEAD, branch, index, and current files still match the state you last observed. Run the guard's `verify` command below with the exact planned paths before editing as well as afterward; an ineligible planned path prevents the batch. Keep enough task-local patch information to undo only your edits; do not store sensitive source in a tracked report. If concurrent edits appear, stop editing and preserve them.

Apply only eligible candidates within the cumulative ceiling. Run focused checks per coherent batch. After each batch and before final acceptance, run the guard with the cumulative exact planned paths:

```bash
python3 <skill-dir>/scripts/guard.py verify --checkpoint <checkpoint.json> --allow src/private-helper.ts --allow src/caller.ts
```

Supply real relative paths, repeating `--allow` as needed. Never allow a whole directory or change the allowlist retroactively to accept an unexpected edit. Additional protected files discovered during inspection remain protected even if the helper's filename heuristics do not recognize them.

### 4. Verify or recover

Review the complete affected diff and callers for semantic regressions and protected responsibilities. Complete all required final checks. Keep source edits only if semantic review, the guard, and required checks pass.

On failure, repair only a verified eligible regression without expanding scope; otherwise undo your own failing batch. If final validation cannot pass, undo all source edits from this invocation, provided attribution is clear. Never restore whole files over concurrent work or run blanket checkout/reset/clean. If safe recovery is blocked, stop mutations and report the exact unresolved files; do not claim success. Passing checks establish the observed result, not universal safety.

### 5. Finish once

Re-scan only affected references after edits, then finish. Do not loop until quota runs out, create new maintenance tasks, or revisit skipped candidates without new evidence. Dependency/scheduler/storage inspections are read-only and do not wait for decisions. Do not generate destructive cleanup scripts by default.

For every actual verified bug: show the trigger and evidence, frequency (1–10) × impact (1–10) = score, reasons for both ratings, and separate confidence. Threshold **5**: lower scores remain unchanged in one deduplicated existing authorized backlog item, or **Deferred issues** if none exists. Scores at least 5 permit only an already-authorized allowlisted fix; they do not override protected responsibilities or audit-only mode. Ordinary maintenance candidates need evidence/benefit, not fabricated bug scores. No remote issue creation without authorization.

Return one concise report:

- **APPLIED**, **NO CHANGES**, **AUDIT ONLY**, or **INCOMPLETE** (unsafe recovery/unresolved regression).
- Target/branch and actual scope; applied files and added/deleted lines, or the reason edits were skipped.
- Baseline/final checks with exact commands, results, and coverage gaps. If reverted, state what was reverted and what remains.
- Dependency/scheduler/storage findings, distinguishing measured facts, estimates, unknowns, and inaccessible sources.
- Retained/deferred candidates with brief evidence and reasons; actual bugs use the scoring policy above.

Report in chat by default. Do not add reports, backlogs, or scripts to the checkout unless requested or the repository already requires the specific artifact. No routine approval questions: uncertain work is deliberately left unchanged. Request input only when a concrete unresolved condition actually requires it.
