# Execution-busy investigation: installed shortcut candidate

Owner-reported target: `5c19f0dacb25960bda36a97f4ff871937a3cc9e7`.
One spaced observation: ten successful HTTP requests and two409s, ticks advancing.
Browser tabs closed; separate63-second USB idle observation and three focused
hardware fixtures passed. These are supplied observations, not new physical
measurements or logs independently inspected in this task.

The exact reviewed composition is reconstructed by immutable X + shortcut pins,
not inferred from the frozen `EvilDuckS3` tree alone. The patch applies to that
composed source; original sources/builders/packages remain unchanged.

## Confirmed lock path

- `EvilDuckS3.ino::loop`: register Route B owner, duckscript::update, com::update,
  cli::update, then delay(1) OUTSIDE their execution-lock scopes.
- `duckscript::update` invokes route_u::tick before the legacy execution Guard.
  When idle, it still acquires the recursive execution mutex and tests legacy
  state. When Route B owns execution, it returns after the coordinator tick.
- `com::update` takes the same mutex, updates attackmode/MSC and HID transport,
  consumes loss, then returns from Phase::Idle. Nested API guards are recursive.
- `route_x::endTurn` reads backend status through that mutex on every coordinator
  turn, including idle. Resource sampling is outside publication critical sections
  and happens at most once per eligible1000ms, not every turn.
- CLI input reading has a64-byte/turn budget and no outer execution guard on an
  idle empty serial buffer. Completed legacy commands enter cli::parse's Guard;
  synchronous file/settings/CLI operations can hold the mutex longer. This is NOT
  evidence that CLI serial reading holds a lock on every empty turn.
- Live HID ingress, settings, storage callbacks and other web handlers also use
  execution guards. USB callbacks/MSC callbacks with zero-wait TryGuard must retain
  that policy. Their loss/error/ownership behavior is not removed by this fix.
- Original `/status` and `/routeb/diagnostics` perform zero-wait TryGuard before
  authentication and copy/format/send under that lock. Collision with ANY owner
  produces409 immediately. It is a contention indication, not proof that a script
  is active, a browser is connected, a mutex leaked or the loop stopped.
- checkAuth also takes TryGuard in Route B builds. Under an already held recursive
  handler lock this succeeds; original HTTP STOP calls checkAuth without such an
  outer guard, causing auth contention to masquerade as401.

Thus browser tabs are not required to produce collisions. Source inspection and
native contention tests independently establish this mechanism. The exact holder
and scheduling responsible for the owner's12 particular observations are UNKNOWN:
the installed build did not record lock-holder telemetry. No physical attribution
or expected409 percentage is invented.

Pinned AsyncTCP defaults: priority10, any core(-1), stack16384 B; Arduino loop task
priority1 on its configured running core. The S3 SDK uses1000 FreeRTOS ticks/sec.
Depending on actual scheduling, immediate-fail polling can repeatedly coincide
with a low-priority owner. The new wait blocks the request task on a recursive
mutex so the scheduler/mutex priority inheritance can let the owner release it;
this is not busy-spin, a delay while holding it, or proof of real-time latency.

## Correction boundary

Only the two snapshot endpoints and HTTP STOP authentication use BoundedGuard:
try immediately, then ONE wait budget5ms (five ticks in this pinned build). Failure
still returns409 and never returns fabricated success/cached JSON. Correctly
acquired but invalid credentials produce401. Request timeout does not publish STOP.
After an explicit authenticated successful retry, Route B STOP goes through the
existing priority publication flag, independent of the ordinary request queue.
Legacy STOP retains its existing execution behavior after authorization.

Snapshot state and live authentication are captured under the same execution
mutex. All owned String copies are made while protected. JSON formatting and
response submission happen AFTER release, including401 responses. Slow network
submission no longer extends these successful snapshot/auth lock scopes.

Route B publication has its own short critical section and can change while the
execution mutex is held (especially unleased capture/stop completion). `/status`
therefore derives phase, reason, running, script name, line and Route B error from
ONE copied route_u::Status. Independently calling duckscript::running afterwards
could combine different generations. A forced transition regression validates
this correction. Other legacy/settings/storage fields remain protected by the
execution mutex. Quotes/backslashes/control bytes in status strings are escaped
outside it, preserving JSON parseability.

`/status` adds snapshotKind=request-capture and capturedAtMs; this describes the
capture, not a claim that state is still current when the client receives bytes.
`/routeb/diagnostics` adds snapshotKind=published-observation, observationKnown,
observedAtMs/observationAgeMs, resourcesAtMs/resourcesAgeMs and completedTurns.
Age arithmetic is unsigned32-bit millis; only interpret age when observationKnown
is true and within one wrap interval. Phase/reason/backend evidence are from the
last completed owner turn, resource values from their sampled timestamp; ticks,
admission/STOP counters can be newer. One published struct is copied coherently;
its fields are deliberately NOT represented as one instantaneous hardware state.
No old cached observation is substituted for a fresh request capture. Diagnostics
are measurements, not liveness or host-delivery proofs.

The fixed record buffer grows1024→1536 B for the expanded schema, including the
local CLI diagnostics path. Worst-width numeric formatting/truncation is tested.
No unbounded report queue, retry loop or background snapshot task is introduced.

## Owner telemetry and its limits

The patched execution header tracks recursive depth under the execution mutex.
Only the OUTERMOST guard sets a holder class; nested getters do not overwrite it:
0 unknown/releasing gap,1 Other,2 DuckUpdate,3 ComUpdate,4 DiagnosticBackend,
5 HttpStatus,6 HttpDiagnostics,7 HttpStop. Unclassified synchronous service/CLI
holders remain Other, not guessed identities or task names.

New response fields executionContentions/executionTimeouts count ONLY bounded HTTP
acquisitions that needed a wait or timed out. lastContendedOwner samples the
outermost class when the immediate attempt failed; it can be0 in ownership-change
windows and is not proof of the holder throughout the entire timeout. maxExecutionHoldUs
measures completed OUTERMOST holds, including preemption, modulo32-bit microseconds;
not valid for holds exceeding one~71-minute wrap and not an absolute transport
latency or task-stack measurement. Counters saturate at UINT32_MAX. Statistics
are short synchronized observational copies, not atomic with application snapshots.

A separate static portMUX guards only fixed telemetry words; no execution acquire,
publication lock, SDK call, formatting, allocation or deliberate wait occurs while
it is held. Lock order is execution→telemetry; failed-attempt observation releases
telemetry BEFORE waiting for execution. Publication and telemetry critical sections
are not nested by this implementation. No new RTOS mutex allocation is required
for telemetry. Host tests use an independent std::mutex for that tiny region.
An initial lock-free std::atomic assumption was rejected by the target compile;
it was removed, not bypassed with a weaker assertion or SDK change.

Five ticks is the scheduling WAIT budget, NOT a guaranteed five-ms wall-clock HTTP
response. Long filesystem/USB/library operations, scheduler delays, allocator or
network backpressure can still exceed it. String allocation during protected
capture remains; response assembly and network allocation move outside. Existing
legacy API bounds and failure semantics are not rewritten. This fix does not
promise zero409s, fix transport retirement, hide starvation or establish physical
performance. Future owner-authorized observation can use the new fields to
attribute remaining waits and compare progress.
