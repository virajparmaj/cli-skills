---
name: v-post-launch
description: "Review a launched website’s indexing, canonical redirects, sitemap, metadata, and chosen analytics or promotion setup. Use for post-launch checks and explicitly requested fixes; external submissions, publishing, and optional marketing additions require the user’s authorization."
---

# Post-Launch Website Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.


## Quick Start

Run local discovery:

```bash
python3 "<skill-path>/scripts/audit_post_launch.py" --repo "<repo>" --json
```

Read [references/post-launch-playbook.md](references/post-launch-playbook.md) only for the checkpoints being investigated or implemented. The script reports static candidates, not confirmed production readiness. Verify deployed headers, generated routes, DNS settings, and external account state separately when access is available.

## Ten checkpoints and applicability

| Checkpoint | What to verify |
|---|---|
| Indexing directives | Remove unintended `noindex` only from public production pages meant for search. Preserve intentional exclusions and staging/private controls. |
| Search Console | Inspect authorized property state or verification artifacts. Missing source tags do not disprove DNS or account verification. |
| Analytics | Check the user’s chosen telemetry and any existing consent controls. Analytics is optional; adding it is a product choice. |
| robots.txt | Evaluate crawler groups and intended public paths; keep required rendering assets crawlable. `robots.txt` controls crawling, not authorization. |
| Canonical host | Follow HTTP/HTTPS and www/root variants, preserving paths and queries; verify a stable canonical destination and no loop. |
| Sitemap | Verify the deployed XML or index and canonical URLs. Separate file validity from submission/account status; use accurate modification dates. |
| Titles and descriptions | Inspect rendered metadata on representative indexable routes. Character counts are editorial guidance, not pass/fail rules. |
| Bing / IndexNow | Verify if chosen; distinguish verification, key availability, submission, and actual indexing. |
| Product Hunt | Optional promotion. Prepare drafts/assets only when relevant; check current platform requirements before recommending sizes or timing. |
| Trust badges | Optional. Show only verifiable claims; reserve space and measure loading cost if adding a badge is requested. |

## Implementation boundaries

An audit stays read-only. Apply explicitly requested local fixes within the active task, preserving intentional crawler controls, consent behavior, and existing canonical URLs. External account creation, DNS changes, sitemap submissions, analytics enablement, Product Hunt publishing, and outreach require authorization for that action. Prepare concrete reviewable files or drafts before asking for any missing approval.

Use the installed framework and hosting configuration rather than copying provider-specific templates blindly. Async scripts can still consume CPU and network; measure their effect. Reserve image space with dimensions or aspect ratio and choose loading priority based on visibility.

## Output

Return a scorecard of the ten checkpoints with `PASS`, `FAIL`, `WARN`, `N/A`, or `UNVERIFIED`, exact evidence, and any smallest fix. Explain applicability; do not count optional or unverified checks as failures. If reporting a score, show the numerator and denominator of applicable, verified checks and list unknowns separately.

Then give verified bugs with trigger, frequency x impact = score, rating reasons, confidence, and verification; a short prioritized action list; **Deferred issues**; and external steps still requiring access or authorization. Base `READY FOR TRAFFIC`, `FIXES NEEDED`, or `UNVERIFIED` on observed behavior. Use `BLOCKED FROM SEARCH` only with verified production evidence for intended public pages.
