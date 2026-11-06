"""Behavioral regressions for scoped audit discovery."""
import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / 'audit_post_launch.py'
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

    def test_training_bot_block_does_not_block_googlebot(self):
        robots = self.write("robots.txt", "User-agent: GPTBot\nDisallow: /\nUser-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml\n")
        self.assertEqual(audit.check_robots_txt(self.repo, [robots])["status"], "PASS")

    def test_specific_and_empty_groups_override_wildcard(self):
        self.assertTrue(audit.root_crawl_allowed("User-agent: *\nDisallow: /\nUser-agent: Googlebot\nAllow: /\n"))
        self.assertTrue(audit.root_crawl_allowed("User-agent: Googlebot\nDisallow:\nUser-agent: *\nDisallow: /\n"))

    def test_next_root_app_metadata_routes_are_found(self):
        robots = self.write("app/robots.ts", "export default function robots() { return {rules: {userAgent: '*', allow: '/'}} }")
        sitemap = self.write("app/sitemap.ts", "export default function sitemap() { return [{url: 'https://example.com'}] }")
        self.assertIn("Dynamic robots generator", " ".join(audit.check_robots_txt(self.repo, [robots])["details"]))
        self.assertEqual(audit.check_sitemap(self.repo, [sitemap])["status"], "PASS")

    def test_unrelated_environment_word_does_not_prove_noindex_is_guarded(self):
        page = self.write("index.html", '<!-- production site --><meta name="robots" content="noindex">')
        self.assertEqual(audit.check_noindex(self.repo, [page])["status"], "WARN")

    def test_generic_xml_is_not_a_valid_sitemap(self):
        sitemap = self.write("sitemap.xml", "<hello>world</hello>")
        self.assertEqual(audit.check_sitemap(self.repo, [sitemap])["status"], "WARN")

    def test_sitemap_index_is_recognized(self):
        sitemap = self.write("sitemap.xml", '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://example.com/pages.xml</loc></sitemap></sitemapindex>')
        result = audit.check_sitemap(self.repo, [sitemap])
        self.assertEqual(result["status"], "PASS")
        self.assertIn("sitemapindex", " ".join(result["details"]))


if __name__ == "__main__":
    unittest.main()
