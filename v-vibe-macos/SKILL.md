---
name: v-vibe-macos
description: "Review macOS applications built with Swift, AppKit, SwiftUI, Tauri, or Electron for persistence, permissions, sandboxing, signing, updates, and release readiness. Use for a desktop audit; distinguish Mac App Store requirements from direct distribution."
---

# Post-Vibe macOS Desktop Software Audit

## Practical review and implementation

- Confirm a reachable trigger in current code, inputs, and configuration before calling something a bug. Checklists and size/style heuristics are inspection prompts, not proof; do not add systems for hypothetical future needs.
- For every bug, report **frequency (1–10) x impact (1–10) = score**, the trigger, and a brief reason for each rating. Frequency measures occurrence in actual usage; confidence in the evidence is separate.
- Default fix threshold: **5**. Below 5, leave code alone and update one deduplicated existing backlog item; if no backlog exists or remote issue creation is not authorized, use **Deferred issues**. Deferrals do not block completion or start another fix cycle.
- At 5 or above, use the smallest verified fix only within the authorized task. Review-only requests stay read-only; preserve prior authorization across turns. Required checks and explicitly requested fixes still apply.
- Pass scope, evidence, scores, threshold, and deferrals to any fixer. Stop when the requested behavior works, eligible in-scope findings are addressed, and required checks pass; repeat only for new changes, failures, or unresolved evidence.


Use this skill when auditing a native macOS desktop application or web-wrapper desktop app (Swift, AppKit, SwiftUI, Tauri, Electron). Stay in review mode unless the user explicitly requests implementation.

## Evidence and execution

- Resolve bundled `scripts/` and `references/` from this skill’s directory, and pass the target repository separately. Use relevant discovery helpers after checking their arguments and effects; their output identifies candidates, not an exhaustive verdict.
- Confirm candidates in source and current configuration, and use runtime evidence when the conclusion depends on runtime behavior. Cite exact paths/lines or measurements; distinguish verified findings, inferred risks, and unavailable evidence. A failed helper does not invalidate independently verified facts.
- Read only references relevant to the requested scope. Mark inapplicable checks **N/A** and unavailable checks **UNVERIFIED**; do not infer a missing capability from an unmatched scanner pattern.

## Quick Start

1. Run the deterministic scanner:
   ```bash
   python3 "<skill-path>/scripts/audit_macos_vibe.py" --repo "<repo>"
   ```
2. Read only domain references relevant to this review:
   - [references/mac-app-store-release-readiness-checklist.md](references/mac-app-store-release-readiness-checklist.md) for full Mac App Store pre-release readiness & rejection gates
   - [references/macos-desktop-architecture.md](references/macos-desktop-architecture.md) for local persistence, atomic writes, and memory hygiene
   - [references/app-store-notarization-checklist.md](references/app-store-notarization-checklist.md) for App Sandbox, entitlements, and privacy manifests
   - [references/desktop-offline-resilience.md](references/desktop-offline-resilience.md) for offline sync, permissions, and bookmarks

## Applicability

Identify the distribution channel and framework version first. App Store and direct-distribution checks differ; inspect release build settings and bundled SDKs. Confirm ownership and lifetime before recommending weak captures, and actual contention/durability needs before prescribing WAL or atomic replacement for every write. Verify current Apple requirements for the APIs and SDKs actually shipped.

## Workflow

### 1. Absorb Context & Project Structure
- Inspect Xcode project files (`.xcodeproj`, `Package.swift`), Tauri config (`tauri.conf.json`), or Electron config (`electron-builder.yml`).
- Determine distribution target: Mac App Store vs Direct Developer ID Distribution (Notarization).

### 2. Audit App Sandbox & Entitlements
- **Sandbox Status**: Verify `com.apple.security.app-sandbox = true` for App Store builds.
- **Least-Privilege Entitlements**: Check network client/server permissions and file access entitlements.
- **Temporary Exceptions**: Flag any `com.apple.security.temporary-exception.*` entitlements as major App Store rejection risks.
- **Security-Scoped Bookmarks**: Ensure apps that remember user-opened files implement bookmarks so access persists across restarts.

### 3. Audit Privacy Manifest & Store Review Readiness
- **Privacy Manifest**: Identify required-reason API usage, tracking, and bundled SDK requirements, then verify applicable `PrivacyInfo.xcprivacy` declarations against current Apple guidance.
- **Deprecated APIs**: Check for obsolete APIs (`WebView`, `NSArchiver`, deprecated Carbon symbols).
- **Auto-Update (Sparkle)**: For direct distribution, verify Sparkle 2 is configured with EdDSA public keys (`SUPublicEDKey`).

