# Offline reproduction — transient shortcuts

Run from the checkout root. Use fresh external output paths; all commands below
are source tests/builds/inspection, with no port/upload/flasher interface. Reuse
the established protected toolchain; no global configuration change, download,
installation or new service is needed. Native: Linux Python3.12.14, g++14.2.0-19,
Git2.52.0. Target: ArduinoCLI1.3.1, protected ESP32 core3.3.0, pinned Xtensa GCC14.2,
SDK v5.5-b66b5448-v1, existing AsyncTCP3.5.0/ESPAsyncWebServer3.12.1 pins.

```sh
python3 tests/stage28h/verify_freeze.py
python3 tests/keyboard_shortcuts/run_tests.py --build-dir /tmp/shortcuts-native --results /tmp/shortcuts-native.json
python3 tests/keyboard_shortcuts/run_bridge.py --sources /tmp/shortcuts-native/sources --build-dir /tmp/shortcuts-bridge --results /tmp/shortcuts-bridge.json
python3 tests/keyboard_shortcuts/run_core.py --sources /tmp/shortcuts-native/sources --build-dir /tmp/shortcuts-core --results /tmp/shortcuts-core.json
python3 tests/keyboard_shortcuts/run_core_new.py --sources /tmp/shortcuts-native/sources --build-dir /tmp/shortcuts-core-new --results /tmp/shortcuts-core-new.json
python3 tests/keyboard_shortcuts/run_negative.py --bridge-results /tmp/shortcuts-bridge.json --build-dir /tmp/shortcuts-negative --results /tmp/shortcuts-negative.json
python3 tests/keyboard_shortcuts/build_candidate.py --output-dir /tmp/shortcuts-link --config /workspace/tooling/stage26-final-controlled-core/arduino-cli.json --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 2
python3 tests/keyboard_shortcuts/verify_link.py --build-root /tmp/shortcuts-link --output /tmp/shortcuts-link-checked.json
python3 tests/keyboard_shortcuts/audit.py --output /tmp/shortcuts-scope.json
```

The build command is specific to this prepared cloud toolchain layout; use an
independently prepared pinned environment for another machine. Do not assume High
Sierra can run these target tools. No native Mac compilation is claimed here.
`--selector-off` is deliberately rejected by this selected candidate builder.
Do not substitute its outputs into the old X public manifest.

Historical tests remain unchanged. `run_core.py` uses byte-identical historical
test sources in a disposable mirror with the candidate header, because those tests
otherwise include the old header by a relative path. Mixing old/new Event ABIs is
not a valid test. Five historical groups with changed command-vocabulary assumptions
are explicitly not run; three new cases cover bounds, diagnostics and allocation.
T34 is skipped in the full-composition T selection with a recorded reason; new
K25 uses the full simulated RTOS task identity. The original failed observation
is retained in the committed report/results, not counted as a PASS.

Actual executed roots: `/workspace/tooling/shortcuts-dev/native-complete` for the
24 original new cases, W34 and T46; `k25-final` for the one new task-identity case;
`bridge-final`, `core-final`, `core-new`, `negative`; target `linked-verified`.
The final aggregate combines those executed rows once, excluding the separately
recorded T34 harness diagnostic. The final reproducible runner now includes K25
and the necessary T mock, and explicitly omits T34. Test logic/expectations are
unchanged for the selected historical cases. No historical prior PASS count is
substituted for execution. Initial setup/development failures are in the report.

Source manifests record SHA-256s for pre-patch inputs, patch and outputs. Prepare
first reproduces the original hash-pinned X composition with no fuzz. Overlay
rejects unexpected bytes before patching and checks every new source hash after.
The initial wrong-source fault probe used a disposable `com.cpp` and proved
rejection before any patch, not an altered installed dependency.

The target verifier checks exact source inventories, core/SDK/framework/compiler
identities, linked modifier API, feature selectors, unchanged partitions, the
same startup/HID/NVS guards, actual linked ELF and regenerated BIN equality.
Build-path/debug metadata or build timestamp changes can change artifact hashes;
the receipt identifies this actual clean build, not a promised cross-machine
byte-identical binary. No raw-device files, credentials or owner backups are inputs.

For publication checks, save read-only `git ls-remote --refs origin` snapshots and
pass both paths to `audit.py --before ... --after ... --output <fresh-json>`.
Only the new branch may be added; every previous ref must still match.
