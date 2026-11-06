"""Known-answer drawdown and invalid-input regressions for the report helper."""
import importlib.util
import math
from pathlib import Path
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    'report_metrics', Path(__file__).parents[1] / 'scripts/compute-metrics.py'
)
metrics = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = metrics
SPEC.loader.exec_module(metrics)


class ReportMetricTests(unittest.TestCase):
    def test_percent_units_are_identical_in_both_loaders(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'returns.csv'
            path.write_text('date,return\n2024-01-01,1%\n2024-01-02,-2\n')
            series = metrics.load_with_stdlib(path, None, None, None, True)
            self.assertEqual(series.returns, [.01, -.02])
            if metrics._HAVE_PANDAS:
                pandas_series = metrics.load_with_pandas(path, None, None, None, True)
                self.assertEqual(series.returns, pandas_series.returns)

    def test_missing_returns_are_not_silently_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'returns.csv'
            path.write_text('date,return\n2024-01-01,0.1\n2024-01-02,\n')
            with self.assertRaisesRegex(ValueError, 'handle missing observations explicitly'):
                metrics.load_with_stdlib(path, None, None, None, False)
            if metrics._HAVE_PANDAS:
                with self.assertRaisesRegex(ValueError, 'handle missing observations explicitly'):
                    metrics.load_with_pandas(path, None, None, None, False)

    def compute(self, returns):
        return metrics.compute_metrics(
            metrics.Series([str(i) for i in range(len(returns))], returns), 12, 0
        )

    def test_first_period_loss_is_underwater_from_initial_capital(self):
        result = self.compute([-0.1, 0.05])
        self.assertAlmostEqual(result['max_drawdown'], -0.1)
        self.assertEqual(result['max_drawdown_peak_date'], 'initial capital')
        self.assertEqual(result['max_drawdown_underwater_periods'], 2)

    def test_later_peak_and_trough_are_preserved(self):
        result = self.compute([0.1, -0.5, 1.0])
        self.assertAlmostEqual(result['max_drawdown'], -0.5)
        self.assertEqual(result['max_drawdown_peak_date'], '0')
        self.assertEqual(result['max_drawdown_trough_date'], '1')

    def test_total_loss_has_negative_one_cagr(self):
        result = self.compute([-1.0])
        self.assertEqual(result['cagr'], -1.0)
        self.assertEqual(result['max_drawdown'], -1.0)

    def test_invalid_returns_and_frequency_are_rejected(self):
        for returns in ([math.nan], [math.inf], [-1.1]):
            with self.subTest(returns=returns), self.assertRaises(ValueError):
                self.compute(returns)
        for periods in (0, -1, math.nan, math.inf):
            with self.subTest(periods=periods), self.assertRaises(ValueError):
                metrics.compute_metrics(metrics.Series(['0'], [0.1]), periods, 0)


if __name__ == '__main__':
    unittest.main()
