# Evidence for conservative housekeeping

Read only the sections needed for the current candidates. Treat scanner output as leads; absence from a pattern match is not evidence of non-use. Do not turn this pass into a full architecture, security, ML, or performance audit.

## Private dead code

- Map the actual supported entry points: application startup, framework-discovered routes/components, CLI/module launchers, jobs, tests/fixtures, build scripts, package exports, and generated-code inputs.
- Check repository references, re-exports, configuration, decorators/registries, string lookup, dynamic imports, plugin discovery, and import side effects. A zero-match `rg` search alone cannot authorize deletion.
- Public APIs can have consumers outside the checkout. Exported/published entry points, compatibility code, and private-looking symbols exposed through serialization or reflection stay unchanged if consumer evidence is incomplete.
- A flag off in the current environment can remain supported elsewhere. Without establishing all supported configurations, retain its branch.
- A function that has no callers can still be registered by a decorator. A class definition can invoke metaclass, inheritance, static initializer, annotation, or registration behavior. Keep any candidate whose initialization effects are uncertain.
- Do not remove test-only utilities, historical migrations, configuration samples, legal notices, operational documentation, or build inputs merely because application entry points do not import them.
- Type-only import deletion must use the language's actual type-only semantics. Other imports require establishing that initialization is unnecessary; do not infer this from an unused binding.
- No whole-file deletion until module initialization and every supported loading path have been checked. Stay within the same source-file and line limits.

## Trivial exact duplication

- Compare supported inputs, outputs, defaults, exceptions, side effects, mutation, ordering, async behavior, state ownership, and framework lifecycle. Similar text or matching test examples alone is insufficient.
- Choose an existing implementation for its actual contract, clear dependency direction, and current test coverage. Check for newly introduced dependency cycles or module initialization changes.
- Existing tests must cover the contract relied on by callers. Do not add new tests/abstractions to justify a larger refactor under this skill; retain the candidate instead.
- Preserve small differences that encode business rules. No new generic helper, configuration flags, public adapter, UI restructuring, or cross-domain extraction.

## Dependency audit only

- Inventory direct declarations by workspace and category. Check source, configuration, plugins, scripts, CI, code generation, public types, optional/peer contracts, and runtime loading.
- Distinguish verified unused, overlap with meaningful differences, and unknown. Never remove a package here, even a development dependency. Do not edit lockfiles or uninstall/reinstall packages.
- A short custom replacement is not a benefit by itself. Note compatibility and maintenance costs only when relevant to a concrete candidate.
- Use existing measurements if available. Distinguish direct declarations, resolved packages, installed size, production bundle size, and compressed delivery size. No network download or reinstall just to measure. A package still needed transitively may produce no space savings; label estimates.

## Scheduled-work audit only

- Start with this repository's scheduled CI definitions and timer-driven scripts. Inspect current-user cron/launchd and app scheduled tasks only through available supported tools, and connect findings to this repository by command/path or verified purpose. Do not expand to unrelated account/project audits.
- Use native app/scheduler tools when available; do not read internal app databases. No privileged access or permission workarounds. Record inaccessible sources once and continue.
- Record ID/source, purpose, enabled/installed state, cadence/timezone, outputs/consumers, latest known success, and available runtime/cost evidence. A defined schedule does not prove it is active.
- Use the last 30 days with explicit start/end timestamps and timezone. Separate observed success/failure, retries, skips/cancellations, and expected opportunities. State history retention. No records means unknown, not zero runs or zero failures.
- Classify keep, reduce-frequency candidate, disable candidate, or unknown. Include the concrete consequence of a proposed change. Backups, health/security checks, and compliance jobs can be valuable without regular readership; missing telemetry is not proof of waste.
- Compare actual purpose, environment, inputs, outputs, consumers, and recovery role before calling jobs redundant. No execution, test notification, schedule mutation, or follow-up automation. Redact secrets from commands/log evidence.

## Storage audit only

- Use filesystem metadata for the configured Codex home (otherwise `~/.codex`) and this project's registered worktrees. No session/log bodies, source contents for this audit, credentials, databases, or internal application-state files. Read-only Git status/refs/ancestry and supported app lifecycle metadata are permitted.
- Do not follow symlinks outside those roots. Reuse one metadata inventory, avoid rescanning nested dependency trees, and skip inaccessible sources without seeking broader access. Git inspections must not fetch, prune, clean, or create worktrees.
- Group session sizes by modification month and label the timestamp basis. Retained history stays review-first without an explicit retention policy. Age alone does not establish disposability.
- For worktrees record branch/HEAD, allocated size, tracked/untracked/ignored filenames, locks/activity where verifiable, pending Git operations, ancestry against the correct integration branch, and remote preservation evidence/freshness. Do not print sensitive file contents.
- Unpublished commits, no reliable remote evidence, unknown activity, squash-merge uncertainty, ignored personal files, or incomplete inspection all mean review-first. Always preserve current/primary worktrees. Inactivity cannot be inferred from an old directory timestamp.
- Respect native lifecycle and snapshot behavior for app-managed worktrees. Do not archive chats or remove worktrees during this audit.
- Identify cache/build candidates only when regeneration and ownership are established from already-known project configuration or supported tooling. Unknown cache contents stay review-first. No filesystem, cache, session, or worktree deletion under this skill.
- Deduplicate nested paths and report eligible-looking estimates separately from review-first estimates. Allocated sizes are potential savings, not promises: hard links, APFS clones, snapshots, and regeneration can change reclaimed space.
