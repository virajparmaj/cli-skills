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
            if f.endswith("SKILL.md") or f.endswith("GEMINI.md"):
                continue
            p = Path(root) / f
            yield p


def root_crawl_allowed(content: str, user_agent: str = "Googlebot") -> bool:
    """Evaluate only the root path, using specific groups and Allow tie precedence.

    Scope: static robots.txt root rules, not fetched HTTP or every route.
    Reference: https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec
    """
    groups = []
    agents, rules = [], []
    for raw_line in content.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if rules:
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value.lower())
        elif key in {"allow", "disallow"} and agents:
            rules.append((key, value))
    if agents:
        groups.append((agents, rules))
    specific = [(max((len(a) for a in agents if a != "*" and a in user_agent.lower()), default=0), rules)
                for agents, rules in groups]
    longest = max((length for length, _ in specific), default=0)
    selected = [rules for length, rules in specific if length == longest] if longest else [rules for agents, rules in groups if "*" in agents]
    matches = []
    for rules in selected:
        for key, rule in rules:
            if not rule:
                continue
            anchored = rule.endswith("$")
            value = rule[:-1] if anchored else rule
            pattern = "^" + re.escape(value).replace(r"\*", ".*") + ("$" if anchored else "")
            if re.search(pattern, "/"):
                specificity = len(value.replace("*", ""))
                matches.append((specificity, key == "allow"))
    return max(matches, default=(0, True))[1]


def check_robots_txt(repo_path: Path):
    robots_files = [p for p in walk_files(repo_path) if p.name == "robots.txt"]
    robots_files = [p for p in robots_files if not any(part in IGNORE_DIRS for part in p.parts)]

    result = {
        "found": bool(robots_files),
        "path": str(robots_files[0].relative_to(repo_path)) if robots_files else None,
        "blocks_ai_bots": [],
        "allows_ai_bots": [],
        "googlebot_blocked": None,
        "has_sitemap": False,
        "issues": [],
    }

    if not robots_files:
        result["issues"].append("No static robots.txt found; verify generated or hosted crawl policy separately. Missing robots.txt alone does not block crawling.")
        return result

    try:
        content = robots_files[0].read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        result["issues"].append(f"Unable to read robots.txt: {exc}")
        result["googlebot_blocked"] = None
        return result
    ai_bots = ["Googlebot", "GPTBot", "OAI-SearchBot", "ClaudeBot", "PerplexityBot", "Applebot-Extended"]
    result["googlebot_blocked"] = not root_crawl_allowed(content, "Googlebot")
    for bot in ai_bots:
        if root_crawl_allowed(content, bot):
            result["allows_ai_bots"].append(bot)
        else:
            result["blocks_ai_bots"].append(f"{bot} disallowed from root")
    result["has_sitemap"] = any(line.split("#", 1)[0].strip().lower().startswith("sitemap:") for line in content.splitlines())

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
            if "fonts.googleapis.com" in content and "display=swap" not in content:
                results["render_blocking_fonts"].append(rel)

            if "React.lazy" in content or "dynamic(" in content or "import(" in content:
                results["dynamic_import_usage"] = True

            if "debounce(" in content or "useDebounce" in content or "throttle(" in content:
                results["debounced_inputs"] = True

    # Check package.json for heavy packages
    package_files = [p for p in walk_files(repo_path) if p.name == "package.json"]
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
                if any(k in content.lower() for k in ["turnstile", "recaptcha", "hcaptcha", "honeypot"]):
                    results["has_form_bot_defense"] = True

    return results


