# Stage 14 offline tests

Run `python3 tests/stage14/run_tests.py --build-dir /tmp/evilduck-stage14 --results /tmp/stage14-results.json`.

The runner compiles actual production parser, preprocessor, registry, expression,
function/loop runtime, scheduler, HID backend and storage modules against RAM-only
clock/USB/filesystem mocks. ASan/UBSan are enabled. No ports, hardware, flash/erase,
OTA, real HID or host-side command payloads are used.

Deterministic raw sources permit exact entropy counts, controlled rejection and
replay. The host-only seeded source is not a DuckyScript seed.bin implementation.
US visible text mocks are not German hosts: German tests assert independently
specified eight-byte HID reports, including AltGr/QWERTZ/dead-key strokes. Release
checks tick the service after transport recovery; no release can be delivered while
disconnected/refused. Jitter tests compare relative timestamps and exact bytes with
unchanged disabled scheduling, not physical timing conformance.

The fixture prints a deterministic numeric singleton, then a random digit and Enter.
It is also executed verbatim by the automated fixture test with a controlled source.
No arbitrary string length syntax, seed file encoding, packed INJECT_VAR or restart
semantics are invented. See docs/stage14-design.md and stage14-deferred-features.md.
