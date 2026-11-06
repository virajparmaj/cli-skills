import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('timeseries_scan', Path(__file__).parents[1] / 'scripts/find-split-leakage.py')
scan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scan)


class NotebookPipelineTests(unittest.TestCase):
    def test_split_and_fit_across_cells_remain_one_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'research.ipynb'
            path.write_text(json.dumps({'cells': [
                {'cell_type': 'code', 'source': '%matplotlib inline\ndf.index = pd.to_datetime(df.index)'},
                {'cell_type': 'code', 'source': 'X = scaler.fit_transform(df)'},
                {'cell_type': 'code', 'source': 'X_train, X_test = train_test_split(X)'},
            ]}))
            sources = list(scan.iter_sources(root))
            self.assertEqual(len(sources), 1)
            report = scan.analyze(*sources[0])
            self.assertTrue(report['datetime_index_hint'])
            self.assertEqual(len(report['fits_before_split']), 1)
            self.assertTrue(report['fits_before_split'][0]['location'].endswith('#cell1:1'))
            self.assertTrue(report['split_calls'][0]['location'].endswith('#cell2:1'))
            self.assertEqual(len(scan.summarize([report])['high_signal_flags']), 2)

    def test_keyword_negative_shift_is_detected_without_claiming_regime_class_is_smoothed(self):
        report = scan.analyze(Path('pipeline.py'), 'feature = df.shift(periods=-1)\nmodel = MarkovRegression(y)\n')
        self.assertEqual(len(report['forward_windows']), 1)
        flags = scan.summarize([report])['high_signal_flags']
        self.assertEqual(len(flags), 1)
        self.assertNotIn('smoothing', flags[0])

    def test_syntax_failure_is_disclosed(self):
        report = scan.analyze(Path('pipeline.py'), 'def unfinished(')
        self.assertIn('parse_error', report)
        self.assertEqual(report['fits_before_split'], [])


if __name__ == '__main__':
    unittest.main()
