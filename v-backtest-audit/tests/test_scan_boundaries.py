import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import os

SCRIPT = Path(__file__).parents[1] / 'scripts/scan-leakage.py'
SPEC = importlib.util.spec_from_file_location('backtest_scan', SCRIPT)
scan = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = scan
SPEC.loader.exec_module(scan)


class ScanBoundaryTests(unittest.TestCase):
    def test_excluded_trees_are_not_visited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src/signal.py').write_text('x = frame.shift(-1)')
            (root / 'node_modules/package/deep').mkdir(parents=True)
            (root / 'node_modules/package/deep/vendor.py').write_text('ignored')
            visited = []
            real_scandir = os.scandir
            def tracked(path):
                visited.append(str(path))
                return real_scandir(path)
            with mock.patch.object(os, 'scandir', tracked):
                files = list(scan.iter_source_files(root))
            self.assertEqual(files, [(root / 'src/signal.py', False)])
            self.assertFalse(any('node_modules' in path for path in visited))

    def test_commented_out_leakage_is_not_active_code(self):
        report = scan.scan_text('signals.py', '# result = frame.shift(-1)\nresult = frame.shift(1)\n')
        self.assertFalse(report.hits)

    def test_plain_row_index_is_not_a_datetime_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.csv'
            path.write_text('value\n1\n2\n')
            self.assertIsNone(scan.dataset_date_span(path))


if __name__ == '__main__':
    unittest.main()
