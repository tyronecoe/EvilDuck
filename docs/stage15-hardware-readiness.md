# Stage 15 hardware readiness and recovery — PREPARATION ONLY

No commands below were executed against hardware. Every physical action needs the
owner's separate authorization. This document does not authorize migration, OTA,
erase, formatting, USB fault injection or host keystrokes.

## Evidence ledger and gates

Owner previously reported actual ESP32-S3 QFN56 rev0.2,16MiB flash, quad/four data
lines at3.3V,40MHz crystal,8MiB embedded PSRAM, secure boot/encryption disabled,
SPI_BOOT_CRYPT_CNT0, working ROM USB Serial/JTAG with Python3.8.10/esptool4.12.0.
PSRAM remains disabled. Repository schematic N16 is supporting design evidence,
not verification of any other device. Stage15 made no physical query.

These owner-recorded files were not found in this workspace; Stage15 cannot certify
current existence, location, size, hashes, seven-file content or restore usability:

| File | Expected bytes | Owner-recorded SHA256 |
| --- | ---: | --- |
| evilduck-16m-backup.bin |16777216 |d1712805e3282e59395efc4f10bd9496b7d338e1b18710379c1112f35248bda7 |
| partition-table-backup.bin |4096 |8edc409c4d09a6ac4cb2b3029ad9aaf2edcd2c5e0e89137861b1018a7d21ee15 |
| new-spiffs-0x160000.bin |1441792 |fea8c95f9a0b49878e69fe9e9afec7472ce52f6b3d7c1b35db43e905470043fe |

Before migration, independently recheck all three on the Mac and keep at least two
copies of the original full image on separate storage. Revalidate the new filesystem
image and its file inventory, not only a previous transcript. Stop on mismatch.
Owner reported seven files totaling1181 payload bytes and a byte-for-byte extraction/
repack/unpack roundtrip; that supports feasibility but is not a new verification here.

## Individually authorized read-only owner commands

Run only after confirming the exact port belongs to this EvilDuck and putting it in
the already established ROM-download mode. ROM entry resets execution; esptool may
upload a volatile RAM stub for reads. These commands do not erase/write persistent
flash but do interact with hardware and are NOT run by Codex. Disconnect other serial
devices, close IDE/serial monitors, use the verified BOOT/EN procedure, a known data
cable, stable power, direct port, and sufficient local disk space. Do not infer the
port from a stale name after USB personality/ROM changes.

```sh
# Local file inspection only, in the directory containing the real owner backups:
wc -c evilduck-16m-backup.bin partition-table-backup.bin new-spiffs-0x160000.bin
shasum -a 256 evilduck-16m-backup.bin partition-table-backup.bin new-spiffs-0x160000.bin
python3 -m esptool version
# Replace this placeholder with the independently identified existing port:
ED_PORT='/dev/cu.usbmodem_REPLACE_WITH_VERIFIED_PORT'
python3 -m esptool --chip esp32s3 --port "$ED_PORT" flash_id
python3 -m esptool --chip esp32s3 --port "$ED_PORT" get_security_info
# Use new filenames; never overwrite the verified originals:
python3 -m esptool --chip esp32s3 --port "$ED_PORT" read_flash 0x8000 0x1000 stage15-current-partition.bin
python3 -m esptool --chip esp32s3 --port "$ED_PORT" read_flash 0x0 0x1000000 stage15-pre-migration-full.bin
shasum -a 256 stage15-current-partition.bin stage15-pre-migration-full.bin
```

esptool4.12.0 uses underscore command spellings; no upgrade to5.x is required for
these operations. Decode the current4096-byte table with pinned gen_esp32part.py
using local input/output only. If it differs from the owner-recorded old map, reassess
rather than forcing migration. Full raw images can differ if settings/files changed;
preserve both versions and explain differences. Do not confuse a newly captured hash
with the recorded original recovery hash.

## Installed versus proposed layout

