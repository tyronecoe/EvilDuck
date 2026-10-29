# Offline reproduction — composed source/text portability

The native test command actually executed was:

```bash
python3 tests/source_text/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/source-text/native-v1 --results /workspace/scratch/source-text/native-v1.json
```

Do not reuse that occupied output. Use fresh disposable outputs for reproduction. Commands below do not open hardware, emit HID, execute owner scripts, upload/flash firmware, invoke the installer or contact a device. Exact source/patch guards and inherited dependency predicates remain mandatory.

```bash
python3 tests/source_text/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-source-text-native --results /workspace/scratch/NEW-source-text-native.json
python3 tests/source_text/build_candidate.py --output-dir /workspace/scratch/NEW-source-text-build --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/source_text/verify_link.py --build-root /workspace/scratch/NEW-source-text-build --output /workspace/scratch/NEW-source-text-linked.json
python3 tests/stage28h/verify_freeze.py
```

Fresh native results:435 PASS/0 FAIL,16,922 assertions;32 new cases/1,697 assertions and403 adapted regression cases/15,225 assertions. ASan/UBSan/leak detection completed cleanly, without development compiler/test failures. The full command and per-case output are in source-text-test-results.json. Historical403-case restart results are not reused as fresh success. Generated P14/V11 change BOM refusal to acceptance (17→26 and16→25 assertions); V06 removes two superseded inline-alias refusal inputs (11→7), net+14 assertions. Historical files and classifications remain unchanged. Clean target build and final post-link verification also passed; package/publication results remain pending actual receipts.

The actual clean build/final-link commands were:

```bash
python3 tests/source_text/build_candidate.py --output-dir /workspace/scratch/source-text/build-v1 --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/source_text/verify_link.py --build-root /workspace/scratch/source-text/build-v1 --output /workspace/scratch/source-text/linked-final.json
```

These outputs are occupied. Use new paths for reproduction. The first post-link attempt used linked-v1.json and exposed a prefix-match collision with local signature data; the new verifier now selects executable symbol types and final verification passes without firmware/dependency changes. Exact commands, archive/source/compiler identities and disassembly are in source-text-build.json; resources are in source-text-resources.json. Target compiler is xtensa-esp-elf-g++14.2.0, crosstool-NG esp-14.2.0_20241119. The approved isolated Arduino ESP32 core3.3.0 profile retains ESP32-S3/16MiB custom partitions, PSRAM disabled and existing USB-OTG/TinyUSB/CDC/240MHz/flash settings. All177 SDK archive identities, USB/NVS/startup/ownership safeguards, source selectors and ELF-to-BIN checks pass. Compiler/object/frame data is not physical heap, stack high-water, latency or host-delivery evidence. No global core/SDK changes are authorized.

Host package interfaces target High Sierra10.13.6, Bash3.2, Python3.8 and esptool4.12. The review-only physical BOM procedure is separately documented in OWNER-CHECK.md; it must not be run during offline development.

After tests/build/link pass, commit source before binding the package revision. Use `python3 tests/source_text/package.py --help`; verify exact accepted restart rollback, then run package/mock-installer checks only on disposable public data and synthetic tool responses. Publish only the isolated branch/package, download the commit-pinned archive, verify bytes/hash/app identities, and compare historical refs. Actual package/publication receipts are PENDING; no second ZIP/helper is required.

## Public package checks

```bash
python3 tests/source_text/package.py --directory /workspace/outputs/evilduck-routeb-source-text-portability-macos-v1 --build-root /workspace/scratch/source-text/build-v1 --linked-report docs/source-text-build.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --archive /workspace/outputs/evilduck-routeb-source-text-portability-macos-v1.zip --source-commit b209084ab7afebb64b66e32634151138af3bd1e7
python3 tests/source_text/test_package.py --directory /workspace/outputs/evilduck-routeb-source-text-portability-macos-v1 --archive /workspace/outputs/evilduck-routeb-source-text-portability-macos-v1.zip --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin --results /workspace/scratch/source-text/package-tests.json
python3 tests/source_text/test_bound_installer.py --directory /workspace/outputs/evilduck-routeb-source-text-portability-macos-v1 --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin --results /workspace/scratch/source-text/installer-tests.json
```

Paths are occupied; use fresh names. Reproducing the frozen ZIP requires the source-commit versions of its bundled documents/receipts: the repository report subsequently gains publication evidence. All45 package/38 mock-installer checks passed. No network acceptance snippet was executed by these checks.
