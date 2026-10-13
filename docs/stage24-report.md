# Stage 24 report — fail-closed scanner and fresh provisioning

Baseline commit `9af270f01d455e0bd282a14449ee941751938b1a`.
Branch: `stage24-nvs-hardening-fresh-provisioning`.

**The known initial-NULL scanner failure-open path is corrected within the separately
verified experimental boundary. Production dependencies remain unchanged. Physical
migration, application boot and OTA remain NO-GO.**

The owner's recovery-first policy is respected. Exact original firmware/NVS/settings/
scripts/filesystem preservation is not mandatory. Backups remain optional untouched
resources. Stock recovery is owner-provided for later compatibility verification; no
search for stock firmware was performed. No owner files were supplied or inspected.

## Production scope and scanner

All repository changes are additive. Existing EvilDuck production source, Arduino Micro,
normal/safe partition CSV, installed Arduino/SDK, USB identities and historical reports
are unchanged. The separate candidate retains Stage 16 HID routing, Stage 18 no-auto-erase,
Stage 22 pre-init descriptor/table/callback gate and quiescent setup/loop.

The Boolean SDK API cannot distinguish an empty search from allocation/load failure.
Returning false on initial NULL is therefore deliberately conservative for every range.
This closes the demonstrated permission-policy failure; it is not evidence of a physical
write bypass or a new original-error API. Invalid descriptor geometry and 32-bit endpoint
overflow also deny. Both iterator releases remain; exhaustion still uses SDK cleanup.
Known valid writable ranges pass; running-app/driver/alignment rules remain independent.

[Scanner analysis](stage24-scanner-analysis.md) states exact zero-length, boundary,
allocation, callback and metadata limitations. [Patch](../proposals/esp-idf-5.5-stage24-failclosed-scanner.patch)
contains only the scanner changes. No locks, allocations, recursion or retries were added.

The unchanged-source object reproduces all 33 shipped allocated runtime sections,
normalized relevant relocations and public ABI. The changed object differs only in
scanner text/literals/relocations; the other archive member is identical. Independent
fresh builds produce the same archive. Mandatory candidate verification checks exact
SDK/core/patch/source/ELF/bin/table/map identity, linked iterator release, gate ordering,
USB routes and normal/safe/candidate separation. Existing Stage 22/23 builders reject
this new dependency; no production builder guard was relaxed.

| Pin | SHA-256 |
|---|---|
| Original source | 5917caadeb7a4a405c72eecbee939fdd153f50c32d9340699623da172f0f58d6 |
| Corrected source | 6d8e76681b6a60189dcad43676e51e8f8c64fc8dd407a4aa3573452975ba9b29 |
| Patch | 11a6e638bef6c47669b85ac303750e95f387b8ca8fd5a328a90be14ffdea4de2 |
| Original archive | dd56cec7a28fb58246381dafddff33fcd9b46f56c9a863bdb8fb3441288d991d |
| Corrected archive | c0f1b50e79db307b60c6b1b5e71aae1bf468fd46b88b7fd4556e02acb13058e3 |
| Corrected SDK tree | 08ef228bef15e968786fb8301d5db01586eca2b8917699ec9fe3af06aa8a0e5f |

Compiler/source/core and original unchanged SDK identities appear in stage24-sdk-pin.json,
source provenance, both rebuild receipts and the final profile provenance files. This is
one-component ABI/runtime equivalence, not a whole-SDK source rebuild or full Xtensa execution.

## Fresh provisioning and integration

The selected [fresh contract](stage24-fresh-provisioning.md) prepares complete local images
offline, rather than adding an automatic runtime repair/format/provisioning path. It
requires explicit owner credentials, existing typed settings schema, disabled autorun and
no existing destination reuse. Missing/private inputs fail without invented defaults.
Interrupted publication leaves an unapproved incomplete directory; inventory is published
last and verified separately. Existing multi-key saves remain non-atomic.

Fresh SPIFFS is empty, exactly 0x160000 bytes with verified block4096/page256 geometry,
capacity/roundtrip checks and reproducible bytes. No old differently sized image is copied,
truncated or relocated. No owner or bundled scripts are fabricated in the image. Private
fresh NVS images are 0x5000 bytes at the reviewed NVS offset; the official generator and
structural inspector are pinned. No generated credential-bearing binary is committed.

Real selected SDK/core/settings/setup/loop source initializes the generated synthetic NVS
in native tests. Normal services start with autorun false; safe/error profiles suppress
application activity. These are service adapters, not actual Wi-Fi/USB/mount/RTOS behavior.

Source review exposes existing normal risks: absent namespace uses legacy credentials and
empty web password; normal SPIFFS.begin(true) may format on mount failure; an empty library
causes bundled examples to be written; mount failure is not a full application latch. They
remain explicit deployment gates, not silently changed behavior or claimed repairs. The
readonly candidate cannot provision writable settings and has no automatic normal transition.

## Executed verification

