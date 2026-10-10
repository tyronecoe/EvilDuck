# EvilDuck S3: 16 MiB builds and migration preparation

**Do not upload or migrate until the individual device has been physically
verified as having at least 16 MiB flash.** The schematic and BOM specify an
ESP32-S3-WROOM-1U-N16, but they do not verify the module fitted to your unit.
Preparing a build is not a hardware migration. The individual device's capacity,
ROM recovery and security state were reported verified on 2026-10-10 (see below).
That does not authorize migration. Stages 3/4 are complete; Stage 5 remains paused.
Codex has not accessed this device. PSRAM remains disabled despite reported 8 MiB
embedded PSRAM; enabling it requires a separate investigation.

Adding `EvilDuckS3/partitions.csv` changes subsequent Arduino builds. It does not
change a device already running the old firmware. Arduino prioritizes this CSV
even when an old IDE partition-menu setting is selected. Do not use generic
Arduino defaults or upload these artifacts to an unverified/unmigrated device.

## Reproducible compilation, without hardware

Required: Python 3 (offline helpers support Python 3.8), Arduino CLI (tested 1.3.1), ESP32 Arduino core **3.3.0**, and
the existing S3 libraries. The wrapper verifies the active core version and
refuses a different core. It does not install/update libraries, discover serial
ports, upload, erase, or access USB hardware. This pins the board/core settings,
not every external library or tool; retain the Stage 2 library versions when
comparing binary sizes.

The Mac currently has core **2.0.17** installed. Do not compile/upload Stage 4
using that core. In Arduino IDE Boards Manager install/select **esp32 by
Espressif Systems 3.3.0**, then confirm that exact version. With Arduino CLI,
install the pinned package explicitly (build preparation only, no hardware):

```sh
arduino-cli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core install esp32:esp32@3.3.0 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core list
```

Use the wrapper below rather than an unguarded IDE compilation. It checks the
resolved active core and refuses 2.0.17 before firmware compilation. Installing
3.3.0 tools successfully on macOS 10.13.6 has not been tested here; if tool/OS
compatibility fails, stop and use reviewed artifacts from the pinned cloud build
or a compatible build machine. Do not silently fall back to 2.0.17.
Python 3.8.10/esptool 4.12.0 need no upgrade for the documented ROM operations.
The old installed firmware's core cannot be inferred from the Mac's current core.

From the repository root:

```sh
python3 tools/build_s3.py --build-dir /tmp/evilduck-s3-16m-build --jobs 2
```

The output directory must be empty and outside the checkout. Omitting
`--build-dir` selects a new temporary directory. `--arduino-cli` and
`--config-file` select a non-default CLI/configuration. Cloud example:

```sh
export XDG_CACHE_HOME=/workspace/tooling/arduino/cache
python3 tools/build_s3.py \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli \
  --config-file /workspace/tooling/arduino/arduino-cli.yaml \
  --build-dir /workspace/tooling/arduino/build/new-s3-16m-build --jobs 2
```

Pinned FQBN:

