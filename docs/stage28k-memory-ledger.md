# Stage28K fixed storage and allocation evidence

Target evidence is **unlinked metadata-only Xtensa objects**, not firmware execution or a linked image. Existing core/SDK/compiler checks passed fresh; all three unchanged preview module object hashes, selected sections and type sizes match Stage28J. A separate `object_layout.cpp` exposes only sizeof values. No global dependency was patched. Host primary tests used Linux x86_64 GCC 14.2; ABI differences are reported, not flattened.

| Item | Capacity | Bytes each, Xtensa / Linux | Fixed storage, Xtensa / Linux |
|---|---:|---:|---:|
| Program | 1 | 6936 / 6936 | 6936 / 6936 |
| CompileSession (includes Compiler) | 1 | 2408 / 2416 | 2408 / 2416 |
| Bridge (includes Runtime + Planner) | 1 | 5020 / 5056 | 5020 / 5056 |
| Existing independent object sum | — | — | **14364 / 14408** |
| Report action Record, intent and accepted snapshots | 256 | 56 / 56 | 14336 / 14336 |
| IntentRecord | 128 | 40 / 40 | 5120 / 5120 |
| Request handoff | 8 | 4 / 4 | 32 / 32 |
| New three arrays | — | — | **19488 / 19488** |
| Other Driver storage + ABI padding | — | — | 180 / 232 |
| All additional storage beyond existing object sum | — | — | **19668 / 19720** |
| Complete synthetic Driver sizeof | 1 | — | **34032 / 34128** |

Other storage includes MemoryReader (12 target / 24 host), callback/context pointers, monotonic counters (24 B), first diagnostic (48 B), clocks, bounded stats/rejection/request state, indexes, flags and padding. It is the residual of actual sizeof, not invented independent estimates. Bridge Runtime 4872 B and Planner 84 B target sizes are already included in Bridge; Compiler 2312 B is already inside CompileSession. Individual Event/Report/diagnostic types are often embedded; do not add them again.

Capacities were chosen before tests, deliberately non-overwriting. Most added bytes are **test evidence**, not an endorsed production memory budget. No proposal to put this 34 KB journal in firmware or to enlarge preview capacities follows from these measurements. The existing contexts, input buffers, File/UI/task/USB allocations, compiler/callback stacks and actual device margin remain UNKNOWN. No heap, task-stack high-water, latency, OTA headroom or runtime device measurement was performed.

Selected unchanged preview object frame estimates remain Runtime tick 112 B, expression 144 B, ownership proposal 96 B, Bridge step 32 B/start 48 B; these are not complete callgraph/task-stack estimates. New wrapper target *code* stack/sections were not compiled or measured: the extra target object is metadata-only. Native tests keep persistent member objects for the case lifetime; the allocation probe uses static Driver storage. Test-local stack use is not a recommended ESP32 placement.

The separate host allocation probe observes **zero C++ `new` calls** during healthy compile/run/journal acceptance/drain. It runs without sanitizers so replacement allocation functions do not interfere with ASan. It does not intercept every libc allocation, every error/exception path or SDK allocation, and does not prove physical heap behavior. Primary tests and the negative-control executable separately ran ASan/UBSan with Linux leak detection enabled. Intentional fault tests include a mocked `bad_alloc` decision; healthy zero-new evidence is not extended to all exception paths.

Exact commands, layout object/header hashes and sizeof receipts: `stage28k-object-layout.json`. Exact compiler/core/SDK pins and preview object/frame identities: `stage28k-target-build.json`. No object was linked into a firmware, upload bundle or installable image.
