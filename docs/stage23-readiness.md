# Stage 23 readiness under the revised owner policy

**Physical migration, application boot and OTA remain NO-GO.**

The owner-authorized addendum removes exact preservation of the old firmware, NVS,
settings and scripts from mandatory future criteria. Original backups are optional,
must not be altered/deleted, and have not been supplied to Codex. Compatible stock
recovery is acceptable; a functional upgraded firmware remains the primary goal.
See stage23-owner-policy.md; older reports remain historical, not overwritten.

| Gate | Current evidence / remaining requirement |
| --- | --- |
| Iterator ownership | Confirmed source/native-allocation loss, target20-byte structure evidence; minimal cleanup passes ownership/protection tests |
| SDK correction | One-object runtime/relocation/ABI equivalence and repeated deterministic archive rebuild; linked only in isolated experimental candidate |
| Stage22 gate | All36 corrected-source cases pass; rejects unsafe descriptors before initializer, retains safe-start and no auto-erase/arming |
| Callback/metadata | Advanced mutable fields, one-shot query, null-iterator/OOM allowing decision and pre-install no-OS interval remain limitations |
| Early-writer coverage | Bounded native/source audit extended through bootloader/flash/coredump/OTA; indirect/ROM/raw/proprietary paths not fully certified |
| Owner local evidence | Previously reported three hashes/sizes, full preflight, SPIFFS roundtrip and zero NVS findings retained; optional for legacy-data recovery, not Codex physical inspection |
| Recovery firmware | Still mandatory: a verified compatible stock/recovery image or reproducible build. Stock repository similarity alone is not an image identity or recovery test |
| ROM/cable/power/port | Owner previously reported ROM access; fresh owner-controlled recovery readiness and suitable setup remain required for deployment review |
| Geometry/image integrity | Exact chip/16MiB/bootloader/table/OTA/app identities and explicitly approved ranges remain mandatory; currently installed original table must not be mistaken for proposed layout |
| Filesystems | Old SPIFFS0x290000/0x170000 differs from proposed0xE90000/0x160000. Raw relocation remains unsafe. Optional file preservation uses verified repacking; deliberate fresh initialization would require separate approval |
| NVS provisioning | Exact old contents no longer required. Current checked loader/no-auto-repair safeguards remain. Fresh writable namespace/default provisioning must be reviewed, not silently introduced as error recovery |
| Autorun/HID/storage | Quiescent candidate suppresses application services; earlier USB/CDC descriptors may exist. Normal transition needs explicit safe defaults/autorun review and physical acceptance testing |
| Hardware behavior | Flash preservation, USB transport, timing, heap, stack high-water and High Sierra compatibility remain unmeasured |
| Authorization | No current physical authorization. Verified software artifacts do not grant it |

**GO:** offline artifact/source/contract/recovery-image review and separately approved
software preparation. **NO-GO:** any physical migration, application boot or OTA now.
This is not conditional on achieving exact legacy NVS immutability, and not on stage
number. It follows from unresolved recovery/deployment evidence and absent authorization.

Recommended Stage24 scope, subject to review: establish a verified compatible recovery
build/image and a recovery-first, owner-approved fresh-NVS/settings/filesystem provisioning
contract; investigate scanner failure-open policy and early no-OS/callback stability
within controlled approved ranges. Retain read-only candidate as an optional diagnostic
profile. Do not silently permit old tooling to bypass its historical preservation gates,
reset settings, format media or transition into writable operation. No Stage24 work or
physical/destructive commands are introduced in Stage23.