### 4. Audit Native Desktop Architecture & Stability
- **Atomic File Writes**: Verify all file saves use atomic options (`[.atomic]`) to prevent zero-byte corruptions on power loss or crash.
- **SQLite / Database Concurrency**: Trace database access and UI-thread blocking, journal mode, transactions, and timeouts. Recommend WAL only when appropriate to the actual storage model.
- **Timer & Battery Conservation**: Flag unthrottled polling timers (< 2.0s interval) that drain battery and trigger App Nap throttling.
- **Retain Cycles**: Check closure captures for missing `[weak self]` in long-lived services or network publishers.

### 5. Audit Web-Wrapper Container Security (Electron / Tauri)
- **Node Integration**: Trace whether untrusted content can reach Node capabilities; assess `nodeIntegration`, navigation restrictions, preload/IPC validation, sandboxing, and context isolation together.
- **Context Isolation**: Verify `contextIsolation: true` in Electron webPreferences.
- **Tauri Permissions**: Determine the Tauri version; inspect its actual allowlist or capabilities and scope shell/fs access to required operations.

## Output Contract

Produce the audit report in this exact structure:

```markdown
# macOS Desktop App Production Audit: [App Name]

**Scanned Path**: `<path>`
**Desktop Framework**: `SwiftUI / AppKit / Tauri / Electron`
**Distribution Target**: `Mac App Store` | `Direct Developer ID (Notarized)`
**App Store & Notarization Verdict**: `READY TO SUBMIT` | `REJECTION RISKS DETECTED` | `NO-SHIP (SECURITY FLAW)`

## 1. Executive Summary
- 3-5 sentence synthesis of desktop architecture, sandbox compliance, stability risks, and App Store readiness.

## 2. Sandbox, Entitlements & Notarization Scorecard
| Check | Status | Evidence / Notes |
|---|---|---|
| App Sandbox Enabled | `PASS / FAIL` | `*.entitlements` |
| Temporary Exceptions | `CLEAN / FLAGGED` | ... |
| Security-Scoped Bookmarks | `IMPLEMENTED / MISSING` | ... |
| Privacy Manifest (xcprivacy) | `PASS / MISSING` | ... |
| Hardened Runtime & Code Signing | `VERIFIED / UNVERIFIED` | ... |
| Sparkle EdDSA Signature | `PASS / FAIL / N/A` | ... |

## 3. Findings by Severity (P0, P1, P2, P3)

### [P0/P1/P2/P3-CODE] Title
- **Severity**: P0 (Verified severe security or distribution blocker) | P1 (Crash on launch / data corruption) | P2 (Battery/memory leak) | P3 (Polish)
- **Status**: Verified | Unverified Concern
- **Trigger and score**: frequency (1–10, reason) x impact (1–10, reason) = score; confidence stated separately
- **File**: `path/to/file:line`
- **What**: Exact code or entitlements evidence.
- **Why it matters**: Rejection clause, user data loss, or system crash scenario.
- **Smallest fix**: Targeted, minimal refactor with code snippet.
- **Verification**: How to verify with Xcode, `codesign`, or `spctl`.

## 4. Desktop Stability & Lifecycle Assessment
| Metric | Status | Notes |
|---|---|---|
| Atomic File Writes | `ENFORCED / INSECURE DIRECT WRITES` | ... |
| SQLite WAL Journal Mode | `CONFIGURED / ROLLBACK LOCK RISK` | ... |
| Background Timer Throttle | `CLEAN / RUNAWAY POLLING DETECTED` | ... |
| Menu Bar Dark/Light Mode | `NATIVE TEMPLATE / HARDCODED COLOR` | ... |
| Memory Management / Retain Cycles| `LOW RISK / WEAK SELF AUDIT NEEDED` | ... |

## 5. Prioritized Cleanup Backlog
- **Quick Wins (< 30 mins)**: Fixing entitlement keys, adding `.atomic` options, setting menu bar template image.
- **Targeted Refactors (1-3 hours)**: Adding `PrivacyInfo.xcprivacy`, wrapping SQLite in WAL mode, refactoring polling timers.
- **Store Submission Prep (Half-day)**: Test account review notes, notarytool automation, sandboxed bookmark persistence.

## 6. What's Already Good
- Highlight well-architected native Mac patterns present in the codebase.
```
