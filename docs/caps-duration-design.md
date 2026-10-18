# Caps-only duration trial and feedback-path review

Baseline: `3e693fbe790af670278716cdf4d64c75485cb097`, composed through
`tests/led_feedback`, not the unselected root firmware. Owner-installed application
`2c657f0c74f1d12c88aa1e6fa6daf5cc76de36e8e68bc41a325f39b19c9045a7`,
1,386,176 bytes, is the rollback. The owner supplied installer verification and
observed `LED-FEEDBACK-BOUNDARY-20261018-v1` boot ID; this is owner-reported physical
evidence, not a new cloud readback. Historical reports remain unchanged.

## Owner evidence and decision

Ordinary `STRING LED BOUNDARY CHECK 123` reportedly typed exactly. Physical Caps
OFF/ON/OFF observations shared boot `d37e7cc1ef0a5950`, feedback session3 and current
configured/not-suspended samples. All cumulative raw arrivals, dispatch and accepted
LED counts stayed zero. No ID-zero packet was observed. Registration=null and
protocol255 at last raw are unobserved defaults, not registration failure.

Owner's ordinary Caps tap did not change the Mac keyboard light or subsequently
manually typed case. Later cumulative counts (5/7/8 pairs) show repeated local
submissions/completions, not one fully correlated request. Queue-return intervals
were6903/6912us; completion intervals6978/5966us. None is wire dwell or proof of OS
acceptance. Apple advises a slightly longer Caps press but establishes no numeric
external-keyboard threshold here:
https://support.apple.com/en-gb/guide/mac-help/-mchlp1240/mac .

The actual composed `com.cpp` (not the unused preview Planner) implements Route B
output through `seam.inc` -> `report` -> `Phase::Press` -> backend `beginReport` ->
`tud_hid_n_report(0,1,8bytes)`, then `waitFor(5,Phase::Release)`. Subsequent scheduler
turns submit release. A following DELAY does not extend this press. Older report
wording attributing this composed timing to Planner was imprecise; historical
source is retained as evidence.

## Narrow owner operation

Authenticated POST `/caps-trial/start` requires the exact form field `ms` equal to
`0`, `100`, `250` or `500`. Zero selects the unchanged 5ms scheduled baseline.
These are finite experiments, not Apple requirements. GET `/caps-trial` observes
only; it does not start/repeat a trial. Dashboard provides explicit selection,
confirmation and refresh. Compact STOP and expandable details remain intact.

Admission uses the existing bounded execution lock, publication queue, idle/media
checks, transaction exclusions, monotonic request ID and single owner. The owner
compiles a fixed memory-only `DELAY 5000; CAPSLOCK` program using the existing
compiler/adapter. No owner file is read, saved or modified. This is not HOLD/RELEASE
language support: the existing capability rejection remains.

Only an active diagnostic Caps press changes the wait. Dwell starts at the
`waitFor` millis sample immediately after successful `beginReport` returns. The
microsecond downReturn timestamp is sampled inside the backend immediately after
`tud_hid_n_report` returns. These closely related but distinct timebases are not
physical on-wire timing. Scheduling may lengthen the interval. Millis subtraction
remains wrap-safe. Five-second focus delay is separate from dwell. STOP during
that delay can prevent the press entirely.

Backend lease and execution ownership remain held through release and terminal
cleanup. No timer callback or detached delayed work exists. Normal completion,
STOP, runtime/deadline errors and loss reuse existing adapter cancellation, neutral
cleanup, one-second pending/clearing bounds and quarantine. Endpoint-not-ready
polling makes no submission; ambiguous called-false outcomes are never replayed.
A disconnected/suspended or changed feedback session cancels the trial. Cleanup
may be impossible and may quarantine; the host is never claimed released.
No automatic retry, reconnect replay or automatic arming is added.

`caps_trial` is fixed storage with an independent short critical section. It keeps
one last trial, requested duration, request ID, boot nonce, feedback session,
accepted down/up return timestamps, observed down/up completion timestamps and
terminal reason. The asynchronous completion hook sees only validated keyboard
frames/Caps presence. Zero/unobserved completion fields are not fabricated.
Completions outside the active trial window are not attributed to that trial;
boot-lifetime legacy counters remain separately available. USB callbacks have no
authenticated hardware epoch; even a locally matching pair cannot prove transport
retirement, host release or physical lock state. Refresh is sampled evidence.

Queued admission can precede owner initialization of the trial record: compare
requestId with trialId before interpreting timestamps. After an ordinary subsequent
script, requestId may differ from the retained last trial. Do not compare another
request's reason to the last trial; the trial record is a separate observation.

## Feedback decision enabled by this release

The candidate is an actionable duration experiment, not another instrumentation-only
release. If manually typed `abc` changes case following the longer pair, timing is
supported as a Caps-output factor. Genuine incoming OUTPUT evidence is a separate
success criterion. If Caps works while raw arrivals remain zero, review the Mac's
matching HID service/descriptor before changing receive routing or identifiers.
If neither baseline nor longer trials works, reduce to one correlated trace and
review recognition/report exposure; do not globally slow keys or keep replaying.
Fixed-message integration remains gated on physical Caps AND Num feedback, with
only the finite RAM-only `EVILDUCK TEST 123` receiver scope retained.
