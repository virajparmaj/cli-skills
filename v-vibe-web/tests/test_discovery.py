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


if __name__ == "__main__":
    unittest.main()