```text
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

Arduino IDE equivalents (core 3.3.0):

| Setting | Selection |
| --- | --- |
| Board | ESP32S3 Dev Module |
| Flash Size | 16MB (128Mb) |
| Partition Scheme | Custom; repository `partitions.csv` |
| Flash Mode | QIO 80MHz |
| PSRAM | Disabled |
| CPU Frequency | 240MHz (WiFi) |
| USB Mode | USB-OTG (TinyUSB) |
| USB CDC On Boot | Enabled |
| USB MSC On Boot | Disabled |
| USB DFU On Boot | Disabled |
| Erase All Flash Before Sketch Upload | Disabled |

The core's QIO menu uses a QIO bootloader ELF but DIO image-header fields. The
validator expects this combination, 80 MHz, ESP32-S3 chip ID and **16 MiB** in
both application and bootloader image headers. Enabling OPI flash or PSRAM
based solely on the N16 flash capacity would be incorrect.

The wrapper performs a clean compilation with `upload.maximum_size=7602176`.
It independently rejects an application `.bin` larger than `0x740000`, validates
the exact CSV and generated partition binary using Espressif's tooling, checks
resolved settings, and checks bootloader/table/OTA initialization/application
placement in the generated merged image. Logs, resolved properties and size/hash
reports remain in the build directory.

**Never use the padded `EvilDuckS3.ino.merged.bin` for data-preserving migration.**
It spans all 16 MiB and contains padding over data partitions. Keep it only as a
checked build artifact. A future authorized migration must use individually
reviewed regions and restored data. The application-only `EvilDuckS3.ino.bin`
is suitable for ordinary OTA only after the device has the new layout and
compatible bootloader configuration.

The IDE Custom menu alone reports a misleading 16 MiB program maximum. Use the
wrapper for reproducible builds and the independent slot-size check. Ordinary
IDE compilation/upload is not a migration safeguard.

## Reviewed layout

All end addresses are exclusive. The partition-table sector stays at `0x8000`
and the S3 bootloader stays at `0x0`.

| Partition | Type/subtype | Offset | Size | End |
| --- | --- | --- | --- | --- |
| nvs | data/nvs | `0x9000` | `0x5000` | `0xE000` |
| otadata | data/ota | `0xE000` | `0x2000` | `0x10000` |
| app0 | app/ota_0 | `0x10000` | `0x740000` | `0x750000` |
| app1 | app/ota_1 | `0x750000` | `0x740000` | `0xE90000` |
| spiffs | data/spiffs | `0xE90000` | `0x160000` | `0xFF0000` |
| coredump | data/coredump | `0xFF0000` | `0x10000` | `0x1000000` |

Each OTA slot is 7,602,176 bytes (7.25 MiB). New SPIFFS is 1,441,792 bytes
(1.375 MiB); NVS is 20 KiB; OTA metadata is 8 KiB; coredump is 64 KiB.

Offline validation and tests, after a completed wrapper build:

```sh
python3 tools/s3_validation.py --core-dir PATH_TO_ESP32_CORE_3_3_0 \
  --build-dir PATH_TO_COMPLETED_BUILD
python3 tests/stage2/run_tests.py
python3 tests/stage25/run_tests.py --core-dir PATH_TO_ESP32_CORE_3_3_0 \
  --build-dir PATH_TO_COMPLETED_BUILD
