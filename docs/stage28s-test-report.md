# Stage28S executed verification

Primary IDs S01–S56 correspond to exact programs and assertions in test_main.cpp. Machine results contain all programs, terminal state/first fault, local session/last operation, admission/local ack/Retry/Delay counts and lossless RLE journals (time, scheduler phase, local IDs, outcome, exact8 bytes). RLE retains every emitted queue attempt; canonical reconstructed call-array SHA is verified. Full raw stdout and gcov remain outside the checkout; canonical/hashes and executed function evidence are published. No private/owner script was read.

| Cases | Exercised behavior |
|---|---|
| S01–S05 | a/a and a/b exact48-byte-vector assertions per pair, expressions/IF/loop/function known text+variable, all95 printables/tab/newline, all ten fixed named keys |
| S06–S11 | malformed later expression, inactive/function ownership, non-ASCII, disabled HID/foreign persistent ownership and DE refusal before backend output |
| S12–S17 | one admission despite readiness Retry, known and ambiguous press failure, accepted press then restoration refusal/error/ambiguity |
| S18–S24 | cancellation at Press/dwell/Release/Finish and Done-before-source-ack, Runtime Delay cancellation, actual STOP cancellation |
| S25–S29 | disconnect/config loss before/after submit, pending clear blocks restart, cancel once, explicit new session, unresolved ambiguous clear |
| S30–S33 | competing live/script entry and callback ownership preserved, callback reentrant start/tick, deferred cancel, legacy owner/action prevents start |
| S34–S36 | caller uint32 wrap, exact pending deadline/first fault, deterministic native jitter policy while global settings retained |
| S37–S41 | Reader Retry/error/truncated EOF/seek failure, loading/compile cancellation and borrow/lifetime reuse |
| S42–S46 | session/operation exhaustion before admission, wrong/stale/repeated observations, Delay exact clock boundary/no double wait, numeric/no-key session and fresh clear/sync |
| S47–S50 | invalid ASCII/key values, K01 prior local work barrier, restored legacy timing, exact clear deadline/quarantine |
| S51–S56 | excluded ownership, owned captured source, runtime variable division error with physical line, source-size bound, stuck-clock operation turn bound, literal command-looking text |

Source execution evidence is actual gcov for copied/patched com.cpp and unchanged core.cpp, plus seam.inc. Report totals are not a claim of complete production coverage: native subset intentionally does not execute every command/device path. Existing scheduler text/report/update/fail and Runtime tick/deliver/evaluation/call and CompileSession functions execute, not just a disconnected adapter return. Actual counts, compiler/commands and final source hashes are in machine results.

Sanitizers: ASan/UBSan with detect_leaks=1 and halt-on-error; completed primary, negative control and executed regression cases have no sanitizer diagnostic. Negative control deliberately fails an S01 oracle, exit1, excluded from primary counts. No controller/watchdog models or owner Mac rerun. Historical language XPASS, upstream HID XFAIL and all old risk observations remain unchanged/unrerun.

Development corrections are preserved distinctly: first S24 expected Completed for STOP while unchanged Runtime correctly returns Cancelled; test corrected. S36 exposed beginScript cleanup resetting random/jitter; native seam now snapshots/restores that state and prior default delay. Final source review identified the native lease's idle-gap visibility to duckscript::run; com::busy opt-in branch now blocks that actual entry and S30 verifies it. No historical test expectations were changed. Earlier development/repeated counts are not summed into final executed totals.

Separate tests compile the **unchanged** Stage14 production source fixtures with real hid_backend and fake USB, then the latest scratch patch with opt-in DISABLED; all exits/stdout/stderr must match. Unchanged function/continuation Stage28A and text Stage28B suites run once as reused-core regressions, including their allocation probes. Earlier default-off run is superseded after the busy-guard change, not counted again. Five preparation static/fault checks verify exact output, existing-output refusal, wrong source, wrong patch and wrong output hash; they are not language/runtime assertions.

No target/static RAM/OTA/heap high-water or physical timing measurement. Native sizeof Adapter22592B includes source capture, Program, Compiler storage and Runtime; Bridge/Planner are absent, not double-counted. Fixed result1 and fake queue-attempt journal4096 are bounded; fixture journaling/host String/vector/compiler/libc allocations exist. No zero-allocation claim for the whole native adapter/scheduler; unchanged core-specific no-heap probes are narrower evidence. Quarantine retains scheduler ownership; fixture process exit is not a real firmware recovery strategy.

## Final executed counts

| Execution | PASS groups | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| New Stage28S primary | 56 | 0 | 512 |
| Unchanged production Stage14 scheduler fixtures | 77 | 0 | 67,371 |
| Same fixtures, latest scratch patch opt-in DISABLED | 77 | 0 | 67,371 |
| Unchanged Stage28A functions/continuations | 23 | 0 | 526 |
| Unchanged Stage28B text/blocks | 26 | 0 | 4,733 |

Disabled comparison is separate repeated functional coverage, not77 new compatibility features. Unique unchanged affected regression groups126/assertions72630; primary remains56/512. Five preparation checks PASS separately, not runtime assertions. Negative control exit1 is intended and excluded. Earlier/superseded runs are not added. No mandatory final suite failed or was skipped.

Gcov records real com::update8477 calls, startText172, report185, fail6; unchanged Runtime::tick3247, deliver3034, CompileSession::step1147. Coverage is specific to this opt-in subset, not complete command/physical/controller coverage.

## Reproduction, isolated native only

From the reviewed checkout root, choose unused external output paths (the runners refuse existing outputs):

```sh
python3 tests/stage28s/run_tests.py --build-dir /tmp/evilduck-stage28s-primary --results /tmp/evilduck-stage28s-primary.json
python3 tests/stage28s/run_regressions.py --build-dir /tmp/evilduck-stage28s-regressions --results /tmp/evilduck-stage28s-regressions.json
python3 tests/stage28s/test_preparation.py
python3 tests/stage28s/verify_scope.py --output /tmp/evilduck-stage28s-scope.json
```

Requires existing Python3, native g++, patch, gcov and repository Git history. No Arduino/SDK build, USB library/device or download is used. Runners enable ASan/UBSan/detect_leaks=1, C++17, warnings-as-errors (existing misleading-indentation suppression), pthread and native coverage. GCC/gcov14.2.0 and Python3.12.14 were used here. Full commands are in receipts. Source preparation checks trusted checkout manifest hashes, fresh output and exact patch result; standalone helper must be given a fresh scratch destination, never installed core/firmware paths. Native runners enforce output outside the repository.

For source execution evidence, run `gcov -b -c native-com.gcno native-core.gcno` inside the primary external build directory; it writes native coverage there. Primary runner writes raw journals; the published compact receipt uses lossless RLE with independently checked reconstructed-call SHA. No compilation, target layout, resource/latency or USB delivery result should be inferred by running only the static scope checker. The committed integrity receipt intentionally precedes commit/publication and excludes its own hash.

Patch-format note: Git's blanket staged whitespace check reports14 single-space blank **context markers** in the valid unified diff. Those markers are required patch syntax, not whitespace in the generated C++. They are individually verified to be exactly one space; all other new-file whitespace checks remain enabled. The runtime-tested patch bytes and input/output hashes are preserved. No compiler warning, sanitizer, functional expectation or dependency guard was weakened.
