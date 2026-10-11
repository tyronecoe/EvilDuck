# Stage 6 function regression tests

Run `python3 tests/stage6/run_tests.py` from the repository root. This compiles the
actual S3 executor, parser, expression engine and command scheduler against the
Stage 1 mocked HID, storage, clock, logging and supporting interfaces. It does not
discover or access hardware and cannot send host HID reports.

The runner executes 64 independent integration cases and one allocation probe:
65 PASS, 0 FAIL, 60,727 assertions in the recorded run. ASan/UBSan are enabled for
both targets. Exact names and individual assertion counts are recorded in
`docs/stage6-results.json`, with the complete prior-suite results.

Coverage includes definitions skipped in sequential execution; repeated and
forward invocation; globals and numeric/Boolean/void returns; suspended expression
evaluation; nested/recursive calls; IF/ELSE IF/WHILE isolation and unwinding;
condition-side-effect progress; inactive branches; DEFINE and literal lexical
modes; malformed/unknown/duplicate declarations; all function/call/expression
bounds; storage read/seek failures; STOP and cancellation during text, delays,
held keys and USB backpressure; fresh runs and live-command ownership.

The harmless visible fixture runs through both mocked SPIFFS and SD. Its expected
text is `n=2`, `n=1`, `done`, `n=1`, `after`, with Enter after each line. Other
fixtures directly inspect numeric state or validate diagnostics and zero HID.

`no_alloc.cpp` verifies 10,000 postfix/call-stack suspend/resume cycles, exact
depth, overflow and underflow, observing zero C++ heap allocations in that isolated
path. It does not claim that string parsing or the entire firmware never allocates.
The existing Stage 1 historical diagnostic labels are untouched: three XPASS
reflect previous IF/WHILE fixes and two XFAIL remain HID/locale bugs.

No Stage 7 text-block runtime semantics are implemented here.
