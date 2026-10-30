---
name: v-vibe-app
description: "Review-only post-vibe audit for full-stack SaaS web applications, mobile backends, and APIs. Audits the 19 distributed systems pillars (rate limiting, caching, queues, circuit breakers, timeouts, retries, idempotency, sagas), the 80+ enterprise production readiness checklist (database migrations, non-blocking indexes, connection pooling, integer money, RLS, IDOR prevention, MFA, SAML/SSO, SCIM, billing, webhooks, audit logs), Codebase Slop indicators (implicit coupling, layer-first folders, duplication, representable illegal states, god files, shotgun surgery, layering violations, pass-through wrappers, errors/validation not at boundary), Design Slop indicators (badge spam, italicized words, instrument serif + negative kerning, over-detailed UI, dividers, multiple color opacities, containers with borders, superfluous diagrams, code breadcrumbs, section numbering), and the Pre-Launch 20 release gate. Trigger on audit app, audit saas, audit backend, v-vibe-app, v-vibe-saas, distributed systems audit, enterprise readiness audit, codebase slop, backend slop."
---

# Post-Vibe SaaS Application & Backend Audit

## Practical review and implementation

- Do not design for rare or future cases nobody asked about.
- For each bug, report **frequency (1-10)** in current usage, **impact (1-10)**, **frequency x impact = score**, and the reachable trigger with evidence. Keep confidence separate from occurrence frequency; hypothetical future requirements are not bugs. Checklist examples are inspection prompts, not automatic findings or severity assignments.
- Default fix threshold: **5**, unless the user explicitly changes it. **Below 5:** record one deduplicated backlog issue and leave the code alone; use **Deferred issues** in the review if no backlog exists or remote issue creation is not already authorized. Do not block completion or reopen the same issue without new evidence or an explicit request.
- **5 or above:** propose the smallest verified fix; implement only within the authorized task. Review-only work stays review-only. Preserve existing report structure and add the scores to each finding. Required checks and explicitly requested fixes still apply.
- Pass evidence, scores, threshold, and deferrals to the fixer. Stop after the requested scope is covered and required checks pass; re-review affected paths only when changes, failures, or unresolved evidence justify it.

Use this skill when auditing a full-stack SaaS application, web app backend, or API. Stay in review mode unless the user explicitly requests implementation.

<!-- skill-operating-standard -->
## Operating standard — run at maximum capability

Run this skill in your highest-effort mode, whatever model you are. Prefer correctness and completeness over speed or brevity; if you support extended thinking or an adjustable reasoning effort, raise it for this work. Do not guess when you can verify.

- **Think first.** Before acting, plan: what the skill must produce, which files or scripts give ground truth, and where the likely failure modes are. Reason step by step internally before writing the answer.
- **Facts before judgment.** Run this skill's `scripts/` first (when it has them) and treat their output as the only ground truth. Never invent file paths, line numbers, metrics, or data a script did not produce. If a script cannot run, say so and mark every dependent conclusion UNVERIFIED.
- **Evidence discipline.** Label every claim `Confirmed from code` (you read the exact file:line and traced the logic), `Strongly inferred` (a pattern implies it but a runtime path could exonerate it), or `Not found in repository`. A scanner/grep hit is not a finding until you open the file and confirm it in context.
- **Adversarial self-check.** After a first draft, run a second pass whose only job is to refute each finding: what input, config, or code path would make it false? Drop or downgrade anything you cannot defend. For subtle calls (leakage, statistics, security, correctness, money) reason from at least two independent angles before asserting.
- **Bound the review.** Cover the requested scope and verify plausible findings. Stop once that scope is covered and required checks pass; expand or repeat only for changed code, failed checks, or unresolved evidence. State coverage gaps; do not chase speculative cases to fill a report.
- **Use every tool you have.** When a capability (code execution, file read, web or docs lookup, subagents, parallel calls) is available and would raise accuracy, use it instead of answering from memory or a single pass.
- **Honesty.** If a category is clean, say so; do not pad with generic best-practice filler that has no evidence in this repo. State assumptions, gaps, and anything unverified plainly.
- **Contract.** Follow this skill's output contract exactly — strict format, severity ranks, verdict labels, smallest viable fix.

## Quick Start

1. Run the deterministic scanner:
   ```bash
   python3 "<skill-path>/scripts/audit_app_vibe.py" --repo "<repo>"
   ```
2. Read the domain references before evaluating:
   - [references/distributed-systems-resilience.md](references/distributed-systems-resilience.md) for the 19 distributed systems pillars
   - [references/enterprise-production-checklist.md](references/enterprise-production-checklist.md) for the 80+ enterprise production criteria
   - [references/prelaunch-20-checklist.md](references/prelaunch-20-checklist.md) for the pre-launch release gate

## Workflow

