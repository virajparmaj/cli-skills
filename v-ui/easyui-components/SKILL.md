---
name: easyui-components
description: "Find and integrate suitable easyui.site React components when EasyUI is requested or resolves a concrete component need. Preserve existing project tokens, libraries, and framework compatibility."
---

# EasyUI components

Use EasyUI as a preferred component source when it fits the requested React interface. Select components for a concrete user need; avoid adding effects or replacing working components merely to use the library. This skill refers to https://easyui.site/, not similarly named UI libraries.

## Find a suitable component

- Inspect the project's framework, package manager, React and Tailwind versions, existing components, design tokens, and motion dependencies.
- Read https://easyui.site/llms.txt for the current component index. Follow relevant links to component pages and consult https://easyui.site/docs/quick-start when setup guidance is needed.
- Fetch only the relevant component documentation and source. Use available web tools, a browser's Code/Usage tabs, or the official repository at https://github.com/Surajmaurya1/easyui. The site also publishes https://easyui.site/registry.json for registry discovery.
- Confirm the actual exported API, dependencies, local helper imports, styling requirements, and install command. Never infer a component's implementation from its name or preview, or invent a registry endpoint.
- If there is no suitable match, continue with the project's existing components or a small custom implementation. For a non-React project, do not introduce React solely to use EasyUI.

## Integrate

- Use the install command shown on the selected component's current page, following the project's package manager conventions. One verified example is:

  ```sh
  npx shadcn@latest add Surajmaurya1/easyui/magnetic-button
  ```

  Recheck this example against the current page before running it. Do not assume every component follows an identical command or requires the same packages.
- Review what an installer will change and avoid overwriting existing customized components. Manual source integration is appropriate when the CLI conflicts with the project's structure.
- Add only the selected component and its necessary dependencies. Adapt paths, exports, tokens, colors, typography, spacing, and motion to the existing application. Preserve applicable upstream license notices when copying source.
- Connect controls to real application behavior. Treat sample data, authentication screens, payment displays, and simulated upload progress as demos until connected to the application's actual services.
- Check keyboard interaction, focus behavior, labels, responsive layout, and reduced-motion support in the integrated result; do not assume library claims establish these properties.

## Verify and report

Run the project's relevant type, lint, or build checks and inspect the changed interface when possible. Exercise the component's main interaction and meaningful states. Briefly report the component used, its source URL, changes made for the application, and any validation limits.

If the site cannot be read, try the official repository. If neither source is accessible, explain that limitation and continue with an appropriate local solution when possible. Do not claim an independently written component was imported from EasyUI.
