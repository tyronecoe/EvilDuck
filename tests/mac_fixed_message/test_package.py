"""Public source-only ZIP integrity and non-Mac refusal; no host I/O device calls."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
ZIP = ROOT / "downloads/evilduck-macos-fixed-message-v1.zip"
PREFIX = "evilduck-macos-fixed-message-v1/"


class PackageTests(unittest.TestCase):
    def test_allowlisted_source_only_package_and_hashes(self):
        expected = {"README-MAC.md", "run-mac.sh", "native.c", "engine.c", "engine.h",
                    "workflow.py", "device.py", "FIXED-MESSAGE.json", "CHANGE-AND-TEST-REPORT.md",
                    "OFFLINE-RESULTS.json", "SOURCE-MANIFEST.json", "SHA256SUMS.txt"}
        with ZipFile(ZIP) as z:
            self.assertEqual(set(z.namelist()), {PREFIX + name for name in expected})
            self.assertEqual(z.testzip(), None)
            checksums = z.read(PREFIX + "SHA256SUMS.txt").decode("ascii").splitlines()
            self.assertEqual(len(checksums), len(expected)-1)
            for row in checksums:
                digest, name = row.split("  ")
                self.assertEqual(hashlib.sha256(z.read(PREFIX + name)).hexdigest(), digest)
            manifest = json.loads(z.read(PREFIX + "SOURCE-MANIFEST.json"))
            self.assertFalse(manifest["contains_firmware"])
            for item in manifest["files"]:
                data = z.read(PREFIX + item["file"])
                self.assertEqual(len(data), item["size"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), item["sha256"])
            fixed = json.loads(z.read(PREFIX + "FIXED-MESSAGE.json"))
            self.assertEqual(bytes.fromhex(fixed["frame_hex"])[6:23], b"EVILDUCK TEST 123")
    def test_package_sources_equal_reviewed_tree(self):
        with ZipFile(ZIP) as z:
            for name in ("README-MAC.md", "run-mac.sh", "native.c", "engine.c", "engine.h",
                         "workflow.py", "device.py", "FIXED-MESSAGE.json"):
                self.assertEqual(z.read(PREFIX + name), (ROOT / "host_tests/led_return/mac_fixed_message" / name).read_bytes())
            self.assertEqual(z.read(PREFIX + "CHANGE-AND-TEST-REPORT.md"), (ROOT / "docs/mac-fixed-message-report.md").read_bytes())
            self.assertEqual(z.read(PREFIX + "OFFLINE-RESULTS.json"), (ROOT / "docs/mac-fixed-message-results.json").read_bytes())
    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux refusal check only; never run native launcher on a Mac during tests")
    def test_linux_launcher_stops_before_compilation_or_device_work(self):
        with tempfile.TemporaryDirectory() as directory:
            with ZipFile(ZIP) as z: z.extractall(directory)
            launcher = Path(directory) / PREFIX / "run-mac.sh"
            result = subprocess.run(["bash", str(launcher)], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires native macOS", result.stderr)
            self.assertNotIn("Compiling", result.stdout)


if __name__ == "__main__": unittest.main(verbosity=2)
