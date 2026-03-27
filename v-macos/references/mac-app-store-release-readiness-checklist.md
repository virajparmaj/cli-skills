# Mac App Store Release Readiness Checklist For A macOS App

Use this checklist as a pre-release audit before submitting a macOS app to the Mac App Store.

## 1. Hard Blockers Before Submission

- App is a final, review-ready build with no placeholders, fake content, unfinished flows, hidden WIP features, or broken URLs.
- App has been tested on-device for bugs, crashes, and stability issues.
- Reviewer can access all key functionality via working review credentials or an approved demo mode.
- App Store Connect metadata matches the real app experience (screenshots, previews, description, privacy details, and "What's New").

## 2. macOS-Specific App Store Compliance

- App is properly sandboxed and follows macOS filesystem boundaries.
- App is packaged and submitted with Xcode-provided technologies.
- Distribution is a self-contained single-app bundle.
- App does not install shared system resources outside the app bundle.
- App does not auto-launch at startup/login without user consent.
- App does not leave helper processes running after quit without user consent.
- App does not auto-create Dock icons or desktop shortcuts.
- App does not download/install standalone apps, kexts, extra executable code, or resources that materially change reviewed functionality.
- App does not request root privilege escalation and does not use `setuid`.
- App does not enforce launch-time license gates, license keys, or custom copy-protection flows.
- App uses Mac App Store update mechanisms (no separate custom updater).
- App runs on the current shipping macOS version and avoids deprecated/optional runtime dependencies.
- Language/localization support is bundled in the app.

## 3. Privacy, Permissions, And Data Handling

- Privacy policy URL is set in App Store Connect.
- Privacy policy is also visible inside the app in an easily accessible location.
- Privacy policy clearly states:
  - collected data types
  - data collection methods
  - data usage
  - third-party sharing
  - retention period
  - consent withdrawal and deletion request path
- Consent is obtained where required for user/usage data collection.
- Users can revoke consent where applicable.
- Sensitive API usage has clear `Info.plist` purpose strings.
- Third-party SDKs (analytics/ads/etc.) are reviewed for policy alignment.

## 4. Security And System-Behavior Checks

- App uses only public APIs.
- App remains self-contained and does not read/write outside allowed locations except platform-approved paths.
- App does not download or execute code that changes features/functionality.
- App does not transmit malware or harmful payloads.
- App has appropriate controls to prevent unauthorized access, disclosure, or misuse of user data.

## 5. Efficiency And Performance Audit

- No abnormal battery drain under normal usage.
- No excessive CPU/GPU load during idle/background conditions.
- No abnormal thermal behavior.
- No unnecessary memory pressure, swap churn, or heavy write loops.
- No unrelated background activity.
- No hidden miners, daemons, or post-quit processes.
- App does not request users to disable unrelated security/system settings.

### 5.1 Efficiency Test Cases

- Cold launch, warm launch, and first-window render latency.
- Idle CPU and memory footprint after launch.
- CPU spikes during common interactions.
- Memory growth across long sessions (leak detection).
- Disk write behavior during sync/cache/export/index/autosave.
- Behavior after minimize, close window, and full quit.
- Large-file handling.
- Offline mode and flaky-network recovery.
- Sleep/wake resilience.
- External display, battery mode, and low-power behavior.
- Repeated open-close-import-export loops for stability and cleanup.

## 6. Metadata And Listing Compliance

- Name, subtitle, keywords, screenshots, previews, and description are truthful and specific.
- No hidden, dormant, or undocumented marketed features.
- No claims for unsupported capabilities.
- Pricing and purchase flow are accurately represented.
- No irrelevant keyword stuffing or trademark stuffing.
- Age rating is selected honestly.
- Metadata is suitable for broad audiences regardless of app age rating.
- "What's New" clearly describes meaningful changes.

## 7. Payments And Monetization Checks

- If digital features/content/services are sold and consumed in-app, payment flow is validated against In-App Purchase requirements.
- If using an exception category (for example reader app, enterprise service, real-time person-to-person service, physical goods/services, or standalone companion app), rationale is documented.
- App does not direct users to alternate in-app purchase methods unless explicitly allowed.

## 8. UX And Design Review

