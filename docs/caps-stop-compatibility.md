# Evidence-led Caps/STOP findings

## CONFIRMED in source and executed software tests

The composed candidate is the Mac Caps timing baseline plus the additive
`tests/caps_stop/application.patch`, `hid_trace.h/.cpp`. Root EvilDuck sources alone
are not the installed composition. Per-run Caps dwell remains5ms by default or
explicitly selected500ms; selection is RAM-only, captured at admission and not
changed by later UI selection. Trace is separately opt-in and starts OFF.

`route_u::requestStart/requestCapsTrial` admits one owned generation. `tick` dequeues,
preflights and services the adapter. `com::route_b::key` schedules key-down, dwell,
neutral key-up; `routeFinish` retires each operation. Normal completion closes the
source, empties the request queue, relinquishes the lease and returns idle. There
is no new worker/timer/replay in this patch.

HTTP STOP202 is a **request receipt**, not owner acknowledgement or host release.
`stopWithStatus` publishes a priority flag. Owner `tick` observes it, cancels the
adapter, closes the source and clears ownership through existing bounded cleanup.
STOP can race an already executing turn: a report accepted before owner observation
cannot be retracted. Tests prove no new Caps/other-key reports after owner-observed
STOP in the covered timing windows, with neutral cleanup permitted. Completion
callbacks after STOP may acknowledge old submissions; they are not new sends.
They have run=0/op=0 because no authentic transfer-generation identifier is provided.

`backend_b::submit` traces the actual `tud_hid_n_report` invocation and Boolean
return. Accepted means that API accepted locally, not USB host delivery. False can
be ambiguous; existing quarantine/failure semantics remain. The strong SDK failure
callback replaces a pinned weak no-op only to observe errors; it never retries.
The accepted keyboard LED path is traced separately from raw OUTPUT callback entry.
Incoming LED reports are host-to-device feedback, not proof of built-in keyboard LED.

## Competing hypotheses — not a diagnosis

1. Host/device-specific Caps-state reconciliation after prior legitimate reports.
2. Continued firmware sends, an unobserved additional Start or a legacy/live path.
3. In-flight accepted input or cleanup not observed by the host.
4. Observer context/sampling effects or another physical input source.

The handoff establishes none conclusively. A global polled Caps flag cannot identify
which keyboard emitted a report. Unplug ending transitions is useful evidence but
not a report capture. Neutral release clears held usages, not the host's latched Caps
state, and cannot promise to switch off a different keyboard's light.

## UNKNOWN / pending physical evidence

Actual post-STOP traffic, host consumption, delayed callbacks, effective initial
Caps state, native IOHID observer visibility and permissions, Mac LED behavior and
USB disconnect/reconnect semantics are unverified for this new application. Trace
does not implement DCD retirement fencing or claim end-to-end delivery. No firmware
behavioral fix is justified from the existing screenshots. The deliverable is scoped
instrumentation and a finite discriminating test, not a fabricated root-cause fix.
