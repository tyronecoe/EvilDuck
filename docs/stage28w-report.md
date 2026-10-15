# Stage28W bounded framework and controlled link report

**BUILD REVIEW: GO. RUNTIME INTEGRATION: NO-GO pending actual-task/lower-framework
validation. PHYSICAL DEPLOYMENT: NO-GO.** These verdicts are separate. The owner
explicitly authorized an offline link in W; V's historical blocked gate/report
remains unchanged. No device action or Stage28X is authorized by this result.

Exact parent: `3144c9bdf7b78a4f75d6861fdffa0707c755fffc`.
Branch: `stage28w-framework-boundary-controlled-link`.
The new branch preserves all1,307 historical paths/bytes/modes and235 frozen
Stage26 files. The actual47 previous remote refs are snapshotted and compared at
publication. No production profile, library/core/SDK installation, partition,
USB identity, previous expectation or owner file is modified.

Delivered a reproducible controlled target link with Route B explicitly compiled
in, while ordinary run remains legacy and boot never selects/arms Route B. Scope
is the reachable application/framework boundary, not arbitrary raw SDK sandboxing.
Mutating WebSocket CLI is disabled. Dynamic filesystem static responses are
disabled from boot, so no accepted async File is retired on a guessed disconnect
hook. Built-in immutable pages remain. Synchronous dynamic readers retain admission
until File cleanup and body copying. Existing guarded writers and503 upload/update/
restart policy remain. A discovered settings/authentication snapshot race is
closed with nonblocking admission. Partial settings saves remain non-atomic.

Enabled serial work is owner-only and bounded to64 read attempts per turn, with
512-byte line storage, framing across turns, whole-line overflow/NUL rejection
and no truncated-prefix execution. Actual loop tests demonstrate progress with
continuous input; STOP behind arbitrary unread backlog is not instantaneous.
Existing copied requests,8,192-byte capture/verification, explicit media selection,
Runtime Delay, source-in-memory execution and permanent ambiguity/loss quarantine
are preserved. No grammar, numerical semantics, descriptors or new ownership
model is introduced. LOCAL_SCHEDULER_DONE/LOCAL_CLEARING_SUBMITTED remain local;
strict Route A/host release remain unresolved.

Final clean linked measurements:

| Measurement | Controlled Route B | Selector-off controlled |
| --- | ---: | ---: |
| Program usage | 1,355,051 B | 1,329,611 B |
| Application BIN | 1,355,200 B | 1,329,760 B |
| Static RAM | 106,136 B | 82,248 B |
| Free bytes per0x740000 slot | 6,246,976 B | 6,272,416 B |
| Free OTA percentage | 82.17352505% | 82.50816608% |

Actual linked symbols reconcile V's23,390-byte subtotal and additional serial/
removed WS state exactly with23,888 bytes of RAM growth; nested Program/Runtime
are not counted twice. Enabled linked image contains no AsyncFileResponse symbols.
The original slot is too small; the unchanged proposed table is required. Static
budget remainder is not heap margin. No task high-water, physical heap, real USB
behavior, AsyncTCP task runtime or scheduling latency was measured.

Fresh verification:34 W cases/380 assertions and5 selected exact pinned framework
component cases/116, all passing. Separate unchanged V56/566, U64/515, T47/467,
affected production77/67,371 and controlled startup30/635 pass. Exact selector-off
production comparison77/67,371 is not counted again as new coverage. Completed
native ASan/UBSan/leak checks are clean; the65-byte real-body negative control
fails as intended. Historical diagnostics and superseded runs are separately
recorded. No existing failure classification was rewritten.

Both links pass the existing protected-core startup/HID/NVS/settings/ELF-to-BIN
checks and new source/framework/archive/profile checks. The enabled owner loop
calls bind/update/tick before bounded CLI; compiler/runtime and backend bodies
are actually linked, not merely compiled.277 enabled/273 selector-off input files,
183 archives each, three link response files,13 scripts,72/60 source-copy checks,
map/section/frame and artifact hashes are retained. Libraries consumed are
ESPAsyncWebServer3.12.1 / AsyncTCP3.5.0 with exact tree pins, not guessed Git commits.
All generated artifacts are external scratch review outputs, not authorized images.

Remaining runtime limits: whole actual AsyncTCP/FreeRTOS request cancellation,
concurrency/error/OOM behavior and lower drivers are not executed by native mocks;
selected framework tests are not a complete network stack. Unregistered/injected
SDK/VFS writers and external media stability are excluded from the supported
boundary. No current escaped enabled handler is inferred from V48. Actual USB
queue/retirement, host delivery/release and device stack/heap remain unmeasured.
Runtime integration/physical review must address these premises independently;
a successful link is not their validation. Firmware availability remains OWNER
CONFIRMED: AVAILABLE EXTERNALLY; no search/request/reconstruction or old-data
preservation requirement is reintroduced. Backups/credentials were not inspected.

Review framework-boundary, caller-matrix, serial-contract, resources, tests,
reproduction, source-manifest, linked-enabled/selector-off, test-results and
integrity receipts. All changes are new W files and a scratch-applied three-file
application patch. Rollback is leaving Route B disabled and discarding scratch.
No merge, installed dependency edit, hardware/serial/USB access, real HID, flash,
erase, format, boot, OTA, external support message or owner payload execution
occurred. Stop here for review; Stage28X was not started.

## Complete new-file inventory

- `docs/stage28w-caller-matrix.md`
- `docs/stage28w-framework-boundary.md`
- `docs/stage28w-integrity.json`
- `docs/stage28w-linked-enabled.json`
- `docs/stage28w-linked-selector-off.json`
- `docs/stage28w-protected-refs.json`
- `docs/stage28w-report.md`
- `docs/stage28w-reproduction.md`
- `docs/stage28w-resources.md`
- `docs/stage28w-serial-contract.md`
- `docs/stage28w-source-manifest.json`
- `docs/stage28w-test-results.json`
- `docs/stage28w-tests.md`
- `tests/stage28w/boot_fixture.cpp`
- `tests/stage28w/boundary.patch`
- `tests/stage28w/build_candidate.py`
- `tests/stage28w/collect_results.py`
- `tests/stage28w/framework_test.cpp`
- `tests/stage28w/mocks/Adafruit_NeoPixel.h`
- `tests/stage28w/mocks/Arduino.h`
- `tests/stage28w/mocks/ESPAsyncWebServer.h`
- `tests/stage28w/mocks/FS.h`
- `tests/stage28w/mocks/SD.h`
- `tests/stage28w/mocks/SPI.h`
- `tests/stage28w/mocks/SPIFFS.h`
- `tests/stage28w/mocks/USBHID.h`
- `tests/stage28w/mocks/USBHIDKeyboard.h`
- `tests/stage28w/mocks/USBMSC.h`
- `tests/stage28w/mocks/Update.h`
- `tests/stage28w/mocks/WiFi.h`
- `tests/stage28w/mocks/esp_flash.h`
- `tests/stage28w/mocks/esp_partition.h`
- `tests/stage28w/mocks/host.h`
- `tests/stage28w/mocks/network.h`
- `tests/stage28w/prepare_sources.py`
- `tests/stage28w/run_framework.py`
- `tests/stage28w/run_regressions.py`
- `tests/stage28w/run_startup.py`
- `tests/stage28w/run_tests.py`
- `tests/stage28w/test_main.cpp`
- `tests/stage28w/verify_link.py`
- `tests/stage28w/verify_scope.py`
