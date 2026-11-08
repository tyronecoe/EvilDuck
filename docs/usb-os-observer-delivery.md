# USB enumeration observer: review delivery

**CAPTURE ONLY — NOT INSTALLED — NO OS CLASSIFIER OR VALIDATED HIGH SIERRA RULE.**

The one authorized observer stage is built, tested and published. It records a
bounded USB metadata prefix for later analysis. `UNKNOWN / NO_VALIDATED_RULE` is
an explicit capture-stage label, not a completed detector. A final detection and
branching release still requires independent justification and held-out validation.

[Download the commit-pinned High Sierra review ZIP](https://raw.githubusercontent.com/tyronecoe/EvilDuck/6dba2b53885f7aaceddf2c779938e27fabb5db03/downloads/evilduck-routeb-usb-enum-observer-h1-macos-review-v1.zip).
Downloaded bytes, CRC, candidate application, nested working return and older
rollback identities were verified. Offline preflight on the published extraction
passed. See the [publication receipt](usb-os-observer-publication-verification.json).

| Identity | Exact value |
| --- | --- |
| Branch | `routeb-usb-enum-observer-h1-review-v1` |
| Build ID | `ROUTEB-USB-ENUM-OBSERVER-H1-v1` |
| Firmware/verifier checkpoint | `7472de1e0edf123a9fcdf9d1d4feb1b38250280e` |
| Package checkpoint | `20f08464d3b51786d2a3773a7aef25bee9cd2ad5` |
| ZIP publication commit | `6dba2b53885f7aaceddf2c779938e27fabb5db03` |
| Application | 1,445,008 bytes; SHA-256 `e60af8a1b53ab2ba9e7c79b4ff821719ddd06a0a55384dd987288c4189aed6a9` |
| ELF | SHA-256 `e63663295f250868e006e3273c718e84cb68f246ae58b7f47c86835505898377` |
| ZIP | 5,492,049 bytes, 62 members; SHA-256 `a93215b2c23b6937e867b6f988b30f3924be37a2f599fe7b3e805ae51030719c` |

[Artifact identities](usb-os-observer-artifacts.json),
[actual build/source inventory](usb-os-observer-build.json),
[complete release verification](usb-os-observer-release-verification.json),
[test receipts and results](usb-os-observer-results.json), and
[package verification](usb-os-observer-package-verification.json) make the
candidate reviewable. The build binds 113 committed inputs, with no
post-compilation verifier delta.

The actual composed Route B has 201 files. Relative to the working DEFINE
composition, five change: `hid_backend.cpp` and `hid_backend.h` add the bounded
observer, `webserver.cpp` adds authenticated export, `webfiles.h` adds manual
Diagnostics controls, and `caps_trial.h` changes only the build identity. The
other 196 files match. Compiler, runtime, keyboard translation, ownership, storage,
STOP/cleanup/quarantine and experimental H1 behavior remain inherited.

The [backend patch](../tests/usb_os_observer/application.patch) and
[web patch](../tests/usb_os_observer_web/application.patch) are maintained overlays;
the canonical guarded builder selects the complete composition. No SDK archive,
descriptor, VID/PID, partition, USB mode, dependency guard or PSRAM setting changes.
The clean build uses the approved isolated Arduino ESP32 3.3.0 archive profile,
ESP32-S3/16 MiB flash/PSRAM disabled. It does not generate a migration/merged image
for installation. Mac helpers retain Bash 3.2, Python 3.8 and esptool 4.12 support.

The [frozen capture contract](usb-os-observer-contract.md) specifies the exact
whitelist and exclusions. Port 0, the first 64 selected headers and five seconds
from first foreground service include bounded boot-captured requests. Raw request
fields/order remain separate from interpretation. Unsupported reasons distinguish
unhandled selected standard/class headers and unknown DCD IDs; overflow,
missing reset, clock/exhaustion and generation/configuration failures remain
explicit. A COMPLETE state does not prove a legal/completed USB transaction or OS.
No payload bodies, string/descriptor contents, HID report contents, keystrokes,
host files or credentials are captured. No host helper, active lock probe, upload,
persistent learning or automatic payload is introduced.

The actual linked SDK SETUP path is verified through `dcd_int_handler` and
`handle_ep_irq`: event ID 6, the eight-byte SETUP copy, ISR flag and wrapper call.
The wrapper calls the observer and original handler once each. Instruction
inspection removes only nonallocated Xtensa metadata in a disposable copy;
allocated bytes/addresses/flags and all symbols must remain identical. The
original ELF is unchanged. Authenticated-before-snapshot compiled call edges
corroborate the pinned source and passing HTTP tests; instruction ordering alone
is not a complete authentication proof.

| Verification | Final result and scope |
| --- | --- |
| Observer native | 30 PASS, 1,049 assertions |
| Source scope | 8 PASS, 25 assertions |
| Export/auth/actual wrapper-to-JSON/UI | 40 PASS, 562 assertions |
| Inherited native, including DEL/DEFINE | 691 PASS, 28,547 assertions |
| Inherited browser/resource groups | 86 PASS, 1,563 assertions |
| Target/negative controls | 24 PASS, no failures or skips |
| Frozen release chain | All six layers, 190 original assertions retained |
| Package policy / focused package | 8 PASS / 105 PASS |
| Archive / bound installer mocks | 83 PASS / 38 PASS |
| Fresh local extraction / published extraction | Both offline preflights PASS |

ASan, UBSan and leak checks are clean on the native probes. Browser tests use
Linux Chromium or mocked DOM/HTTP, not a physical High Sierra/iPhone browser.
All 691 inherited native cases and 86 web groups executed on this frozen
composition during this stage. Continuations explicitly reused matching receipts;
the last regression invocation reran only nine dashboard groups. The earlier
24/963 and 7/21 observer receipts are historical: adding explicit event categories
justified the new focused runs. Historical DEL/DEFINE focused provenance in the
package remains separate from current-composition regression receipts.

Earlier rejected attempts remain recorded. Native mock API gaps, a stale
chunk-dependent assertion count and the fourth-panel browser fixture were fixed
without editing historical tests or reducing their checks. Clean build 1 compiled
but its inherited flag comparison rejected the additive observer selector. Clean
build 2 passed target proofs and all 190 assertions but failed strict receipt
equality because objdump headings contained temporary paths. The exact selector
adapter and heading-only normalization were committed, then clean build 3 passed
all guards. No failed image was packaged; no `--verify-existing` bypass was used.

| Resource | Candidate | Change from working DEFINE |
| --- | ---: | ---: |
| Application bytes | 1,445,008 | +6,960 |
| Compiler program bytes | 1,444,855 | Separately recorded in build receipt |
| Static RAM | 114,968 | +1,072 |
| Observer state plus guard | 1,084 | Separately measured |
| State plus conservative sum of observer callback frames | 1,356 / 2,048 | Within bound |
| Largest observer callback frame | 64 / 256 | Within bound |
| Compiler workspace | 3,928 / 4,096 | Unchanged; 168 bytes remain |
| Free bytes per application slot | 6,157,168 | 80.99% free |

Stack figures are compiled estimates for observer-owned frames, not measured
whole-IRQ peak stack or runtime latency. No real USB capture, host discrimination,
physical timing, runtime memory peak or new physical acceptance is established.

The owner-reported installed baseline remains DEFINE publication
`bdc8cbeea024ebb63f952da7fc4f39ac9e32fe29`. The [integrated owner evidence](define-labels-owner-acceptance.md)
retains successful write/verify and three scoped DEFINE passes: `DEFINE27OK`,
`DEFINE31OK`, and Request 3 line 1/code 6 rejection with owner-reported blank
output. Full running build ID and positive request/status evidence remain unknown.
DEL and previous accepted groups remain closed; no repeat campaign is requested.

The ZIP includes the exact original `working-define-labels-macos-review-v1.zip`,
2,691,374 bytes, SHA-256
`b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed`.
It restores working application 1,438,048 bytes, SHA-256
`167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`.
Extract it separately and follow its original guarded **install** procedure after
its offline preflight. Rediscover the port after ROM entry/reconnection.

The outer rollback action deliberately selects the older source/text-v2 image,
1,413,200 bytes, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It lacks later privacy/dashboard repairs and is not a full-device restore. These
roles are distinct. Both exact byte identities were verified inside the published
ZIP. Existing private backups, stored scripts, credentials and settings were not
read or altered. Future guarded installation backs up flash before final consent;
that private backup persists even if final installation is declined.

For the one owner session, use [OWNER-CHECK](usb-os-observer-owner-check.md) and
the included installation/return guides. First keep EvilDuck unplugged and run:

```bash
python3 preflight.py --directory .
```

Expect PASS, `plan_ready=false`, empty write ranges and no hardware/installation
authorization. Any later physical installation remains owner-operated.

After the later installation, verify the running observer ID, connect normally
to the known High Sierra Mac, wait at least five seconds after the dashboard is
ready, then manually View/Download capture A. Re-enumerate once using the same
image, rejoin Wi-Fi if needed and preserve capture B unchanged locally. Provide
A first; freeze a proposed rule and independent justification before using B for
validation. An optional existing harmless TextEdit marker may check ordinary
keyboard behavior after collection. No broad old trials or OS probe are needed.
If observations are incomplete, ambiguous or unsupported, stop detector work and
use the exact working DEFINE return path. Do not install another observer image
or claim a positive result from the known-host label, missing LEDs or low counts.
Two Mac captures alone do not establish accuracy across operating systems.

All 96 recorded pre-existing remote refs and every historical file mode were
preserved. Of 2,585 baseline tree entries, only the authorized compatibility
inventory and canonical builder selector changed; the other 2,583 remain exact.
H1 remains opt-in/experimental; canonical Hak5 numeric encoding and unchanged
OS_DETECTION compatibility remain unresolved. No hardware access, live capture,
real HID output, flashing, OTA, formatting or owner trial occurred here.
