---
name: v-scripts
description: "Review repository efficiency: dead code, duplicate work, slow scripts, builds and startup, oversized dependencies, and wasted compute or I/O. Use for engineering cleanup and bottleneck audits; distinguish measured costs from candidates."
---

# Repo Efficiency Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


Stay in audit mode unless the user explicitly asks for code changes.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

## Workflow

1. Confirm the target repo. If the user says "this repo", use the current working directory.
2. Run [`scripts/surface-map.sh`](scripts/surface-map.sh) first to collect docs, manifests, entrypoints, scripts, build tooling, CI files, large files, and likely performance-sensitive patterns while skipping generated folders.
3. Read the highest-value context that exists before making claims:
   - `CLAUDE.md`
   - `README*`
   - dependency manifests and lockfiles
   - build config
   - CI or release config
   - startup or bootstrap entrypoints
   - architecture or notes docs
4. Use [`references/audit-playbook.md`](references/audit-playbook.md) as the audit contract for scope, evidence rules, confidence labels, output format, and prioritization.
5. Classify each claim as `measured`, `likely`, or `speculative`. If runtime behavior is unknown, say what evidence exists and what still needs measurement.
6. Prefer high-confidence, high-impact findings over generic best practices.

## Priorities

Focus first on:

- dead code, stale files, unused dependencies, and stale scripts
- duplicated logic, repeated parsing or transforms, and overlapping tooling
- slow startup paths, blocking synchronous work, repeated scans, and avoidable I/O
- build, test, release, and automation steps that can be cached, skipped, parallelized, or made incremental
- oversized packages, bundles, binaries, and assets with low payoff
- maintainability problems that directly increase runtime, size, cost, or fragility

## Output

Return the sections from [`references/audit-playbook.md`](references/audit-playbook.md):

1. Executive Summary
2. Findings
3. Dead Code Candidates
4. Redundancy Candidates
5. Performance Opportunities
6. Action Plan
7. Measurement Plan

Close with short ranked lists of supported changes, wasted compute, latency sources, and safe cleanup candidates. Include only evidence-backed items; do not fill quotas or list the same root cause multiple times.
