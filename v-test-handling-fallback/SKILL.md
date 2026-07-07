---
name: v-test-handling-fallback
description: "Audit and test application error handling and fallback behavior across UI, API, network, media, and third-party integrations. Use when asked to validate user-friendly error messages, API failure handling, timeouts and retries, partial failures, loading and empty states, media fallbacks, recovery flows, and silent failure risks. Key capabilities: map failure surfaces, execute scenario-based checks, report verified findings with file evidence, and propose smallest viable fixes plus missing tests. Trigger phrases: test error handling, validate fallback behavior, check retries and timeouts, why does this fail silently, test third-party failure paths, audit loading and empty states."
---

# Error Handling And Fallback Testing

Use this skill when the goal is to validate resilience, recovery, and user experience during failure conditions.

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

## CRITICAL

- Stay in testing and audit mode unless the user explicitly asks for code changes.
- Never report a failure without showing concrete evidence (file paths, logs, or reproducible steps).
- Prioritize user impact: broken flows, silent failures, data loss, or unrecoverable states.

## Instructions

1. Identify the target repo.
   - If the user says "this repo", use the current working directory.
2. Run [`scripts/discover-error-surface.sh`](scripts/discover-error-surface.sh) first.
   - Use its output to locate likely failure and fallback hotspots.
3. Read context before judging behavior.
   - Prefer `CLAUDE.md`, `README*`, `notes/*`, API contracts, and test setup docs when present.
4. Execute the test checklist from
   [references/error-handling-fallback-test-spec.md](references/error-handling-fallback-test-spec.md).
   - Cover all twelve dimensions:
     - clear, user-friendly error messages
     - API failures and unexpected responses
     - network timeouts and retries
     - partial failure handling
     - loading states (spinners, skeletons, disabled UI)
     - empty states and first-time user states
     - image and media fallback behavior
     - third-party service failure handling
     - retry and recovery flows
     - no silent failures or broken UI states
5. Classify each result as `verified`, `likely`, or `needs runtime confirmation`.
6. Return a prioritized report with reproducible steps and smallest viable fixes.

## Output Contract

Return these sections in order:

1. Scope and assumptions
2. Verified findings (severity, evidence, repro, impact)
3. Likely risks requiring runtime confirmation
4. Missing tests by failure category
5. Prioritized fix plan (smallest viable fixes first)
6. Regression guardrails to prevent recurrence

## Examples

Example 1
User says: "Test fallback behavior before launch"
Actions:
1. Run surface discovery script.
2. Validate all ten failure categories from the reference checklist.
3. Produce severity-ranked findings with exact file references.
Result: Launch-readiness report with concrete fixes and missing tests.

Example 2
User says: "Why does this screen fail silently when API errors?"
Actions:
1. Trace request path and error boundaries.
2. Confirm whether UI state transitions on failure.
3. Check logs and telemetry hooks for swallowed errors.
Result: Root cause, affected paths, and minimal remediation plan.

## Troubleshooting

Skill does not trigger
- Make request wording explicit, for example: "audit error handling and fallback flows".

Too many generic findings
- Narrow scope to one user flow, then expand to all ten categories.

No runtime evidence available
- Mark as `needs runtime confirmation` and provide exact test steps to validate.

False positives from static scan
- Re-check with runtime logs, integration tests, or network interception before marking as verified.
