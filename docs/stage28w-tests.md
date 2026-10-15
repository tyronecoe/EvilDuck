# Stage28W executed tests and classifications

| Fresh suite | PASS | Unexpected FAIL | Assertions |
| --- | ---: | ---: | ---: |
| Actual W app/setup/loop/registered-handler bodies | 34 | 0 | 380 |
| Selected pinned framework response components | 5 | 0 | 116 |
| Unchanged V | 56 | 0 | 566 |
| Unchanged U | 64 | 0 | 515 |
| Unchanged T | 47 | 0 | 467 |
| Affected original production cases | 77 | 0 | 67,371 |
| Existing controlled startup cases on selector-off W sources | 30 | 0 | 635 |
| Separate exact selector-off production comparison | 77 | 0 | 67,371 |

Listed case sets excluding the repeated comparison total313 PASS /70,050 assertions.
The comparison is exact exit/stdout/stderr, not additional coverage. No unrelated
retirement model was rerun. Historical language XPASS, USB XFAIL, Stage9 observations
and old risk results remain unchanged; they are not fabricated fresh W passes.

Completed native cases run ASan/UBSan and detect_leaks=1 with halt-on-error. The
actual65-byte-budget negative variant fails W10 with the intended serial-budget
message and exit1. It is an expected control, not an unexpected failure, forced
assert or watchdog kill. Unchanged V/U/T controls retain their original expected
outcomes. No completed final case has a sanitizer/leak finding. There is no claim
that Linux leak detection measures ESP32 heap behavior.

W's real webserver, CLI, settings/storage/media/HID modules and actual selected
setup/loop bodies execute with named lower mocks. Tests cover disabled dynamic
File responses before/after ownership, immutable pages, copied body lifetime,
WS registration/data/disconnect/malformed input, bounded continuous serial,
fragmented commands, CRLF,512/513 overflow, embedded NUL, backlog STOP, queue full,
explicit SD, authenticated HTTP/status/STOP, disabled upload/update/restart,
mutator denial, admitted-write/reentrant-Start, quarantine/no replay, fresh clear,
foreign serial task, existing streams/MSC, source-size and changed-byte refusal.
W33/34 test the discovered settings/auth snapshot contention path. Existing V/U
regressions cover stale identities/deferred chunk retirement; no new async File
reservation is falsely claimed, because this feature is disabled from boot.

Framework F01–05 compile exact pinned response classes and selected constructor,
read and destructor bodies. Abstract base/File are mocks; request disconnect
ordering is source-derived, **not executed full request/AsyncTCP/FreeRTOS**. Native
W response-copy/disconnect is also a mock lifetime test. Actual package sources
are independently compiled and linked by both clean target builds; those are
build results, not target runtime tests.

Earlier two32-case runs passed364 assertions each and are superseded, not added.
The first links succeeded before the final snapshot-race correction; final clean
links supersede them. Post-link verifier diagnostics were resolved: a target
uint32_t mangling assumption was corrected against actual nm/disassembly; a dump-
section invocation initially rewrote scratch ELFs. Saved link commands recreated
the **exact recorded ELF hashes**; the corrected inspector writes a separate
inspection ELF and asserts source ELF/all artifact hashes unchanged. BINs, sources,
installed dependencies and owner files were untouched. No such diagnostic is
hidden as a hardware failure or an unperformed test PASS.

Exact commands, outputs, assertions and controls are in test-results JSON. The
linked receipts separately record sources/objects, actual link inputs, map/BIN/ELF
hashes, disassembly, marker and compiler frames. No physical acceptance case ran.
