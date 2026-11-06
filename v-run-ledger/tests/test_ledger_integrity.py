import csv
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / 'scripts/log-run.py'
SPEC = importlib.util.spec_from_file_location('run_ledger', SCRIPT)
ledger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger)


class LedgerIntegrityTests(unittest.TestCase):
    def invoke(self, root, *extra):
        return subprocess.run([sys.executable, str(SCRIPT), str(root), '--model', 'Ridge', '--metric', 'r2', '--mean', '.5', *extra], capture_output=True, text=True)

    def test_repo_relative_data_path_is_hashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'train.csv').write_text('x,y\n1,2\n')
            run = self.invoke(root, '--data', 'train.csv')
            self.assertEqual(run.returncode, 0, run.stderr)
            with (root / 'experiments/runs.csv').open() as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row['data_hash'], hashlib.sha256((root / 'train.csv').read_bytes()).hexdigest()[:16])

    def test_invalid_params_or_metrics_do_not_create_ledger(self):
        for flags in (['--params', '{bad'], ['--mean', 'nan'], ['--std', '-1'], ['--data', 'missing.csv']):
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as tmp:
                run = self.invoke(tmp, *flags)
                self.assertNotEqual(run.returncode, 0)
                self.assertFalse((Path(tmp) / 'experiments/runs.csv').exists())

    def test_incompatible_existing_schema_is_not_appended_to(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'experiments').mkdir()
            path = root / 'experiments/runs.csv'
            path.write_text('custom,columns\nkeep,these\n')
            before = path.read_bytes()
            self.assertNotEqual(self.invoke(root).returncode, 0)
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
