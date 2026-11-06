# Input & Edge-Case Checklist (2.1-2.9)

Use this checklist as the baseline matrix for input and edge-case testing.
For each scenario, capture:
- expected behavior
- actual behavior
- reproduction steps
- evidence (logs, request IDs, screenshots, traces, payload samples)

## 2.1 Empty, Invalid, and Boundary Input Values
- Test empty strings, nulls, omitted required fields, and whitespace-only input.
- Validate min/max boundaries (length, numeric range, enum values, file count).
- Verify server-side validation is authoritative, even if client validation exists.
- Confirm error messages are actionable and do not leak internals.

## 2.2 Special Characters, Long Text, and Unusual Formats
- Test symbols, Unicode, emoji, escaped characters, and mixed encodings.
- Test very long strings across fields, including multiline payloads.
- Validate unusual but legal formats (regional phone/email/date formats).
- Confirm rendering and storage behavior is safe (no truncation corruption or injection side effects).

## 2.3 Duplicate Submissions and Race Conditions
- Attempt double-click and repeated submit while request is in flight.
- Fire concurrent writes against the same record from multiple clients/tabs.
- Verify idempotency keys or dedupe logic for retried writes.
- Confirm final state is consistent and no duplicate side effects occur.

## 2.4 Large Files, Payloads, and Datasets
- Upload large files near and above declared limits.
- Submit large JSON/form payloads and batch operations.
- Test pagination/filtering/search with large datasets.
- Validate timeout, chunking, backpressure, and graceful failure behavior.

## 2.5 Slow Network, Offline, and Reconnect Scenarios
- Simulate high latency, packet loss, and limited bandwidth.
- Test offline behavior for read/write flows and queued actions.
- Validate reconnect sync, retry policy, and duplicate-prevention safeguards.
- Confirm user-visible status and recovery guidance are clear.

## 2.6 Expired Sessions and Token Handling
- Test expired access tokens, revoked tokens, and malformed tokens.
- Validate refresh-token rotation and failure handling.
- Confirm protected endpoints reject invalid auth on the server side.
- Verify forced logout and re-auth flows preserve or safely discard pending state.

## 2.7 Timezone, Date, and Locale Variations
- Test users in different timezones including DST boundaries.
- Validate date parsing/formatting across locale preferences.
- Check server/client conversion consistency (UTC vs local display).
- Confirm sorting, filtering, and scheduled actions behave correctly across locales.

## 2.8 Concurrent User Actions
- Simulate simultaneous edits by multiple users on shared records.
- Test conflict detection/resolution (last-write-wins, merge, or lock strategy).
- Verify optimistic UI updates roll back correctly on conflict.
- Confirm audit trails and version history reflect concurrent changes accurately.

## 2.9 Cache and Stale Data Scenarios
- Test stale reads after writes in single-tab and multi-tab sessions.
- Validate cache invalidation for list/detail views and related aggregates.
- Simulate out-of-order responses and ensure the newest state wins.
- Confirm background refresh and manual refresh produce consistent state.

## 2.10 File Type and Content Validation
- Test upload of files with mismatched extensions and MIME types (e.g., .jpg that is actually a .exe).
- Validate server-side magic byte / file signature checks beyond extension-based filtering.
- Test handling of polyglot files, nested archives, and zip bomb patterns.
- Verify file size limits are enforced server-side, not just client-side.
- Confirm malicious file content (scripts in SVGs, macros in Office files) is sanitized or rejected.

## 2.11 API Versioning and Deprecation Handling
- Test behavior when the client calls a deprecated API version.
- Verify deprecation warnings are surfaced to users or logged for developers.
- Test response schema evolution: added fields, removed fields, and type changes.
- Confirm the client handles version negotiation or fallback gracefully.
- Verify sunset headers and deprecation notices are processed correctly.

## Reporting Template

For each failed or risky scenario, report:
1. Scenario ID (for example `2.3-01`)
2. Environment and build/version
3. Reproduction steps
4. Expected vs actual behavior
5. Impact and severity
6. Evidence links or artifacts
7. Suggested fix and missing regression test
