# App README Spec

Use this spec when refreshing the README for an app or desktop-software repo.

## Required section order

1. App name
2. Logo at the top
3. One short intro sentence explaining what the app does
4. App Preview / Screenshots
5. User-facing features
6. Install / Getting Started
7. Developer Install / Local Setup

## Logo and branding rules

- Keep the existing logo or hero brand image at the top when the repo already
  uses one.
- Do not move the logo below the intro.
- Preserve existing branding assets and paths when they still match the current
  product.
- Do not replace branding casually just to make the README look newer.

## Screenshot capture

- Capture real screenshots of the running app before writing the README when
  the repo can be launched locally.
- Follow
  [`references/screenshot-capture-guide.md`](screenshot-capture-guide.md) for
  the app-type-specific workflow and fallbacks.
- Target 4-6 key views. Do not exceed 8 screenshots.

## Screenshot storage

- Store screenshot assets in `docs/screenshots/`.
- Use descriptive filenames such as `main-view.png` or
  `settings-panel-dark.png`.
- Compress screenshot files larger than 500 KB before embedding them.

## Screenshot gallery format

Use HTML tables for side-by-side layout because GitHub strips most CSS:

```html
<table>
  <tr>
    <td width="33%"><img src="docs/screenshots/main.png" width="280" alt="Main view"><br><sub>Main view</sub></td>
    <td width="33%"><img src="docs/screenshots/settings.png" width="280" alt="Settings"><br><sub>Settings</sub></td>
    <td width="33%"><img src="docs/screenshots/feature.png" width="280" alt="Feature"><br><sub>Feature name</sub></td>
  </tr>
</table>
```

Rules:

- Use 2-3 images per row at roughly 280 px width each.
- Put short captions in `<sub>` tags below each image.
- If there are only 1-2 screenshots, reduce the number of columns.
- Put dark-mode screenshots in a second row or inside a `<details>` block.
- Do not rely on scrolling galleries, flexbox, or CSS-only layout tricks.

## Screenshot fallback

- If capture fails and no existing screenshots are still usable, insert
  `<!-- Screenshots pending -->`.
- Never insert broken image links.
- Never silently substitute mockups or generated images.

## Copy rules

- Keep the tone simple, clean, and user-first.
- Prefer one short intro sentence over a long paragraph.
- Make the feature section benefit-focused and easy to scan.
- Only include user-facing features that are implemented right now.
- Remove or rewrite outdated, internal, or overly technical details from the
  top sections.
- Keep architecture, implementation detail, and low-level technical notes out of
  the main feature section unless they are required for user understanding.
- Keep the README product-page first, setup doc second.

## Feature verification rules

- A feature should appear in the main feature section only if current code,
  scripts, or tests support it.
- Prefer direct evidence from:
  - app entrypoints
  - UI/menu/settings files
  - install/build scripts
  - test coverage
- Treat old README copy, roadmap docs, and aspirational notes as secondary
  context, not proof.
- If a feature is conditional, describe it honestly.
  - Example: `Shows weekly usage when your account exposes it.`
- If support is missing or unclear, remove the claim or mark it outside the
  main feature list.

## Install section rules

### Normal user install

Keep this section short and practical.

Include:

- who the app is for
- required OS or platform support
- required external tooling only if a normal user truly needs it
- the shortest valid install path
- first-run or trust steps only when relevant
- uninstall steps if the repo has a supported uninstall path

### Developer install / local setup

Put this at the end.

Include:

- how to clone or download locally
- how to install dependencies
- how to run locally
- how to build
- how to test
- required OS/tooling/version requirements
- permissions, environment, or local-path notes when relevant

## Validation checklist

Before finishing a README refresh, confirm:

- the section order matches this spec
- the logo remains at the top
- referenced screenshot files exist
- screenshot gallery uses HTML table markup
- screenshot captions are short
- screenshot image files stay under the size target
- feature bullets are evidence-backed
- install steps match the real scripts and tooling
- developer setup is complete and moved to the end
- outdated defaults, limits, permissions notes, or workflows have been corrected

## Out of scope

- Website marketing copy strategy
- Landing-page SEO structure
- Blog or docs-site organization
- Rebranding unrelated product assets
