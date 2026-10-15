# Stage28V object and native resources

No firmware was linked. Compiler program usage, actual application BIN size,
final static RAM, OTA headroom, linked map, heap margin and per-task high-water
are **UNAVAILABLE**, not zero or extrapolated from object payloads.

| Object / selected payload | U native | V native | U Xtensa | V Xtensa |
| --- | ---: | ---: | ---: | ---: |
| Adapter, including Program/CompileSession/Runtime/source | 22,608 | 22,608 | 22,528 | 22,528 |
| Publication | 552 | 576 | 552 | 568 |
| FileSource | 56 | 56 | 44 | 44 |
| `persistentBytes()` for these three only | 23,216 | 23,240 | 23,124 | 23,140 |
| Previously selected target static payload sum | — | — | 23,374 | 23,390 |

The16-byte target /24-byte native publication growth is fixed ownership/depth
state. The selected sum includes backend lease128, permission24, route80, gate8,
publication mux8 and two flags. It excludes linker layout, all legacy/application/
framework globals and library allocations. Nested Program6,936, CompileSession2,408,
Runtime4,872 and captured source8,193 bytes must not be added a second time.
No Planner/Bridge is added. A Mutation is synchronous RAII, not a dynamic queue.

Measured individual target frames: requestStart64, enterMutation32,
leaveMutation32, coordinator tick304 (unchanged from U), settings saveChecked64,
SPIFFS streamWrite48, handleRunScript160, handleStatus144, upload refusal64 bytes.
Complete `.su` records are retained in the target receipt. No frame sum is presented
as a callgraph/task stack requirement. Arduino main.cpp uses the pinned existing
loop stack selection; its source identity is recorded, not device high-water.

Native C++ allocation probes include fixtures, network maps/String copies and
memory Files. V01 records13 calls /533 requested bytes; V17 direct settings denial
5/172; V27 thread contention4/146; V52 admitted write/reentrant Start15/719. These
are cumulative C++ new requests after fixture setup, not live/peak heap, malloc,
aligned allocation, RTOS mutex allocation or ESP32 heap behavior. Final completed
native cases pass ASan/UBSan and leak detection. The V probe adds matching nothrow
new/new[] overloads; disabling ASan alloc/dealloc mismatch was not used.

Filesystem and existing execution mutex/lower SDK work may block outside short
publication sections, even with32-byte source reads and nonblocking service
admission. No host or device latency, stack high-water or physical allocation was
measured. There is no installed-core/SDK change.
