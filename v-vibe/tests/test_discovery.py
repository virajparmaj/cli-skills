"""Behavioral regressions for scoped audit discovery."""
import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / 'repo_audit_inventory.py'
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

    def test_inventory_prunes_dependency_tree_before_scanning(self):
        self.write("node_modules/vendor/example.test.ts", "export const ignored = 1;")
        self.write("src/example.test.ts", "export const owned = 1;")
        original = audit.os.scandir
        def scandir(path):
            if Path(path).name == "node_modules":
                raise AssertionError("dependency tree visited")
            return original(path)
        with mock.patch.object(audit.os, "scandir", side_effect=scandir):
            result = audit.collect_inventory(self.repo, 300, 10)
        self.assertEqual(result["placeholder_tests"], ["src/example.test.ts"])


if __name__ == "__main__":
    unittest.main()
