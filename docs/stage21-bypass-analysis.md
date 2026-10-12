# Stage 21 SDK mutation and bypass inventory

| Route | Read-only policy | Evidence / conclusion |
| --- | --- | --- |
| `esp_partition_write`, `write_raw`, `erase_range` on canonical read-only descriptor | Return NOT_ALLOWED before lower flash access | Exact source bodies executed with recorded addresses; actual native guard loads byte42 and returns0x10d |
| NVS init/Page/Storage cleanup via `NVSPartition` | Goes through partition API; PageManager skips selected recovery for readonly | Real plaintext C API + actual partition/lookup/manager source executed; every tested protected byte unchanged |
| `NVS_READONLY` handle on writable partition | Only denies handle writes; SDK reads/init still recover | Actual C API corrupt-string read mutates bitmap and returns NOT_FOUND; OBSERVED, not protection PASS |
| Corrupted-string/blob read on read-only partition | Cleanup denied at partition boundary | Actual source C accessors fail, no lower writes; production settings failure latch tested with same real API |
| GC/state changes on read-only backing | State write denied | Actual PageManager GC request with one spare page attempts a transition and returns NOT_ALLOWED; no lower mutation |
| Direct main-chip `esp_flash_write` or `esp_flash_erase_region` | Main OS callback consults the global canonical readonly region list | Exact region-check source plus target flash-archive evidence; callback-aware adapter rejects both before synthetic mutation; full physical driver not executed |
| Copy/forge `esp_partition_t` with `readonly=false` | Upper API trusts supplied descriptor, but main OS guard checks canonical table | Upper gate can be bypassed; global region callback rejects alias before synthetic mutation |
| `nvs_flash_init_partition_ptr()` with writable alias | Accepts caller descriptor; main-chip global readonly guard remains | Actual C API can open writable handle, but its setter fails NOT_ALLOWED at main region boundary; bytes preserved |
| `nvs_flash_init_partition_ptr()` with readonly descriptor | Correctly preserves property for this path | Actual API refuses writable namespace open and preserves test bytes |
| `esp_partition_register_external()` | Source sets new descriptor readonly=false; default-chip overlap check exists | Source inspected only; do not claim overlap registration automatically succeeds. Alternate chip aliases/raw paths not executed |
| Custom `nvs::Partition` / `NVSPartitionManager::init_custom()` | Can supply a different backend | Canonical main-chip region guard still applies if that backend uses normal guarded main APIs; guardless/custom routes remain outside the verified boundary |
| Missing/changed chip OS region callback | Normal API protection depends on callback presence | Callback-disabled synthetic cases mutate bytes; source has a secondary-chip null callback and startup transitions, but actual default-chip bypass was not demonstrated |
| Canonical descriptor readonly flag changed in RAM | Global scan reads current table metadata | Deliberately changed synthetic metadata admits a write; not an observed spontaneous SDK flag change or hardware fault |
| Dangerous-write exemption / no_protect | Dangerous-region exemption occurs after readonly scan | Exact callback test with no_protect=true still returns NOT_ALLOWED for NVS |
| Missing/failed partition iteration | Region scan returns writable when iterator is null | Exact source scanner result observed with missing-table iterator adapter; not proof that complete lower driver permits a write, since other checks may fail/abort |
| Encryption-specific/bootloader/ROM/raw SPI/memory corruption writers | Not certified by these tests | Retained unsupported/unverified paths; no instruction patch or guessed interception installed |

The read-only property is not a hardware/security boundary against arbitrary in-process
writers or changes to the driver/metadata it trusts. The main-flash global guard is
important: an early draft adapter omitted it and permitted alias/direct mutations.
Those permissive-adapter results do **not** demonstrate a default SDK main-driver bypass.
Final tests include the exact scan/callback source and distinguish rejected ordinary
main paths from explicitly callback-disabled or metadata-changed observations.
The pointer initializer's nominal source allocates a Partition without adding it to the
manager-owned partition list. The host fixture explicitly frees that allocation after
deinitialization to avoid a test leak; this is not a production SDK repair or a target
ownership claim. Source/target identity remains distinct.

All mutation/bypass runtime results use synthetic flash and an iterator adapter, not
the actual partition iterator allocation or SPI/RTOS driver. A lower-operation observation
does not prove that a physical chip would accept the same operation. Protection depends
on both descriptor enforcement and, for lower/alias calls, correct main-chip callback
installation and canonical table metadata. That is not a complete whole-boot guarantee.

Read-only initialization may return success while ignoring denied orphan/index cleanup,
or skipping FREEING/no-spare recovery. Those findings are recorded as observations and
must not be relabeled healthy compatibility. No successful return was fabricated. The
owner's zero offline findings are useful preparation evidence, not runtime immutability.

Stage 21 does not install a generic flash interceptor, edit SDK archives, mutate native
descriptors at runtime, clear flags on failure, suppress flash errors, or automatically
repair data. No firmware candidate may rely on a setup-time check to undo earlier writes.

The source region scanner returns early on a protected overlap without an explicit
iterator release. Actual iterator allocation/locking and repeated denied-driver-call
heap behavior were not executed by the iterator adapter; this is a resource/ownership
review item, not a certified target leak or a reason to remove protection. Ordinary
canonical read-only NVS writes are rejected by the upper API before this lower scan.
