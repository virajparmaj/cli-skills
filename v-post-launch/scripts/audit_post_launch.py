#!/usr/bin/env python3
"""
audit_post_launch.py - Deterministic scanner for the 10 Post-Launch Website Essentials.

Ten things to do right after your website goes live:
 1. Remove the noindex tags.
 2. Set up your Google Search Console.
 3. Set up your Google Analytics.
 4. Check your robots.txt.
 5. Redirect the www version to the non-www version (or vice-versa).
 6. Submit your sitemap.
 7. Give every page its own title and meta description.
 8. Submit to Bing Webmaster Tools (and IndexNow).
 9. Launch your website on Product Hunt.
10. Add a score badge / trust widget.
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
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
    "archive",
    ".cache",
}

TEMPLATE_EXTENSIONS = {
    ".html",
    ".htm",
    ".jsx",
    ".tsx",
    ".vue",
    ".svelte",
    ".astro",
    ".php",
}

CONFIG_FILES = {
    "vercel.json",
    "netlify.toml",
    "_headers",
    "_redirects",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "astro.config.mjs",
    "vite.config.ts",
    "vite.config.js",
    "Caddyfile",
    "nginx.conf",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Audit website for the 10 critical post-launch essentials"
    )
    parser.add_argument("--repo", default=".", help="Path to website repository")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    return parser.parse_args()


def get_all_files(repo_path: Path):
    all_files = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            all_files.append(Path(root) / f)
    return all_files


def find_public_dir(repo_path: Path):
    candidates = ["public", "static", "dist", "."]
    for c in candidates:
        p = repo_path / c
        if p.is_dir() and c != ".":
            return p
    return repo_path


# --- 1. Remove noindex tags ---
def check_noindex(repo_path: Path, files):
    findings = []
    status = "PASS"

    noindex_meta_regex = re.compile(
        r'<meta\s+[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex[^"\']*["\']',
        re.IGNORECASE,
    )
    noindex_meta_regex_alt = re.compile(
        r'<meta\s+[^>]*content=["\'][^"\']*noindex[^"\']*["\'][^>]*name=["\']robots["\']',
        re.IGNORECASE,
    )
    noindex_header_regex = re.compile(
        r'X-Robots-Tag[\s:]*["\']?.*?noindex', re.IGNORECASE
    )

    for f in files:
        if f.suffix in TEMPLATE_EXTENSIONS or f.name in CONFIG_FILES:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            rel_path = f.relative_to(repo_path)

            # Check if conditionally guarded by environment check
            is_guarded = bool(
                re.search(
                    r'(VERCEL_ENV|NODE_ENV|PROD|production|isPreview|isDev|ENVIRONMENT)',
                    content,
                )
            )

            meta_hits = list(noindex_meta_regex.finditer(content)) + list(
                noindex_meta_regex_alt.finditer(content)
            )
            if meta_hits:
                if is_guarded:
                    if status != "FAIL":
                        status = "WARN"
                    findings.append(
                        f"{rel_path}: noindex tag and environment-related text found; whether the tag is conditional remains unverified."
                    )
                else:
                    status = "FAIL"
                    findings.append(
                        f"{rel_path}: Hardcoded <meta name='robots' content='noindex'> tag found! Search engines cannot index this page."
                    )

            if f.name in CONFIG_FILES and noindex_header_regex.search(content):
                status = "FAIL"
                findings.append(
                    f"{rel_path}: Configures 'X-Robots-Tag: noindex' response header!"
                )

    if not findings:
        findings.append("No rogue noindex meta tags or X-Robots-Tag headers found in production code.")

    return {
        "id": 1,
        "name": "Remove noindex tags",
        "status": status,
        "details": findings,
    }


# --- 2. Google Search Console ---
def check_search_console(repo_path: Path, files):
    status = "WARN"
    findings = []
    gsc_meta_regex = re.compile(
        r'<meta\s+[^>]*name=["\']google-site-verification["\'][^>]*content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    gsc_file_regex = re.compile(r'^google[a-f0-9]{16}\.html$', re.IGNORECASE)

    found_meta = []
    found_files = []

    for f in files:
        if gsc_file_regex.match(f.name):
            found_files.append(str(f.relative_to(repo_path)))

        if f.suffix in TEMPLATE_EXTENSIONS:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                for match in gsc_meta_regex.finditer(content):
                    found_meta.append((str(f.relative_to(repo_path)), match.group(1)))
            except Exception:
                continue

    if found_files:
        status = "PASS"
        findings.append(f"GSC verification HTML file present: {', '.join(found_files)}")
    if found_meta:
        status = "PASS"
        for p, code in found_meta:
            findings.append(f"GSC meta verification tag found in {p} (Token: {code[:8]}...)")

    if status != "PASS":
        findings.append(
            "No GSC HTML verification tag or google*.html file found. (Note: Domain DNS TXT verification may be configured at your DNS provider)."
        )

    return {
        "id": 2,
        "name": "Google Search Console",
        "status": status,
        "details": findings,
    }


# --- 3. Google Analytics / Telemetry ---
def check_analytics(repo_path: Path, files):
    status = "WARN"
    findings = []

    ga4_regex = re.compile(r'G-[A-Z0-9]{8,12}')
    gtm_regex = re.compile(r'GTM-[A-Z0-9]{6,10}')
    alt_analytics = {
        "PostHog": re.compile(r'posthog-js|app\.posthog\.com'),
        "Plausible": re.compile(r'plausible\.io/js/script'),
        "Vercel Analytics": re.compile(r'@vercel/analytics'),
        "Umami": re.compile(r'cloud\.umami\.is|analytics\.umami\.is'),
    }

    found_services = []

    for f in files:
        if f.suffix in {".html", ".htm", ".jsx", ".tsx", ".js", ".ts", ".vue", ".astro"}:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            rel_path = str(f.relative_to(repo_path))
            ga_matches = ga4_regex.findall(content)
            if ga_matches and "google" in content.lower():
                found_services.append(f"Google Analytics GA4 ({ga_matches[0]}) in {rel_path}")

            gtm_matches = gtm_regex.findall(content)
            if gtm_matches:
                found_services.append(f"Google Tag Manager ({gtm_matches[0]}) in {rel_path}")

            for name, reg in alt_analytics.items():
                if reg.search(content):
                    found_services.append(f"{name} integration in {rel_path}")

    if found_services:
        status = "PASS"
        findings.extend(list(dict.fromkeys(found_services)))
    else:
        findings.append("No Google Analytics (GA4/GTM) or privacy telemetry tag detected in client code.")

    return {
        "id": 3,
        "name": "Google Analytics",
        "status": status,
        "details": findings,
    }


# --- 4. Robots.txt Integrity ---
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


def check_robots_txt(repo_path: Path, files):
    status = "FAIL"
    findings = []
    robots_candidates = [
        repo_path / "public" / "robots.txt",
        repo_path / "static" / "robots.txt",
        repo_path / "robots.txt",
        repo_path / "app" / "robots.ts",
        repo_path / "app" / "robots.js",
        repo_path / "src" / "app" / "robots.ts",
        repo_path / "src" / "app" / "robots.js",
    ]

    target = None
    for c in robots_candidates:
        if c.is_file():
            target = c
            break

    if not target:
        findings.append("robots.txt not found in public/, static/, or root!")
        return {
            "id": 4,
            "name": "Check robots.txt",
            "status": "FAIL",
            "details": findings,
        }

    status = "PASS"
    rel_path = target.relative_to(repo_path)
    findings.append(f"robots.txt located at {rel_path}")

    try:
        content = target.read_text(encoding="utf-8", errors="ignore")
        if target.suffix in {".ts", ".js"}:
            return {"id": 4, "name": "Check robots.txt", "status": "WARN",
                    "details": [f"Dynamic robots generator at {rel_path}; effective deployed rules remain unverified."]}
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]

        has_user_agent = any(l.lower().startswith("user-agent:") for l in lines)
        has_sitemap = any(l.lower().startswith("sitemap:") for l in lines)
        disallow_all = not root_crawl_allowed(content, "Googlebot")

        if not has_user_agent:
            status = "WARN"
            findings.append("Missing 'User-agent:' directive.")

        if disallow_all:
            status = "FAIL"
            findings.append("Static robots rules disallow Googlebot at the root path; verify deployed rules and intended public pages before treating it as a bug.")

        if not has_sitemap:
            if status != "FAIL":
                status = "WARN"
            findings.append("Missing 'Sitemap: https://yourdomain.com/sitemap.xml' directive in robots.txt.")
        else:
            sitemap_lines = [l for l in lines if l.lower().startswith("sitemap:")]
            findings.append(f"Referenced {sitemap_lines[0]}")
    except Exception as e:
        status = "WARN"
        findings.append(f"Could not parse robots.txt: {e}")

    return {
        "id": 4,
        "name": "Check robots.txt",
        "status": status,
        "details": findings,
    }


# --- 5. www to non-www Redirect ---
def check_canonical_redirects(repo_path: Path, files):
    status = "WARN"
    findings = []

    # Check vercel.json
    vercel_path = repo_path / "vercel.json"
    if vercel_path.is_file():
        try:
            v_data = json.loads(vercel_path.read_text(encoding="utf-8"))
            redirects = v_data.get("redirects", [])
            for r in redirects:
                source = r.get("source", "")
                has_www = "www." in source or "www" in str(r.get("has", []))
                if has_www and r.get("permanent", False):
                    status = "PASS"
                    findings.append(f"vercel.json: 301 canonical redirect rule detected for www -> non-www (or vice versa).")
                    break
        except Exception:
            pass

    # Check _redirects
    for redir_name in ["_redirects", "public/_redirects"]:
        redir_path = repo_path / redir_name
        if redir_path.is_file():
            try:
                content = redir_path.read_text(encoding="utf-8", errors="ignore")
                if "www." in content and ("301" in content or "302" in content):
                    status = "PASS"
                    findings.append(f"{redir_name}: Canonical domain redirect found.")
            except Exception:
                pass

    # Check next.config
    for nc in ["next.config.js", "next.config.mjs", "next.config.ts"]:
        nc_path = repo_path / nc
        if nc_path.is_file():
            try:
                content = nc_path.read_text(encoding="utf-8", errors="ignore")
                if "redirects" in content and "www." in content:
                    status = "PASS"
                    findings.append(f"{nc}: Canonical redirect logic found.")
            except Exception:
                pass

    if status != "PASS":
        findings.append(
            "No code-level 301 www -> non-www redirect found. (Verify if DNS / Edge Host like Cloudflare/Vercel handles this at domain level)."
        )

    return {
        "id": 5,
        "name": "Redirect www to non-www",
        "status": status,
        "details": findings,
    }


# --- 6. XML Sitemap ---
def check_sitemap(repo_path: Path, files):
    status = "FAIL"
    findings = []

    sitemap_candidates = [
        repo_path / "public" / "sitemap.xml",
        repo_path / "static" / "sitemap.xml",
        repo_path / "sitemap.xml",
        repo_path / "app" / "sitemap.ts",
        repo_path / "app" / "sitemap.js",
        repo_path / "src" / "app" / "sitemap.ts",
        repo_path / "src" / "app" / "sitemap.js",
    ]

    target = None
    for c in sitemap_candidates:
        if c.is_file():
            target = c
            break

    if not target:
        findings.append("sitemap.xml not found in public/, static/, or root!")
        return {
            "id": 6,
            "name": "Submit your sitemap",
            "status": "FAIL",
            "details": findings,
        }

    rel_path = target.relative_to(repo_path)
    status = "PASS"

    if target.suffix == ".xml":
        try:
            content = target.read_text(encoding="utf-8", errors="ignore")
            root = ET.fromstring(content)
            kind = root.tag.rsplit("}", 1)[-1]
            if kind not in {"urlset", "sitemapindex"}:
                status = "WARN"
                findings.append(f"XML at {rel_path} has unsupported sitemap root '{kind}'.")
            else:
                item_name = "url" if kind == "urlset" else "sitemap"
                entries = [item for item in root if item.tag.rsplit("}", 1)[-1] == item_name]
                locations = [child.text for item in entries for child in item if child.tag.rsplit("}", 1)[-1] == "loc" and child.text and child.text.strip()]
                if not entries or len(locations) != len(entries):
                    status = "WARN"
                    findings.append(f"Sitemap at {rel_path} is empty or has entries without a loc URL.")
                else:
                    findings.append(f"Valid XML {kind} at {rel_path} with {len(entries)} {item_name} entries; deployed URLs and submission remain unverified.")

        except Exception as e:
            status = "WARN"
            findings.append(f"sitemap.xml exists at {rel_path} but XML parsing threw warning: {e}")
    else:
        findings.append(f"Dynamic sitemap generator located at {rel_path}.")

    return {
        "id": 6,
        "name": "Submit your sitemap",
        "status": status,
        "details": findings,
    }


# --- 7. Titles and Meta Descriptions ---
def check_titles_and_meta(repo_path: Path, files):
    status = "PASS"
    findings = []
    issues = []

    title_regex = re.compile(r'<title>(.*?)</title>', re.IGNORECASE | re.DOTALL)
    desc_regex = re.compile(
        r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
        re.IGNORECASE,
    )
    desc_regex_alt = re.compile(
        r'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',
        re.IGNORECASE,
    )

    placeholder_titles = {
        "vite + react",
        "vite + react + ts",
        "vite app",
        "react app",
        "create next app",
        "next.js app",
        "untitled",
        "document",
        "my website",
    }

    checked_pages = 0

    for f in files:
        if f.suffix in {".html", ".htm"}:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            checked_pages += 1
            rel_path = str(f.relative_to(repo_path))

            # Title check
            t_match = title_regex.search(content)
            if not t_match:
                issues.append(f"{rel_path}: Missing <title> tag.")
                status = "FAIL"
            else:
                title = t_match.group(1).strip()
                if title.lower() in placeholder_titles:
                    issues.append(f"{rel_path}: Generic/placeholder title '{title}'!")
                    status = "FAIL"
                elif len(title) > 65:
                    issues.append(f"{rel_path}: Title is long ({len(title)} chars > 65 max).")
                elif len(title) < 15:
                    issues.append(f"{rel_path}: Title is very short ({len(title)} chars).")

            # Meta description check
            d_match = desc_regex.search(content) or desc_regex_alt.search(content)
            if not d_match:
                issues.append(f"{rel_path}: Missing <meta name='description'> tag.")
                if status == "PASS":
                    status = "WARN"
            else:
                desc = d_match.group(1).strip()
                if len(desc) < 50:
                    issues.append(f"{rel_path}: Meta description is too brief ({len(desc)} chars < 50).")
                elif len(desc) > 165:
                    issues.append(f"{rel_path}: Meta description may truncate ({len(desc)} chars > 165).")

    if checked_pages == 0:
        status = "WARN"
        findings.append("No HTML pages inspected; rendered route titles and descriptions remain unverified.")
    elif issues:
        findings.extend(issues[:8])
        if len(issues) > 8:
            findings.append(f"...and {len(issues) - 8} more title/meta issues.")
    else:
        findings.append(f"All {checked_pages} inspected HTML pages have custom titles and meta descriptions.")

    return {
        "id": 7,
        "name": "Unique title & meta description",
        "status": status,
        "details": findings,
    }


# --- 8. Bing Webmaster Tools & IndexNow ---
def check_bing_webmaster(repo_path: Path, files):
    status = "WARN"
    findings = []

    bing_meta_regex = re.compile(
        r'<meta\s+[^>]*name=["\']msvalidate\.01["\'][^>]*content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    bing_xml_file = repo_path / "public" / "BingSiteAuth.xml"
    if not bing_xml_file.is_file():
        bing_xml_file = repo_path / "BingSiteAuth.xml"

    if bing_xml_file.is_file():
        status = "PASS"
        findings.append("BingSiteAuth.xml file detected in public directory.")

    # Check for meta tag
    for f in files:
        if f.suffix in TEMPLATE_EXTENSIONS:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                for match in bing_meta_regex.finditer(content):
                    status = "PASS"
                    findings.append(f"msvalidate.01 meta tag found in {f.relative_to(repo_path)}")
            except Exception:
                continue

    # Check for IndexNow key file
    indexnow_keys = []
    for f in files:
        if f.name.endswith(".txt") and len(f.stem) in [32, 64] and re.match(r'^[a-f0-9]+$', f.stem):
            indexnow_keys.append(str(f.relative_to(repo_path)))

    if indexnow_keys:
        status = "PASS"
        findings.append(f"IndexNow API key file detected: {', '.join(indexnow_keys)}")

    if status != "PASS":
        findings.append(
            "No Bing verification tag (msvalidate.01) or IndexNow key found. (Bing can also be synced automatically from Google Search Console)."
        )

    return {
        "id": 8,
        "name": "Submit to Bing Webmaster Tools",
        "status": status,
        "details": findings,
    }


# --- 9. Product Hunt Launch Prep ---
def check_product_hunt_prep(repo_path: Path, files):
    status = "WARN"
    findings = []

    ph_mentions = []
    for f in files:
        if f.suffix in {".md", ".json", ".html", ".tsx", ".jsx", ".txt"}:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if "producthunt" in content.lower() or "product hunt" in content.lower():
                    ph_mentions.append(str(f.relative_to(repo_path)))
            except Exception:
                continue

    if ph_mentions:
        status = "PASS"
        findings.append(f"Product Hunt references/assets found in: {', '.join(ph_mentions[:4])}")
    else:
        findings.append(
            "No Product Hunt launch materials, draft comments, or badges detected in repository."
        )

    return {
        "id": 9,
        "name": "Launch on Product Hunt",
        "status": status,
        "details": findings,
    }


# --- 10. Score Badge / Trust Widget ---
def check_score_trust_badge(repo_path: Path, files):
    status = "WARN"
    findings = []

    badge_patterns = {
        "Product Hunt Badge": re.compile(r'api\.producthunt\.com/widgets/embed-image'),
        "GitHub Star / Release Badge": re.compile(r'img\.shields\.io|shields\.io'),
        "Lighthouse / Perf Score Badge": re.compile(r'lighthouse-badger|pagespeed'),
        "Trust / Security Badge": re.compile(r'trustpilot|capterra|g2\.com|stripe-badge|soc2'),
    }

    found_badges = []
    for f in files:
        if f.suffix in TEMPLATE_EXTENSIONS or f.suffix in {".md", ".mdx"}:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for name, pattern in badge_patterns.items():
                if pattern.search(content):
                    found_badges.append(f"{name} in {f.relative_to(repo_path)}")

    if found_badges:
        status = "PASS"
        findings.extend(list(dict.fromkeys(found_badges)))
    else:
        findings.append(
            "No social proof, score, or trust badge (Product Hunt, Shields, Trustpilot) embedded."
        )

    return {
        "id": 10,
        "name": "Add a score / trust badge",
        "status": status,
        "details": findings,
    }


def main():
    args = parse_args()
    repo_path = Path(args.repo).resolve()

    if not repo_path.is_dir():
        print(f"Error: {repo_path} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    files = get_all_files(repo_path)

    checks = [
        check_noindex(repo_path, files),
        check_search_console(repo_path, files),
        check_analytics(repo_path, files),
        check_robots_txt(repo_path, files),
        check_canonical_redirects(repo_path, files),
        check_sitemap(repo_path, files),
        check_titles_and_meta(repo_path, files),
        check_bing_webmaster(repo_path, files),
        check_product_hunt_prep(repo_path, files),
        check_score_trust_badge(repo_path, files),
    ]

    pass_count = sum(1 for c in checks if c["status"] == "PASS")
    warn_count = sum(1 for c in checks if c["status"] == "WARN")
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")

    if args.json:
        result = {
            "evidence_scope": "Static discovery signals; production readiness and account status remain unverified",
            "summary": {
                "total": 10,
                "passed": pass_count,
                "warnings": warn_count,
                "failed": fail_count,
                "score_pct": int((pass_count / 10.0) * 100),
            },
            "checks": checks,
        }
        print(json.dumps(result, indent=2))
        return

    # Colored terminal output
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"

    print(f"\n{BOLD}{CYAN}=== 10 Post-Launch Website Essentials Audit ==={RESET}")
    print(f"Target Repository: {repo_path}")
    print(f"Total Checks: 10 | {GREEN}PASS: {pass_count}{RESET} | {YELLOW}WARN: {warn_count}{RESET} | {RED}FAIL: {fail_count}{RESET}")
    print(f"Post-Launch Readiness Score: {BOLD}{int((pass_count / 10.0) * 100)}%{RESET}\n")

    for c in checks:
        if c["status"] == "PASS":
            badge = f"{GREEN}[PASS]{RESET}"
        elif c["status"] == "WARN":
            badge = f"{YELLOW}[WARN]{RESET}"
        else:
            badge = f"{RED}[FAIL]{RESET}"

        print(f"{BOLD}{c['id']}. {c['name']}{RESET} {badge}")
        for d in c["details"]:
            print(f"   • {d}")
        print()


if __name__ == "__main__":
    main()
