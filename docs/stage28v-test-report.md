# Stage28V executed verification

Fresh completed runs on Linux x86-64; native lower interfaces are simulated.
No Apple-clang, physical USB, board or RTOS execution is implied.

| Suite | PASS | Unexpected FAIL | Assertions | Classification |
| --- | ---: | ---: | ---: | --- |
| V actual-module service tests | 56 | 0 | 566 | New focused cases |
| Unchanged U runner/cases | 64 | 0 | 515 | Separate regression, original U sources |
| Unchanged T runner/cases | 47 | 0 | 467 | Separate regression, original T sources |
| Affected original Stage14 production cases | 77 | 0 | 67,371 | Existing semantics |
| Final-selector-disabled V production comparison | 77 | 0 | 67,371 | Exact exit/stdout/stderr match, not additional coverage |
| Original controlled startup | 30 | 0 | 635 | Unchanged Stage25 cases |
| Selector-off V startup comparison | 30 | 0 | 635 | Same cases on actual patched settings/storage/SPIFFS/ino, not new coverage |
| V preparation controls | 7 | 0 | separate checks | Healthy plus six intentional corrupt/reuse refusals |
| Pinned target declarations/object compilation | 20 | 0 | not assertion tests | Enabled candidate, no link or target execution |
| Selector-off target firmware objects | 15 | 0 | not assertion tests | No route/lease symbols, no link |

Unique listed case sets total274 PASS /69,554 assertions. Do not add the repeated
selector-off comparison executions or superseded runs to inflate coverage.
Historical language XPASS, USB XFAIL, Stage9 observations and prior risk receipts
remain byte-identical; they were not rerun or relabeled as new Stage28V results.
The V48 raw-VFS capability observation is expected and separately blocks the
complete isolation gate; it is not a false claim of an escaped enabled handler.

Completed C++ runs use ASan/UBSan and leak detection. The explicit V01 negative
control exits1 for `deliberate negative control`; immutable U/T negative controls
also fail for their intended reason and are not unexpected failures. No sanitizer
warning remains in completed final cases. No watchdog timeout is counted as PASS.

Earlier diagnostic runs are retained in the result classification: duplicate
mock Arduino declarations, a missing mock NeoPixel/Arduino declaration, and the
inherited allocation probe's nothrow-array mismatch were corrected in V-only
fixtures. The mismatch was a real ASan finding in that superseded fixture, not
ignored, reclassified as a clean run or hidden by disabling alloc/dealloc checks.
The earlier48-case run passed402 assertions but is superseded, not added.
The first56-case whole-web run also passed566 assertions; the final run verifies
the final selector-off-only declaration guard and supersedes that run. An
initial comparison-runner import error occurred before compiling and was fixed.

The final primary TU includes the **entire patched webserver.cpp**, not rewritten
handler logic. Registration through actual webserver::begin is executed; run,
status, STOP and disabled upload/update completion use the simulated server's
registered callbacks in selected cases. Other cases invoke the actual static
bodies. `web_handlers.inc` generated in scratch is an unused body-hash evidence
clip; it is not the compiled implementation. Source receipts identify these
bodies and the whole module. The lower platform removes only mock namespaces
replaced by actual settings/storage/SPIFFS/LED code; no tracked older fake changes.

Important cases: V26/V52 admitted operations survive STOP/reentrant Start denial;
V27/V51 real-thread contention refuses without waiting; V28/V29 chunk task/deferred
abort; V30 nesting boundary; V31 owner-only stepping; V34/V35 no retry from ambiguous
lower outcome/loss; V36 fresh local clear; V41/V42 changed/removable media refusal;
V43/V44 actual MSC startup/callback state; V45/V50 WS dispatch/bounds; V55/V56 actual
registered completion/status/STOP callbacks. Task identities, network cancellation,
media churn and lower I/O are synthetic. Native success does not close framework
request cancellation, transport lifetime or SDK/VFS bypass questions.

Commands, exact stdout/stderr, assertion totals, source hashes, allocation traces
and negative controls are in stage28v-native-results.json. Target command lines,
SDK/core pin identities, sections, symbols and frame estimates are in the separate
target-object receipt. Both preserve their actual scope.
