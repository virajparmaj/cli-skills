---
name: good-css
description: "Apply modern CSS to page and component layout, styling, responsive behavior, and interaction states. Use for CSS, Tailwind, inline styles, or CSS-in-JS work within the project's browser and design constraints."
---

# Good CSS

Prefer intrinsic layout and native CSS when they fit the requested behavior. Preserve the existing design tokens, component system, supported browsers, and user-selected style; do not rewrite unrelated styling to apply these preferences.

Each technique is a set of properties and values, so it works in any authoring system. Class names in the examples are placeholders. Write the declarations in what the project already uses, whether that is a stylesheet, Tailwind utilities or StyleX objects. Where that system has no shorthand for a declaration, write it the long way, as a Tailwind arbitrary property or a rule in the project's CSS file. Use the technique when supported and appropriate; keep a breakpoint or script when it implements behavior CSS cannot express reliably in the target environment.

## In all CSS

These need no file.

- Write `inline` and `block` properties in place of left, right, top and bottom. Tailwind has them too, as in `mbs-`, `pe-` and `inset-bs-`, so never write `mt-`, `pr-` or `top-`. The block ones need Tailwind 4.2. Below it, write them as arbitrary properties, as in `[margin-block-start:theme(spacing.4)]`.
- Reuse project color tokens. For new color definitions, prefer `oklch()` when target browsers support it; derive hover, tint, or transparent variants with `color-mix()` where appropriate. Do not replace semantic BoardUI or other design-system tokens with literals.
- Put sizes that grow with the screen in one `clamp()` token.
- Put every `:hover` rule inside `@media (hover: hover) and (pointer: fine)`.
- Keep a visible keyboard focus indicator with `:focus-visible`; prefer an outline that survives forced-colors mode. Remove a default outline only when an equivalent visible focus treatment is present.
- Give everything pressable an `:active` state.
- Put a transition that moves or scales something inside `@media (prefers-reduced-motion: no-preference)`. Name its properties, never `all`, and never use `ease-in`.
- Use `overflow: clip` for purely visual clipping. Keep `hidden`, `auto`, or `scroll` where scroll-container behavior, focus scrolling, sticky positioning, or existing layout semantics require it.

## Read the entry before you write

Each file holds entries with the CSS and its rules. The rules are the conditions the CSS needs to work, so keep all of them. Read only the files whose row matches what you are about to write. One component matches two or three, and a whole page matches most of them.

| Read | Before you write |
| --- | --- |
| `references/foundations.md` | a reset or base stylesheet, a set of color tokens, dark mode, a type or spacing scale |
| `references/layout.md` | a page or section container or any centered `max-width` wrapper, whether or not anything goes edge to edge, a grid of cards, cards whose parts line up, a sidebar, a component placed in slots of different widths, overlapping layers, centered content that can overflow |
| `references/spacing-and-shape.md` | spacing between sections, elements stacked one above another, one item pushed to the far end of a row or column, nested rounded corners |
| `references/text-and-media.md` | text or images that come from a user or a CMS, such as names, titles, excerpts, thumbnails, avatars and embeds, an icon next to a label, a label that looks off-center, numbers in a column |
| `references/interaction.md` | the focus, hover and press states of a button, link, input or card, a small tap target, a clickable card, form validation, a textarea, a parent styled by what it contains, page scroll locked behind a modal |
| `references/motion.md` | easing and duration tokens, one state change that drives several values, a shadow that changes on hover, a transition between pages, the indicator under an active tab |
| `references/show-and-hide.md` | a dialog, popover, dropdown menu or accordion |
| `references/scroll-and-viewport.md` | a carousel, a row that may overflow, a modal body, chat list or drawer that scrolls between a header and a footer, in-page links under a sticky header, an app shell on desktop or on a phone |

## Left out on purpose

Never add `text-box` trim on `*`, `text-rendering: optimizeLegibility`, or a reset that puts `display: contents` or one shared grid cell on every element. `references/foundations.md` has the reasons.

## Browser support

Most entries end with a `Support:` line. Treat version claims as research leads and verify support for a selected feature against current primary documentation when it matters. This skill sets no browser floor. Weigh the line against the browsers the project targets, and tell the user when something you used is missing from one of them.

## Motion

Whether something should animate, the design or review of motion, springs, gestures and drag, and checks on a real phone belong to Emil Kowalski's skills `animate`, `review-animations`, `improve-animations`, `find-animation-opportunities` and `mobile-native`. When they are installed, use them for those jobs, and where one disagrees with a value here, use its value. When they are not, use the entries as written and add no motion beyond what an entry or the task calls for.
