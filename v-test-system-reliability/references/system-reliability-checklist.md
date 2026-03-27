# System & Reliability Checklist (4.1-4.10)

Use this checklist as the default test matrix. For each item, capture:
- expected behavior
- actual behavior
- reproduction steps
- evidence (logs, screenshots, traces, request IDs)

## 4.1 Authentication and Authorization Behavior
- Verify login, logout, session expiry, refresh, and invalid-token handling.
- Confirm role/permission checks are enforced server-side, not only hidden in UI.
- Test direct API access to protected resources with missing/expired/wrong-role tokens.
- Validate multi-tab/session behavior (revoked token, password change, forced logout).

## 4.2 Input Sanitization and Security-Related Cases
- Test malformed input, oversized payloads, encoding edge cases, and dangerous characters.
- Validate server-side sanitization and schema validation on every write path.
- Probe for common injection vectors (SQL/NoSQL, command, HTML/script, template).
- Ensure security errors are safe: no secrets, stack dumps, or internals leaked to clients.

## 4.3 Performance Under Load and Large Data
- Measure key flows under concurrent traffic and burst conditions.
- Test pagination, filtering, search, and exports with large datasets.
- Track p95/p99 latency, timeout behavior, queue buildup, and resource saturation.
- Confirm graceful degradation (rate limits, backpressure, partial results, retries).

## 4.4 Responsive Behavior Across Devices
- Validate major flows on mobile, tablet, and desktop breakpoints.
- Check navigation, forms, tables, and modals for overflow, clipping, and tap targets.
- Verify orientation changes and viewport resizing do not corrupt state.

## 4.5 Cross-Browser Compatibility
- Run critical journeys on Chromium, Firefox, and Safari (plus Edge when required).
- Check auth redirects, storage behavior, file uploads, and date/time inputs.
- Verify CSS/JS feature compatibility and fallback behavior.

## 4.6 Accessibility (Keyboard, Screen Reader, Contrast)
- Validate full keyboard navigation, focus order, focus visibility, and escape paths.
- Ensure semantic structure and labels for forms, controls, and landmarks.
- Test screen-reader announcements for errors, async loading, and status changes.
- Confirm contrast ratios and non-color cues for important states.

## 4.7 State Consistency Between Frontend and Backend
- Verify UI state reflects persisted backend state after refresh, retries, and reconnects.
- Check optimistic updates, rollback behavior, and stale-cache invalidation.
- Test race conditions: simultaneous edits, duplicate submits, and out-of-order responses.
- Confirm idempotency for retried writes.

## 4.8 Deployment/Environment Mismatch Scenarios
- Compare local/staging/prod config parity (env vars, feature flags, secrets, URLs).
- Validate migration/version compatibility across frontend and backend deployments.
- Test missing or misconfigured dependencies (CORS, auth issuer, storage bucket, CDN).
- Confirm safe failure behavior when third-party services are unavailable.

## 4.9 Logging and Error Traceability
- Ensure each request and failure path produces traceable logs with correlation IDs.
- Verify errors include actionable context for debugging without exposing secrets.
- Check structured logging consistency across services and background jobs.
- Validate alerting signals exist for high-severity failures.

## 4.10 Recovery from Crashes or Interrupted Flows
- Test restart/retry behavior after server crash, worker restart, or network interruption.
- Validate resume semantics for long-running or multi-step workflows.
- Ensure partial writes recover safely (transaction rollback or compensating actions).
- Confirm user-facing recovery guidance is clear and non-destructive.

## 4.11 Database Migration and Rollback Testing
- Verify forward migrations apply cleanly on a fresh database and on existing data.
- Test rollback safety: can the previous migration state be restored without data loss?
- Validate zero-downtime migration strategies (e.g., expand-contract pattern).
- Check data integrity after migration: foreign keys, constraints, and default values.
- Verify migration scripts are idempotent or guarded against double-execution.

## 4.12 Background Job and Queue Reliability
- Verify job processing completes within expected time and resource bounds.
- Test retry behavior with exponential backoff for transient failures.
- Validate dead-letter queue handling for permanently failed jobs.
- Check duplicate prevention (idempotency keys or dedup logic).
- Verify monitoring and alerting for job queue depth, failure rates, and processing latency.

## 4.13 Rate Limiting and Throttling Behavior
- Verify rate limits are enforced correctly (per-user, per-IP, or global as designed).
- Test `Retry-After` headers and client-side backoff behavior.
- Validate graceful client-side handling of 429 responses (queuing, retry, user notification).
- Check distributed rate limiting consistency across multiple instances or regions.
- Verify rate limiting does not block legitimate high-frequency flows (e.g., bulk imports with proper auth).

## Reporting Template

For each failed or risky scenario, report:
1. Scenario ID (for example `4.7-02`)
2. Environment and build/version
3. Reproduction steps
4. Expected vs actual behavior
5. Impact and severity
6. Evidence links or artifacts
7. Suggested fix and missing regression test
