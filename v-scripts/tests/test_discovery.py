import subprocess
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / 'surface-map.sh'

class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="shell audit fixture ")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)

    def test_real_io_and_polling_markers_are_discovered(self):
        (self.repo / "src").mkdir()
        (self.repo / "src/hot.ts").write_text('setInterval(work, 1000);\nfs.readFile("file");\nconst data = JSON.parse(raw);\n')
        result = subprocess.run(["bash", str(SCRIPT), str(self.repo)], capture_output=True, text=True, check=True)
        for marker in ["setInterval", "readFile(", "JSON.parse"]:
            self.assertIn(marker, result.stdout)


if __name__ == "__main__":
    unittest.main()
