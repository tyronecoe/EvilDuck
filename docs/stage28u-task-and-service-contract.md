# Stage28U portable task and service contract

`task_platform.h` uses actual `TaskHandle_t`, `xTaskGetCurrentTaskHandle`,
`portMUX_TYPE` and task critical-section APIs on target. Only native platform
primitives substitute a simulated task handle, thread-local identity and mutex.
No target lease uses std::thread or thread-local permission. Native forced
identities/interleavings are not FreeRTOS execution, affinity or latency proof.

The existing loop's scratch-only call to `bindOwner()` registers its task; it
does not arm or start anything. Owner identity cannot be reassigned. Only that
task opens/closes files, captures/verifies source, steps compiler/Runtime,
acquires/drives/clears the backend and publishes progress. Foreign update calls
return without progressing it. The static Adapter and FileSource outlive all
Reader/Program/session references, including quarantine.

Publishers copy a maximum95-byte path into a four-entry fixed request queue.
Mode is explicitly RouteB, never inferred from source or boot. Accepted Start
reserves engine/service ownership before capture, including time spent Queued.
The request IDs are monotonic64-bit values copied under the publication lock,
not assumed lock-free atomics or secret capabilities. Exhaustion rejects.
The queue also accepts bounded status-poll notifications; they consume one owner
turn and do not invoke borrowed callbacks or change source semantics.
The ordinary owner update drains these even while idle, without implicitly
starting an engine. Requested/active/preparing MSC also rejects Start and
conflicting service admission; it cannot be hidden by an empty token registry.

STOP and loss use separate latched flags, regardless of queue saturation. USB
event callbacks only latch observations; they never run an engine or wait on
execution/filesystem mutexes. These publication APIs require task context, not
ISR context. The pinned Arduino USB event route uses event dispatch; actual
callback scheduling and physical event behavior remain unexecuted.

Each owner turn consumes at most one ordinary request and one bounded engine
step. File capture/verification makes at most one32-byte read per turn. The
compiler and Runtime retain their original bounded step/tick budgets. A poll
queued before Start cannot reuse a previous Adapter terminal state (U52).

After scheduler work, the Adapter polls priority flags before the next Runtime
tick. STOP arriving inside a committed scheduler step therefore prevents the
next source tick; it cannot undo already accepted work or host-visible output.
Loss is converted by the owner into the real backend's retained loss/quarantine
observation, before cleanup can submit another report. No callback recursively
steps the coordinator. First reason/diagnostic survive later successful clear.

Lock order: execution try/recursive guard, then short publication critical
section. No path takes execution/filesystem locks while holding publication.
Critical sections copy fixed data, flags and IDs only: no File access, String
growth, compiler step, USB call, logging or deliberate wait. Public conflicting
backend/com mutation checks run before their potentially blocking execution
guard. U50 checks this with a held host mutex; U55 checks zero-wait service
admission. Internal privileged APIs are not a security sandbox.

`begin(Service,Token&)` reserves a service transaction before side effects.
`enterChunk(token)` reserves its one in-flight chunk; a second chunk rejects.
Actual work occurs outside publication. `end(token)` during a chunk closes
admission and defers release; `leaveChunk(token)` retires the last in-flight
operation. A lost callback retains a bounded reservation, never forces reuse.
`valid(token)` is informational, not permission to perform a later unguarded
write. Completion/abort must retain their copied token, not a borrowed HTTP
pointer. Stale completion cannot release a newer transaction. U54 exercises
deferred abort with a second simulated task.

Task-only publication sections are short in source, not hard real-time latency
proof. File/VFS operations may block despite bounded byte counts. Existing
execution Guard uses a recursive RTOS mutex with portMAX_DELAY; lower/core and
service calls retain their own waits. Target object compilation cannot measure
these waits, task stack high-water or callback concurrency.
