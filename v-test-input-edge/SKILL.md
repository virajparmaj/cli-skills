---
name: v-test-input-edge
description: Input and edge-case testing for web apps and APIs. Use when asked to validate empty, invalid, boundary, malformed, duplicated, concurrent, offline, stale-cache, large-payload, timezone, locale, session-expiry, and token-refresh behavior. Typical triggers include "edge case test this", "test weird inputs", "validate offline and reconnect", "check duplicate submits and races", and "stress input handling before release".
---

# Input & Edge Case Testing

Use this skill to run a focused, evidence-driven pass on risky input handling and real-world edge conditions.

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
