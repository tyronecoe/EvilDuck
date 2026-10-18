# Reproducing this build-input investigation

Baseline: `d32a60bd3fef73e38293f95905f5905eb41b32fd`. New branch:
`caps-queue-macos-install`. No historical source/profile/verifier is edited.
All commands here are cloud/offline software work, not owner-device instructions.
Use NEW external output directories; do not overwrite previous evidence.

## Actual environments and network recovery

Linux cloud; Python3.12.14, ArduinoCLI1.3.1, GCC14.2.0, Node24.19.0.
The prior attempt's fresh core remained under `/workspace/tooling/arduino/data`.
The managed network policy is unrestricted through the supported session proxy.
The initial CLI attempt in the preceding task did not use its proxy configuration.
In this attempt a separate CLI config explicitly uses the existing configured
HTTPS proxy via `network.proxy`; no secret value is printed or committed.
Index/update and installation then succeeded. No owner Mac installation or global
core modification is involved.

Recorded official index URL:
`https://espressif.github.io/arduino-esp32/package_esp32_index.json`.
Recorded release URL:
`https://github.com/espressif/arduino-esp32/releases/download/3.3.0/esp32-3.3.0.zip`.
Verify its SHA before extraction; do not replace the value to accept a mismatch.

Actual clean CLI data/config (external, not Git):
`/workspace/scratch/mac-recovery/cli-data` and `cli-config.json`.
The config points only at disposable data/download/user paths and uses the supported
proxy. Existing tools/core in `/workspace/tooling/arduino` remain unpatched.

```sh
/workspace/tooling/arduino/bin/arduino-cli --config-file /workspace/scratch/mac-recovery/cli-config.json core update-index
/workspace/tooling/arduino/bin/arduino-cli --config-file /workspace/scratch/mac-recovery/cli-config.json core install esp32:esp32@3.3.0
```

These operations were executed, not merely proposed. CLI uses publisher archive
checksums. The already verified c8525462 release was separately extracted into
`/workspace/scratch/mac-recovery/fresh-extraction/esp32-3.3.0`. Both trees have
exactly the same hashed records; the CLI also adds ignored root `installed.json`.

## Exact inventory semantics

```sh
python3 tests/mac_install/core_inventory.py --root /workspace/scratch/mac-recovery/fresh-extraction/esp32-3.3.0 --compare /workspace/scratch/mac-recovery/cli-data/packages/esp32/hardware/esp32/3.3.0 --output /tmp/raw-vs-cli-NEW.json
```

Uses sorted Path.rglob, is_file/read_bytes (following file links), exactly the root
installed.json exclusion, compact JSON path/hash records, no permission/mtime input.
Symlinks are listed separately. This was also compared against the existing manual
extraction. Complete original/patched records are committed in
`docs/mac-install-core-inventory.json`; historical full records are unavailable.

The verified raw source was COPIED into NEW isolated directories for HID-only and
HID+NVS stages. Apply only the existing pinned proposal patch files using
`patch --batch --fuzz=0 -p1 -i ABSOLUTE_PATCH_PATH`. Never patch the installed core.
Only the declared two source files change in the full patched proposal.

## Input proposal and fault tests

Actual paths below may be replaced with independently verified equivalent paths;
results/output directories must not exist:

```sh
python3 tests/mac_install/proposed_profile.py --archive /workspace/tooling/arduino/downloads/esp32-3.3.0.zip --raw /workspace/scratch/mac-recovery/fresh-extraction/esp32-3.3.0 --patched /workspace/scratch/mac-recovery/proposed-patched-core --sdk /workspace/scratch/mac-recovery/cli-data/packages/esp32/tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3 --compiler /workspace/tooling/arduino/data/packages/esp32/tools/esp-x32/2411/bin/xtensa-esp32s3-elf-g++ --output /tmp/proposed-inputs-NEW.json
python3 tests/mac_install/test_profile.py --archive /workspace/tooling/arduino/downloads/esp32-3.3.0.zip --raw /workspace/scratch/mac-recovery/fresh-extraction/esp32-3.3.0 --patched /workspace/scratch/mac-recovery/proposed-patched-core --sdk /workspace/scratch/mac-recovery/cli-data/packages/esp32/tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3 --compiler /workspace/tooling/arduino/data/packages/esp32/tools/esp-x32/2411/bin/xtensa-esp32s3-elf-g++ --results /tmp/profile-tests-NEW.json
python3 tests/mac_install/test_installer.py --results /tmp/installer-tests-NEW.json
```

The proposal check returns input verification, **not** build/install approval.
The installer tests use injected responses and temporary files, not serial devices.
The synthetic application fixture is not valid firmware. CLI actions remain unbound
and cannot reach device I/O. Tests check exact rejection reasons, not just any error,
so a wrong earlier gate cannot masquerade as a successful fault injection.

## Actual protected-build retry

```sh
python3 tools/build_s3_patched.py --controlled-normal-start --core-dir /workspace/scratch/mac-recovery/cli-data/packages/esp32/hardware/esp32/3.3.0 --user-dir /workspace/tooling/arduino/user --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --isolation-dir /workspace/scratch/mac-recovery/historical-build-isolation --build-dir /workspace/scratch/mac-recovery/historical-target-build --jobs 2
```

Executed exit1: `FAIL: Core tree mismatch`, before copying/patching/compiling.
The historical validator was NOT altered. Do not call this a successful build.
The exact historical fingerprints and proposed new fingerprints are in the report.

## Fresh relevant software regressions

```sh
python3 tests/caps_queue/run_tests.py --build-dir /workspace/scratch/mac-recovery/regression-native --results /workspace/scratch/mac-recovery/regression-native.json
node tests/caps_queue/test_ui.cjs /workspace/scratch/mac-recovery/regression-native/sources/webfiles.h
python3 tests/stage28h/verify_freeze.py
```

125 native cases /6574 assertions with ASan/UBSan/leak detection;18 JS groups /
31 assertions. Earlier full-suite totals are not reused as fresh runs.

esptool4.12.0's official source archive was downloaded into this scratch directory,
SHA checked (`d797f6529d582173508baf0572542ddadf53aae8c92c84ea9f420f242464103c`),
then installed only in `/workspace/scratch/mac-recovery/esptool-env`. Python requirement
>=3.7 supports the owner's recorded Python3.8 at the version-constraint level.
Only version/help and a parser-only AST prefix execute; no connection dispatcher.

```sh
/workspace/scratch/mac-recovery/esptool-env/bin/python -m esptool version
/workspace/scratch/mac-recovery/esptool-env/bin/python tests/stop_led_package/tool_parser_tests.py --directory /workspace/scratch/mac-recovery/parser-fixtures --results /tmp/parser-tests-NEW.json
```

Parser fixture filenames use the public working image only for argument parsing;
no new image or hardware compatibility is implied. No actual write operation is
executed. Native High Sierra serial/USB behavior remains owner-run and untested.
