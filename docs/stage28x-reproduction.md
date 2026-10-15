# Stage28X offline reproduction

All commands below are host tests or target build/inspection only, from repository
root. No port/board/upload/OTA/flasher mode exists. Existing verified environment
was reused; no installation, global dependency modification or environment service
is required. Use fresh external output paths, never overwrite owner files.

Executed environment: Python3.12.14; Debian g++14.2.0-19; Git2.52.0;
Arduino CLI1.3.1 commit08ff7e2b; Xtensa GCC14.2.0 esp-x32/2411;
Arduino ESP323.3.0 protected core; idf-release_v5.5-b66b5448-v1 ESP32-S3 SDK;
ESPAsyncWebServer3.12.1, AsyncTCP3.5.0. Exact compiler/source/tree/archive hashes are
in linked receipts. Existing tools reject pin mismatches, not SKIP or downgraded flags.
No task outside this environment, native macOS or physical S3 is claimed tested.

```sh
python3 tests/stage28h/verify_freeze.py
python3 tests/stage28x/run_tests.py --build-dir /tmp/stage28x-native --results /tmp/stage28x-native.json
python3 tests/stage28w/run_tests.py --build-dir /tmp/stage28x-w --results /tmp/stage28x-w.json
python3 tests/stage28v/run_tests.py --build-dir /tmp/stage28x-v --results /tmp/stage28x-v.json
python3 tests/stage28u/run_tests.py --build-dir /tmp/stage28x-u --results /tmp/stage28x-u.json
python3 tests/stage28t/run_tests.py --build-dir /tmp/stage28x-t --results /tmp/stage28x-t.json
python3 tests/stage28w/run_regressions.py --build-dir /tmp/stage28x-production --results /tmp/stage28x-production.json
python3 tests/stage28w/run_startup.py --sdk-source /workspace/tooling/stage19-sdk-source --build-dir /tmp/stage28x-startup --results /tmp/stage28x-startup.json
python3 tests/stage28w/run_framework.py --user-dir /workspace/tooling/arduino/user --output-dir /tmp/stage28x-framework
python3 tests/stage28x/build_candidate.py --output-dir /tmp/stage28x-link --config /workspace/tooling/stage26-final-controlled-core/arduino-cli.json --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 2
python3 tests/stage28x/verify_link.py --build-root /tmp/stage28x-link --output /tmp/stage28x-link-checked.json
python3 tests/stage28x/build_candidate.py --diagnostics-off --output-dir /tmp/stage28x-link-off --config /workspace/tooling/stage26-final-controlled-core/arduino-cli.json --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 2
python3 tests/stage28x/verify_link.py --build-root /tmp/stage28x-link-off --output /tmp/stage28x-link-off-checked.json
python3 tests/stage28x/audit.py --build-root /tmp/stage28x-link --output /tmp/stage28x-audit.json
```

X prepare checks immutable W pins/composition, overlays coordinator from the validated
historical V source and applies exact X patch with fuzz0, checks output hashes, then
copies reviewed runtime files. New header guard prevents duplicate scratch/header
aliases in native tests; target consumes one sketch copy. Native test API mocks are
selected only under EVILDUCK_HOST_TEST, which target commands do not define.
Diagnostic selector is absent in comparison, not merely runtime-disabled.

Build wrappers retain W controlled-start flags, protected core verification, source
ROOT redirection only to reviewed scratch, exact partition validation and original
ELF-to-BIN/startup/HID/NVS guards. Post-link checker verifies copied source, explicit
flags, actual measurement calls from endTurn, owner tick hooks, linked8192 stack
getter and no enabled AsyncFileResponse/WS live-dispatch symbols. It verifies all
consumed SDK archives against immutable W, resolves linker scripts/response inputs,
and uses a separate explicit inspection ELF, asserting original ELF unchanged.

Actual final run roots/commands are in linked/test receipts. Outputs are
/workspace/tooling/stage28x-linked-enabled-final and stage28x-linked-off-final;
final native receipt stage28x-native-verified.json. Collector reads these named fresh
receipts only, never executes tests, modifies old docs or converts historical counts.
Audit checks all1349 historical paths/bytes/modes,235 frozen files, allowed new paths,
artifact hashes/bounds and planned sector overlap. Add --before/--after snapshots
to audit publication: all48 previous refs must match and only new X branch appear.
A matching review receipt is not a cryptographic signature or hardware authorization.

Rollback: leave diagnostic selector undefined and use separately reviewed existing
profile; discard only disposable X scratch. Existing core/SDK/branches/Stage26 and
owner data need no rollback. No arming/replay/recovery operation is added. Stop after
review; neither Stage28Y nor physical work is authorized.
