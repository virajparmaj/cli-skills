"""Regressions for fold-local preprocessing and chronological input ordering."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import TimeSeriesSplit, cross_validate
except ImportError:
    np = pd = None

SPEC = importlib.util.spec_from_file_location(
    'baseline_harness', Path(__file__).parents[1] / 'scripts/run-baselines.py'
)
harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harness)


@unittest.skipIf(pd is None, 'requires pandas, numpy, and scikit-learn')
class BaselineProtocolTests(unittest.TestCase):
    def test_float_classes_and_explicit_integer_regression(self):
        from sklearn.dummy import DummyClassifier, DummyRegressor
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'train.csv'
            pd.DataFrame({'x': range(30), 'target': [0.0, 1.0] * 15}).to_csv(data, index=False)
            with mock.patch.object(harness, 'build_models', lambda task: {'dummy': DummyClassifier() if task == 'classification' else DummyRegressor()}):
                task, scoring, _, results = harness.run(data, 'target', None, 3)
                self.assertEqual((task, scoring), ('classification', 'roc_auc'))
                self.assertIn('dummy', results)
                task, scoring, _, results = harness.run(data, 'target', None, 3, task='regression')
                self.assertEqual((task, scoring), ('regression', 'r2'))
                self.assertIn('dummy', results)

    def test_temporal_gap_is_in_the_actual_splitter(self):
        from sklearn.dummy import DummyRegressor
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'train.csv'
            pd.DataFrame({'date': pd.date_range('2024-01-01', periods=30), 'x': range(30), 'target': range(30)}).to_csv(data, index=False)
            actual_sizes = []
            from sklearn.model_selection import cross_val_score as actual_cv
            def checked_cv(model, X, y, *, cv, **kwargs):
                for train, test in cv.split(X, y):
                    actual_sizes.append(test[0] - train[-1] - 1)
                return actual_cv(model, X, y, cv=cv, **kwargs)
            with mock.patch.object(harness, 'build_models', lambda task: {'dummy': DummyRegressor()}), mock.patch('sklearn.model_selection.cross_val_score', checked_cv):
                harness.run(data, 'target', 'date', 3, task='regression', gap=2)
            self.assertEqual(actual_sizes, [2, 2, 2])

    def test_imputation_learns_only_from_each_training_fold(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'train.csv'
            pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=9),
                'x': [0, np.nan, 2, 1000, 2000, 3000, 4000, 5000, 6000],
                'target': list(range(9)),
            }).to_csv(data, index=False)
            X, y, temporal = harness.load_xy(data, 'target', 'date')
            self.assertTrue(temporal)
            self.assertTrue(X['x'].isna().any(), 'loading must not learn global medians')
            model = harness.build_models('regression')['dummy']
            fitted = cross_validate(model, X, y, cv=TimeSeriesSplit(2),
                                    return_estimator=True)
            first_median = fitted['estimator'][0].named_steps['impute'].statistics_[0]
            self.assertEqual(first_median, 1.0)  # first fold is [0, missing, 2]

    def test_datetime_sort_uses_parsed_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'train.csv'
            data.write_text('date,x,target\n11/01/2024,3,30\n2/01/2024,1,10\n9/01/2024,2,20\n')
            X, y, temporal = harness.load_xy(data, 'target', 'date')
            self.assertTrue(temporal)
            self.assertEqual(list(y), [10, 20, 30])
            self.assertEqual(list(X.columns), ['x'])

    def test_explicit_missing_datetime_column_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'train.csv'
            data.write_text('x,target\n1,0\n2,1\n')
            with self.assertRaisesRegex(ValueError, 'datetime column'):
                harness.load_xy(data, 'target', 'missing')


if __name__ == '__main__':
    unittest.main()
