"""An annualized Sharpe must not be compared directly to standard-error units."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / 'scripts/signal-inventory.py'


class SharpeThresholdTests(unittest.TestCase):
    def run_inventory(self, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            run = subprocess.run([sys.executable, str(SCRIPT), tmp,
                                  '--reported-sharpe', '2', '--trials', '20', *extra],
                                 text=True, capture_output=True, check=True)
            return run.stdout

    def test_missing_sample_length_produces_no_validity_verdict(self):
        output = self.run_inventory()
        self.assertIn('comparison UNVERIFIED', output)
        self.assertNotIn('CLEARS expected-max noise bar', output)
        self.assertNotIn('DOES NOT clear expected-max noise bar', output)

    def test_annualized_sharpe_is_converted_to_iid_z_units(self):
        output = self.run_inventory('--n-obs', '252', '--periods-per-year', '252')
        self.assertIn('iid z=2.000', output)
        long_sample = self.run_inventory('--n-obs', '1008', '--periods-per-year', '252')
        self.assertIn('iid z=4.000', long_sample)


if __name__ == '__main__':
    unittest.main()
