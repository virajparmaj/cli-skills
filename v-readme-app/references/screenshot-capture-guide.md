# Screenshot Capture Guide

Use this guide after running `scripts/detect-app-type.sh` and
`scripts/discover-app-readme-surface.sh`.

## 1. Strategy table

| App Type | Primary Tool | Fallback |
| --- | --- | --- |
| Web (`web-next`, `web-vite`, `web-other`) | Preview-capable environment, preferably Claude Preview when available | `npx playwright screenshot` |
| Electron | Launch app, then capture the real window | macOS `screencapture`, otherwise ask the user |
| Python web | Preview-capable environment, preferably Claude Preview when available | `npx playwright screenshot` |
| Python GUI | Launch app and capture the real window | macOS `screencapture`, otherwise ask the user |
| macOS native | Build, launch, and capture the real window | macOS `screencapture`, otherwise ask the user |
| CLI | Skip screenshots | Add a brief note when no visual UI exists |

## 2. Generic preview workflow for web apps

Use a preview-capable environment first. If your environment exposes Claude
Preview tools, prefer that path.

1. Create `.claude/launch.json` in the target repo if the preview tool expects
   one and the repo does not already have it.
2. Use the detected `Dev Command` and `Dev Port` from `detect-app-type.sh`.
3. Start the preview session and watch logs until the app is ready.
4. Visit the routes and UI surfaces reported by
   `discover-app-readme-surface.sh`.
5. Resize the viewport to `1280x800` before each capture.
6. Save screenshots to `docs/screenshots/<surface>-light.png`.
7. Trigger settings panels, menus, modals, dialogs, drawers, popovers, and
   sheets before capturing those surfaces.
8. If dark mode is supported, capture the main surfaces again as
   `docs/screenshots/<surface>-dark.png`.
9. Stop the preview session after captures complete.

For Claude Preview environments, the usual sequence is:
`preview_start` -> wait for `preview_logs` -> navigate with `preview_eval` ->
stabilize with `preview_snapshot` -> size with `preview_resize` -> capture with
`preview_screenshot`.

## 3. Playwright CLI fallback

Use Playwright when the app is a local web server but preview tooling is
unavailable.

```bash
npx playwright install chromium
npx playwright screenshot http://localhost:<port> docs/screenshots/<name>.png --viewport-size="1280,800"
```

If a route needs time or a selector before capture, use a small script or the
CLI with a wait condition before taking the screenshot. Keep filenames aligned
to the README gallery plan.

## 4. macOS `screencapture` workflow

Use this for Electron, Python GUI, and native macOS apps when browser-based
capture does not apply.

1. Build and launch the app.
2. Bring the target window to the front.
3. Capture the window directly:

```bash
screencapture -x -l<windowid> docs/screenshots/<name>.png
```

4. If needed, use AppleScript to open menus, preferences, or dialogs first.
5. If window capture is not reliable, fall back to a region capture:

```bash
screencapture -x -R<x,y,w,h> docs/screenshots/<name>.png
```

## 5. Environment handling

- Check `.env.example`, sample config files, and README setup notes before
  starting the app.
- Copy `.env.example` to `.env` only when the repo already expects that flow.
- Never invent secrets, API keys, or credentials.
- If real credentials are required, say so clearly instead of faking a working
  state.
- Install missing dependencies only when needed by the capture path.
- Retry startup at most 3 times before falling back.

## 6. Fallback chain

Use this order:

1. Preview-capable capture
2. Playwright CLI
3. macOS `screencapture`
4. Reuse fresh existing screenshots
5. Insert `<!-- Screenshots pending -->`

Never leave broken image links in the README.

## 7. File conventions

- Store screenshots in `docs/screenshots/`.
- Use `<surface>-<variant>.png` naming, for example
  `dashboard-light.png` or `settings-dark.png`.
- Target `1280x800` desktop captures.
- Compress images larger than 500 KB, for example:

```bash
sips --resampleWidth 1280 docs/screenshots/<name>.png
```

- Target 4-6 screenshots and cap the gallery at 8.
