import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parents[1] / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


inventory = load('inventory-datasets')
edges = load('sample-edge-provenance')


class ProvenanceModeTests(unittest.TestCase):
    def invoke(self, repo, *args):
        output = io.StringIO()
        with mock.patch.object(sys, 'argv', ['inventory', str(repo), '--json', *args]), contextlib.redirect_stdout(output):
            code = inventory.main()
        return code, json.loads(output.getvalue())

    def test_json_emit_verify_and_missing_card_exit_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / 'data').mkdir()
            (repo / 'data/train.csv').write_text('x\n1\n2\n')
            code, records = self.invoke(repo, '--verify')
            self.assertEqual(code, 1)
            self.assertEqual(records[0]['status'], 'ORPHANED')
            code, records = self.invoke(repo, '--emit')
            self.assertEqual(code, 0)
            self.assertTrue((repo / records[0]['emitted_card']).is_file())
            with mock.patch.object(inventory, 'profile', side_effect=AssertionError('verify must only hash')):
                code, records = self.invoke(repo, '--verify')
            self.assertEqual(code, 0)
            self.assertEqual(records[0]['status'], 'OK')

    def test_human_card_without_hash_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / 'data/PROVENANCE').mkdir(parents=True)
            (repo / 'data/train.csv').write_text('x\n1\n')
            card = repo / 'data/PROVENANCE/data_train.csv.md'
            original = '# Human source notes\nDo not lose this research.\n'
            card.write_text(original)
            code, records = self.invoke(repo, '--emit')
            self.assertEqual(code, 0)
            self.assertEqual(card.read_text(), original)
            self.assertIn('preserved', records[0]['emit_note'])

    def test_edge_source_endpoint_is_not_provenance(self):
        report = edges.report_edges('edges', [{'source': 'A', 'target': 'B'}], None)
        self.assertEqual(len(report['missing']), 1)
        report = edges.report_edges('edges', [{'source': 'A', 'target': 'B', 'provenance_id': 'p1'}], {'p1'})
        self.assertFalse(report['missing'])
        self.assertFalse(report['unresolved'])

    def test_empty_provenance_store_still_requires_reference_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / 'sources.json').write_text('[]')
            ids = edges.collect_prov_ids(repo)
            self.assertEqual(ids, set())
            report = edges.report_edges('edges', [{'src': 'a', 'dst': 'b', 'provenance_id': 'missing'}], ids)
            self.assertEqual(len(report['unresolved']), 1)


if __name__ == '__main__':
    unittest.main()
