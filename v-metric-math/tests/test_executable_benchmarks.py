import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('metric_harness', Path(__file__).parents[1] / 'scripts/run-metric-benchmarks.py')
harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harness)


class ExecutableBenchmarkTests(unittest.TestCase):
    def test_dataclass_module_is_imported_once_and_emitted_tests_recompute(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            module = repo / 'metrics.py'
            module.write_text('''from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
counter = Path(__file__).with_name('imports.txt')
with counter.open('a') as fh: fh.write('imported\\n')
@dataclass
class Config:
    scale: float = 1.0

def brier_score(y_true, y_prob):
    return sum((float(y)-float(p))**2 for y,p in zip(y_true,y_prob))/len(y_true)
''')
            rows = harness.run(repo, module)
            brier = [row for row in rows if row['metric'] == 'brier']
            self.assertEqual([row['status'] for row in brier], ['PASS', 'PASS'])
            self.assertEqual((repo / 'imports.txt').read_text().count('imported'), 1)
            output = repo / 'tests/test_benchmarks.py'
            harness.emit_pytest(rows, output, repo)
            self.assertNotIn('pytest.skip', output.read_text())
            run = subprocess.run([sys.executable, '-m', 'pytest', '-q', str(output)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            module.write_text(module.read_text().replace('return sum(', 'return 2 * sum('))
            run = subprocess.run([sys.executable, '-m', 'pytest', '-q', str(output)], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0, 'emitted test must detect changed metric output')
            with self.assertRaises(FileExistsError):
                harness.emit_pytest(rows, output, repo)

    def test_scalar_and_keyword_only_inputs(self):
        observed, _ = harness.call_with_fixture(lambda *, mu, sigma, alpha: mu + sigma + alpha,
            {'input': {'returns_are_standard_normal_theoretical': True, 'mu': 0, 'sigma': 1, 'alpha': .95}})
        self.assertEqual(observed, 1.95)
        def ece(y_true, y_prob, *, n_bins):
            self.assertEqual(n_bins, 2)
            return .25
        observed, _ = harness.call_with_fixture(ece, {'input': {'y_true': [0, 1], 'y_prob': [.2, .8], 'n_bins': 2}})
        self.assertEqual(observed, .25)


if __name__ == '__main__':
    unittest.main()
