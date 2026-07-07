---
name: v-macos
description: "Pre-release Mac App Store readiness audit for macOS apps. Use when asked to verify a macOS app before App Store submission, run a ship/no-ship gate, check sandbox/privacy/security/metadata compliance, validate reviewer-access paths, or identify common rejection risks. Key capabilities: execute a structured release checklist, classify findings by confidence and severity, produce submission-ready gaps, and return a clear readiness verdict with smallest viable next fixes. Trigger phrases: Mac App Store readiness, pre-submit audit, App Store rejection check, macOS release checklist, ship/no-ship for mac app, review App Store compliance."
---

# macOS App Store Release Readiness

Use this skill to run an evidence-based pre-submission audit for macOS apps targeting the Mac App Store.

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

- Treat policy and compliance gaps as release blockers unless the user explicitly accepts risk.
- Never mark an item as passed without evidence (code, config, metadata, runtime behavior, or reproducible test notes).
- Separate `verified`, `likely`, and `needs runtime confirmation` clearly.

## Instructions

Step 1: Confirm scope and release target
- Identify the app, branch/build, target macOS version, and whether this pass is read-only or includes fixes.
- Confirm whether this is a final pre-submit gate or an early dry run.

Step 2: Gather release artifacts
- Collect: app metadata draft, screenshots/previews, "What's New", privacy policy URL, support URL, review notes, demo credentials, and IAP config (if used).
- Confirm reviewer access path for login-gated features.

Step 3: Run the baseline checklist
- Use [references/mac-app-store-release-readiness-checklist.md](references/mac-app-store-release-readiness-checklist.md).
- Cover sections `1` through `12` unless the user explicitly narrows scope.
- Prioritize hard blockers first: section `1`, section `2`, section `3`, and section `9`.

Step 4: Validate with evidence
- For each section, record:
  - expected requirement
  - observed behavior
  - evidence source (file path, config, command output, repro steps, screenshots, or runtime note)
  - confidence (`verified`, `likely`, `needs runtime confirmation`)
- Flag policy-critical behaviors immediately: unsandboxed writes, downloaded executable code, custom updater paths, privilege escalation, misleading metadata, or missing reviewer access.

Step 5: Assess rejection risk
- Map findings to likely rejection triggers using section `10`.
- Identify impacted user flow and reviewability risk (for example, reviewer cannot access a core feature).

Step 6: Return ship/no-ship verdict
- Return:
  - scope tested and assumptions
  - blocker findings
  - non-blocker findings
  - unverified runtime checks
  - submission package gaps
  - verdict: `ship`, `ship-with-risks`, or `no-ship`
- If the user asks for fixes, apply smallest viable changes first, then re-check impacted checklist sections.

## Output Contract

Return these sections in order:

1. Scope and assumptions
2. Blockers (policy/compliance/reviewer-path)
3. Non-blocking issues
4. Runtime confirmations still needed
5. Submission package checklist status
6. Final verdict (`ship`, `ship-with-risks`, or `no-ship`)
7. Prioritized next actions

## Examples

Example 1:
User says: "Run a Mac App Store readiness check before I submit."
Actions:
1. Execute sections `1-12` from the reference checklist.
2. Validate hard blockers first, then metadata and performance.
3. Return a ship/no-ship verdict with submission gaps.
Result: Submission-ready risk report with prioritized fixes.

Example 2:
User says: "Only check likely App Store rejection reasons for this mac app."
Actions:
1. Focus on sections `1`, `2`, `3`, `9`, and `10`.
2. Verify reviewer access, sandbox behavior, privacy disclosures, and metadata truthfulness.
3. Return blocker list plus exact evidence and remediation steps.
Result: Focused rejection-risk audit for fastest pre-submit cleanup.

## Troubleshooting

Issue: Skill does not trigger reliably
Solution: Use direct phrases like "Mac App Store pre-submit audit" or "ship/no-ship for macOS App Store".

Issue: Too many speculative findings
Solution: Downgrade uncertain checks to `needs runtime confirmation` and list exact runtime validation steps.

Issue: Metadata not available yet
Solution: Run a partial technical pass, mark section `6` and section `9` as pending, and avoid claiming full readiness.

Issue: Login-only app blocks reviewer flow
Solution: Require working review credentials or a compliant demo mode before a `ship` verdict.
