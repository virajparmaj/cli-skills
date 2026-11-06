"""Behavioral regressions for scoped audit discovery."""
import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / 'audit_perf.py'
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

    def test_dependency_trees_are_never_traversed(self):
        self.write("node_modules/vendor/package.json", '{"dependencies":{"next":"x"}}')
        self.write("node_modules/vendor/vite.config.ts", "export default {}")
        self.write("src/App.tsx", "export default function App() { return <main />; }")
        original = audit.os.scandir
        def scandir(path):
            if Path(path).name == "node_modules":
                raise AssertionError("dependency tree visited")
            return original(path)
        with mock.patch.object(audit.os, "scandir", side_effect=scandir):
            audit.detect_stack(self.repo)
            audit.check_bundles_and_deps(self.repo)
            audit.check_caching_and_delivery(self.repo)

    def test_file_is_rejected_as_repository(self):
        target = self.write("input.txt", "not a repository")
        result = subprocess.run(["python3", str(SCRIPT), "--repo", str(target), "--json"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