def check_design_and_codebase_slop(repo_path: Path):
    results = {
        "design_slop": {
            "badge_count": 0,
            "italic_buzzwords": [],
            "instrument_serif_negative_kerning": [],
            "divider_count": 0,
            "opacity_layering_count": 0,
            "bordered_container_count": 0,
            "superfluous_diagrams": [],
            "code_breadcrumbs": [],
            "section_numbering": [],
        },
        "codebase_slop": {
            "layer_first_layout": False,
            "feature_first_layout": False,
            "god_files": [],
            "representable_illegal_states": [],
            "layering_violations": [],
        },
    }

    src_dir = repo_path / "src"
    if src_dir.exists():
        layer_dirs = {"components", "services", "controllers", "models", "hooks", "utils", "views", "pages"}
        found = [d.name for d in src_dir.iterdir() if d.is_dir() and d.name in layer_dirs]
        has_features = (src_dir / "features").is_dir() or (src_dir / "modules").is_dir()
        results["codebase_slop"]["layer_first_layout"] = len(found) >= 3 and not has_features
        results["codebase_slop"]["feature_first_layout"] = has_features

    badge_pat = re.compile(r'<Badge\b')
    italic_pat = re.compile(r'(?:\*(?:effortlessly|seamlessly|intelligently|instantly|automatically)\*|\bitalic\b)', re.IGNORECASE)
    serif_kerning_pat = re.compile(r'(?:font-serif|Instrument Serif).*?(?:tracking-tighter|tracking-\[-0\.05em\])', re.IGNORECASE)
    divider_pat = re.compile(r'(?:<Separator\b|<hr\b|divide-y|border-t\b)')
    opacity_pat = re.compile(r'(?:bg-opacity-|text-white/\d+|text-muted-foreground/\d+|bg-neutral-\d+/\d+)')
    border_container_pat = re.compile(r'border\s+border-border\s+rounded-')
    diagram_pat = re.compile(r'(?:```mermaid|<svg[^>]*class="[^"]*(?:diagram|flowchart)[^"]*")', re.IGNORECASE)
    breadcrumb_pat = re.compile(r'(?:Dashboard\s*>\s*[A-Za-z]+|[A-Za-z]+\s*>\s*[A-Za-z]+\s*>\s*[A-Za-z]+)')
    section_num_pat = re.compile(r'(?:0[1-9]\s*\/|0[1-9]\s*-\s*|Step\s*0?[1-9][:\s-])', re.IGNORECASE)
    illegal_state_pat = re.compile(r'(?:isLoading|loading)\s*:\s*boolean.*?(?:isError|error).*?(?:data|user)', re.DOTALL)
    layering_violation_pat = re.compile(r'(?:supabase\.from\(|prisma\.[a-zA-Z0-9_]+\.(?:find|create|update)|SELECT\s+.+?\s+FROM)', re.IGNORECASE)

    for p in walk_files(repo_path):
        if p.suffix.lower() not in WEB_EXTENSIONS:
            continue
        rel = str(p.relative_to(repo_path))

        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        lines = content.splitlines()
        if len(lines) > 300 and len(results["codebase_slop"]["god_files"]) < 5:
            results["codebase_slop"]["god_files"].append({"file": rel, "lines": len(lines)})

        if illegal_state_pat.search(content) and len(results["codebase_slop"]["representable_illegal_states"]) < 3:
            results["codebase_slop"]["representable_illegal_states"].append(rel)

        is_ui = any(part in ["components", "views", "pages", "app"] for part in p.parts) or p.suffix.lower() in [".tsx", ".jsx", ".astro", ".html"]
        if is_ui:
            if layering_violation_pat.search(content) and len(results["codebase_slop"]["layering_violations"]) < 3:
                results["codebase_slop"]["layering_violations"].append(rel)

            results["design_slop"]["badge_count"] += len(badge_pat.findall(content))
            results["design_slop"]["divider_count"] += len(divider_pat.findall(content))
            results["design_slop"]["opacity_layering_count"] += len(opacity_pat.findall(content))
            results["design_slop"]["bordered_container_count"] += len(border_container_pat.findall(content))

            for m in italic_pat.finditer(content):
                if len(results["design_slop"]["italic_buzzwords"]) < 3:
                    results["design_slop"]["italic_buzzwords"].append({"file": rel, "text": m.group(0)})

            for m in serif_kerning_pat.finditer(content):
                if len(results["design_slop"]["instrument_serif_negative_kerning"]) < 3:
                    results["design_slop"]["instrument_serif_negative_kerning"].append({"file": rel, "text": m.group(0)})

            for m in diagram_pat.finditer(content):
                if len(results["design_slop"]["superfluous_diagrams"]) < 3:
                    results["design_slop"]["superfluous_diagrams"].append(rel)

            for m in breadcrumb_pat.finditer(content):
                if len(results["design_slop"]["code_breadcrumbs"]) < 3:
                    results["design_slop"]["code_breadcrumbs"].append({"file": rel, "text": m.group(0)})

            for m in section_num_pat.finditer(content):
                if len(results["design_slop"]["section_numbering"]) < 5:
                    results["design_slop"]["section_numbering"].append({"file": rel, "text": m.group(0)})

    return results