```

The Stage 2 runner includes the complete Stage 1 suite. Its ASan/UBSan C++
fixtures use only mocked HID, clock, storage and command output. Stage 2.5 tests
use Python, generated artifacts and synthetic flash backups. No hardware is
accessed by these commands.

## Reported real-device evidence and corrected installed map

Evidence supplied by the owner on 2026-10-10, using **esptool 4.12.0** in ROM
download mode: ESP32-S3 QFN56 revision v0.2, WiFi/BLE, embedded PSRAM 8 MB
(AP_3v3), 40 MHz crystal, ROM USB-Serial/JTAG, **16 MB detected flash**, quad
flash eFuse (four data lines), 3.3 V flash, Secure Boot disabled, Flash Encryption
disabled, `SPI_BOOT_CRYPT_CNT=0x0`. ROM USB-Serial/JTAG differs from the normal
firmware's TinyUSB configuration and does not require changing that build mode.
Capacity is now owner-verified; the exact module marking/PSRAM configuration is
not inferred from the chip report. **Keep PSRAM disabled.**

Backups reported successfully read by the owner:

| File | Exact bytes | Reported SHA-256 |
| --- | ---: | --- |
| `evilduck-16m-backup.bin` | 16,777,216 | `d1712805e3282e59395efc4f10bd9496b7d338e1b18710379c1112f35248bda7` |
| `partition-table-backup.bin` | 4,096 | `8edc409c4d09a6ac4cb2b3029ad9aaf2edcd2c5e0e89137861b1018a7d21ee15` |

The actual backup binaries are not present in the cloud workspace. These are
recorded owner observations, not independently recalculated cloud hashes. Use
the matching expected-hash guards below when processing the local originals.
The full backup must also contain the exact saved sector at `0x8000`.

Actual decoded installed table (end addresses exclusive):

| Partition | Offset | Size | End |
| --- | --- | --- | --- |
| nvs | `0x9000` | `0x5000` | `0xE000` |
| otadata | `0xE000` | `0x2000` | `0x10000` |
| app0 | `0x10000` | `0x140000` | `0x150000` |
| app1 | `0x150000` | `0x140000` | `0x290000` |
| spiffs | `0x290000` | **`0x170000`** | **`0x400000`** |

**No coredump partition exists on the installed device.** The earlier assumption
of `0x160000` SPIFFS plus `0x10000` coredump described the Arduino core's default
CSV, not this device. It was incorrect for this migration. The corrected helper
requires the actual five-partition table; it does not substitute the core default.
Old SPIFFS source is 1,507,328 bytes (1,472 KiB), not 1,441,792 bytes.

## Layout comparison and retained recommendation

App partition offsets require 64 KiB alignment; with no Secure Boot the installed
partition tooling allows 4 KiB application size alignment. Accounting for both
constraints, the largest equal slots are:

| Option | Each OTA slot | SPIFFS | Coredump | Free per slot with Stage 4 bin |
| --- | --- | --- | --- | --- |
| **A: retain repository layout** | `0x740000` / 7.25 MiB | `0x160000` | `0x10000` | 6,304,944 B |
| B: full old SPIFFS plus coredump | `0x730000` / 7.1875 MiB | `0x170000` | `0x10000` | 6,239,408 B |
| B without coredump | `0x740000` / 7.25 MiB | `0x170000` | None | 6,304,944 B |

A valid B-with-coredump map has app0 `0x10000..0x740000`, app1
`0x740000..0xE70000`, SPIFFS `0xE70000..0xFE0000`, an unused 64 KiB gap
`0xFE0000..0xFF0000`, and coredump `0xFF0000..0x1000000`. NVS and otadata
remain unchanged. Slot sizes above `0x730000` require the next aligned app1
address and cannot fit full SPIFFS plus coredump. B-without-coredump uses A's
app addresses and SPIFFS `0xE90000..0x1000000`.

**Retain A.** It keeps the approved reproducible Arduino/dual-OTA layout and
reserves crash diagnostics supported by the pinned core: its S3 qio_qspi
sdkconfig enables flash coredump, ELF format and boot checking. A 64 KiB partition
is conventional but does not guarantee every possible crash dump will fit.
The owner-verified old layout has no historical coredump to preserve.

A reduces SPIFFS capacity by 64 KiB, about 4.35%. That is a modest cost when SD
holds larger payload/data files, but actual internal-file usage is not yet known.
File-level export/repack must prove that the files fit with sensible free space.
If they do not, stop and revisit B; do not silently omit files, truncate images,
expand partitions or offload files without review. B reduces migration complexity
only when a same-size old image also has compatible filesystem geometry; it still
needs the same backups, bootloader/table/OTA initialization and recovery checks.
Both retain standard app0 and dual OTA. Coredump removal saves no OTA headroom
relative to A and sacrifices useful diagnostics, so it is not preferred.

## Read-only verification commands on macOS 10.13.6

These commands are retained for user-operated verification/recovery, not for
execution during repository preparation. esptool **5.x requires Python 3.10 or
newer**; macOS 10.13.6's system Python is insufficient. Use a compatible Python
3 installation on that Mac, preferably a virtual environment, and check:

```sh
python3 --version
python3 -m esptool version
```

The owner's esptool 4.12.0 already worked on this Mac; no upgrade is required
for this correction. Use that tested environment unless there is a separate reason
to change it. Version 4.x uses `flash_id`, `read_flash`, and `no_reset`; 5.x uses
hyphens. Do not mix syntax. The offline capacity parser accepts both versions.
Installing esptool 5.x is optional and requires a compatible Python/OS environment;
its installation on this particular Mac has not been tested in the cloud.

Equivalent **esptool 4.12.0 read-only commands**, after manually entering ROM
mode and choosing the actual port:

```sh
EVILDUCK_PORT=/dev/cu.usbmodem_REPLACE_WITH_ACTUAL_PORT
python3 -m esptool --chip esp32s3 --port "$EVILDUCK_PORT" \
  --before no_reset --after no_reset flash_id
