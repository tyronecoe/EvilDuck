# Proposed execution ownership, retirement and restart

Design only. No RTOS race test, device cancellation, endpoint takeover, arming or recovery operation occurred. All Stage26 producers/services/profiles remain unchanged. S/E/R meanings stay as in Stage28K; PROPOSED C is transport connection/protocol lifetime and Q is one actual submission attempt.

## Actual contexts and producers

| Context / source | Verified scope | Design consequence |
|---|---|---|
| Arduino `loopTask`, C `cores/esp32/main.cpp:47–105`; R `EvilDuckS3.ino:114–123` | Actual task creation at priority 1 / selected Arduino core, setup then loop; duckscript/com/CLI updates in gated main loop | Proposed opt-in execution owner is this loop task, with persistent Program/CompileSession/Bridge/adapter objects. No new task now |
| R `webserver.cpp:549–585`, `cli.cpp:193–207`; `execution_guard.h:28–50` | Direct com/CLI entry under recursive Guard; serial CLI also reached by loop | Async web library callback task identity is not fully established here. Treat all non-owner entry points as bounded producers, not direct mutable Bridge callers |
| C TinyUSB service task `esp32-hal-tinyusb.c:760–767,846` | `tud_task` servicing in task; source documents callbacks | Ordinary application transfer callbacks are serviced in this task model, not assumed ISR. All exceptional DCD/interrupt routes remain unverified |
| C Arduino USB event loop `USB.cpp:83–150` | Separate queue/task, queue capacity 5, unpinned event task; posts with portMAX_DELAY | Event delivery may lag/block; not an authentic per-submission or immediate-loss boundary |
| R backend and core Keyboard helpers | Raw scheduler, cancellation/update retry, manual press/print/releaseAll all can submit same HID path | Exclusive HID IN lease must prevent **all** these paths during a future preview session, not just web route filtering |
| R `usb_msc.cpp:49–78`; core CDC/MSC | MSC uses zero-time executor TryGuard; classes share USB service/controller | Never make HID callbacks wait on executor/storage locks; shared task/lock fairness still needs stack evidence |

The existing execution Guard can wait indefinitely. It is not sufficient to declare callback serialization safe. Existing short feedback portMUX section (`hid_backend.cpp:31–53`) is a model for fixed copies only, not evidence that the proposed queues already exist.

## Proposed handoff and synchronization

- One execution owner mutates compiler/Program/Runtime/Planner/Bridge and adapter state. Callbacks never call Bridge/Sink/start/drain or log/allocate/mount/wait. They publish fixed observations/sticky flags only.
- Ordinary request capacity **8**, budget **64 bytes per slot**; callback observation capacity **4**, budget **96 bytes per slot**. These are design budgets, not sizeof results. Requests own bounded copied parameters or an owner-managed source handle, never a borrowed HTTP String/payload pointer. Owner keeps Reader/source/context alive until relevant lifetime end.
- Use a short task-context portMUX critical section for ring indexes/slot copies and priority flags, as supported by the verified task/feedback model. 64-bit IDs are not assumed lock-free atomics. Payload publication and slot ownership occur under the same section. No USB call, stack operation or expensive validation inside it. If any future observation is proven ISR-origin, review ISR-safe publication primitives separately before enabling that path; do not call ordinary task APIs by assumption.
- Full ordinary queue: reject visibly **before admission**, return request status; do not overwrite. Cancellation/STOP uses a separate sticky priority flag independent of ordinary saturation. Loss/protocol/reset/overflow uses an independent sticky first-fault flag; cannot disappear behind a full observation queue.
- Full observation queue: latch overflow, invalidate acceptance/epoch, remain terminal/quarantined. A dropped observation cannot serve as retirement. No drop-oldest, fabricated completion or restart. A later real fence may permit resource retirement; not automatic continuation.
- Owner step: consume urgent flags first; at most one observation, one ordinary request and one Bridge step (one report poll or Runtime tick). Never spin waiting for completion. Ordinary requests remain bounded; reject start until setup queue and setup report work are fully resolved (K01). Before mutation, check expected session/request state and report explicit executed/rejected/cancelled disposition.
- No lock nesting between short publication section and executor/USB/filesystem locks. Acquire/copy/release mailbox section, then perform owner work. Never wait for USB completion while holding a lock needed by the USB task, nor block USB task on application work. Source core SendReport's blocking wait is not selected. Raw submit's infinite claim-lock path requires a separately reviewed bounded/try-submission service; CDC/MSC contention cannot be presumed absent merely from HID exclusivity.

