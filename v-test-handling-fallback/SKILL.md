---
name: v-test-handling-fallback
description: "Audit and test application error handling and fallback behavior across UI, API, network, media, and third-party integrations. Use when asked to validate user-friendly error messages, API failure handling, timeouts and retries, partial failures, loading and empty states, media fallbacks, recovery flows, and silent failure risks. Key capabilities: map failure surfaces, execute scenario-based checks, report verified findings with file evidence, and propose smallest viable fixes plus missing tests. Trigger phrases: test error handling, validate fallback behavior, check retries and timeouts, why does this fail silently, test third-party failure paths, audit loading and empty states."
---

# Error Handling And Fallback Testing

Use this skill when the goal is to validate resilience, recovery, and user experience during failure conditions.

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
