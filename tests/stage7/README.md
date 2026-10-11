# Stage 7 multiline runtime regression tests

Run `python3 tests/stage7/run_tests.py` from the repository root. The runner builds
the real S3 interpreter, command scheduler, parser and expression engine against
RAM-only HID/storage/clock/support mocks, with ASan/UBSan. It never discovers or
accesses physical hardware or sends real HID output.

The recorded run contains 67 integration tests and one line-allocation probe:
68 PASS, 0 FAIL, 40,520 assertions. Exact names, individual assertion totals and
the complete Stage 1–7 regression results are in `docs/stage7-results.json`.

Coverage includes empty/single/multiline blocks; blank lines; literal-tab versus
space indentation; internal/trailing whitespace; quotes/backslashes; delimiters;
LF/CRLF/BOM/final newline; literal commands/calls; DEFINE and known/unknown numeric
and text interpolation; exact line/expansion/source limits; inactive branches;
IF/WHILE/functions/recursion and exact nesting boundaries; per-line default delay and replay; cancellation under
typing/delay/USB pressure; live ownership; SPIFFS/SD faults and clean next runs.
Malformed static structures and static expansion errors must emit zero HID.

The harmless combined function/loop fixture runs through both mocked SPIFFS and
SD. Expected output, with Enter after each displayed line:

```text
ready n=2
IF literal THEN
joined-2
ready n=1
IF literal THEN
joined-1
```

A 4,096-line block verifies 65,536 streamed output characters. The isolated
10,000-line probe observes host C++ allocation request sizes for lexing/DEFINE/
interpolation: maximum request 961 bytes, with 50,006 requests in the recorded
run. This is not an ESP32 live-heap/fragmentation measurement or a zero-allocation
claim. Block size does not cause a whole-block buffer allocation.

Stage 2–6 tests that deliberately rejected text-block runtime as deferred are
updated to verify literal output; malformed-block tests remain. Historical
diagnostic labels remain three XPASS (earlier IF/WHILE fixes) and two XFAIL
(F13/German locale defects). Stage 8 fixes are not included.

Reproduce all earlier suites using the commands in `docs/stage7-report.md`.
Stage 2's runner includes Stage 1. Clean firmware builds and partition validation
use the unchanged pinned core 3.3.0 / 16 MiB / PSRAM-disabled profile. The optional
`tools/analyze_s3_stack.py` performs offline compiler frame estimates only.
