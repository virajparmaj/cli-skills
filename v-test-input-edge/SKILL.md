---
name: v-test-input-edge
description: Input and edge-case testing for web apps and APIs. Use when asked to validate empty, invalid, boundary, malformed, duplicated, concurrent, offline, stale-cache, large-payload, timezone, locale, session-expiry, and token-refresh behavior. Typical triggers include "edge case test this", "test weird inputs", "validate offline and reconnect", "check duplicate submits and races", and "stress input handling before release".
---

# Input & Edge Case Testing

Use this skill to run a focused, evidence-driven pass on risky input handling and real-world edge conditions.

## Instructions

Step 1: Confirm target and scope
- Identify the app/API, environment, and whether this is validation-only or includes fixes.
- Confirm whether to run full coverage (`2.1` to `2.11`) or a narrowed subset.

Step 2: Build the edge-case matrix
- Use [references/input-edge-checklist.md](references/input-edge-checklist.md) as the default matrix.
- For each scenario, define expected behavior, observable evidence, and pass/fail criteria.

Step 3: Execute high-risk scenarios first
- Prioritize security and data-integrity risks first: invalid input validation, duplicate submissions, race conditions, session expiry, token handling, and stale cache behavior.
- Capture exact repro steps, payload samples, and logs for every verified issue.

Step 4: Report with clear outcomes
- Return:
  - scope tested
  - verified findings (severity + impact + repro + evidence)
  - unverified concerns and blockers
  - recommended fixes and missing regression tests
  - readiness verdict (`ready`, `ready-with-risks`, or `not-ready`)

Step 5: If user asks for fixes
- Implement minimal, high-confidence fixes first.
- Re-run affected scenarios and report before/after behavior.

## Examples

Example 1:
User says: "Run edge-case testing on form inputs before release."
Actions:
1. Run `2.1`, `2.2`, `2.3`, and `2.9` first.
2. Validate server-side constraints, duplicate-submit protections, and cache invalidation.
3. Return reproducible findings and a release verdict.
Result: Input-risk report with prioritized fixes.

Example 2:
User says: "Only test offline/reconnect and session expiry behavior."
Actions:
1. Run `2.5` and `2.6` scenarios.
2. Validate queued writes, conflict handling, token refresh, and forced re-auth behavior.
3. Report failure modes with exact repro and expected handling.
Result: Focused resilience report for connectivity and auth lifecycle.

## Troubleshooting

Issue: No controlled way to simulate network conditions
Solution: Use browser devtools/network throttling, OS-level offline mode, or API gateway rate shaping; document simulation method used.

Issue: Race conditions are intermittent
Solution: Run repeated concurrent submissions with stable fixtures and request IDs; preserve timestamps and server logs for correlation.

Issue: Cannot verify token/session expiry timings reliably
Solution: Use short-lived test tokens or mocked clocks in non-prod environments and report exact expiry configuration.

Issue: Cache behavior differs by environment
Solution: Record cache layer details (browser, CDN, backend, query client) and test each layer with explicit invalidation and stale-read checks.
