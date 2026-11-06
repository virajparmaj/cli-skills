# Screenshot Capture Guide

Use this guide after running `scripts/detect-app-type.sh` and
`scripts/discover-app-readme-surface.sh`.

All paths, launch commands, and screenshot filenames in this guide are
placeholders for the current `target repo`. Never reuse app-specific capture
commands or screenshot references from a different project unless they were
rediscovered from the target repo itself.

## 1. Choose the screenshot directory

- If the repo already uses a screenshot folder such as `docs/images/`, keep it
  unless there is a good reason to migrate.
- If no screenshot folder is established, use `docs/screenshots/`.
- Use one screenshot directory consistently for the refresh.
- Do not silently mix an existing screenshot folder with `docs/screenshots/`.

## 2. Capture status labels

Use one of these labels in your final report:

- `freshly captured`: new screenshot captured from the current running app
- `reused`: existing screenshot kept as a documented fallback
- `pending`: no usable screenshot was available, so the README should use
  `<!-- Screenshots pending -->`

## 3. Strategy table

| App Type | Primary Tool | Fallback |
| --- | --- | --- |
| Web (`web-next`, `web-vite`, `web-other`) | Preview-capable environment, preferably Claude Preview when available | `npx playwright screenshot` |
| Electron | Launch app, then capture the real window | macOS `screencapture`, otherwise ask the user |
| Python web | Preview-capable environment, preferably Claude Preview when available | `npx playwright screenshot` |
| Python GUI | Launch app and capture the real window | macOS `screencapture`, otherwise ask the user |
| macOS native | Build, launch, and capture the real window | macOS `screencapture`, otherwise ask the user |
| CLI | Skip screenshots | Add a brief note when no visual UI exists |

## 4. Generic preview workflow for web apps

Use a preview-capable environment first. If your environment exposes Claude
Preview tools, prefer that path.

1. Create `.claude/launch.json` in the target repo if the preview tool expects
   one and the repo does not already have it.
2. Use the detected `Dev Command` and `Dev Port` from `detect-app-type.sh`.
3. Start the preview session and watch logs until the app is ready.
4. Visit the routes and UI surfaces reported by
   `discover-app-readme-surface.sh`.
5. Resize the viewport to `1280x800` before each capture.
6. Save screenshots to `<screenshot-dir>/<surface>-light.png`.
7. Trigger settings panels, menus, modals, dialogs, drawers, popovers, and
   sheets before capturing those surfaces.
8. If dark mode is supported, capture the main surfaces again as
   `<screenshot-dir>/<surface>-dark.png`.
9. Stop the preview session after captures complete.

For Claude Preview environments, the usual sequence is:
`preview_start` -> wait for `preview_logs` -> navigate with `preview_eval` ->
stabilize with `preview_snapshot` -> size with `preview_resize` -> capture with
`preview_screenshot`.

## 5. Playwright CLI fallback

Use Playwright when the app is a local web server but preview tooling is
unavailable.

```bash
npx playwright install chromium
npx playwright screenshot http://localhost:<port> <screenshot-dir>/<name>.png --viewport-size="1280,800"
```

If a route needs time or a selector before capture, use a small script or the
CLI with a wait condition before taking the screenshot. Keep filenames aligned
to the README gallery plan. Record the attempted command and target path in the
final note.

## 6. macOS `screencapture` workflow

Use this for Electron, Python GUI, and native macOS apps when browser-based
capture does not apply.

1. Build and launch the app.
2. For native macOS apps, treat reuse of older screenshots as fallback only.
   "Real screenshots" means capturing the current app window after a real
   launch, not just reusing old assets.
3. Bring the target window to the front.
4. Capture the window directly:

```bash
screencapture -x -l<windowid> <screenshot-dir>/<name>.png
```

5. If needed, use AppleScript to open menus, preferences, or dialogs first.
6. If window capture is not reliable, fall back to a region capture:

```bash
screencapture -x -R<x,y,w,h> <screenshot-dir>/<name>.png
```

7. Record the attempted build or launch command, capture command, and output
   path in the final note.

## 7. Environment handling

- Check `.env.example`, sample config files, and README setup notes before
  starting the app.
- Copy `.env.example` to `.env` only when the repo already expects that flow.
- Never invent secrets, API keys, or credentials.
- If real credentials are required, say so clearly instead of faking a working
  state.
- Install missing dependencies only when needed by the capture path.
- Retry startup at most 3 times before falling back.
- If fresh capture is blocked or skipped, explain the blocker before reusing
  screenshots or marking them pending.

## 8. Fallback chain

Use this order:

1. Preview-capable capture
2. Playwright CLI
3. macOS `screencapture`
4. Reuse still-valid existing screenshots after documenting why fresh capture
   was blocked or skipped
5. Insert `<!-- Screenshots pending -->`

Never leave broken image links in the README.

## 9. File conventions

- Store screenshots in the chosen screenshot directory.
- Use `<surface>-<variant>.png` naming, for example
  `dashboard-light.png` or `settings-dark.png`.
- Target `1280x800` desktop captures.
- Compress images larger than 500 KB, for example:

```bash
sips --resampleWidth 1280 <screenshot-dir>/<name>.png
```

- Target 4-6 screenshots and cap the gallery at 8.

## 10. Required final screenshot note

The final response must include a short verification note that lists:

- which screenshots were newly captured
- which screenshots were reused
- which screenshots are pending
- what command, tool, or capture path was attempted
- what blocker occurred if fresh capture failed or was skipped
