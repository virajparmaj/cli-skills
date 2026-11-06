#!/usr/bin/env python3
"""
audit_perf.py - Deterministic Web Application Performance & Core Web Vitals Scanner.

Audits web applications and marketing sites across the 20 Vibe Coder Performance checks:
- Core Web Vitals (LCP, INP, CLS) bottlenecks
- Image sizing, formats, layout shifts, lazy-loading & hero priority
- Bundle splitting, heavy dependencies & unused JavaScript
- Unnecessary CSR, component re-render hotspots & context thrashing
- Request waterfalls, unmemoized API queries & slow database patterns
- Caching headers, static asset delivery & third-party script impacts
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".astro",
    "out",
    ".vercel",
    ".turbo",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
    "references",
}

WEB_EXTENSIONS = {
    ".html",
    ".htm",
    ".jsx",
    ".tsx",
    ".js",
    ".ts",
    ".vue",
    ".svelte",
    ".astro",
}

HEAVY_LIBRARIES = {
    "moment": "Replace with date-fns (modular) or native Intl.DateTimeFormat",
    "lodash": "Replace with native Array/Object methods or lodash-es",
    "underscore": "Replace with native JavaScript ES6+ methods",
    "recharts": "Measure route bundle impact; consider dynamic import for costly chart routes",
    "chart.js": "Large chart library; ensure tree-shaking or dynamic import",
    "three": "Measure 3D engine delivery and main-thread cost; isolate only when useful",
    "pdf-lib": "PDF generation library; move to serverless background job or lazy-chunk",
    "pdfjs-dist": "Heavy PDF renderer; chunk dynamically",
    "lottie-web": "Replace with dotlottie-player or lightweight CSS/video animations",
    "framer-motion": "Motion library; use selective imports or CSS transitions for simple UI",
}

THIRD_PARTY_SCRIPTS = [
    ("Google Tag Manager", r"googletagmanager\.com|gtm\.js"),
    ("Google Analytics", r"google-analytics\.com|gtag/js"),
    ("Hotjar", r"static\.hotjar\.com|hjid"),
    ("Intercom", r"widget\.intercom\.io"),
    ("Facebook Pixel", r"connect\.facebook\.net|fbevents\.js"),
    ("TikTok Pixel", r"analytics\.tiktok\.com"),
    ("Segment", r"cdn\.segment\.com/analytics\.js"),
    ("FullStory", r"fullstory\.com/s/fs\.js"),
    ("Clarity", r"clarity\.ms/tag"),
]


def parse_args():
    parser = argparse.ArgumentParser(description="Deterministic Web Performance & CWV Scanner")
    parser.add_argument("--repo", default=".", help="Path to website/app repository")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    return parser.parse_args()


def walk_files(repo_path: Path):
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            yield Path(root) / f


def detect_stack(repo_path: Path):
    stack = {
        "framework": "Static / Vanilla",
        "has_ssr": False,
        "is_spa": False,
        "has_router": False,
    }

    package_files = [p for p in walk_files(repo_path) if p.name == "package.json"]
    package_files = [p for p in package_files if not any(part in IGNORE_DIRS for part in p.parts)]

    all_deps = set()
    for pf in package_files:
        try:
            data = json.loads(pf.read_text(errors="ignore"))
            all_deps.update(data.get("dependencies", {}).keys())
            all_deps.update(data.get("devDependencies", {}).keys())
        except Exception:
            pass

    if "next" in all_deps:
        stack["framework"] = "Next.js"
        stack["has_ssr"] = True
    elif "astro" in all_deps:
        stack["framework"] = "Astro"
        stack["has_ssr"] = True
    elif "@remix-run/react" in all_deps:
        stack["framework"] = "Remix"
        stack["has_ssr"] = True
    elif "vite" in all_deps or "react-scripts" in all_deps:
        stack["framework"] = "Vite / React SPA" if "react" in all_deps else "Vite"
        stack["is_spa"] = True
    elif "vue" in all_deps or "nuxt" in all_deps:
        stack["framework"] = "Nuxt" if "nuxt" in all_deps else "Vue"
        stack["has_ssr"] = "nuxt" in all_deps
    elif "svelte" in all_deps or "@sveltejs/kit" in all_deps:
        stack["framework"] = "SvelteKit" if "@sveltejs/kit" in all_deps else "Svelte"
        stack["has_ssr"] = "@sveltejs/kit" in all_deps

    if any(r in all_deps for r in ["react-router", "react-router-dom", "@tanstack/react-router"]):
        stack["has_router"] = True

    return stack


def check_images(repo_path: Path):
    large_images = []
    missing_dimensions = []
    missing_lazy = []
    hero_lazy_anti_patterns = []

    for p in walk_files(repo_path):
        suffix = p.suffix.lower()
        rel = str(p.relative_to(repo_path))

        # Check raw image asset file size
        if suffix in [".png", ".jpg", ".jpeg"]:
            try:
                size_kb = p.stat().st_size / 1024
                if size_kb > 200:
                    large_images.append({
                        "file": rel,
                        "size_kb": round(size_kb, 1),
                        "recommendation": "Convert to modern WebP/AVIF and resize to rendered dimensions",
                    })
            except Exception:
                pass

        # Check HTML/JSX image tags
        if suffix in WEB_EXTENSIONS:
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue

            # Look for <img> tags
            img_matches = list(re.finditer(r'<img\s+([^>]+)>', content, re.IGNORECASE))
            for m in img_matches:
                tag_attrs = m.group(1)

                # Check missing width / height (causes CLS)
                has_w = bool(re.search(r'\bwidth\s*=', tag_attrs, re.IGNORECASE))
                has_h = bool(re.search(r'\bheight\s*=', tag_attrs, re.IGNORECASE))
                if not (has_w and has_h):
                    if len(missing_dimensions) < 15:
                        missing_dimensions.append({
                            "file": rel,
                            "tag": f"<img {tag_attrs[:70]}...>",
                            "issue": "Missing explicit width and/or height attribute (triggers CLS)",
                        })

                # Check lazy loading
                is_lazy = 'loading="lazy"' in tag_attrs or "loading='lazy'" in tag_attrs
                is_hero = bool(re.search(r'(hero|banner|masthead|above-the-fold|primary-cover)', tag_attrs + rel, re.IGNORECASE))

                # Hero anti-pattern: lazy loading the main hero image delays LCP
                if is_hero and is_lazy:
                    hero_lazy_anti_patterns.append({
                        "file": rel,
                        "tag": f"<img {tag_attrs[:70]}...>",
                        "issue": "Main hero image is lazy-loaded (destroys LCP! Hero images should use fetchpriority='high')",
                    })
                elif not is_lazy and not is_hero:
                    if len(missing_lazy) < 15:
                        missing_lazy.append({
                            "file": rel,
                            "tag": f"<img {tag_attrs[:70]}...>",
                        })

    return {
        "large_images": large_images,
        "missing_dimensions": missing_dimensions,
        "missing_lazy": missing_lazy,
        "hero_lazy_anti_patterns": hero_lazy_anti_patterns,
    }


def check_fonts(repo_path: Path):
    blocking_fonts = []
    missing_preloads = []
    font_families = set()

    for p in walk_files(repo_path):
        suffix = p.suffix.lower()
        if suffix in WEB_EXTENSIONS or suffix in [".css", ".scss"]:
            rel = str(p.relative_to(repo_path))
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue

            # CSS @import url for fonts
            if re.search(r'@import\s+url\(["\']?https?://fonts\.googleapis\.com', content):
                blocking_fonts.append({
                    "file": rel,
                    "issue": "CSS @import for fonts blocks rendering; replace with <link rel='preconnect'> and <link rel='preload'>",
                })

            # fonts.googleapis without display=swap
            if "fonts.googleapis.com" in content and "font-display=swap" not in content and "display=swap" not in content:
                blocking_fonts.append({
                    "file": rel,
                    "issue": "Google Fonts loaded without &display=swap (causes FOIT / layout shift)",
                })

            # Check font-family names to detect font proliferation
            for match in re.finditer(r'font-family:\s*["\']?([^;"\',]+)', content):
                fam = match.group(1).strip()
                if fam and not fam.startswith("var(") and fam not in ["inherit", "sans-serif", "serif", "monospace"]:
                    font_families.add(fam)

    return {
        "blocking_fonts": blocking_fonts,
        "font_family_count": len(font_families),
        "font_families": sorted(list(font_families))[:5],
    }


def check_bundles_and_deps(repo_path: Path):
    heavy_detected = []
    has_dynamic_imports = False
    missing_manual_chunks = False

    package_files = [p for p in walk_files(repo_path) if p.name == "package.json"]
    package_files = [p for p in package_files if not any(part in IGNORE_DIRS for part in p.parts)]

    for pf in package_files:
        try:
            data = json.loads(pf.read_text(errors="ignore"))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            for hl, suggestion in HEAVY_LIBRARIES.items():
                if hl in deps:
                    heavy_detected.append({
                        "package": hl,
                        "version": deps[hl],
                        "recommendation": suggestion,
                    })
        except Exception:
            pass

    # Check for dynamic imports across code
    for p in walk_files(repo_path):
        if p.suffix.lower() in WEB_EXTENSIONS:
            try:
                content = p.read_text(errors="ignore")
                if "React.lazy" in content or "dynamic(" in content or "import(" in content:
                    has_dynamic_imports = True
                    break
            except Exception:
                continue

    # Check vite.config or next.config for chunking
    vite_configs = [p for p in walk_files(repo_path) if p.name.startswith("vite.config.")]
    for vc in vite_configs:
        try:
            content = vc.read_text(errors="ignore")
            if "manualChunks" not in content:
                missing_manual_chunks = True
        except Exception:
            pass

    return {
        "heavy_detected": heavy_detected,
        "has_dynamic_imports": has_dynamic_imports,
        "missing_manual_chunks": missing_manual_chunks,
    }


def check_render_and_react(repo_path: Path):
    unmemoized_contexts = []
    heavy_render_loops = []

    for p in walk_files(repo_path):
        if p.suffix.lower() in [".jsx", ".tsx"]:
            rel = str(p.relative_to(repo_path))
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue

            # Check context provider value={{ inlineObject }}
            for m in re.finditer(r'<(\w+Context\.Provider|\w+Provider)\s+[^>]*value=\{\{\s*([^}]+)\s*\}\}', content):
                prov_name = m.group(1)
                unmemoized_contexts.append({
                    "file": rel,
                    "provider": prov_name,
                    "issue": "Context Provider passes unmemoized object literal in value={{ ... }}; triggers cascading full-tree re-renders",
                })

            # Check for expensive inline operations in JSX render loop
            lines = content.splitlines()
            for idx, line in enumerate(lines, 1):
                if ".map(" in line and ("sort(" in line or "filter(" in line) and "useMemo" not in content:
                    if len(heavy_render_loops) < 10:
                        heavy_render_loops.append({
                            "file": rel,
                            "line": idx,
                            "code": line.strip()[:80],
                            "issue": "Unmemoized array filtering/sorting inside render path",
                        })

    return {
        "unmemoized_contexts": unmemoized_contexts,
        "heavy_render_loops": heavy_render_loops,
    }


def check_network_and_waterfalls(repo_path: Path):
    potential_waterfalls = []
    unbounded_queries = []

    for p in walk_files(repo_path):
        if p.suffix.lower() in WEB_EXTENSIONS:
            rel = str(p.relative_to(repo_path))
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue

            # Sequential awaits in useEffect
            if "useEffect(" in content:
                for block in re.finditer(r'useEffect\s*\(\s*(?:async\s*)?\(\s*\)\s*=>\s*\{([^}]+)\}', content, re.DOTALL):
                    body = block.group(1)
                    awaits = re.findall(r'await\s+[\w.]+\(', body)
                    if len(awaits) > 1 and "Promise.all" not in body:
                        potential_waterfalls.append({
                            "file": rel,
                            "awaits_count": len(awaits),
                            "issue": "Sequential async awaits inside useEffect create request waterfall; combine with Promise.all",
                        })

            # Supabase / DB unbounded queries
            if re.search(r'\.from\([^)]+\)\.select\([\'"]\*[\'"]\)', content) and ".limit(" not in content:
                if len(unbounded_queries) < 10:
                    unbounded_queries.append({
                        "file": rel,
                        "issue": "Unbounded query: select('*') without .limit(); scans and transfers unnecessary rows",
                    })

    return {
        "potential_waterfalls": potential_waterfalls,
        "unbounded_queries": unbounded_queries,
    }


def check_caching_and_delivery(repo_path: Path):
    has_vercel_config = (repo_path / "vercel.json").exists()
    has_cache_headers = False

    for config_name in ["vercel.json", "next.config.js", "next.config.mjs", "next.config.ts"]:
        for cfg in (p for p in walk_files(repo_path) if p.name == config_name):
            try:
                txt = cfg.read_text(errors="ignore")
                if "Cache-Control" in txt or "s-maxage" in txt or "stale-while-revalidate" in txt:
                    has_cache_headers = True
                    break
            except Exception:
                pass

    return {
        "has_vercel_config": has_vercel_config,
        "has_cache_headers": has_cache_headers,
    }


def check_third_party_scripts(repo_path: Path):
    detected_scripts = []

    for p in walk_files(repo_path):
        if p.suffix.lower() in WEB_EXTENSIONS:
            rel = str(p.relative_to(repo_path))
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue

            for name, pattern in THIRD_PARTY_SCRIPTS:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if script tag has async or defer
                    has_async = "async" in content
                    has_defer = "defer" in content
                    detected_scripts.append({
                        "service": name,
                        "file": rel,
                        "has_async_or_defer": has_async or has_defer,
                        "recommendation": "Load asynchronously, defer, or initialize inside requestIdleCallback to protect INP",
                    })

    # Deduplicate by service
    deduped = {}
    for item in detected_scripts:
        if item["service"] not in deduped:
            deduped[item["service"]] = item

    return list(deduped.values())


def run_full_audit(repo_path: Path):
    stack = detect_stack(repo_path)
    images = check_images(repo_path)
    fonts = check_fonts(repo_path)
    bundles = check_bundles_and_deps(repo_path)
    react_checks = check_render_and_react(repo_path)
    network = check_network_and_waterfalls(repo_path)
    caching = check_caching_and_delivery(repo_path)
    third_party = check_third_party_scripts(repo_path)

    # Calculate overall Core Web Vitals risk profile
    cwv_risks = {
        "LCP": [],  # Target <= 2.5s
        "INP": [],  # Target < 200ms
        "CLS": [],  # Target < 0.1
    }

    if images["hero_lazy_anti_patterns"]:
        cwv_risks["LCP"].append("Main hero image is lazy-loaded (anti-pattern delaying LCP)")
    if images["large_images"]:
        cwv_risks["LCP"].append(f"{len(images['large_images'])} large source images > 200KB; verify usage and critical-path impact")
    if fonts["blocking_fonts"]:
        cwv_risks["LCP"].append("Render-blocking font stylesheets / missing font-display: swap")
    if bundles["heavy_detected"]:
        cwv_risks["LCP"].append(f"Potentially costly dependencies declared; measure loaded route bundles ({len(bundles['heavy_detected'])} packages)")

    if bundles["heavy_detected"]:
        cwv_risks["INP"].append("Declared libraries may contribute to JS cost; measure route execution and hydration")
    if react_checks["unmemoized_contexts"]:
        cwv_risks["INP"].append("Inline Context provider values found; profile consumers and actual input latency")
    if third_party:
        cwv_risks["INP"].append(f"{len(third_party)} third-party tracking scripts competing for main thread execution")

    if images["missing_dimensions"]:
        cwv_risks["CLS"].append(f"{len(images['missing_dimensions'])} images missing explicit width/height dimensions")
    if fonts["blocking_fonts"]:
        cwv_risks["CLS"].append("Web fonts without font-display: swap causing layout shift on load")

    return {
        "evidence_scope": "Static source risks; Core Web Vitals have not been measured",
        "stack": stack,
        "cwv_targets": {
            "LCP": "2.5 seconds or less",
            "INP": "under 200 milliseconds",
            "CLS": "under 0.1",
        },
        "cwv_risks": cwv_risks,
        "images": images,
        "fonts": fonts,
        "bundles": bundles,
        "react_checks": react_checks,
        "network": network,
        "caching": caching,
        "third_party": third_party,
    }


def main():
    args = parse_args()
    repo_path = Path(args.repo).resolve()

    if not repo_path.is_dir():
        print(f"Error: path '{repo_path}' is not a repository directory.", file=sys.stderr)
        sys.exit(1)

    audit_data = run_full_audit(repo_path)

    if args.json:
        print(json.dumps(audit_data, indent=2))
        return

    # Formatted terminal output
    print("\n" + "=" * 70)
    print("  VIBE CODER PERFORMANCE & CORE WEB VITALS AUDIT")
    print("  'A fast website is not just about a green score. People feel it.'")
    print("=" * 70)
    print(f"\n[Stack Detected] {audit_data['stack']['framework']} (SSR: {audit_data['stack']['has_ssr']})")

    # Core Web Vitals Summary
    print("\n[Core Web Vitals Risk Summary]")
    for metric, target in audit_data["cwv_targets"].items():
        risks = audit_data["cwv_risks"][metric]
        status = "SOURCE RISKS TO VERIFY" if risks else "UNVERIFIED (no configured risk patterns found)"
        print(f"  - {metric} (Target: {target}): [{status}]")
        for r in risks:
            print(f"      * {r}")

    # Top Bottlenecks
    print("\n[Actionable Bottlenecks Detected]")

    # 1. Images
    img_data = audit_data["images"]
    if img_data["hero_lazy_anti_patterns"]:
        print(f"  [!] HERO LAZY-LOAD ANTI-PATTERN ({len(img_data['hero_lazy_anti_patterns'])} instances):")
        for h in img_data["hero_lazy_anti_patterns"][:3]:
            print(f"      - {h['file']}: {h['issue']}")

    if img_data["large_images"]:
        print(f"  [!] Large unoptimized images (>200KB): {len(img_data['large_images'])}")
        for img in img_data["large_images"][:3]:
            print(f"      - {img['file']} ({img['size_kb']} KB)")

    if img_data["missing_dimensions"]:
        print(f"  [!] Images missing width/height (CLS hazard): {len(img_data['missing_dimensions'])} tags")

    # 2. Bundles & Code Splitting
    b_data = audit_data["bundles"]
    if b_data["heavy_detected"]:
        print(f"  [!] Heavy client libraries: {len(b_data['heavy_detected'])}")
        for lib in b_data["heavy_detected"]:
            print(f"      - {lib['package']} ({lib['version']}): {lib['recommendation']}")

    if not b_data["has_dynamic_imports"]:
        print("  [!] Dynamic imports: NONE DETECTED (Monolithic bundle risk; add React.lazy / dynamic())")

    # 3. Fonts
    f_data = audit_data["fonts"]
    if f_data["blocking_fonts"]:
        print(f"  [!] Render-blocking fonts: {len(f_data['blocking_fonts'])}")
        for bf in f_data["blocking_fonts"][:2]:
            print(f"      - {bf['file']}: {bf['issue']}")

    # 4. React & Rerender
    r_data = audit_data["react_checks"]
    if r_data["unmemoized_contexts"]:
        print(f"  [!] Unmemoized Context Providers: {len(r_data['unmemoized_contexts'])}")
        for uc in r_data["unmemoized_contexts"][:2]:
            print(f"      - {uc['file']}: {uc['issue']}")

    if r_data["heavy_render_loops"]:
        print(f"  [!] Unmemoized array operations in render path: {len(r_data['heavy_render_loops'])}")

    # 5. Network & Waterfalls
    n_data = audit_data["network"]
    if n_data["potential_waterfalls"]:
        print(f"  [!] Request Waterfalls: {len(n_data['potential_waterfalls'])}")
        for pw in n_data["potential_waterfalls"][:2]:
            print(f"      - {pw['file']}: {pw['issue']}")

    # 6. Third Party Scripts
    tp_data = audit_data["third_party"]
    if tp_data:
        print(f"  [!] Third-party tracking scripts: {len(tp_data)}")
        for tp in tp_data:
            print(f"      - {tp['service']} ({tp['file']})")

    # 7. Caching
    c_data = audit_data["caching"]
    if not c_data["has_cache_headers"]:
        print("  [!] Caching headers: Missing explicit Cache-Control or stale-while-revalidate headers")

    print("\n" + "=" * 70)
    print("  GOLDEN RULE: Fix the biggest real bottlenecks first.")
    print("  Don't optimize random code just to make a report look better.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
