---
name: v-production
description: "Review-only production readiness and deployment safety audit. Use for pre-launch checks, release gates, and safe-to-deploy decisions in Vite/React apps with Vercel, Supabase, and/or FastAPI. Finds env and secret risks, demo-vs-prod gaps, auth and API trust issues, manifest and CI problems, observability gaps, and missing tests; reports VERIFIED vs UNVERIFIED findings with P0-P3 severity."
---

# Production Readiness Audit

## Practical review and implementation

- Do not design for rare or future cases nobody asked about.
- For each bug, report **frequency (1-10)** in current usage, **impact (1-10)**, **frequency x impact = score**, and the reachable trigger with evidence. Keep confidence separate from occurrence frequency; hypothetical future requirements are not bugs. Checklist examples are inspection prompts, not automatic findings or severity assignments.
- Default fix threshold: **5**, unless the user explicitly changes it. **Below 5:** record one deduplicated backlog issue and leave the code alone; use **Deferred issues** in the review if no backlog exists or remote issue creation is not already authorized. Do not block completion or reopen the same issue without new evidence or an explicit request.
- **5 or above:** propose the smallest verified fix; implement only within the authorized task. Review-only work stays review-only. Preserve existing report structure and add the scores to each finding. Required checks and explicitly requested fixes still apply.
- Pass evidence, scores, threshold, and deferrals to the fixer. Stop after the requested scope is covered and required checks pass; re-review affected paths only when changes, failures, or unresolved evidence justify it.

Stay in review mode. Do not edit files unless the user explicitly asks.

<!-- skill-operating-standard -->
## Operating standard — run at maximum capability

Run this skill in your highest-effort mode, whatever model you are. Prefer correctness and completeness over speed or brevity; if you support extended thinking or an adjustable reasoning effort, raise it for this work. Do not guess when you can verify.

- **Think first.** Before acting, plan: what the skill must produce, which files or scripts give ground truth, and where the likely failure modes are. Reason step by step internally before writing the answer.
- **Facts before judgment.** Run this skill's `scripts/` first (when it has them) and treat their output as the only ground truth. Never invent file paths, line numbers, metrics, or data a script did not produce. If a script cannot run, say so and mark every dependent conclusion UNVERIFIED.
- **Evidence discipline.** Label every claim `Confirmed from code` (you read the exact file:line and traced the logic), `Strongly inferred` (a pattern implies it but a runtime path could exonerate it), or `Not found — fill in manually`. A scanner/grep hit is not a finding until you open the file and confirm it in context.
- **Adversarial self-check.** After a first draft, run a second pass whose only job is to refute each finding: what input, config, or code path would make it false? Drop or downgrade anything you cannot defend. For subtle calls (leakage, statistics, security, correctness, money) reason from at least two independent angles before asserting.
- **Bound the review.** Cover the requested scope and verify plausible findings. Stop once that scope is covered and required checks pass; expand or repeat only for changed code, failed checks, or unresolved evidence. State coverage gaps; do not chase speculative cases to fill a report.
- **Use every tool you have.** When a capability (code execution, file read, web or docs lookup, subagents, parallel calls) is available and would raise accuracy, use it instead of answering from memory or a single pass.
- **Honesty.** If a category is clean, say so; do not pad with generic best-practice filler that has no evidence in this repo. State assumptions, gaps, and anything unverified plainly.
- **Contract.** Follow this skill's output contract exactly — strict format, severity ranks, verdict labels, smallest viable fix. For generator skills, every emitted value must trace to a computed fact or a cited line; label anything else inferred.

## First pass

1. Read repo context before judging risk:
   - `CLAUDE.md`, `README.md`, `.env.example`
   - `notes/03_architecture.md`, `notes/04_auth_and_roles.md`, `notes/09_dev_setup.md`
   - `notes/10_deployment.md`, `notes/11_known_issues.md`
2. Map the repo to a deployment tier before scoring anything:
   - Static SPA
   - SPA plus Supabase
   - SPA plus Vercel serverless
   - SPA plus external backend
   - Hybrid
3. Separate proven findings from absence-based concerns.
4. Do not re-report a documented known gap unless the docs are stale or the severity has escalated.

## Working method

- Start with file discovery, not assumptions.
- Prefer exact file evidence with line numbers.
- If deploy behavior depends on services not represented in the repo, say what is missing instead of guessing.
- Keep focus on deployment safety, production failure modes, and observability. Skip generic cleanup unless it changes launch risk.

Useful discovery commands:

```bash
find . -maxdepth 2 \( -name package.json -o -name vercel.json -o -name render.yaml -o -name Procfile -o -name Dockerfile -o -name docker-compose.yml -o -name '.env*' -o -name CLAUDE.md -o -path './notes/*' -o -path './.github/workflows/*' \) | sort
rg -n "VITE_[A-Z0-9_]+|localhost|127\\.0\\.0\\.1|onrender\\.com|vercel\\.app|localStorage|VITE_DEMO_MODE|service_role|anon_key|zod|joi|pydantic" .
rg --files -g 'supabase/migrations/*' -g 'api/**' -g 'backend/**' -g 'src/**' -g 'test/**'
```

## References

- Read [references/audit-checklist.md](references/audit-checklist.md) for the full tier map, risk checklist, severity model, required output fields, and optional add-ons.
- Read [references/workspace-patterns.md](references/workspace-patterns.md) for common Vite, React, Tailwind, Vercel, Supabase, and FastAPI failure patterns that should influence prioritization.

## Output contract

Produce sections in this order:

1. Deployment Topology
2. Findings
3. Unverified Concerns
4. Missing Test Coverage
5. Reusable Audit Patterns

Within Findings, group by `P0`, `P1`, `P2`, `P3`. Each finding must include:

- Title
- File evidence
- Production failure mode
- Smallest viable fix
- Smoke test or monitor
- VERIFIED or UNVERIFIED
