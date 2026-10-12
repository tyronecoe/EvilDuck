# Stage 23 offline reproduction and rollback

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING**

Use the existing Linux pinned Arduino ESP32 3.3.0/GCC14.2/ESP-IDF5.5 environment and
libraries. High Sierra target-toolchain compatibility is not established. Existing
normal/safe wrappers and original SDK identities remain unchanged. No serial, upload,
flash, erase, format or OTA command exists in this workflow.

Build both production profiles with tools/build_s3_patched.py as documented in Stage22.
Use fresh external core/build directories. Obtain partition_target.c from the immutable
URL in stage20-partition-reference.json; its SHA is checked before compiling. Keep
reference sources outside the checkout and global installation. Run:

```sh
python3 tools/stage23_sdk_cleanup.py --core-dir "$VERIFIED_NORMAL_CORE" \
  --build-dir "$VERIFIED_NORMAL_BUILD" --source "$PINNED_PARTITION_TARGET_C" \
  --output-dir "$NEW_EXTERNAL_SDK_REBUILD"
```

This verifies the full normal build, compiler identity, original SDK inputs and source,
then rebuilds the unchanged and patched component. Runtime section/relocation/ABI checks
must succeed, and only the approved scanner changes may differ. The unrelated archive
member is copied byte-identically. Repeat in another fresh directory and compare hashes;
the wrapper's independently pinned archive/hash/tree checks never trust an arbitrary
replacement merely because its filename matches.

```sh
python3 tools/stage23_candidate.py --experimental-readonly-iterator-cleanup \
  --core-dir "$ORIGINAL_CORE" --user-dir "$LIBRARIES" --arduino-cli "$CLI" \
  --verified-sdk-rebuild-dir "$NEW_EXTERNAL_SDK_REBUILD" \
  --isolation-dir "$NEW_EXTERNAL_CANDIDATE_CORE" --build-dir "$NEW_EXTERNAL_CANDIDATE_BUILD"
```

The explicit selector, copied core/SDK, unchanged Stage22 gate/table, exact corrected
SDK tree and mandatory linked-ELF verification form a separate reviewed candidate.
FQBN remains `esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default`.
No existing builder is relaxed, global SDK altered, descriptor changed or normal
operation enabled. The candidate still carries the Stage22 quiescent identifier;
Stage23 provenance additionally identifies the corrected SDK and actual linked release.
Padded merged output is discarded and is not a review/deployment artifact.

Run tests/stage23/run_tests.py with --partition-dir, --reference-source, fresh --build-dir
and --results. It instruments real native allocations for exact pinned iterator/scanner
source, retaining the unpatched LSan failure separately. protection_tests.py reruns actual
SDK source components with the corrected scanner; iterator adapters there have no heap,
so ownership is proved by the separate real-allocation harness. gate_tests.py compiles
actual corrected-candidate core/gate/setup/loop with the same pinned SDK source and
synthetic interfaces. integration_tests.py verifies the real final build and dependency
separation. Exact arguments and outcomes are recorded in stage23-results.json/receipts.

All tests use synthetic data and mocked physical interfaces. Optional original owner
backups are neither inputs nor shipped artifacts. Stage22 regression checks deliberately
retain the original Stage22 SDK fixture to confirm historical guards still reject a new
unapproved dependency; new Stage23 tests cover the corrected candidate independently.

Rollback of software preparation means selecting the original Stage22 builder/pins and
discarding disposable Stage23 output directories. Nothing was installed globally or
physically, so no device rollback is necessary here. Original backups must remain intact
as optional resources. Future physical recovery/provisioning requires separate compatible
image verification, range review and owner authorization; no physical steps are supplied.
