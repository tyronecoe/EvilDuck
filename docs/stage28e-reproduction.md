# Stage28E reproduction — offline only

Use fresh external destinations and the established verified tooling:

```sh
python3 tests/stage28e/run_tests.py --build-dir "$NEW_BRIDGE_TEST_DIR" --results "$NEW_BRIDGE_RESULTS"
python3 tests/stage28d/run_tests.py --build-dir "$NEW_PLANNER_DIR" --results "$NEW_PLANNER_RESULTS"
python3 tests/stage28c/run_tests.py --build-dir "$NEW_COMPILE_DIR" --results "$NEW_COMPILE_RESULTS"
python3 tests/stage28b/run_tests.py --build-dir "$NEW_BLOCK_DIR" --results "$NEW_BLOCK_RESULTS"
python3 tests/stage28a/run_tests.py --build-dir "$NEW_CALL_DIR" --results "$NEW_CALL_RESULTS"
python3 tests/stage27b/run_tests.py --build-dir "$NEW_REGRESSION_DIR" --results "$NEW_REGRESSION_RESULTS"
python3 tests/stage28e/target_check.py --baseline-build "$FROZEN_STAGE26_BUILD_DIR" \
  --original-core "$ORIGINAL_CORE_3_3_0" --output-dir "$NEW_OBJECT_DIR"
python3 tests/stage28e/verify_freeze.py
```

The new runner links actual core.cpp, keyboard.cpp and bridge.cpp, with mock report sink and
externally supplied virtual timestamps. It includes only prior Stage27B assertion helpers,
not historical outcomes. All six runners freshly execute ASan/UBSan with leak detection,
warnings-as-errors and process timeouts. No hardware operations or owner payloads.

Object checker preserves exact original/protected Arduino3.3.0, SDK/config/compiler source/hash
checks and target flags. Generate core.o, keyboard.o, bridge.o and unlinked sizes.o only. The
72-byte readonly sizeof dump measures18 types (including internal Compiler through metadata TU);
it is not USB metadata, firmware ELF/BIN or a deployable profile. Module sections/stack estimates
are separate and do not measure production flash/OTA usage. No global toolchain changes.

Read-only ref verification accepts saved git ls-remote --refs output with --remote-before and
--remote-after and checks every existing ref. Source hashes/freeze receipts are in versioned docs.
Only new Stage28E may be pushed. See stage28e-macos-smoke.md for the separate native Apple
host-only recipe; Linux flags and sanitizer support are not assumed on High Sierra.

API order: begin(mockReportSink,context,now); step(now) until Prepared; optionally admit owner
setup and step until Planner Ready; start(program,now); externally call step(now) until terminal.
Inspect Runtime state/error and accepted/neutral evidence. If needed, call drain explicitly and
step only its cleanup before a fresh begin. Never externally step/mutate owned const observations.