python3 -m esptool --chip esp32s3 --port "$EVILDUCK_PORT" \
  --before no_reset --after no_reset \
  read_flash 0x8000 0x1000 NEW-partition-table-backup.bin
python3 -m esptool --chip esp32s3 --port "$EVILDUCK_PORT" \
  --before no_reset --after no_reset \
  read_flash 0x0 0x1000000 NEW-evilduck-16m-backup.bin
```

The existing verified backups must not be overwritten; use new filenames/directories
for any additional read. The following sections retain the requested 5.x forms.

The basic esptool 5.x identification syntax is:

```sh
python3 -m esptool --chip esp32s3 flash-id
```

Prefer the explicit-port commands below, which suppress automatic resets. First
establish ROM-download recovery: hold BOOT/GPIO0 while resetting EN, then release
BOOT after entering download mode. Confirm the board's buttons or test pads
against the schematic. This prevents application startup/autorun during reading.
Keep the device in ROM download mode until reading is finished. If a subsequent
command cannot connect, repeat the manual BOOT/reset sequence before retrying.
If ROM native
USB is unavailable, investigate the documented 3.3 V UART recovery connection;
do not improvise GPIO wiring or voltage levels.

List macOS serial device names and choose the **ROM-download** port:

```sh
ls /dev/cu.*
EVILDUCK_PORT=/dev/cu.usbmodem_REPLACE_WITH_ACTUAL_PORT
python3 -m esptool --chip esp32s3 --port "$EVILDUCK_PORT" \
  --before no-reset --after no-reset flash-id > flash-id.txt
cat flash-id.txt
```

Require `Detected flash size: 16MB` or greater; retain the manufacturer/device
identification and inspect the module marking as corroboration. An image header
or Arduino menu saying 16MB is not physical verification. The offline guard can
check the recorded output:

```sh
python3 tools/s3_migration.py check-flash-id --log flash-id.txt
```

It rejects insufficient, absent or ambiguous detected-capacity evidence. A saved
log can be stale or belong to another device; this is a preparation guard, not
fresh detection or authorization. Check secure-boot/flash-encryption status with
an appropriate read-only diagnostic before planning raw-image restoration.
Encrypted backups cannot be assumed safe to relocate to different addresses.

Save the existing partition-table sector in a new backup directory:

```sh
python3 -m esptool --chip esp32s3 --port "$EVILDUCK_PORT" \
  --before no-reset --after no-reset \
  read-flash 0x8000 0x1000 NEW-partition-table-backup.bin
```

**Only after detected physical capacity is at least 16 MiB**, save a full 16 MiB
backup (on a larger device this backs up the first 16 MiB; also retain a complete
device-size backup if needed):

```sh
python3 -m esptool --chip esp32s3 --port "$EVILDUCK_PORT" \
  --before no-reset --after no-reset \
  read-flash 0x0 0x1000000 NEW-evilduck-16m-backup.bin
