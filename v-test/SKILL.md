---
name: v-test
description: "Test requested functional flows, error recovery, input boundaries, or system reliability in an existing app or API. Report reproducible failures and coverage limits; edit only when fixes are authorized."
---

# Unified Testing & Reliability Suite

Run evidence-based functional, error handling, edge case, and system reliability testing across web apps, desktop software, and backend APIs.

## Practical review and implementation

- Do not design for rare or future cases nobody asked about.
- For each bug, report **frequency (1-10)** in current usage, **impact (1-10)**, **frequency x impact = score**, and the reachable trigger with evidence. Briefly justify both ratings from current usage and the observed consequence. Keep confidence separate from occurrence frequency; hypothetical future requirements are not bugs. Checklist examples are inspection prompts, not automatic findings or severity assignments.
- Default fix threshold: **5**, unless the user explicitly changes it. **Below 5:** record one deduplicated backlog issue and leave the code alone; use **Deferred issues** in the review if no backlog exists or remote issue creation is not already authorized. Do not block completion or reopen the same issue without new evidence or an explicit request.
- **5 or above:** propose the smallest verified fix; implement only within the authorized task. Review-only work stays review-only. Preserve existing report structure and add the scores to each finding. Required checks and explicitly requested fixes still apply.
- Pass evidence, scores, threshold, and deferrals to the fixer. Stop after the requested scope is covered and required checks pass; re-review affected paths only when changes, failures, or unresolved evidence justify it.

Stay in review mode. Do not edit files unless the user explicitly asks for fixes.

## Evidence and execution

Choose checks from reachable features and the requested mode. Reproduce failures with the relevant input and configuration; keep scanner candidates, untested paths, and observed failures separate.

Resolve bundled `scripts/` and `references/` from the directory containing this `SKILL.md`, and pass the target repository explicitly. If a helper cannot run, inspect the relevant source directly and state the remaining verification gap. Stop after the requested deliverable and applicable checks are complete.

## Workflow

### 1. Discover Testing Surfaces
Run the error and boundary surface discovery script:
```bash
bash scripts/discover-error-surface.sh /absolute/path/to/repo
```
This identifies API failure points, mutation endpoints, form inputs, toast/error boundaries, and offline caching logic.

### 2. Select Test Mode(s)

Choose the mode matching the user's request (or run all 4 for a full pre-release audit):

#### Mode A: Functional User Flows
Follow [references/functional-testing-checklist.md](references/functional-testing-checklist.md):
- Core user journeys (signup, onboarding, primary CRUD, checkout, export/download).
- Route navigation, query parameter persistence, and deep linking.
- Interruption testing: page refresh during multi-step forms, browser back/forward, double-clicking action buttons.
- State persistence across tab closures and local storage rehydration.

#### Mode B: Error Handling & Fallbacks
Follow [references/error-handling-fallback-test-spec.md](references/error-handling-fallback-test-spec.md):
- Network failure, HTTP 4xx/5xx handling, and timeout behavior.
- UI state completeness: **Loading**, **Empty**, **Error**, and **Retry** states on every view.
- Degradation fallbacks: fallback heuristics when backend API is unreachable or rate-limited.
- Silent failure detection: unhandled promise rejections, swallowed catch blocks without user feedback.

#### Mode C: Input & Boundary Edge Cases
Follow [references/input-edge-checklist.md](references/input-edge-checklist.md):
- Boundary values: empty strings, max-length overflow, negative values, Unicode/special characters.
- Concurrent and duplicate submits (rapid clicking, optimistic UI race conditions).
- Malformed data payloads, partial schema migrations, and stale localStorage formats.
- Offline behavior: offline mutations, reconnection sync, and conflict resolution.

#### Mode D: System Reliability & Release Gate
Follow [references/system-reliability-checklist.md](references/system-reliability-checklist.md):
- Authentication & authorization boundary integrity across routes and endpoints.
- Environment & deployment consistency (local vs production environment variables).
- Logging, error traceability, and Sentry/monitoring readiness.
- Crash recovery: can the application recover cleanly from unexpected runtime errors?

## Output Contract

Return a structured report with:

```markdown
# Test & Reliability Audit Report

## Executive Summary
- **Overall Verdict**: PASS / CONDITIONAL PASS / FAIL
- **Modes Covered**: Functional | Fallback | Edge Case | System Reliability
- **Total Findings**: N (P0: X, P1: Y, P2: Z)

## Verified Findings
For each verified finding:
- **Title**: [P0-P3] Short issue description
- **Evidence**: `path/to/file.ts:line` (exact code reference)
- **Score**: Frequency (1-10) x Impact (1-10) = Score, with a brief reason for each rating
- **Reachable Trigger**: Concrete user action or input causing the failure
- **Smallest Verified Fix**: Minimal code diff to resolve the defect

## Unverified / Hypothetical Concerns
(Concerns not reproducible or missing code evidence)

## Deferred Issues
Deduplicated findings below the threshold, with scores and no code changes.

## Missing Test Cases
Only meaningful regression coverage for verified behavior or required acceptance checks.

## Verification Limits
Paths not exercised and checks that could not run; do not label them passing.
```
