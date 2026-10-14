# K01 controlled reproduction and new barrier

The exact historical `tests/stage28k/journal_driver.cpp/.h` remain unchanged. `tests/stage28m/k01_reproducer.cpp` is compiled twice against the same unchanged preview: once using `HISTORICAL_K01`, once using the new driver.

Sequence: compile benign `DELAY 0`; begin and accept sync to Prepared; enqueue owner0 HOLD usage4; call start before any setup step. Assert the intended barrier. No immediate setup execution was requested.

Historical execution: `start=true`, queued_after_start1; then Runtime terminates with queued_after_terminal0, setup_held=false, reports1, state4 (TerminalUndrained). S remains1. **Exit1**, diagnostic:

```text
K01 INTENDED BARRIER FAILED: start crossed one admitted unresolved setup request; terminal cleared it without setup execution
```

This is a **CONTROLLED DEFECT REPRODUCTION**, excluded from primary PASS/FAIL totals, not a fabricated pass or retroactive change to the prior37 green K groups. Those tests did not cover this ordering.

New driver execution: `start=false`, queued_after_start1, queued_after_terminal1, setup_held=false, reports1, state2 (Prepared), S remains1. **Exit0**. The same barrier regression now passes without partial Runtime start or identity consumption. B01 additionally consumes the queued request, retains Executing while transport retries, rejects start after success but before retirement, then marks Executed and permits start; repeated start rejects. B02 tests admitted but rejected rollover setup, B03 cancellation of pending setup, L14 eight-request saturation/priority cancel, B08 disposition-journal exhaustion, and no-request startup is exercised by L01.

Full command, structured stdout, stderr and exit records: `stage28m-test-results.json`. Historical reproduction is sanitized; its expected application exit1 is not an ASan/UBSan/leak diagnostic. Normal harness negative control is separate: deliberately failed L01 expectation yields35 PASS/1 FAIL and exit1; its repeated assertions are not added to the36 primary group totals.
