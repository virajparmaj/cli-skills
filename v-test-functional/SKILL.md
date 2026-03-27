---
name: v-test-functional
description: Functional testing for web and app products with emphasis on real user behavior and interruption handling. Use when asked to run a functional test pass, validate end-to-end workflows (signup, login, checkout, upload), verify navigation and routing, test buttons/links/modals/dropdowns, check multi-step flows with back/refresh/duplicate-click interruptions, validate search/filter/sort, audit admin or restricted access paths, verify file import/export flows, or test ML/AI feature execution.
---

# Functional Testing

Use this skill to run evidence-based functional testing focused on user outcomes, access boundaries, and flow resilience.

## Instructions

Step 1: Confirm scope and environment
- Identify the target app, role types (guest/user/admin), environment, and whether this is read-only testing or test plus fixes.
- Confirm which flows are in scope and whether ML/AI behavior is expected to be deterministic.

Step 2: Build the functional matrix
- Use [references/functional-testing-checklist.md](references/functional-testing-checklist.md) as the baseline matrix.
- Cover sections `1.1` through `1.13` unless the user explicitly narrows scope.
- For each test, define preconditions, action, expected result, and observable evidence.

Step 3: Execute high-risk flows first
- Prioritize lockout and revenue risks first: signup/login, checkout/payment, upload/import, and admin restriction checks.
- Stress multi-step workflows with interruptions: back button, refresh, duplicate-clicks, retries, and resumed sessions.
- Validate both happy paths and misuse paths (invalid input, unauthorized access, interrupted actions).

Step 4: Capture findings with reproducible evidence
- Record each verified issue with exact repro steps, expected behavior, actual behavior, and impact.
- Attach concrete evidence where possible: logs, request/response snippets, timestamps, and UI state diffs.
- Mark uncertain items as unverified concerns instead of asserting defects.

Step 5: Return a release-focused summary
- Return:
  - scope and environment tested
  - pass/fail coverage for `1.1-1.13`
  - verified findings (severity + impact + repro)
  - unverified concerns and blockers
  - recommended fixes and missing tests
  - readiness verdict (`ready`, `ready-with-risks`, or `not-ready`)

Step 6: If the user asks for fixes
- Apply minimal, high-confidence fixes to the highest-risk defects first.
- Re-test impacted paths and report before/after behavior.

## Examples

Example 1:
User says: "Run functional testing for signup, login, checkout, and back-button behavior."
Actions:
1. Execute sections `1.1`, `1.4`, and `1.5`.
2. Validate user-state transitions and interruption handling in checkout.
3. Report failures with concrete reproduction and severity.
Result: Functional report with prioritized fixes and release risk.

Example 2:
User says: "Validate admin-restricted flows and import/export."
Actions:
1. Execute sections `1.7` and `1.8` with user and admin roles.
2. Attempt unauthorized access via direct routes and API requests.
3. Validate import/export file integrity and permission enforcement.
Result: Access-control and data-flow validation with clear pass/fail evidence.

## Troubleshooting

Issue: Test environment is unstable or missing services  
Solution: Run a reduced-scope pass on stable flows, clearly label confidence limits, and avoid declaring full release readiness.

Issue: Browser/device behavior is inconsistent  
Solution: Prioritize highest-traffic browser/device combinations first and list untested combinations explicitly.

Issue: Duplicate-click or refresh defects are intermittent  
Solution: Add controlled network delay/throttling, record exact timing, and capture request traces per attempt.

Issue: ML/AI output varies across runs  
Solution: Validate execution success, policy guardrails, retries, and fallback behavior separately from model-quality variance.
