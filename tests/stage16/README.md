# Stage 16 software-only verification

Run `tools/build_s3_patched.py` first using [reproduction instructions](../../docs/stage16-patched-build.md).
Then substitute its actual paths:

```sh
python3 tests/stage16/run_tests.py --core-dir "$ED_ISOLATION/data/packages/esp32/hardware/esp32/3.3.0" --build-dir /tmp/evilduck-stage16-routing --results /tmp/stage16-routing.json
python3 tests/stage16/build_validation.py --original-core "$ED_CORE" --patched-core "$ED_ISOLATION/data/packages/esp32/hardware/esp32/3.3.0" --build-dir "$ED_BUILD" --arduino-cli "$ED_CLI" --original-config /absolute/path/to/owner-arduino-cli.yaml --results /tmp/stage16-build-validation.json
```

Routing compiles exact patched core callback/lookup/dispatch bodies, current production
HID/runtime/storage modules and RAM mocks with ASan/UBSan. It includes all applicable
Stage15 paired vectors, exhaustive8-bit report IDs/types, input backpressure, rapid and
concurrent feedback, executor-lock independence, reconnect/session evidence and stock
hook exclusion. Stock indefinite event-post policy is an OBSERVED limitation, not a
compatibility pass. No physical USB, HID output or real storage is involved.

Build validation checks wrong version/source/tree, installed-directory protection,
missing core argument/compile guard, actual CLI fallback rejection and final ELF/map/
compilation database provenance. Its assertion count is one acceptance predicate per
case. Compiler estimates and C++new probes remain separate from physical heap/high-water.

Stage15 history uses its original unpatched installed core and a temporary exact
baseline backend, not this branch's corrected backend; no original results are deleted.
