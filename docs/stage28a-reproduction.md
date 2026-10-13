# Stage28A offline reproduction

NOT FLASH-AUTHORIZED. No Stage26 artifacts, production core/SDK or deployable profile is rebuilt.
Use fresh external destinations and the already verified Stage26 target compilation database:

```sh
python3 tests/stage28a/run_tests.py --build-dir "$NEW_CALL_TEST_DIR" \
  --results "$NEW_CALL_RESULTS"
python3 tests/stage27b/run_tests.py --build-dir "$NEW_REGRESSION_TEST_DIR" \
  --results "$NEW_REGRESSION_RESULTS"
python3 tests/stage28a/target_check.py --baseline-build "$FROZEN_STAGE26_BUILD_DIR" \
  --original-core "$ORIGINAL_CORE_3_3_0" --output-dir "$NEW_TARGET_OBJECT_DIR"
```

Both test runners compile actual language_preview/core.cpp with ASan/UBSan, leak detection,
C++17, warnings-as-errors and per-case process timeouts. The new runner reuses only the Stage27B
mock/assertion helpers, not historical results. Its stage27b_main symbol is not executed; the
complete Stage27B case list is actually executed by the separate regression runner. No hardware,
owner script, credentials, network or real HID interface is invoked.

The Stage28A target checker uses the pinned compiler/flags and checks original plus frozen
patched-core source hashes, SDK NVS archive/config hashes and compiler identity. It compiles
only core.o and a sizes metadata object. A28-byte type-sizes.raw section dump encodes seven
sizeof measurements; it is not a firmware image. No firmware ELF, application BIN, partition
artifact, upload recipe or new installation profile is generated. The old Stage27B helper and
historical resource receipts remain unchanged.

Exact executed stdout/assertions and commands are committed in stage28a-test-results.json.
Source/core/SDK/compiler/object hashes are in stage28a-source-hashes.json and target-build.json.
Repeated build paths can change debug/object hashes, so compare source and dependency identity
as well as measured sections. Object sections are not a linked application flash-size estimate.
Program/Runtime lifetimes, caller callback latency and single-thread API remain explicit contracts.
