#!/usr/bin/env python3
"""Reproducible, allowlisted source-only kit; never reads owner evidence or firmware."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
KIT = "evilduck-macos-fixed-message-v1"
SOURCE = ROOT / "host_tests/led_return/mac_fixed_message"
BASELINE = "0803937b9b552fe4b6e6cb6d1dd60f80f098449c"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    files = {name: (SOURCE / name).read_bytes() for name in
             ("README-MAC.md", "run-mac.sh", "native.c", "engine.c", "engine.h",
              "workflow.py", "device.py", "FIXED-MESSAGE.json")}
    files["CHANGE-AND-TEST-REPORT.md"] = (ROOT / "docs/mac-fixed-message-report.md").read_bytes()
    files["OFFLINE-RESULTS.json"] = (ROOT / "docs/mac-fixed-message-results.json").read_bytes()
    entries = [dict(file=name, size=len(data), sha256=hashlib.sha256(data).hexdigest())
               for name, data in sorted(files.items())]
    files["SOURCE-MANIFEST.json"] = (json.dumps(dict(
        format="evilduck-fixed-message-source-kit-v1", baseline=BASELINE,
        contains_firmware=False, native_apple_compile="PENDING_OWNER",
        physical_delivery="PENDING_OWNER", files=entries), indent=2) + "\n").encode()
    files["SHA256SUMS.txt"] = "".join("{}  {}\n".format(hashlib.sha256(data).hexdigest(), name)
                                     for name, data in sorted(files.items())).encode("ascii")
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(KIT + "/" + name, (2026, 10, 22, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100755 if name == "run-mac.sh" else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    data = memory.getvalue()
    with args.output.open("xb") as out:
        out.write(data)
    print(json.dumps(dict(filename=args.output.name, size=len(data), sha256=hashlib.sha256(data).hexdigest(),
                          entries=sorted(KIT + "/" + name for name in files)), indent=2))


if __name__ == "__main__": main()
