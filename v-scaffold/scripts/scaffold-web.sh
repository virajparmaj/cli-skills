#!/usr/bin/env bash
#
# scaffold-web.sh — Bootstrap a Vite + React 18 + TypeScript (strict) + Tailwind +
# shadcn/ui project in Veer's exact conventions. Writes only convention files; does
# NOT run npm install and does NOT git commit (the caller decides when to do those).
#
# Usage: scaffold-web.sh <target-dir> [project-name] [--supabase] [--force]
#   <target-dir>   directory to scaffold into (created if missing)
#   [project-name] package.json name (default: basename of target-dir)
#   --supabase     include lib/supabase.ts typed-client stub + Supabase env vars
#   --force        overwrite existing convention files instead of skipping them
#
# Prints a "=== manifest ===" section listing every file it created or skipped so the
# model can echo the strict manifest without re-listing the tree.

set -euo pipefail

# --- args -----------------------------------------------------------------
if [[ $# -lt 1 ]]; then
  echo "usage: scaffold-web.sh <target-dir> [project-name] [--supabase] [--force]" >&2
  exit 2
fi

target_dir=""
project_name=""
want_supabase=0
force=0

for arg in "$@"; do
  case "$arg" in
    --supabase) want_supabase=1 ;;
    --force) force=1 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    --*) echo "Unknown option: $arg" >&2; exit 2 ;;
    *)
      if [[ -z "$target_dir" ]]; then
        target_dir="$arg"
      elif [[ -z "$project_name" ]]; then
        project_name="$arg"
      else
        echo "Unexpected argument: $arg" >&2; exit 2
      fi
      ;;
  esac
done

if [[ -z "$target_dir" ]]; then
  echo "error: target-dir is required" >&2
  exit 2
fi

if [[ -z "$project_name" ]]; then
  project_name="$(basename "$target_dir" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9._-')"
  project_name="${project_name#.}"; project_name="${project_name#_}"
  [[ -z "$project_name" ]] && project_name="app"
fi
if [[ ! "$project_name" =~ ^(@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$ ]]; then
  echo "Invalid npm project name: $project_name (use lowercase letters, digits, dots, hyphens, or underscores)." >&2
  exit 2
fi
mkdir -p "$target_dir"
target_dir="$(cd "$target_dir" && pwd)"

created=()
skipped=()
supabase_dependency=""
if [[ $want_supabase -eq 1 ]]; then
  supabase_dependency=$',\n    "@supabase/supabase-js": "^2.0.0"'
fi

# write_file <relative-path> <heredoc-marker-content-on-stdin>
# Skips existing files unless --force. Records manifest state.
write_file() {
  local rel="$1"
  local abs="$target_dir/$rel"
  if [[ -e "$abs" && $force -eq 0 ]]; then
    skipped+=("$rel")
    cat >/dev/null   # drain stdin
    return 0
  fi
  mkdir -p "$(dirname "$abs")"
  cat >"$abs"
  created+=("$rel")
}

# --- package.json ---------------------------------------------------------
write_file "package.json" <<EOF
{
  "name": "$project_name",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "engines": { "node": "^20.19.0 || ^22.13.0 || >=24.0.0" },
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint ."
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.6.0"$supabase_dependency
  },
  "devDependencies": {
    "@eslint/js": "^10.0.0",
    "eslint": "^10.0.0",
    "globals": "^15.0.0",
    "typescript-eslint": "^8.0.0",
    "@types/node": "^22.7.4",
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.7.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.13",
    "typescript": "^5.6.2",
    "vite": "~7.3.0"
  }
}
EOF

# ESLint flat config supports the emitted TypeScript source without a global install.
write_file "eslint.config.js" <<'EOF'
import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist/**"] },
  {
    files: ["src/**/*.{ts,tsx}"],
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    languageOptions: { globals: globals.browser },
  },
);
EOF

# --- tsconfig (strict) with @ alias --------------------------------------
write_file "tsconfig.json" <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"]
}
EOF

# --- vite config ----------------------------------------------------------
write_file "vite.config.ts" <<'EOF'
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
});
EOF

# --- tailwind + postcss ---------------------------------------------------
write_file "tailwind.config.ts" <<'EOF'
import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
        secondary: { DEFAULT: "hsl(var(--secondary))", foreground: "hsl(var(--secondary-foreground))" },
        muted: { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
        accent: { DEFAULT: "hsl(var(--accent))", foreground: "hsl(var(--accent-foreground))" },
        destructive: { DEFAULT: "hsl(var(--destructive))", foreground: "hsl(var(--destructive-foreground))" },
        card: { DEFAULT: "hsl(var(--card))", foreground: "hsl(var(--card-foreground))" },
        popover: { DEFAULT: "hsl(var(--popover))", foreground: "hsl(var(--popover-foreground))" },
      },
      borderRadius: { lg: "var(--radius)", md: "calc(var(--radius) - 2px)", sm: "calc(var(--radius) - 4px)" },
    },
  },
  plugins: [],
} satisfies Config;
EOF

write_file "postcss.config.js" <<'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
EOF

# --- shadcn/ui components.json (default new-york style) --------------------
write_file "components.json" <<'EOF'
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
EOF

# --- index.html -----------------------------------------------------------
write_file "index.html" <<EOF
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>$project_name</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

# --- src entry ------------------------------------------------------------
write_file "src/main.tsx" <<'EOF'
import React from "react";
import ReactDOM from "react-dom/client";
import App from "@/App";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import "@/index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
EOF

write_file "src/App.tsx" <<EOF
function App() {
  return (
    <main className="min-h-screen grid place-items-center bg-background text-foreground">
      <h1 className="text-2xl font-semibold">$project_name</h1>
    </main>
  );
}

export default App;
EOF

