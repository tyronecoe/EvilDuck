# Stage 24 scanner contract and evidence

Baseline: `9af270f01d455e0bd282a14449ee941751938b1a`.
Pinned ESP-IDF source: `b66b5448e0dfac6be135e6f0ac21010aba231180`.

## Root cause and observable failures

The exact `partition.c` implementation collapses partition-loader errors, iterator
allocation failure and a successfully exhausted/empty initial ANY search into NULL.
The loader builds a temporary list and publishes it only on successful validation.
`esp_partition_next()` exhausts and releases an existing iterator; it has no separately
reported advancement error in the pinned implementation. The public Boolean scanner
cannot recover the original loader or allocator error. It must not claim to do so.

Stage 23's scanner returned true on an initial NULL. The new experimental policy returns
false. This denies every requested range when metadata cannot be established, including
otherwise writable ranges. That conservative availability cost is intentional. No public
partition lookup API or SDK error propagation was changed. The main callback turns the
false permission result into its existing ESP_ERR_NOT_ALLOWED result; it cannot report
an unavailable original allocation/read error.

Before addition, the scanner rejects addresses above UINT32_MAX and lengths exceeding
UINT32_MAX-address. This is a conservative 32-bit endpoint rule, not a flash-capacity
probe. The normal driver retains chip-size/alignment/running-application checks. The
candidate has 16 MiB flash; the conservative endpoint exclusion at the 4 GiB limit has
no effect on its valid partitions. Zero-length requests retain existing semantics:
a readonly start address is denied, an established writable address can be allowed.

NULL descriptors, zero partition size and overflowing partition endpoints deny and
release the iterator. Both Stage 23 matching readonly exits still release. Successful
exhaustion still uses the SDK's existing iterator cleanup. No extra allocations, locks,
recursion or retry are introduced.

## Verified boundary

The real pinned iterator allocation/advancement/get/release bodies run with native
malloc/free, loader and immutable-table adapters. ASan/UBSan/LSan verify 26 new cases,
including NULL/allocator/loader/empty-table denial, malformed geometry, host-width and
endpoint overflow, zero length, overlap, repeated operations and four concurrent
immutable-table threads. Corrected attempts leave no owned iterator retained.

Established readonly NVS denies writes; established writable OTA metadata, alternate
application, SPIFFS and coredump ranges pass the scanner. The standalone counter harness
models lower dispatch and does not execute a complete flash driver. Separate tests execute
selected real NVS C API, Page/Storage/manager/handle and target partition API source with
synthetic flash and the pinned callback/dispatch macro. They record attempted and actual
lower operations and compare bytes. Those tests retain missing/replaced callback and
mutable flag mutation as observations, not protection passes.

41 SDK protection/startup PASS, 10 observations; 36 candidate-gate PASS. The formerly
allowing `region_scan_missing_table` behavior is independently replaced by a denial test
only in Stage 24. Historical Stage 21/23 observations remain intact and were rerun.

## Limits

This does not independently authenticate a table, detect every duplicate/conflict, protect
against metadata races or raw/ROM routes, or install a missing callback. The existing
Stage 22 runtime descriptor/table gate independently rejects duplicates, wrong offsets,
wrong flags, altered table identity, chip mismatch and absent/permissive callbacks before
NVS initialization. Normal exhaustion is accepted only according to the actual SDK
ownership contract; there is no invented iterator-failure status.

The initial no-OS callback-absence interval and subsequent mutable callback/metadata state
remain unresolved. Direct raw-driver and secondary-chip routes are outside this boundary.
The gate's successful one-shot callback query does not guarantee lifetime stability.

## Isolated integration

The new patch is based on verified original target source and includes both iterator
releases, rather than applying an ambiguous overlapping patch chain. The original reference
rebuild matches all 33 allocated runtime sections, normalized relocations and public ABI
of the shipped object. Only scanner text/literals/relocations differ after correction.
The other archive member remains identical. Two fresh rebuild directories produce the
same archive hash. See stage24-sdk-pin.json and both rebuild receipts.

Only the separate Stage 24 experimental builder accepts this archive/tree. The original
Stage 22 and Stage 23 builders reject it. Normal/safe production dependencies retain their
original archive. Final candidate ELF/table/bin/map and USB/NVS/gate provenance are
verified by the new builder and 19 integration cases. No installed dependencies changed.
