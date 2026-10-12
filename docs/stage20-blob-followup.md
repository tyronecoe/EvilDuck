# Stage 20 follow-up: owner evidence and bounded blob relationships

This follow-up starts from Stage 20 commit
`1896d62524614ab50419c32365b3577c076c1dae`. It changes only offline inspection,
synthetic tests and documentation. Firmware, SDK patches, installed core, partitions,
USB identities, migration artifacts and application behavior remain unchanged.
Physical migration remains **NO-GO**. Stage 21 has not begun.

## Owner evidence

The owner reports successfully running complete Stage 19 `deployment_preflight.py`
on the three original local files on macOS High Sierra 10.13.6:

| Reported result | Value |
| --- | --- |
| Owner files verified | true |
| SPIFFS roundtrip verified | true |
| NVS classification | insufficient-evidence |
| Blob data relationship findings | 5 |
| Blob index relationship findings | 5 |
| Finding pages | 0 and 1 |
| Invalid/recovery findings | None reported |
| Migration authorized | false |

These are owner-reported results, preserved in
[stage20-owner-preflight-evidence.json](stage20-owner-preflight-evidence.json).
No original binaries or private report were supplied here. Individual entry locations
and per-page counts were not supplied. Five data findings and five index findings do
not establish five valid pairs. **The extended inspector has not run on the owner's
bytes here or in any newly reported owner run. Their NVS remains unresolved.**
Historical Stage 19 evidence and earlier test results have not been rewritten.

## Independently checked format rules

Source reference: ESP-IDF commit
`b66b5448e0dfac6be135e6f0ac21010aba231180`. Complete source pins are in
[stage19-sdk-source-pin.json](stage19-sdk-source-pin.json); the relevant subset is
[stage20-blob-reference.json](stage20-blob-reference.json). Each new test runner checks
the pinned source files before and after SDK source execution where applicable.
The official generator package 0.1.9 and source checksums remain pinned by
[stage19-generator-pin.json](stage19-generator-pin.json).

The verified rules used by `tools/nvs_blob.py` are:

- A `BLOB_IDX` record (`0x48`) occupies one entry, has header chunk index `0xff`,
  and stores a little-endian 32-bit total size, 8-bit chunk count, 8-bit generation
  start and 16-bit reserved field. Offsets within the entry are 24, 28, 29 and 30.
- `BLOB_DATA` (`0x42`) stores a 16-bit length and reserved field, then a 32-bit
  payload CRC. Its span is exactly `1 + ceil(length / 32)` and stays inside its page.
  The previous inspector's span, bitmap, header CRC and payload CRC checks remain.
- Namespace index and NUL-terminated key identify a logical blob across all five
  pages. Physical adjacency or page order is not a relationship requirement.
- There must be exactly one live index and exactly one live child for each chunk
  number in `[start, start + count)`. Matching total count/length alone is insufficient:
  chunks 0 and 2 cannot satisfy an index expecting chunks 0 and 1.
- Generation start is 0 or `0x80`. The first family permits indices 0 through 127;
  the second permits 128 through 254. `0xff` is the wildcard, not a data chunk.
  Actual source comparisons establish these bounds; an upstream explanatory comment
  is narrower than its first-family comparison. No arithmetic wrap is accepted.
- Child lengths sum exactly to the index total. The source header consistency
  ceiling is `127 * 125 * 32 = 508,000` bytes. Actual five-page entry/span/free-page
  checks impose a much smaller capacity. The ceiling is not a capacity promise.
- The verified writer/generator emits an empty blob as one zero-length child and
  a count-one, size-zero index. A count-zero index or multiple/extra empty chunks
  are conservatively unsupported; uncertain behavior is not guessed.
- Verified writer metadata has reserved fields `0xffff`. Unknown encodings remain
  unsupported rather than accepted.
- Orphans, missing/extra/duplicate children, multiple live indices, simultaneous
  generations and legacy/index coexistence require review. No winner is selected.
