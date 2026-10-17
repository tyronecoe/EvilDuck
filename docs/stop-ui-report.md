# Change A — visible STOP and correlated local completion

Baseline: composed HTTP-hardening candidate commit400b25dd1eb401eb9ab08eae2bf8c9c4289c4098.
The earlier installed candidate remains unchanged; this is source/software work.
The source is a separately pinned scratch-only delta, preserving historical trees.

The actual `/`, `/index.html` and `/index.htm` handler serves embedded INDEX_HTML;
`/index.js` serves embedded INDEX_JS before filesystem fallbacks. The new sticky,
red48px-minimum STOP script button lives outside home-page tabs. It remains usable
when polling fails, status is stale or the browser reconnects. Other pages link
Home; this does not claim a STOP control on every separate settings/terminal page.
Existing `sessionStorage.duckPw` / `X-Duck-Password` authentication is reused; no
credentials are hardcoded or printed. Home Run now explicitly names the reviewed
Route B engine, visibly labeled; legacy `/run` clients are not silently changed.
No Run or STOP is automatically replayed; in-flight duplicate submissions are
suppressed. Fetch has a4-second UI timeout, which is not a device cancellation bound.

`POST /stop` has no body and carries `X-Duck-Password`. Authentication retains the
prior bounded5-tick guard.409/401/network/timeout are errors, not displayed success.
202 JSON is admission only: message, engine, decimal-string requestId and wasOwned
for Route B. The coordinator atomically copies that execution ID while publishing
its existing priority STOP flag. No new execution owner is introduced. `/status`
adds the same request ID and owned bit from its one coherent Route B snapshot.
Only an authenticated, matching request-capture with Idle/not-owned/Cancelled
confirms local cancellation in the UI. Prior IDs and published observations cannot
confirm it. Completion, quarantine, legacy idle and no-active-at-admission have
separate qualified messages. No message proves host key release.

For legacy execution, HTTP only sets an atomic request; existing owner update
consumes it and calls the existing stop/cleanup. HTTP does not submit HID cleanup.
Route B STOP stays on its existing priority publication/owner path. The old HTTP
contention fix, authentication and all execution/publication locks remain.

Focused tests:84 native cases PASS,0FAIL,2,733 assertions, ASan/UBSan/leaks clean;
9 actual embedded-JS VM groups PASS,0FAIL,20 assertions. Tests include60-second
DELAY, WHILE, cancellation while a transient CTRL report is active, queued text,
no later output after owner completion, legacy held-state cleanup deferred to owner,
actual served assets/routes, authentication and unchanged H/K/W regressions.
Route B still rejects persistent HOLD (existing capability limit); the task does
not authorize enabling it. Native report cleanup proves only mock submission.

An initial S07 fixture used malformed HOLD CTRL and failed its expected capability
classification. It was corrected to existing supported-parse HOLD a, which is
rejected by the unchanged capability gate; no parser behavior was changed. Earlier
harness imports/missing webfiles copy failed before compile and were corrected.
JS checks cover admission versus confirmation, stale IDs, wrong snapshot kind,
401/409/500, offline/retry, timeout, duplicate STOP/Run and explicit engine selection.
These are not real Chrome/iPhone rendering, native OS or physical timing results.

A new reviewed firmware build including A will be produced with Change B. Asset
installation later needs that reviewed application update and browser hard refresh;
no SPIFFS formatting/upload is needed for these embedded assets. No deployment is
authorized by this report. Physical acceptance and host receipt remain NOT TESTED.

Added files: docs/stop-ui-report.md, docs/stop-ui-results.json,
docs/stop-ui-source-manifest.json, tests/stop_ui/{prepare_sources.py,stop.patch,
run_tests.py,test_main.cpp,test_ui.cjs}. No historical files modified.
