---
name: v-ui
description: "Build, restyle, or review web UI using relevant Good CSS, Component Gallery, EasyUI, BoardUI, or Stageshow guidance. Preserve the project's framework and design system; distinguish working UI from staged illustrations."
---

# V UI

Use one entry point to choose the right UI guidance for the user's task. The five bundled skills have different jobs. Read only the modules and references that improve the current work; invoking this skill does not require running every workflow.

## Start with the requested result

- Determine whether the user wants working application UI, a pattern comparison, a styling fix, a review, or a staged product illustration. A request to build a page, dashboard, form, or app means working UI unless the user asks for a mockup or demonstration.
- Inspect the relevant existing UI and project conventions before choosing components. Preserve the user's design references, selected framework and libraries, existing tokens, and authorization boundaries. A review stays read-only; a styling request does not authorize a redesign.
- Select the modules below yourself; do not ask the user to choose a skill. Ask about the actual desired result only when missing information materially changes the deliverable and cannot be inferred.

## Select the relevant modules

| Need | Read | Role |
| --- | --- | --- |
| Write, edit, or review CSS, Tailwind, inline styles, layouts, or responsive behavior | [good-css/SKILL.md](good-css/SKILL.md) | Implementation techniques for styling. Use with other modules whenever styling is involved. |
| Choose an interaction pattern, identify a component name, or compare how design systems solve a UI problem | [component-gallery/SKILL.md](component-gallery/SKILL.md) | Research and discovery across design systems. Follow selected entries to their original documentation or code. |
| Add or enhance a React component where an EasyUI implementation may fit, or the user explicitly requests EasyUI | [easyui-components/SKILL.md](easyui-components/SKILL.md) | Obtain actual component code and adapt it to the application. |
| Build or extend a BoardUI project, explicitly use BoardUI, or select a coherent component system for a compatible React dashboard or chat interface | [boardui/SKILL.md](boardui/SKILL.md) | Use BoardUI's official catalog, source installation, semantic tokens, typography, and page recipes. Apply the integration guidance below before project setup. |
| Create a mocked product screen, marketing product shot, feature-card illustration, or authored animation with simulated cursor interactions | [stageshow/SKILL.md](stageshow/SKILL.md) | Compose and rehearse a still or animated scene using the bundled React/CSS kit. |

Open each selected module's `SKILL.md` before using it. Resolve its relative references, kit, examples, and scripts from that module's own folder. Retain the full bundled resources; this entry point is routing guidance, not a replacement for their instructions.

## Combine them purposefully

- For working UI, start with the existing component system. Apply Good CSS when styling. Consult Component Gallery when the pattern or behavior needs research; consult EasyUI when suitable React component code may help. Consider BoardUI when a compatible project needs a coherent dashboard or chat component system, or already uses it. These sources do not require adding a library or replacing a working local component.
- For an explicit EasyUI request, start with EasyUI and use Good CSS for integration. A second gallery search is unnecessary unless it resolves a remaining decision.
- For an explicit BoardUI request or an existing BoardUI project, start with BoardUI and apply its semantic tokens, composite type utilities, and component behavior. Use Good CSS for compatible layout and interaction techniques; retain BoardUI token references instead of introducing conflicting literal colors or typography.
- For illustrations and demos, use Stageshow and Good CSS as needed. A landing page may have both working page controls and a Stageshow hero scene; keep each workflow scoped to its part of the page.
- Component Gallery, EasyUI, and BoardUI can overlap during discovery. Choose the more relevant source first; use additional sources only when they add something concrete. Avoid repeated browsing, unnecessary dependencies, or mixing several visual systems.
- Stageshow's simulated clicks, data, and scene state communicate a story. They do not implement backend services or establish that a feature works. Real controls, validation, persistence, uploads, authentication, and payments require the actual application behavior appropriate to the task.
- Apply each module's requirements to its relevant work. When guidance conflicts, follow the user's explicit intent and project constraints. Preserve existing design tokens and supported browser behavior; do not let a module's example impose an unrelated visual style or framework.

## BoardUI integration

The bundled [official skill](boardui/SKILL.md) and its references provide BoardUI knowledge; project initialization happens only when implementing with BoardUI. Check current [installation docs](https://www.boardui.com/installation) and actual package peer requirements. The documented stack is React 19 and Tailwind CSS v4. Do not upgrade React or Tailwind solely because a UI task triggered this router; use the existing system when adopting BoardUI would require an out-of-scope migration.

For a selected, compatible BoardUI implementation, run commands from the destination package using the project's package manager conventions. The documented npm examples for a coding agent are:

```sh
npx boardui@latest init --yes
npx boardui@latest add button select date-picker --yes
```

Initialize only when needed and add only the requested components, using exact names from the catalog. `--yes` installs required dependencies and keeps existing files; do not add `--overwrite` merely to resolve an install conflict. Inspect retained files for compatibility. Init writes theme, typography, global styles, the `cx` utility, and agent design rules; merge them with existing project conventions and preserve unrelated `AGENTS.md` guidance. Follow the CLI's printed stylesheet/font wiring for the actual framework instead of copying a Next.js layout into Vite.

For monorepos or custom aliases, configure `boardui.json` in the destination package before the first install and follow the docs for exports and Tailwind source detection. Verify free versus Pro availability for selected items; use existing authorized license access when available and otherwise offer a suitable free option. Adding this module does not configure an MCP server or authorize a purchase.

## Typical requests

| User request | Likely selection |
| --- | --- |
| Fix this mobile layout | Good CSS; keep the fix scoped. |
| Build a working React dashboard | Good CSS, with EasyUI, BoardUI, or Component Gallery when a component decision benefits from them and the stack fits. |
| Should this interaction be a drawer or a dialog? | Component Gallery; compare the usage guidance before implementation. |
| Add an EasyUI animated button | EasyUI and Good CSS. |
| Build a BoardUI data table or chat page | BoardUI and compatible Good CSS guidance; verify setup, tokens, actual component API, and license availability. |
| Make a looping product demo for the hero | Stageshow and Good CSS. |
| Review this existing component without editing | Relevant styling or pattern guidance; report findings without mutations. |

## Finish at the right depth

For implementation, verify the affected interactions, relevant states, responsive behavior, keyboard and focus behavior, and applicable reduced-motion handling. Run project checks appropriate to the change. Follow Stageshow's visual rehearsal workflow when creating a staged scene. Do not build extra test or audit machinery for trivial changes.

Briefly identify which modules were useful, what changed or was found, the sources used when external components informed the work, and meaningful verification limits. Do not claim that automatic skill selection, upstream tags, or an unchecked visual preview proves correctness.

For bug findings in a UI review, give the concrete trigger, evidence, confidence, and frequency (1-10) x impact (1-10) = score with brief rating reasons. The default fix threshold is 5: lower scores go once to an existing authorized backlog or `Deferred issues` without code edits; higher scores are eligible only within authorized implementation scope. Remote issue creation needs existing authorization. Stop after the requested behavior and required checks pass.
