"""Behavioral regressions for scoped audit discovery."""
import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / 'audit_web_vibe.py'
SPEC = importlib.util.spec_from_file_location("audit_under_test", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="audit fixture ")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)

    def write(self, relative, text):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_specific_agent_group_overrides_wildcard(self):
        robots = "User-agent: *\nDisallow: /\nUser-agent: Googlebot\nAllow: /\n"
        self.write("public/robots.txt", robots)
        self.assertFalse(audit.check_robots_txt(self.repo)["googlebot_blocked"])

    def test_grouped_agents_comments_and_allow_ties(self):
        text = "User-agent: Googlebot\nUser-agent: Bingbot\nDisallow: / # blocked root\nAllow: /\n"
        self.assertTrue(audit.root_crawl_allowed(text))
        self.assertTrue(audit.root_crawl_allowed("User-agent: Googlebot\nDisallow:\nUser-agent: *\nDisallow: /\n"))

    def test_absent_policy_does_not_claim_verified_access(self):
        self.assertIsNone(audit.check_robots_txt(self.repo)["googlebot_blocked"])

    def test_valid_font_url_is_not_missing_swap(self):
        self.write("index.html", '<link href="https://fonts.googleapis.com/css2?family=Example&display=swap" rel="stylesheet">')
        self.assertEqual(audit.check_speedmaxxing(self.repo)["render_blocking_fonts"], [])

    def test_markdown_subheadings_are_not_extra_h1(self):
        self.write("src/pages/guide.md", "# Guide\n## Start\n## Finish\n")
        report = audit.check_google_technical_seo(self.repo)
        self.assertEqual(report["h1_issues"]["multiple_h1"], [])

    def test_csrf_marker_is_not_bot_defense(self):
        self.write("index.html", '<form><input name="csrf"></form>')
        self.assertFalse(audit.check_prelaunch_essentials(self.repo)["has_form_bot_defense"])

    def test_twelve_essentials_complete_real_site(self):
        # 1. Custom 404
        self.write("404.html", "<h1>Page Not Found</h1><a href='/'>Home</a>")
        # 2. CTA above the fold & 3. Title & 4. Description & 5. OG Image & 9. Alt text
        self.write(
            "index.html",
            """<!DOCTYPE html>
            <html>
            <head>
                <title>Acme Inc | Cloud Infrastructure</title>
                <meta name="description" content="Acme is the premier developer platform for edge orchestration.">
                <meta property="og:image" content="https://acme.com/og.png">
            </head>
            <body>
                <header>
                    <h1>Build Faster with Acme</h1>
                    <a href="/signup" class="btn">Get Started Free</a>
                </header>
                <main>
                    <img src="/hero.png" alt="Acme Dashboard Screenshot">
                </main>
            </body>
            </html>"""
        )
        # 6. Favicon set
        self.write("public/favicon.ico", "ico")
        self.write("public/apple-touch-icon.png", "png")
        # 7. robots.txt
        self.write("public/robots.txt", "User-agent: *\nAllow: /\nSitemap: https://acme.com/sitemap.xml\n")
        # 8. sitemap.xml
        self.write("public/sitemap.xml", "<urlset><url><loc>https://acme.com/</loc></url></urlset>")
        # 10. Loading states
        self.write("src/components/Loader.tsx", "export function TableSkeleton() { return <div className='skeleton'>Loading...</div> }")
        # 11. Privacy policy
        self.write("src/pages/privacy.tsx", "export default function Privacy() { return <h1>Privacy Policy</h1> }")
        # 12. Analytics installed
        self.write("package.json", json.dumps({"dependencies": {"@vercel/analytics": "^1.0.0"}}))

        robots_rep = audit.check_robots_txt(self.repo)
        seo_rep = audit.check_google_technical_seo(self.repo)
        prelaunch_rep = audit.check_prelaunch_essentials(self.repo)

        report = audit.check_twelve_essentials(self.repo, robots_rep, seo_rep, prelaunch_rep)

        self.assertEqual(report["score"], "12/12")
        self.assertEqual(report["verdict"], "REAL SITE (PRODUCTION READY)")
        for key, item in report["items"].items():
            self.assertTrue(item["passed"], f"Expected {key} to pass, but details: {item['details']}")

    def test_twelve_essentials_fake_vibe_site_flags_gaps(self):
        # Empty repo has no essentials
        robots_rep = audit.check_robots_txt(self.repo)
        seo_rep = audit.check_google_technical_seo(self.repo)
        prelaunch_rep = audit.check_prelaunch_essentials(self.repo)

        report = audit.check_twelve_essentials(self.repo, robots_rep, seo_rep, prelaunch_rep)
        self.assertIn("FAKE VIBE SITE DETECTED", report["verdict"])
        self.assertFalse(report["items"]["custom_404"]["passed"])
        self.assertFalse(report["items"]["cta_above_the_fold"]["passed"])
        self.assertFalse(report["items"]["meta_title_per_page"]["passed"])
        self.assertFalse(report["items"]["meta_description_per_page"]["passed"])
        self.assertFalse(report["items"]["og_image"]["passed"])
        self.assertFalse(report["items"]["favicon_set"]["passed"])
        self.assertFalse(report["items"]["robots_txt"]["passed"])
        self.assertFalse(report["items"]["sitemap_xml"]["passed"])
        self.assertFalse(report["items"]["loading_states"]["passed"])
        self.assertFalse(report["items"]["privacy_policy"]["passed"])
        self.assertFalse(report["items"]["analytics_installed"]["passed"])


if __name__ == "__main__":
    unittest.main()
