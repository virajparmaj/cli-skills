import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).parents[1] / "scripts"


class RouteCandidateTests(unittest.TestCase):
    def test_without_parser_regex_never_claims_resolved_public_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/App.tsx").write_text('<Route path="/admin" element={<ProtectedRoute/>}><Route path="settings" /></Route>')
            result = subprocess.run(["node", str(SCRIPTS / "list-routes.mjs"), str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            routes = json.loads(result.stdout)
            self.assertTrue(routes)
            self.assertTrue(all(r["kind"] == "candidate" for r in routes))
            self.assertIn("unverified", result.stderr)

    def test_external_sample_is_rejected_before_browser_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            routes = root / "routes.json"
            routes.write_text(json.dumps([{"path": "/items/:id", "kind": "dynamic", "samplePath": "https://example.com/"}]))
            result = subprocess.run(["node", str(SCRIPTS / "capture-routes.mjs"), str(root),
                                     "--base-url", "http://localhost:5173", "--routes", str(routes)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("same-origin", result.stderr)
            self.assertNotIn("playwright not installed", result.stderr)


if __name__ == "__main__":
    unittest.main()
