---
name: component-gallery
description: Find and adapt UI patterns using component.gallery when building or improving web pages, forms, navigation, tables, dialogs, and other interface components. Use for component selection, naming, design-system comparisons, and Component Gallery requests. Consult relevant examples when useful while respecting the project's existing stack and design system.
---

# Component Gallery

Use https://component.gallery/components/ as a reference for selecting interface patterns and discovering implementations. It aggregates examples from real design systems; it is not a single installable component package. Most entries require following the original design system's documentation or source.

## Find relevant examples

- Identify the user's actual interaction need and inspect the project's framework, existing components, dependencies, and visual conventions.
- Open https://component.gallery/components/ and follow the relevant category. Use the listed alternative names to find equivalent patterns when terminology differs.
- Example category: https://component.gallery/components/modal/ links to dialog implementations. Use https://component.gallery/design-systems/ when comparing libraries or looking for a coherent component family.
- Narrow examples by the project's technology and available code, usage guidance, and accessibility documentation. Treat gallery tags, screenshots, and maintenance indicators as discovery aids; confirm current facts at the original source.
- Compare a small relevant set when the choice matters. Prefer an existing project library or native platform element when it meets the need. Do not install multiple design systems simply to reproduce their appearances.

## Follow the original source

- Open the selected entry's official component documentation. Read its intended use, limitations, API, interaction behavior, installation instructions, and any relevant accessibility guidance before integrating code.
- Fetch actual examples or source when needed; a gallery screenshot does not establish implementation details or an exported API. Verify package names, versions, framework compatibility, and licensing at the original source.
- Use an upstream package when it fits the project, adapt permitted source when appropriate, or implement the pattern using existing local primitives. Never invent a Component Gallery package, registry endpoint, CLI command, or component export.
- Keep inspiration and imported code accurately described. Retain applicable license notices for copied source. If a reference cannot be reached, try its official repository or another suitable entry; disclose unresolved limits instead of claiming source verification.

## Adapt and verify

- Preserve the application's tokens, typography, spacing, and established component conventions. Add only dependencies needed for the selected implementation; avoid replacing working components without a task-related reason.
- Connect interactions to real application state and cover relevant loading, empty, error, disabled, and recovery behavior.
- Check semantics, keyboard operation, focus, labels, responsive behavior, and reduced motion as relevant. Exercise the main interaction and run applicable project checks.
- Briefly identify the selected pattern, link its gallery category and original source, and report important adaptations or validation limits.

Use the gallery when it can resolve a component decision; skip unnecessary research for unrelated backend tasks or trivial changes with an already-established pattern. The user's explicit component or library choice takes priority. Other sources, including EasyUI, can supply implementation code when appropriate; this skill does not require using them.
