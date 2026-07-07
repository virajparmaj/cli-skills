#!/usr/bin/env node
// list-routes.mjs — discover React Router routes from source, deterministically.
//
// Usage:
//   node list-routes.mjs <repo-path>
//
// Reads the repo's source (App.tsx, router config, *.route(s).tsx) with regex —
// no bundler, no execution — and prints a JSON array of route objects to stdout:
//   [{ "path": "/dashboard", "kind": "public"|"auth"|"dynamic", "source": "src/App.tsx", "reason": "..." }]
//
// Read-only. Never writes to the target repo. stdlib / Node built-ins only.

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";

const repoPath = process.argv[2] || ".";

const SRC_DIRS = ["src", "app", "pages", "."];
const SKIP_DIRS = new Set([
  "node_modules", ".git", "dist", "build", "coverage",
  ".next", ".vercel", ".turbo", "out", "public",
]);
const CODE_EXT = new Set([".tsx", ".jsx", ".ts", ".js"]);

// Words in a path or wrapper that signal an authenticated / protected route.
const AUTH_HINTS = [
  "protected", "requireauth", "requireauth", "privateroute", "authguard",
  "authrequired", "requireuser", "requireadmin", "guard",
];
const AUTH_PATH_HINTS = ["login", "logout", "signin", "signup", "register", "auth"];

function fail(msg) {
  process.stderr.write(`list-routes: ${msg}\n`);
  process.exit(1);
}

function isCodeFile(name) {
  const dot = name.lastIndexOf(".");
  return dot !== -1 && CODE_EXT.has(name.slice(dot));
}

function walk(dir, acc) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return acc;
  }
  for (const entry of entries) {
    if (entry.name.startsWith(".") && entry.name !== ".") continue;
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (SKIP_DIRS.has(entry.name)) continue;
      walk(full, acc);
    } else if (entry.isFile() && isCodeFile(entry.name)) {
      acc.push(full);
    }
  }
  return acc;
}

function collectFiles() {
  const seen = new Set();
  const files = [];
  for (const d of SRC_DIRS) {
    const base = d === "." ? repoPath : join(repoPath, d);
    let ok = false;
    try {
      ok = statSync(base).isDirectory();
    } catch {
      ok = false;
    }
    if (!ok) continue;
    for (const f of walk(base, [])) {
      if (!seen.has(f)) {
        seen.add(f);
        files.push(f);
      }
    }
    if (d !== ".") break; // prefer the first real source root; "." is a fallback
  }
  return files;
}

// Normalize a raw path literal into a leading-slash absolute-style route.
function normalizePath(raw) {
  let p = raw.trim();
  if (p === "" || p === "*") return null;
  if (p === "index") return "/";
  if (!p.startsWith("/")) p = "/" + p;
  p = p.replace(/\/{2,}/g, "/");
  if (p.length > 1 && p.endsWith("/")) p = p.slice(0, -1);
  return p;
}

// Classify a route. `guardCtx` is the route's OWN element/component text only —
// scoped tightly so a guard on one route never bleeds onto its siblings.
function classify(path, guardCtx) {
  const lowerPath = path.toLowerCase();
  const lowerCtx = (guardCtx || "").toLowerCase();

  if (path.includes(":") || path.includes("*")) {
    return { kind: "dynamic", reason: "path contains a route param" };
  }
  for (const hint of AUTH_PATH_HINTS) {
    if (lowerPath.split("/").includes(hint)) {
      return { kind: "auth", reason: `path segment '${hint}' implies auth flow` };
    }
  }
  for (const hint of AUTH_HINTS) {
    if (lowerCtx.includes(hint)) {
      return { kind: "auth", reason: `wrapped by a guard-like element (${hint})` };
    }
  }
  return { kind: "public", reason: "no auth or param signals" };
}

// Given the index just past a matched `path` literal, return the text of the
// element/component that renders THIS route only:
//   JSX:  from the match to the end of the <Route ...> opening tag ('>' or '/>').
//   obj:  from the match to the end of this route object (balanced closing '}').
// Kept small so guard wrappers on other routes are never counted here.
function guardContextFrom(src, fromIndex, isJsx) {
  if (isJsx) {
    // scan to the first unquoted '>' that closes the opening <Route ...> tag
    const slice = src.slice(fromIndex, fromIndex + 600);
    let quote = null;
    for (let i = 0; i < slice.length; i++) {
      const c = slice[i];
      if (quote) {
        if (c === quote) quote = null;
        continue;
      }
      if (c === '"' || c === "'" || c === "`") quote = c;
      else if (c === ">") return slice.slice(0, i + 1);
    }
    return slice;
  }
  // object form: walk braces from the enclosing '{' to its matching '}'
  const start = src.lastIndexOf("{", fromIndex);
  const from = start === -1 ? fromIndex : start;
  const slice = src.slice(from, from + 800);
  let depth = 0;
  let quote = null;
  for (let i = 0; i < slice.length; i++) {
    const c = slice[i];
    if (quote) {
      if (c === quote) quote = null;
      continue;
    }
    if (c === '"' || c === "'" || c === "`") quote = c;
    else if (c === "{") depth++;
    else if (c === "}") {
      depth--;
      if (depth === 0) return slice.slice(0, i + 1);
    }
  }
  return slice;
}

// Extract path literals from JSX <Route path="..."> and object { path: "..." } forms.
function extractFromSource(src, relPath, routes) {
  // <Route ... path="x" ... /> or path='x' or path={"x"}
  const jsxRe = /<Route\b[^>]*?\bpath\s*=\s*(?:{\s*)?["'`]([^"'`]*)["'`]/g;
  // object-config: path: "x"  (createBrowserRouter / route arrays)
  const objRe = /\bpath\s*:\s*["'`]([^"'`]*)["'`]/g;

  const grab = (re, isJsx) => {
    let m;
    while ((m = re.exec(src)) !== null) {
      const norm = normalizePath(m[1]);
      if (norm === null) continue;
      const guardCtx = guardContextFrom(src, m.index + m[0].length, isJsx);
      const { kind, reason } = classify(norm, guardCtx);
      routes.push({ path: norm, kind, source: relPath, reason });
    }
  };

  grab(jsxRe, true);
  grab(objRe, false);
}

function dedupe(routes) {
  const byPath = new Map();
  const rank = { public: 3, dynamic: 2, auth: 1 }; // keep the most-informative classification
  for (const r of routes) {
    const existing = byPath.get(r.path);
    if (!existing || (rank[r.kind] || 0) < (rank[existing.kind] || 0)) {
      // prefer stronger auth/dynamic signal over public if any source flags it
      byPath.set(r.path, existing && (rank[r.kind] || 0) > (rank[existing.kind] || 0) ? existing : r);
    }
  }
  return [...byPath.values()].sort((a, b) => a.path.localeCompare(b.path));
}

function main() {
  try {
    statSync(repoPath);
  } catch {
    fail(`repo path not found: ${repoPath}`);
  }

  const files = collectFiles();
  const routes = [];
  for (const f of files) {
    let src;
    try {
      src = readFileSync(f, "utf8");
    } catch {
      continue;
    }
    if (!src.includes("path")) continue; // cheap prefilter
    const rel = relative(repoPath, f).split(sep).join("/");
    extractFromSource(src, rel, routes);
  }

  const result = dedupe(routes);
  process.stdout.write(JSON.stringify(result, null, 2) + "\n");
}

main();
