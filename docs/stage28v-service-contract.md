# Stage28V service admission and frontend contract

This is a scratch-only, opt-in source candidate from exact Stage28U
`967596476dfe0dde5e824c8f6d1b2ba543502443`. Production files are unchanged.
`EVILDUCK_PORTABLE_ROUTE_B` remains the sole target selector; neither Stage28T
host selector is enabled. No grammar, expression, character set or report-ID change.

A synchronous `route_u::Mutation` first takes the existing execution mutex with
zero wait, then admits under the short publication critical section. It holds
execution admission through the actual body and retires on scope exit. No File,
String, USB, network, log or deliberate wait occurs under publication. Foreign
tasks reject; nested synchronous calls on the admitted task are allowed to depth32.
The33rd guard fails. Start and transaction begin reject while any mutation remains,
including recursive Start from inside a lower File write. STOP does not revoke a
previously admitted operation. Failed/short writes remain failures; no rollback
or atomic multi-key persistence is invented.

A transaction token alone grants no mutation permission. An explicitly entered
chunk records its current task; only that task can mutate/leave the chunk. A
second chunk rejects. End during a chunk closes new admission and defers token
retirement; an already admitted synchronous body and its nested calls may finish.
A stale token cannot retire a newer reservation. A missing completion retains
bounded admission, rather than allowing reuse. Upload/OTA/restart remain disabled;
this generic API is not presented as their implementation.

The module retains the U namespace for the inherited lease/backend ABI. It is
not a second coordinator: include paths select V copies in the fresh scratch
build. Publication grows by task identities/depth only. The singleton Adapter
still owns Program, CompileSession, Runtime and one8,193-byte source buffer.

Explicit selection from an already operational application:

* CLI `routeb <path>` calls the copied,95-byte-bounded request publisher. It
  reports queued/refused without legacy fallback. Ordinary `run` stays legacy.
* HTTP `/run?engine=routeb&s=<path>` authenticates using the existing request
  mechanism, then publishes a copied request and returns202/409. Unknown engine
  returns400. It bypasses library installation and cross-volume resolution.
* `/status` exposes the typed phase/reason in addition to existing diagnostics.
  Contended status/run handlers use nonblocking execution admission, returning409.
* Authenticated POST `/stop` and exact CLI STOP latch cancellation independently
  of ordinary queue capacity. STOP is a request, not proof of host release.
* WebSocket text remains the existing CLI dispatch, with a128-byte enabled-
  candidate frame bound and null-data rejection. Its existing application-level
  authentication/lifecycle is not certified by this work; do not infer that an
  authenticated HTTP test authenticates the WebSocket. This remains an integration
  review item, including whether mutating WebSocket commands should be disabled.

The ordinary operational loop binds its existing Arduino loop task; it never
implicitly selects Route B. The pinned `cores/esp32/main.cpp` creates loopTask
from app_main and repeatedly invokes loop; app startup failures return before
binding. No task creation, owner reassignment or automatic arming is added here.
USB event observation publishes loss; only the owner progresses File capture,
verification, compiler, Runtime, scheduler, clear and quarantine. Native task
identities and std::thread contention are simulations, not FreeRTOS execution.

An open writable SPIFFS stream blocks Start. All inventoried repository writer
entry bodies gain guards before mutation; actual MSC pending/active/requested
state also blocks Start. Capture and byte verification detect observed removal,
size/content or I/O changes before backend admission. They are not a filesystem
snapshot against arbitrary raw SDK/VFS handles or external media replacement.
The strict closure gate therefore remains BLOCKED; no firmware link is attempted.

Called-false ambiguity and loss retain permanent session quarantine, first fault
and ownership. There is no retry/replay or automatic rearm from quarantine. A
subsequent safe session after known cancellation/completion performs fresh local
clearing. LOCAL_SCHEDULER_DONE / LOCAL_CLEARING_SUBMITTED have their existing local
meaning; no USB completion, retirement, host delivery or host release is claimed.