- An index sharing its namespace/key with a live ordinary scalar/string is also
  rejected. The pinned SDK's duplicate identity includes namespace, key and chunk,
  **not datatype**; a same-page conflict can remove the index and orphan its children.

Relevant source paths include `Item::checkHeaderConsistency`,
`Storage::writeMultiPageBlob`, `populateBlobIndices`, `eraseMismatchedBlobIndexes`,
`eraseOrphanDataBlobs`, `readMultiPageBlob`, `Page::load` and the item hash list.
The inspector now includes chunk number in duplicate identity and excludes datatype,
fixing its prior false duplicate finding for healthy multipage blobs.

The actual linked Xtensa NVS archive's identity and mutation-path evidence remain
recorded by Stage 19/20. These native tests execute hash-verified **source components**
with synthetic adapters, not that Xtensa archive or complete `nvs_flash_init()`.
No source/binary equivalence or physical flash behavior is inferred.

## Bounds, privacy and diagnostics

The input remains exactly `0x5000` bytes at full-backup offset `0x9000`. Oversized
input is rejected before copying it. There are five pages of at most 126 entries;
relationship metadata and grouping stay bounded by that inventory. Generation ranges
have at most 128 elements. Missing chunks produce one generic finding per index,
not an expanded finding for every missing number. No recursive graph, SDK initialization,
repair, owner flash write, whole-blob assembly or source-image modification occurs.

Keys are used privately in memory for grouping; payload bytes are used only for existing
CRC/format checks. JSON emits generic codes, classifications and page/entry locations,
not namespace names, keys or values. The private report's existing region hash stays
private; `deployment_summary.py` excludes it and other non-whitelisted fields. New code
names are whitelisted; historical `*_relationships_unverified` names remain understood
so earlier owner summaries can still be projected without relabeling.

`blob_relationships_checked=true` means the bounded check ran, not that it passed.
Every pre-existing error remains in the final classification. The strongest healthy
result is `compatible-within-verified-checks`; it still leaves
`sdk_immutability_verified=false`, `settings_values_validated=false` and
`migration_authorized=false`. Corrupt reads, GC, later saves and other SDK operations
can still mutate writable NVS. Structural compatibility does not prove logical settings
validity, historical preservation or startup immutability.

## Executed verification

All Stage 1–20 baseline suites were rerun, including Stage 2.5 plan/partition tests,
Stage 9 observations, historical USB diagnostics and both linked profile guards.
Exact names, assertions and outcomes are in
[stage20-blob-followup-results.json](stage20-blob-followup-results.json).

| Group | PASS | Unexpected FAIL | Assertions |
| --- | ---: | ---: | ---: |
| Existing Stage 1–20 contract suites | 1,105 | 0 | 636,353 including separate observations/diagnostics |
| New independent blob-format/generator/privacy tests | 53 | 0 | 279 |
| New SDK component/read-only inspection tests | 12 | 0 | 326 |
| Combined current suites | **1,170** | **0** | **636,958** |

Historical classifications remain separate: five language XPASS, upstream USB
39 historical PASS / six expected XFAIL / seven observations, Stage 9 79 matched
observations / zero mismatches. Existing Stage 16/17/18/20 risk observations are retained.
Raw PASS rows including the 39 historical routing passes total 1,209.

New tests cover both generation families and exact limits, cross-page and reversed
physical placement, empty blobs, multiple keys/namespaces, CRC/span/bitmap errors,
missing/extra/duplicate chunks, sequence gaps with matching count/sum, conflicting values,
size/range limits, reserved encodings, privacy and owner-evidence boundaries.
Pinned official-generator vectors of 0, 1, 32, 33, 3,904, 3,968, 4,000, 8,000 and
12,000 bytes pass. This fixes actual false duplicate classifications in larger generated
images, without changing the SDK.

