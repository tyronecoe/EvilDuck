# Stage 16 hardware readiness — no physical actions performed

The [Stage15 checklist](stage15-hardware-readiness.md) remains the detailed evidence,
read-only command, old/new map, backup, filesystem, NVS, ROM recovery and physical
acceptance reference. Stage16 supersedes only its unpatched-core readiness finding.
Both reviewed patches are active in the isolated production build. Four router fault
paths are guarded and the two stock empty/null paths cannot be reached through that
OUTPUT route. Direct stock callback invocation remains unsafe; valid stock event
posting and other USB/SDK event-queue/descriptor limitations are unchanged.

Confirmed here: software source/provenance/hash checks, mock routing, native link and
resource results. NOT confirmed: physical keyboard LED report delivery, host receipt
of release during disconnect, hardware USB/CDC/MSC coexistence/latency, task high-water,
heap, High Sierra controller/input-source behavior or Darwin compiler execution.
Feedback still has no on-wire epoch or causal acknowledgment. No physical hostile USB
probes are recommended. Nothing authorizes identity/personality changes.

Owner's prior physical16MiB/quad3.3V/security-disabled/ROM-recovery evidence is retained,
not newly interrogated. PSRAM remains off despite reported8MiB physical PSRAM. Actual
backup files are absent from this environment and must be independently rechecked on
the Mac before any migration:

* Full original16777216bytes, SHA256 d1712805e3282e59395efc4f10bd9496b7d338e1b18710379c1112f35248bda7.
* Original partition sector4096bytes, SHA256 8edc409c4d09a6ac4cb2b3029ad9aaf2edcd2c5e0e89137861b1018a7d21ee15.
* New SPIFFS1441792bytes, SHA256 fea8c95f9a0b49878e69fe9e9afec7472ce52f6b3d7c1b35db43e905470043fe.

Old slots0x140000 remain installed unless independently established otherwise. The
Stage16 build exceeds them; NO-GO for application-only OTA/upload into the old map.
Standard app0 remains0x10000; proposed app1 moves0x150000→0x750000. NVS0x9000/0x5000
must be protected from both writes and sector erases. Old SPIFFS0x290000/0x170000
cannot raw-copy to0xE90000/0x160000. File-level extraction/repack/verification with
4096-block/256-page geometry and every file hash/roundtrip is required. New coredump
0xFF0000/0x10000 has no old partition to preserve. Review deterministic OTA metadata,
both application placements and full manifest; no full-chip erase or padded merged
image for normal migration. SPIFFS.begin(true) formatting risk remains.

Establish exact port/cable/power, owner-controlled ROM download entry and recovery,
two independently checked original backups and sufficient disk space. Prevent autorun
from preserved NVS on first application boot: use data isolation and review/disable
payload autorun before connecting an injecting USB host. Do not expose an MSC image
as a supposedly read-only test: macOS may write metadata. Owner's esptool4.12.0 with
Python3.8.10 suffices for previously verified ROM read-only operations; do not force
5.x solely because the build package uses a different esptool. No new destructive
commands or migration images are provided in Stage16.

**Conditional GO:** separately authorized local backup/hash inspection and known-device
ROM read-only checks after port/power/recovery prerequisites. These reset/interact with
the device and must be performed by the owner under separate authorization.

**NO-GO now:** migration, old-slot OTA, first application HID/MSC exposure or claims of
physical USB safety. Require Stage16 review, final exact artifact/region/hash/NVS-safe
manifest approval, verified backups/repack, ROM recovery, autorun prevention and toolchain
or reviewed cloud artifact compatibility first. Later authorized harmless TextEdit tests
must cover US/DE text, modifier releases, ordinary reconnect, actual feedback/unknown
states, SD/SPIFFS integrity, jitter timing, CDC/web responsiveness and heap/task-stack.
No Stage17 is started. Recommend this gated normal-host validation before personality
changes; retain INJECT_VAR/restart as independently specified future work.