shasum -a 256 NEW-partition-table-backup.bin NEW-evilduck-16m-backup.bin
```

Require successful command exit status, a 4,096-byte partition-sector file and
a 16,777,216-byte flash backup. Retain untouched originals and their hashes.
These are read operations. The separately labeled recovery section later contains
a destructive restore example; it is not part of this verification procedure.
The current device's table must be decoded and compared, not assumed to match
the old cloud build. If it differs, stop and revise the migration plan.

## Offline SPIFFS and settings preparation

The old SPIFFS is **`0x290000`, size `0x170000`**; the destination is
**`0xE90000`, size `0x160000`**. Moving its partition entry does not move files.
**Never raw-copy, truncate or crop the old image into the smaller destination.**
Its last 64 KiB are filesystem data, not a disposable old coredump. The helper
rejects source/destination size mismatch and supplies no hardware writer.

Preserve the untouched full backup, partition sector and hashes on independent
storage. Also preserve file-level contents: every name/path, byte count and
SHA-256, including hidden/empty/binary files and configuration-related files.
NVS settings need separate exports/backups; they are not SPIFFS files. Back up SD
contents independently, including `/sys/usb_disk.img`; SD remains data storage,
not executable firmware storage. No SD cache or firmware behavior changes occur.

### 1. Source archives from verified local backups

This command is **offline**, run on local copies, not the device:

```sh
python3 tools/s3_migration.py prepare \
  --core-dir PATH_TO_ESP32_CORE_3_3_0 \
  --flash-id-log flash-id.txt \
  --backup evilduck-16m-backup.bin \
  --partition-sector partition-table-backup.bin \
  --expected-backup-sha256 d1712805e3282e59395efc4f10bd9496b7d338e1b18710379c1112f35248bda7 \
  --expected-sector-sha256 8edc409c4d09a6ac4cb2b3029ad9aaf2edcd2c5e0e89137861b1018a7d21ee15 \
  --output NEW_OFFLINE_ARCHIVE_DIRECTORY
```

It verifies recorded capacity, exact old/new maps, backup size/hashes, agreement
of the separately saved sector and full backup, and existing output refusal.
It archives `nvs-recovery-backup.bin` and the full **`spiffs-source-archive.bin`**.
It creates no coredump archive. The manifest sets destination addresses to null
and marks raw relocation disallowed; proposed destination geometry is recorded
separately. These archives are recovery/source evidence, never a flash-write plan.

### 2. File-level export and optional offline decode

Primary migration data is a complete file tree plus integrity inventory. Use the
installed firmware's file export facilities where supported, with autorun/USB
payload execution prevented under a separately approved procedure. Do not assume
a text script editor/download captures every binary file or every SPIFFS name.
Codex will not boot or access the unit to obtain these exports.

Optional offline decoding is available with installed **mkspiffs 0.2.3** built
for arduino-esp32. The tested configuration matches pinned core 3.3.0: block 4096,
page 256, name length 32, metadata 4, magic and magic-length enabled. The helper
checks tool version/configuration, validates names before unpacking, compares
unpacked names/sizes with the source listing and refuses existing output.

```sh
python3 tools/s3_migration.py extract-files \
  --mkspiffs PATH_TO_MKSPIFFS_0_2_3 \
  --image NEW_OFFLINE_ARCHIVE_DIRECTORY/spiffs-source-archive.bin \
  --output NEW_FILE_EXPORT_DIRECTORY
python3 tools/s3_migration.py inventory \
  --files NEW_FILE_EXPORT_DIRECTORY --output NEW_FILE_INVENTORY.json
```

Cloud tests reliably roundtrip synthetic binary, hidden, empty, nested and text
files using this geometry. **The owner's actual image has not been supplied or
decoded in the cloud.** Old firmware geometry and actual-image extraction remain
unverified. If decoding fails, do not repair, format or overwrite the source;
retain the original and use explicit device-assisted file-level backup/restore
instead of guessing geometry. Under a separately approved HID-isolated procedure,
enumerate every SPIFFS path and obtain byte-for-byte exports, file lengths and
hashes; compare the full independent inventory. The web script editor is not a
binary-safe full-filesystem backup. Existing upload handlers may use basenames:
verify support for nested paths before restoring them. If the installed interface
cannot export/restore any file reliably, stop for a reviewed backup/restore method;
do not silently flatten names, normalize text or omit files.
Compare decoded contents with an independent installed-firmware export when
possible. Offline decode/repack verification proves agreement with the exported
file tree, not independently that the tree contains all original user data.

### 3. Create the smaller filesystem and verify restoration offline

```sh
python3 tools/s3_migration.py pack-files \
  --mkspiffs PATH_TO_MKSPIFFS_0_2_3 \
  --files NEW_FILE_EXPORT_DIRECTORY --output NEW_REPACK_DIRECTORY
