# Stage28P test report and reproduction

33 primary observation PASS /0 unexpected FAIL /167 assertions. Contract NOT SATISFIED; no actual controller retirement or identity is certified.

| ID | Actual source observation | Assertions |
|---|---|---:|
| P01 | Retained buffer/length; genuine FIFO9 and completion | 12 |
| P02 | Closed endpoint definite refusal | 4 |
| P03 | Outstanding descriptor overwritten by direct second submission | 7 |
| P04 | 137-byte transfer,64/64/9 progression | 6 |
| P05 | FIFO space refusal then progression | 4 |
| P06 | Zero-length transfer | 4 |
| P07 | Early IRQ/class callback before lower return | 6 |
| P08 | Equal frames in successive transfers | 5 |
| P09 | Old unlabeled IRQ reads newer total/buffer | 5 |
| P10 | Stale completion clears current stack busy | 7 |
| P11 | Repeated completion invokes repeated callbacks | 4 |
| P12 | Simultaneous reset/old IEP snapshot yields cleared length | 4 |
| P13 | Reset closes software descriptor, configuration reopens | 5 |
| P14 | Actual builder suspend emits UNPLUGGED | 5 |
| P15 | OTG session-end UNPLUGGED retains descriptor | 4 |
| P16 | Raw DCD still schedules after stack unplug | 4 |
| P17 | Close-all zeroes max, retains pointer/length | 5 |
| P18 | Forced post-close old IRQ emits old length | 3 |
| P19 | IN stall with scripted ready flags; clear-stall | 5 |
| P20 | Five events into four slots; one refusal | 5 |
| P21 | Close/configuration/reopen with stale completion | 5 |
| P22 | Success leaves retained cursor and software metadata | 4 |
| P23 | Remote wake and resume signal | 4 |
| P24 | ID0 class-entry framing | 4 |
| P25 | Historical oversize HID claim retention | 4 |
| P26 | Remote-wake SOF interrupt handling | 2 |
| P30 | Genuine tu_fifo data path; plain register TSIZ not consumed | 9 |
| P31 | FIFO item-size rejection | 4 |
| P32 | OUT scheduling/completion metadata; no RX data success claimed | 6 |
| P33 | Inconsistent TSIZ with injected XFRC emits stored total | 4 |
| P34 | Real stack weak-deinit/late-event deleted queue boundary | 6 |
| P35 | Genuine observer reentry mutates borrowed class buffer | 7 |
| P36 | Injected timeout/AHB flags do not publish failure | 4 |

P27 expected watchdog: INEPNE never arrives in original stall wait. P28: original close-all TX FIFO flush cannot resolve. P29: original common.c with platform include substitution only reaches actual PHY hook and cannot self-clear CSRST. Each is killed after1 second externally; stdout/source establish path, but gcov finalization/leak cleanup is unavailable. These are separate observations, not33 PASS/assertions or new production timeouts.

Completed cases compile real selected DCD body through driver_unit.c, real pinned common/stack/HID/FIFO code, fake CUSTOM OS and simulated register/platform boundary. Every completed case has original dcd_init/dcd_int_handler/reset/enum/open/dfifo allocation/core-init coverage. Actual submission, FIFO, class and IRQ functions are checked where applicable. P30 executes real tu_fifo_read_n_const_addr_full_words; P07 checks that the submit caller is still pending inside its controlled early hook. No callback shortcut replaces driver event emission.

GCC/gcov14.2.0; C11/O1/debug/Wall/Wextra/Werror, inherited misleading-indentation suppression, ASan/UBSan/non-PIE/frame pointers/gcov; ASAN_OPTIONS=detect_leaks=1, UBSAN_OPTIONS=halt_on_error=1. Compiler/config/source/shim/patch SHA, commands/exits and exact vendor function/line counts are in JSON. P negative control exits1; original O/N negative controls and two original-defect reproductions are separate.

Unchanged O suite executed once:46/931. Fresh N supplied baseline20/131 and O disabled20/131 are separately recorded; no historical totals silently reused. Prior M/older suites and Mac are not repeated without a new concrete risk.

P native driver event/packet/queue logs contain exact bytes/lengths and state transitions. Identity fields are unavailable, not manufactured. Buffer addresses are not serialized or used as transfer identity. Native descriptor array336B/control8B are not target/resource measurements. Watchdog cases have no finished sanitizer/leak-clean claim. Plain registers, manually retained statuses, packet consumption and PHY readiness are explicit fixture assumptions; forced unusual status combinations are not physical observations.

## Safe host-native reproduction

Existing GCC/gcov/Python/patch only; no tool install, target compiler, SDK rebuild, physical registers, owner files or USB access. Fresh external output directories required.

```sh
python3 tests/stage28p/prepare_sources.py --output /tmp/evilduck28p-original-new --mode original
python3 tests/stage28p/prepare_sources.py --output /tmp/evilduck28p-adapted-new --reuse /tmp/evilduck28p-original-new --mode adapted
python3 tests/stage28p/prepare_sources.py --output /tmp/evilduck28p-plain-new --reuse /tmp/evilduck28p-original-new --mode plain-platform
python3 tests/stage28p/run_tests.py --source-root /tmp/evilduck28p-adapted-new --plain-root /tmp/evilduck28p-plain-new --build-dir /tmp/evilduck28p-build-new --results /tmp/evilduck28p-results-new.json
python3 tests/stage28p/verify_scope.py --source-root /tmp/evilduck28p-adapted-new --output /tmp/evilduck28p-scope-new.json
python3 tests/stage28h/verify_freeze.py
```

Separate unchanged O/N regression commands, as actually used:

```sh
python3 tests/stage28n/run_tests.py --source-root /tmp/evilduck28p-original-new --build-dir /tmp/evilduck28p-n-new --results /tmp/evilduck28p-n-new.json
python3 tests/stage28o/prepare_sources.py --original /tmp/evilduck28p-original-new --output /tmp/evilduck28p-o-copy-new
python3 tests/stage28o/run_tests.py --source-root /tmp/evilduck28p-o-copy-new --original-root /tmp/evilduck28p-original-new --build-dir /tmp/evilduck28p-o-new --results /tmp/evilduck28p-o-new.json --baseline-results /tmp/evilduck28p-n-new.json
```

Preparation retrieves only exact full-revision public inputs or verifies existing bytes before copying; fresh destination, patch digest/fuzz0 and exact output checks fail closed. No installed source/global configuration is changed. The opt-in native O fake controller remains the unchanged historical comparison; it is not called the actual P DCD.
