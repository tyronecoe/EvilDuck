# LED boundary diagnostic contract

Baseline: 0d100caa120d11920341e493019e5fc016c05a4f. Its ZIP and application identities
are independently checked public artifacts. The currently running board image is
NOT independently identified: no owner installation receipt or live readback was
supplied. Screenshots cannot identify a build. No reinstallation was requested to
prove the baseline. This update adds visible ID LED-FEEDBACK-BOUNDARY-20261018-v1.

## Findings and selected changes

The prior connected=false field means no accepted LED report in the current
feedback session. It never independently measured USB attachment. callbacks is
inside FeedbackKeyboard::observe and cannot count reports rejected upstream.
The four advancing capturedAtUs snapshots therefore established fresh unknown
feedback, not a disconnected cable or absence of SET_REPORT arrivals. The later
text test demonstrates ordinary typing only. The differing uptimes do not prove
continuous boot. Caps output and host LED feedback remain separate uncertainties.

The selected layers are tests/mac_release -> tests/caps_queue -> led_return ->
stop_ui -> http_snapshot -> historical bounded Route B source preparation.
New tests/led_feedback/prepare_sources.py applies a separately hashed additive
application.patch AFTER that chain, then copies two pinned helper sources. Root
firmware and every prior profile/verifier/receipt remain unchanged.

A separately pinned diagnostic core profile extends the approved publisher
archive profile, using its exact existing HID and NVS patches first, then the
new core-diagnostics.patch. Only USBHID.cpp and USB.cpp receive this extra patch.
No global installation, SDK archive, identity or descriptor changes. USB.cpp's
mount/unmount/suspend/resume callbacks invoke a bounded weak hook synchronously
before the existing Arduino event post; the application strong hook invalidates
feedback and the fixed-message decoder. It does not activate application services.
The existing SDK event-post wait policy remains upstream behavior, not a new
nonblocking guarantee for the entire USB stack.

The actual tud_hid_set_report_cb counts raw arrival before all rejection paths.
The callback's selected type/ID/output dispatch decisions remain unchanged. A
pointer comparison checks whether registered report1 actually belongs to this
FeedbackKeyboard object, rather than assuming any ID1 device is the keyboard.
Each routing attempt and dispatch is recorded separately; FEATURE only increments
FEATURE metadata and never becomes LED OUTPUT. No guessed one-byte ID0 fallback.
No payload bytes are stored. lastEffectiveId may show the single leading ID byte
that the EXISTING prefixed OUTPUT route attempted; arbitrary FEATURE data, text
and raw buffers are never logged. Completion diagnostics inspect only valid-sized
keyboard input report frames and retain only a Caps-present Boolean and timing.

## Exact counter/field meanings

All counters saturate at UINT32_MAX and are boot-lifetime; GET/Observe never
clears them, starts the receiver, injects a key, mounts storage or initializes USB.
Snapshot metadata is copied under its own short critical section. No callback
uses the executor mutex, heap allocation, filesystem, networking or printing.
Application feedback and diagnostic snapshots use separate locks; the endpoint
checks their session equality. These are sampled observations, not an atomic USB
bus transaction or guarantee that state has not changed after sampling.

- rawArrivals: actual SET_REPORT entry, including malformed instance/type/length.
- rawLast*: original callback metadata, not normalized metadata. After session
  invalidation these current-session fields reset to unknown; counters persist.
- outputAttempts: every registry lookup attempted, including ID0 before a prefix.
- outputDispatches: a device OUTPUT virtual method returned; not receiver acceptance.
- keyboardDispatches: dispatch of report1 to the registered actual keyboard object.
- callbacks: legacy derived-keyboard observe calls; may be manually invoked by a
  future internal caller, so it is explicitly not a raw USB counter.
- reports: legacy accepted session-matched LED reports; receiverOutcome.accepted
  tracks the new receiver boundary. Concurrent invalidation can classify a late
  acceptance as stale; no prior-session evidence is claimed as current.
- routeReject: instance, nullBuffer, emptyOutput, type, missingRoute,
  idZeroUnprefixed (reserved6..8 remain zero). One raw report may have two failed
  attempts (ID0 then prefixed ID). This is not a one-error-per-arrival total.
- receiverOutcome: accepted, id, lengthOrNull, padding, notConfigured,
  staleSession, suspended. HID IN readiness is NOT required for OUT acceptance:
  a busy input endpoint does not imply the host feedback path is disconnected.
- usbBusConnectedSample=tud_connected (SDK speed established, not cable sensing);
  usbConfiguredSample=tud_mounted (nonzero SDK configuration);
  usbSuspendedSample=tud_suspended; hidInReadySample=USBHID::ready, i.e. current
  configured/not-suspended/not-busy IN endpoint according to the pinned stack.
- activeProtocolSample=tud_hid_n_get_protocol(0), 0 boot/1 report. Last raw protocol
  is separate. interfaceProtocol is actual core descriptor configuration at the
  last raw callback. The explicit static USBHID object precedes the keyboard
  constructor in this TU; it selects NONE before the keyboard requests boot.
  We expose the actual value instead of changing the descriptor or assuming boot.
- registeredKeyboardAtLastRaw is null without a current-session raw observation;
  otherwise it is the actual registry/object comparison. It is not live polling.
- connected remains legacy feedback history, explicitly deprecated. observed
  remains historical report evidence. ledEvidenceValid additionally requires
  session coherence, configured/not-suspended stack sample and <=5-second age.
  Unknown/stale booleans remain null, not confidently off.
- bootMarker is a 64-bit ESP random correlation nonce, generated at application
  HID begin. It is not authenticated, cryptographic or mathematically unique.
  Compare it WITH buildId and uptimeUs; counters from different boots cannot be
  subtracted. No current-board identity is inferred from prior screenshots.

## Caps output trace and limits

Canonical CAPSLOCK maps to usage0x39 in the selected compiler/adapter. Planner::tap
queues an eight-byte press snapshot. Planner::step submits it, then queues the
release for a later step; DELAY after release does not hold the key down.
Route B's backend submits via tud_hid_n_report(0,1,...), not the blocking
USBHID::SendReport path. Endpoint refusal and cancellation retain their existing
single-owner cleanup behavior. No Caps dwell, global typing delay, grammar or
HOLD/RELEASE support is changed. Local submission success is not host delivery.

capsDown/UpQueued are accepted queue-return transitions; ReturnUs timestamps
are read AFTER tud_hid_n_report returns. Down/UpCompleted are the actual core
report-completion callback observations, with CompleteUs timestamps. Completion
can occur before the submitting function returns; do not infer ordering from
queue-return timestamps or treat differences as precise physical key dwell.
Only exact9-byte ID1 report-mode or supported8-byte boot keyboard frames are
inspected. Session invalidation clears pending pair tracking. A controller/SDK
late completion has no authenticated wire epoch; these metrics do not establish
host key release, physical dwell, endpoint retirement or full USB session safety.

## Reset and transport boundaries

SDK mount/unmount/suspend/resume invalidate feedback synchronously, avoiding reuse
of known prior-session state while Arduino's notification is queued. The old
asynchronous STOPPED-event failure handling remains intact. A raw bus reset has
no separate new ISR hook here; SDK configuration sampling suppresses validity
while unconfigured and the next mount invalidates evidence. Low-level event
ordering, silent resets, stale hardware transfers and High Sierra behavior remain
unverified. The TinyUSB stack is not replaced or represented as physically proven.

Outcome: repaired misleading diagnostics plus an instrumented candidate awaiting
one physical observation; no source evidence proves the Mac's actual packet
format, and no physical repair is claimed.
