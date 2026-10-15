# Stage28X clean target links and resources

Linux-hosted clean Arduino3.3.0 / ESP-IDF5.5 target builds. REVIEW ONLY. No deployed
firmware or actual-task/physical heap/latency/stack measurement is represented.

| Measurement | W Route B | X diagnostics off, Route B on | X instrumented |
| --- | ---: | ---: | ---: |
| Compiler program bytes |1,355,051|1,355,087|1,358,083|
| Application BIN bytes |1,355,200|1,355,232|1,358,224|
| Static RAM bytes |106,136|106,136|106,256|
| Free bytes per0x740000 OTA slot |6,246,976|6,246,944|6,243,952|
| Free percent per slot |82.17352505%|82.17310412%|82.13374697%|

Instrumented vs W: program+3,032, BIN+3,024, RAM+120 bytes. Vs matching X diagnostics
off: program+2,996, BIN+2,992, RAM+120. Diagnostics-off small code/layout delta comes
from the X admission wrapper/coordinator composition; no diagnostic state/symbols
remain. Final linked diagnostic State is exactly0x78=120 bytes; existing nested
Adapter/Program/Runtime storage remains counted once within W's23,390-byte subtotal.
W bounded serial state is unchanged. No unbounded report queue or dynamic telemetry
table is added. Static budget remainder221,424B is NOT measured free heap.

Instrumented app SHA-256:
`a0cefdbb8ff9915e58b9142841b4c015dd738406c6861ef5f8e4c3f9105cffc4`

Instrumented ELF SHA-256:
`9dd8a8ed952d1c62cbb7fb16447748cfd0628bf22d96f5aa856404c0df8ec54b`

Diagnostics-off app SHA-256:
`e5b527491f80f798e53bf9711fc103a8605ab05966d39842a201e414629b47fd`

Diagnostics-off ELF SHA-256:
`345e9cc14d59386085b6888fd73361b2974c4e1f1b558a9cfc0b48b7033d0d0f`

Partition table3072 bytes, unchanged:
`b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.
Instrumented image exceeds historical0x140000 slots by47,504 bytes; diagnostics-off
by44,512. No app-only migration or original-slot placement is safe.

Compiler stack frames (not additive worst-case/high-water): loop32, tick304,
beginTurn32, endTurn240, snapshot32, formatter320, HTTP handleDiagnostics1088.
CLI parse frame1216 includes its1024-byte local diagnostics buffer.
Configured loop stack8192 is proven by linked getter, not remaining space. Formatter
can be reached on AsyncTCP/CLI stacks; HTTP1088 +formatter320 is a source-supported
stack concern, not a complete call-chain bound. AsyncTCP default16384 is configured,
not measured. Core/SDK/libc/File/heap scan call chains and interrupts need hardware
high-water evidence; AsyncTCP actual task handle remains unavailable.

The native fail-all C++ allocator test permits2000 owner turns with no new C++
allocation over named lower mocks. It does not cover target SDK malloc internals or
network response construction, which still allocates. Sparse API counts, clock
wrap/rollback/saturation, unknown/zero resources, auth contention, serial pressure,
STOP and unchanged quarantine are tested. No heap scan or printf is under publication.

Full linked-enabled/diagnostics-off receipts retain compiler flags, source identities,
compiled source-copy checks, ELF/BIN/map hashes, linker scripts/response files,
actual archive hashes, frame lists, disassembly and protected startup/HID/NVS checks.
Each resolves183 archives; linked measurement body calls the real heap, stack and
timer APIs, and actual owner tick calls both X hooks. Off has no route_x symbols.
No full-flash merged image, global patch or dependency replacement is generated.
The exact pinned protected core remains81c11f59e01c1e6263d387a008d3f3211319d94feb4751ddfa11af35a2a57ed3;
NVS archive a1ac62b0f8b69ef2ac08e82dd1c57f58d53db74147bc309f070e36a148067a2e;
sdkconfig06fcb22dee7956d54f1c7c05b0856ee87a362380697071fef2c26753fb14c271.
USB/NVS patches and compiler hashes are unchanged from W and independently checked
before/after. This provenance is build evidence, not physical safety certification.
