# Stage 22 experimental pre-initialization gate

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING**

Baseline: `516fb642b1126af55db909fcff856943935b7111`. Normal production and
production deployment-safe source, flags, partition metadata and dependency patches
are unchanged. The additive candidate has no arming or writable transition.

## Contract

In the tested candidate `initArduino()` path, the SDK initializer is called only after
`evilduck_nvs_preinit_gate()` returns ESP_OK. Descriptor absence, writable NVS, wrong
geometry/type/subtype/main chip, inconsistent canonical identity, duplicate/extra
partitions, missing callback or table mismatch prevent that call. Original flash-read
errors propagate; configuration rejection returns ESP_ERR_INVALID_STATE with a reason.
SDK initialization errors propagate unchanged. No erase, repair, fallback, default
writes or automatic retry exists. A second call is rejected even after first-call
failure or success. Production setup's existing NVS latch and safe-start return then
suppress settings, application HID, filesystems, storage, web/CLI and payload services.

The gate does not establish authenticity, hardware write protection, logical NVS
health, or complete early-boot immutability. Mutable loaded descriptors and callback
state can change after it returns. Malicious callbacks can return a fabricated denial.
ROM, custom/raw writers, concurrency and earlier SDK paths remain outside the guarantee.

## Exact checks and order

1. Require a default main-chip pointer. Read and compare the exact 3072-byte pinned
   experimental binary table at 0x8000, including official MD5 and padding, in 32-byte
   chunks. No NVS data is read by this check. It does not compare the unused last 1024
   bytes of the partition-table sector. Read failure returns the original error.
2. Enumerate the complete loaded canonical list. Exactly six entries must match the
   reviewed names/types/subtypes/offsets/sizes, 4096-byte erase geometry, default-chip
   identity, no encryption, and only NVS readonly. Order is irrelevant; duplicates,
   extras, truncation and null descriptors fail. The loop has a seven-entry ceiling.
3. Require `esp_partition_verify(p) == p` for each entry. The actual pinned implementation
   does **not** compare readonly despite its broad header wording. Explicit flag/field
   checks are therefore essential. Pointer equality checks canonical list identity,
   not cryptographic provenance or immutable flash-backed RAM.
4. Check the main chip's installed OS hook and its `region_protected` callback. Invoke
   that callback **only as a policy query**, once, for 0x9000/0x5000; require NOT_ALLOWED.
   No write/erase operation is used as a probe. These exposed `esp_flash_t` fields are
   explicitly described by ESP-IDF as advanced, non-stable API. This experiment pins
   their source/config/archive identity and ABI through actual compilation; it is not
   a portable supported-API guarantee. A missing/permissive callback fails closed.
5. Call actual `nvs_flash_init()` only on success. Preserve its result and existing
   Stage18 no-auto-erase policy. SDK recovery may attempt mutations, denied within
   the previously tested readonly boundary; successful initialization can still skip
   repair or ignore a cleanup failure. Success is not a settings-health certificate.

Reasons exposed by `evilduck_nvs_gate_failure()`: 1 repeat, 2 missing main chip,
3 raw table mismatch/read error, 4 missing/incomplete iteration, 5 descriptor fields,
6 duplicate/extra/null entry, 7 canonical verification, 8 callback policy. The SDK
iterator API cannot distinguish OOM, absent table and loader error; these fail closed
without claiming a fabricated precise loader error. Error logging may be compiled out
at the configured core debug level; the retained reason/status hooks remain linked.
Application diagnostics use existing debug support; unavailable transport cannot be
claimed to show the owner an error. Repeated loop execution yields and stays unarmed.

## Memory and ownership

Gate-owned working storage is a 32-byte stack buffer, counters and pointers. The
3072-byte expected table and six-row geometry are constants. No gate malloc, whole-NVS
buffer, AST, RTOS wait or unbounded retry is introduced. SDK partition loading and
iteration allocate; canonical objects persist normally. Gate iterators are explicitly
released on every early rejection, or consumed by next() exhaustion. verify() owns and
releases its own iterator in the pinned source.

The pinned global readonly scan returns false before releasing its matching iterator.
Calling the installed policy query therefore inherits a potential **one-iterator
retention per candidate first attempt**. The one-shot latch prevents repeated gate
queries; this is not a fix for arbitrary later SDK scans. Native gate ownership tests
use iterator adapters and do not measure the target allocation/leak. Normal writable
profiles are not changed. A separately reviewed upstream scanner cleanup is a priority.

## Table binding and profile separation

`experimental/stage22/partitions.csv` changes only NVS flag mask 2. Production
`EvilDuckS3/partitions.csv` remains byte-identical and writable. `expected_table.h` is
independently checked against pinned gen_esp32part serialization. The wrapper snapshots
unchanged application sources outside the repository and substitutes only the separate
CSV. Stage16/18 patches are applied first; the candidate patch/header pair is applied
only to that disposable core. New source/tree/table hashes are pinned. Reverting the
extra patch in a disposable verification copy must reproduce every existing dependency
pin. Original global files are never patched.

Final verification checks source identity, safe-start compiler flags, exact table,
ESP32-S3/16MiB image headers, slot fit, real gate and conditional branch before the
initializer, USB routing/companion symbols, retained candidate identifier, and byte
identity of the application regenerated from ELF. It is mandatory in the wrapper.
Production builders reject the candidate core/table; candidate checks reject production
inputs. Review inventory hash/size/profile/geometry faults are rejected. Review artifacts
are labeled, contain no owner data, and are **not** a migration plan. Arduino-generated
padded merged output is removed from the candidate output; no physical commands exist.

## Evidence limits

Host probes compile the exact candidate gate/core startup and actual application
setup/loop with the pinned plaintext SDK NVS C API/manager/Storage/Page components.
Descriptor iteration/canonical lookup, bus operations, diagnostics and services are
adapters. They do not execute Xtensa SDK binaries, ROM, RTOS tasks, encrypted NVS, full
constructors or physical USB. Linked-ELF inspection is independent native evidence,
not execution of the final device startup. All owner backups remain private and absent.

Flash reads and iterator locking use ordinary SDK synchronization. Their target
lock/driver latency, concurrency or deadlock behavior is not tested by Linux no-op
locks or the sequential descriptor adapters. Bounded read/iteration counts are not a
claim of a hard physical-time bound. There is no new gate RTOS wait/retry loop.
