# STOP, LED return and host diagnostic delivery

**GO: source/build review and owner-side offline compilation. Physical installation,
USB/capture trials and security-product results remain unperformed/unauthorized.**
The whole logger goal is not marked complete.

Work starts from HTTP-fix branch/commit400b25dd1eb401eb9ab08eae2bf8c9c4289c4098,
composing frozen public Stage28X + shortcuts + HTTP fix + separately pinned A/B
deltas. The owner's installed candidate is not assumed to equal this new build.
Branch: `stop-lock-led-diagnostics`. Historical files, settings, packages, NVS,
payloads, dependencies and partitions are unchanged. No private data was inspected.

Three separately reviewable changes:

1. **A — STOP:** `ef0ff5a`; [implementation/results](stop-ui-report.md).
   Visible sticky red button on embedded home UI, live authentication, bounded
   admission, explicit errors, duplicate protection and owner request correlation.
   Route B is explicitly selected by home Run; legacy clients remain supported.
   Legacy HTTP stop only publishes an owner request; callbacks never clean up HID.
2. **B — LED:** `1e920ed`; [receiver/build report](led-return-report.md).
   Fixed-size callback queue and normal-loop decoder, unknown/stale/disconnected
   evidence, explicit120-second receiving and separate stop, RAM-only fixed17-byte
   message, authenticated view/download/clear and text-safe display. Two attempted
   host senders and finite launchers are provided. Custom framing, not Hak5 format.
   Includes a response-BODY timeout refinement to STOP controls.
3. **C — host fake-phrase tests:** this report's commit;
   [implementation/limits/matrix](host-capture-report.md). Independent visible,
   explicitly started60-second Windows/macOS/Linux attempts retain only the agreed
   fake phrase from OS events, with normal permissions and no automatic delivery.
   Native Windows/macOS and actual Linux-device execution are NOT TESTED.

## Actual completed software verification

| Scope | PASS | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| Final composed native L/S/H/K/W | 103 | 0 | 5,884 |
| Related backend/diagnostic T/X | 63 | 0 | 2,650 |
| Current positive C++ total | 166 | 0 | 8,534 |
| Embedded STOP JS VM | 10 | 0 | 21 |
| Embedded receiver JS VM | 3 | 0 | 5 |
| Python fake-capture production unit mocks | 11 | 0 | not instrumented |
| Public launcher compiler/runtime mock traces | 4 | 0 | not instrumented |

ASan/UBSan/leaks clean for completed native suites and launcher traces. Two
missing-symbol ELF controls still fail the unchanged safety predicates as intended;
these are separately classified negative evidence. Earlier development compile,
fixture and wrong-main failures are documented in A/B/C reports, not hidden or
reclassified. No expectation changes to historical diagnostic classifications.
Relevant scoped suites were run, not every historical stage. Windows/macOS native
builds, real browser/mobile rendering, USB delivery, capture permissions, timing
and defense outcomes are NOT TESTED. No physical heap/stack measurement occurred.
The Linux environment is Debian13(trixie), kernel6.18.44; tools/commands appear in
[reproduction](stop-led-reproduction.md) and machine-readable results.

## Reviewed firmware

Clean pinned Arduino3.3.0 / ESP-IDF5.5 / Xtensa14.2.0, isolated existing protected
core,16MiB, PSRAM disabled, existing USB-OTG/CDC/240MHz/partition configuration.
Actual source/object/archive/link/ELF-to-BIN proofs remain;281 linked inputs,
177 identical SDK archives. No installed core/SDK modified, no USB identity or
descriptor changes. [Complete provenance/resources](stop-led-build.json).

- Compiler program:1,376,423B (+9,720 versus HTTP candidate).
- Application:1,376,576B (+9,728).
- Static RAM:107,480B (+1,152).
- Free per0x740000 OTA slot:6,225,600B /81.892342%.
- Application SHA256:`c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4`.
- ELF SHA256:`b0e2513538e83ccfedc247ae0786e5fe52c4b1cd717d1f9be69c6d566265f566`.