```

This creates a **new** filesystem image of exactly `0x160000`, restores every
exported file, unpacks it again and compares every path/size/SHA-256. It includes
hidden files and refuses links/unrepresentable names, overwritten output and an
output inside the source tree. It rejects data above a conservative 75% raw
capacity budget (1,081,344 content bytes); metadata/GC overhead can still require
more space, so actual packing and roundtrip verification must also pass. This
budget is a preparation safeguard, not a precise SPIFFS totalBytes/usedBytes
prediction. Never silently drop files to make an image fit.

Output `spiffs-new-0x160000.bin` is distinct from the larger source archive. Its
manifest and file inventory record image/file hashes and mark hardware migration
unauthorized and on-device restoration unverified. This procedure creates and
formats only an offline image, never the physical filesystem.

### 4. Verify the later on-device restore

During a separately authorized migration, either install the validated new-size
image before first normal boot or deliberately format only the **new** partition
and restore the complete file set. After restoration, independently export the
actual files back to a new local directory and compare:

```sh
python3 tools/s3_migration.py verify-files \
  --files NEW_RESTORED_EXPORT_DIRECTORY --inventory NEW_FILE_INVENTORY.json
```

Check device-reported capacity/free space, every file hash, NVS settings and SD
contents. Migration is incomplete until restored-file verification passes.
Normal firmware still calls `SPIFFS.begin(true)`: mount failure can automatically
format the selected partition on first boot. Avoid an unplanned first normal boot
with a missing/invalid new filesystem. If formatting is intentional, it must be
reviewed, followed by restoration and verification. Bundled-example installation
is not evidence of successful user-data restoration. No firmware behavior was
changed by this correction.

## Future authorized migration and recovery

Do not perform this sequence until device verification and a separate migration
review/authorization are complete. No hardware writer is supplied in this stage.

1. Verify physical capacity, current partition map, security state and dependable
   ROM-download recovery. Keep an independent copy of the current full backup,
   user files, settings and SD data. Preserved NVS may still enable autorun: first
   normal boot must not deliver HID to the development host. Use a separately
   reviewed HID-isolated/power-only/Wi-Fi restoration procedure and disable autorun
   through existing controls before application validation, recording its old setting.
   Remain in ROM download mode until that first-boot procedure is approved.
2. Build and validate the new bootloader, table and approved Stage 4 application.
   Confirm flash size 16 MiB, app0 address `0x10000` and the exact reviewed map.
3. With stable power and ROM recovery available, install only individually
   reviewed regions. **Do not full-chip erase or write a padded merged image.**
   NVS remains at `0x9000`, size `0x5000`, preserving the `duck` namespace and
   Wi-Fi/web/autorun/LED settings. Keep the same core and settings schema.
   Preservation still requires a readable, compatible NVS image: Arduino core
   startup can erase NVS after `ESP_ERR_NVS_NO_FREE_PAGES` or
   `ESP_ERR_NVS_NEW_VERSION_FOUND`. Retain both the raw backup and exported
   settings, particularly if the physical device used a different core version.
4. Deliberately initialize OTA metadata at `0xE000` for initial app0 boot.
   Metadata stores OTA sequence/slot index and state, not an absolute app address.
   Preserving it may select the newly relocated, empty/stale app1 or retain
   inappropriate old update state. **Replace both 4 KiB sectors** with the pinned
   core 3.3.0 `boot_app0.bin`, which selects app0 deterministically. Install the
   same compiled/mock-tested Stage 4 image in **both** new slots. This prepares
   bootable images; physical boot validation is still required before calling
   either image known-good on this unit. Web OTA cannot initialize this layout.
5. Install only the validated **new `0x160000`** SPIFFS image at `0xE90000`,
   or carry out the reviewed format/file-restore alternative. Never use the
   `0x170000` source archive there. Explicitly initialize the new coredump region
   at `0xFF0000`; no old coredump partition/history exists to restore. Preserve
   the complete old SPIFFS in backups; do not treat its last 64 KiB as crash data.
6. Verify written regions and settings before allowing normal boot. Confirm
   SPIFFS files, NVS values, SD, USB interfaces, boot and web operation. Do not
   run payloads against the development host; use controlled harmless fixtures.
7. Validate app-only web OTA to the alternate new slot and confirm both installed
   images boot correctly. Retain a wired recovery procedure and the old backups.

Changing bootloader/table is not protected by ordinary app OTA. Interruption
can require ROM recovery. Old apps remaining at old addresses are not automatic
fallback partitions under the new table. Restoring the old installation requires
its matching old bootloader, table, metadata and data locations, not just an old
application binary; this too needs a reviewed recovery operation.

### Exact initial regions and offline review plan

The reviewed initial operation uses only these seven regions. This is a plan,
not permission or an executable flashing procedure:

| Region | Address | Image length / bound | Purpose |
| --- | --- | --- | --- |
| S3 bootloader | `0x0` | current build 20,256 B; must end before `0x8000` | Pinned 3.3.0/16 MiB boot configuration |
| Partition table sector | `0x8000` | exactly `0x1000` | Generated 3 KiB table padded with 0xFF to one sector |
| OTA metadata | `0xE000` | exactly `0x2000` | Pinned `boot_app0.bin`, both sectors replaced |
| Stage 4 app0 | `0x10000` | current `.bin` 1,297,232 B; maximum `0x740000` | Initial app0 boot |
| Same Stage 4 app1 | `0x750000` | same image/size/hash | Valid alternate-slot contents |
| New repacked SPIFFS | `0xE90000` | exactly `0x160000` | Complete verified file-level restore |
| New empty coredump | `0xFF0000` | exactly `0x10000` of 0xFF | Erased state, no historical dump |

NVS `0x9000..0xE000` is deliberately absent from the write list. The offline
validator checks both image bytes and 4 KiB sector-rounded erase ranges, exact
addresses and lengths, and refuses overlaps with NVS, old app1 addresses,
oversized raw SPIFFS, missing slots, arbitrary-region or merged-chip plans.
The unpadded 3 KiB partition table is padded only to its own sector; it does not
extend into NVS. Never use a full-chip erase or the padded full-chip merged image.
Before first normal boot, read back and compare NVS with its original archive;
then verify settings after boot, since core initialization may erase incompatible
NVS as described above. A physical old-to-new core/settings transition remains
untested and needs that explicit check.

The pinned OTA initializer has a valid first record (sequence 1, state
`0xFFFFFFFF`, CRC32 `0x4743989A`) and an invalid second record. It selects app0,
with no inherited pending-update state. Initializing only one sector or preserving
old metadata is not the deterministic migration plan. Coredump is a newly
introduced standard data/coredump partition; the pinned SDK's flash ELF/CRC32
boot checks recognize erased/empty storage. Its presence is supported by the
compiled default SDK configuration, but physical dump capture remains untested.

Prepare a **review-only** local artifact directory after backup/export/repack
checks. No helper performs serial discovery, runs esptool or writes hardware:

```sh
python3 tools/s3_write_plan.py \
  --core-dir PATH_TO_ESP32_CORE_3_3_0 \
  --build-dir PATH_TO_CLEAN_STAGE4_BUILD \
  --archive-dir NEW_OFFLINE_ARCHIVE_DIRECTORY \
  --repack-dir NEW_REPACK_DIRECTORY \
  --expected-backup-sha256 d1712805e3282e59395efc4f10bd9496b7d338e1b18710379c1112f35248bda7 \
  --expected-sector-sha256 8edc409c4d09a6ac4cb2b3029ad9aaf2edcd2c5e0e89137861b1018a7d21ee15 \
  --output NEW_REVIEW_ONLY_PLAN_DIRECTORY
