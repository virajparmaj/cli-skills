# Desktop Offline Resilience & System Permissions

Desktop applications operate in hostile, intermittent network environments: sleep/wake cycles, hotel captive portals, and offline flights.

---

## 1. Security-Scoped Bookmarks (Persisting File Access)
- In a sandboxed app, when a user selects a file via `NSOpenPanel`, the app only has access during that run unless a Security-Scoped Bookmark is stored.
- **Save Bookmark**:
  ```swift
  let bookmarkData = try url.bookmarkData(
      options: .withSecurityScope,
      includingResourceValuesForKeys: nil,
      relativeTo: nil
  )
  UserDefaults.standard.set(bookmarkData, forKey: "savedFileURL")
  ```
- **Restore & Access**:
  ```swift
  var isStale = false
  let url = try URL(
      resolvingBookmarkData: bookmarkData,
      options: .withSecurityScope,
      relativeTo: nil,
      bookmarkDataIsStale: &isStale
  )
  guard url.startAccessingSecurityScopedResource() else { return }
  defer { url.stopAccessingSecurityScopedResource() }
  // Perform file reads/writes
  ```

## 2. Network Reachability & Offline Sync
- **No Blocking Calls on Main Thread**: Never make synchronous HTTP network requests on the UI thread (`URLSession.shared.data(from:)` inside a button action without `Task`).
- **Offline Queue**: Enqueue mutating actions into a local SQLite table when offline.
- **Sync Conflict Resolution**: Implement Last-Write-Wins (LWW) or explicit Conflict Resolution UI when syncing offline changes back to the cloud.

## 3. System Permission Courtesy
- **Never Trigger Modals on Launch**: Asking for Camera, Microphone, or Accessibility permissions within 0.5s of first app launch guarantees user rejection.
- **Contextual Priming**: Explain *why* the permission is necessary in custom UI immediately before invoking the system prompt:
  ```swift
  // Show in-app explanation sheet first, then:
  AVCaptureDevice.requestAccess(for: .video) { granted in ... }
  ```

## 4. Local Telemetry & Crash Path Scrubbing
- Scrub local file paths (`/Users/username/secret_docs/file.txt` -> `[USER_HOME]/secret_docs/file.txt`) before sending crash reports to Sentry or Bugsnag to preserve user privacy.
