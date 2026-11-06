import contextlib
import importlib.util
import io
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('parquet_facts', Path(__file__).parents[1] / 'scripts/parquet-facts.py')
facts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(facts)


class SchemaCoverageTests(unittest.TestCase):
    def test_unavailable_schemas_are_not_reported_as_matching(self):
        output = io.StringIO()
        root = Path('/tmp')
        groups = {'events': [(root / 'a.parquet', '', []), (root / 'b.parquet', '', [])]}
        with contextlib.redirect_stdout(output):
            facts.print_drift(groups, root)
        self.assertIn('UNVERIFIED schema for 2', output.getvalue())
        self.assertNotIn('OK', output.getvalue())
        self.assertNotIn('single schema', output.getvalue())


if __name__ == '__main__':
    unittest.main()
