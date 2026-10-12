# Stage 19 NVS compatibility and recovery analysis

Baseline Stage18 07864bb151ed4b38cc22b02ea1ea9569cc78c78b. Arduino3.3.0,
SDK idf-release_v5.5-b66b5448-v1; unchanged Stage18 whole-tree/HID/NVS pin.
Exact archive SHA256 a1ac62b0f8b69ef2ac08e82dd1c57f58d53db74147bc309f070e36a148067a2e.
SDK source investigation uses immutable official commit
[b66b5448e0dfac6be135e6f0ac21010aba231180](https://github.com/espressif/esp-idf/tree/b66b5448e0dfac6be135e6f0ac21010aba231180/components/nvs_flash).
File hashes are in stage19-sdk-source-pin.json. Source is fetched only into external
host-test directories, not vendored or substituted into the firmware SDK. The nominal
SDK release commit identifies the source reference; bit-for-bit source/binary equivalence
and identical host/target compilation are not certified.

## Evidence levels

1. Exact pinned Xtensa archive inspected with objdump: API init -> partition manager ->
   Storage::init -> PageManager::load; entry-load and readItem reference eraseEntryAndSpan;
   Storage references blob cleanup; backing Partition write/erase call actual ESP partition
   APIs. Page operations also use virtual/indirect calls. Relocations prove references,
   not every dynamic condition or every emitted branch. stage19-sdk-archive-evidence.json
   records tool/archive/function-section hashes and references.
2. Unmodified pinned Page, PageManager, Storage, Item and HashList source compiled/run
   under host ASan/UBSan with synthetic Partition, CRC, logging, heap and BSD interfaces.
   Actual source recovery algorithm runs; mocked flash logs exact absolute ranges.
3. Full protected production firmware linked for both profiles against the **unchanged
   precompiled SDK** and isolated HID+Arduino-NVS patched core. The Xtensa SDK binary is
   not executed in host tests; complete API/locks/ROM/flash/task startup is not emulated.
4. No physical startup or owner NVS data was examined. Owner local hash confirmation
   is a separate provenance class.

## Initialization and mutation paths

| Path | Conditions and actions from source | Verification/limits |
| --- | --- | --- |
| nvs_flash_init | Encryption disabled in pinned config: invokes nvs_flash_init_partition("nvs") | Actual archive references and config checked; full API not host-executed |
| Partition manager | Lock/lookup, allocate Storage, initialize; cleanup failed in-memory objects | Missing partition/memory/flash failures may occur; freeing RAM does not undo flash changes |
| Page::load | Header/sector reads; erased state scans actual page; CRC/state/version checks; active/full/freeing loads entries | Host read/partial-read errors exercised; encryption/ROM not emulated |
| Version | Format version counts down; <0xfe returns NEW_VERSION_FOUND; older >=0xfe accepted by source | Host 0xfd rejection; offline subset conservatively accepts only 0xfe |
| Entry table recovery | Incomplete writes, illegal entry bits, bad header CRC/span/type, incomplete variable spans and duplicates can mark entries erased | Actual source host tests record writes to bitmap word; success does not imply immutability |
| PageManager duplicate cleanup | Earlier matching live record may be erased after interrupted replacement | Source/archive references; duplicates tested within a page; exhaustive cross-page updates untested |
| FREEING recovery | May erase current active destination, activate spare, copy surviving entries, erase old freeing page | Host actual source records both sector erases and intervening writes, including failure after first erase |
| activatePage | A selected corrupt free-list page can be erased | Host corrupt-only partition test records 4096-byte erase |
| No free page | Can return NO_FREE_PAGES after preceding page/entry recovery | Host simple no-free error and separate mutation-before-later-error cases; not every mixed combination |
| Storage::init blobs | Loads namespaces; removes mismatched indexes and orphan blob chunks | Actual source tests demonstrate entry-state writes; some cleanup errors are ignored and initialization still succeeds |
| readItem | String/blob payload CRC failure may erase entry bits during read | Actual source string CRC test: successful init, later read fails and changes bitmap |
| Repeated init | Manager init_custom may reuse Storage and call init again; no general no-op promise | Same PageManager and same Storage clean/repaired source cases tested; full API handle/locking lifetime untested |
| Flash failures | Reads/writes/erases can fail after earlier changes; power interruption can partially alter storage | Host partial reads/failing writes/erases logged; partial physical flash-program effects not modeled |

Source path specifics: nvs_page.cpp::load/mLoadEntryTable/findItem/readItem/erase;
nvs_pagemanager.cpp::load/activatePage; nvs_storage.cpp::init/
eraseMismatchedBlobIndexes/eraseOrphanDataBlobs; nvs_api.cpp::nvs_flash_init;
nvs_partition_manager.cpp::init_custom and nvs_partition.cpp backing operations.
Some recovery cleanup results are ignored in source; this stage does not rewrite them
or label successful return as proven healthy storage.

## Preservation decision

Keep Stage18: Arduino itself never performs its old automatic whole-partition erase or
retry, preserves SDK return, and application startup stops on error. This does not wrap
or restrict SDK flash APIs. Native NVS_READONLY handles prohibit intentional user writes
but do not prove internal recovery is read-only, including reads.

Do not pass a fake read-only partition, skip init, rewrite precompiled instructions,
return fake success, intercept generic flash operations or rebuild an entire SDK from
unverified sources/configuration. A fully source-pinned SDK rebuild plus host/target
provenance and a reviewed recovery contract would be needed for stricter protection.
Only page/header inspection before SDK init cannot independently certify all blob,
namespace, corruption, timing and later-read paths. This stage adds offline conservative
inspection; no new early SDK patch. **Strict preservation remains unresolved; migration
and application boot remain NO-GO.**

## Offline validation subset

nvs_inspect.py reads five 4096-byte plaintext pages at offset9000/size5000. It checks
known state encodings, version0xfe, sequence duplication, header CRC over bytes4..27,
reserved header/bitmap bits, 126 two-bit entry states, 32-byte entries, item CRC excluding
stored CRC, spans and per-page boundaries, supported types, namespace references,
string termination/data CRC and duplicate live records. CRC uses zlib(initial ffffffff),
matching the pinned official generator and ROM-adapter tests. Data/key material remains
only in memory; JSON contains numeric positions/counts/generic codes and region digest.

Classifications: compatible-within-verified-checks; invalid; recovery-potentially-required;
unsupported-format; insufficient-evidence. Ranked invalid, unsupported, recovery,
insufficient when multiple findings exist; full issue list retained. Dirty erased pages,
FREEING, duplicates and missing spare pages flag recovery. New/older versions require
review rather than automatic conversion. Complex BLOB_IDX/BLOB_DATA relationships are
**insufficient evidence**, even if entry/data CRCs are correct. Encrypted or unfamiliar
input is not deciphered or guessed. Erased fresh namespace is valid default state within
checks, not a read-only init certificate. No settings semantic values are emitted or
certified by offline structure alone. Clean classifications never authorize migration.
Checked plans reject unresolved structure; preflight still saves findings for review.

## Settings audit and intentional compatibility change

Original Preferences-based load ignored open/getter failures, allowing failures to become
default settings; normal services/filesystem mount preceded load. New load uses typed raw
read-only APIs, tolerates only genuine NOT_FOUND, captures the first other error, closes
handles, validates stored domains and publishes a complete snapshot only on success.
No set/commit/erase call is added to load. Failed validation disables startup before LED,
HID, MSC, filesystem/example install or web/CLI. A boot-lifetime failure latch prevents
later successful read/repeated setup from arming. Safe profile skips loading entirely.

Boolean bytes must be0/1; channel1..13; SSID1..32; password8..63; RGB<=ffffff;
delay minimum<=maximum; enabled autorun needs a script name. Strings incl NUL <=4000
with no embedded NUL. Missing namespace/keys use RAM defaults, no write-back. Former
silently normalized invalid stored values now fail closed; this is an intentional
compatibility tightening. Public void load/save/reset interfaces retained, ready/loadError
added. Save refuses unvalidated load or failed namespace open. Explicit normal-operation
save/reset still writes settings; no atomic multi-key transaction or full save-error
handling is promised. Preferences logging/put/commit limitations and later Wi-Fi/SDK
writes remain. Settings raw reads can encounter SDK internal mutation; guard prevents
application side effects after reported failure but cannot roll back SDK changes.

Temporary string buffer is bounded to4000 bytes and released per key. Checked allocation
failure disables startup; String snapshots use existing bounded dynamic allocation and
move publication. No new persistent queue/table/parser/SDK binary dependency. Task high
water and heap under actual boot remain unmeasured.