[Review-only application](../downloads/evilduck-stop-led-review.bin). It is not an
installation package or permission to flash, and cannot be substituted into old
packages with different pinned hashes. Embedded assets need no SPIFFS formatting
or full filesystem replacement. Original working archives remain intact.

## Boundaries and owner gates

Five RTOS ticks bounds the mutex WAIT, not total HTTP or cancellation latency.
The browser timeout covers headers/body but does not undo an admitted command.
Local terminal/cancel/clear submission is not proof of host key release. The LED
acceptance deadline is checked before owner decoding; a blocked owner loop can
delay timeout publication, but cannot decode an expired queued frame successfully.
The fixed queue still caps callback storage and reports overflow. No physical
real-time or SDK disconnect guarantee is inferred from these tests.

The original DuckyLogger is a different Linux/xinput/reverse-TCP/persistent payload.
No such behaviors or source were reused. No arbitrary keystroke log, credential
collection, external webhook or automatic capture-to-LED sending was implemented.
Fake-only cross-application acceptance must still be demonstrated with actual owner
input in another ordinary editor. Retain normal controls and use the provided
sanitized record; failed delivery is not automatically security-product prevention.

Review the [short owner checklist](stop-led-reproduction.md) and host READMEs.
Remaining gates: native host compilation, actual installed artifact/layout/update
review and separate installation authorization, actual lock-report capabilities,
byte-exact fixed roundtrip, visible second-app fake capture/stop and iPhone view.
Original stock firmware availability is owner-confirmed externally and is not a
blocker introduced here. No original-data preservation requirement is reimposed.
No hardware, flash, erase, format, OTA, actual HID or stored owner script ran.
No further stage or automatic hardware operation will start.

## Complete added-file inventory

- `docs/host-capture-report.md`
- `docs/host-capture-results.json`
- `docs/led-return-report.md`
- `docs/led-return-results.json`
- `docs/led-return-source-manifest.json`
- `docs/stop-led-build.json`
- `docs/stop-led-integrity.json`
- `docs/stop-led-references.json`
- `docs/stop-led-report.md`
- `docs/stop-led-reproduction.md`
- `docs/stop-ui-report.md`
- `docs/stop-ui-results.json`
- `docs/stop-ui-source-manifest.json`
- `downloads/evilduck-stop-led-review.bin`
- `host_tests/capture/README.md`
- `host_tests/capture/WindowsCapture.cs`
- `host_tests/capture/capture-macos.c`
- `host_tests/capture/capture-windows.ps1`
- `host_tests/capture/capture_linux.py`
- `host_tests/capture/launchers/macos.duck`
- `host_tests/capture/launchers/windows.duck`
- `host_tests/defensive-record-template.json`
- `host_tests/led_return/README.md`
- `host_tests/led_return/WindowsSender.cs`
- `host_tests/led_return/launchers/macos.duck`
- `host_tests/led_return/launchers/windows.duck`
- `host_tests/led_return/protocol_vectors.py`
- `host_tests/led_return/send-macos.c`
- `host_tests/led_return/send-windows.ps1`
- `tests/host_capture/compile_launchers.cpp`
- `tests/host_capture/run_checks.py`
- `tests/host_capture/test_capture.py`
- `tests/led_return/build_candidate.py`
- `tests/led_return/led_receiver.cpp`
- `tests/led_return/led_receiver.h`
- `tests/led_return/mocks/esp_timer.h`
- `tests/led_return/prepare_sources.py`
- `tests/led_return/receiver.patch`
- `tests/led_return/run_related.py`
- `tests/led_return/run_tests.py`
- `tests/led_return/test_main.cpp`
- `tests/led_return/test_stop_ui.cjs`
- `tests/led_return/test_ui.cjs`
- `tests/led_return/verify_link.py`
- `tests/stop_ui/prepare_sources.py`
- `tests/stop_ui/run_tests.py`
- `tests/stop_ui/stop.patch`
- `tests/stop_ui/test_main.cpp`
- `tests/stop_ui/test_ui.cjs`
