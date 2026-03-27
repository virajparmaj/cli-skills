# Workspace Patterns

Use this reference when auditing Vite + React + TypeScript + Tailwind projects.
These signals calibrate the audit so it matches common real-world patterns instead of generic frontend advice.

## Common Signals

- Shared stack: most projects are Vite + React + TypeScript apps using `@vitejs/plugin-react-swc`, Tailwind, and shadcn-style component structure.
- Notes-driven context exists in many repos. Look for `notes/03_architecture.md`, `notes/11_known_issues.md`, `notes/13_prompt_context.md` before diving into code.
- Manual chunking is inconsistent: some repos define `manualChunks` in `vite.config.ts`, others rely on Vite defaults.
- Route-level lazy loading is mixed: some apps lazy-load most routes while keeping the home route eager, others keep everything eager.
- State and data layers vary: Zustand, TanStack Query, large app-level Contexts, and multiple contexts all appear across projects.
- Font loading patterns are mixed: CSS `@import` for Google Fonts and HTML `preconnect` + `preload` + stylesheet links both appear. The `@import` variant is the more likely render blocker.
- Oversized `public/` assets are common and worth auditing by byte-to-display ratio. Multi-megabyte PNGs used as logos or thumbnails are a recurring pattern.
- Vercel configs vary in maturity: some repos have detailed security headers and cache rules, others only define rewrites.
- Bundle budget tooling is rare. Most repos lack `.size-limit.json` or equivalent.
- Virtualization is rare. Most list renders use plain `.map()` without TanStack Virtual or similar.
- Serverless cold-start anti-patterns exist: in-memory rate limiters in `api/` handlers reset on cold start.

## Why the Rubric Emphasizes These Checks

- Read `notes/` before code because repos often document architecture, known issues, and prior context.
- Audit image byte-to-display ratio because multi-megabyte assets in `public/` are common.
- Distinguish CSS `@import` from HTML font links because both patterns exist, and the `@import` variant is the more likely render blocker.
- Check context fan-out and selector usage because both large app-level contexts and good Zustand selector usage appear.
- Treat verified and unverified findings separately. Many perf concerns are plausible without proving their runtime cost from static code alone.
- Keep the bundle budget check explicit because most repos lack a size budget.
- Use the serverless cold-start add-on when `api/` exists. In-memory helpers that work locally can be fragile on serverless cold starts.
