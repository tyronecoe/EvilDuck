# Stage28T executed tests and reproduction

| Executed category | PASS | Unexpected FAIL | Assertions |
| --- | ---: | ---: | ---: |
| T01–T47 primary, final exact candidate | 47 | 0 | 467 |
| Unchanged Stage28S, run once separately | 56 | 0 | 512 |
| Affected actual production scheduler/backend suites | 77 | 0 | 67,371 |
| Final candidate with both selectors OFF, same77 cases/output comparison | 77 | 0 | 67,371 |

Six preparation controls pass separately, with no runtime assertion count.
The disabled comparison repeats functional coverage; it is not77 new features.
Do not add prior stages' historical assertions or superseded development runs.
ASan/UBSan and `detect_leaks=1:halt_on_error=1` are clean for completed cases.
Deliberate T01 negative control exits1 with the intended assertion; S's negative
control remains separately recorded. No historical XPASS/XFAIL is reclassified.
No generic controller/model, Mac smoke or broad compatibility rerun was used.

## Primary coverage map

- T01–T05: a/a and a/b exact eight-byte ID1 reports, all95 printables plus TAB/LF,
  ten named keys, actual functions/expressions/IF/WHILE integration.
- T06–T10: malformed/ownership/non-ASCII source and disabled HID/DE acquisition
  reject before any lower output, including sync.
- T11–T16: precall refusal versus actual false returns; press/restoration and
  both deliberately possible/nonaccepted false cases; no duplicate admission.
- T17–T22: cancellation at press/dwell/restoration/result handoff/Runtime Delay;
  STOP_PAYLOAD and fresh known local cleanup.
- T23–T29: raced/post-event disconnect, pending/failed clear, stale validation,
  fresh Invalid, loss consumption and explicit later synchronization.
- T30–T36: actual legacy script/com entry rejection and callback preservation,
  backend/raw/held/lifecycle ingress, lower callback reentry/deferred cancel,
  foreign host thread, mode/layout changes.
- T37–T47: deadlines/first fault, unsigned Runtime Delay wrap, namespace/journal
  exhaustion, existing owner, settings/timing restoration, forged/stale results
  and operation scope, separate legacy Keyboard software ownership.

Each primary trace contains the harmless source program, local admission and ack
counts, backend first fault, state/quarantine/clear counters and lower report
bytes, time, ID, operation and phase. `retries` counts Sink Retry, not USB sends.
Lower outcomes0/1/2 mean true/false-without-acceptance/false-after-possible-
acceptance in the fixture only. Backend sees only called/returned/loss evidence.
Journal overflow has one bounded snapshot asserted in T45, outside stored calls.

Actual code compiled: scratch com/backend plus unchanged preview core and the
production modules listed in `run_tests.py::MODULES`. Existing host Arduino,
Keyboard, storage, clock, attackmode, USB event/mount and service mocks replace
platform dependencies. Only the additional lower ready/report fake is new.
Neither full USB stack, real RTOS, real attackmode/MSC nor webserver runs.

gcov primary source lines: com47.07% (478 lines), backend45.61% (353),
preview core84.51% (426), scheduler seam98.28% (58), lease100% (46).
Branch taken coverage is lower; no full-path claim. Actual beginReport162,
releaseReport144, queueRaw9,445, update11,130 and cancelReport130 calls are
recorded. See machine-readable function counts and summary in coverage JSON.

Development failures were investigated rather than relabeled: an initial missing
mock declaration was fixed; source review found inconsistent quoted USBHID
header lookup in the platform mock. The final runner copies host.cpp
byte-identically to scratch platform.cpp so both modules select the same mock.
Later review found raw Keyboard ownership outside Owned; an initially overbroad
latch caused T43 to fail. It was narrowed to raw helpers, leaving HOLD's tracked
Owned cleanup intact. Final47-case run passes unchanged expectations. Earlier
47-case development run had46PASS/1FAIL and is excluded from final counts.

## Reproduce (native, disconnected; fresh external paths)

Environment: Debian g++14.2.0, Python3.12.14, Git2.52.0, GNU patch2.8,
gcov14.2.0. Full exact compiler commands, hashes and receipts are in test-results
and source manifest JSON. Existing warning policy includes
`-Wall -Wextra -Werror -Wno-misleading-indentation`; it was not relaxed for a failure.

```sh
python3 tests/stage28t/run_tests.py --build-dir /tmp/evilduck-t-primary --results /tmp/evilduck-t-primary.json
python3 tests/stage28t/run_regressions.py --build-dir /tmp/evilduck-t-regression --results /tmp/evilduck-t-regression.json
python3 tests/stage28t/check_preparation.py
python3 tests/stage28h/verify_freeze.py
python3 tests/stage28t/verify_scope.py --output /tmp/evilduck-t-scope.json
```

Paths must not exist; never use an installed core as a patch destination.
`run_regressions.py` executes original and final opt-in-disabled production
sources. During development, the already-executed original77 receipt was reused
to compare the final disabled binary; no need to rerun unchanged original cases.
Stage28S was run once using its unchanged published runner; exact command is in
the embedded S receipt. To regenerate primary-only coverage in the external
primary build directory: `gcov -b -c native-com.gcno native-hid_backend.gcno native-core.gcno`.
No Arduino/core install or target compiler is needed for these tests.
