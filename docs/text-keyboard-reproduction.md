# Offline reproduction — composed text/keyboard utilities

These commands build or test fresh disposable outputs only. They do not open a board, run a host payload, send real HID, upload firmware or invoke an installer. Historical overlays and installed dependencies remain unchanged. The new layer validates exact source/patch hashes and its explicit selector.

## Commands executed for the current receipts

```bash
python3 tests/text_keyboard/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/text-keyboard/native-v1 --results /workspace/scratch/text-keyboard/native-v1.json
python3 tests/text_keyboard/build_candidate.py --output-dir /workspace/scratch/text-keyboard/build-v1 --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/text_keyboard/verify_link.py --build-root /workspace/scratch/text-keyboard/build-v1 --output /workspace/scratch/text-keyboard/linked-final.json
python3 tests/stage28h/verify_freeze.py
```

Do not reuse these occupied output directories for another execution. For reproduction, replace the native/build/results/output paths with fresh disposable names; the native and build tools refuse an existing output. The complete native compiler command and exact target command/configuration are recorded in `text-keyboard-test-results.json` and `text-keyboard-build.json`.

Tests exercise actual composed compiler/runtime/adapter/backend modules with mocked HID, storage, clocks and randomness. Native results are 371 PASS / 0 FAIL with 14,907 assertions, including 40 new cases and 331 selected regressions. ASan, UBSan and leak detection are enabled. Intentional selector rejection controls and historical capability refusals remain distinct from unexpected failures. Historical R27/U27 files are unchanged; generated copies retain their explicitly documented earlier capability adaptations. No complete historical firmware suite or physical acceptance is newly claimed.

## Environment and provenance

* Host: Linux; Python 3.12.14; GNU Bash 5.2.37.
* Native C++: Debian g++ 14.2.0 (`14.2.0-19`), C++17, ASan/UBSan and leak detection.
* Arduino CLI: 1.3.1, commit `08ff7e2b`, release date 2025-08-28.
* Target compiler: `xtensa-esp-elf-g++` 14.2.0, crosstool-NG `esp-14.2.0_20241119`.
* Core/profile: isolated Arduino ESP32 3.3.0; ESP32-S3, 16 MiB custom partitions, PSRAM disabled, USB-OTG/TinyUSB and CDC-on-boot, existing flash/CPU configuration. Exact FQBN and flags are in the build receipt.

The build preserves all 177 pinned SDK archive identities, startup/HID/NVS/ownership safeguards, source selectors, linked call edges and ELF-to-BIN verification. No global Arduino core or SDK is patched. Compiler frames and static/object sizes are not physical heap, task-stack high-water, timing or host-delivery measurements. Host tooling compatibility targets remain High Sierra 10.13.6, Bash 3.2, Python 3.8 and esptool 4.12; running these tests on Linux does not establish native Mac execution.

## Later package verification

After successful source/native/build/link checks, inspect `python3 tests/text_keyboard/package.py --help`. Commit the reviewed source before binding the package source revision. Package/installer checks must use disposable public copies and synthetic tool responses only. Bind exact current randomization/jitter rollback. Publish only the new branch/archive, download the commit-pinned ZIP and compare size/hash, then verify prior remote refs unchanged. Package/publication results must be recorded separately after execution; this document does not claim they have happened. No LED helper is required.
