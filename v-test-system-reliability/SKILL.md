---
name: v-test-system-reliability
description: System and reliability testing for web products and APIs. Use when asked to run a system-test pass, reliability audit, pre-release quality gate, or end-to-end validation across authentication and authorization behavior, input sanitization and security cases, load and large-data performance, responsive and cross-browser behavior, accessibility, frontend-backend state consistency, deployment or environment mismatch scenarios, logging and error traceability, and recovery from crashes or interrupted flows. Typical triggers include "system test this repo", "do a reliability pass", "test auth + recovery", "check cross-browser and accessibility", and "find deployment mismatch issues before launch".
---

# System & Reliability Testing

Use this skill to run a practical, evidence-based system test across security, performance, compatibility, accessibility, state integrity, and recovery.

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
