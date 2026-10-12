# Stage 23 iterator ownership and minimal correction

## Confirmed resource ownership

The pinned scanner's two protected-overlap exits return false without advancing or
releasing the iterator. Nominal official `partition.c` creates a heap object in
iterator_create() with malloc(sizeof iterator), find() advances to a matching entry,
next() releases it on exhaustion, and iterator_release() simply frees it. Early false
returns bypass exhaustion. The iterator owns its allocation, not the canonical partition
nodes, borrowed label, mutex or references to flash. next() releases the list lock
before returning. SDK descriptor lifetime and external-unregistration races are separate.

This is **confirmed source-level ownership loss**, reproduced with real native
malloc/free executing the exact pinned iteration/scanner bodies. It is no longer merely
a suspected retention. Shipped Xtensa disassembly independently shows false returns
without release, find() allocation and release()/free routing. Native DWARF records
**20 bytes** for the target iterator structure; host fixture sizeof is **32 bytes**.
Target heap allocator overhead and actual ESP32 growth were not measured.

For128 repeated denied scans, unpatched native counters show128 allocations,
0 SDK releases,128 retained objects:4096 host payload bytes. Four immutable-table threads
perform512 denials:512 retained objects,16384 payload bytes. Patched cases balance each
allocation with a release, retain0 objects, and keep the same denial. Nonmatching and
exhausted scans release without the fix. An empty table can create then exhaust/release
one iterator; load/OOM failure can create none. Allocation/advancement/get/release counts
for every fixture are in stage23-results.json.

Normal/safe production tables have no readonly flags, so their ordinary exhaustion
path does not exhibit this matching-exit leak. Canonical readonly partition writes
are rejected at the upper API before the lower scanner; direct guarded writes/erases,
writable aliases and Stage22's policy query can reach the leaking lower path. A single
Stage22 gate query previously retained at most one matching iterator; repeated external
queries/denials could accumulate resources. The fix removes that source of retention
in the experimental candidate only. Neither production SDK configuration is replaced.

## Correction

The separately pinned proposal adds `esp_partition_iterator_release(it)` immediately
before each false return. No new allocation, predicate, lock, iteration, repair or flash
operation is introduced. The same iterator is still owned on these exits; exhaustion
remains responsible for its own release. Canonical descriptors are not freed. This
preserves original permission/error behavior, including its existing failure limitations.

The native harness uses the exact iterator type/body definitions and actual allocation,
with wrapper counters and a std::mutex adapter for SDK list locking. The table loader,
flash/ROM and bus remain adapters. Concurrent tests use immutable synthetic metadata;
they do not execute ESP-IDF RTOS, ISR/cache-disabled contexts or dynamic registration
races. Fixture cleanup of retained pointers is separate from SDK releases. A dedicated
unpatched LSan probe deliberately drops fixture references and produces expected exit23
with detected leaks; conservative root scanning can report fewer unreachable allocations
than the128 retained objects independently counted. The corrected probe is leak-clean.

## Independently verified target integration

Only `partition_target.c` is rebuilt. Before accepting its replacement, the unchanged
hash-verified source is rebuilt with pinned GCC14.2/SDK3.3.0-build flags/config/headers.
All **33 allocated runtime sections and their normalized relocations match the shipped
object exactly**, including the original assertion filename after deterministic prefix
mapping. Machine/ABI and public symbols are checked. This establishes runtime equivalence
for this component, not whole-SDK source/binary equivalence or debug-byte identity.

The corrected object changes only scanner text/literal sections and their relocations,
plus the required undefined release symbol and scanner size. All other runtime sections,
ABI symbols and the separate `partition.c.obj` archive member remain identical. Two
independent disposable rebuild directories yield the same archive SHA-256. A third
acceptance rebuild with final guards also matches. Complete SDK source is not rebuilt;
only one verified archive member is replaced in an independently copied experimental SDK.
The SDK tree changes only that archive. Nothing in the installed SDK/core is patched.

The experimental builder retains Stage22 core/table/gate identity, verifies all old
pins plus the separately pinned corrected archive/tree, and requires final ELF/bin/map
verification. The actual final scanner calls the original SDK iterator release. Original
Stage22 builders deliberately reject the corrected SDK; no existing guard is relaxed.
Normal/safe builders keep their original archive. There is no unverified fallback.

Hashes and exact compiler commands are in stage23-sdk-pin.json and the two rebuild
receipts. Source/patch hashes, complete SDK identities and linked artifacts are recorded
independently. No SDK archive or owner binary is committed to the repository.

## Retained risks, not corrected by cleanup

The scanner returns writable when find() yields null, including allocation/table-load
failure. Actual native source with injected allocation failure and otherwise readonly
metadata reproduces an allowing callback decision for the synthetic safe NVS range.
This is a **verified permission-policy risk**, not proof a physical driver wrote flash.
Invalid zero-size metadata behavior is also retained, not certified compatible. Existing
Stage21 callback-disabled and changed-metadata observations remain separate.

Missing/replaced OS callback, later canonical metadata changes, raw/ROM routes and the
no-OS startup interval remain outside protection. The query is a consistency check at
one time, not hardware protection or an allocation-free continuing guarantee. Potential
32-bit endpoint-wrap behavior in scanner/lower range checks was source-inspected but
not established as a physical bypass and is not silently changed. Readonly handles on
writable partitions and SDK ignored cleanup errors remain documented limitations.
