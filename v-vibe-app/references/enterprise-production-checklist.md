# Enterprise & Production Readiness Checklist: 80+ Real-World Checks

Before your vibe-coded application touches a paying customer or an enterprise buyer, make sure it satisfies these verified operational and architectural criteria.

---

## 1. Database & Data Integrity
- [ ] **Designed Schema**: Relational schema intentionally designed with foreign key constraints, column constraints, and foreign key indexes, not an improvised JSON blob table.
- [ ] **Forward & Backward Migrations**: Every migration script has a verified rollback path. Never run migrations that acquire an exclusive table lock on high-traffic tables at peak hours (e.g., use `ADD COLUMN ... DEFAULT NULL` then backfill).
- [ ] **PostgreSQL Indexing**: Explicit indexes on all foreign keys, status/filter flags, and search columns. Verify index usage via `EXPLAIN ANALYZE`.
- [ ] **Connection Pooling**: PgBouncer or serverless connection pooling (e.g. Prisma Accelerate, Supabase pooler) configured to prevent connection starvation during traffic bursts.
- [ ] **Automated Backups & Tested Restore**: Automated daily snapshots and WAL archiving. A backup that has never been restored is merely a wish; run quarterly restore drills into staging.
- [ ] **Point-in-Time Recovery (PITR)**: Configured retention window (typically 7-30 days) allowing database rewind to the second before an accidental `DELETE` without a `WHERE` clause.
- [ ] **Soft Deletes**: Critical business entities use `deleted_at TIMESTAMP WITH TIME ZONE` with filtered unique indexes (`CREATE UNIQUE INDEX ... WHERE deleted_at IS NULL`).
- [ ] **Integer Money (No Floating Point)**: All currencies stored as integer smallest units (cents, satoshis, pence) or fixed-point `NUMERIC(12, 4)`. Floating point `0.1 + 0.2 != 0.3` is strictly prohibited.
- [ ] **UTC Timezones**: All timestamps stored as UTC (`TIMESTAMPTZ` in Postgres). Conversions to user local time occur exclusively at the presentation layer.
- [ ] **Name & Character Encoding**: Database and API handle full UTF-8 (diacritics, apostrophes like O'Connor, non-Latin scripts, emojis, and right-to-left Hebrew/Arabic).
- [ ] **Cursor-Based Pagination**: Large list queries use keyset pagination (`WHERE id < cursor LIMIT 50`) instead of offset pagination (`OFFSET 100000`).
- [ ] **CSV Import/Export Streaming**: File imports and exports stream row by row; never load a 50MB CSV entirely into Node/Python memory.
- [ ] **Data Retention & Pruning**: Automated jobs delete or archive temporary sessions, expired tokens, and contractually pruned data.

## 2. Authentication, Authorization & Enterprise
- [ ] **Plus-Addressing in Email**: Email regex and validation supports `user+alias@company.com` standard RFC 5322.
- [ ] **Expiring Single-Use Password Resets**: Reset tokens stored hashed, valid for maximum 15-30 minutes, invalidated immediately upon use.
- [ ] **MFA with Recovery Codes**: TOTP (Time-based One-Time Password) authenticator support plus encrypted single-use recovery codes for lost phones.
- [ ] **Session Expiration & Revocation**: Sliding window or fixed session timeouts, with a server-side endpoint to revoke all active sessions for a user ("Log out of all devices").
- [ ] **Enterprise SSO & SAML 2.0**: Integration readiness for enterprise identity providers (Okta, Azure AD, Ping) via SAML 2.0 or OIDC.
- [ ] **SCIM Automated Directory Sync**: SCIM 2.0 endpoint to automatically provision and instantly deprovision user seats when IT offboards employees.
- [ ] **Granular RBAC**: Permission models granularly separating View, Edit, Admin, Billing, and Auditor scopes beyond a binary `is_admin` boolean.
- [ ] **IDOR (Insecure Direct Object Reference) Prevention**: Every query taking an `id` from the URL verifies tenant or user ownership: `SELECT * FROM orders WHERE id = :id AND tenant_id = :current_tenant_id`.
- [ ] **Multi-Tenant Isolation**: Row-Level Security (RLS) or tenant middleware enforcing hard boundaries across customer data.
- [ ] **Support Impersonation Audit Log**: Admin "Log in as customer" feature records an immutable audit log entry capturing who impersonated whom, timestamp, IP, and reason.
- [ ] **Login Rate Limits & Smart Lockouts**: Rate limiting on `/api/login` and `/api/password-reset` to prevent brute force; account lockouts configured to prevent denial-of-service on executive emails.

## 3. Security, Privacy & Compliance
- [ ] **Zero Secrets in Code or Git**: No API keys, database passwords, or JWT secrets committed to git or stored in client-accessible frontend bundles.
- [ ] **Automated Secret Rotation**: Runbooks or tools (AWS Secrets Manager, Doppler, Vault) for rotating credentials without service downtime.
- [ ] **Dependency Supply Chain Audit**: Audit dependencies against known CVEs (`npm audit`, `pip-audit`, Dependabot); verify all AI-suggested packages are legitimate published packages.
- [ ] **Server-Side Input Validation**: Comprehensive schema validation (Zod, Pydantic) on every incoming payload before business logic executes.
- [ ] **OWASP Top 10 Protections**: SQL injection immunity via parameterized queries; XSS defense via HTML escaping; CSRF protection on cookie-authenticated mutations.
- [ ] **Secure File Uploads**: Size limits, MIME type verification by file magic bytes, malware scanning, storage in private non-executable buckets (e.g. S3 private) served via presigned URLs.
- [ ] **Strict CORS & Security Headers**: Explicit CORS whitelist (never `*` with credentials); headers: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`.
- [ ] **Encryption at Rest & Transit**: TLS 1.3 for all endpoints; encrypted database volumes (AES-256) and backups.
- [ ] **Least-Privilege Cloud IAM**: App workers and CI/CD agents possess only the minimal required permissions; production access isolated from personal accounts.
- [ ] **PII Scrubbing in Logs**: Passwords, access tokens, credit card PANs, and patient data masked before writing to log streams.
- [ ] **SOC 2 & HIPAA Readiness**: System logging, change control, employee access reviews, vendor BAA agreements with cloud and AI providers.
- [ ] **GDPR Right-to-be-Forgotten**: Deletion workflows that cascade across primary tables, analytics, search indexes, and log sinks.
- [ ] **Data Residency Compliance**: Architecture supports data residency requirements (EU data remaining within EU regions).

## 4. Reliability, Operations & Infrastructure
- [ ] **Environment Parity**: Dev, Staging, and Production share identical architecture, database engines, and runtime configurations.
- [ ] **Infrastructure as Code (IaC)**: Cloud infrastructure defined declaratively in Terraform, Pulumi, or AWS CDK.
- [ ] **Automated CI/CD Test Gates**: Pull requests cannot merge unless linters, type checks, and unit/integration tests pass.
- [ ] **One-Click Rollbacks**: Automated, instant rollback capability for application containers and code deployments.
- [ ] **Zero-Downtime Deployments**: Rolling updates or blue/green deployments so customer requests are not dropped during releases.
- [ ] **Feature Flags**: Decouple code deployment from feature release (LaunchDarkly, PostHog, Unleash).
- [ ] **Horizontal Autoscaling**: CPU/memory-based pod or container autoscaling for traffic surges.
- [ ] **Global CDN & Automated SSL**: CDN caching for static assets and automated TLS renewal (Let's Encrypt / AWS ACM).
- [ ] **Background Queues & DLQs**: Asynchronous task queues with retries, exponential backoff, and a Dead Letter Queue for permanently failed jobs.
- [ ] **Distributed Cron Locking**: Multi-instance cron jobs protected by distributed locks (Redlock, PG advisory locks) so tasks do not run multiple times concurrently.
- [ ] **Transactional Email Deliverability**: SPF, DKIM, and DMARC aligned; bounce and complaint webhook handlers deactivating invalid emails.
- [ ] **Cloud Spend Alerts**: Hard budget limits and daily anomaly alerts configured on AWS, GCP, Vercel, and AI API providers.

## 5. Observability & Incident Response
- [ ] **Structured JSON Logging**: Logs emitted as machine-searchable JSON containing `trace_id`, `user_id`, `tenant_id`, and `duration_ms`.
- [ ] **Centralized Error Tracking**: Sentry, Bugsnag, or Datadog grouping errors with stack traces, breadcrumbs, and release tags.
- [ ] **Synthetic Uptime Monitoring**: External probes (BetterStack, Pingdom) hitting health endpoints every 60 seconds from outside the internal network.
- [ ] **Latency & Throughput Dashboards**: Real-time graphs for P50, P95, and P99 response times and 5xx error rates.
- [ ] **Distributed Tracing**: OpenTelemetry instrumentation tracing requests across frontend, API gateway, backend services, and database.
- [ ] **On-Call Rotation & Runbooks**: PagerDuty/Opsgenie schedule with actionable runbooks for standard critical alerts.
- [ ] **Public Status Page**: Dedicated status page (e.g. status.yourdomain.com) hosted independently of primary infrastructure.

## 6. Billing, Monetization & APIs
- [ ] **Subscription Lifecycle**: Graceful handling of plan upgrades, downgrades, and immediate vs end-of-period prorations.
- [ ] **Dunning & Failed Payment Retries**: Automated email sequences and webhooks handling `invoice.payment_failed` with self-serve card update links.
- [ ] **Invoices with Tax & PO Numbers**: Compliant invoices supporting customer Purchase Order (PO) numbers, company legal names, and regional sales tax / VAT.
- [ ] **Usage-Based Metering**: Accurate, auditable event metering reconciled against billing invoices down to the cent.
- [ ] **Webhook Signature Verification**: Every incoming webhook (Stripe, GitHub, Shopify) validates HMAC signatures and rejects unverified calls.
- [ ] **API Versioning**: Customer-facing APIs use versioned pathing (`/v1/`) or headers to prevent breaking customer integrations.
- [ ] **Customer API Keys & Quotas**: Revocable API keys, hashed storage (like passwords), with per-key rate limits and usage analytics.
