# Stage28C offline reproduction

Use fresh external directories, the existing verified toolchain and frozen Stage26 build:

```sh
python3 tests/stage28c/run_tests.py --build-dir "$NEW_COMPILE_TEST_DIR" --results "$NEW_COMPILE_RESULTS"
python3 tests/stage28b/run_tests.py --build-dir "$NEW_BLOCK_TEST_DIR" --results "$NEW_BLOCK_RESULTS"
python3 tests/stage28a/run_tests.py --build-dir "$NEW_CALL_TEST_DIR" --results "$NEW_CALL_RESULTS"
python3 tests/stage27b/run_tests.py --build-dir "$NEW_REGRESSION_DIR" --results "$NEW_REGRESSION_RESULTS"
python3 tests/stage28c/target_check.py --baseline-build "$FROZEN_STAGE26_BUILD_DIR" \
  --original-core "$ORIGINAL_CORE_3_3_0" --output-dir "$NEW_TARGET_OBJECT_DIR"
python3 tests/stage28c/verify_freeze.py
```

Actual preview core is freshly compiled with ASan/UBSan, leak detection, C++17 and warnings-as-
errors. New tests reuse prior mock/assertion helpers only, not historical outcomes. JSON captures
all commands/results/assertions. Each test group has an external process timeout; compiler itself
has65536-step cap. New hardware/source adapters and physical tests do not exist.

Target check preserves Arduino3.3.0 original/protected core and SDK/compiler hashes plus Stage26
flags. Only core.o and metadata sizes.o are produced; the latter includes core.cpp to expose
sizeof the internal Compiler type and is never linked. Its48-byte readonly metadata contains12
sizes. Stack/sections/undefined symbols are reported from core.o/core.su only. No firmware ELF,
BIN, partition artifact, deployable profile or installation procedure is generated. Global tooling
and frozen artifacts are unchanged. Paths affect object debug hashes; source/SDK pins remain exact.

Example cooperative caller (RAM source lifetime remains caller-owned):

```cpp
MemoryReader source{bytes, length, 0};
CompileSession session; // own outside a small scheduler stack if necessary
session.start(program, source.reader(), "mock.duck");
// On each external scheduler turn: session.step(); inspect state/work/error.
// Start a mock Runtime only after CompileState::Complete. Cancel explicitly as needed.
```

Program::compile retains the old signature but synchronously drives this same state machine.
It does not retain source input afterward; it uses a local session with documented stack cost.
Remote snapshot checks accept --remote-before/--remote-after saved git ls-remote --heads output;
only the new Stage28C branch may change. No physical operation is part of reproduction.
