# Reproduction — isolated feedback diagnostic profile

Start at0d100caa120d11920341e493019e5fc016c05a4f, use only the additive
led-feedback-boundary-diagnostics branch and its pinned overlays. ArduinoCLI1.3.1,
Arduino ESP32 core3.3.0, Xtensa GCC14.2.0 and the177 original ESP-IDF5.5 archives
retain the archive-based provenance. See led-feedback-dependency-pin.json and
led-feedback-build.json for complete source/object/archive/ELF hashes.
Global Arduino/SDK files are not patched. Exact original archive SHA is required;
two existing source patches plus the separately pinned diagnostic patch are
applied only inside an independent disposable source copy, with zero fuzz.
No descriptors, USB identity, partitions, SDK libraries or settings schema change.

Use unique external paths; these example commands are offline and have no port
or upload argument. The paths reflect this prepared cloud environment:

```bash
python3 tests/led_feedback/prepare_core.py --archive /workspace/tooling/arduino/downloads/esp32-3.3.0.zip --core /workspace/scratch/mac-recovery/cli-data/packages/esp32/hardware/esp32/3.3.0 --destination /workspace/scratch/NEW-led-core --user /workspace/tooling/arduino/user
python3 tests/led_feedback/build_candidate.py --output-dir /workspace/scratch/NEW-led-build --config /workspace/scratch/NEW-led-core/arduino-cli.json --core /workspace/scratch/NEW-led-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/led_feedback/verify_link.py --build-root /workspace/scratch/NEW-led-build --output /workspace/scratch/NEW-led-linked.json
python3 tests/led_feedback/run_tests.py --core /workspace/scratch/NEW-led-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-led-native --results /workspace/scratch/NEW-led-native.json
python3 tests/led_feedback/run_related.py --native-results /workspace/scratch/NEW-led-native.json --build-dir /workspace/scratch/NEW-led-related --results /workspace/scratch/NEW-led-related.json
node tests/caps_queue/test_ui.cjs /workspace/scratch/NEW-led-build/candidate/EvilDuckS3/webfiles.h
python3 tests/stage28h/verify_freeze.py
```

The native runner extracts exact pinned dispatcher, registry lookup, completion
and lifecycle function bodies; these call the real composed backend/receiver
with simulated transport/clock/registration/events. It does NOT execute the
entire Xtensa SDK or TinyUSB controller, and does not prove the physical host's
protocol/descriptor registration. New147-case source suite includes the unchanged
125-case custom regression set. ASan/UBSan/leak status is recorded separately.
Target build verifies exact source and final ELF, including direct calls through
the compiler-outlined diagnostic lambda. It never falls back to another core.
Relevant unchanged63 backend cases retain their historical T34/X13/X15 exclusions.

Package/image/layout tests and bound-installer tests use disposable public copies
and synthetic device responses only. The pinned esptool4.12 parser harness omits
the device dispatcher entirely. Python3.8 grammar, Node UI tests and Linux serial
mocks are not native High Sierra or hardware tests. Do not run the installer in
this environment. The owner later controls separately authorized physical steps.
