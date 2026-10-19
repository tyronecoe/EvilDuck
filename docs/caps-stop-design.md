# Bounded source-tagged HID/STOP instrumentation

Baseline:5e22569709f44bd4a6c429beb43a055d94d39257. New isolated branch:
`caps-stop-hid-trace`. BuildId:CAPS-STOP-TRACE-20261019-v1. Historical source,
profiles, archives, verifiers, USB identity/descriptors, partition table and settings
schema remain unchanged. All composition changes are a new hash-pinned additive
layer. No timing/scheduler/cancellation policy change or language feature.

## Implementation and ordering

Actual source references are in `tests/caps_stop/application.patch` hunks:
- coordinator.cpp: `phase`, `complete`, `requestStart`, `requestCapsTrial`,
  `stopWithStatus`, `tick`: admission/run ID, captured dwell, dequeue, phase,
  published/observed STOP, loss, terminal reason. Existing queue is emptied by
  completion; STOP prevents queued Start from being dequeued in that tick.
- seam.inc: `route_b::key`, `routeFinish`: pending/terminal operation IDs.
- hid_backend.cpp: `backend_b::submit`: directly surrounding the real
  `tud_hid_n_report`; `receiveHostReport`: accepted LED mask after validation.
- feedback_diag.cpp: actual raw SET_REPORT hook, normalized valid input completion,
  and `tud_hid_report_failed_cb`. Pinned SDK weak callback is a no-op; new strong
  callback only records type/instance0, no dereference/retry. Existing OUTPUT/
  FEATURE routing and input descriptor remain unchanged.
- webserver.cpp: `handleHidTrace`, `handleStop`, authenticated routes. HTTP receipt
  uses the captured request ID even if another generation starts before logging.
- webfiles.h: `hidTrace`: explicit enable/disable/read-next only, no polling/replay.

`hid_trace.cpp` stores128x32-byte events plus fixed counters/state; a read copies at
most8 into a Batch, JSON buffer2304bytes. Saturating counters and explicit oldest/
latest/overwritten identify lost evidence. Capture expires on the next event/read
at120seconds; no background timer or unbounded retry. Sequence exhaustion or backward
clock disables capture. Disabled fast path performs no ring write/allocation. The
backend still categorizes the fixed six-key snapshot; no variable-length processing.
No payload, filename, arbitrary key identity, character, password or key-array bytes
are recorded. Max HTTP page8, browser success history16000characters; optional tool
has its own finite count/time limit. Browser error text is manually requested only.

Trace has its own short critical section (host mutex in native tests). Owner/publication
and feedback locks may precede trace; trace never acquires either lock. HTTP takes an
execution guard for auth/control and coherent ring copy, then releases it before
JSON serialization. Callback logging uses no execution guard, network, storage or
allocation. This is software lock-order review, not a physical latency measurement.

## API and decoding

Authenticated POST `/hid-trace/enable` resets while idle only;409 while owned.
POST `/hid-trace/disable` stops capture even while owned. GET `/hid-trace?after=N`
reads the next8 events.401/400/409/503 remain visible, never mislabeled current data.
Controls execute no script, HID, storage or NVS action. Read header contains current
feedbackSessionSample and bootMarker, not per-event USB transfer/session attribution.
Enabling resets sequence/cursor; do not merge separate captures as one epoch.

Each event:sequence, device monotonic atUs, run, operation, source, event, detail.
Owner run is admission ID. Backend has owner run only while leased; unleased backend
output is run0. USB/LED callbacks always run0/op0; no guessed run matching.

Detail is event-specific:
- admitted:captured Caps milliseconds; phase/terminal/operation-end:existing enum value.
- pending:1 Caps usage,2 other operation.
- backend attempt/accepted/refused bitmask:1 Caps present,2 other nonmodifier present
  when Caps absent,4 clear request,8 modifier present,16 active Route B lease.
  A Caps+other-key snapshot is categorized Caps; exact other keys never logged.
- input-completed:1 Caps present,0 Caps absent; **0 does not prove neutral**.
- raw-output:(reportType<<8)|reportId; led-accepted:Num/Caps/Scroll mask&7.
- transfer-failed:report type; stop-published/http202-prepared:owned Boolean.

Counters[17] are internally bounded/tested but HTTP returns the retained sequence,
overwrite and clock counters plus events, not all lifetime per-kind totals.
`http202-prepared` occurs before send invocation, not proof browser receipt. Ring
write timestamps are sampled at logging; cross-core ordering is serialized ring order,
not a measured bus/host order. Events can expire/overwrite: gaps preclude a no-output
conclusion. Failure hooks cannot see packets rejected before that SDK callback.

## Expected minimal traffic and limits

For DELAY2000 / CAPSLOCK / DELAY1000: initial neutral synchronization, one Caps-down,
neutral-up after captured dwell, terminal neutral cleanup through existing adapter.
Delays cause no character report. Exact duplicates/cleanup counts follow current
backend states; check actual trace rather than assume each callback means a new send.
After terminal no later owned key is expected without new admission. Tests cover STOP
before press, during500ms dwell, between toggles, after completion, disconnect,
ambiguous queue refusal/quarantine, two generations and concurrent trace publishers.
No guarantee that an accepted neutral was received while physically disconnected.

Target compiler estimates:handleHidTrace3184bytes static frame; trace note48bytes, append48bytes, failedcallback32bytes. These are individual compiler frames, not total call chains. Pinned Async_TCP/src/AsyncTCP.h:45-46 defaults CONFIG_ASYNC_TCP_STACK_SIZE to8192*2; no target flag override was found in the build command inventory. Actual RTOS high-water/latency remains unmeasured. Loop stack selection remains8192bytes. HTTP String/response allocations are inherited, not eliminated by fixed trace storage.
