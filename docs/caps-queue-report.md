# Caps Lock / LED feedback, request evidence and compact STOP review

**Software fixes implemented and mocked verification executed. New firmware build
BLOCKED by the historical core-tree provenance check. This is not an installable
firmware release and the task's clean-build acceptance requirement is unfinished.**

Branch: `capslock-queue-stop-fixes`; parent
`3dd4a083aa6634cf413ac7a43c36baaa749b7540`. Installed STOP/LED source remains
`d18b7fddedaecef27be9fd7e486ad2d092a513c6`. The owner's October 17 handoff reports
physical installation and verification of both slots, STOP cancellation, unknown
LED feedback, confusing queued runs, intermittent request errors and a possible
preview discrepancy. These are owner observations, not new Codex hardware tests.

## Findings and changes

All references below are to the **composed** application, not the unselected
legacy `EvilDuckS3` source alone. Materialization is reproducible through
`tests/caps_queue/prepare_sources.py`; before/after hashes are in
[caps-queue-source-manifest.json](caps-queue-source-manifest.json). The reviewable
production delta is [fixes.patch](../tests/caps_queue/fixes.patch). Historical
source, tests, profiles and package pins are not edited.

| Path | Before / evidence | After / remaining boundary |
|---|---|---|
| LED data GET | `webserver.cpp:webserver::begin` registered `/led-test` before `/led-test/data`. Exact pinned ESPAsyncWebServer3.12.1 `WebServer.cpp:337`, `AsyncURIMatcher::matches`, accepts `_value == path` **or** `path.startsWith(_value + "/")`. Thus generic GET consumes data GET and returns snapshot JSON. | Leaf data handler registered first; generic/data wrappers reject mismatched URLs. Incomplete data remains 409. UI requires text/plain and exact `EVILDUCK TEST 123` before rendering/downloading. C17–C19 exercise actual handlers/registration with a source-derived ordered matcher mock. |
| Queued run evidence | `webserver.cpp:handleRunScript` returned only plain-text `Queued Route B`. Coordinator already had request ID, phase, reason, line and diagnostic code. Queued is admission, not execution. | 202 JSON gives engine, state and decimal-string ID. `/status` includes `routeBLine` and `routeBErrorCode` from the same captured Status. UI shows matching queued/compile/run/terminal evidence. Missing-file and compiler failures become visible terminal results, not a blank legacy log. |
| Save followed by Run | `webfiles.h:runEditorScript` started a file after `saveScript` returned even on failed HTTP save. | Save returns success/failure; failed save cannot run stale stored contents. No automatic run retry or replay. |
| Auth confusion | `checkAuth` returned false when its TryGuard failed, so some content handlers could label mutex contention Unauthorized. Content loader retried fallback endpoints after all failures, including 401/409. | Bounded `authorize` distinguishes busy409 from bad-credential401 for affected content/delete handlers. Existing password validation remains. Script fallback occurs only for404. Legitimate ownership/queue conflicts remain409. This explains a code path, not every historical Unauthorized response. |
| STOP | Persistent large red panel; initial stale/offline UI had little correlated run evidence. | Compact sticky STOP while active/uncertain; separate disclosure opens details; one tap sends STOP directly. Confirmed idle/terminal collapses active control but retains terminal text and ordinary STOP. Timeout/offline or a different request cannot hide STOP or claim completion. STOP results open details; host release remains explicitly unproven. No Pause/Resume. |
| Poll/log errors | Status fetch could stall; overlapping polling possible; log rendered an HTTP error body without checking status. | Bounded response-body handling and one in-flight status poll. HTML/502 is an explicit HTTP error, not a successful run log. Empty legacy logs direct the owner to request status. Source of the owner's earlier502 remains unknown. |
| Library deletion | Library rows always hid Delete; state-changing deletion used GET. | Delete offered only for names present in authenticated `/list`, not firmware-only entries. Exact storage/file named in confirmation. POST with body `s`, existing safe-path parsing and storage ownership; GET405. Cancel submits nothing. C11–C15/C21 verify temporary fixtures, SD, auth, traversal and busy behavior. |
| Source bytes / preview | No evidence yet that the stored file lost `DE`. | C16 verifies exact save/load of first characters, UTF-8 BOM and CRLF/LF through actual endpoints. Preview does not substring away first characters. Browser Fetch BOM decoding and textarea newline normalization were not exercised by this native endpoint test; end-to-end browser byte preservation is not established. The owner's actual saved bytes have not been inspected; the historical `LAY` symptom remains unresolved, not declared repaired. |

