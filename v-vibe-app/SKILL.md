---
name: v-vibe-app
description: "Review SaaS applications, backends, and APIs for production reliability, data integrity, tenant isolation, and maintainability. Use for a post-vibe app or backend audit; apply distributed-systems and enterprise checks only where the product needs them."
---

# Post-Vibe SaaS Application & Backend Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


Use this skill when auditing a full-stack SaaS application, web app backend, or API. Stay in review mode unless the user explicitly requests implementation.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

## Quick Start

1. Run the deterministic scanner:
   ```bash
   python3 "<skill-path>/scripts/audit_app_vibe.py" --repo "<repo>"
   ```
2. Read only domain references relevant to this review:
   - [references/distributed-systems-resilience.md](references/distributed-systems-resilience.md) for the 19 distributed systems pillars
   - [references/enterprise-production-checklist.md](references/enterprise-production-checklist.md) for the 80+ enterprise production criteria
   - [references/prelaunch-20-checklist.md](references/prelaunch-20-checklist.md) for the pre-launch release gate

## Applicability

Establish the current product, traffic, deployment, and data model before applying enterprise or distributed-systems checks. Missing Redis, queues, circuit breakers, SSO, SCIM, soft deletes, or a particular folder structure is not itself a defect. Follow the reachable request and failure path and its existing safeguards.

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
- **Trigger and score**: frequency (1–10, reason) x impact (1–10, reason) = score; confidence stated separately
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