def check_google_technical_seo(repo_path: Path):
    results = {
        "rendering_architecture": "Unknown from source inventory; inspect rendered output",
        "sitemap_files": [],
        "noindex_tags": [],
        "canonical_tags": [],
        "h1_issues": {
            "missing_h1": [],
            "multiple_h1": [],
        },
        "images_missing_alt": [],
        "schema_types": [],
        "has_breadcrumbs": False,
        "eeat_signals": {
            "has_author_byline": False,
            "has_author_bio_page": False,
            "has_person_schema": False,
        },
        "ai_slop_phrases": [],
    }

    # 1. Framework detection in package.json
    package_files = [p for p in walk_files(repo_path) if p.name == "package.json"]
    package_files = [p for p in package_files if not any(part in IGNORE_DIRS for part in p.parts)]
    for pf in package_files:
        try:
            data = json.loads(pf.read_text(errors="ignore"))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "next" in deps:
                results["rendering_architecture"] = "Next.js (SSR / SSG Supported)"
            elif "astro" in deps or "@astrojs/core" in deps:
                results["rendering_architecture"] = "Astro (Zero-JS SSG Default)"
            elif "@remix-run/react" in deps:
                results["rendering_architecture"] = "Remix (SSR Supported)"
            elif "nuxt" in deps:
                results["rendering_architecture"] = "Nuxt (SSR Supported)"
            elif "@sveltejs/kit" in deps:
                results["rendering_architecture"] = "SvelteKit (SSR Supported)"
            elif "gatsby" in deps:
                results["rendering_architecture"] = "Gatsby (SSG Supported)"
        except Exception:
            pass

    # 2. Sitemap files & Author pages
    for p in walk_files(repo_path):
        name_lower = p.name.lower()
        if name_lower in ["sitemap.xml", "sitemap.ts", "sitemap.js"] or "sitemap-index" in name_lower:
            results["sitemap_files"].append(str(p.relative_to(repo_path)))
        if "author" in name_lower and any(term in name_lower for term in [".html", ".tsx", ".jsx", ".md", ".mdx"]):
            results["eeat_signals"]["has_author_bio_page"] = True

    # Regex patterns
    noindex_pat = re.compile(r'(?:<meta[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex|X-Robots-Tag:\s*noindex)', re.IGNORECASE)
    canonical_pat = re.compile(r'(?:<link[^>]*rel=["\']canonical["\']|canonical:\s*["\']https?:\/\/|metadata\.alternates\.canonical)', re.IGNORECASE)
    h1_pat = re.compile(r'<h1\b|^#(?!#)\s+', re.IGNORECASE | re.MULTILINE)
    alt_pat = re.compile(r'<img\s+([^>]+)>', re.IGNORECASE)
    breadcrumb_pat = re.compile(r'(?:<nav[^>]*aria-label=["\']breadcrumb|BreadcrumbList|from ["\'].*?breadcrumb)', re.IGNORECASE)
    author_pat = re.compile(r'(?:rel=["\']author["\']|class=["\'][^"\']*author-bio|@type["\']\s*:\s*["\']Person["\']|author:\s*["\'][^"\']+["\'])', re.IGNORECASE)

    ai_slop_patterns = [
        re.compile(r'\bin today[\'’]s fast-paced\b', re.IGNORECASE),
        re.compile(r'\bdelve into\b', re.IGNORECASE),
        re.compile(r'\ba testament to\b', re.IGNORECASE),
        re.compile(r'\bmultifaceted tapestry\b', re.IGNORECASE),
        re.compile(r'\bit is crucial to remember\b', re.IGNORECASE),
        re.compile(r'\bseamlessly integrates\b', re.IGNORECASE),
        re.compile(r'\brevolutionize the way\b', re.IGNORECASE),
    ]

    for p in walk_files(repo_path):
        if p.suffix.lower() not in WEB_EXTENSIONS:
            continue
        rel = str(p.relative_to(repo_path))
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            continue

        # Noindex check
        if noindex_pat.search(content):
            results["noindex_tags"].append(rel)

        # Canonical check
        if canonical_pat.search(content):
            results["canonical_tags"].append(rel)

        # Breadcrumbs
        if breadcrumb_pat.search(content):
            results["has_breadcrumbs"] = True

        # E-E-A-T signals
        if author_pat.search(content):
            results["eeat_signals"]["has_author_byline"] = True
            if '"@type": "Person"' in content or "'@type': 'Person'" in content:
                results["eeat_signals"]["has_person_schema"] = True

        # H1 count in route / page files
        is_page = any(part in ["pages", "app", "routes", "views"] for part in p.parts)
        if is_page and p.suffix.lower() in [".tsx", ".jsx", ".html", ".astro", ".md", ".mdx"]:
            h1_count = len(h1_pat.findall(content))
            if h1_count == 0 and len(results["h1_issues"]["missing_h1"]) < 5:
                results["h1_issues"]["missing_h1"].append(rel)
            elif h1_count > 1 and len(results["h1_issues"]["multiple_h1"]) < 5:
                results["h1_issues"]["multiple_h1"].append({"file": rel, "count": h1_count})

        # Missing alt attributes
        for m in alt_pat.finditer(content):
            tag_content = m.group(1)
            if not re.search(r"\balt\s*=", tag_content, re.IGNORECASE):
                if len(results["images_missing_alt"]) < 8:
                    results["images_missing_alt"].append({"file": rel, "tag": f"<img {tag_content[:50]}...>"})

        # Schema types
        for schema_match in re.findall(r'"@type"\s*:\s*"([A-Za-z0-9_]+)"', content):
            if schema_match in ["FAQPage", "Article", "BlogPosting", "BreadcrumbList", "TechArticle"]:
                if schema_match not in results["schema_types"]:
                    results["schema_types"].append(schema_match)

        # AI slop phrases
        for pat in ai_slop_patterns:
            m = pat.search(content)
            if m and len(results["ai_slop_phrases"]) < 5:
                results["ai_slop_phrases"].append({"file": rel, "match": m.group(0)})

    return results


