# Stage28M test report and safe reproduction

Primary: **36 PASS / 0 FAIL / 9,689 assertions**, fresh executed C++ results only. ASan/UBSan and ASAN detect_leaks=1 clean. No SKIP_ENVIRONMENT. No real USB, hardware or OS input. The 24 L trace groups are memory executions, not actual-stack/hardware passes.

| Separate verification | Result | Classification |
|---|---|---|
| Historical K01 intended barrier | Exit1, start crossed queued setup | Controlled defect reproduction, not unexpected primary FAIL or PASS |
| New K01 same barrier | Exit0, Prepared/queue/identity unchanged | Separate corrected regression; excluded primary counts |
| Deliberate Stage28M negative control | Exit1;35 PASS/1 FAIL | Required runner sensitivity, excluded primary |
| Healthy allocation probe | Exit0;zero C++ new calls | Non-sanitized compile/run/drain/fenced teardown only; excluded primary |

## Required traces: actual fixture evidence

| Trace | Mock result | Assertions | Variants | Real stack/hardware |
|---|---|---:|---:|---|
| L01 | PASS | 69 | 1 | NOT EXECUTED |
| L02 | PASS | 46 | 1 | NOT EXECUTED |
| L03 | PASS | 43 | 1 | NOT EXECUTED |
| L04 | PASS | 62 | 2 | NOT EXECUTED |
| L05 | PASS | 60 | 1 | NOT EXECUTED |
| L06 | PASS | 222 | 7 | NOT EXECUTED |
| L07 | PASS | 17 | 1 | NOT EXECUTED |
| L08 | PASS | 30 | 1 | NOT EXECUTED |
| L09 | PASS | 75 | 2 | NOT EXECUTED |
| L10 | PASS | 44 | 1 | NOT EXECUTED |
| L11 | PASS | 48 | 1 | NOT EXECUTED |
| L12 | PASS | 51 | 1 | NOT EXECUTED |
| L13 | PASS | 90 | 2 | NOT EXECUTED |
| L14 | PASS | 38 | 1 | NOT EXECUTED |
| L15 | PASS | 34 | 1 | NOT EXECUTED |
| L16 | PASS | 44 | 1 | NOT EXECUTED |
| L17 | PASS | 78 | 1 | NOT EXECUTED |
| L18 | PASS | 40 | 1 | NOT EXECUTED |
| L19 | PASS | 90 | 5 | NOT EXECUTED |
| L20 | PASS | 6681 | 2 | NOT EXECUTED |
| L21 | PASS | 30 | 1 | NOT EXECUTED |
| L22 | PASS | 17 | 1 | NOT EXECUTED |
| L23 | PASS | 785 | 1 | NOT EXECUTED |
| L24 | PASS | 62 | 1 | NOT EXECUTED |

L01 records C1/S1, E1, R/Q1–4: ID1 wire `010000000000000000`, `010000040000000000`, then two fresh zero frames. Four submitted/Accepted reports, one keyboard source ack. Delay has no report/Q (B07). Structured receipts contain every transfer C/Q/S/E/R, binding, wire bytes, outcome, poll count, success/retirement/acceptance order, source/report acknowledgements, request dispositions and notices. Each fixture captures its terminal/test outcome before an explicit owner cancel + **injected** transfer/observer fence; canReclaim is asserted before destruction. Teardown is not inferred from destructor or empty queue.

L20 executes the retained128-intent and256-report boundaries and operational slot reuse. Exact final Delay/non-event progress through a new pre-admission API is BLOCKED/UNSELECTED. L21 deliberately rejects untagged observations despite equal bytes; no actual SDK pointer was exercised. L22 producer state/fence is fixture evidence, not proof of real USB exclusivity. L24 proves only model transport-neutral completion.

B01–B12 cover the resolved setup/start barrier; rejected setup; cancellation during setup; retirement-before-success; ambiguous quarantine; cancel-after-committed-ack; Delay timing; request evidence exhaustion; ordered invalid notice/teardown; malformed source with zero reports; plan capacity/first fault; transfer/notice evidence exhaustion.

## Relevant unchanged regressions, separately executed

| Suite | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| stage27b | 25 | 0 | 2,543 |
| stage28c | 17 | 0 | 390,573 |
| stage28d | 21 | 0 | 14,989 |
| stage28e | 24 | 0 | 109,591 |
| stage28f | 20 | 0 | 18,419 |
| k | 37 | 0 | 10,346 |

Separate unchanged total: **144 PASS / 0 FAIL / 546,461 assertions**. These are not added to the36 new groups or primary assertion total. Selection rationale is recorded in JSON: actual compiler/core/runtime, source session, Planner, Bridge, confirmed ownership APIs and required K driver. No broad legacy sweep solely to increase counts. No target object gate was run because this milestone explicitly forbids target builds/layout measurements. Other legacy/owner Mac suites were not rerun or represented as fresh evidence.

Two development fixture assertions failed before finalization: B11 injected failure was behind default early success; B09 invalid notice was behind retirement in the one-notice owner queue. Fixtures were corrected to control the intended ordering. They were not firmware defects, hidden sanitizer failures or relabelled historical expectations. Final executed primary has zero unexpected failures. The final published runner also executes the corrected K01 with explicit teardown. Fixture lifetime review added fences to service-only capacity tests; all final assertions are counted once from the final primary run.

## Reproduction

Reuse existing Linux GCC/Python; no installation, services, target compiler invocation or USB needed. Actual compiler version:

```text
g++ (Debian 14.2.0-19) 14.2.0
Copyright (C) 2024 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

Flags: C++17/O1/debug, Wall/Wextra/Werror, unchanged misleading-indent suppression, ASan+UBSan, frame pointers, non-PIE. ASAN_OPTIONS=detect_leaks=1; UBSAN_OPTIONS=halt_on_error=1. Each compiler/test command and exit is in the JSON. Runner rejects pre-existing or repository-contained output paths. From repo root, fresh external outputs:

```sh
python3 tests/stage28m/run_tests.py \
  --build-dir /tmp/evilduck28m-new-build \
  --results /tmp/evilduck28m-new-results.json
python3 tests/stage28h/verify_freeze.py
python3 tests/stage28m/verify_scope.py \
  --results /tmp/evilduck28m-new-scope.json
```

Optional existing protected-dependency identity check adds `--protected-core /workspace/tooling/stage26-final-controlled-core/data/packages/esp32/hardware/esp32/3.3.0` to verify_scope; it only invokes check_sources, never prepare/patch/install/build. The owner need not run these cloud Python/Git checks on their Mac for this delivery.

Regressions use unchanged published `tests/<suite>/run_tests.py --build-dir <fresh-external> --results <fresh-external-json>` for stage27b, stage28c,d,e,f,k. Executed output locations and full command details are in structured results. Public provenance retrieval is separate from test execution; tests use no network. No new Apple/native Mac claim.

JSON enums: driver states0 Idle/1 Syncing/2 Prepared/3 Running/4 TerminalUndrained/5 DrainPending/6 Drained; receipts0 Pending/1 Accepted/2 Rejected/3 Abandoned; request dispositions0 Admitted/1 Executing/2 Executed/3 Rejected/4 Cancelled. Transport fault codes follow synthetic_transport.h; notice classification1 current/2 duplicate-stale/3 invalid. Fixture payloads are harmless memory literals, not private script or credential captures.
