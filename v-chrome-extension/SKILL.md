---
name: v-chrome-extension
description: "Review Chrome extensions for Chrome Web Store submission, permission and privacy mismatches, security, reliability, and listing accuracy. Use for an extension audit or rejection-risk review; verify applicable policy against current official sources."
---

# Chrome Extension Pre-Release Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


Use this skill to run a complete release-gate audit for Chrome extensions with strict Chrome Web Store standards.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.


## Workflow

1. Identify extension roots from `manifest.json`; inspect the manifest to distinguish an extension from unrelated web-app manifests. For a focused request, audit the selected surface; for a full pre-release audit, cover the applicable sections of the reference.
2. Run `bash "<skill-path>/scripts/discover-extension-surface.sh" "<repo>"`. Read the manifest, service worker/background code, content scripts, UI, external APIs, and listing/privacy artifacts. The helper caps output; inspect additional matches when they affect coverage.
3. Read [references/chrome-extension-pre-release-audit-spec.md](references/chrome-extension-pre-release-audit-spec.md) and verify policy conclusions against its current official Chrome links. Distinguish observed behavior from policy interpretation and untested concerns.
4. For a full audit, build permission and data-flow tables. Map each permission to actual use and each collected data type to purpose, storage, retention, sharing, and user controls.
5. Check the extension’s actual runtime flows where available: service-worker suspension, permission denial, offline behavior, API failure, and upgrades. Mark unrun tests as unverified rather than failed.
6. Report evidence-backed submission risk as low, moderate, or high. If the user asks for a numeric score, label it a subjective rubric score with its basis; do not present an uncalibrated percentage as a probability of store rejection.

## Output

For a full audit, use the reference’s sections: scope; policy; permissions/privacy; security; suspicious behavior; functional/edge/error tests; performance; maintainability; UX trust; listing; rejection risks; improvements; verdict and action plan. A focused request may omit unrelated sections.

Every bug includes its reachable trigger, frequency and impact with reasons, score, confidence, exact evidence, smallest fix, and verification. Separate unverified concerns and **Deferred issues**. Missing optional features do not determine submission readiness.

Use `ready`, `not ready`, or `unverified` with the concrete basis. A simulated rejection email is an optional draft when requested or useful for explaining confirmed policy issues; label it clearly and do not manufacture rejection reasons when none were verified.

If no extension manifest exists, report the searched scope and stop. Do not submit to the store, change listing/privacy declarations, or contact reviewers without authorization.
