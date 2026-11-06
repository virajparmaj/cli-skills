"""Regression checks for static discovery statuses, without network access."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_post_launch.py"
SPEC = importlib.util.spec_from_file_location("audit_post_launch", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class PostLaunchStatusTests(unittest.TestCase):
    def test_missing_sitemap_does_not_downgrade_root_disallow(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            robots = repo / "robots.txt"
            robots.write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
            result = audit.check_robots_txt(repo, [robots])
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("Sitemap" in detail for detail in result["details"]))

    def test_missing_html_is_not_a_metadata_pass(self):
        result = audit.check_titles_and_meta(Path("."), [])
        self.assertEqual(result["status"], "WARN")
        self.assertIn("unverified", " ".join(result["details"]))

    def test_valid_metadata_can_still_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            page = repo / "index.html"
            page.write_text(
                '<title>Practical launch checks</title>'
                '<meta name="description" content="'
                + "Useful documentation for reviewing a launched website."
                + '">',
                encoding="utf-8",
            )
            self.assertEqual(audit.check_titles_and_meta(repo, [page])["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
