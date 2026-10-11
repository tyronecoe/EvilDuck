# Stage 10 production-source MSC fault tests

```
python3 tests/stage10/run_tests.py --build-dir /tmp/evilduck-stage10 --results /tmp/stage10-results.json
```

52 actually executed tests:51 cases in the full runtime target and one separately
compiled MSC-disabled target. Every target uses ASan/UBSan and no physical hardware.
Full runtime target includes production usb_msc/attackmode/sd_card, CLI/com/parser/
execution/HID modules. The SDK endpoint, SD filesystem and clock are RAM mocks.
The original script storage mock remains, so this is not a physical mount test or
complete storage.cpp/AsyncWebServer HTTP integration test.

Fault coverage: truthful pending/active state, missing SD/image, wrong size and
nontruncating open, startup open/seek/read/SDK failures, identical-mode retry,
repeated startup, eject/power stop/load, stale host load after OFF/cancel, writable
restoration, offsets/unaligned cross-sector/end/overflow/null/4096-byte bounds,
failed seek without fallback, short transfers, removal/size changes, quarantine,
explicit recovery, timeout across millis wrap, interrupted preparation, script/
function/IF/WHILE continuation, STOP and preserved active media, live CLI/status
and web-equivalent com ownership, callback contention/error storms/threaded stop,
real SD-adapter file interleaving/remount and allocation probe. No format/create/
truncate occurs in production initialization. Mock preloaded4MiB raw data is only
an in-memory test fixture, not a generated migration or filesystem image.

TryGuard contention is tested from another thread; positive partial callbacks are
permitted by TinyUSB but our policy is fail/quarantine. A valid-range short write
can modify its prefix; tests assert this honestly. Invalid ranges/failed seeks
must never write at a different position. Callback addresses remain stable across
failure/deactivation to avoid SDK teardown races; inactive callbacks reject access.

One narrowly instrumented probe executes2000 accepted read/write callbacks and
observes0 C++ allocations. It does not establish zero allocations inside actual
ESP SD/FatFS/USB drivers. Source File creation/test storage vector allocations are
outside that probe. ASan/UBSan are not a substitute for a physical USB or data-race
validation campaign. See docs/stage10-design.md for contracts and limitations.

The Stage9 production failure probe is legitimately updated: failed begin now
returns failure and repeated same-mode requests retry. Its historical Stage9
report/output remains unchanged; this is RESOLVED_STAGE10, not native personality
conformance or a silently deleted expectation.
