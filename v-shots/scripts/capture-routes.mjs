#!/usr/bin/env node
// capture-routes.mjs — screenshot each public route of a running app with Playwright.
//
// Usage:
//   node capture-routes.mjs <repo-path> --base-url http://localhost:5173 --routes routes.json [--mobile] [--out docs/screenshots]
//
//   <repo-path>   target repo (screenshots are written under it)
//   --base-url    origin of the ALREADY-RUNNING dev server (required)
//   --routes      path to a JSON file OR '-' to read the route list from stdin
//                 (the array printed by list-routes.mjs)
//   --mobile      also capture a 375x812 variant per route (default: desktop only)
//   --out         output dir relative to repo (default: docs/screenshots)
//
// Captures ONLY routes whose kind is "public". Auth/dynamic-without-sample routes
// are printed as SKIPPED lines and never fabricated. Full-page PNG, network-idle wait.
//
// This is a generator: it WRITES PNGs into the target repo's docs/screenshots.
// Requires Playwright: `npm i -D playwright && npx playwright install chromium`.

import { readFileSync, mkdirSync, statSync } from "node:fs";
import { join } from "node:path";

const DESKTOP = { width: 1280, height: 800, tag: "1280x800" };
const MOBILE = { width: 375, height: 812, tag: "375x812" };

function fail(msg, code = 1) {
  process.stderr.write(`capture-routes: ${msg}\n`);
  process.exit(code);
}

function parseArgs(argv) {
  const args = { repo: null, baseUrl: null, routes: null, mobile: false, out: "docs/screenshots" };
  const rest = argv.slice(2);
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a === "--mobile") args.mobile = true;
    else if (a === "--base-url") args.baseUrl = rest[++i];
    else if (a === "--routes") args.routes = rest[++i];
    else if (a === "--out") args.out = rest[++i];
    else if (!a.startsWith("--") && args.repo === null) args.repo = a;
    else fail(`unknown or misplaced argument: ${a}`);
  }
  if (!args.repo) fail("missing <repo-path>");
  if (!args.baseUrl) fail("missing --base-url (start the dev server first)");
  if (!args.routes) fail("missing --routes <file|->");
  return args;
}

function readRoutes(routesArg) {
  let raw;
  if (routesArg === "-") {
    raw = readFileSync(0, "utf8"); // stdin
  } else {
    raw = readFileSync(routesArg, "utf8");
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (e) {
    fail(`--routes is not valid JSON: ${e.message}`);
  }
  if (!Array.isArray(parsed)) fail("--routes JSON must be an array");
  return parsed;
}

// Mirror the slug rules documented in SKILL.md.
function slugFor(path, taken) {
  let slug;
  if (path === "/") slug = "home";
  else slug = path.replace(/^\//, "").replace(/[/:]/g, "-").toLowerCase();
  slug = slug.replace(/[^a-z0-9-]/g, "-").replace(/-{2,}/g, "-").replace(/^-|-$/g, "");
  if (!slug) slug = "home";
  let candidate = slug;
  let n = 2;
  while (taken.has(candidate)) {
    candidate = `${slug}-${n++}`;
  }
  taken.add(candidate);
  return candidate;
}

function humanSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function loadPlaywright() {
  try {
    const mod = await import("playwright");
    return mod.chromium;
  } catch {
    fail(
      "playwright not installed. Run: npm i -D playwright && npx playwright install chromium",
      2,
    );
  }
}

async function captureOne(context, baseUrl, route, viewport, outDir, slug) {
  const page = await context.newPage();
  await page.setViewportSize({ width: viewport.width, height: viewport.height });
  const url = new URL(route.path, baseUrl).toString();
  const suffix = viewport === MOBILE ? "-mobile" : "";
  const file = join(outDir, `${slug}${suffix}.png`);
  try {
    await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    // settle animations / lazy content
    await page.waitForTimeout(600);
    await page.screenshot({ path: file, fullPage: true });
  } finally {
    await page.close();
  }
  const size = humanSize(statSync(file).size);
  return { file, size };
}

async function main() {
  const args = parseArgs(process.argv);

  try {
    if (!statSync(args.repo).isDirectory()) fail(`not a directory: ${args.repo}`);
  } catch {
    fail(`repo path not found: ${args.repo}`);
  }

  const routes = readRoutes(args.routes);
  const outDir = join(args.repo, args.out);
  mkdirSync(outDir, { recursive: true });

  const chromium = await loadPlaywright();
  const browser = await chromium.launch();
  const context = await browser.newContext({ deviceScaleFactor: 2 });

  const taken = new Set();
  const viewports = args.mobile ? [DESKTOP, MOBILE] : [DESKTOP];

  process.stdout.write(`=== capturing ${routes.length} routes from ${args.baseUrl} ===\n`);
  let captured = 0;
  let skipped = 0;

  for (const route of routes) {
    if (route.kind !== "public") {
      const why =
        route.kind === "auth"
          ? "requires login"
          : route.kind === "dynamic" && !route.samplePath
            ? "needs a real param"
            : route.reason || route.kind;
      process.stdout.write(`SKIPPED ${route.path} (${why})\n`);
      skipped++;
      continue;
    }
    const target = route.samplePath ? { ...route, path: route.samplePath } : route;
    const slug = slugFor(route.path, taken);
    try {
      const done = [];
      for (const vp of viewports) {
        const { file, size } = await captureOne(context, args.baseUrl, target, vp, outDir, slug);
        done.push(`${file} (${size}, ${vp.tag})`);
      }
      process.stdout.write(`CAPTURED ${route.path} -> ${done.join(" | ")}\n`);
      captured++;
    } catch (e) {
      process.stdout.write(`SKIPPED ${route.path} (dev server never served this path: ${e.message})\n`);
      skipped++;
    }
  }

  await context.close();
  await browser.close();
  process.stdout.write(`=== done: ${captured} captured, ${skipped} skipped ===\n`);
}

main().catch((e) => fail(e && e.stack ? e.stack : String(e)));