## Caps Lock and raw feedback investigation

The selected compiler recognizes `CAPSLOCK` via `shortcut_keys.h` page07 usage
**0x39**; the event traverses Runtime, Bridge, Planner and the repository backend
into the mocked eight-byte report (C02). Planner tap presses and releases on
successive cooperative steps; no minimum Caps-specific dwell or host delivery
acknowledgment is established. No broad timing change or forced uppercase was
introduced. US character translation does not compensate for observed Caps state;
host Caps processing and editor capitalization remain separate physical questions.

**The proposed longer HOLD trial is not supported by this Route B composition.**
`tests/stage28v/adapter.cpp:74` explicitly fails `Fault::Capability` when compiled
`Program::ownershipCommands()` is true. The compiler/Bridge support for HOLD in
isolation does not override this adapter gate. C01 proves the exact proposed
HOLD/DELAY/RELEASE program ends with Capability and **zero HID calls**. Historical
S07 is preserved and still passes. The new UI now exposes the failure. It would
be incorrect to call the owner's unconfirmed long trial a proven macOS failure.
No silent legacy fallback or unreviewed persistent-ownership enablement was added.
C10 verifies cancellation after a **transient Caps press** with local clear output;
that is not a host release guarantee.

Feedback path: pinned keyboard descriptor uses report ID1; the reviewed Stage16
core sends OUTPUT to virtual `FeedbackKeyboard::_onOutput`; repository code checks
ID, pointer, length, mask, USB mounted/session/disconnect evidence before accepting
an observation. Core/descriptor identities are unchanged. C03–C05 invoke the real
derived production callback through a mock keyboard object, including malformed
input. New bounded counters expose callback entry count and last ID/length, without
capturing keys, arbitrary text or private host input. Callback entry counters are boot-lifetime observations; compare deltas and current-session feedback, not a historical last ID alone. Unknown/connected:false still
means feedback evidence is unavailable, not a disconnected cable.

One known boundary: the pinned routing patch cannot dispatch an unprefixed
**ID0, one-byte** OUTPUT through the keyboard's ID1 lookup; it does not guess that
payload's target. FEATURE is not treated as LED evidence. This is a source-proven
unsupported form, **not proof that the owner's Mac uses it**. Callback counters
cannot observe packets dropped before dispatch. A real transport trace or supported
raw-report observation would be needed to establish that cause. No descriptor/core
routing changes or generic report normalization were invented in this change.

## Verification

Fresh final software results are in `caps-queue-results.json`,
`caps-queue-ui-results.json`, `caps-queue-resource-results.json`, `caps-queue-related-results.json` and
`caps-queue-sender-results.json`.

- Composed production-source mock suite: **125 PASS, 0 FAIL, 6,574 assertions**.
  Includes22 new focused cases and103 selected unchanged LED/STOP/HTTP/shortcut/W
  regressions. Expected rejection of HOLD is a safety test, not a compatibility pass.
- Additional unchanged backend/diagnostic regressions on the changed composition:
  **63 PASS, 0 FAIL, 2,650 assertions**. Combined native suites: **188 PASS,
  0 FAIL, 9,224 assertions**, with ASan/UBSan/leak detection. Historical T34 and
  X13/X15 fixture limitations remain explicitly recorded by the inherited runner;
  they are not counted as passes.
- Embedded actual JavaScript in Node VM: **18 PASS groups, 0 FAIL, 31 assertions**.
  Covers correlated terminal errors, mismatched IDs, another page/reload, stale
  polling/timeouts, disclosure, one-tap STOP, no replay, failed saves, auth fallback,
  typed exact phrase and SD confirmation/cancel. This is not a rendered browser or
  physical iPhone layout test. Compact CSS/HTML is inspected; iPhone portrait remains
  an acceptance gate.
