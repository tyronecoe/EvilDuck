import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import host_workflow as h
sys.path.insert(0,str(ROOT/"tests/mac_fixed_message"))
from test_device import snapshot


class HostProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files=h.prepare()
        cls.device={"__name__":"new_build_device"}
        exec(compile(cls.files["device.py"],"new_build_device.py","exec"),cls.device)
    def test_only_expected_build_source_changes(self):
        records=json.loads(self.files["SOURCE-MANIFEST.json"])["source_adaptations"]
        self.assertEqual([r["file"] for r in records if r["before_sha256"]!=r["after_sha256"]],["device.py"])
        old=(ROOT/"host_tests/led_return/mac_fixed_message/device.py").read_bytes()
        self.assertEqual(self.files["device.py"].replace(h.BUILD.encode(),b"CAPS-STOP-TRACE-20261019-v1"),old)
    def test_explicit_new_build_accepted(self):
        self.assertEqual(self.device["validate_snapshot"](snapshot(buildId=h.BUILD))["buildId"],h.BUILD)
    def test_old_build_still_refused(self):
        with self.assertRaises(self.device["DeviceError"]) as caught: self.device["validate_snapshot"](snapshot())
        self.assertEqual(caught.exception.code,"BUILD_MISMATCH")
    def test_all_kit_checksums_match(self):
        for line in self.files["SHA256SUMS.txt"].decode().splitlines():
            digest,name=line.split("  ");self.assertEqual(hashlib.sha256(self.files[name]).hexdigest(),digest)
    def test_protocol_constant_remains_fixed(self):
        v=json.loads(self.files["FIXED-MESSAGE.json"])
        self.assertEqual(v["frame_hex"],"0045445231114556494c4455434b205445535420313233d6cc")
        self.assertEqual(v["payload_bytes"],17)
        self.assertFalse(v["arbitrary_input_supported"])


if __name__ == "__main__": unittest.main(verbosity=2)