| Region | Owner-recorded installed offset / size | Repository proposal offset / size |
| --- | --- | --- |
| NVS |0x9000 /0x5000 |0x9000 /0x5000 (preserve) |
| OTA metadata |0xE000 /0x2000 |0xE000 /0x2000 (initialize app0) |
| app0 |0x10000 /0x140000 |0x10000 /0x740000 |
| app1 |0x150000 /0x140000 |0x750000 /0x740000 |
| SPIFFS |0x290000 /0x170000, ends0x400000 |0xE90000 /0x160000, ends0xFF0000 |
| Coredump |Absent |0xFF0000 /0x10000 (new) |

The Stage15 application is1329136bytes, exceeding the old0x140000 slot (1310720bytes) by18416bytes. Physical16MiB capacity alone does not enlarge the installed partition table. NO-GO for an application-only web OTA/upload of this build while that old map is installed; the reviewed full region migration must come first.

Old SPIFFS is1507328bytes; new SPIFFS1441792bytes. Never raw-relocate the old image:
it would exceed the destination and corrupt the new coredump region. File-level
backup is mandatory. Verified geometry is4096-byte blocks/256-byte pages; extract
old image to files, verify names/contents/hashes, construct exact0x160000 destination,
unpack into a separate directory and compare every file byte-for-byte. Capacity must
be checked by actual successful image construction/roundtrip, not payload-size sum
alone; reserve filesystem overhead. Existing tools reject mismatched raw sizes and
unverified repacks. Device-assisted file backup/restore is the fallback if geometry
cannot be reproduced. Never silently format or lose files.

SPIFFS.begin(true) currently can format a missing/unmountable relocated filesystem
on first boot. Therefore restore/verify the prepared image before boot, and prevent
normal application startup until the written data is checked. MicroSD contents are
independent of this flash migration; back up the card and any4MiB USB backing image
as a precaution. Do not mount a served MSC image on the Mac in a read-only validation:
the host may automatically write filesystem/Spotlight metadata. Storage exposure/
write tests require separate permission and a reviewed disposable backed-up image.

## Migration plan — separate final review, never automatic execution

1. Verify physical capacity/security, current layout, all local backups, repack file
   contents/hash and ROM recovery first. Resolve any changed evidence. Reconfirm
   PSRAM off, dual slots and app0 standard address. Confirm a pinned known-good build,
   its image/header/hash/size and review whether the upstream HID patch should be
   adopted; Stage15 shipped firmware remains unpatched.
2. Prepare exact reviewed region manifest using existing s3_write_plan.py. It stages
   local files only and must validate both sector-rounded erases and writes. No
   full-chip erase and no padded full-flash merged image for normal migration.
3. Reviewed write set: bootloader at0x0 (within0..0x8000), partition sector at0x8000,
   deterministic Arduino OTA initializer at0xE000 (both sectors), identical approved
   app binaries at0x10000 and0x750000, verified new filesystem at0xE90000, erased
   new coredump initialization at0xFF0000. Both apps fit0x740000. The actual manifest
   supplies exact sizes/hashes and sector rounding; this document supplies no new
   migration binaries and cannot be substituted for that artifact review.
4. NVS0x9000..0xDFFF is protected from every write AND sector erase. Never span
   bootloader+table+apps using a padded merged image. OTA metadata must not blindly
   preserve old app1 selection: old app1 is at0x150000, which is now inside expanded
   app0. The known initializer selects app0 with valid CRC; app1 also receives a
   known-good application. Changing the table alone is insufficient.
5. New coredump has no old data to relocate. Initialize erased0xFF as required by
   the reviewed plan; actual panic dump operation/configuration is a separate test.
   Do not deliberately crash hardware during ordinary readiness checks.
6. Future owner-executed writes/erases need explicit individual authorization and
   a final manifest review immediately before execution. None are issued here.
   Verify written region hashes/readback, decode the new table, verify both app
   placements and SPIFFS contents before considering migration complete.
7. First application boot must prevent existing autorun/payloads from reaching the
   host. Preserved NVS may retain autorun and unknown settings. Review/disable it
   through an approved method, initially using power-only/USB-data isolation and
   WiFi management if appropriate. Do not assume example/test filenames are harmless.
   Restoring NVS does not authorize its stored payload behavior.

