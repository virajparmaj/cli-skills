#!/usr/bin/env python3
"""
audit_web_vibe.py - Post-Vibe Website & Marketing Site Production Readiness Scanner.

Audits:
1. GEO (Generative Engine Optimization) & AI Search Discovery (ChatGPT, Perplexity, Claude)
2. Speedmaxxing & Core Web Vitals (Images, Fonts, Lazy Loading, Bundles, Debounce)
3. Web Pre-Launch Essentials (Meta/OG tags, Custom 404/500, Legal terms, Form protection)
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
    ".md",
    ".mdx",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Audit website code for vibe-coding gaps")
    parser.add_argument("--repo", default=".", help="Path to website repository")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    return parser.parse_args()


def walk_files(repo_path: Path):
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            p = Path(root) / f
            yield p


def check_robots_txt(repo_path: Path):
    robots_files = list(repo_path.glob("**/robots.txt"))
    robots_files = [p for p in robots_files if not any(part in IGNORE_DIRS for part in p.parts)]

    result = {
        "found": bool(robots_files),
        "path": str(robots_files[0].relative_to(repo_path)) if robots_files else None,
        "blocks_ai_bots": [],
        "allows_ai_bots": [],
        "has_sitemap": False,
        "issues": [],
    }

    if not robots_files:
        result["issues"].append("Missing robots.txt. Search bots and AI crawlers may not crawl cleanly.")
        return result

    content = robots_files[0].read_text(errors="ignore")
    ai_bots = ["GPTBot", "OAI-SearchBot", "ClaudeBot", "PerplexityBot", "Applebot-Extended"]

    current_agents = []
    lines = content.splitlines()
    for line in lines:
        line_clean = line.strip().lower()
        if line_clean.startswith("user-agent:"):
            agent = line.split(":", 1)[1].strip()
            current_agents = [agent]
        elif line_clean.startswith("disallow:"):
            rule = line.split(":", 1)[1].strip()
            for agent in current_agents:
                for target_bot in ai_bots:
                    if agent.lower() == target_bot.lower() and rule == "/":
                        result["blocks_ai_bots"].append(f"{target_bot} disallowed from root")
                    elif agent.lower() == target_bot.lower() and rule == "":
                        result["allows_ai_bots"].append(target_bot)
        elif line_clean.startswith("sitemap:"):
            result["has_sitemap"] = True

    if not result["has_sitemap"]:
        result["issues"].append("robots.txt does not specify a Sitemap directive.")

    return result


def check_structured_data_and_geo(repo_path: Path):
    results = {
        "has_json_ld": False,
        "json_ld_schemas": [],
        "h2_questions": [],
        "one_line_definitions": [],
        "comparison_routes": [],
        "last_updated_signals": [],
    }

    definition_pattern = re.compile(
        r'([A-Za-z0-9_-]+)\s+is\s+(?:an?|the)\s+([A-Za-z0-9_\s-]+?)\s+that\s+helps\s+([A-Za-z0-9_\s-]+)',
        re.IGNORECASE,
    )
    h2_pattern = re.compile(r'<h2[^>]*>(.*?\?)<\/h2>|##\s+(.*?\?)', re.IGNORECASE)

    for p in walk_files(repo_path):
        if p.suffix.lower() not in WEB_EXTENSIONS:
            continue
        rel = str(p.relative_to(repo_path))

        # Check comparison routes
        lower_name = p.name.lower()
        if any(term in lower_name for term in ["-vs-", "_vs_", "alternative", "comparison"]):
            results["comparison_routes"].append(rel)

        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        if 'application/ld+json' in content:
            results["has_json_ld"] = True
            for schema_match in re.findall(r'"@type"\s*:\s*"([A-Za-z0-9_]+)"', content):
                if schema_match not in results["json_ld_schemas"]:
                    results["json_ld_schemas"].append(schema_match)

        # Check H2 questions
        for m in h2_pattern.finditer(content):
            q_text = (m.group(1) or m.group(2)).strip()
            if len(q_text) < 120 and len(results["h2_questions"]) < 10:
                results["h2_questions"].append({"file": rel, "question": q_text})

        # Check one-line definition
        for m in definition_pattern.finditer(content):
            match_str = m.group(0).strip()
            if len(match_str) < 140 and len(results["one_line_definitions"]) < 5:
                results["one_line_definitions"].append({"file": rel, "definition": match_str})

        # Check last-updated / dateModified
        if "dateModified" in content or "lastUpdated" in content or "last-updated" in content:
            if len(results["last_updated_signals"]) < 5:
                results["last_updated_signals"].append(rel)

    return results


def check_speedmaxxing(repo_path: Path):
    results = {
        "images_without_lazy": [],
        "large_unoptimized_images": [],
        "render_blocking_fonts": [],
        "dynamic_import_usage": False,
        "debounced_inputs": False,
        "heavy_client_packages": [],
    }

    # Check image assets
    for p in walk_files(repo_path):
        suffix = p.suffix.lower()
        if suffix in [".png", ".jpg", ".jpeg"]:
            try:
                size_kb = p.stat().st_size / 1024
                if size_kb > 250:
                    results["large_unoptimized_images"].append(
                        {"file": str(p.relative_to(repo_path)), "size_kb": round(size_kb, 1)}
                    )
            except Exception:
                pass

        if suffix in WEB_EXTENSIONS:
            rel = str(p.relative_to(repo_path))
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue

            # Check <img> without loading="lazy"
            for m in re.finditer(r'<img\s+([^>]+)>', content, re.IGNORECASE):
                img_tag = m.group(1)
                if 'loading="lazy"' not in img_tag and "loading='lazy'" not in img_tag:
                    if len(results["images_without_lazy"]) < 10:
                        results["images_without_lazy"].append({"file": rel, "tag": f"<img {img_tag[:60]}...>"})

            # Check font imports
            if "fonts.googleapis.com" in content and "font-display=swap" not in content:
                results["render_blocking_fonts"].append(rel)

            if "React.lazy" in content or "dynamic(" in content or "import(" in content:
                results["dynamic_import_usage"] = True

            if "debounce(" in content or "useDebounce" in content or "throttle(" in content:
                results["debounced_inputs"] = True

    # Check package.json for heavy packages
    package_files = list(repo_path.glob("**/package.json"))
    package_files = [p for p in package_files if not any(part in IGNORE_DIRS for part in p.parts)]
    heavy_libs = ["moment", "lodash", "recharts", "three", "lottie-web"]

    for pf in package_files:
        try:
            data = json.loads(pf.read_text(errors="ignore"))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            for hl in heavy_libs:
                if hl in deps:
                    results["heavy_client_packages"].append({"package": hl, "version": deps[hl]})
        except Exception:
            pass

    return results


def check_prelaunch_essentials(repo_path: Path):
    results = {
        "has_og_tags": False,
        "has_twitter_card": False,
        "has_custom_404": False,
        "has_custom_500": False,
        "has_privacy_policy": False,
        "has_terms_of_service": False,
        "has_forms": False,
        "has_form_bot_defense": False,
    }

    # Check 404 / 500 files
    for p in walk_files(repo_path):
        name_lower = p.name.lower()
        if name_lower in ["404.html", "404.tsx", "404.jsx", "404.vue", "not-found.tsx", "not-found.jsx"]:
            results["has_custom_404"] = True
        if name_lower in ["500.html", "500.tsx", "500.jsx", "error.tsx", "error.jsx"]:
            results["has_custom_500"] = True
        if "privacy" in name_lower:
            results["has_privacy_policy"] = True
        if "terms" in name_lower or "tos" in name_lower:
            results["has_terms_of_service"] = True

        if p.suffix.lower() in WEB_EXTENSIONS:
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue

            if 'property="og:image"' in content or 'property="og:title"' in content or 'name="og:image"' in content:
                results["has_og_tags"] = True
            if 'name="twitter:card"' in content or 'property="twitter:card"' in content:
                results["has_twitter_card"] = True
            if "<form" in content.lower():
                results["has_forms"] = True
                if any(k in content.lower() for k in ["turnstile", "recaptcha", "hcaptcha", "honeypot", "csrf"]):
                    results["has_form_bot_defense"] = True

    return results


def main():
    args = parse_args()
    repo_path = Path(args.repo).resolve()

    if not repo_path.exists():
        print(f"Error: path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    robots_report = check_robots_txt(repo_path)
    geo_report = check_structured_data_and_geo(repo_path)
    speed_report = check_speedmaxxing(repo_path)
    prelaunch_report = check_prelaunch_essentials(repo_path)

    full_report = {
        "repo": str(repo_path),
        "robots_txt": robots_report,
        "geo_and_ai_search": geo_report,
        "speedmaxxing": speed_report,
        "prelaunch_essentials": prelaunch_report,
    }

    if args.json:
        print(json.dumps(full_report, indent=2))
        return

    print("=" * 70)
    print("V-VIBE-WEB: WEBSITE & LANDING PAGE AUDIT SUMMARY")
    print("=" * 70)

    print("\n1. GEO & AI Search Discovery (ChatGPT / Perplexity / Claude):")
    print(f"  - robots.txt found: {'YES' if robots_report['found'] else 'NO (Missing!)'}")
    if robots_report["blocks_ai_bots"]:
        print(f"  - [WARNING] Blocks AI crawlers: {', '.join(robots_report['blocks_ai_bots'])}")
    if robots_report["allows_ai_bots"]:
        print(f"  - AI crawlers explicitly allowed: {', '.join(robots_report['allows_ai_bots'])}")
    print(f"  - JSON-LD structured data: {'YES' if geo_report['has_json_ld'] else 'NO (Missing schema.org)'}")
    if geo_report["json_ld_schemas"]:
        print(f"    Schemas: {', '.join(geo_report['json_ld_schemas'])}")
    print(f"  - Exact question H2s detected: {len(geo_report['h2_questions'])}")
    print(f"  - One-line category definitions found: {len(geo_report['one_line_definitions'])}")
    print(f"  - Comparison/alternatives pages found: {len(geo_report['comparison_routes'])}")

    print("\n2. Speedmaxxing & Web Vitals:")
    print(f"  - Large unoptimized images (>250KB): {len(speed_report['large_unoptimized_images'])}")
    for img in speed_report["large_unoptimized_images"][:3]:
        print(f"    * {img['file']} ({img['size_kb']} KB)")
    print(f"  - Images without lazy loading: {len(speed_report['images_without_lazy'])}")
    print(f"  - Render blocking fonts: {len(speed_report['render_blocking_fonts'])}")
    print(f"  - Dynamic imports / code splitting: {'YES' if speed_report['dynamic_import_usage'] else 'NO (Monolithic bundle risk)'}")
    print(f"  - Input debouncing detected: {'YES' if speed_report['debounced_inputs'] else 'NO'}")
    if speed_report["heavy_client_packages"]:
        print("  - Heavy packages installed:")
        for pkg in speed_report["heavy_client_packages"]:
            print(f"    * {pkg['package']} ({pkg['version']})")

    print("\n3. Pre-Launch Web Essentials:")
    print(f"  - Open Graph tags: {'YES' if prelaunch_report['has_og_tags'] else 'NO'}")
    print(f"  - Twitter Cards: {'YES' if prelaunch_report['has_twitter_card'] else 'NO'}")
    print(f"  - Custom 404 page: {'YES' if prelaunch_report['has_custom_404'] else 'NO'}")
    print(f"  - Custom 500/Error page: {'YES' if prelaunch_report['has_custom_500'] else 'NO'}")
    print(f"  - Privacy Policy: {'YES' if prelaunch_report['has_privacy_policy'] else 'NO'}")
    print(f"  - Terms of Service: {'YES' if prelaunch_report['has_terms_of_service'] else 'NO'}")
    print(f"  - Form bot defense (Turnstile/honeypot): {'YES' if prelaunch_report['has_form_bot_defense'] else ('N/A' if not prelaunch_report['has_forms'] else 'NO (Vulnerable to spam bots)')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
