from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts/discover-notes-drift.sh"


class NotesDiscoveryTests(unittest.TestCase):
    def test_native_bash_handles_changed_paths_without_namerefs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "src/pages").mkdir(parents=True)
            (root / "src/pages/my page.tsx").write_text("export const Page = () => null;\n")
            result = subprocess.run(["/bin/bash", str(SCRIPT), str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("08_pages_and_routes.md", result.stdout)
            self.assertIn("00_overview.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