## Recovery

Establish working ROM-download entry, port/cable/power, read-only identification and
backup access BEFORE migration. Failed boot/USB enumeration cannot be relied on for
web OTA recovery. If migration fails, stop, record symptoms, and reenter ROM mode.
After separately authorized destructive recovery, restoring the exact verified
original16MiB image starting0x0 would restore original bootloader/table/apps/NVS/SPIFFS
and erase/write all covered sectors. This intentionally overwrites preserved data
and rolls settings back; it is a full recovery operation, not normal migration.
Rehash the source and verify readback after that separately reviewed recovery.
No recovery/erase/write command is executed or presented as a read-only check here.

## High Sierra toolchain and USB mode caveats

Owner reports Python3.8.10, esptool4.12.0 and core3.3.0 installed. Installation alone
does not prove bundled compilers/esptool/CLI binaries execute on macOS10.13.6. Perform
an offline wrapper clean compile, inspect exact active core/library versions, and
check downloaded Darwin executable architecture/minimum OS with file/otool if needed.
Actual Darwin tools are absent here; minimum OS compatibility is unresolved. Do not
silently use core2.0.17, enable PSRAM or change the profile to make a Mac build pass.
Use reviewed pinned cloud artifacts or a compatible build machine if necessary.

The pinned profile is USBMode=default (USB-OTG/TinyUSB), CDCOnBoot=cdc, CPU240,
FlashSize16M/custom CSV, QIO80MHz, PSRAMdisabled, MSC/DFU bootdefault. The owner's
older IDE selection 'Hardware CDC and JTAG' differs from this profile; use the guarded
wrapper, not that menu selection. ROM USB Serial/JTAG is recovery mode, not evidence
that an application built in Hardware CDC/JTAG mode provides this TinyUSB HID backend.
No USB descriptor/personality migration is implemented by ATTACKMODE.

## Physical acceptance matrix — PROPOSED, NOT RUN

| Test | Prerequisites / evidence to capture | Stop condition |
| --- | --- | --- |
| ROM/read-only inventory | Explicit authorization, right port, power; chip/flash/security/table and local file hashes | Capacity/security/layout/hash mismatch |
| TextEdit plain US output | Separately installed reviewed firmware, autorun disabled, matching input source, blank saved document; exact visible text | Unexpected keys/host commands |
| Modifier/HOLD/release | Harmless letters only, no GUI/system shortcut; record presses, EOF/STOP release and editor recovery | Stuck modifiers, repeated unintended keys |
| DE AltGr/dead keys | Matching actual host layout; text-only document; inspect literal punctuation and pending composition | Wrong output or unverified input source |
| Normal USB reconnect | Approved unplug/replug only, no malformed packets; enumeration/CDC port change and cleared ownership | Unrecoverable port/device state |
| Lock feedback | Observe ordinary Caps reports first; Num/Scroll may be absent on High Sierra; known/unknown/session evidence | Unknown treated as false/false ACK |
| SD/SPIFFS | Backed-up files, harmless read-only scripts, no formatting; content/hash and read/error behavior | Missing files, autoformat or changes |
| Timing/jitter | Text-only output, USB trace/timestamps; separate extra jitter from dwell/default/explicit delays | Blocking UI/cancellation or unexpected timing |
| Heap/task-stack | Reviewed instrumentation, web traffic and harmless bounded scripts; minimum heap/high-water per task | Exhaustion, unbounded growth, resets |
| MSC/OTA/coredump | Separate write/crash/update authorization and disposable media/recovery; not this read-only phase | Unapproved writes or missing recovery |

GO only for separately authorized ROM identification/local-file hash checks after
port/power/output-path prerequisites. NO-GO for migration or Stage15 firmware HID
validation until current backup/toolchain/autorun/firmware installation gates and the
upstream patch decision are reviewed. NO-GO for malformed physical USB tests here.
