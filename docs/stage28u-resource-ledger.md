# Stage28U measured resource ledger

These are native/relocatable-object measurements, not linked firmware RAM/flash,
OTA capacity, device heap, physical latency or task-stack high-water.

| Object | Native x86-64 bytes | Pinned Xtensa bytes | Ownership |
| --- | ---: | ---: | --- |
| Adapter | 22,608 | 22,528 | Static coordinator member, never task-stack aggregate |
| Program | 6,936 | 6,936 | Nested in Adapter; do not add again |
| CompileSession | 2,416 | 2,408 | Nested in Adapter |
| Runtime | 4,888 | 4,872 | Nested in Adapter; no Planner/Bridge |
| Captured source | 8,193 | 8,193 | Nested in Adapter |
| Publication including four copied requests | 552 | 552 | Singleton |
| FileSource | 56 | 44 | Singleton File handle/cursors; no second source buffer |
| Backend lease / permission | 136 / 24 | 128 / 24 | Fixed singleton records, not per-thread lease storage |
| Scheduler route | 80 | 80 | Fixed singleton |
| Platform gate / publication mutex | 16 / 40 | 8 / 8 | Native mutex versus real target portMUX |
| Stepping / verified flags | 1 / 1 | 1 / 1 | Owner-only singleton flags |
| Status / Scope | 24 / 1 | 24 / 1 | Types; Status already nested in Publication |

Native Adapter grows16B versus T's22,592B (cancellation poll and alignment).
T did not measure a target Adapter, so no target growth claim is made.
`persistentBytes()` reports23,216 native bytes for Publication+Adapter+FileSource
only. Selected target static symbol payloads sum23,374B including lease, route,
gate/mux and flags. This excludes legacy engine/session globals, framework state,
linker alignment, garbage collection and filesystem allocations; it is not final
application RAM. The inherited helper name perThreadStorageBytes is not used to
claim thread-local ownership in U: permission is now one static record.

Actual target compiler frames include coordinator tick304B, requestStart64B,
FileSource open128B/read48B/verify80B, Adapter step at most144B. These are
individual GCC frame estimates, not a total callgraph stack requirement. Full
frames/sections/undefined references are in target-object-results JSON.

Native ordinary C++ allocation probes include fixtures/platform maps, copied
mock File contents, String and vector work: U03 a/a10 calls/437 requested bytes;
U06 exact8,192-byte source18/55,499; U50 thread contention9/309. These are
cumulative requests, not peak/live bytes, malloc/aligned/RTOS coverage or target
Arduino String behavior. ASan/UBSan/leak checks cover completed native cases.

Publication and lease state introduce no dynamic queue/table. File/Ref/String
and the actual filesystem may allocate or block outside publication. Native
allocation observations do not establish target OOM behavior or service latency.
Owner/media snapshot exclusivity, final link RAM/heap/stack peaks and real task
execution remain prerequisites for later integration review.
