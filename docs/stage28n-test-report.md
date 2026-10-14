# Stage28N test report and reproduction

**20 observation PASS / 0 unexpected FAIL / 131 primary assertions.** ASan/UBSan and detect_leaks=1 clean. These are observations, **not transport compatibility passes**. Every case is CONTRACT NOT SATISFIED overall: unchanged stack lacks authentic creation-time identity/retirement. No physical behavior tested.

| ID | Actual native observation | Assertions | Status |
|---|---|---:|---|
| N01 | Copy, ID1 framing, fresh zero and genuine completion dispatch | 13 | observation PASS |
| N02 | Report-ID zero8 versus ID1 nine-byte framing | 9 | observation PASS |
| N03 | Partial success, failed INPUT and injected oversized completion | 6 | observation PASS |
| N04 | Completion through queue/task/class before DCD submit return | 6 | observation PASS |
| N05 | Busy/claimed refusal, invalid instance and oversized retained claim | 14 | observation PASS |
| N06 | Failed lower submission clears busy/claim; copied buffer remains | 7 | observation PASS |
| N07 | Equal back-to-back frames; repeated buffer pointer has no token | 10 | observation PASS |
| N08 | Duplicate completion invokes callback again | 5 | observation PASS |
| N09 | Old completion reads reused current buffer and clears busy | 6 | observation PASS |
| N10 | Completion before queued reset; reset is not controller retirement | 5 | observation PASS |
| N11 | Reset before completion; mapping drop, then endpoint reuse | 4 | observation PASS |
| N12 | Unplug and reused endpoint accept unidentifiable old completion | 6 | observation PASS |
| N13 | SET_CONFIGURATION0 closes; configuration1 reopens; old notice | 8 | observation PASS |
| N14 | Finite copied event queue saturation and repeated callbacks | 3 | observation PASS |
| N15 | WAIT_FOREVER entry and forced OS failure ignored in claim | 5 | observation PASS |
| N16 | Two logical producers share boundary; no producer lease | 4 | observation PASS |
| N17 | Callback reentry submits new report and changes borrowed buffer | 5 | observation PASS |
| N18 | Injected suspend/resume plus genuine SET_PROTOCOL ACK | 7 | observation PASS |
| N19 | Unconfigured raw class call routes EP0, not keyboard IN | 4 | observation PASS |
| N20 | False DCD deinit ignored; late event reaches deleted queue shim | 4 | observation PASS |

| Unexecuted path | Classification |
|---|---|
| N21 selected builder DCD register/FIFO/DMA runtime | BLOCKED; source/static analysis only |
| N22 protected Arduino USBHID/FreeRTOS runtime | BLOCKED; source/static analysis only |
| All physical USB/host behavior | NOT TESTED |

Expected contract violations are not unexpected test failures. N03 artificially injects partial/failing/oversized lengths; observer copies at most64 bytes. N08/N09/N11/N12/N13 inject duplicate/late events and do not claim hardware normally generates them. N15 is a forced custom-OS failure, not a real FreeRTOS WAIT_FOREVER result. N18 injects SUSPEND directly into real dispatcher while selected builder source emits UNPLUGGED on hardware suspend. N19 deliberately misuses raw class API when unconfigured; it is not evidence the current EvilDuck caller does so. N20 forces DCD failure; null queue rejection belongs to fake OS and is not SDK robustness. These distinctions are retained in the component boundary/report.

## Executed source evidence

Each case runs in a separate process. Actual unchanged tusb.c/usbd.c/usbd_control.c/hid_device.c executes with the custom OS and fake DCD. GNU gcov JSON records exact vendor function names, execution counts and source ranges for every case. Runner requires dcd_event_handler/tud_task_ext/tud_hid_n_report/usbd_edpt_xfer; it requires hidd_xfer_cb for N01–N18, hidd_control_xfer_cb for N18 and tud_deinit/hidd_deinit for N20. tusb_fifo.c is compiled support with no exercised FIFO routines. No static scope was removed, vendor body copied into a model, or dispatcher bypassed by direct mock callback calls.

Receipts retain exact frames, input events, copied queue transitions, submit/completion/failure counts and early order. Example A frame `010000040000000000`; neutral `010000000000000000`; ID0 A `0000040000000000`. Fixture endpoint129/interface0/instance0/protocolKEYBOARD is explicitly configured, not a physical descriptor claim. Callback borrowed addresses are not serialized; order counters are not C/Q identities. Hardware teardown is not inferred from process exit or fake controller reset.

## Separate checks

Deliberate negative control reruns N01 with a failed expectation: exit1/observation FAIL; its assertions are excluded. The unchanged Stage28M published runner was executed **once** separately:36 PASS/0 FAIL/9,689 assertions, sanitized/leak-clean; historical K01 controlled exit1 and new barrier exit0 remain separate. Other historical runtime suites and Mac smoke were not rerun or promoted to fresh counts. Static freeze/source/hash checks are not C assertions.

Fixture build diagnostics were corrected without vendor edits or flag weakening: endpoint count7 rather than8; canonical network option instead of deprecated CFG_TUD_NET; missing fake controller interrupt/ISO symbols; volatile selected pointer across longjmp. No diagnostic was downgraded to SKIP. A development receive-yield shim was removed before final verification; reset order is observed via actual callback/FIFO dispatch. Final verification has no unexpected errors.

## Safe reproduction

Existing Linux gcc/gcov/Python only; no dependency installation or target compiler. Exact tool versions:

```text
gcc (Debian 14.2.0-19) 14.2.0
Copyright (C) 2024 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
gcov (Debian 14.2.0-19) 14.2.0
JSON format version: 2
Copyright (C) 2024 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

Fresh external outputs from repository root:

```sh
python3 tests/stage28n/prepare_sources.py \
  --output-dir /tmp/evilduck28n-sources-new
python3 tests/stage28n/run_tests.py \
  --source-root /tmp/evilduck28n-sources-new \
  --build-dir /tmp/evilduck28n-native-build-new \
  --results /tmp/evilduck28n-native-results-new.json
python3 tests/stage28n/verify_scope.py \
  --source-root /tmp/evilduck28n-sources-new \
  --results /tmp/evilduck28n-scope-new.json
python3 tests/stage28h/verify_freeze.py
```

Retrieval reads only full-revision official TinyUSB URLs and verifies SHA before storing; it stops on access/error/mismatch. Build runner verifies21 source hashes, uses C11/O1/debug/Wall/Wextra/Werror, inherited misleading-indent suppression, ASan/UBSan/non-PIE/frame pointers and coverage. ASAN_OPTIONS=detect_leaks=1, UBSAN_OPTIONS=halt_on_error=1. GCOV_PREFIX isolates each case data; gcov reads native coverage only. Commands/config/shim/compiled hashes and negative exit are in JSON. No target objects, SDK/firmware link or real USB operation is authorized.

Actual final build: `/workspace/tooling/stage28n-publication-native-build`, minimal source tree `/workspace/tooling/stage28n-prepared-sources`; unchanged M receipt `/workspace/tooling/stage28n-regression-m.json`. Source manifest has official URLs/full revisions/SHA and host include provenance. Host dcd_event_t sizeof24 is not target ABI; no production heap, RAM, stack, latency or device neutrality measurements.
