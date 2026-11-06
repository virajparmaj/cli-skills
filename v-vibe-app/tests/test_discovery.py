"""Behavioral regressions for scoped audit discovery."""
import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / 'audit_app_vibe.py'
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

    def test_only_git_tracked_env_files_are_called_tracked(self):
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.write(".gitignore", ".env\n")
        self.write(".env", "DUMMY=fixture\n")
        result = audit.check_secrets_and_env(self.repo)
        self.assertEqual(result["local_env_files"], [".env"])
        self.assertEqual(result["env_files_in_git"], [])
        subprocess.run(["git", "-C", str(self.repo), "add", "-f", ".env"], check=True)
        self.assertEqual(audit.check_secrets_and_env(self.repo)["env_files_in_git"], [".env"])

    def test_synthetic_secret_values_never_enter_json(self):
        fake = "sk_live_" + "X" * 30
        secret = "sb_secret_" + "Y" * 30
        self.write("src/config.ts", f'const latestKey = "{fake}";\nconst supabaseKey = "{secret}";')
        result = audit.check_secrets_and_env(self.repo)
        self.assertEqual(len(result["hardcoded_secrets"]), 2)
        self.assertNotIn(fake, json.dumps(result))
        self.assertNotIn(secret, json.dumps(result))

    def test_vendor_schema_is_not_project_migration_evidence(self):
        self.write("node_modules/vendor/prisma/schema.prisma", "model User {}")
        self.assertFalse(audit.check_database_hygiene(self.repo)["has_migrations"])
        self.write("supabase/migrations/001.sql", "create table app_table(id int);")
        self.assertEqual(audit.check_database_hygiene(self.repo)["migration_framework"], "Supabase")


if __name__ == "__main__":
    unittest.main()
