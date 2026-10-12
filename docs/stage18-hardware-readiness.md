# Stage 18 readiness: software protection, not hardware certification

[Stage17 checklist](stage17-owner-checklist.md) remains the backup/map/ROM/toolchain
reference. This supplement resolves its Arduino whole-NVS erase path and retains
remaining SDK/physical gates. No device was accessed, booted, flashed, erased, formatted
or exposed as storage/HID in this task. Stage19 has not begun.

## Software findings

* Fixed: Arduino error recovery cannot erase the NVS partition or retry automatically.
  Exact original error is retained, every nonzero result stops further Arduino hooks,
  and both application profiles latch a quiescent error state before services.
* Verified software only: exact core-source/mock erase instrumentation, synthetic20KiB
  preservation, no app autorun/mount/HID/storage/settings/web/CLI, unchanged healthy
  profile behavior, final ELF policy and image provenance.
* Remaining: SDK page/item recovery can mutate NVS during nvs_flash_init before return.
  An injected example is OBSERVED, real SDK recovery is not emulated or physically
  tested. Early SDK/component/bootloader, heap/USB/flash failures and later settings
  namespace readability remain outside the layer. Existing OTA validation can happen
  before NVS and is not new health-based recovery assurance.
* Safe-start never arms normal services. Core USB/constructors may still enumerate;
  no new VID/PID/personality/descriptor is introduced. No writable backing image is
  activated by EvilDuck on failed NVS or safe boot. Host release/feedback behavior
  still needs ordinary separately approved physical validation.

## Owner evidence and preservation gates

Actual files are absent here; owner is separately verifying them on High Sierra:
full16777216bytes SHA d1712805e3282e59395efc4f10bd9496b7d338e1b18710379c1112f35248bda7;
sector4096bytes SHA 8edc409c4d09a6ac4cb2b3029ad9aaf2edcd2c5e0e89137861b1018a7d21ee15;
new SPIFFS1441792bytes SHA fea8c95f9a0b49878e69fe9e9afec7472ce52f6b3d7c1b35db43e905470043fe.
Preserve independently verified originals/recovery copies, file inventory and geometry.
No new actual backup verification result is manufactured by the synthetic tests.

Installed original slots remain140000 unless separately checked; normal protected
firmware exceeds them. Proposed dual740000 slots/table are not assumed installed.
NVS9000..DFFF remains excluded from every planned write and sector erase. Old
SPIFFS290000/170000 must not raw-copy toE90000/160000. Preserve file-level exports,
roundtrip metadata capacity and the separately approved new image. Old coredump is
absent; newFF0000/10000 is initialized inside its region. No full-chip erase/padded
merged image for normal migration. Destructive NVS repair is never automatic or
requested by an application error; owner approval, backups and exact region review
are prerequisites. Full-original restore through ROM would overwrite current data.

## GO / NO-GO

**GO:** owner-controlled offline file hashes/content/plan review and isolated software
reproduction. Known Ardu erase policy is demonstrably disabled in both profiles.

**Conditional GO:** separately authorized ROM read-only checks after confirming exact
ESP32-S3,16MiB/quad3.3V/security state, port/cable/power, known BOOT/EN entry/recovery and
new backup filenames. Prior owner physical facts are supporting evidence, not newly
reconfirmed. Python3.8.10/esptool4.12.0 ROM reads need no forced upgrade.

**NO-GO now:** firmware migration, application boot/OTA or normal services. Require
actual owner backup verification, current device/layout/security/recovery, NVS
compatibility/readability and SDK recovery-policy review, exact approved artifact
manifest, filesystem preservation, autorun prevention, first-boot selection and
individual authorization. Safe fitting an old slot does not waive the new layout.
High Sierra compiler/tool execution remains uncertain. No diagnostic delivery,
physical mutation-free initialization or successful migration is claimed.

Recommended Stage19 scope: independently review SDK NVS page-recovery/compatibility
and owner backup evidence, plus settings-read failure handling if justified. Keep
physical application boot gated until strict data-preservation expectations are resolved.
No unrelated language/personality or automatic next-stage implementation is included.
