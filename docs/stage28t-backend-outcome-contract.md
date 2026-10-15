# Stage28T actual-backend local outcome contract

The unchanged preview Runtime emits to `native_b::Adapter::receive`; one event
is admitted to scratch `com` with a monotonic local session/operation ID. Sink
Retry polls the same admission, never schedules a duplicate. Actual `com`
performs press, five-millisecond dwell, restoration and Finish. Only the same
immutable admission's actual Done result is consumed as source acceptance.
Delay is owned exclusively by Runtime. The scheduler's default delay and jitter
are suppressed only for this session; prior global values/callbacks are retained.

Scratch `hid_backend.cpp::queueRaw` records the observation around its actual
lower call. `reportError` remains a validation diagnostic, not transport proof.

| Backend observation | Evidence and native policy |
| --- | --- |
| None | No current observation; never acknowledgement |
| NoCall | USB/mount/readiness check refused before `tud_hid_n_report`; bounded local polling permitted |
| Submitted | Lower function called and returned true; only local progress permitted |
| CalledFalse | Lower called and returned false; acceptance is ambiguous, quarantine immediately |
| Loss | Actual backend USB event/mount-loss path, including post-call loss; quarantine |
| Invalid | Current request validation failed without lower submission; fail source, request known local cleanup |
| Exhausted | Observation namespace exhausted; fail closed before another lower call |

The fake lower API knows whether a false return also recorded possible acceptance;
the adapter/backend never receive that distinction. T12–T15 impose the identical
policy on both. Quarantine is retained by the real scratch backend, not a fake
poison flag. Its first observation keeps the original ID, sequence and call flags.
Further scheduler/update/end/cancel paths cannot send through that lease. There
is no quarantine reset, retry-to-success or automatic reconnect/resume API.

Fresh acquisition rejects scheduler ownership/work, persistent Owned keys,
pending clearing/dirty ownership, mount loss, unconsumed disconnect, prior
quarantine and legacy raw-helper software state. Only a known idle/unowned
validation diagnostic may be discarded. A stale loss must be explicitly consumed
through the existing legacy path and local cleanup before a new explicit start.

Cleanup records a floor, requires a newer clear request with a true lower return,
empty local Owned state and no unresolved flags before detach. A zero report does
not clear Arduino Keyboard's separate software ledger: legacy raw-helper use
sets a conservative latch; explicit legacy `releaseAll` clears that software
latch outside a lease, followed by fresh synchronization. No host-release claim.

The lease is fixed storage under the actual host `execution::Guard`, with a
thread-local permission scoped to explicit session AND operation and owning host
thread. A lower-call-in-progress guard rejects callback reentry. Foreign thread,
stale operation, raw helper and lifecycle ingress cannot borrow the current ID.
This is not a production RTOS task-affinity or memory-order proof.

Pending/clearing bounds are each 1,000 turns or 1,000 milliseconds, whichever
first expires. Clearing expiry retains the lease in Quarantined state. First
fault survives later cleanup. Unsigned elapsed subtraction handles the tested
Runtime Delay wrap; arbitrary production clock jumps/USB timing remain untested.
Session/operation/observation counters reject exhaustion without wrap reuse.

Subset and all preview limits are unchanged from
[Stage28S](stage28s-capability-subset.md): ASCII source only, US layout identity,
HID enabled, 95 printable bytes plus TAB/LF and ten fixed named keys. Ownership
IR is rejected even in inactive code. No INJECT_MOD/RESET, Unicode, DE extension,
device commands or new grammar. Preview checked arithmetic still differs from
the legacy engine. Literal dollars remain literal, without legacy interpolation.
