"""Split checks must hash observations and must not report unreadable data clean."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location(
    'dataset_profile', Path(__file__).parents[1] / 'scripts/profile-dataset.py'
)
profile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile)


class SplitOverlapTests(unittest.TestCase):
    def test_column_order_is_ignored_but_schema_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            train, test = Path(tmp) / 'train.csv', Path(tmp) / 'test.csv'
            train.write_text('feature,target\n1,0\n2,1\n')
            test.write_text('target,feature\n1,2\n')
            for mode in ([False, True] if profile.HAVE_PANDAS else [False]):
                with self.subTest(pandas=mode), mock.patch.object(profile, 'HAVE_PANDAS', mode):
                    self.assertEqual(len(profile.row_hashes(train) & profile.row_hashes(test)), 1)
            test.write_text('other,outcome\n1,0\n')
            self.assertFalse(profile.row_hashes(train) & profile.row_hashes(test))

    def test_shared_csv_header_is_not_an_overlapping_observation(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(profile, 'HAVE_PANDAS', False):
            train, test = Path(tmp) / 'train.csv', Path(tmp) / 'test.csv'
            train.write_text('feature,target\n1,0\n2,1\n')
            test.write_text('feature,target\n3,0\n4,1\n')
            self.assertFalse(profile.row_hashes(train) & profile.row_hashes(test))
            test.write_text('feature,target\n2,1\n4,1\n')
            self.assertEqual(len(profile.row_hashes(train) & profile.row_hashes(test)), 1)

    def test_unavailable_parquet_loader_is_not_an_empty_clean_split(self):
        with mock.patch.object(profile, 'HAVE_PANDAS', False):
            with self.assertRaisesRegex(ValueError, 'require pandas'):
                profile.row_hashes(Path('unreadable.parquet'))

    def test_failed_pandas_read_remains_unverified(self):
        with mock.patch.object(profile, 'HAVE_PANDAS', True):
            with mock.patch.object(profile, '_read', side_effect=OSError('unreadable')):
                with self.assertRaisesRegex(ValueError, 'cannot read split file'):
                    profile.row_hashes(Path('unreadable.csv'))


if __name__ == '__main__':
    unittest.main()
