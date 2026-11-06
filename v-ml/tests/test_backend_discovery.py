import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('ml_map', Path(__file__).parents[1] / 'scripts/map_ml_repo.py')
mapper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mapper)


class BackendDiscoveryTests(unittest.TestCase):
    def test_standard_app_layout_is_recognized_and_venv_is_pruned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'app').mkdir()
            (root / 'app/main.py').write_text('app = FastAPI()\n')
            (root / 'app/.venv/site-packages').mkdir(parents=True)
            (root / 'app/.venv/site-packages/vendor.py').write_text('ignored = True')
            self.assertEqual(mapper.infer_topology(root), 'backend-only')
            files = mapper.glob_many(root, mapper.BACKEND_PATTERNS)
            self.assertEqual(files, [root / 'app/main.py'])

    def test_python_src_package_is_not_labeled_frontend_demo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src/metrics.py').write_text('def score(): return 1')
            self.assertTrue(mapper.infer_topology(root).startswith('unknown'))


if __name__ == '__main__':
    unittest.main()
