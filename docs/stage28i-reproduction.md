# Stage28I reproduction — audit only

Existing cloud environment reused; no packages/tools/services/core installed or modified.
Observed host versions: Python 3.12.14, GNU Bash 5.2.37, Debian GCC 14.2.0-19. Target compiler
Xtensa GCC 14.2 with pinned Arduino 3.3.0/ESP-IDF 5.5 sources/config, protected-core workflow.
No firmware build command is authorized or used here.

Fresh regressions from repository root, external empty outputs:

```sh
stage28i_results="$(mktemp -d /tmp/evilduck28i-tests.XXXXXX)"
for stage28i_suite in stage27b stage28a stage28b stage28c stage28d stage28e stage28f stage28g stage28h; do
  python3 "tests/$stage28i_suite/run_tests.py" \
    --build-dir "$stage28i_results/$stage28i_suite-build" \
    --results "$stage28i_results/$stage28i_suite.json" || exit 1
done
python3 tests/stage28h/verify_freeze.py
```

Existing runners unchanged, warnings-as-errors/ASan/UBSan/leak enabled where previously supported.
Expected failing synthetic programs in Stage28H verify classification; they are not compatibility
passes for blocked features. Exact actual group names/commands/exits are in stage28i-test-results.json.
No new runtime test suite; static audit counts are separate and not added to assertion totals.

Existing pinned object-only check, cloud paths shown for reproduction rather than owner prerequisites:

```sh
python3 tests/stage28h/target_check.py \
  --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled \
  --original-core /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --output-dir /tmp/evilduck28i-target-new
```

New output directory must not exist. Core/SDK/compiler hashes verified before four UNLINKED
objects; no firmware ELF/BIN/UF2, Arduino compile/upload or device access.

Optional cloud static source/evidence/scope audit (NOT owner smoke prerequisite):

```sh
python3 tests/stage28i/audit_sources.py \
  --protected-core /workspace/tooling/stage26-final-controlled-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --sdk /workspace/tooling/arduino/data/packages/esp32/tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3 \
  --results /tmp/evilduck28i-audit-new.json
```

This reads exact documented source spans, independently checks all old tracked files against Git
baseline and rejects any new path outside stage28i docs/tests. No patch/compile/transport occurs.
It needs Git history and existing dependency sources; absence is an audit prerequisite, not reason
to install them on the Mac. A ZIP alone cannot execute historical-Git integrity checks.

Owner disconnected High Sierra command stays EXACTLY the existing kit:

```sh
bash tests/stage28h/run_host_smoke.sh
```

EvilDuck UNPLUGGED; root is unpacked repository, not Arduino sketch directory. Existing
stage28h-macos-validation.md includes unique local transcript/status handling and troubleshooting.
No Python/Git/Arduino/network/install required. Owner reports only version, exit and sanitized
relevant PASS/FAIL/SKIP/vector diagnostics; do not send private files/credentials/paths. Native
Mac NOT TESTED / PENDING OWNER; cloud SKIP_ENVIRONMENT cannot substitute for that gate.

Git publication: save all refs with git ls-remote --refs origin before/after, compare using
unchanged Stage28H freeze verifier --remote-before/--remote-after, then verify only the new review
branch was added at exact HEAD. Network limited to separately required Git publication checks;
no network test/telemetry/reference fetch. Preserve all prior refs, never force/merge/rebase.