- App behavior and interaction patterns feel native to macOS.
- App does not alter expected system behavior in surprising ways.
- App does not create alternate desktop/home-screen environments.
- If app includes web browsing, WebKit usage and entitlement requirements are satisfied.
- Human Interface Guidelines are used as the baseline quality standard.

## 9. Submission Package Checklist

- Correct build is selected in App Store Connect.
- Required metadata fields are complete.
- Privacy policy URL is present and valid.
- Support URL is working.
- Relevant in-app purchases are visible and functional for review.
- Review notes explain non-obvious behavior.
- Demo credentials are valid.
- Backend services needed for review are active.
- Contact information is current.

## 10. Common Rejection Triggers To Hunt Early

- Crashes, freezes, or obvious technical instability.
- Placeholder content or incomplete flows.
- Broken external links.
- Reviewer blocked by login-gated access.
- Hidden features not documented in review notes.
- Misleading screenshots or descriptions.
- Missing privacy policy or missing permission-purpose strings.
- Excessive resource usage.
- Unsandboxed behavior or disallowed filesystem writes.
- Custom updaters, installers, helper binaries, or downloaded feature code.
- Root escalation behavior.
- Manipulative monetization or deceptive UX.
- Dishonest metadata, review fraud, or misleading identity details.

## 11. Recommended Release Test Matrix

### 11.1 Functional

- Fresh install
- Upgrade from previous version
- First-run onboarding
- Sign in / sign out
- Purchase / restore purchase
- Import / export
- Deep links, file open, drag-and-drop, share, notifications

### 11.2 Reliability

- Repeated launch/quit cycles
- Network loss and recovery
- Corrupt file input
- Empty-state behavior
- Permission-denied flows
- Backend timeout/rate-limit handling
- Crash recovery and autosave recovery

### 11.3 Performance

- Large datasets
- Long-running sessions
- Background/foreground transitions
- Multiple windows
- Sleep/wake
- Battery vs charging behavior
- Intel and Apple silicon coverage (if applicable)

### 11.4 Compliance

- Sandbox boundaries
- Permission prompts
- Privacy disclosures
- Metadata accuracy
- Payment path correctness
- Removal of debug menus, dev toggles, and internal endpoints

## 11.5 Additional macOS-Specific Checks

### Universal Binary And Architecture

- Verify the app includes both arm64 and x86_64 slices (Universal Binary) if targeting both Intel and Apple Silicon Macs.
- Test on both architectures if Universal Binary is used.
- Verify Rosetta 2 compatibility if only x86_64 is shipped.

### Notarization And Code Signing

- App is signed with a valid Developer ID or Apple Distribution certificate.
- App is notarized and stapled for Gatekeeper compliance.
- All embedded frameworks, helpers, and plugins are also signed.
- Hardened Runtime is enabled with only necessary entitlements.
- Verify entitlements are minimal and justified (no unnecessary `com.apple.security.*` entitlements).

### Accessibility Compliance

- VoiceOver navigation works for all primary flows.
- Keyboard navigation covers all interactive elements.
- Dynamic Type and text scaling are supported where applicable.
- Focus indicators are visible and follow system conventions.
- Accessibility labels are set for non-text interactive elements.

### Appearance And System Integration

- App supports both Light and Dark modes correctly.
- App respects system accent color and highlight color preferences.
- App uses standard macOS controls and conventions where possible.
- Menu bar, keyboard shortcuts, and Dock behavior follow platform conventions.
- App responds correctly to system appearance changes at runtime.

### Energy And Memory Efficiency

- Profile with Instruments (Energy Log, Allocations, Time Profiler) under normal and heavy workloads.
- Verify App Nap compliance for background behavior.
- Check for excessive timer usage, wake locks, or background network activity.
- Verify memory footprint is reasonable for the app category.
- Confirm no memory leaks during extended usage sessions.

## 12. Ship/No-Ship Gate

Do not submit until all are true:

- No known crashers.
- No unfinished screens or fake content.
- No policy-violating system behavior.
- No privacy gaps.
- No unexplained permissions.
- No broken links or reviewer dead-ends.
- No major efficiency regressions.
- Store listing exactly matches the shipped build.
