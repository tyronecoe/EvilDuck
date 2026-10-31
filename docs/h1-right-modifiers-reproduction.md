# Right-side modifiers on H1 — offline reproduction

This release composes the reviewed H1 source, then applies the two-header right-modifier layer. Historical source layers/builders are unchanged. All preparation/build work uses disposable directories and the approved isolated Arduino ESP32 3.3.0 archive profile, not global installations. No command below opens a board or executes real HID output. Choose fresh output paths; the recorded run directories are preserved and must not be overwritten to hide failures.

Recorded composed-module invocation:

```bash
python3 tests/h1_right_modifiers/run_tests.py \
  --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /workspace/scratch/h1-right-modifiers/native-v1 \
  --results /workspace/scratch/h1-right-modifiers/native-v1.json
```

The runner includes inherited H1/lock-wait and relevant earlier composed regressions. Its receipt distinguishes the new cases, generated identity adjustments, source-selector refusals, assertion counts and sanitizers. Test-only access-control relaxation is never permitted by the target build/link checks. New source names use the existing keyboard event/ownership path; no alternate HID implementation or H1 numeric contract is introduced.

Recorded clean target build and final link checks:

```bash
python3 tests/h1_right_modifiers/build_candidate.py \
  --output-dir /workspace/scratch/h1-right-modifiers/build-v1 \
  --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json \
  --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 tests/h1_right_modifiers/verify_link.py \
  --build-root /workspace/scratch/h1-right-modifiers/build-v1 \
  --output /workspace/scratch/h1-right-modifiers/linked-v1.json
```

Build and link receipts pin the actual executed wrappers, unchanged historical parents, final source identities, compiler flags, core/SDK identities and final ELF/BIN. Missing/wrong selectors fail closed. Full H1 experimental identity remains explicit; a build-ID string is not physical application readback evidence.

After the implementation source commit and verified build are recorded, the separate app packager uses `--source-commit` for the packaging tools commit. `firmware_source_commit` separately identifies the reviewed implementation. It requires the exact candidate/ELF/receipt identities and extracts the unchanged cf42 source/text-v2 application from its pinned prior public ZIP for rollback. See package CLI `--help` and the final report/artifact receipt for the bound identities. Source/core/SDK pin checks are not bypassed to accommodate the new header hashes.

Focused public-copy checks use the new packager's extracted directory and archive, with the same pinned OTA template as prior app-only releases:

```bash
python3 tests/h1_right_modifiers/test_package.py \
  --directory /workspace/scratch/h1-right-modifiers/package \
  --archive /workspace/scratch/h1-right-modifiers/evilduck-routeb-right-modifiers-h1-experimental-macos-v1.zip \
  --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin \
  --results /workspace/scratch/h1-right-modifiers/package-tests.json
python3 tests/h1_right_modifiers/test_bound_installer.py \
  --directory /workspace/scratch/h1-right-modifiers/package \
  --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin \
  --results /workspace/scratch/h1-right-modifiers/installer-tests.json
```

Only synthetic metadata/tool responses are used by these checks. The full physical High Sierra environment, host key behavior, boot, heap, stack high-water and precise timing are not measured by them.

On the owner’s Mac, first verify the ZIP checksum supplied with publication, extract into a new directory and run only the offline local check:

```bash
python3 preflight.py --directory .
```

Expect integrity PASS with no supplied installed metadata, no selected write ranges and no hardware access/installation authorization. Read INSTALL-MAC.md, ROLLBACK-MAC.md and OWNER-CHECK.md before any separately approved device operation. The installer’s default `check` is a device-reading action, not this offline check. No automatic Start, retry, settings reset, EDR1 change, flashing, OTA or physical repetition is part of development.
