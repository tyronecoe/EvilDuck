# Stage 21 offline reproduction

All operations below prepare external source/build/test files only. They do not discover
serial devices, upload, format, erase, flash, run owner scripts or send real HID reports.
Keep fresh paths outside the repository and installed Arduino/core/SDK directories.

Use the Stage20 pinned environment: Arduino ESP32 3.3.0, CLI1.3.1, Xtensa GCC14.2.0,
SDK `idf-release_v5.5-b66b5448-v1`, existing libraries, USB-OTG/TinyUSB/CDC, CPU240/QIO80,
PSRAM disabled and exact production `partitions.csv`. The isolated wrapper applies only
Stage16 HID and Stage18 NVS patches and fails closed on source/tree/archive/config or
ELF mismatch. Do not use local core2.0.17 or modify installed SDK files.

```sh
ED_CORE='/absolute/path/to/data/packages/esp32/hardware/esp32/3.3.0'
ED_USER='/absolute/path/to/arduino/user'
ED_CLI='/absolute/path/to/arduino-cli'
ED_NORMAL_ISO='/absolute/path/new-stage21-normal-core'
ED_SAFE_ISO='/absolute/path/new-stage21-safe-core'
ED_NORMAL_BUILD='/absolute/path/new-stage21-normal-build'
ED_SAFE_BUILD='/absolute/path/new-stage21-safe-build'
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
 --arduino-cli "$ED_CLI" --isolation-dir "$ED_NORMAL_ISO" --build-dir "$ED_NORMAL_BUILD"
python3 tools/build_s3_patched.py --core-dir "$ED_CORE" --user-dir "$ED_USER" \
 --arduino-cli "$ED_CLI" --isolation-dir "$ED_SAFE_ISO" --build-dir "$ED_SAFE_BUILD" --deployment-safe-start
ED_NORMAL_CORE="$ED_NORMAL_ISO/data/packages/esp32/hardware/esp32/3.3.0"
ED_SAFE_CORE="$ED_SAFE_ISO/data/packages/esp32/hardware/esp32/3.3.0"
ED_REFERENCE='/absolute/path/new-stage21-reference-source'
python3 tools/startup_reference_prepare.py --prepare-dir "$ED_REFERENCE"
python3 tools/startup_reference_prepare.py --verify-dir "$ED_REFERENCE"
```

Reference downloader uses immutable official commit URLs, TLS and recorded hashes.
It writes only a new reference directory, never installs/replaces SDK sources. Existing
Stage19 SDK source/generator and Stage20 partition source preparers remain applicable.
Native source tests require Linux g++/ASan/UBSan; High Sierra execution of these new
native test binaries/toolchain is not established or required for private owner preflight.

```sh
ED_SDK_SOURCE='/absolute/path/hash-verified-stage19-sdk-source'
ED_PARTITION_SOURCE='/absolute/path/verified-partition-reference/partition_target.c'
python3 tests/stage21/run_tests.py --sdk-source "$ED_SDK_SOURCE" \
 --partition-source "$ED_PARTITION_SOURCE" --patched-core "$ED_NORMAL_CORE" --reference-source "$ED_REFERENCE" \
 --build-dir /absolute/path/new-stage21-native --results /absolute/path/new-stage21-native.json
python3 tests/stage21/integration_tests.py --original-core "$ED_CORE" \
 --normal-core "$ED_NORMAL_CORE" --safe-core "$ED_SAFE_CORE" \
 --normal-build "$ED_NORMAL_BUILD" --safe-build "$ED_SAFE_BUILD" \
 --reference-source "$ED_REFERENCE" --results /absolute/path/new-stage21-integration.json
python3 tools/analyze_s3_stack.py --build-dir "$ED_NORMAL_BUILD" --output /absolute/path/new-normal-stack.json
python3 tools/analyze_s3_stack.py --build-dir "$ED_SAFE_BUILD" --output /absolute/path/new-safe-stack.json
```

All previous Stage1–20 runners remain required, including Stage2.5 manifest/partition
guards, Stage9 observations, Stage15 historical source diagnostic classification,
Stage16 routing/dependency guards, Stage17/18/19/20 suites and both Stage20 blob runners.
Stage2 contains the five Stage1 tests and historical language diagnostic runner. Stage15
historical backend is obtained from its original commit, not current production code.
Each suite's README/--help specifies arguments; use actual new clean build paths for
provenance checks. Exact executed inventories and results are in stage21-results.json.

`tools/inspect_startup_elf.py` takes an actual generated ELF plus pinned `--nm` and
`--objdump` paths, and a fresh `--output`. It inventories file-backed native startup
arrays and selected instruction/direct-call evidence without executing them. It is
not a complete boot or transitive flash-write proof.

No read-only firmware candidate is built here. A future wrapper must explicitly pair
a pre-init descriptor requirement and isolated reviewed table/profile while leaving
existing builders/guards unchanged. Temporary test CSV/binary is discarded; no merged
build image is approved for migration. Rollback of this investigation is selecting the
preserved Stage20 branch; no installed toolchain change needs undoing. Removal of external
test/build directories is optional local housekeeping, never physical recovery.