```

It checks the completed build/table/headers, archive provenance, repack geometry,
file inventory, capacity, image hashes and OTA initializer. It stages individual
images and `review-plan.json`, never an uploader. Actual complete old-file
coverage must be established independently; the manifest cannot prove that an
incomplete user export contains all old files. Migration authorization remains
false. No new physical migration write commands are supplied in this correction.
Changing only the table is insufficient; the bootloader, metadata, both matching
applications and new filesystem must be prepared together before normal boot.
Interrupted migration can still require ROM recovery, regardless of dual OTA.

### Destructive recovery example — manual, separately authorized only

The owner already holds the verified **complete original 16 MiB image** and
partition-sector backup with the exact hashes recorded above. In a failed
migration, restoring the full original image in ROM mode returns the matching
old bootloader, table, metadata, apps, NVS and `0x170000` SPIFFS together. It also
**overwrites all newer flash contents/settings** with the backup. The small
partition-sector backup alone is not a complete recovery image.

The following is an explicitly destructive **future manual restore example**,
not a read-only check, not authorization, and never an automated test command.
First verify file length and recorded SHA-256, physically confirm the correct
16 MiB device/port/security state, enter ROM mode, use stable power and obtain
separate recovery authorization. Do not reset into the application afterward:

```sh
# DESTRUCTIVE RESTORE — DO NOT RUN DURING PREPARATION OR READ-ONLY VERIFICATION
python3 -m esptool --chip esp32s3 --port "$EVILDUCK_PORT" \
  --before no_reset --after no_reset \
  write_flash --flash_mode keep --flash_freq keep --flash_size keep \
  0x0 evilduck-16m-backup.bin
