# Stage28B offline reproduction

NOT FLASH-AUTHORIZED. Use existing pinned tooling, fresh external destinations:

```sh
python3 tests/stage28b/run_tests.py --build-dir "$NEW_BLOCK_TEST_DIR" --results "$NEW_BLOCK_RESULTS"
python3 tests/stage28a/run_tests.py --build-dir "$NEW_CALL_TEST_DIR" --results "$NEW_CALL_RESULTS"
python3 tests/stage27b/run_tests.py --build-dir "$NEW_REGRESSION_DIR" --results "$NEW_REGRESSION_RESULTS"
python3 tests/stage28b/target_check.py --baseline-build "$FROZEN_STAGE26_BUILD_DIR" \
  --original-core "$ORIGINAL_CORE_3_3_0" --output-dir "$NEW_TARGET_OBJECT_DIR"
python3 tests/stage28b/verify_freeze.py
```

All runners compile actual preview core with C++17, warnings-as-errors, ASan/UBSan and
ASAN_OPTIONS=detect_leaks=1; cases have process timeouts. The new test source includes prior
mock helpers only; its renamed stage27b_main is not executed. Complete prior case lists are
executed separately by their unchanged runners. JSON records exact commands/stdout/assertions.
No production firmware test counts or historical diagnostic outcomes are recycled.

Target checking verifies original/isolated protected Arduino3.3.0 sources, SDK archive/config
and compiler hashes against the frozen Stage26 compilation database. It uses existing ESP32-S3
PSRAM-disabled,16MiB/QIO80/CPU240/USB-OTG/TinyUSB/CDC flags. Only core.o, sizes.o and a32-byte
raw sizeof metadata section are generated. No linked firmware ELF/BIN, partition image or
installable profile. The sizes metadata contains eight measurements including TextCursor.
Global toolchains and frozen build outputs are never modified. Debug paths can affect object
hashes; compare source/dependency provenance and sections, not a fictional reproducible firmware.

Read-only source freeze checks235 files against immutable Stage26 Git objects. Remote-head
snapshots can additionally be compared using --remote-before and --remote-after (saved
`git ls-remote --heads origin` text). Only the Stage28B branch may be newly published; do not
move prior refs or auto-merge. No physical operation or owner script is part of reproduction.
