import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts/phase-status.py"
SPEC = importlib.util.spec_from_file_location("phase_inventory", SCRIPT)
phase = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(phase)


class PhaseInventoryTests(unittest.TestCase):
    def test_paths_with_spaces_and_line_suffixes(self):
        found = phase.references("Use `src/my file.py:42`, [design](../src/my%20file.py), and `missing.ts`.")
        self.assertIn(("src/my file.py", False), found)
        self.assertIn(("../src/my file.py", True), found)
        self.assertIn(("missing.ts", False), found)

    def test_wrong_directory_is_only_a_basename_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/existing.py").write_text("pass\n")
            (root / "phase-01.md").write_text("status: pending\n- [ ] Implement `wrong/existing.py`\n")
            ignored = root / "node_modules/dep"
            ignored.mkdir(parents=True)
            (ignored / "phase-99.md").write_text("status: done\n")
            result = subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("BASENAME wrong/existing.py", result.stdout)
            self.assertNotIn("EXISTS   wrong/existing.py", result.stdout)
            self.assertNotIn("phase-99", result.stdout)


if __name__ == "__main__":
    unittest.main()
