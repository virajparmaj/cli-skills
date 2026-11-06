import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('regression_inventory', Path(__file__).parents[1] / 'scripts/inventory-model-fits.py')
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


class RegressionCallTests(unittest.TestCase):
    def test_imports_without_calls_are_not_models(self):
        self.assertIsNone(inventory.analyze(Path('analysis.py'), 'from statsmodels.api import OLS\nfrom scipy.stats import ttest_ind\n'))

    def test_formula_api_and_notebook_path_are_preserved(self):
        path = Path('research/credit/model.ipynb')
        report = inventory.analyze(path, 'import statsmodels.formula.api as smf\nmodel = smf.ols("y ~ x", data=df).fit()\n')
        self.assertEqual(report['models'], ['OLS'])
        self.assertEqual(report['file'], str(path))
        self.assertEqual(report['model_sites'][0]['line'], 2)


if __name__ == '__main__':
    unittest.main()
