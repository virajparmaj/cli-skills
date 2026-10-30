# Design Slop & Codebase Slop Guide for Websites & Web Apps

Vibe-coding engines (v0, Lovable, Bolt, Cursor, Claude) frequently produce two categories of structural defects: visual design slop that immediately gives away AI-generated templates, and codebase slop that causes technical debt.

---

## Part 1: Design Slop Indicators (The 10 AI UI Smells)

### 1. Tags / Badge Spam
- **The Pattern**: Slapping `<Badge>` pills on every card, feature title, and navbar item ("NEW", "FEATURE", "AI-POWERED", "BETA", "v1.2", "POPULAR").
- **Why It's Slop**: Dilutes visual hierarchy. When everything is flagged as special, nothing is.
- **Fix**: Remove 80% of badges. Badges should be reserved exclusively for actionable system statuses (e.g., "Out of Stock", "Payment Failed").

### 2. Italicized Words
- **The Pattern**: Arbitrary italicization in headings and hero copy (*effortlessly*, *seamlessly*, *intelligently*, *instantly*, *automatically*).
- **Why It's Slop**: The hallmark of AI copywriting trying to simulate editorial gravitas. It breaks rhythm and draws attention to empty buzzwords.
- **Fix**: Strip italics and rewrite copy using concrete verbs that describe exact product outcomes.

### 3. Instrument Serif + Negative Kerning
- **The Pattern**: Forcing a high-contrast editorial serif (Instrument Serif, Playfair Display) paired with `tracking-tighter` (`-0.05em` letter spacing) into technical landing pages.
- **Why It's Slop**: Homogenizes products into an identical "vibe-coded indie hacker" aesthetic; negative tracking causes characters to collide on low-DPI or mobile displays.
- **Fix**: Choose typography reflecting the product domain. Clean, legible sans-serifs (Geist, Inter, Plus Jakarta Sans) with standard tracking provide timeless clarity.

### 4. Over the Top Detailed UI
- **The Pattern**: Faux telemetry graphs, mock terminal feeds, pseudo-complex metric counters, and miniature charts on landing pages for products that don't need them.
- **Why It's Slop**: Distracts users from the value proposition with decorative noise.
- **Fix**: Show real product screenshots or clean, high-fidelity UI states focused on primary user tasks.

### 5. Dividers Everywhere
- **The Pattern**: Slicing up cards and pages with hairline rules (`<Separator />`, `divide-y`, `border-t`, `border-b`) between every paragraph, icon, and button.
- **Why It's Slop**: Visual fragmentation. High-quality interfaces use whitespace (padding, margin, gap) to group content naturally.
- **Fix**: Remove dividers; increase vertical space using Tailwind `space-y-6` or `gap-8`.

### 6. Multiple Color Shades and Opacities
- **The Pattern**: Inconsistent alpha opacities (`bg-opacity-50`, `text-white/70`, `text-muted-foreground/60`, `bg-neutral-800/40`) resulting in 4-6 competing shades of gray in a single card.
- **Why It's Slop**: Murky contrast ratios that violate WCAG 2.1 AA standards; creates a muddy, uncalibrated visual hierarchy.
- **Fix**: Stick strictly to semantic design tokens (`bg-card`, `bg-muted`, `text-foreground`, `text-muted-foreground`) without ad-hoc opacity modifiers.

### 7. Containers with Borders (Box-in-a-Box)
- **The Pattern**: Deeply nested bordered containers: page in a card, containing section cards, containing item cards, containing pill cards, each with `border border-border rounded-lg bg-card p-4`.
- **Why It's Slop**: "Bento box fatigue." Borders dominate the viewport rather than the content.
- **Fix**: Flatten card nesting. Rely on subtle background contrast (`bg-muted/50`) or borderless sections grouped by whitespace.

### 8. Diagrams (The More Detailed, the Worse)
- **The Pattern**: Elaborate Mermaid diagrams, multi-node flowcharts, or decorative SVG pipeline graphs crammed into marketing pages.
- **Why It's Slop**: Decorative diagrams drift from reality, are unreadable on mobile screens, and serve as complexity posturing.
- **Fix**: Replace with a clear 3-step bulleted explanation or a simple high-level conceptual diagram.

### 9. Code Breadcrumbs
- **The Pattern**: Fake terminal headers (`bash $ npm install...`), pseudo-code blocks, or decorative breadcrumbs (`Home > Features > AI Engine > Core`) on simple marketing sites.
- **Why It's Slop**: Clutters the top of views and distracts from primary conversion calls-to-action.
- **Fix**: Remove fake terminal wrappers; keep navigation breadcrumbs functional only on deep (3+ level) documentation hierarchies.

### 10. Section Numbering
- **The Pattern**: Robotic numbered headings: "01 / Overview", "02 / Features", "03 / Architecture", "Step 01 - Getting Started".
- **Why It's Slop**: Dead giveaway of AI template scaffolding; rigid numbering breaks when sections are reordered or modified.
- **Fix**: Use descriptive, value-focused headers without artificial serial numbering.

---

## Part 2: Codebase Slop Indicators (The 9 Core Antipatterns)

### 1. Implicit Coupling
- **Symptom**: Components secretly read from or write to unversioned localStorage, global window variables, or rely on implicit parent re-render side-effects.
- **Fix**: Make dependencies explicit via component props, typed context, or explicit query hooks.

### 2. Layer-First Folders
- **Symptom**: Code organized by technical category (`components/`, `services/`, `utils/`, `hooks/`, `views/`) rather than by business domain.
- **Fix**: Reorganize into feature slices (`features/marketing/`, `features/pricing/`, `features/docs/`) with co-located components, hooks, and types.

### 3. Duplication
- **Symptom**: Repeated formatting logic, duplicate fetch helpers, and slightly varied CSS snippets across multiple files.
- **Fix**: Consolidate shared logic into canonical utility modules (`src/lib/formatters.ts`, `src/lib/api.ts`).

### 4. Representable Illegal States
- **Symptom**: Loose boolean state models (`isLoading: boolean`, `isError: boolean`, `data?: T`, `error?: Error`) allowing conflicting states to coexist.
- **Fix**: Enforce discriminated unions: `{ status: 'loading' } | { status: 'error'; error: Error } | { status: 'success'; data: T }`.

### 5. God Files
- **Symptom**: Single files ballooning beyond 300 to 1,500+ LOC as the AI continuously appends code rather than modularizing.
- **Fix**: Decompose into focused single-responsibility files: extract subcomponents, custom hooks, and pure transformation helpers.

### 6. Shotgun Surgery
- **Symptom**: Changing a single design token, feature flag, or link requires editing 10+ disparate files.
- **Fix**: Centralize configuration in single sources of truth (`src/config/site.ts`, `src/config/navigation.ts`).

### 7. Layering Violations
- **Symptom**: UI components executing raw database queries or direct backend SDK mutations in JSX handlers.
- **Fix**: Enforce clear boundary contracts: UI Component -> Custom Hook / Action -> API Client -> Backend Service.

### 8. Pass-Through Wrappers
- **Symptom**: Pointless 1-line facade functions that merely delegate to another function without adding logic, validation, or transformation.
- **Fix**: Remove the redundant indirection; invoke the underlying function directly.

### 9. Errors / Validation Not at the Boundary
- **Symptom**: Validation checks placed deep inside helper functions rather than at the system entry point.
- **Fix**: Validate inputs strictly at the boundary (API request handlers, form submission handlers via Zod) and guarantee clean, valid types internally.
