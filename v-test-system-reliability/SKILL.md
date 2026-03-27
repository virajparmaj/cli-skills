---
name: v-test-system-reliability
description: System and reliability testing for web products and APIs. Use when asked to run a system-test pass, reliability audit, pre-release quality gate, or end-to-end validation across authentication and authorization behavior, input sanitization and security cases, load and large-data performance, responsive and cross-browser behavior, accessibility, frontend-backend state consistency, deployment or environment mismatch scenarios, logging and error traceability, and recovery from crashes or interrupted flows. Typical triggers include "system test this repo", "do a reliability pass", "test auth + recovery", "check cross-browser and accessibility", and "find deployment mismatch issues before launch".
---

# System & Reliability Testing

Use this skill to run a practical, evidence-based system test across security, performance, compatibility, accessibility, state integrity, and recovery.

## Instructions

Step 1: Confirm target and constraints
- Identify the target repo/app, environment(s), and whether this is read-only validation or includes fixes.
- Confirm acceptance criteria (release gate, bug sweep, regression check, or incident follow-up).

Step 2: Build the test matrix
- Use [references/system-reliability-checklist.md](references/system-reliability-checklist.md) as the baseline matrix.
- Cover sections `4.1` through `4.13` unless the user explicitly narrows scope.
- Map each test to expected behavior and observable evidence (logs, traces, screenshots, failing requests, or repro steps).

Step 3: Execute and capture evidence
- Prioritize high-risk paths first: auth boundaries, input handling, state sync, and crash recovery.
- Record every verified issue with exact reproduction steps and concrete impact.
- Mark uncertain items clearly as unverified instead of assuming failure.

Step 4: Summarize with release-oriented output
- Return:
  - system scope tested
  - verified findings (severity + impact + repro + evidence)
  - unverified concerns / blockers
  - recommended fixes and missing tests
  - release readiness verdict (`ready`, `ready-with-risks`, or `not-ready`)

Step 5: If the user asks for fixes
- Implement minimal, high-confidence fixes first.
- Re-run the affected tests and report before/after behavior.

## Examples

Example 1:
User says: "Run a system reliability pass before launch."
Actions:
1. Build the full `4.1-4.13` matrix.
2. Validate authz boundaries, sanitization, load, responsive/browser coverage, a11y, state sync, deploy parity, logging, and recovery.
3. Return findings with a release verdict.
Result: Launch decision with reproducible issues and prioritized fix order.

Example 2:
User says: "Only check crash recovery and logging traceability."
Actions:
1. Run `4.9` and `4.10` scenarios first.
2. Validate correlation IDs, stack traces, retry behavior, and partial-state recovery.
3. Report gaps with exact repro and expected telemetry.
Result: Focused reliability report for observability and resilience.

## Troubleshooting

Issue: No staging environment available  
Solution: Use local/prod-like config, clearly label confidence limits, and avoid claiming full release readiness.

Issue: Browser/device coverage is incomplete  
Solution: Test the highest-traffic targets first and explicitly list untested combinations.

Issue: Cannot reproduce intermittent failures  
Solution: Increase logging/trace depth, capture timestamps and request IDs, and run repeated attempts with the same dataset.

Issue: Frontend and backend results disagree  
Solution: Compare API payloads, persistence layer state, and client cache invalidation to isolate the desync boundary.
