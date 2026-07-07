---
name: v-chrome-extension
description: "Run a strict, production-grade pre-release Chrome Extension audit before Chrome Web Store submission. Use when asked to check policy compliance, permissions/privacy risk, security vulnerabilities, malicious behavior signals, functional and edge-case reliability, performance inefficiencies, listing metadata accuracy, and likely rejection causes. Key capabilities: least-privilege permission review, privacy-policy gap analysis, vulnerability triage with severity, test-matrix design, rejection-likelihood scoring, and reviewer-style rejection simulation. Trigger phrases: audit Chrome extension, CWS readiness check, pre-release extension review, why will this be rejected, extension security and permissions audit."
---

# Chrome Extension Pre-Release Audit

Use this skill to run a complete release-gate audit for Chrome extensions with strict Chrome Web Store standards.

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

- Assume Google-level reviewer strictness.
- Treat policy, privacy, and security findings as release blockers by default.
- Never mark an item as compliant without evidence from code, config, runtime behavior, or docs.
- Classify each claim as `verified`, `likely`, or `needs runtime confirmation`.
- Stay in audit mode unless the user explicitly asks for implementation fixes.

## Instructions

1. Confirm audit target.
   - Find extension roots by locating `manifest.json`.
   - If multiple manifests exist, audit each or confirm scope.
2. Gather evidence first.
   - Run [`scripts/discover-extension-surface.sh`](scripts/discover-extension-surface.sh) with the target repo path.
   - Read manifest, permission declarations, background/service worker logic, content scripts, popup/options pages, and external API usage.
3. Execute the full checklist in
   [references/chrome-extension-pre-release-audit-spec.md](references/chrome-extension-pre-release-audit-spec.md).
   - Cover all sections `1` through `14`.
   - Use the policy links embedded in the reference for compliance decisions.
4. Build mandatory audit tables.
   - Permission table: permission, where used, business necessity, least-privilege alternative, privacy disclosure status.
   - Data flow table: data type, source, purpose, storage, retention, sharing, user control.
5. Assess testing coverage.
   - Provide core flow checks, edge/failure scenarios, and missing automated tests.
6. Score rejection risk.
   - Compute rejection likelihood `0-100%` and list top rejection reasons with evidence.
7. Provide final verdict and rejection simulation.
   - Include reviewer-style rejection email with policy-aligned language and concrete remediation items.

## Output Contract

Return sections in this exact order:

1. Scope and assumptions
2. Policy and compliance audit (blockers first)
3. Permissions and privacy audit
4. Security and data handling vulnerabilities
5. Malicious or suspicious behavior assessment
6. Functional testing coverage and failures
7. Edge and failure testing coverage and gaps
8. Error handling and user safety findings
9. Performance and inefficiency findings
10. Code quality and maintainability findings
11. UX trust and transparency findings
12. Listing and store metadata risks
13. Common rejection trigger check + rejection likelihood score
14. Improvements beyond compliance
15. Final verdict:
   - approval readiness (`ready` or `not ready`)
   - critical issues (must fix)
   - medium issues (should fix)
   - safe areas
   - step-by-step action plan
16. Simulated Chrome Web Store rejection email (mandatory)

## Examples

Example 1  
User says: "Audit this extension before Chrome Web Store submission."
Actions:
1. Discover extension surfaces from manifest and code.
2. Run all `1-14` checklist sections.
3. Return blocker-first findings, rejection score, and fix plan.
Result: Release-gate audit with clear submission decision.

Example 2  
User says: "Why is this extension likely to be rejected?"
Actions:
1. Focus on permissions/privacy mismatches, undocumented behavior, and listing claims.
2. Map issues to policy-aligned rejection triggers.
3. Produce simulated reviewer email and prioritized remediation.
Result: Concrete rejection-risk explanation and submission-hardening plan.

## Troubleshooting

Skill does not trigger
- Use explicit requests like "run a Chrome Web Store pre-release audit."

No manifest found
- Confirm the repo contains an extension root with `manifest.json`.

Too many uncertain findings
- Add runtime confirmation steps (network throttling, permission denial, offline mode, API fault injection).

Privacy conclusions are weak
- Build explicit data-flow mapping and require policy text that matches real behavior.
