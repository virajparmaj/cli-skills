---
name: v-vibe-macos
description: "Review-only post-vibe audit for macOS desktop applications (Swift, SwiftUI, AppKit, Tauri, Electron, Flutter for Mac). Audits App Sandbox compliance, least-privilege entitlements, Security-Scoped Bookmarks, mandatory Privacy Manifest (PrivacyInfo.xcprivacy), Hardened Runtime, Gatekeeper notarization readiness, native desktop stability (atomic file writes, SQLite WAL mode, memory leaks/retain cycles, battery/timer polling), menu bar Dark/Light mode integration, and Sparkle auto-update security. Trigger on audit macos, audit desktop, audit mac app, v-vibe-macos, v-vibe-mac, mac app store audit."
---

# Post-Vibe macOS Desktop Software Audit

## Practical review and implementation

- Do not design for rare or future cases nobody asked about.
- For each bug, report **frequency (1-10)** in current usage, **impact (1-10)**, **frequency x impact = score**, and the reachable trigger with evidence. Keep confidence separate from occurrence frequency; hypothetical future requirements are not bugs. Checklist examples are inspection prompts, not automatic findings or severity assignments.
- Default fix threshold: **5**, unless the user explicitly changes it. **Below 5:** record one deduplicated backlog issue and leave the code alone; use **Deferred issues** in the review if no backlog exists or remote issue creation is not already authorized. Do not block completion or reopen the same issue without new evidence or an explicit request.
- **5 or above:** propose the smallest verified fix; implement only within the authorized task. Review-only work stays review-only. Preserve existing report structure and add the scores to each finding. Required checks and explicitly requested fixes still apply.
- Pass evidence, scores, threshold, and deferrals to the fixer. Stop after the requested scope is covered and required checks pass; re-review affected paths only when changes, failures, or unresolved evidence justify it.

Use this skill when auditing a native macOS desktop application or web-wrapper desktop app (Swift, AppKit, SwiftUI, Tauri, Electron). Stay in review mode unless the user explicitly requests implementation.

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
   python3 "<skill-path>/scripts/audit_macos_vibe.py" --repo "<repo>"
   ```
2. Read the domain references before evaluating:
   - [references/macos-desktop-architecture.md](references/macos-desktop-architecture.md) for local persistence, atomic writes, and memory hygiene
   - [references/app-store-notarization-checklist.md](references/app-store-notarization-checklist.md) for App Sandbox, entitlements, and privacy manifests
   - [references/desktop-offline-resilience.md](references/desktop-offline-resilience.md) for offline sync, permissions, and bookmarks

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
- **Privacy Manifest**: Verify existence and completeness of `PrivacyInfo.xcprivacy` with Required Reason APIs documented.
- **Deprecated APIs**: Check for obsolete APIs (`WebView`, `NSArchiver`, deprecated Carbon symbols).
- **Auto-Update (Sparkle)**: For direct distribution, verify Sparkle 2 is configured with EdDSA public keys (`SUPublicEDKey`).

### 4. Audit Native Desktop Architecture & Stability
- **Atomic File Writes**: Verify all file saves use atomic options (`[.atomic]`) to prevent zero-byte corruptions on power loss or crash.
- **SQLite / Database WAL Mode**: Verify SQLite/CoreData uses WAL journal mode and busy timeouts to prevent UI thread lockups.
- **Timer & Battery Conservation**: Flag unthrottled polling timers (< 2.0s interval) that drain battery and trigger App Nap throttling.
- **Retain Cycles**: Check closure captures for missing `[weak self]` in long-lived services or network publishers.

### 5. Audit Web-Wrapper Container Security (Electron / Tauri)
- **Node Integration**: Flag any `nodeIntegration: true` as critical vulnerability.
- **Context Isolation**: Verify `contextIsolation: true` in Electron webPreferences.
- **Tauri Permissions**: Verify allowlist in `tauri.conf.json` does not expose broad unneeded shell/fs capabilities.

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
- **Severity**: P0 (Security flaw / instant Apple rejection) | P1 (Crash on launch / data corruption) | P2 (Battery/memory leak) | P3 (Polish)
- **Status**: Verified | Unverified Concern
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
