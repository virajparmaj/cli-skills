# Mac App Store & Notarization Readiness Checklist

Apply the entrypoint’s scope, evidence, frequency x impact scoring, threshold (5), and deferral policy. These checks and severity examples guide inspection; they do not prove a bug or require a new feature. Mark inapplicable checks N/A and unavailable evidence UNVERIFIED. Below-threshold issues do not block completion; review-only requests remain read-only.

Checklist to pass Apple review and Gatekeeper notarization on macOS Sonoma, Sequoia, and beyond.

---

## 1. App Sandbox & Least-Privilege Entitlements
- **Mandatory for Mac App Store**:
  ```xml
  <key>com.apple.security.app-sandbox</key>
  <true/>
  ```
- **File Access Rules**:
  - For user-selected files: `com.apple.security.files.user-selected.read-write`
  - For saving bookmarks across restarts: `com.apple.security.files.bookmarks.app-scope`
- **Rejection Risks (Temporary Exceptions)**:
  - Do NOT submit with `com.apple.security.temporary-exception.files.absolute-path.read-only` or `/tmp` exceptions unless accompanied by detailed business justification. Apple reviewers routinely reject apps with temporary exceptions.

## 2. Privacy Manifest (`PrivacyInfo.xcprivacy`)
- Identify the required-reason APIs, tracking behavior, SDKs, and distribution requirements actually present. Verify current Apple rules before asserting a missing manifest is a submission blocker.
- Must declare:
  - `NSPrivacyTracking`: Boolean indicating cross-app tracking.
  - `NSPrivacyCollectedDataTypes`: Array of collected data (User ID, Email, Crash Data).
  - `NSPrivacyAccessedAPITypes`: Declares use of Required Reason APIs (File timestamp APIs, System boot time, Disk space, Active keyboard).

## 3. Direct Developer ID Distribution: Signing & Gatekeeper Notarization

Use this route for direct distribution; assess Mac App Store signing and review separately.
- **Hardened Runtime**: Must be enabled (`ENABLE_HARDENED_RUNTIME = YES`).
- **Developer ID Application**: Signed with valid Apple Developer ID Certificate.
- **Notarization Pipeline**:
  ```bash
  xcrun notarytool submit "$APP_ZIP" --keychain-profile "$PROFILE" --wait
  xcrun stapler staple "$APP_PATH"
  ```
- **Verification**: Verify staple before distribution:
  ```bash
  spctl --assess --type execute --verbose "$APP_PATH"
  ```

## 4. App Store Review Readiness
- **Reviewer Demo Credentials**: Working test account credentials provided in App Store Connect review notes.
- **No Private or Deprecated APIs**: No references to private frameworks (`_CFront`, private WebKit symbols). Replace deprecated `WebView` with `WKWebView`.
- **In-App Purchase Restoration**: If using StoreKit 2 subscriptions, provide an explicit "Restore Purchases" button in Settings.

## Entitlement evidence

Read each entitlement’s actual typed plist value, not a key-name hit or an unrelated `<true/>` elsewhere. XML and binary plist files are supported by [Python plistlib](https://docs.python.org/3/library/plistlib.html). Confirm which file and signing settings the release target actually uses; an enabled debug entitlement does not prove the shipped application’s sandbox.
