import subprocess
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / 'discover-extension-surface.sh'

class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="shell audit fixture ")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)

    def test_secret_discovery_prints_locations_without_token_values(self):
        (self.repo / "manifest.json").write_text('{"manifest_version":3,"name":"Fixture","version":"1.0.0"}')
        fake = "sk_live_" + "X" * 30
        (self.repo / "worker.js").write_text(f'const api_key = "{fake}";')
        result = subprocess.run(["bash", str(SCRIPT), str(self.repo)], capture_output=True, text=True, check=True)
        self.assertIn("worker.js", result.stdout)
        self.assertNotIn(fake, result.stdout)


if __name__ == "__main__":
    unittest.main()
