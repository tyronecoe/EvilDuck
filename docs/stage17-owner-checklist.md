# Stage 17 owner preparation, recovery and stopping gates

Nothing here authorizes flashing. No physical checks were run in this stage. Retain
[Stage15 readiness](stage15-hardware-readiness.md) and
[Stage16 checklist](stage16-hardware-readiness.md) as historical/physical references.

## GO: local, offline preparation only

1. Keep two independent original full-flash copies and the original partition sector;
   never overwrite them. Owner-recorded full image16777216bytes SHA256
   d1712805e3282e59395efc4f10bd9496b7d338e1b18710379c1112f35248bda7;
   sector4096bytes SHA256 8edc409c4d09a6ac4cb2b3029ad9aaf2edcd2c5e0e89137861b1018a7d21ee15.
   Approved new SPIFFS1441792bytes SHA256
   fea8c95f9a0b49878e69fe9e9afec7472ce52f6b3d7c1b35db43e905470043fe.
2. Run local wc/shasum and the new read-only verifier. Its default owner pins cannot
   be replaced by synthetic-test hashes. Require all seven files, checked geometry,
   actual extractability and byte-for-byte old/new preservation. Missing files or
   changed hashes are stopping conditions, not reasons to update the pins silently.
3. Preserve old SPIFFS at290000/170000 and its file export. Never truncate/raw-relocate
   it toE90000/160000. Keep the independent approved new image; temporary capacity
   repack verifies overhead/content but is not a replacement owner artifact.
4. Use pinned core3.3.0 in the Stage16 isolated wrapper, PSRAM off,16MiB,USB-OTG/TinyUSB,
   CDC on,QIO80MHz/240MHz/custom table. Mac10.13.6 Python3.8.10 helpers are compatible
   by syntax, but actual Arduino CLI/Darwin compiler execution remains unverified.
   Local core installation alone is insufficient. No downgrade to2.0.17, USBMode
   change or global-core patch is an acceptable shortcut. A separately performed
   offline Mac smoke build or reviewed cloud artifact is required.
5. Review normal versus quiescent-safe artifact hashes/provenance. Safe-start has no
   filesystem/web/CLI/autorun/keyboard execution services and cannot be armed live.
   Default normal firmware retains existing autorun and SPIFFS formatting behavior.
   Do not confuse the two or treat the generated merged image as a migration artifact.
6. Prepare/reverify the exact seven-region plan from real owner files. NVS9000..DFFF
   is protected from all writes and sector erases. Both new app slots receive the
   identical approved safe image; OTA metadataE000/2000 is initialized to app0 rather
   than preserving old app1 selection at150000. Newly introduced coredumpFF0000/10000
   is erased-state initialized, with no old coredump to relocate. No full-chip erase
   or padded merged image for normal migration. This remains a plan, not execution.

## Separately authorized hardware prerequisites — NOT executed

Owner previously reported ESP32-S3 QFN56v0.2,16MiB quad3.3V flash,40MHz crystal,8MiB
PSRAM (kept disabled), security/encryption disabled and working ROM USB Serial/JTAG.
Reconfirm the particular device/current installed layout before migration;16MiB capacity
alone does not install the new table. Establish exact port, known good data cable,
stable power, verified BOOT/EN ROM-entry/recovery method and closed competing serial
monitors. Do not infer GPIO/button wiring or use a stale port after re-enumeration.

Python3.8.10/esptool4.12.0 already performed ROM reads per owner evidence. No5.x upgrade
is required for flash_id, get_security_info or read_flash. Those are **physical** reads,
may reset the device/upload a volatile stub and need separate authorization. The cloud
build's bundled5.0 elf2image use is local-file conversion, not a requirement to replace
owner esptool. Refer to the prior read-only commands only after port/ROM verification;
none are executed by Stage17. Host MSC mounting may write Spotlight/filesystem metadata;
it is not a read-only validation and is prohibited until separately reviewed.

## NO-GO: application boot, migration or OTA now

* Actual owner backups are absent here and have not been independently checked.
* Normal firmware exceeds original140000 slots; safe firmware fitting a small slot
  does not authorize installing it with an incompatible table. New SPIFFS/app1
  addresses and16MiB profile require the reviewed migration first.
* Before EvilDuck setup, Arduino3.3.0 can erase NVS on no-free-pages/new-version errors.
  Safe-start prevents application autorun/mounting but does not fix that core path.
  NVS readability/compatibility has not been established. Resolve/review this risk
  before any application boot if strict no-auto-erase preservation is required.
* Preserved autorun must be inspected/explicitly disabled before transitioning to normal
  firmware. Power/data isolation prevents host injection during owner preparation;
  it does not itself stop CPU payload execution or SPIFFS/NVS writes in normal firmware.
  Safe profile is deliberately quiescent, with no remote/button arming shortcut.
* All ROM recovery, backup, final artifact/region/hash, first-boot policy and individual
  migration authorization gates remain unmet by software tests alone.

Stop on different chip/capacity/security, changed table/hashes, failed file extraction,
wrong compiler/profile, missing provenance, unsafe ranges, unexpected boot/autorun,
unknown NVS compatibility or recovery uncertainty. Do not repeatedly boot an unreviewed
application to diagnose a potential formatting/autorun failure.

## Recovery plan — destructive restore is a different operation

Preserve the original verified16MiB image and original4096-byte sector on independent
media with a recorded hash ledger. The original full image includes bootloader, table,
NVS, OTA metadata, applications and old SPIFFS. Returning that raw image to address0
through the verified ROM recovery path would revert all those regions and overwrite
current data. It is **destructive**, requires separate owner approval/current-data
backup, and is not a read-only command or a normal migration step. No restore/erase/write
command is generated here. Recheck its exact hash before any future recovery review;
a sector backup alone cannot recover applications/files/settings. On recovery failure,
stop rather than guessing addresses/security/tool versions.

Recommended next reviewed scope: owner offline backup verification plus a dedicated
no-auto-erase early-NVS startup policy investigation before physical application boot.
Only after those reviews should individual ROM read-only checks/migration/TextEdit
acceptance be authorized. Stage18 has not begun.
