# Isolated build and software verification

Baseline:baddb8f2d3bb6060e0f72e6cbe58377c894c86bb; branch mac-caps-timing-profile.
The new hash-pinned application layer applies after tests/caps_duration and all
inherited overlays. All historical files and verifiers remain unchanged. New
post-link verification keeps all existing predicates and changes the added Caps
scheduler call-edge check to the new admitted-value accessor. No core/SDK change.

Prepared cloud tools:ArduinoCLI1.3.1, Arduino ESP32 core3.3.0 approved isolated
archive-feedback profile, Xtensa GCC14.2.0, pinned ESP-IDF5.5 archives; native
GCC14.2.0/Python3.12.14/Node24.19.0. SDK, compiler, libraries and source hashes are
recorded in mac-caps-build.json and mac-caps-dependency-pin.json. Python3.8 grammar
and Bash syntax checks are not native High Sierra execution.

Use new external directories and the retained exact pinned isolated core; no
command below has upload/port/device access:

```bash
python3 tests/mac_caps/build_candidate.py --output-dir /workspace/scratch/NEW-mac-build --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/mac_caps/verify_link.py --build-root /workspace/scratch/NEW-mac-build --output /workspace/scratch/NEW-mac-linked.json
python3 tests/mac_caps/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-mac-native --results /workspace/scratch/NEW-mac-native.json
python3 tests/mac_caps/run_related.py --native-results /workspace/scratch/NEW-mac-native.json --build-dir /workspace/scratch/NEW-mac-related --results /workspace/scratch/NEW-mac-related.json
node tests/mac_caps/test_ui.cjs /workspace/scratch/NEW-mac-build/candidate/EvilDuckS3/webfiles.h
python3 tests/stage28h/verify_freeze.py
```

To prepare an isolated core from the pinned archive on a new environment, use the
unchanged tests/led_feedback/prepare_core.py workflow documented in
caps-duration-reproduction.md. It validates all source and archive hashes and
copies only into disposable destinations. Do not alter global toolchains.

Native tests execute actual composed modules and pinned callback slices against
mock storage/USB/clocks. New M cases cover admission snapshots and actual report
bytes/timing/cancellation. Inherited tests retain behavior; only their copied
buildId-prefix literals are adjusted to this new release ID. Historical source
files/expected outcomes are untouched. Related T34/X13/X15 exclusions remain
recorded for their prior Linux identity/old-buffer assumptions.

Native/related runners retain ASan detect_leaks=1:halt_on_error=1 and UBSan
halt_on_error=1. UI runs in a Node VM. Package/installer fault tests use only public
copies and synthetic device responses. The esptool4.12 parser harness truncates
the real AST before connection/operation dispatch. None measures physical USB,
Caps state, RTOS high-water, native Mac behavior or host release.
