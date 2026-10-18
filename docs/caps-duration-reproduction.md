# Reproduce the additive Caps-duration candidate

Baseline branch led-feedback-boundary-diagnostics, commit
3e693fbe790af670278716cdf4d64c75485cb097. New branch caps-duration-feedback-trial.
No historical source/profile/guard is edited. New manifest applies after every
pinned prior layer. The approved archive-based feedback core is reused exactly:
no new USB stack patch, SDK replacement, descriptor or identity change.

Prepared Linux toolchain: ArduinoCLI1.3.1; Arduino ESP32 core3.3.0; Xtensa GCC14.2.0;
all177 pinned ESP-IDF5.5 archives. Full hashes are in caps-duration-build.json and
caps-duration-dependency-pin.json. Native GCC14.2.0, Python3.12.14 and Node24.19.0
run simulated tests; released helper grammar is checked for Python3.8 and Bash.
No claim of native High Sierra execution is made by these cloud checks.

Use unique external destinations, never an installed core modification:

```bash
python3 tests/led_feedback/prepare_core.py --archive /workspace/tooling/arduino/downloads/esp32-3.3.0.zip --core /workspace/scratch/mac-recovery/cli-data/packages/esp32/hardware/esp32/3.3.0 --destination /workspace/scratch/NEW-core --user /workspace/tooling/arduino/user
python3 tests/caps_duration/build_candidate.py --output-dir /workspace/scratch/NEW-build --config /workspace/scratch/NEW-core/arduino-cli.json --core /workspace/scratch/NEW-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/caps_duration/verify_link.py --build-root /workspace/scratch/NEW-build --output /workspace/scratch/NEW-linked.json
python3 tests/caps_duration/run_tests.py --core /workspace/scratch/NEW-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-native --results /workspace/scratch/NEW-native.json
python3 tests/caps_duration/run_related.py --native-results /workspace/scratch/NEW-native.json --build-dir /workspace/scratch/NEW-related --results /workspace/scratch/NEW-related.json
node tests/caps_duration/test_ui.cjs /workspace/scratch/NEW-build/candidate/EvilDuckS3/webfiles.h
python3 tests/stage28h/verify_freeze.py
```

The native runner executes actual composed startup, coordinator, adapter, scheduler,
backend, storage/settings and web handlers with simulated clocks/USB/storage.
It includes exact pinned core dispatcher/completion/lifecycle bodies. Historical
D12's local copied buildId string expectation is updated to the new build ID;
its logic is unchanged and the historical file is untouched. No other expected
behavior is weakened. Related backend cases retain their documented T34/X13/X15
exclusions. Sanitizer/leak settings and commands are retained in result receipts.
New UI tests execute embedded JavaScript in a Node VM, not an iPhone browser.

Package tests operate only on disposable PUBLIC copies, injected esptool responses
and the public OTA initializer fixture. Parser tests truncate esptool's actual AST
before any connection/dispatch. Do not invoke installation helpers in the cloud.
The release remains app-only with no automatically generated migration image.
