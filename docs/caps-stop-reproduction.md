# Isolated build and software verification

Baseline:5e22569709f44bd4a6c429beb43a055d94d39257; branch caps-stop-hid-trace.
The new hash-pinned application layer applies after tests/caps_duration and all
inherited overlays. All historical files and verifiers remain unchanged. This layer follows tests/mac_caps as well as the earlier overlays. New
post-link verification keeps all existing predicates and changes the added Caps
scheduler call-edge check to the new admitted-value accessor. No core/SDK change.

Prepared cloud tools:ArduinoCLI1.3.1, Arduino ESP32 core3.3.0 approved isolated
archive-feedback profile, Xtensa GCC14.2.0, pinned ESP-IDF5.5 archives; native
GCC14.2.0/Python3.12.14/Node24.19.0. SDK, compiler, libraries and source hashes are
recorded in caps-stop-build.json and caps-stop-dependency-pin.json. Python3.8 grammar
and Bash syntax checks are not native High Sierra execution.

Use new external directories and the retained exact pinned isolated core; no
command below has upload/port/device access:

```bash
python3 tests/caps_stop/build_candidate.py --output-dir /workspace/scratch/NEW-mac-build --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/caps_stop/verify_link.py --build-root /workspace/scratch/NEW-mac-build --output /workspace/scratch/NEW-mac-linked.json
python3 tests/caps_stop/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-mac-native --results /workspace/scratch/NEW-mac-native.json
python3 tests/caps_stop/run_related.py --native-results /workspace/scratch/NEW-mac-native.json --build-dir /workspace/scratch/NEW-mac-related --results /workspace/scratch/NEW-mac-related.json
node tests/caps_stop/test_ui.cjs /workspace/scratch/NEW-mac-build/candidate/EvilDuckS3/webfiles.h
python3 tests/stage28h/verify_freeze.py
```

To prepare an isolated core from the pinned archive on a new environment, use the
unchanged tests/led_feedback/prepare_core.py workflow documented in
caps-duration-reproduction.md. It validates all source and archive hashes and
copies only into disposable destinations. Do not alter global toolchains.

Native tests execute actual composed modules and pinned callback slices against
mock storage/USB/clocks. New G cases cover admission snapshots and actual report
bytes/timing/cancellation. Inherited tests retain behavior; only their copied
buildId-prefix literals are adjusted to this new release ID. Historical source
files/expected outcomes are untouched. Related T34/X13/X15 exclusions remain
recorded for their prior Linux identity/old-buffer assumptions.

Native/related runners retain ASan detect_leaks=1:halt_on_error=1 and UBSan
halt_on_error=1. UI runs in a Node VM. Package/installer fault tests use only public
copies and synthetic device responses. The esptool4.12 parser harness truncates
the real AST before connection/operation dispatch. None measures physical USB,
Caps state, RTOS high-water, native Mac behavior or host release.

New G cases execute source-tagged trace/STOP paths. Callback tests register the
actual mock keyboard before invoking pinned routing; earlier G08 omission was
recorded and corrected, not an expectation relaxation. See report for exact commands
and failed-attempt evidence. Observer filter branch can run under ASan/UBSan on Linux;
Apple IOHID branch requires native owner testing. Do not run a Mac installer against
any device as part of cloud reproduction.

Executed paths for this task: /workspace/scratch/caps-stop-build-release,
caps-stop-native-complete, caps-stop-related. Final linked verifier output is
caps-stop-linked-final.json. Exact native/related compiler invocations and per-case
exit/output are in the published *-tests.json receipts. Final new native suite has
231cases/7470assertions; related63cases/2650assertions. Additional commands:

```bash
node tests/caps_stop/test_ui.cjs /workspace/scratch/caps-stop-build-release/candidate/EvilDuckS3/webfiles.h
python3 tests/led_feedback/test_core_profile.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --results /workspace/scratch/NEW-core-results.json
cc -std=c11 -Wall -Wextra -Werror -DFILTER_TEST -fsanitize=address,undefined tests/caps_stop/mac_caps_observer.c -o /workspace/scratch/NEW-filter
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 /workspace/scratch/NEW-filter
```

The native Apple branch is excluded in FILTER_TEST. Native High Sierra remains
SKIP_ENVIRONMENT and requires owner output, never inferred from this filter test.
