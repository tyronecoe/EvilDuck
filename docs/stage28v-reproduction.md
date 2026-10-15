# Stage28V offline reproduction

Use the Stage28V checkout and its exact U parent. Existing environment required:
Python3.12.14, GNU patch2.8, Git2.52.0, Debian g++14.2.0; pinned Xtensa compiler
`esp-14.2.0_20241119` (actual version string is in target receipt), Arduino ESP32
3.3.0 protected isolated copy and matching SDK/source receipts. No new package
installation, core patching, private file, service, serial/USB enumeration or
hardware access is required. The cloud setup skill was used to verify/reuse this
ready toolchain; no reusable environment configuration change was needed.

Run from repository root. Every output directory/file below must be fresh and
outside the checkout. Paths are illustrative local scratch, not deployable files.

```sh
python3 tests/stage28h/verify_freeze.py
python3 tests/stage28v/prepare_sources.py /tmp/stage28v-source-review
python3 tests/stage28v/check_preparation.py
python3 tests/stage28v/run_tests.py --build-dir /tmp/stage28v-native --results /tmp/stage28v-native-results.json
python3 tests/stage28u/run_tests.py --build-dir /tmp/stage28v-u --results /tmp/stage28v-u-results.json
python3 tests/stage28t/run_tests.py --build-dir /tmp/stage28v-t --results /tmp/stage28v-t-results.json
python3 tests/stage28v/run_regressions.py --build-dir /tmp/stage28v-legacy --results /tmp/stage28v-legacy-results.json
python3 tests/stage25_startup/run_tests.py --sdk-source /workspace/tooling/stage19-sdk-source --build-dir /tmp/stage28v-startup --results /tmp/stage28v-startup-results.json
python3 tests/stage28v/run_startup.py --sdk-source /workspace/tooling/stage19-sdk-source --build-dir /tmp/stage28v-startup-candidate --results /tmp/stage28v-startup-candidate-results.json
python3 tests/stage28v/target_check.py --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled --output-dir /tmp/stage28v-target
python3 tests/stage28v/target_check.py --selector-off --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled --output-dir /tmp/stage28v-target-off
python3 tests/stage28v/verify_scope.py --output /tmp/stage28v-scope.json
```

The native runner currently expects the verified SDK source at the recorded
/workspace/tooling path; missing prerequisites must be reported, not replaced
with arbitrary headers or downgraded to PASS. Target check requires the existing
Stage26 compile database and protected-core provenance, validates the compiler
SHA and core/SDK hashes, and issues `-c` commands only. It has no link or writer
mode. No old host-only T selector is used on target. Native test executable linking
is distinct from target firmware linking.

ASAN_OPTIONS is detect_leaks=1:halt_on_error=1 and UBSAN_OPTIONS=halt_on_error=1.
Run original U/T once as separate regression suites; do not fold repeated default-
off comparison counts into new coverage. The receipts record actual external
run locations. `collect_results.py /workspace/tooling` records those named existing
run receipts; it does not execute tests or turn stale reports into fresh passes.

Publication review uses read-only Git ref snapshots before and after the authorized
new-branch push, then `verify_scope.py --remote-before <before> --remote-after <after>
--output <fresh-external-receipt>`. It requires46 existing refs unchanged and only
the new Stage28V branch added at the local HEAD. Precommit integrity excludes its
own hash; final commit identity is Git's commit/ref and the external post-push
receipt, not a circular self-hash embedded in the commit.

Do not invoke the historical full firmware builder here. The conditional link
gate is BLOCKED. Rollback consists only of leaving the selector disabled and
removing scratch outputs. No owner data or installed package requires alteration.
