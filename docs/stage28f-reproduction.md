# Stage28F offline reproduction

Read command-contract/report first. Stage26 firmware and Stage27A are not targets.
GCC C++17, Python3 and existing pinned toolchain are required for the complete cloud workflow.
No setup change or installation was needed here. No server/start process or environment draft
update is required. Reuse the checkout; do not build/upload Arduino sketches for this preview.

Run each old runner with a fresh external directory and JSON result; do not overwrite prior runs:

```sh
stage28f_results="$(mktemp -d /tmp/evilduck28f-tests.XXXXXX)"
for stage28f_suite in stage27b stage28a stage28b stage28c stage28d stage28e stage28f; do
  python3 "tests/$stage28f_suite/run_tests.py" \
    --build-dir "$stage28f_results/$stage28f_suite-build" \
    --results "$stage28f_results/$stage28f_suite.json" || exit 1
done
python3 tests/stage28f/verify_freeze.py
```

The runners compile only host preview/mock code, with existing warning/sanitizer discipline,
20-second case timeouts, ASan detect_leaks=1 and UBSan halt_on_error=1. No test installation
or HID endpoint exists. Exact names and commands are in tests/stage28f/test-results.json.

Cloud target evidence uses the existing pinned directories, not a freshly installed core:

```sh
python3 tests/stage28f/target_check.py \
  --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled \
  --original-core /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --output-dir /tmp/evilduck28f-target-new
```

Output directory must not exist. This validates original/protected core, compiler and SDK hashes,
reuses frozen compiler flags and builds four UNLINKED objects only: core, keyboard, bridge and
size metadata. No new firmware ELF/BIN/UF2, production linker invocation or upload. Any pin failure
is a blocker; do not weaken checks. Report preserves exact commands, objects and stack/section
sizes. `/workspace` paths are cloud provenance, not download links or owner Mac tool locations.

Portable fixed-buffer smoke: see stage28f-macos-smoke.md for optional native Apple recipe.
Linux verification used g++ with the same sanitizers and warnings, linking only preview host
code and tests/stage28f/mac_smoke.cpp. A Linux executable is not installable EvilDuck firmware.

For future publication, capture all refs using `git ls-remote --refs origin` before/after, then
pass the two saved files to verify_freeze.py --remote-before/--remote-after. The verifier checks
all preexisting refs; separately check only the reviewed new branch was added at the exact SHA.
