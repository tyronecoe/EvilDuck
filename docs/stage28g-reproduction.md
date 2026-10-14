# Stage28G offline reproduction

Exact base3650caf7c66d5742d39a939fa0c8495be11d3b1b. Reuse the existing pinned checkout/toolchain;
cloud setup skill requires no new install/environment/service configuration for this workflow.
No global core changes, production build or owner data required. Actual commands and status are
also in stage28g-reproduction.json and test-results.json.

Fresh host suites:

```sh
stage28g_results="$(mktemp -d /tmp/evilduck28g-tests.XXXXXX)"
for stage28g_suite in stage27b stage28a stage28b stage28c stage28d stage28e stage28f stage28g; do
  python3 "tests/$stage28g_suite/run_tests.py" \
    --build-dir "$stage28g_results/$stage28g_suite-build" \
    --results "$stage28g_results/$stage28g_suite.json" || exit 1
done
python3 tests/stage28g/verify_freeze.py
```

GCC C++17 warnings-as-errors and ASan/UBSan/leak, existing20-second per-case deadline. Old tests
unaltered; output directories/results must not exist. Stage28G test vectors are RAM-only mocks.

Cloud pinned object-only verification:

```sh
python3 tests/stage28g/target_check.py \
  --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled \
  --original-core /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --output-dir /tmp/evilduck28g-target-new
```

Fail closed on mismatched original/protected core, SDK/config/compiler pins. Four unlinked objects
only; no firmware ELF/BIN/UF2 or upload. Cloud paths describe provenance, not owner tool locations.
Target report records flags/source/dependencies/hash/frame evidence. No new install is needed here.

Linux smoke command/env are recorded in JSON. Optional Apple native recipe in macos-smoke.md;
Linux sanitizer success is not Apple runtime/physical USB verification. Remote publication uses
all-ref snapshots before/after and freeze verifier --remote-before/--remote-after; independently
check exactly the new reviewed branch was added at published HEAD. No force/merge/rebase.
