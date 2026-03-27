# Chrome Extension Pre-Release Audit Spec

Use this as the strict checklist for Chrome Extension release readiness.

## Policy References

- Chrome Web Store Program Policies: https://developer.chrome.com/docs/webstore/program-policies
- Prepare your extension for publication: https://developer.chrome.com/docs/webstore/prepare
- Chrome Web Store listing best practices: https://developer.chrome.com/docs/webstore/best-practices

## Evidence Rules

- Every finding must include:
  - `classification`: `verified` | `likely` | `needs runtime confirmation`
  - `severity`: `critical` | `high` | `medium` | `low`
  - `evidence`: file path(s), config key(s), or reproducible runtime steps
  - `fix`: smallest viable remediation
- Block submission if any `critical` policy, privacy, or security issue exists.

## 1) Policy & Compliance Audit (Blocker)

Validate:
- Real user value and non-duplicate utility.
- No misleading UI, fake controls, or deceptive flow.
- No impersonation of brands, services, or official products.
- No hidden behavior not disclosed in UI/listing/policy.
- No install or review manipulation patterns.

Output:
- Violations and gray areas.
- Exact policy-aligned fixes required before submission.

## 2) Permissions & Privacy Audit

Inspect `manifest.json`:
- Enforce least privilege across `permissions`, `host_permissions`, `optional_permissions`.
- Flag risky patterns, especially:
  - `"*://*/*"`
  - `tabs`
  - `cookies`
  - `webRequest` / `declarativeNetRequest`
  - `scripting`

Validate for each permission:
- Necessary for stated feature.
- Used in code (not dead/excessive).
- Disclosed in privacy policy and listing text when relevant.

Privacy policy must clearly define:
- Data categories collected
- Purpose and legal/business necessity
- Storage location and retention
- Sharing/third-party processors
- User controls (delete/revoke/export) where applicable

Output:
- Over-permission analysis.
- Missing or weak disclosures.
- Suggested policy text rewrite points.

## 3) Security & Data Handling

Check:
- No unnecessary sensitive data collection.
- No credential/token logging.
- HTTPS-only external calls unless unavoidable local protocols are justified.
- No hardcoded secrets in repo or extension package.

Code-risk sweep:
- `eval`, `new Function`, string-based code execution.
- Remote code execution paths (forbidden).
- XSS/injection sinks (`innerHTML`, unsafe templating, URL injection).
- Data exfiltration patterns and broad network beacons.

Output:
- Vulnerabilities with severity and exploit path.
- Prioritized fixes.

## 4) Malicious / Suspicious Behavior

Detect:
- Hidden scripts or undeclared behavior.
- Obfuscated/minified logic with unclear purpose.
- Undocumented API calls/endpoints.
- Script injection on unrelated domains.

Output:
- Suspicion level: `low` | `medium` | `high`.
- Why it was assigned.

## 5) Functional Testing (Core)

Test:
- Extension install/load/init behavior.
- Popup/options behavior.
- Background/service worker correctness.
- Content script injection and messaging.
- Feature-to-description alignment.

Output:
- Functional test cases.
- Failures, flaky behavior, and coverage gaps.

## 6) Edge Case & Failure Testing

Browser contexts:
- Offline/no internet.
- Slow network/high latency.
- Tab refresh/navigation races.
- Multi-tab concurrency.
- Incognito behavior (if supported).

Data edges:
- Empty/null inputs.
- Very large inputs.
- Invalid and malformed formats.
- Rapid repeated actions (spam clicks/requests).

Failure modes:
- API failures/timeouts.
- Permission denial or revoked permission.
- Content script injection failure.

Validate:
- Graceful fallback behavior.
- Human-readable error states.
- No crashes or stuck states.

Output:
- Missed edge cases.
- Required fallback logic.

## 7) Error Handling & User Safety

Ensure:
- Clear actionable errors.
- No silent failures.
- Safe defaults if action fails.
- Recovery actions (retry/backoff/manual retry) are available where needed.

