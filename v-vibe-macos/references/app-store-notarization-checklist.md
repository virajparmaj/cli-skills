# Mac App Store & Notarization Readiness Checklist

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

## 2. Mandatory Privacy Manifest (`PrivacyInfo.xcprivacy`)
- Required for all Mac App Store apps and third-party SDKs.
- Must declare:
  - `NSPrivacyTracking`: Boolean indicating cross-app tracking.
  - `NSPrivacyCollectedDataTypes`: Array of collected data (User ID, Email, Crash Data).
  - `NSPrivacyAccessedAPITypes`: Declares use of Required Reason APIs (File timestamp APIs, System boot time, Disk space, Active keyboard).

## 3. Code Signing & Gatekeeper Notarization
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
