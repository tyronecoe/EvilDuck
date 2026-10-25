# Offline reproduction — composed randomization/jitter candidate

These commands build/test disposable artifacts only; they do not open a board, emit real HID, execute owner scripts or invoke an installer. Use fresh output directories. Historical overlays and installed dependencies remain unchanged. The new composition must validate exact before/after hashes and explicit selectors.

```bash
python3 tests/randomization_jitter/run_tests.py --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --build-dir /workspace/scratch/NEW-randomization-jitter-native --results /workspace/scratch/NEW-randomization-jitter-native.json
python3 tests/randomization_jitter/build_candidate.py --output-dir /workspace/scratch/NEW-randomization-jitter-build --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/randomization_jitter/verify_link.py --build-root /workspace/scratch/NEW-randomization-jitter-build --output /workspace/scratch/NEW-randomization-jitter-linked.json
python3 tests/stage28h/verify_freeze.py
```

Tests use actual composed compiler/runtime/backend modules with mocked HID, storage, clocks and entropy; no reference-repository scripts or owner payloads are run. Historical R27/U27 refusal fixtures remain unchanged; generated copies remove only the newly implemented commands from their old rejection lists. The new suite must record the intentional new expectation while retaining rejection of other unimplemented groups. Expected negative controls and historical classifications remain separate from unexpected failures.

The build retains the approved separately pinned archive-feedback profile and all 177 SDK archive identities, source/selector checks, USB/NVS/startup safeguards, linked call edges and ELF-to-BIN regeneration. No global core/SDK is patched. Compiler frame estimates and Linux object sizes are not physical stack-high-water or latency measurements.

After successful tests, clean build and post-link verification, inspect `python3 tests/randomization_jitter/package.py --help`. Commit the reviewed source before binding its source SHA in the package. Packaging/installer tests must use disposable public copies and fake esptool only. Require the exact accepted uppercase rollback, not the older preprocessing image. Publish only the verified new branch/archive, download the commit-pinned ZIP and match size/SHA-256. Verify earlier remote refs stayed unchanged. No LED helper is needed or bundled.