Cancellation publication is a pending request, not an immediate Stop acknowledgment. Its application linearizes at the serialized owner boundary: urgent flags present before committing the next Bridge step win; a request arriving during an already committed Runtime tick is applied before the following step and cannot retroactively retract that tick. UI must expose Requested versus Applied, not report Stopped merely on publication. Callback/submission-phase cancellation must be applied before the subsequent Runtime acknowledgement tick, including when completion arrived during a submission call. If current R was already Accepted but E not yet acked, source cancellation still prevents E acknowledgement. No fake rollback after an E was actually acknowledged. Future mock/RTOS tests must exercise ordering, visibility, queue-full and lock-graph cases; this document does not demonstrate their concurrency correctness.

## Identity and actual correlation

C and Q are checked monotonic uint64 IDs, allocated once by a persistent lifetime coordinator; never wrap/reuse. C changes for a new reviewed endpoint/protocol lifetime, not just a mounted flag. Q belongs to one `(C,S,E,R)` submission and immutable buffer. Polling does not allocate a new Q; a definitely-not-submitted attempt may retire and allocate a new Q for the same R. IDs at maximum fail closed before new allocation. Delay has no Q; setup/sync/drain have E=0.

One outstanding transfer is sufficient for six-key snapshot scheduling and existing press/restoration order. It does **not** solve stale correlation alone. Actual existing callback includes instance/buffer/length, not Q/C/endpoint. Associating it with the current slot, FIFO order, pointer identity, equal bytes or callback-time C is unsafe after duplicate/timeout/reset/reuse. Future genuine Q must survive creation→actual completion event; a tokenless callback is unidentifiable until a reviewed source guarantee proves otherwise. No implementation may silently mint Q at dispatch.

The service owns immutable framed bytes through submission and certified retirement; SDK owns its internal copy as separately proven. Callback pointer is borrowed only for callback duration; validate/copy bounded shape before return if safe under exact source contract. Owner consumes copied observation, not a retained SDK pointer. A cancelled/failed Q remains quarantined until retirement certificate. Duplicate Q observations never advance R/E; known stale retired Q may be ignored before any borrowed pointer use. Invalid current metadata faults rather than being reassigned.

Destroying/reconstructing application context requires: stop source/submission producers; disable observer admission; retire outstanding transfers; drain/fence queued callbacks and in-progress observer calls; receive service certificate that old context/buffer cannot be referenced; then reclaim. `USBHID::end`, application queue empty, reconnect or zero snapshot does not prove this. If no certificate exists, retain the bounded quarantined context and deny restart. A persistent context avoids ordinary destruction but still needs endpoint generation fences before slot reuse. Destructor performs no hidden USB work.

## Cancellation/drain/restart state table — PROPOSED, not executed

| Event / state | Immediate action | Resources and restart gate |
|---|---|---|
| Normal EOF / no in-flight Q | Clear logical source owners; TerminalUndrained | Explicit fresh neutral R/Q completion + retirement required; old zero not enough |
| Source STOP / external cancel | Stop source tick/ack, clear intent; cancel pending not-submitted work | Already submitted work may finish; never acknowledge cancelled E; retain Q until retirement |
| Cancel during submission call | Sticky cancel; service resolves ownership and early observation before owner resumes | If submitted/ambiguous, quarantine; if definitely rejected, retire. No repeated press/resubmission |
| Late success after cancellation | Validate genuine old Q; retire only | Preserve first fault/source tombstone, zero new E ack; no automatic restart |
| Send/transfer failure or deadline | Terminal fault, inhibit ordinary actions | No retry of uncertain transfer; drain only after safe retirement |
| Disconnect/reset | Invalidate C immediately at trusted service boundary; signal sticky loss | Reconnect creates no retirement or neutral evidence; old Q/context remains until fence |
| Suspend/protocol change | Stop admissions, invalidate pending acceptance binding | Review lifecycle retirement before fresh epoch; do not reframe in-flight R or auto-resume |
| Explicit drain after old Q retired/fenced | Allocate **fresh** neutral R/Q in a valid bound lifetime, E=0 | Must receive exact current correlated full neutral success **and** retirement. No source command ack from drain |
| Neutral failure/timeout/loss/unidentifiable callback | Remain terminal/undrained, keep evidence | No new session; host release unknown; require separate reviewed recovery boundary |
| Valid fresh drain | Transport-drained at selected boundary only | New owner-authorized S may begin with its own fresh sync after lease/epoch validation; no automatic normal firmware transition |

Even a completed all-zero IN transfer does not prove OS/application key state: earlier devices, OS layout/session handling and host interpretation are outside transport contract. No automatic restart/resume, destructive recovery or physical procedure is provided.
