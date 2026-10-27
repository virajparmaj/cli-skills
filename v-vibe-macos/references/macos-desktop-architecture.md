# macOS Desktop Architecture & Stability Guide

Vibe-coding a desktop app often leads to web wrappers that consume 800MB RAM, burn battery in the background, corrupt user databases on crash, and fail Apple review. Follow these architectural standards.

---

## 1. Local Database & SQLite Integrity
- **WAL Mode (Write-Ahead Logging)**: Always enable WAL mode on SQLite / CoreData / SwiftData databases. Default rollback journals lock the entire database during writes, causing UI freezes and "database is locked" crashes.
  ```sql
  PRAGMA journal_mode = WAL;
  PRAGMA busy_timeout = 5000;
  PRAGMA synchronous = NORMAL;
  ```
- **Local Database Migrations**: Desktop apps cannot migrate on the server. Write schema migrations that execute sequentially on launch (e.g. `v1_to_v2.sql`, GRDB migrations).
- **Corruption Recovery**: Implement a fallback to back up and re-initialize a corrupted SQLite database, rather than crashing on launch forever.

## 2. Atomic File Writes
- **Never overwrite files directly** (`fileHandle.write(...)` or `.write(to: url)` without atomic options).
- If the app crashes, OS reboots, or user pulls the power cord mid-write, direct writes leave a zero-byte or corrupt file.
- **Swift Mandate**:
  ```swift
  try data.write(to: fileURL, options: [.atomic])
  ```
  This writes to an auxiliary temporary file on the same volume and renames it atomically via `renamex_np` / `rename()`.

## 3. Battery Conservation & App Nap
- **No Unthrottled Timers**: Never run `Timer.scheduledTimer(withTimeInterval: 0.1, ...)` or while-true polling loops for state checks. Use Combine, Swift Concurrency `AsyncStream`, or system notification observers (`NSWorkspace.didWakeNotification`).
- **Activity Tracking**: When performing long background work (e.g. video rendering, syncing), notify macOS via `ProcessInfo.beginActivity`:
  ```swift
  let activity = ProcessInfo.processInfo.beginActivity(
      options: [.userInitiated, .idleSystemSleepDisabled],
      reason: "Exporting high-resolution asset"
  )
  defer { ProcessInfo.processInfo.endActivity(activity) }
  ```

## 4. Retain Cycles & Memory Hygiene
- Long-running desktop apps stay open for weeks. Retain cycles that are harmless in short-lived web sessions will leak gigabytes over time.
- **Rule**: Always capture `[weak self]` in closures passed to async tasks, notification centers, and network publishers:
  ```swift
  Task { [weak self] in
      guard let self else { return }
      await self.updateUI()
  }
  ```

## 5. Menu Bar & Multi-Display UI Polish
- **Status Item Sizing**: Set `statusItem.button?.image?.isTemplate = true` so the menu bar icon automatically adapts between Dark Mode and Light Mode.
- **Notch Avoidance**: On modern MacBook screens with camera notches, menu bar items can get crowded or hidden. Provide a native window fallback or keyboard shortcut (`Cmd+Shift+...`).
- **Standard Keyboard Shortcuts**: Desktop users expect macOS conventions: `Cmd+,` for Settings/Preferences, `Cmd+W` to close window, `Cmd+Q` to quit.

## 6. Auto-Update Safety (Sparkle)
- If distributing outside the Mac App Store, use **Sparkle 2.x**.
- **EdDSA Signatures**: Always sign app cast updates with `SUPublicEDKey` (Ed25519). Unsigned auto-updates allow man-in-the-middle code execution.
- **Rollback Safety**: Retain previous version backup until new version launches successfully once.
