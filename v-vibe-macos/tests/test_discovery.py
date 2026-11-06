"""Behavioral regressions for scoped audit discovery."""
import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / 'audit_macos_vibe.py'
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

    def test_sandbox_boolean_is_paired_to_its_own_key(self):
        path = self.repo / "App.entitlements"
        path.write_bytes(plistlib.dumps({"com.apple.security.app-sandbox": False, "com.apple.security.network.client": True}))
        result = audit.check_entitlements_and_sandbox(self.repo)
        self.assertFalse(result["sandbox_enabled"])
        self.assertTrue(result["network_client"])

    def test_binary_entitlements_are_read(self):
        path = self.repo / "App.entitlements"
        path.write_bytes(plistlib.dumps({"com.apple.security.app-sandbox": True}, fmt=plistlib.FMT_BINARY))
        self.assertTrue(audit.check_entitlements_and_sandbox(self.repo)["sandbox_enabled"])

    def test_malformed_entitlements_are_reported(self):
        self.write("App.entitlements", "<plist><dict>")
        self.assertEqual(audit.check_entitlements_and_sandbox(self.repo)["unreadable_entitlements"], ["App.entitlements"])

    def test_vendor_framework_does_not_classify_host_project(self):
        self.write("node_modules/electron/package.json", '{"name":"electron","dependencies":{"electron":"x"}}')
        self.assertEqual(audit.detect_macos_project_type(self.repo), ["Generic / Unknown Desktop"])
        self.write("package.json", '{"devDependencies":{"electron":"x"}}')
        self.assertIn("Electron (Node + Web)", audit.detect_macos_project_type(self.repo))


if __name__ == "__main__":
    unittest.main()
