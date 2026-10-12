# Stage 21 read-only NVS preservation contract

## Answer and decision

**The pinned SDK supports a defensible, tested read-only NVS API boundary. Complete
first-boot NVS immutability is not established.** A correctly loaded read-only partition
descriptor blocks the tested NVS mutation paths at the partition API, including paths
that run before EvilDuck `setup()`. It is a software policy, not flash hardware protection.
The pinned main-flash OS callback adds a second, global read-only region check, so
ordinary main-chip direct writes/erases and writable descriptor aliases are also denied
within that verified boundary. Missing/changed callbacks, mutable canonical metadata,
ROM/custom/raw driver routes and uninspected early paths remain outside the guarantee.

Stage 21 is **investigation/test-only**. Normal and Stage 17 deployment-safe production
sources, partition offsets/sizes/flags and isolated core patches are unchanged. No third
firmware profile or deployment table is enabled or emitted. A transient, explicitly
experimental table is generated only inside an offline test's temporary directory.
Physical migration, application boot and OTA remain NO-GO. Stage 22 has not begun.

## Proposed separately selected quiescent profile

A future reviewed candidate would combine all of these requirements; none may be implied
by the existing safe-start binary alone:

1. An explicitly reviewed table with NVS at `0x9000`, size `0x5000`, and flag bit 1
   (`readonly`, numeric mask 2). All other geometry stays exact. It is a distinct candidate
   table; the approved proposed production CSV currently has **no read-only flag**.
2. A pinned early core policy that **verifies** the expected descriptor, range and
   read-only flag before calling `nvs_flash_init()`. If missing or writable, do not invoke
   the initializer. Preserve a real error and remain unarmed. This paired pre-init
   requirement is not implemented in Stage 21. Build-time table validation alone cannot
   establish which table is physically installed.
3. An explicitly named quiescent profile retaining Stage 16 HID routing and Stage 18
   no-auto-erase policy plus Stage 17's source-level service suppression. No settings
   load/save/reset, payload, application HID initialization, filesystem mount/format,
   MSC backing activation, application web or CLI, or automatic transition.
4. An early-path and bypass audit for that exact ELF, bootloader, SDK configuration and
   dependency identity. No arbitrary writable descriptor, pointer initializer, direct
   flash call or unreviewed early component may target protected NVS.
5. Independently retained owner backups, local structural checks, exact artifact review,
   ROM recovery readiness and separate owner authorization. Neither a successful init
   return nor a clean offline report authorizes boot/migration.

The existing build guards correctly reject the experimental table. They were not weakened
to build a third image. A new isolated candidate wrapper and paired pre-init policy need
their own review and tests. An application check in `setup()` would be too late.

## Supported verification boundary

The native tests execute hash-verified, unmodified ESP-IDF source at commit
`b66b5448e0dfac6be135e6f0ac21010aba231180`: plaintext NVS C initializer/accessors,
partition lookup, manager, handle, `NVSPartition`, Storage, PageManager and Page. They
also execute complete pinned target partition read/read_raw/write/write_raw/erase bodies
against synthetic flash. Exact global region-scan/main-flash callback bodies are also
executed; the lower API adapter invokes those callbacks rather than executing the
complete bus/driver implementation. Linux no-op locks, descriptors, flash/ROM CRC and application
service adapters remain simulated. They do not execute the linked Xtensa library, ESP-IDF
RTOS startup, global constructor execution, bootloader or ROM.

Separate actual archive evidence establishes table flag decoding into descriptor byte
42, the NVS getter's load of that byte, and native partition write/raw/erase guards
returning `ESP_ERR_NOT_ALLOWED` (`0x10d`) before lower calls. Main-flash callback/API/OS
installation evidence is independently inspected in the actual flash archive. Actual target headers
compile with `offsetof(esp_partition_t, readonly) == 42`. This is evidence of the
mechanism, not certification of source/binary equivalence or all transitive callers.

Within these tested boundaries, **all read-only test NVS bytes stay unchanged**; attempted
mutations are rejected before lower synthetic flash write/erase operations. Exact
attempt/error/address records are in `stage21-results.json`. Intentional fixture writes
occur before preservation snapshots. Observed bypass cases deliberately change only
synthetic RAM-backed flash and are not counted as protection passes.

## Initialization, recovery and read semantics

| Situation | Actual tested behavior / limit |
| --- | --- |
| Healthy stored data and cross-page blobs | Real C API initialization/reads succeed; bytes unchanged |
| Empty read-only partition | Initialization can succeed with RAM bookkeeping; no persistent namespace/settings creation |
| FREEING page or no spare page | Read-only manager skips writable recovery/spare requirement; may return success without repair |
| Orphan/mismatched blob cleanup | Partition write is denied; SDK may ignore cleanup failure and still return success |
| Bad header CRC, interrupted entry, invalid states, future version, read errors | Tested failures preserve bytes; original failure propagated, no automatic erase/retry |
| Corrupt string/blob payload read | Cleanup attempts are denied; string accessor returns NOT_ALLOWED; error is not fabricated as success |
| Actual production settings load after corrupt read | Load error latches normal application disabled before services; no settings writes or filesystem/HID activation |
| Read-only handle on writable partition | Does **not** prevent corrupt-read cleanup; real source test changes synthetic bytes and returns NOT_FOUND |
| SDK setter/partition erase/GC attempt | Verified read-only partition boundary denies writes/erase; writable handle opening is denied |
| Repeated failed initialization | Same failure, no lower mutation in the tested case; no retry repairs data |

Success with skipped or failed recovery does not prove logical correctness. The offline
inspector rejects relevant bad states; it remains a subset, not a semantic settings
certificate. The owner reports a clean extended inspection, not independently examined
Codex bytes. It does not establish freshness of the device's current NVS.

## Exclusions and failure policy

There is no complete immutability guarantee for guardless/direct ROM or custom flash
writers, changed OS callbacks/canonical metadata, memory corruption, ROM/bootloader behavior, uninspected SDK
callback callees, concurrency, encryption variants or physical flash faults. There is
also no claim of whole-chip read-only operation: OTA metadata and coredump activity are
separate regions. See `stage21-startup-analysis.md` and `stage21-bypass-analysis.md`.

When a future candidate cannot initialize/read without recovery, stop in bounded
diagnostics. Never clear the flag, repair, retry with writable storage, write defaults,
erase NVS or activate services to hide the error. Keep backups and investigate offline.
Recovery or destructive repair requires separate explicit owner review; no physical
commands are supplied here.

Normal firmware remains writable and functional for healthy settings. Its existing
multi-key saves are not atomic; a prefix or mixed autorun state can persist after a
failure. A future writable transition would require separate authorization, fresh
private preservation evidence, settings/autorun review and a reviewed table/profile
change. It must not occur automatically, via button/payload/web command, or by silently
reusing a read-only first-boot table for normal operation.