```

This esptool 4.12.0 form preserves original image-header settings, including the
old configured flash size; it does not convert the backup to the new layout.
No separate full-chip erase is needed. A full restore intentionally rewrites NVS
from its verified original backup; this is distinct from normal migration, which
must preserve NVS in place. The security state reported for this unit permits
unencrypted raw recovery; recheck if that state ever changes.

After an authorized restore, these **read-only verification** commands save new
files without overwriting the originals:

```sh
python3 -m esptool --chip esp32s3 --port "$EVILDUCK_PORT" \
  --before no_reset --after no_reset \
  read_flash 0x0 0x1000000 RECOVERY-readback-16m.bin
python3 -m esptool --chip esp32s3 --port "$EVILDUCK_PORT" \
  --before no_reset --after no_reset \
  read_flash 0x8000 0x1000 RECOVERY-readback-partitions.bin
shasum -a 256 RECOVERY-readback-16m.bin RECOVERY-readback-partitions.bin
```

Require exact original sizes and hashes before permitting a reviewed HID-isolated
normal boot. Neither restore nor these device operations was executed by Codex.

## OTA compatibility and deferred issues

`webserver.cpp` uses `Update.begin(UPDATE_SIZE_UNKNOWN)` with the default
application command, streams `Update.write`, and finishes with `Update.end(true)`.
In core 3.3.0, `Updater.cpp` selects `esp_ota_get_next_update_partition(NULL)`,
uses that partition's actual size and activates it with `esp_ota_set_boot_partition`.
Neither path hardcodes old offsets or slot capacity, so the alternate new OTA
partition remains selectable. This is verified from source/build configuration;
on-device OTA and power-loss behavior remain untested. Web OTA updates neither
the bootloader nor the partition table and cannot perform the initial migration.

Rollback is enabled, but Arduino's default `verifyOta()` accepts a pending image
during `initArduino()`, before EvilDuck storage/web initialization. It does not
guarantee recovery from later setup failures. The existing `/update` path also
lacks the explicit authentication checks used by several other routes. Health
verification and updater authentication are deferred issues; neither is changed
in Stage 2.5. Parser/HID/SD/web command behavior and Arduino Micro sources remain
unchanged.