- Receiver module resource runs: **2 PASS**, ASan/UBSan/leaks. Native fixed receiver
  storage **1152 ->1160 B**, Snapshot **72 ->80 B**. Both before and after run1000
  observations without new allocations. These are **Linux native sizes**, not target
  RAM/heap/stack measurements.
- Inherited sender cleanup: **8 executable fake-API combinations PASS**, plus
  **3 Windows source checks**. Native Windows/.NET and Apple IOKit compilation/run
  remain NOT TESTED. Independent Caps/Num attempts and failure result are unchanged.
- Frozen Stage26: **235 protected files byte-identical**. Prior packages and all
  historical tracked bytes/modes are preserved. No historic expectation was changed.

Initial test development exposed incorrect assumptions that HOLD was admitted;
C01 was corrected to test the actual published Capability gate, without changing
that gate or historical S07. C10 now tests transient Caps cancellation. A C19
fixture initially overwrote the intended URL; its dispatch target was corrected.
S08 initially detected removal of existing explanatory text; that text was restored
inside compact details. Earlier harness builds also found missing pinned native
headers and duplicate mock network includes; these environment/fixture problems
were corrected. The final executed results above are not reused historical totals.

## Firmware build blocker — fail closed

[Exact evidence](caps-queue-build-blocker.json). This fresh cloud instance does not
have the prior verified core/build directories. The Espressif Arduino3.3.0 release
archive was independently obtained with the **same recorded SHA-256**
`c8525462e47b37b726c211b71afada0fca5859ba748963e4d967131355716ba2`.
All nine recorded Stage15 source checks match, and both framework source trees
match their published pins. Nevertheless the release's extracted whole-tree hash is
`8d9ff37fa810d0338ed89bc87aa26523ea39add6ec8ce947ae59c4abeedeccc8`, while the protected
workflow requires `27c2bae8bee6e4f8089417c048f41bfd255d7a80fab5e889bf74fb258112cb51`.
`tools/build_s3_patched.py` **refused before patching or compilation**. The original
historical per-file inventory needed to explain the difference is unavailable here.

The pin was **not** changed, bypassed or converted into a passing check. No global
core/SDK was patched and no unverified SDK archive replaced a pinned library.
New candidate build/post-link wrappers preserve the existing checks and extend
source verification with the new overlay pin, but their full execution remains
blocked. No new ELF/BIN, target SHA, compiler byte count, target static RAM, task
stack estimate or OTA measurement is claimed. No installable archive is published
under the identity of the unchanged current firmware.

Reference only: retained installed BIN **1,376,576 B**, SHA
`c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4`;
prior compiler program **1,376,423 B**, RAM **107,480 B**, free OTA
**6,225,600 B /81.892342403%**. These are historical baseline figures, not new builds.

## File inventory

The complete added-file list is [caps-queue-files.json](caps-queue-files.json).
No existing tracked file is modified: the five production-module changes are
explicitly applied only by the new hash-pinned composition overlay. Existing build
profiles and their historical source expectations remain unchanged.

## Completion boundary and next action

**GO:** source review and reproduction of the software-only tests.
**BLOCKED / NO-GO for installation of these changes:** restore/explain the exact
historical protected-core tree, then clean-build, verify linked provenance and
produce a new independently pinned app-only package. Retain the current working
installation/package. No original stock search or owner data restoration is needed.

Caps host delivery, raw LED transport, native senders, fixed-message roundtrip,
physical iPhone behavior and firmware/resource acceptance remain PENDING. The visible
finite reflection goal is **not complete**. Do not launch a helper, run a payload,
change defaults, enable autorun, install or flash automatically. See the owner
checklist for a staged future acceptance sequence and the existing package for
current-artifact recovery instructions. No hardware access, real HID, stored owner
payload execution, flashing, formatting or OTA was performed by Codex.
