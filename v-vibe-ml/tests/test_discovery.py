"""Behavioral regressions for scoped audit discovery."""
import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / 'audit_ml_vibe.py'
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

    def test_configured_models_are_not_limited_to_old_families(self):
        self.write("client.py", 'model = "deployment-main"\nmodel_name = "future-model-2026-10-20"\nmessage = "unrelated-model-name"\n')
        result = audit.check_model_versioning_and_fallbacks(self.repo)
        self.assertEqual({m["model"] for m in result["model_references"]}, {"deployment-main", "future-model-2026-10-20"})
        self.assertEqual(result["pinned_models"][0]["model"], "future-model-2026-10-20")
        self.assertEqual(result["unpinned_models"][0]["model"], "deployment-main")

    def test_empty_source_is_not_reported_as_proven_safe(self):
        result = subprocess.run(["python3", str(SCRIPT), "--repo", str(self.repo)], capture_output=True, text=True, check=True)
        self.assertNotIn("PROTECTED", result.stdout)
        self.assertNotIn("Clean structured messages", result.stdout)
        self.assertIn("UNVERIFIED", result.stdout)


if __name__ == "__main__":
    unittest.main()
