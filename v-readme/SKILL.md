---
name: v-readme
description: "Rewrite or refresh a project README from verified product behavior, preserving branding and separating user installation from developer setup. Supports desktop apps, websites, web apps, and CLI projects."
---

# Unified Product README Generator

Transform any app, desktop software, or web project README into a clean, user-first product page by verifying real codebase evidence first.

## Evidence and execution

Verify user-facing claims and install commands against source and manifests. Keep evidence in your working notes; write clear product copy without internal evidence labels or invented metrics.

Resolve bundled `scripts/` and `references/` from the directory containing this `SKILL.md`, and pass the target repository explicitly. If a helper cannot run, inspect the relevant source directly and state the remaining verification gap. Stop after the requested deliverable and applicable checks are complete.

## Core Rules

- **Repo-Agnostic Truth**: Derive the product name, branding, install steps, and feature copy from the target repo's current code and assets each time. Never invent features, flows, screenshots, defaults, limits, or platform support.
- **Top Branding**: Keep the app or site logo at the very top of the README if the repo already has one. Do not push the logo below the intro paragraphs.
- **User-First Ordering**: The main feature section must be user-facing, benefit-focused, and backed by current code. Internal architecture, technical implementation notes, and developer build commands belong in the setup section at the bottom.
- **Screenshot Discipline**:
  - Store new captures in `docs/screenshots/` (or preserve an existing established directory like `docs/images/`).
  - Use an HTML table gallery for structured, responsive display.
  - Report whether screenshots were freshly captured, reused from valid existing assets, or pending capture.

## Workflow

### 1. Detect Repository & Application Type
Run the deterministic detector:
```bash
bash scripts/detect-app-type.sh /absolute/path/to/repo
```
This identifies:
- **Desktop / Native App** (macOS Swift, AppKit, SwiftUI, Electron, Tauri, Qt, Python GUI)
- **Web App / Site** (Vite + React, Next.js, Astro, Nuxt, static web)
- **CLI / Library** (Python package, Rust crate, Go module)

### 2. Discover Surface Inputs
Based on detected type, run the specialized surface scanner:
- For **Apps / Desktop**:
  ```bash
  bash scripts/discover-app-readme-surface.sh /absolute/path/to/repo
  ```
  Follow [references/readme-app-spec.md](references/readme-app-spec.md).
- For **Websites / Web Apps**:
  ```bash
  bash scripts/discover-web-readme-surface.sh /absolute/path/to/repo
  ```
  Follow [references/readme-web-spec.md](references/readme-web-spec.md).
- Consult [references/screenshot-capture-guide.md](references/screenshot-capture-guide.md) for route capture details.

### 3. Read Context Files (In Order)
1. `CLAUDE.md` / `GEMINI.md`
2. `notes/00_overview.md` to `notes/03_architecture.md` if present
3. Existing `README.md`
4. Main entrypoint / router definitions (`App.tsx`, `routes.ts`, `main.py`, `*App.swift`)
5. Manifests and build scripts (`package.json`, `Cargo.toml`, `pyproject.toml`, `Makefile`)

### 4. Build README in Canonical Product Order
1. **Title and Top Logo / Hero Branding**
2. **One-sentence value proposition & subtitle**
3. **Product Preview / Screenshot Table** (HTML `<table>` layout)
4. **Key Features** (bullet points with user benefits, not file internals)
5. **Quick Start / Installation** (for end-users: binary downloads, dmg, web URL, or clean single-line run command)
6. **Developer Setup & Verification** (clone, prerequisites, dependencies, dev server, test suite)
7. **Tech Stack & Architecture Highlights** (concise table or list)
8. **License**

### 5. Final Self-Check
- [ ] Logo stays at the top.
- [ ] All screenshot paths resolve to real files on disk.
- [ ] No unconfirmed features or speculative roadmap promises.
- [ ] End-user install is clearly separated from developer setup.
