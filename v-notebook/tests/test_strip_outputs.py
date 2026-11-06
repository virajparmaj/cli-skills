import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("notebook_strip", Path(__file__).parents[1] / "scripts/strip-outputs.py")
strip = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(strip)


class StripOutputsTests(unittest.TestCase):
    def test_preserves_content_metadata_and_file_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "with spaces.ipynb"
            notebook = {"cells": [
                {"cell_type": "markdown", "source": ["# Analysis"], "metadata": {"tag": "keep"}},
                {"cell_type": "code", "source": ["print('é')"], "metadata": {}, "id": "abc",
                 "execution_count": 3, "outputs": [{"output_type": "stream", "text": ["é"]}]}
            ], "metadata": {"kernelspec": {"name": "python3"}}, "nbformat": 4, "nbformat_minor": 5}
            path.write_text(json.dumps(notebook))
            path.chmod(0o640)
            self.assertTrue(strip.strip_outputs(path))
            expected = json.loads(json.dumps(notebook))
            expected["cells"][1].update(outputs=[], execution_count=None)
            self.assertEqual(json.loads(path.read_text()), expected)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])
            before = path.read_bytes()
            self.assertFalse(strip.strip_outputs(path))
            self.assertEqual(path.read_bytes(), before)

    def test_invalid_json_and_cells_are_never_truncated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.ipynb"
            for raw in ('{"cells": [', '{"cells": [42]}', '{"other": []}'):
                path.write_text(raw)
                with self.subTest(raw=raw), self.assertRaises(ValueError):
                    strip.strip_outputs(path)
                self.assertEqual(path.read_text(), raw)


if __name__ == "__main__":
    unittest.main()
