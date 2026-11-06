import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tracemalloc
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts/cluster-git-changes.py"


class GitManifestTests(unittest.TestCase):
    def test_staged_and_untracked_names_round_trip_without_commits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            names = ['space name.ts', 'é.ts', 'tab\tname.py', 'line\nbreak.md', '"quote".txt']
            for name in names:
                (root / name).write_text("content\n")
            subprocess.run(["git", "-C", str(root), "add", "--", *names[:3]], check=True)
            before = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain=v1", "-z"])
            result = subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            section = result.stdout.split("=== manifest json ===\n", 1)[1].split("\n=== rename pairs ===", 1)[0]
            records = json.loads(section)
            self.assertEqual({r["path"] for r in records}, set(names))
            after = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain=v1", "-z"])
            self.assertEqual(before, after)

    def test_binary_inventory_keeps_memory_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            with (root / "model.bin").open("wb") as handle:
                handle.truncate(32 * 1024 * 1024)
            spec = importlib.util.spec_from_file_location("manifest_check", SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            output = io.StringIO()
            tracemalloc.start()
            try:
                with patch.object(sys, "argv", [str(SCRIPT), str(root)]), contextlib.redirect_stdout(output):
                    self.assertEqual(module.main(), 0)
                _, peak = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            self.assertIn('binary  "model.bin"', output.getvalue())
            self.assertLess(peak, 5 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
