# Offline v2 reproduction

Use fresh disposable outputs; no installer/device operation is executed. Historical v1 tools and packages remain unchanged.

```bash
python3 tests/source_text_v2/reference_probe.py --source /workspace/scratch/inject-var-focused/reproduction/payloadstudio-community.html
python3 tests/source_text_v2/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/source-text-v2/native-v1 --results /workspace/scratch/source-text-v2/native-v1.json
python3 tests/source_text_v2/build_candidate.py --output-dir /workspace/scratch/source-text-v2/build-v1 --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/source_text_v2/verify_link.py --build-root /workspace/scratch/source-text-v2/build-v1 --output /workspace/scratch/source-text-v2/linked-final.json
python3 tests/stage28h/verify_freeze.py
```

These output paths become occupied; choose fresh ones for reproduction. The public compiler capture must match its pinned SHA; the probe executes only six extracted functions and two regexes with stand-in character mapping/ENTER, not the browser or official runtime. No INJECT_VAR checks are rerun. Node is needed only for these offline reference probes, not the Mac installer.

Native tests use actual composed modules with mocked transport/storage/clocks/randomness and ASan/UBSan/leak checks. Final executed counts/commands and environment versions are recorded in the test receipt. Earlier source/text receipts are historical, not newly executed totals. Generated candidate copies retain documented previous expectation adaptations and update Z12 to terminated-alias precedence; historical test files remain unchanged.

Build profile: isolated Arduino ESP32 3.3.0 archive environment, ESP32-S3/16MiB, PSRAM off, existing USB-OTG/TinyUSB/CDC and CPU/flash settings. All177 SDK identities and source/dependency/ELF guards remain. Host deployment interfaces target High Sierra10.13.6/Bash3.2/Python3.8/esptool4.12. Linux testing is not native Mac execution or physical USB evidence. No hardware memory/timing is measured.

## Bound package verification

```bash
python3 tests/source_text_v2/package.py --directory /workspace/outputs/evilduck-routeb-source-text-portability-macos-v2 --build-root /workspace/scratch/source-text-v2/build-v1 --linked-report docs/source-text-v2-build.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --archive /workspace/outputs/evilduck-routeb-source-text-portability-macos-v2.zip --source-commit 71a62ea1bd775bc260052d099b5784b06ba3fc12
python3 tests/source_text_v2/test_package.py --directory /workspace/outputs/evilduck-routeb-source-text-portability-macos-v2 --archive /workspace/outputs/evilduck-routeb-source-text-portability-macos-v2.zip --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin --results /workspace/scratch/source-text-v2/package-tests.json
python3 tests/source_text_v2/test_bound_installer.py --directory /workspace/outputs/evilduck-routeb-source-text-portability-macos-v2 --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin --results /workspace/scratch/source-text-v2/installer-tests.json
```

Outputs are occupied; choose fresh paths. Reproducing the frozen archive uses the source-commit document/receipt versions, since repository reports subsequently gain publication evidence. No acceptance-network snippet or installer dispatcher is executed by these tests.
