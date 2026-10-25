# Offline reproduction — composed uppercase candidate

These commands build/test disposable artifacts only; they do not open a board, emit real HID, execute owner scripts or invoke an installer. Use fresh output directories. Historical overlays and installed dependencies remain unchanged. The new composition must validate exact before/after hashes and explicit selectors.

```bash
python3 tests/random_uppercase/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-uppercase-native --results /workspace/scratch/NEW-uppercase-native.json
python3 tests/random_uppercase/build_candidate.py --output-dir /workspace/scratch/NEW-uppercase-build --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/random_uppercase/verify_link.py --build-root /workspace/scratch/NEW-uppercase-build --output /workspace/scratch/NEW-uppercase-linked.json
python3 tests/stage28h/verify_freeze.py
```

Tests use actual composed compiler/runtime/backend modules with mocked HID, storage, clocks and entropy; no reference-repository scripts or owner payloads are run. Preserve historical R27's uppercase-rejection expectation in its original suite. The new suite must record the intentional new expectation while retaining rejection of other unimplemented groups. Expected negative controls and historical classifications remain separate from unexpected failures.

The build retains the approved separately pinned archive-feedback profile and all 177 SDK archive identities, source/selector checks, USB/NVS/startup safeguards, linked call edges and ELF-to-BIN regeneration. No global core/SDK is patched. Compiler frame estimates and Linux object sizes are not physical stack-high-water or latency measurements.

After successful tests, clean build and post-link verification, inspect `python3 tests/random_uppercase/package.py --help`. Commit the reviewed source before binding its source SHA in the package. Packaging/installer tests must use disposable public copies and fake esptool only. Require the exact accepted lowercase rollback, not the older preprocessing image. Publish only the verified new branch/archive, download the commit-pinned ZIP and match size/SHA-256. Verify earlier remote refs stayed unchanged. No LED helper is needed or bundled.
