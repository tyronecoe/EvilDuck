# Stage28H cloud/offline reproduction

Base7d391c0900eb4c5eba730abc3143008dcdeb1ae1, clean verified before any edits. Existing checkout,
GCC14.2/Python3/Bash5.2 and pinned Xtensa workflow reused; no install or environment change.
Local owner smoke requires Bash and an existing C++17 compiler only:

```sh
bash tests/stage28h/run_host_smoke.sh
```

Fresh cloud regressions (Linux flags/sanitizers in these Python runners are NOT Mac assumptions):

```sh
stage28h_results="$(mktemp -d /tmp/evilduck28h-tests.XXXXXX)"
for stage28h_suite in stage27b stage28a stage28b stage28c stage28d stage28e stage28f stage28g stage28h; do
  python3 "tests/$stage28h_suite/run_tests.py" \
    --build-dir "$stage28h_results/$stage28h_suite-build" \
    --results "$stage28h_results/$stage28h_suite.json" || exit 1
done
python3 tests/stage28h/verify_freeze.py
```

The Stage28H Python suite compiles actual mock code with ASan/UBSan/leak, checks CLI manifest,
then exercises the Bash runner in disposable synthetic projects/compiler wrappers, including spaces,
missing compiler, failing probes/builds, warnings, damaged manifests, nonzero programs, TERM cleanup
and byte mismatch. Fake compilers are local error-injection fixtures, never installed or used for
production. Repeated smoke executions are not counted as extra compatibility groups/assertions.
No physical endpoints, private files or network test is present.

Pinned cloud target OBJECT ONLY:

```sh
python3 tests/stage28h/target_check.py \
  --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled \
  --original-core /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --output-dir /tmp/evilduck28h-target-new
```

Output must not exist; verify all original/protected core/SDK/compiler pins before unlinked
preview core/keyboard/bridge/size metadata objects. No firmware ELF/BIN/UF2 or board configuration
changes. Exact commands, source/dependency/object hashes and frame/section data in target receipt.
Git freeze check compares235 files to immutable Git content, not just an old copied receipt.
Publication checks all preexisting remote refs; only explicit Git publication operations use
network here, separate from the strictly offline kit. No telemetry, HTTP fetch or test-network use.
See source hashes, test-results and publication receipts. Native Mac SKIP_ENVIRONMENT.
