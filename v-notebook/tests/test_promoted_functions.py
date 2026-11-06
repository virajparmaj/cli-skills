import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('notebook_scan', Path(__file__).parents[1] / 'scripts/scan-notebooks.py')
scan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scan)


class NotebookPromotionTests(unittest.TestCase):
    def test_cell_function_is_found_inside_module_with_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / 'src').mkdir()
            function = 'def transform_values(values):\n    """Normalize reusable numeric values."""\n    return [float(value) / 100.0 for value in values]\n'
            (repo / 'src/features.py').write_text('import math\n\n' + function + '\nSCALE = 100\n')
            notebook = repo / 'research.ipynb'
            notebook.write_text(json.dumps({'cells': [{'cell_type': 'code', 'source': function}]}))
            report = scan.scan_notebook(notebook, repo, scan.src_code_hashes(repo), {})
            self.assertIn('src/features.py:transform_values', report['duplication'][0])

    def test_output_sizes_count_utf8_bytes(self):
        self.assertEqual(scan.output_bytes({'outputs': [{'text': '✅'}]}), len('✅'.encode('utf-8')))


if __name__ == '__main__':
    unittest.main()
