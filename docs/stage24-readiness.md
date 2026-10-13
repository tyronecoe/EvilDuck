# Stage 24 recovery-first readiness

**GO: offline source, candidate, fresh-image and owner recovery-resource review.**
**NO-GO: physical migration, application boot, flash, erase, format or OTA.**

The owner no longer requires exact original firmware/NVS/settings/scripts preservation.
Original backups are optional recovery resources, must remain unchanged, and were not
supplied to Codex. Owner-reported High Sierra hashes/preflight/NVS zero findings/SPIFFS
roundtrip remain historical local evidence. They are not SDK runtime immutability claims.
No stock firmware discovery was performed: the owner already knows its source.

| Gate | Evidence / status |
|---|---|
| Existing layout | Recorded original: NVS 0x9000/0x5000, otadata 0xE000/0x2000, apps 0x10000 and 0x150000 each 0x140000, SPIFFS 0x290000/0x170000, no coredump |
| Proposed layout | Offline verified production geometry unchanged; this is not the installed table |
| Experimental table | Same geometry, only NVS readonly mask 0x2; REVIEW ONLY, not authorized for flashing |
| Arduino erase path | Source/linked and native guards retained; no auto whole-partition erase |
| Iterator cleanup / failure-open | Fixed only in isolated experimental dependency; normal/safe archives intentionally unchanged |
| Early callbacks | No-OS interval lacks later protection; one-shot query and mutable metadata are not lifetime/hardware protection |
| Fresh settings | Offline generation + SDK-source startup checked synthetically; explicit owner credentials required |
| Fresh filesystem | Empty offline image roundtrip and geometry verified; normal auto-format/example-install behavior remains a reviewed risk |
| Quiescence | Safe/candidate skip settings, payloads, filesystem, application HID/MSC/web/CLI; earlier SDK/CDC activity is separate |
| Recovery firmware | Owner-provided resource pending exact image/build, chip/header/partition/offset/hash verification; not searched or fabricated |
| ROM recovery / power / cable | Owner previously reported ROM access; current readiness and controlled recovery must be separately confirmed |
| Physical chip/security | Prior owner 16 MiB/quad/3.3 V/security-disabled evidence retained; no new interrogation performed |
| High Sierra toolchain | Local Python/esptool compatibility evidence retained; target compile compatibility still not established by Linux success |
| Future write ranges | Must be separately approved and checked against every region; no full-chip erase or padded merged deployment plan supplied |
| Normal transition | No automatic arming. Requires independent writable-table/profile/factory-settings/mount/recovery review and authorization |

Exact old-data preservation is no longer a blocker, but known ranges, reliable recovery,
correct images/geometry and safe application startup still are. The readonly candidate
cannot transparently become normal writable firmware. Existing non-atomic settings saves,
legacy blank credentials, startup mount failures and SDK/raw routes need explicit policy.

Recommend Stage 25 review owner-provided recovery-image compatibility and a controlled
fresh provisioning/normal-boot acceptance contract, including mount-error/no-auto-format
policy and credentials verification. Do not infer authorization from the stage number.
No Stage 25 work has begun and no executable physical steps are included.
