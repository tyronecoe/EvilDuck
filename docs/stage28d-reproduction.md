# Stage28D reproduction — offline only

Use existing verified tooling and fresh external outputs:

```sh
python3 tests/stage28d/run_tests.py --build-dir "$NEW_KEYBOARD_TEST_DIR" --results "$NEW_KEYBOARD_RESULTS"
python3 tests/stage28c/run_tests.py --build-dir "$NEW_COMPILE_DIR" --results "$NEW_COMPILE_RESULTS"
python3 tests/stage28b/run_tests.py --build-dir "$NEW_BLOCK_DIR" --results "$NEW_BLOCK_RESULTS"
python3 tests/stage28a/run_tests.py --build-dir "$NEW_CALL_DIR" --results "$NEW_CALL_RESULTS"
python3 tests/stage27b/run_tests.py --build-dir "$NEW_REGRESSION_DIR" --results "$NEW_REGRESSION_RESULTS"
python3 tests/stage28d/target_check.py --baseline-build "$FROZEN_STAGE26_BUILD_DIR" \
  --original-core "$ORIGINAL_CORE_3_3_0" --output-dir "$NEW_OBJECT_DIR"
python3 tests/stage28d/verify_freeze.py
```

All tests compile actual modules with ASan/UBSan, leak detection, warnings-as-errors and per-group
process timeouts. The new suite links core.cpp plus keyboard.cpp and reuses only mock/assertion
helpers. Old runners remain unchanged and are actually executed, not copied as historical passes.
No physical endpoint/OS/storage reader exists. Mock reports are vectors in caller-owned RAM.

Target checks retain all Stage28C original/protected core, SDK/config/compiler hashes and flags.
Compile only core.o, keyboard.o and sizes.o. The unlinked metadata TU includes core.cpp to measure
internal Compiler plus keyboard.h; its64-byte readonly size dump has16 type measurements and
is not USB descriptor/firmware metadata. Core/planner sections and stack estimates are separate.
No linked firmware ELF/BIN, installable profile, partition image or hardware command is created.
Global tooling and frozen Stage26 artifacts are never modified.

Planner::start must first accept a mock neutral sync. Admit hold/release/tap/character only at
Ready, drive step(now) externally, and inspect Accepted evidence independently of desired state.
Cancel clears ownership, then drain explicitly if neutral is unconfirmed. Restart is refused until
terminal state has neutral evidence. Callback/context must remain valid through future drain.
No automatic destructor cleanup or physical release. API is explicitly single-threaded.