Actual source-component tests write synthetic blobs of 0, 33, 4,000 and 8,000 bytes,
and replace 33/4,000-byte blobs to verify generation `0x80`. Each successful fixture
passes native readback, repeated initialization and Python inspection. Intentional
fixture-generation writes/erases have exact instrumented ranges inside `0x9000..0xdfff`;
healthy subsequent initialization/read/reinitialization produces no writes or erases
in **these six cases only**. All images are disposable, external synthetic fixtures.
This does not contradict the established corrupt/recovery mutation paths.

Current C++ suites, including the new SDK-source tests, pass ASan/UBSan. Historical
unpatched HID fault diagnostics retain their expected sanitizer-failure classification.
Python tests are not sanitizer targets. A runner command initially referenced a
nonexistent Stage 16 filename; it was corrected to `build_validation.py`, whose 15
tests then passed. No failed test outcome was relabeled.

One existing Stage 19 test intentionally changes from `nvs_blob_index_unproved` to
`nvs_blob_index_invalid_size`: its unchanged malformed index encodes total size
`0xffffff01`, above the now-verified limit. It now asserts the specific invalid-size
finding instead of the old blanket insufficient-evidence placeholder. Historical
reports retain the original test name/outcome. No XPASS/XFAIL expectation was changed.

## Firmware and deployment boundary

No production source or dependency changes occurred, so no new firmware compilation
was necessary for this follow-up. The clean Stage 20 normal/safe builds are unchanged;
source hashes, isolated-core pins, complete ELF provenance, binary identity and partition
guards were rechecked by the rerun integration suites.

| Measurement | Normal | Deployment-safe |
| --- | ---: | ---: |
| Compiler program bytes | 1,329,491 | 1,065,987 |
| Application binary bytes | 1,329,632 | 1,066,128 |
| Static RAM bytes | 82,248 | 78,280 |
| Free per `0x740000` OTA slot | 6,272,544 / 82.509850% | 6,536,048 / 85.976015% |

Application SHA-256 hashes remain:

- Normal: `ccd557a3d579ae85d593de6a756f3cf6c3a0b65f16f8988ae543a9f38b68e874`
- Safe: `155c27a40539497592372e404f7c2fda0eb8a8291e79786f2cbb3e03b1a23744`

There is zero firmware/RAM/embedded-stack growth from this offline extension. Core 3.3.0,
isolated Stage 16/18 patches, 16 MiB custom layout, PSRAM-disabled and USB-OTG/CDC pins
remain intact. No hardware, owner backup bytes, real HID, payloads, formatting, erase,
flash write, OTA or migration operation was used.

## Next owner-controlled step

Use the updated Stage 20 checkout and new private output paths to rerun the **file-only**
commands in [stage20-owner-inspection.md](stage20-owner-inspection.md). That document
contains the complete High Sierra procedure and privacy-safe summary command. It needs
no serial port, esptool, firmware compiler or upload of private backups.

Interpret generic findings conservatively. A compatible result only closes this
documented structural subset; any unsupported/invalid/recovery/insufficient finding
requires review. Do not edit the report to make it pass. The SDK preservation-policy,
recovery, exact artifact-plan and separate authorization gates remain open even after
a healthy local result. **GO** for private read-only inspection and sharing its safe
summary; **NO-GO** for physical migration/application boot/OTA. Stop for review.

## Files in this follow-up

- `tools/nvs_blob.py`, `tools/nvs_inspect.py`, `tools/deployment_summary.py`
- `tests/stage20/blob_tests.py`, `tests/stage20/blob_sdk.cpp`, `tests/stage20/blob_sdk_tests.py`
- `tests/stage19/offline_tests.py`
- `docs/stage20-owner-preflight-evidence.json`, `docs/stage20-owner-inspection.md`
- `docs/stage20-readiness.md`, `docs/stage20-report.md`, `docs/stage20-blob-followup.md`
- `docs/stage20-blob-followup-results.json`, `docs/stage20-blob-reference.json`
- `tests/stage20/README.md`
