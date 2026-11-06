import json
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest


SCRIPTS = Path(__file__).parents[1] / "scripts"


class ScaffoldTests(unittest.TestCase):
    def test_web_dependencies_and_publishable_key_are_coherent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "web"
            subprocess.run(["bash", str(SCRIPTS / "scaffold-web.sh"), str(root), "--supabase"], check=True, capture_output=True)
            package = json.loads((root / "package.json").read_text())
            self.assertIn("clsx", package["dependencies"])
            self.assertIn("tailwind-merge", package["dependencies"])
            self.assertIn("@supabase/supabase-js", package["dependencies"])
            self.assertIn("eslint", package["devDependencies"])
            self.assertTrue((root / "eslint.config.js").is_file())
            self.assertIn("VITE_SUPABASE_PUBLISHABLE_KEY", (root / ".env.example").read_text())
            self.assertNotIn("sb_secret_", (root / ".env.example").read_text())
            original = root / "src/App.tsx"
            original.write_text("user's application\n")
            subprocess.run(["bash", str(SCRIPTS / "scaffold-web.sh"), str(root)], check=True, capture_output=True)
            self.assertEqual(original.read_text(), "user's application\n")

    def test_python_keyword_name_and_dev_test_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "python"
            subprocess.run(["bash", str(SCRIPTS / "scaffold-py.sh"), str(root), "class", "--no-venv"], check=True, capture_output=True)
            project = tomllib.loads((root / "pyproject.toml").read_text())
            self.assertEqual(project["project"]["name"], "pkg_class")
            self.assertIn("pytest", project["project"]["optional-dependencies"]["dev"])
            self.assertTrue((root / "src/pkg_class/data.py").is_file())
            notebook = json.loads((root / "notebooks/01_explore.ipynb").read_text())
            self.assertTrue(all(not cell.get("outputs") for cell in notebook["cells"]))

    def test_invalid_explicit_npm_name_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "should-not-exist"
            result = subprocess.run(["bash", str(SCRIPTS / "scaffold-web.sh"), str(root), "invalid\"name"], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()
