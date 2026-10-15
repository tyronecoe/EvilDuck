# Stage28X observational instrumentation contract

`EVILDUCK_ROUTE_B_DIAGNOSTICS` is absent by default. Explicitly defining it requires
`EVILDUCK_PORTABLE_ROUTE_B`; X builder additionally always selects the existing
controlled-start profile. Diagnostics-off comparison still has Route B, W policy
and controlled startup compiled in. Boot binds an owner but never selects Route B.
No USB/CDC/VID/PID/descriptor, core, SDK, numerical grammar or language change.

The exact X patch is applied at fuzz0 only after verified W composition. New runtime
files are fixed record/measurement/formatting bodies. `route_u::tick` owner entry
and RAII exit measure Route B coordinator work, including sparse sampling and any
backend mutex wait, not whole-loop duration or HID completion. Maximum observed
entry interval includes CLI, scheduler and previous work, and is not a real-time
upper bound. It excludes tasks before owner binding and critical startup failures.
Clock is actual esp_timer_get_time signed64 microseconds: negative or backward
observations increment clockErrors, reset interval baseline; widths saturate at
UINT32_MAX microseconds (~71.6 minutes), never wrap to plausible short latency.
Counter increments saturate. Counters are boot-lifetime, not cleared by status,
Start, STOP or script completion. Clock/task values in native tests are injected.

Counters: ticks, maxIntervalUs, maxWorkUs, samples, clockErrors, accepted/refused
Start requests (including invalid/unbound), publication queue peak (capacity4),
effective STOP publications while owned, owner tick observations of coalesced STOP.
Multiple STOP publications can coalesce into one observation. Adapter's within-step
priority poll can react sooner than the next counted tick observation. There is no
claim of a per-request transport latency measurement. Phase/reason are the latest
owner-end copies; firstFault retains the first non-completion/non-cancellation
coordinator reason for this boot. Before first tick they are unobserved defaults.
Backend kind/first kind/sequence and clear request/submitted values are a separate
local snapshot, not an atomic transaction with coordinator status. Existing enum
contracts are coordinator.h and backend_lease.h. Quarantine is copied, never cleared.
Kind Submitted/clearSubmitted means local submission only, never host delivery.

Resources sample immediately on first owner turn, then at most once per1000ms
using unsigned32 modular milliseconds. One call per eligible turn, no catch-up
loop. This timebase assumes fewer than2^32ms between observations; no wrap-based
hard deadline proof. The three heap APIs use MALLOC_CAP_8BIT and report bytes:
free-size sums capable regions; minimum-free sums each region's low watermark,
which can come from different times; largest block is allocatable contiguous size,
not total heap. Zero is valid pressure, not unknown. No API offers an error result;
`heapKnown` means API measurement performed, not healthy memory. Pinned SDK headers
and archive hashes are recorded; no physical values are supplied by this stage.

Loop configured allocation comes from the actual weak linked Arduino getter8192;
current bound owner handle comes from xTaskGetCurrentTaskHandle, never a guessed
name. uxTaskGetStackHighWaterMark is minimum remaining stack since task creation.
The generic task.h text says words; pinned Xtensa portmacro.h defines StackType_t
as uint8_t, so this port's stack units are bytes. Static assertion rejects a changed
unit, multiplication by sizeof(StackType_t) is explicit. Configured allocation is
not remaining stack. Scan happens in the owner, outside publication, at sparse rate.
AsyncTCP handle is private static in AsyncTCP.cpp and has no supported getter in
this pinned package: asyncStackKnown=false always. No task traversal or fake handle.

Publication uses the existing portMUX Critical (native mutex stand-in); only fixed
updates/copies happen inside. Owner-only previous-clock/sample state is not read by
services. Heap scans, formatting, serial/network output, allocation and backend
calls are outside publication, never added to lower USB callbacks. Status uses
1024-byte stack buffer, refuses truncation/error, then normal response copy; CLI
uses same fixed formatter. HTTP GET /routeb/diagnostics requires existing password
authentication and execution TryGuard;401/409/503 are refusals, not measurements.
Local CLI `diagnostics` does not start/select/cancel an engine. No scripts, paths,
SSID, credentials or payload bytes appear in this diagnostic record. General legacy
/status remains its previous API; the new route is the privacy-limited telemetry.

Overhead: two clock queries and several short fixed-copy critical sections every
owner tick; one backend snapshot per tick, three heap queries plus one stack scan
per eligible sample; snprintf/response allocation only on explicit requests.
Compiler frames/static bytes are separately measured, not presumed free. The
instrumented elapsed time includes most of its own cost; final publication/return
and status handling lie outside that work measurement. No physical heap/stack,
AsyncTCP latency, SDK lock worst case or diagnostic overhead has been measured.
