# Stage28E bridge design before implementation

Mock-only opt-in module. Bridge owns Runtime and Planner; only const inspection is exposed.
There is no hardware transport, parser change or change to existing Runtime Sink ABI.

Phases: Idle -> Syncing -> Prepared -> Running -> Completed/Cancelled/Error.
An error from pending report work first becomes Failing; the next bounded Runtime turn returns
Failed through its existing sink path. Explicit Draining returns to its saved terminal state.
Prepared permits bounded owner setup via bridge wrappers; Running denies unrelated transitions.

begin queues initial neutral sync. step attempts one planner report until Prepared. start then
borrows a ready Program and begins Runtime. Each Running step does either one Planner step OR
one Runtime tick, never spinning. A first keyboard callback admits one action and returns Retry.
Intent Waiting persists until accepted press and restoration; then Ackable returns Accepted once,
clearing intent at that boundary. A next identical event starts a NEW intent. Equality only detects
protocol mismatches for a current intent; it is not event deduplication/identity. Only the owned
Runtime's guarded callback window may submit events, and reentrant/bogus source calls reject.

Sequence aa: sync0; admit a/Retry; press4; restore0; ack a; admit next a/Retry; press4; restore0;
ack second a. Each press/restore may retry unchanged. Initial/owner readiness cannot acknowledge
a source event. Counters track admissions and keyboard/Delay acknowledgements without a log queue.

Delay has no planner action/report. With no outstanding intent and Planner Ready, accept it
immediately; Runtime itself owns the wait from this accepted timestamp. Its serialized event
protocol prevents following keyboard work from advancing before delay completion. Runtime elapsed
expiry is checked before pending planner work by allowing the existing Runtime timeout path to
run, rather than extending its deadline while report retries occur. All clocks are caller uint32.

Cancel-after-press clears Runtime/intent/owners; no ack is fabricated, accepted report remains.
Explicit drain publishes only0 under Planner budgets, with accepted neutral evidence required
before new begin. Completion/STOP/runtime failure clears owners but cannot prove mock neutral
if persistent holds remain. Sink failure/throw keeps copied planner phase/reason plus Runtime
error after propagation. Callback cancel Accepted/Retry/throw follows Stage28D evidence rules.

Lifetime: Bridge outlives callbacks; Program outlives active Runtime; report callback/context stays
valid until all intended cleanup or a fresh successful begin. Const references are observations,
not external stepping/ownership authority. Single-thread API, no callback self-destruction or
blocking/cross-thread guarantees. Existing compiler/runtime/planner caps remain unchanged.

## Ownership/lifetime detail

Program must remain alive while the owned Runtime or its Program-dependent inspection APIs
can reference it, normally until a new successful begin resets Runtime or Bridge is destroyed.
Terminal getters for snapshot/error/counters do not call report sinks. begin replaces Runtime
in its fixed member storage with placement construction to reset all old variables/errors;
no allocating new, aggregate Bridge copy or dynamic queue. Planner's accepted evidence is never
forgotten before its restart gate. Context may be retired only when no future step/drain can use
it or after a new successful begin replaces it. Destructor cancels internally but sends nothing.
Do not mutate through const getters, destroy objects inside callbacks or use cross-thread calls.

Public sourceSink matches the existing callback ABI but rejects null context and any call outside
the owned Runtime window, including report callbacks. It is not an event injection API. Pure
validEvent tests unsupported fabricated values (unreachable from ordinary source preflight).
One pure Planner::validUsage query is the only planner API extension; existing admission behavior
and structure size are unchanged. Initial/owner Ready states cannot complete an unadmitted source.

Error diagnostics snapshot the first fault and its current event/planner phase/reason; Runtime
error is copied after normal propagation. Planner live getters also expose a subsequent drain
failure without overwriting the original source cause. Invalid prepared setup requests reject
without starting the script. Setup report failures stop the bridge. Completion/STOP/errors clear
owners, but accepted persistent holds require explicit neutral drain before next begin.

Crucial drain rule: prior neutralConfirmed evidence is insufficient to complete a NEW drain.
Require the current planner drain to leave Working and finish as Cancelled with neutral evidence.
A fault test caught the earlier neutral-while-Retry bug and verifies the corrected gate. Cancellation
of a drain is not successful drain acknowledgement. No ordinary Runtime work occurs while draining.

The driver repeats no sink/Runtime calls in a loop. One step selects either Planner.step or
Runtime.tick (not both); constant state observations may follow that one action. Report acceptance
makes intent Ackable, but the owned Runtime's NEXT pending-event callback is the acknowledgement
boundary. This serialized boundary, not equality, distinguishes back-to-back equal values.
Equality is used only to reject a mismatched retry of the already-bound intent.

Runtime elapsed expiry is enforced before a pending planner attempt through Runtime's own timeout
path. Planner retries consume its256-attempt action budget; Runtime tick/instruction budgets count
actual Runtime ticks/instructions, not extra report turns. Stuck-clock Delay still hits Runtime's
100000 tick bound. No new execution caps or wall-clock API. Caller times must obey existing uint32
interval assumptions. A blocking caller-supplied report callback cannot be preempted.

Each Bridge requires exclusive use of its report-state stream. Independent bridges have their
own planners but must not pretend separate accepted evidence describes one shared endpoint.
Sharing a report context/state stream, mutation through const_cast, or forged non-null callback
contexts is outside this C++ lifetime/ownership contract; no global endpoint registry is added.
