# Stage28W safe offline reproduction

Exact parent: `3144c9bdf7b78a4f75d6861fdffa0707c755fffc`. New files only;
original application, previous patches/reports and installed packages are inputs.
Python3.12.14, g++14.2.0, GNU patch2.8, Git2.52.0 and the existing pinned Xtensa
esp-14.2.0_20241119 compiler are used. Arduino ESP323.3.0, IDF release_v5.5-
b66b5448-v1, protected HID/NVS patches and actual framework versions are pinned
in source and linked receipts. No package installation or global patch is needed.

Every output below must be fresh and external to the checkout. Run from repo root:

```sh
python3 tests/stage28h/verify_freeze.py
python3 tests/stage28w/prepare_sources.py /tmp/stage28w-sources
python3 tests/stage28w/run_tests.py --build-dir /tmp/stage28w-native --results /tmp/stage28w-native-results.json
python3 tests/stage28w/run_framework.py --user-dir /workspace/tooling/arduino/user --output-dir /tmp/stage28w-framework
python3 tests/stage28v/run_tests.py --build-dir /tmp/stage28w-v --results /tmp/stage28w-v-results.json
python3 tests/stage28u/run_tests.py --build-dir /tmp/stage28w-u --results /tmp/stage28w-u-results.json
python3 tests/stage28t/run_tests.py --build-dir /tmp/stage28w-t --results /tmp/stage28w-t-results.json
python3 tests/stage28w/run_regressions.py --build-dir /tmp/stage28w-production --results /tmp/stage28w-production-results.json
python3 tests/stage28w/run_startup.py --sdk-source /workspace/tooling/stage19-sdk-source --build-dir /tmp/stage28w-startup --results /tmp/stage28w-startup-results.json
python3 tests/stage28w/build_candidate.py --output-dir /tmp/stage28w-linked --config /workspace/tooling/stage26-final-controlled-core/arduino-cli.json --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 2
python3 tests/stage28w/verify_link.py --build-root /tmp/stage28w-linked --output /tmp/stage28w-linked-checked.json
python3 tests/stage28w/build_candidate.py --selector-off --output-dir /tmp/stage28w-linked-off --config /workspace/tooling/stage26-final-controlled-core/arduino-cli.json --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 2
python3 tests/stage28w/verify_link.py --build-root /tmp/stage28w-linked-off --output /tmp/stage28w-linked-off-checked.json
python3 tests/stage28w/verify_scope.py --output /tmp/stage28w-scope.json
```

Missing/mismatched dependencies are errors, not unexplained SKIP. Prepare composes
unchanged S/T/U/V, applies W at fuzz0, and checks exact output/source hashes. The
builder copies public firmware and reviewed runtime inputs into a fresh sketch,
uses the selected isolated protected core, and checks its identity before/after.
Only generated config/cache/build outputs are new; installed core/SDK/libraries
are unchanged. Link uses actual builder-selected SDK, core, libraries and target
compiler. No old T host selector or EVILDUCK_HOST_TEST reaches target commands.

The existing validators' **source root** is directed to that reviewed scratch
candidate; their dependency checker retains its original root and exact baseline
pins. No old tool or guard is edited. Exact candidate source copies, unchanged
approved partition CSV, profile flags, linked startup/settings checks, protected
HID/NVS implementation and ELF-to-BIN regeneration are verified. The post-link
checker resolves response files/linker scripts/archive inputs, checks selected
symbols and loop/tick wiring, and uses an explicit temporary inspection output.
It rejects artifact changes and never operates on an owner backup.

`collect_results.py /workspace/tooling` collects the named actual run receipts;
it does not execute tests or turn an old count into new evidence. Publication
uses actual before/after remote snapshots and `verify_scope.py --before <file>
--after <file> --output <fresh-external-receipt>`. It requires47 old refs unchanged
and only this new branch at HEAD. Integrity excludes its own hash; final Git commit
and post-push comparison bind publication without a circular self-hash.

These wrappers have no upload, port, board, OTA or physical-flash mode. No merged
full-flash image is generated. ELF/BIN/map outputs are REVIEW ONLY, not an install
package. Do not invoke a physical writer. Rollback: leave the selector undefined
and discard only external scratch outputs. Stage28X is not authorized.
