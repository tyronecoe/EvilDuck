# Stage 11 ownership/report fault tests

Run entirely offline:

```sh
python3 tests/stage11/run_tests.py --build-dir /tmp/evilduck-stage11 --results /tmp/stage11-results.json
```

Production sources include parser/preflight, streamed runtime, expressions/functions,
keyboard scheduler, HID backend, locale translation and CLI. Only USB endpoints,
clock, filesystem/script adapters and unrelated device features are mocked. The
pinned SDK event signature and mounted state are modeled separately from endpoint
readiness; ready=false alone is backpressure, not disconnect. Byte checks cover
endpoint0, keyboard reportID1, reserved0, modifier byte and all six usage bytes.
No physical HID, media, USB discovery or host commands are executed.

Tests cover all256 modifier masks, every modifier bit, selective releases,
duplicates/idempotence, six/seven usage boundaries, merged chords/text/Enter/DE
AltGr/dead keys, raw KEYCODE modifiers, documented INJECT_MOD forms, canonical
RESET/STOP_PAYLOAD, DEFINE/repeat/default delays, streaming SPIFFS/SD text, nested
conditional/loop/function ownership, runtime/storage/control faults, EOF/cancellation,
refused holds/releases and zero priority, loss/reconnect/events between ticks,
callback-thread lock isolation, live CLI/web-equivalent com admission and new-run
state isolation. Actual AsyncWebServer HTTP routes are not linked or contacted.

The allocation probe reserves mock capture buffers before tracking and executes
1,000 ownership/merge/release/refusal/recovery cycles. It measures C++ allocation
requests in the exercised hot path, not ESP driver/library heap use or total script
parsing allocations. ASan/UBSan are enabled in every executable. This does not
constitute ThreadSanitizer or a proof of real USB/host release acknowledgment.

The Stage9 five formerly rejected ownership/control fixtures are now expected to
execute their harmless first output line, with status RESOLVED_STAGE11. Historical
Stage9 documentation/results stay unchanged; exact report semantics have separate
Stage11 tests. Five historical language XPASS labels remain auditable in Stage1.