def check_twelve_essentials(repo_path: Path, robots_report: dict, google_seo_report: dict, prelaunch_report: dict):
    """Audit the 12 essentials that make a vibe-coded site real instead of a fake demo."""
    results = {
        "custom_404": {
            "name": "Custom 404 page",
            "passed": False,
            "details": "Missing custom 404 / not-found page",
        },
        "cta_above_the_fold": {
            "name": "CTA above the fold",
            "passed": False,
            "details": "No prominent CTA button/link detected in hero or landing view",
        },
        "meta_title_per_page": {
            "name": "Meta title per page",
            "passed": False,
            "details": "No route-specific <title> or metadata.title detected",
        },
        "meta_description_per_page": {
            "name": "Meta description per page",
            "passed": False,
            "details": "No meta description (<meta name='description'> or metadata.description) detected",
        },
        "og_image": {
            "name": "Open Graph image",
            "passed": False,
            "details": "Missing og:image / twitter:image or opengraph-image asset",
        },
        "favicon_set": {
            "name": "Favicon set",
            "passed": False,
            "details": "Missing custom favicon suite (/favicon.ico, apple-touch-icon, etc.)",
        },
        "robots_txt": {
            "name": "robots.txt",
            "passed": False,
            "details": "Missing robots.txt",
        },
        "sitemap_xml": {
            "name": "sitemap.xml",
            "passed": False,
            "details": "Missing sitemap.xml or dynamic sitemap generation",
        },
        "alt_text": {
            "name": "Alt text on every image",
            "passed": False,
            "details": "Images missing alt attributes",
        },
        "loading_states": {
            "name": "Loading states",
            "passed": False,
            "details": "No loading states, skeletons, spinners, or Suspense fallbacks detected",
        },
        "privacy_policy": {
            "name": "Privacy policy page",
            "passed": False,
            "details": "Missing privacy policy page (/privacy)",
        },
        "analytics_installed": {
            "name": "Analytics installed",
            "passed": False,
            "details": "No analytics telemetry detected (PostHog, Plausible, GA4, Vercel Analytics, etc.)",
        },
    }

    # 1. Custom 404 page
    if prelaunch_report.get("has_custom_404"):
        results["custom_404"]["passed"] = True
        results["custom_404"]["details"] = "Custom 404 / not-found page found"
    else:
        for p in walk_files(repo_path):
            if p.suffix.lower() in WEB_EXTENSIONS:
                try:
                    content = p.read_text(errors="ignore")
                    if re.search(r'path=["\']\*["\'].*?(?:NotFound|<404|not-found)', content, re.IGNORECASE) or 'NotFound' in p.name:
                        results["custom_404"]["passed"] = True
                        results["custom_404"]["details"] = f"Wildcard/NotFound route in {p.name}"
                        break
                except Exception:
                    pass

    # 7. robots.txt
    if robots_report.get("found"):
        results["robots_txt"]["passed"] = True
        results["robots_txt"]["details"] = f"robots.txt found ({robots_report.get('file', 'robots.txt')})"

    # 8. sitemap.xml
    sitemaps = google_seo_report.get("sitemap_files", [])
    if sitemaps:
        results["sitemap_xml"]["passed"] = True
        results["sitemap_xml"]["details"] = f"Sitemap found ({', '.join(sitemaps[:2])})"

    # 9. Alt text on every image
    missing_alts = google_seo_report.get("images_missing_alt", [])
    if not missing_alts:
        results["alt_text"]["passed"] = True
        results["alt_text"]["details"] = "All images include alt attributes"
    else:
        results["alt_text"]["passed"] = False
        results["alt_text"]["details"] = f"{len(missing_alts)} image(s) missing alt attributes"

    # 11. Privacy policy
    if prelaunch_report.get("has_privacy_policy"):
        results["privacy_policy"]["passed"] = True
        results["privacy_policy"]["details"] = "Privacy policy page/file found"
    else:
        for p in walk_files(repo_path):
            if "privacy" in p.name.lower():
                results["privacy_policy"]["passed"] = True
                results["privacy_policy"]["details"] = f"Privacy page file: {p.name}"
                break

    cta_patterns = [
        re.compile(r'\b(?:get started|start free|start trial|sign up|join now|join waitlist|book demo|book a demo|schedule demo|try free|try for free|request access|get access|explore features|download now|buy now|subscribe)\b', re.IGNORECASE),
        re.compile(r'<(?:button|Button)[^>]*>[^<]*(?:Start|Join|Sign|Try|Get|Book|Download|Buy|Subscribe|Explore)[^<]*<\/(?:button|Button)>', re.IGNORECASE),
        re.compile(r'<a\s+[^>]*href=["\'](?!#$)[^"\']+["\'][^>]*>[^<]*(?:Start|Join|Sign|Try|Get|Book|Download|Buy|Subscribe|Explore)[^<]*<\/a>', re.IGNORECASE),
        re.compile(r'<Link\s+[^>]*to=["\'](?!#$)[^"\']+["\'][^>]*>[^<]*(?:Start|Join|Sign|Try|Get|Book|Download|Buy|Subscribe|Explore)[^<]*<\/Link>', re.IGNORECASE),
    ]

    title_pat = re.compile(r'<title>([^<]+)<\/title>', re.IGNORECASE)
    meta_title_pat = re.compile(r'(?:title:\s*["\']([^"\']+)["\']|<Title>([^<]+)<\/Title>)', re.IGNORECASE)
    desc_pat = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']|<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']|description:\s*["\']([^"\']+)["\']', re.IGNORECASE)
    loading_pat = re.compile(r'\b(?:Skeleton|Loader2|Spinner|isLoading|isPending|isSubmitting|fallback={<(?:Skeleton|Spinner|Loader2))\b|<Suspense\b|loading\.tsx|loading\.jsx', re.IGNORECASE)

    analytics_signatures = [
        ("@vercel/analytics", re.compile(r'@vercel\/analytics|va\(|VercelAnalytics')),
        ("PostHog", re.compile(r'posthog-js|@posthog\/|posthog\.init|posthog\.capture')),
        ("Plausible", re.compile(r'plausible-tracker|plausible\.io')),
        ("Google Analytics / gtag", re.compile(r'gtag\(|google-analytics\.com|@next\/third-parties\/google|react-ga4|react-ga|G-[A-Z0-9]+')),
        ("Umami", re.compile(r'umami\.is|analytics\.umami\.is|data-website-id=')),
        ("Fathom", re.compile(r'usefathom\.com|fathom-client')),
        ("Mixpanel", re.compile(r'mixpanel-browser|mixpanel\.init')),
        ("Cloudflare Web Analytics", re.compile(r'cloudflareinsights\.com|static\.cloudflareinsights\.com')),
        ("Segment", re.compile(r'@segment\/analytics-next|analytics\.track')),
    ]

    favicon_files = []
    found_titles = []
    found_descs = []
    loading_matches = 0
    hero_cta_found = None
    detected_analytics = []

    for p in walk_files(repo_path):
        name_lower = p.name.lower()

        # Check favicon files
        if name_lower in ["favicon.ico", "favicon.svg", "favicon.png", "apple-touch-icon.png", "site.webmanifest", "manifest.json", "icon.png", "icon.svg"]:
            favicon_files.append(str(p.relative_to(repo_path)))

        # Check OG image files
        if any(name_lower.startswith(prefix) for prefix in ["opengraph-image", "twitter-image", "og-image", "og."]):
            if p.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".tsx", ".jsx", ".ts", ".js"]:
                results["og_image"]["passed"] = True
                results["og_image"]["details"] = f"OG image file found: {p.name}"

        # Check package.json for analytics
        if name_lower == "package.json":
            try:
                data = json.loads(p.read_text(errors="ignore"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                for provider, pat in analytics_signatures:
                    for dep in deps:
                        if pat.search(dep) and provider not in detected_analytics:
                            detected_analytics.append(provider)
            except Exception:
                pass

        if p.suffix.lower() in WEB_EXTENSIONS:
            rel = str(p.relative_to(repo_path))
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue

            # Check OG tags
            if not results["og_image"]["passed"]:
                if 'property="og:image"' in content or 'name="og:image"' in content or ('openGraph:' in content and 'images:' in content):
                    results["og_image"]["passed"] = True
                    results["og_image"]["details"] = f"og:image tag defined in {p.name}"

            # Check favicon tags
            if '<link' in content and ('rel="icon"' in content or "rel='icon'" in content or 'apple-touch-icon' in content):
                if rel not in favicon_files:
                    favicon_files.append(f"tag in {p.name}")

            # Check titles
            for m in title_pat.finditer(content):
                val = m.group(1).strip()
                if val and "Vite + React" not in val:
                    found_titles.append(val)
            for m in meta_title_pat.finditer(content):
                val = (m.group(1) or m.group(2) or "").strip()
                if val and "Vite + React" not in val:
                    found_titles.append(val)

            # Check descriptions
            for m in desc_pat.finditer(content):
                val = (m.group(1) or m.group(2) or m.group(3) or "").strip()
                if val and len(val) > 10:
                    found_descs.append(val)

            # Check loading states
            if loading_pat.search(content):
                loading_matches += 1

            # Check CTA above the fold
            is_landing = any(k in name_lower for k in ["hero", "masthead", "home", "landing"]) or name_lower in ["page.tsx", "page.jsx", "index.tsx", "index.jsx", "app.tsx", "app.jsx", "index.html", "+page.svelte", "index.astro"]
            if is_landing and not hero_cta_found:
                lines = content.splitlines()[:150]
                head_snippet = "\n".join(lines)
                for cta_pat in cta_patterns:
                    match = cta_pat.search(head_snippet)
                    if match:
                        hero_cta_found = (rel, match.group(0)[:40])
                        break

            # Check analytics in code
            for provider, pat in analytics_signatures:
                if provider not in detected_analytics and pat.search(content):
                    detected_analytics.append(provider)

    if hero_cta_found:
        results["cta_above_the_fold"]["passed"] = True
        results["cta_above_the_fold"]["details"] = f"Actionable CTA in {hero_cta_found[0]} ('{hero_cta_found[1].strip()}')"

    if found_titles:
        results["meta_title_per_page"]["passed"] = True
        results["meta_title_per_page"]["details"] = f"Page titles detected ({len(found_titles)} found, e.g. '{found_titles[0][:40]}')"

    if found_descs:
        results["meta_description_per_page"]["passed"] = True
        results["meta_description_per_page"]["details"] = f"Meta descriptions detected ({len(found_descs)} found)"

    if favicon_files:
        results["favicon_set"]["passed"] = True
        results["favicon_set"]["details"] = f"Favicon set detected ({', '.join(favicon_files[:3])})"

    if loading_matches > 0:
        results["loading_states"]["passed"] = True
        results["loading_states"]["details"] = f"Loading states detected ({loading_matches} files with Skeletons/spinners/Suspense)"

    if detected_analytics:
        results["analytics_installed"]["passed"] = True
        results["analytics_installed"]["details"] = f"Analytics installed: {', '.join(detected_analytics)}"

    passed_count = sum(1 for v in results.values() if v["passed"])
    verdict = "REAL SITE (PRODUCTION READY)" if passed_count == 12 else f"FAKE VIBE SITE DETECTED ({12 - passed_count} GAPS)"

    return {
        "score": f"{passed_count}/12",
        "passed_count": passed_count,
        "total": 12,
        "verdict": verdict,
        "items": results,
    }


def main():
    args = parse_args()
    repo_path = Path(args.repo).resolve()

    if not repo_path.is_dir():
        print(f"Error: not a repository directory: {repo_path}", file=sys.stderr)
        sys.exit(1)

    robots_report = check_robots_txt(repo_path)
    geo_report = check_structured_data_and_geo(repo_path)
    speed_report = check_speedmaxxing(repo_path)
    prelaunch_report = check_prelaunch_essentials(repo_path)
    slop_report = check_design_and_codebase_slop(repo_path)
    google_seo_report = check_google_technical_seo(repo_path)
    twelve_essentials_report = check_twelve_essentials(repo_path, robots_report, google_seo_report, prelaunch_report)

    full_report = {
        "evidence_scope": "Static source candidates; runtime enforcement and deployment remain unverified",
        "repo": str(repo_path),
        "twelve_real_essentials": twelve_essentials_report,
        "robots_txt": robots_report,
        "geo_and_ai_search": geo_report,
        "speedmaxxing": speed_report,
        "prelaunch_essentials": prelaunch_report,
        "slop_audit": slop_report,
        "google_technical_seo": google_seo_report,
    }

    if args.json:
        print(json.dumps(full_report, indent=2))
        return

    print("Static source candidates only; unmatched patterns do not prove safety or absence.")
    print("=" * 70)
    print("V-VIBE-WEB: WEBSITE & LANDING PAGE AUDIT SUMMARY")
    print("=" * 70)

    print(f"\nTHE 12 ESSENTIALS: REAL SITE VS FAKE VIBE SITE SCORECARD ({twelve_essentials_report['score']} PASS)")
    print("-" * 70)
    item_order = [
        ("custom_404", "1. Custom 404 page"),
        ("cta_above_the_fold", "2. CTA above the fold"),
        ("meta_title_per_page", "3. Meta title per page"),
        ("meta_description_per_page", "4. Meta description per page"),
        ("og_image", "5. Open Graph image"),
        ("favicon_set", "6. Favicon set"),
        ("robots_txt", "7. robots.txt"),
        ("sitemap_xml", "8. sitemap.xml"),
        ("alt_text", "9. Alt text on every image"),
        ("loading_states", "10. Loading states"),
        ("privacy_policy", "11. Privacy policy page"),
        ("analytics_installed", "12. Analytics installed"),
    ]
    for key, label in item_order:
        item = twelve_essentials_report["items"][key]
        status = "PASS" if item["passed"] else "FAIL (Missing)"
        print(f"  {label:<32}: [{status}] - {item['details']}")
    print(f"  VERDICT: {twelve_essentials_report['verdict']}")
    print("=" * 70)

    print("\n1. GEO & AI Search Discovery (ChatGPT / Perplexity / Claude):")
    print(f"  - robots.txt found: {'YES' if robots_report['found'] else 'NO (Missing!)'}")
    if robots_report["blocks_ai_bots"]:
        print(f"  - [INFO] Static policy blocks these crawler roots; preserve intended policy: {', '.join(robots_report['blocks_ai_bots'])}")
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
    print(f"  - Form bot-defense patterns (Turnstile/honeypot): {'YES' if prelaunch_report['has_form_bot_defense'] else ('N/A' if not prelaunch_report['has_forms'] else 'NOT DETECTED; verify server defenses')}")

    print("\n4. Design Slop Indicators (AI UI Clichés):")
    ds = slop_report["design_slop"]
    print(f"  - Badge/Tag spam: {ds['badge_count']} instances")
    print(f"  - Divider lines (Separator/hr/border-t): {ds['divider_count']} instances")
    print(f"  - Opacity layering instances: {ds['opacity_layering_count']}")
    print(f"  - Nested bordered containers: {ds['bordered_container_count']}")
    if ds["italic_buzzwords"]:
        print(f"  - [WARNING] Italicized copy/buzzwords ({len(ds['italic_buzzwords'])} found):")
        for ib in ds["italic_buzzwords"][:3]:
            print(f"    * {ib['file']}: {ib['text']}")
    if ds["instrument_serif_negative_kerning"]:
        print(f"  - [WARNING] Serif font + negative kerning ({len(ds['instrument_serif_negative_kerning'])} found):")
        for sk in ds["instrument_serif_negative_kerning"][:3]:
            print(f"    * {sk['file']}: {sk['text']}")
    if ds["section_numbering"]:
        print(f"  - Section numbering (01 /, Step 01): {len(ds['section_numbering'])} found")
    if ds["code_breadcrumbs"]:
        print(f"  - Code breadcrumbs / terminal mockups: {len(ds['code_breadcrumbs'])} found")
    if ds["superfluous_diagrams"]:
        print(f"  - Detailed diagrams (Mermaid/SVG): {len(ds['superfluous_diagrams'])} found")

    print("\n5. Codebase Slop Indicators:")
    cs = slop_report["codebase_slop"]
    if cs["layer_first_layout"]:
        print("  - [WARNING] Layer-first folder structure (components/services/utils without feature domain slices)")
    elif cs["feature_first_layout"]:
        print("  - Feature-first domain layout: PASS")
    if cs["god_files"]:
        print(f"  - [WARNING] God files (> 300 LOC) found ({len(cs['god_files'])} files):")
        for gf in cs["god_files"][:3]:
            print(f"    * {gf['file']} ({gf['lines']} lines)")
    if cs["representable_illegal_states"]:
        print(f"  - [WARNING] Representable illegal states in: {', '.join(cs['representable_illegal_states'][:3])}")
    if cs["layering_violations"]:
        print(f"  - [WARNING] Direct DB queries in UI components: {', '.join(cs['layering_violations'][:3])}")

    print("\n6. Google Technical SEO & Search Console Readiness (The 20-Point Checklist):")
    print(f"  - Rendering Architecture: {google_seo_report['rendering_architecture']}")
    if google_seo_report["sitemap_files"]:
        print(f"  - XML Sitemap: FOUND ({', '.join(google_seo_report['sitemap_files'])})")
    else:
        print("  - XML Sitemap: MISSING (Create sitemap.xml to enable URL discovery)")
    blocked = robots_report.get("googlebot_blocked")
    access = "UNVERIFIED (no readable static policy)" if blocked is None else "ROOT DISALLOWED by static policy" if blocked else "ROOT ALLOWED by static policy; deployment unverified"
    print(f"  - Googlebot Access in robots.txt: {access}")
    if google_seo_report["noindex_tags"]:
        print(f"  - [CRITICAL] noindex meta tags found in production files ({len(google_seo_report['noindex_tags'])} files):")
        for nf in google_seo_report["noindex_tags"][:3]:
            print(f"    * {nf}")
    else:
        print("  - noindex Tag Audit: No configured pattern found; deployed directives UNVERIFIED")
    if google_seo_report["canonical_tags"]:
        print(f"  - Canonical Tags (rel=canonical): IMPLEMENTED ({len(google_seo_report['canonical_tags'])} files)")
    else:
        print("  - Canonical Tags: No configured pattern found; inspect generated metadata and canonical signals")
    h1_iss = google_seo_report["h1_issues"]
    if h1_iss["missing_h1"]:
        print(f"  - [WARNING] Pages missing <h1> tags ({len(h1_iss['missing_h1'])} pages): {', '.join(h1_iss['missing_h1'][:3])}")
    if h1_iss["multiple_h1"]:
        print(f"  - [WARNING] Pages with multiple <h1> tags: {', '.join(item['file'] for item in h1_iss['multiple_h1'][:3])}")
    if not h1_iss["missing_h1"] and not h1_iss["multiple_h1"]:
        print("  - <h1> Hierarchy: No configured pattern violations found; rendered structure UNVERIFIED")
    if google_seo_report["images_missing_alt"]:
        print(f"  - [WARNING] Images missing alt text ({len(google_seo_report['images_missing_alt'])} instances)")
    else:
        print("  - Image alt text: PASS")
    if google_seo_report["schema_types"]:
        print(f"  - Structured Data (Schema.org): {', '.join(google_seo_report['schema_types'])}")
    else:
        print("  - Structured Data: MISSING FAQPage / Article / Breadcrumb schemas")
    print(f"  - Breadcrumb Navigation: {'IMPLEMENTED' if google_seo_report['has_breadcrumbs'] else 'MISSING'}")
    eeat = google_seo_report["eeat_signals"]
    eeat_status = "DETECTED" if (eeat["has_author_byline"] or eeat["has_author_bio_page"]) else "MISSING (Anonymous content risk)"
    print(f"  - E-E-A-T Author & Bio Signals: {eeat_status}")
    if google_seo_report["ai_slop_phrases"]:
        print(f"  - [WARNING] AI copywriting slop phrases detected ({len(google_seo_report['ai_slop_phrases'])} matches):")
        for slop in google_seo_report["ai_slop_phrases"][:3]:
            print(f"    * {slop['file']}: \"{slop['match']}\"")
    else:
        print("  - AI Slop Copywriting: PASS (No generic AI filler phrases detected)")
    print("=" * 70)


if __name__ == "__main__":
    main()