### 1. Absorb Context & Architecture
- Read `README.md`, `CLAUDE.md`, `package.json` / `pyproject.toml` / `go.mod`, database schema files, migration histories, and Docker/Kubernetes configurations.
- Map the data flow: Client -> Edge/Proxy -> API Server -> Database / Cache / Background Workers / Third-Party Services.

### 2. Audit the 19 Distributed Systems Pillars
- **Rate Limiting & Abuse Defense**: Check for token/leaky bucket middleware on login, signup, sensitive APIs, and public endpoints.
- **Caching & Stampede Defense**: Inspect Redis/Memcached integration, cache invalidation hooks on writes, and TTL definitions.
- **Timeouts & Circuit Breakers**: Ensure every HTTP client call and database query sets an explicit timeout. Verify circuit breakers or fallbacks on external dependencies.
- **Retries, Backoff & Idempotency**: Verify exponential backoff with jitter on retried operations. Ensure POST/payment mutations validate `Idempotency-Key` headers.
- **Queues & Async Decoupling**: Check that slow operations (email, PDF generation, webhooks, AI) run in worker queues (BullMQ, Celery, SQS) with a configured Dead Letter Queue (DLQ).

### 3. Audit Database & Data Integrity
- **Migrations & Table Locks**: Verify forward/backward migration files exist and do not lock high-traffic tables.
- **Indexes & Connection Pooling**: Verify indexes on foreign keys and filter columns. Check for PgBouncer or connection pool configuration.
- **Integer Money Rule**: Flag any currency, price, or balance stored as `float`, `double`, or `real`. All monetary values must be integer cents or `NUMERIC(12, 4)`.
- **Soft Deletes & Point-in-Time Recovery**: Check for `deleted_at` soft deletion patterns and documented backup/restore procedures.
- **Timezones & Unicode**: Ensure all timestamps are UTC `timestamptz` and names support apostrophes (O'Connor), emojis, and right-to-left scripts.

### 4. Audit Auth, Multi-Tenancy & Enterprise Readiness
- **Tenant Isolation & IDOR**: Verify all data queries strictly enforce tenant/organization boundaries (RLS or tenant ID filters). Test for IDOR in route parameters.
- **Session Lifecycle & Security**: Check session expiration, global session revocation ("log out of all devices"), and plus-sign email address support (`user+test@`).
- **Enterprise Features**: Note status of SSO / SAML 2.0, SCIM directory sync, fine-grained RBAC, and support impersonation audit trails.
- **Secrets & Errors**: Verify zero hardcoded keys and confirm that server errors do not leak stack traces or internal queries.

### 5. Audit Codebase Slop Indicators (The 9 Core Antipatterns)
- **Implicit Coupling**: Check for hidden state dependencies, unversioned localStorage, global singletons, and implicit execution order.
- **Layer-First Folders**: Verify whether backend/app is organized by technical layers (`controllers/`, `services/`, `models/`) instead of domain/feature slices (`billing/`, `auth/`, `projects/`).
- **Duplication**: Identify copy-pasted API handlers, repeated query builders, and redundant schema formatters.
- **Representable Illegal States**: Check data models and state types for loose booleans allowing impossible states (`isLoading: true, error: Error, data: User`).
- **God Files**: Flag sprawling backend files or services (> 300 LOC, often 1,000+ LOC).
- **Shotgun Surgery**: Check if changing a single status enum or tenant setting requires modifying 10+ files.
- **Layering Violations**: Verify API routes don't execute raw database queries directly; check backend models don't import HTTP request/response DTOs.
- **Pass-Through Wrappers**: Identify 1-line facade services that merely delegate to another function without adding logic.
- **Errors / Validation Not at the Boundary**: Ensure payload validation is performed strictly at API ingress boundaries (Zod/Pydantic) rather than scattered deep in database methods.

### 6. Audit Dashboard Design Slop (The 10 UI Smells)
- **Tags & Badge Spam**: Flag gratuitous status chips and pill tags plastered across every table row and card.
- **Italicized Words**: Flag arbitrary italicization in headers and copy.
- **Instrument Serif + Negative Kerning**: Identify editorial serif headers with `tracking-tighter` forced onto SaaS tools.
- **Over the Top Detailed UI**: Identify gratuitous telemetry counters, fake activity monitors, and micro-charts cluttering simple dashboards.
- **Dividers Everywhere**: Flag excessive `<Separator />` and hairline rules fragmenting layouts.
- **Multiple Color Shades and Opacities**: Audit chaotic opacity layering (`text-white/70`, `bg-neutral-800/40`) causing contrast failures.
- **Containers with Borders (Box-in-a-Box)**: Flag deeply nested bordered cards cluttering the interface.
- **Diagrams (The More Detailed, the Worse)**: Scrutinize superfluous Mermaid, SVG, or ASCII diagrams adding visual noise.
- **Code Breadcrumbs**: Check for fake terminal prompts or deeply nested decorative breadcrumbs.
- **Section Numbering**: Flag robotic numbered headers ("01 / Billing", "02 / Security", "Step 01").

### 7. Evaluate the Pre-Launch 20 Gate
- Check each item in the Pre-Launch 20 scorecard (error tracking, rollback plan, email deliverability, spending caps, webhook verification).

## Output Contract

Produce the audit report in this exact structure:

```markdown
# SaaS Application & Backend Production Audit: [Project Name]

**Scanned Path**: `<path>`
**Backend Stack**: `Node.js / FastAPI / Go / Rails / Supabase`
**Database & Cache**: `PostgreSQL (Prisma/Drizzle/SQL) / Redis`
**Production Release Verdict**: `SHIP` | `HOLD (CRITICAL DEFECTS)` | `NO-SHIP (UNAUTHENTICATED/INSECURE)`

## 1. Executive Summary
- 3-5 sentence synthesis of architecture maturity, enterprise readiness, distributed systems resilience, and launch-blocking gaps.

## 2. 19 Distributed Systems Pillars Assessment
| Pillar | Status | File Evidence | Notes |
|---|---|---|---|
| 1. Rate Limiting | `IMPLEMENTED / MISSING` | `path:line` | ... |
| 2. Caching & Stampede Defense | `IMPLEMENTED / MISSING` | `path:line` | ... |
| 3. Load Balancing & Health Checks | `PASS / MISSING` | `/healthz` | ... |
| 4. Reverse Proxies | `PASS / UNVERIFIED` | ... | ... |
| 5. API Gateways | `PASS / N/A` | ... | ... |
| 6. CI/CD Automated Gates | `PASS / MISSING` | `.github/workflows/...` | ... |
| 7. Docker Multi-Stage & Non-Root | `PASS / FAIL` | `Dockerfile` | ... |
| 8. Kubernetes Probes & Limits | `PASS / N/A` | ... | ... |
| 9. Service Discovery | `PASS / N/A` | ... | ... |
| 10. Circuit Breakers | `IMPLEMENTED / MISSING` | ... | ... |
| 11. Timeouts on All Clients | `CONFIGURED / MISSING` | `path:line` | ... |
| 12. Retries & Exponential Backoff | `IMPLEMENTED / MISSING` | `path:line` | ... |
| 13. Idempotency Keys | `IMPLEMENTED / MISSING` | `path:line` | ... |
| 14. Message Queues & DLQs | `IMPLEMENTED / MISSING` | `path:line` | ... |
| 15. Pub/Sub & Event Decoupling | `IMPLEMENTED / N/A` | ... | ... |
| 16. Transactional Outbox Pattern | `IMPLEMENTED / MISSING` | ... | ... |
| 17. Distributed Transactions / Sagas| `IMPLEMENTED / N/A` | ... | ... |
| 18. Graceful Shutdown & Draining | `IMPLEMENTED / MISSING` | ... | ... |
| 19. Graceful Degradation / Fallbacks| `IMPLEMENTED / MISSING` | ... | ... |

## 3. Findings by Severity (P0, P1, P2, P3)

### [P0/P1/P2/P3-CODE] Title
- **Severity**: P0 (Launch blocker / data loss / security breach) | P1 (High risk / downtime) | P2 (Medium) | P3 (Low)
- **Status**: Verified | Unverified Concern
- **File**: `path/to/file:line`
- **What**: Exact code or configuration evidence.
- **Why it matters**: Production impact (data corruption, billing error, cascading outage, tenant leak).
- **Smallest fix**: Targeted, minimal refactor with code snippet.
- **Verification**: Command or smoke test to verify resolution.

## 4. Pre-Launch 20 Scorecard
| Check | Status | Verification Detail |
|---|---|---|
| 1. API Keys Hidden | `PASS / FAIL` | ... |
| 2. Key Rotation Verified | `PASS / FAIL` | ... |
| 3. Rate Limiting Active | `PASS / FAIL` | ... |
| 4. Server-Side Auth Checks | `PASS / FAIL` | ... |
| 5. Tenant Isolation / RLS | `PASS / FAIL` | ... |
| 6. Server Input Validation | `PASS / FAIL` | ... |
| 7. Spending Caps Configured | `PASS / FAIL` | ... |
| 8. Errors Sanitized (No Stacks) | `PASS / FAIL` | ... |
| 9. Sentry / Error Tracking | `PASS / FAIL` | ... |
| 10. Backup & Restore Tested | `PASS / FAIL` | ... |
| ... | ... | ... |

## 5. Prioritized Cleanup Backlog
- **Quick Wins (< 30 mins)**: Immediate config or small fixes.
- **Targeted Refactors (1-3 hours)**: Adding rate limiting middleware, integer money migration, timeout wrappers.
- **Structural Upgrades (Half-day to 2 days)**: Idempotency keys, message queue workers, SSO/SAML integration.

## 6. What's Already Good
- Highlight sound architectural decisions and solid patterns in the codebase.
```