| Group | Result | Assertions |
|---|---|---:|
| Stage1–23 rerun | 1388 current PASS, zero unexpected FAIL | 641635 |
| New real iterator/scanner source | 26 PASS; ASan/UBSan/LSan | 688 |
| New corrected SDK protection/startup | 41 PASS, 10 retained observations; ASan/UBSan | 972 |
| New candidate pre-init gate | 36 PASS; ASan/UBSan | 737 |
| Fresh-image/fault/provenance/privacy | 32 PASS | 32 |
| Generated-NVS real source startup | 9 PASS, 1 retained observation; ASan/UBSan | 253 |
| Final dependency/profile/ELF integration | 19 PASS | 19 |
| **Current total** | **1551 PASS, 0 unexpected FAIL** | **644336** |

Exact names/status/stdout and synthetic attempted/lower flash ranges are recorded in
[results](stage24-results.json) and [test index](stage24-test-index.md). Historical language
5 XPASS, USB39 PASS/6 XFAIL/7 observations, Stage9 79 matched observations and all prior
NVS/bypass limitations remain separate. The historical unpatched iterator LSan XFAIL was
rerun and retained; current corrected real allocation tests have no retained objects.

Intermediate harness issues are not hidden: build-dependent checks ran too early and were
rerun after successful builds; the large Stage7 test hit its host20-second timeout under
load and the same executable passed an isolated retry; Stage22 inventory checks required
fresh fixture paths; a SPIFFS marker image was not reproducible across timestamps and was
replaced by the empty image; an initial interruption adapter affected packing before
publication, so its scope was corrected and rerun. Final executed suites have no unexpected
failure. Source/fixture changes were not made to turn historical limitations green.

## Clean builds and resources

Pinned Arduino ESP32 3.3.0 / ESP-IDF5.5 / GCC14.2, ESP32-S3, 16MiB, PSRAM disabled,
QIO80/240MHz, USB-OTG/TinyUSB/CDC; all three fresh isolated clean builds passed.

FQBN: `esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default`.

| Measurement | Normal | Production-safe | Experimental Stage24 |
|---|---:|---:|---:|
| Compiler program B | 1329491 | 1065971 | 1069995 |
| Application BIN B | 1329632 | 1066112 | 1070144 |
| Static RAM B | 82248 | 78280 | 78288 |
| OTA free B per0x740000 slot | 6272544 | 6536064 | 6532032 |
| OTA free % | 82.50985 | 85.97623 | 85.92319 |
| Growth from Stage23 program/BIN/RAM | 0/0/0 | 0/0/0 | 24/32/0 |

Application/core compiler estimates match the freshly analyzed Stage23 inventories after
path normalization: normal457, safe457, candidate460 records, largest per-function1184B.
The corrected SDK scanner estimate is32B, excluding callees/allocator internals. Earlier
report prose used455/458; the recorded JSON inventories actually contain457/460, and this
comparison uses those complete JSON records. No physical heap, stack high-water, latency
or USB behavior was measured. Native allocation probes do not prove device heap behavior.

Application SHA-256:

- Normal: `a36616489a4acb88c491618a2ce4cca78e60591d89795b4acf7bcd7bd2b19d94`
- Safe: `46e02019c2bbf4284e877b218555835a0ae1cbd1d2e18c4cc858153d3f0a5327`
- Experimental: `2b1f4720dd8c9ff33be0b4351c96bdc94c88289c67f5dd69c7baab9ddecb75eb`

Source behavior/resources remain unchanged for production; build/ELF metadata and isolated
path identities can change hashes. Every current ELF/BIN/bootloader/table hash and size is
in stage24-artifact-inventory.json, with linked profile receipts. These are review records,
not a deployment package. Arduino automatically emitted merged side outputs during compilation; the candidate
wrapper removed its output and the normal/safe side outputs were discarded during final
review. None was used, committed or approved as a migration artifact.

Production geometry remains:

```csv
nvs,data,nvs,0x9000,0x5000,
otadata,data,ota,0xE000,0x2000,
app0,app,ota_0,0x10000,0x740000,
app1,app,ota_1,0x750000,0x740000,
spiffs,data,spiffs,0xE90000,0x160000,
coredump,data,coredump,0xFF0000,0x10000,
```

Supported serializer/MD5 roundtrip, types/subtypes/alignment/nonoverlap/table identity,
16MiB ESP32-S3 headers, standard app0 placement and OTA fit were checked. Experimental
NVS readonly mask2 is separate. An application-only upload would not migrate the installed
old table. No installed layout is claimed verified by a generated build.

## Readiness and stop

[Readiness](stage24-readiness.md) retains the no-OS callback absence, mutable metadata/
callback lifetime, ROM/raw/indirect and physical startup uncertainties. The cleanup/null
correction does not protect routes that never invoke it. Legitimate OTADATA E000/2000 and
coredump FF0000/10000 operations must not be mislabeled NVS corruption.

GO: offline software/artifact/fresh-policy/recovery-resource review.
NO-GO: physical migration, application boot and OTA. Owner-provided recovery image/build,
ROM readiness, actual accepted artifacts/approved ranges, credentials, mount/provisioning
policy and explicit authorization remain required. Recommend separately reviewed Stage25
recovery-first compatibility and controlled normal-start contract. Stage25 was not begun.

No hardware/serial/USB access, physical flash/erase/format/OTA, real HID or owner script
execution occurred. No stock discovery, global dependency edits, private owner file commits,
production table/schema/identity changes or previous branch changes are authorized here.
See stage24-files.md for every new file and stage24-reproduction.md for offline commands.
