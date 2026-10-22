#!/usr/bin/env python3
"""Prepare the unchanged EDR1 host logic with an explicit new firmware build pin."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = "cb3a147719850a0dc4a4797b401b606ea14c6571"
BUILD = "ROUTEB-KEYBOARD-CONTROL-20261022-v1"
KIT = "evilduck-keyboard-control-led-host-v1"
FILES = ("native.c", "engine.c", "engine.h", "workflow.py", "device.py", "run-mac.sh", "FIXED-MESSAGE.json")


def prepare():
    files, pins = {}, []
    for name in FILES:
        relative = "host_tests/led_return/mac_fixed_message/" + name
        old = subprocess.check_output(["git", "show", BASE+":"+relative], cwd=ROOT)
        assert (ROOT / relative).read_bytes() == old, "Historical host source changed"
        data = old
        if name == "device.py":
            before = b'BUILD = "CAPS-STOP-TRACE-20261019-v1"'
            assert data.count(before) == 1
            data = data.replace(before, ('BUILD = "'+BUILD+'"').encode())
        pins.append(dict(file=name, before_sha256=hashlib.sha256(old).hexdigest(),
                         after_sha256=hashlib.sha256(data).hexdigest(),
                         adaptation="expected build identifier only" if name == "device.py" else "byte identical"))
        files[name] = data
    files["README-MAC.md"] = ("""# Optional fixed-message host kit for the keyboard-control candidate

This is the passed fixed-message workflow with only its expected firmware build
identifier changed to `ROUTEB-KEYBOARD-CONTROL-20261022-v1`. It intentionally
refuses the previous installed firmware; the previous kit remains available for
that image. No EDR1 framing, message, CRC, timing, authentication, capability probe,
cleanup or successful-result validation changed. Native execution of this build
binding remains pending; the previous configuration's physical PASS is historical.

Do not repeat the full LED test automatically for an unrelated keyboard change.
This optional kit is supplied so the exact new build pin will not prevent a future
separately owner-chosen regression check. It does not install firmware.

After unzipping into Downloads, the command is:

```bash
bash "$HOME/Downloads/evilduck-keyboard-control-led-host-v1/run-mac.sh"
```

Use macOS10.13.6, existing Apple CLT, Python3.8+, and the existing dashboard Wi-Fi
connection on the Mac and iPhone. Keep all scripts idle. The launcher prints actual
USB303A:1001 serials; choose the exact unique usable interface. Enter the existing
local dashboard address and the hidden Web UI password. Never put a password in
arguments or evidence. Type PROBE for the four device-confirmed Gray-cycle steps,
then SEND for one explicitly armed fixed 17-byte message. No automatic retry occurs.
After the authenticated exact-message result, use iPhone Observe LEDs / refresh and
View test data, preserve a screenshot, and only then type VIEWED. Keep the Desktop
receipt folder, Terminal output, host/build metadata and screenshot from that run.

Only EVILDUCK TEST 123 is sent. Ctrl-C triggers bounded independent best-effort
Caps/Num output restoration; it does not prove global Caps restoration. Overall
limit600 seconds; per-step evidence4seconds; sender90-second soft/95-second
watchdog; direct local HTTP2-second deadline. OS stalls/unplug/forced exits can
prevent cleanup. Missing capability, changed session, stale/wrong probe evidence,
new receiver errors, historical completion or wrong message cannot pass.

The original detailed workflow instructions are preserved in SOURCE-README.md.
Their old firmware identity and old folder name describe the historical kit;
use this README's build identity and command for this explicitly bound variant.
No arbitrary message, capture, global Caps correction, firmware or installer is
included. Windows behavior is unverified.
""").encode()
    files["SOURCE-README.md"] = subprocess.check_output(["git", "show", BASE+":host_tests/led_return/mac_fixed_message/README-MAC.md"], cwd=ROOT)
    files["SOURCE-MANIFEST.json"] = (json.dumps(dict(baseline=BASE, expected_build=BUILD,
        source_adaptations=pins, firmware_included=False, native_macos_execution="PENDING_OWNER",
        original_physical_result="OWNER_ACCEPTED_FOR_PREVIOUS_BUILD_ONLY"), indent=2)+"\n").encode()
    files["SHA256SUMS.txt"] = "".join(hashlib.sha256(data).hexdigest()+"  "+name+"\n" for name,data in sorted(files.items())).encode()
    return files


def main():
    p = argparse.ArgumentParser(); p.add_argument("--archive", type=Path, required=True); a = p.parse_args()
    files = prepare()
    with zipfile.ZipFile(a.archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(KIT+"/"+name, (2026,10,22,0,0,0)); info.create_system=3
            info.external_attr=0o100644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    data=a.archive.read_bytes()
    print(json.dumps(dict(file=a.archive.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
        expected_build=BUILD,changed_algorithm_bytes=0,adaptation="device.BUILD only; new profile README/manifest"),indent=2))


if __name__ == "__main__": main()
