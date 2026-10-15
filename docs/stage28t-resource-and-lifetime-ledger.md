# Stage28T native resource and lifetime ledger

Measurements are Linux x86-64 g++14.2 native objects/symbols, not Xtensa firmware
RAM/stack, production headroom, USB latency or device heap measurements.

| Object | Native bytes | Ownership / placement |
| --- | ---: | --- |
| Adapter | 22,592 | Persistent static fixture; unchanged size from S |
| Program | 6,936 | Inside Adapter, do not add again |
| CompileSession | 2,416 | Inside Adapter, do not add again |
| Runtime | 4,888 | Inside Adapter; no Planner or Bridge used |
| Source capture | 8,193 | Inside Adapter; 8,192 cap plus terminator |
| Scheduler RouteOwner | 80 | Source-local fixed storage; S was72 (+8 for backend operation) |
| Backend lease | 136 | Source-local fixed storage, includes last/first observations |
| Permission | 24 | Per participating native thread, thread-local |
| Observation / Status | 32 / 112 | Type sizes; not extra permanent objects to add to lease |
| Scope | 1 | Entered flag; no heap or retained stack tree |

Adapter's aggregate members, other counters/alignment sum to22,592; the table
must not be summed across nested rows. Runtime owns bounded continuations/calls.
Source and Reader context remain stable during capture, then owned source remains
stable through compilation/run. Program is not replaced while Runtime uses it.
Quarantined Adapter/lease must outlive unresolved operations; the native fixture
keeps static lifetime and offers no force-detach. No new report queue/task exists.

Native `operator new/new[]` accounting includes platform mocks, std::string,
vectors/maps, fixture source copies and thread support, not just adapter code.
T01 a/a:9 calls/309 requested bytes; T03 ASCII sweep:31/11,119; T34 foreign thread:
8/197. Full per-case values are in the trace receipt. These are cumulative ordinary
C++ allocation requests, not peak live bytes, malloc/calloc/realloc/aligned APIs,
Arduino String allocation, RTOS allocation or production heap. No zero-heap claim.
Lease/permission records have fixed size; source-level scope transitions add no
dynamic queue. No task-stack high-water or target frame estimate was measured.

The lower journal has capacity4,096 and an explicit one-attempt overflow snapshot;
T45 checks that exhaustion returns false and triggers real backend quarantine,
not dropped hidden retries. Journal, fixture vectors and mock services are test
overhead, not a proposed production report buffer.

Future placement: one persistent Adapter/source/Program/CompileSession/Runtime,
one scheduler route and one backend lease. Do not place the22K aggregate on the
loop-task stack or duplicate it inside a Bridge. A target review must measure
actual ABI sizes, String copy/diagnostic peaks, bounded read chunk stack, real
mutex waits/task ownership and cancellation on the selected scheduler. No target,
SDK, ELF/BIN, firmware flash/RAM or OTA measurements were authorized this stage.
