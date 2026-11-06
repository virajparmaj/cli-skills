from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / 'scripts/venv-doctor.sh'


class ProjectEnvironmentTests(unittest.TestCase):
    def run_doctor(self, root, no_site=False):
        launch = root / '.venv/bin/python'
        launch.parent.mkdir(parents=True)
        launch.write_text('#!/bin/sh\nexec ' + shlex.quote(sys.executable) + (' -S' if no_site else '') + ' "$@"\n')
        launch.chmod(0o755)
        return subprocess.run(['bash', str(SCRIPT), str(root)], text=True, capture_output=True, timeout=45, check=True).stdout

    def test_missing_optional_ml_libraries_do_not_require_installing_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = self.run_doctor(Path(tmp), no_site=True)
            self.assertIn('xgboost not installed; no libomp repair inferred', output)
            self.assertNotIn('FAIL', output)
            self.assertNotIn('brew libomp: NOT installed', output)

    def test_project_requires_python_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'pyproject.toml').write_text('[project]\nname = "example"\nrequires-python = ">=99"\n')
            output = self.run_doctor(root)
            self.assertIn('requires-python >=99: FAIL', output)


if __name__ == '__main__':
    unittest.main()