Output:
- Missing handlers.
- Suggested user-facing messages.

## 8) Performance & Efficiency

Analyze:
- Background/service worker wakeups and CPU usage risks.
- Memory pressure sources.
- Listener lifecycle and leaks.
- Polling vs event-driven architecture.
- Redundant API calls and repeated renders.
- Bundle size and payload overhead.

Validate:
- Manifest V3 architecture usage.
- Efficient event handling and throttling/debouncing where needed.

Output:
- Bottlenecks.
- Concrete optimization steps.

## 9) Code Quality & Maintainability

Check:
- Modular and readable structure.
- Dead/duplicate code.
- Separation of concerns.
- Logging hygiene (no noisy debug logs in release path).
- Async correctness and error propagation.

Output:
- Refactor candidates with rationale.

## 10) UX, Trust & Transparency

Validate:
- Users can understand what runs, when, and why.
- Data-access implications are visible and not hidden.
- No dark patterns or coercive prompts.
- Onboarding/help explains key permissions and behavior.

Output:
- Trust risks and UX improvements.

## 11) Listing & Store Metadata

Validate:
- Listing description matches actual behavior.
- Screenshots are real and current.
- Icons meet expected sizes and quality.
- No keyword stuffing or misleading claims.

Output:
- Listing risks and exact fixes.

## 12) Common Rejection Triggers (Strict)

Explicitly check:
- Overbroad permissions.
- Weak/missing privacy policy.
- Description-behavior mismatch.
- Ads/affiliate links without disclosure.
- Broken features.
- Excessive or irrelevant data collection.

Output:
- Rejection likelihood score `0-100%`.
- Top reasons that would likely trigger rejection.

## 12.5) Manifest V3 And Platform Compatibility

Manifest V3 migration:
- Verify service worker lifecycle is correct (no persistent background page assumptions).
- Check for alarm-based keepalive patterns where long-running operations are needed.
- Verify offscreen document usage for DOM-dependent operations that cannot run in service workers.
- Confirm `declarativeNetRequest` is used instead of blocking `webRequest` where applicable.

Extension storage:
- Check storage quota awareness for `chrome.storage.local` vs `chrome.storage.sync`.
- Verify large data sets use `chrome.storage.local` (not `sync` which has strict per-item limits).
- Check for storage migration logic when upgrading from previous versions.

Update and migration:
- Verify the extension handles version upgrades gracefully (data migration, schema changes).
- Check `chrome.runtime.onInstalled` handler for install vs update logic.
- Verify no user data is lost during updates.

Automated testing:
- Check for Puppeteer or Playwright extension testing setup.
- Verify content script behavior is testable in isolation.
- Check for service worker unit tests covering alarm, message, and storage flows.

Cross-browser compatibility:
- Note any Firefox WebExtensions or Edge Add-ons compatibility considerations.
- Flag Chrome-only APIs that would prevent cross-browser publishing.
- Check `browser_specific_settings` or polyfill usage for cross-browser support.

## 13) Improvements Beyond Passing

Suggest high-impact improvements:
- Product capability gaps.
- Engineering architecture simplifications.
- UX clarity and friction reduction.

Output:
- Prioritized improvements list.

## 14) Final Verdict

Must include:
- Approval readiness: `ready` or `not ready`.
- Critical issues (must-fix before submission).
- Medium issues (should-fix).
- Safe/compliant areas.
- Step-by-step action plan.

## Bonus (Mandatory)

Simulate Chrome Web Store rejection email:
- Reviewer-style tone.
- Policy-aligned issue list.
- Clear re-submission conditions.

## Rejection Score Guidance

Use this as a baseline rubric:
- `0-20`: low rejection risk, minor polish gaps only.
- `21-50`: moderate risk, at least one meaningful policy/privacy inconsistency.
- `51-80`: high risk, multiple major compliance/security gaps.
- `81-100`: near-certain rejection, blocker-level issues unresolved.
