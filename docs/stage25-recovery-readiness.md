# Stage 25 recovery compatibility and installation review

**PASS:** independently executed offline image/header/hash/table/range checks on compiled
artifacts and explicitly non-executable synthetic format vectors.
**BLOCKED:** actual owner recovery resource not supplied or checked in this workspace;
known-good physical recovery and new application operation not independently established.
**FAIL:** no unresolved demonstrated software failure in the final focused suites.
**Physical installation, application boot and OTA remain unauthorized.**

The owner knows the stock source. No stock lookup/download occurred. Existing backups
remain untouched and optional; exact original firmware/NVS/scripts/filesystem restoration
is not required. Previously owner-reported local full-preflight/hash/ROM results remain
owner evidence, not newly inspected Codex data.

## Required recovery resource

A recovery candidate needs a matching ESP32-S3 bootloader, partition table, deterministic
app0 OTA initializer and application for the selected table (app1 optional). An app-only
file does not establish a complete recovery set. A reproducible source build needs exact
board/core/libraries/flash/USB/PSRAM configuration and artifact identities. A known-good
owner stock image/build is acceptable; the new software-tested build is not automatically
known-good physical recovery firmware.

The offline checker requires:

- ESP32-S3 chip ID9, supported standard IRAM entry, valid segment boundaries/XOR checksum
  and appended digest where present; trusted external SHA256 and exact size for every file.
- Reviewed quad-compatible QIO/QOUT/DIO/DOUT mode and 40/80MHz image frequency. Pinned
  Arduino QIO80 firmware emits DIO80 header fields; this is not an octal flash proposal.
- Revision bounds consistent with owner-reported v0.2, using pinned SDK full-revision rules:
  max0/65535 are unset sentinels and bootloader maximum checks are exempt. Actual old-build
  provenance/known-good operation is still needed; parsed fields alone do not prove opcodes,
  wiring, PSRAM behavior or transport compatibility.
- Physical context16MiB. A legacy4MiB image profile is acceptable with the reviewed old4MiB
  layout; a header capacity smaller than its table is rejected. 16MiB images still require
  the actual16MiB hardware and proper paired table.
- Correct table type/subtype/flags/alignment/geometry/MD5/serialization. Only the recorded old
  or proposed production layout is accepted; the experimental readonly table is not stock
  normal recovery. Images and sector footprints fit their intended regions and do not overlap.
- Bootloader offset0 (not classic ESP32 offset0x1000), table0x8000, OTA0xE000, app0x10000,
  app1 offset from the selected table. OTA initializer selects a populated app0; stale moved
  OTA metadata is not reused.

The original installed map is NVS9000/5000, OTAE000/2000, apps10000 and150000 each140000,
SPIFFS290000/170000, no coredump. Proposed map has apps10000 and750000 each740000,
SPIFFSE90000/160000 and coredumpFF0000/10000, with unchanged NVS/OTA geometry.
The new controlled1329760-byte application exceeds an old140000 slot by19040 bytes.
An app-only upload is incompatible with the recorded installed layout.

## Owner-private offline review input

Place generic-named owner-provided files in a private directory, with `recovery-review.json`:

```json
{
  "kind": "recovery-review",
  "physical_flash_bytes": 16777216,
  "owner_reported_known_good": true,
  "images": [
    {"role":"bootloader","file":"bootloader.bin","offset":0,"bytes":0,"sha256":"REPLACE_WITH_TRUSTED_HASH"},
    {"role":"partitions","file":"partitions.bin","offset":32768,"bytes":0,"sha256":"REPLACE_WITH_TRUSTED_HASH"},
    {"role":"otadata","file":"ota-initializer.bin","offset":57344,"bytes":8192,"sha256":"REPLACE_WITH_TRUSTED_HASH"},
    {"role":"app0","file":"application.bin","offset":65536,"bytes":0,"sha256":"REPLACE_WITH_TRUSTED_HASH"}
  ]
}
```

Zero sizes/placeholders are intentionally invalid. Use actual independently obtained sizes
and trusted hashes, not values invented from this template. The known-good flag records
owner evidence, not Codex authentication. Private original/NVS/filesystem images need not
be uploaded to GitHub. The checker reads images only and refuses an existing output report.

```sh
python3 tools/stage25_recovery_check.py --core-dir "$CORE_3_3_0" \
  --recovery-dir "$PRIVATE_RECOVERY_DIRECTORY" --output "$NEW_PRIVATE_REPORT"
```

This is file-only; no port/chip interrogation. Python3.8-compatible syntax is used. Local
High Sierra execution of this new script was not tested. The owner previously used Python3.8.10
and esptool4.12.0 successfully. Newer esptool is not required for recorded ROM operations.
Local GCC14.2/toolchain operation on10.13.6 remains unverified; supplied Linux review binaries
can avoid a local compile if separately approved. Source reproduction remains available.

## Future installation/recovery plan — non-executable, not authorization

1. Review the owner recovery resource/known-good evidence and ROM access, physical chip,
   flash/security, cable/port/power evidence. Current physical confirmation is owner-controlled.
2. Verify exact controlled binary/bootloader/table/OTA identities and explicit profile. Approve
   private fresh NVS credentials and empty SPIFFS image/hash/geometry; do not raw-relocate the
   old larger filesystem. Existing backup files remain untouched.
3. Review an explicit bounded region plan: bootloader0, table8000, OTAE000/2000, private
   fresh NVS9000/5000, the same controlled app at10000 and750000, fresh SPIFFSE90000/160000,
   newly initialized coredumpFF0000/10000. No whole-chip erase or padded merged image is needed.
   Exact application sector footprints are10000..155000 and750000..895000 for this build;
   other ranges are their exact assigned sectors. The bootloader20256-byte footprint is
   0..5000. No range is an instruction to execute now.
4. NVS replacement is a deliberate fresh-owner operation, not accidental overlap. The old
   preservation planner still protects NVS and is not silently bypassed; a fresh plan requires
   an explicit reviewed allowlist. No physical writer or such authorized plan is supplied here.
5. Before first application boot, validate installed table and each written artifact/readback
   under a separately approved operation. Mixed old/new table or stale OTA selection stops
   deployment. Keep ROM recovery available; stop on any disagreement or unclear image identity.
6. After separate authorization, first acceptance checks are diagnostics, AP/authentication,
   zero SPIFFS scripts, disabled autorun/default MSC, USB reconnection/CDC and optional SD.
   Later owner-authorized harmless TextEdit output checks do not imply all hosts/layouts work.
7. On failure, return to owner-verified ROM recovery and use the previously reviewed matching
   resource/region plan under explicit approval. Do not improvise erase/format/repair.

Only three preparation gates remain: actual recovery-resource verification, private fresh
artifact receipts/final range review, and owner-controlled ROM/readback/physical authorization.
Physical USB/Wi-Fi/storage/heap/stack acceptance follows an authorized installation, not a
fictional prerequisite PASS. No further language work or NVS immutability architecture is
required to perform that review. Recommend Stage26 be that owner preparation/review milestone.