write_file "src/index.css" <<'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222 47% 11%;
    --card: 0 0% 100%;
    --card-foreground: 222 47% 11%;
    --popover: 0 0% 100%;
    --popover-foreground: 222 47% 11%;
    --primary: 222 47% 11%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96%;
    --secondary-foreground: 222 47% 11%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;
    --accent: 210 40% 96%;
    --accent-foreground: 222 47% 11%;
    --destructive: 0 72% 51%;
    --destructive-foreground: 0 0% 100%;
    --border: 214 32% 91%;
    --input: 214 32% 91%;
    --ring: 222 47% 11%;
    --radius: 0.5rem;
  }
  .dark {
    --background: 222 47% 11%;
    --foreground: 210 40% 98%;
    --card: 222 47% 11%;
    --card-foreground: 210 40% 98%;
    --popover: 222 47% 11%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222 47% 11%;
    --secondary: 217 33% 18%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217 33% 18%;
    --muted-foreground: 215 20% 65%;
    --accent: 217 33% 18%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 63% 31%;
    --destructive-foreground: 210 40% 98%;
    --border: 217 33% 18%;
    --input: 217 33% 18%;
    --ring: 212 27% 84%;
  }
  body { @apply bg-background text-foreground; }
}
EOF

# --- lib/utils.ts (shadcn cn helper) --------------------------------------
write_file "src/lib/utils.ts" <<'EOF'
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind class names, resolving conflicts. Used by shadcn/ui components. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
EOF

# --- ErrorBoundary --------------------------------------------------------
write_file "src/components/ErrorBoundary.tsx" <<'EOF'
import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

/** Graceful React error boundary. Wrap the app root so render errors show UI, not a blank page. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Log detailed context; wire this to your error reporter in production.
    console.error("ErrorBoundary caught an error:", error, info);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="min-h-screen grid place-items-center p-6 text-center">
            <div>
              <h1 className="text-xl font-semibold">Something went wrong.</h1>
              <p className="text-sm text-muted-foreground mt-2">
                Please refresh the page. If the problem persists, contact support.
              </p>
            </div>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
EOF

# --- types/ directory -----------------------------------------------------
write_file "src/types/index.ts" <<'EOF'
// Shared application types live here. Import from "@/types".
export {};
EOF

# --- vercel.json skeleton (SPA rewrite) -----------------------------------
write_file "vercel.json" <<'EOF'
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "rewrites": [{ "source": "/(.*)", "destination": "/" }]
}
EOF

# --- .gitignore -----------------------------------------------------------
write_file ".gitignore" <<'EOF'
node_modules
dist
dist-ssr
*.local

# env — actuals gitignored, .env.example committed
.env
.env.local
.env.*.local

# editor / os
.vscode/*
!.vscode/extensions.json
.DS_Store
EOF

# --- env files (Supabase-aware) -------------------------------------------
if [[ $want_supabase -eq 1 ]]; then
  write_file ".env.example" <<'EOF'
# Committed example. Copy to .env.local and fill real values (do not commit .env.local).
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_your-key
EOF

  write_file "src/lib/supabase.ts" <<'EOF'
import { createClient } from "@supabase/supabase-js";
import type { Database } from "@/types/supabase";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  // Fail fast so misconfiguration is obvious at startup, not at first query.
  throw new Error(
    "Missing Supabase env vars: set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY in .env.local"
  );
}

/** Typed Supabase client. Regenerate Database types with `supabase gen types typescript`. */
export const supabase = createClient<Database>(supabaseUrl, supabaseKey);
EOF

  write_file "src/types/supabase.ts" <<'EOF'
// Placeholder for generated Supabase types.
// Regenerate with:
//   supabase gen types typescript --project-id <ref> > src/types/supabase.ts
export type Database = Record<string, never>;
EOF

  write_file "src/vite-env.d.ts" <<'EOF'
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL: string;
  readonly VITE_SUPABASE_PUBLISHABLE_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
EOF
else
  write_file ".env.example" <<'EOF'
# Committed example. Copy to .env.local and fill real values (do not commit .env.local).
# Add VITE_-prefixed vars here as the app needs them.
EOF

  write_file "src/vite-env.d.ts" <<'EOF'
/// <reference types="vite/client" />
EOF
fi

# --- README stub ----------------------------------------------------------
write_file "README.md" <<EOF
# $project_name

Vite + React 18 + TypeScript (strict) + Tailwind + shadcn/ui.

## Getting started

\`\`\`bash
npm install
cp .env.example .env.local   # fill in real values
npm run dev
\`\`\`

## Scripts

- \`npm run dev\` — start dev server
- \`npm run build\` — type-check and build for production
- \`npm run preview\` — preview the production build
EOF

# --- manifest -------------------------------------------------------------
echo "=== scaffold-web summary ==="
echo "target: $target_dir"
echo "project name: $project_name"
echo "supabase: $([[ $want_supabase -eq 1 ]] && echo yes || echo no)"
echo

echo "=== manifest (created) ==="
if [[ ${#created[@]} -eq 0 ]]; then
  echo "(none)"
else
  printf '%s\n' "${created[@]}" | sort
fi
echo

echo "=== manifest (skipped, already existed) ==="
if [[ ${#skipped[@]} -eq 0 ]]; then
  echo "(none)"
else
  printf '%s\n' "${skipped[@]}" | sort
fi
echo

echo "=== next steps ==="
echo "1. cd $target_dir"
echo "2. npm install   # all runtime/dev dependencies are declared in package.json"
echo "3. npm run lint && npm run build"
echo "4. npm run dev"
echo "Optional: npx shadcn@latest add button   # preserves the configured React 18/Tailwind 3 stack"
echo "Commit only when requested, using Veer's identity and intended files."
