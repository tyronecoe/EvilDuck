# Stage 22 readiness — physical migration, application boot and OTA NO-GO

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING**

GO is limited to offline review and separately reviewed software work. Nothing here
authorizes application boot, partition migration, OTA, hardware access or recovery writes.

| Gate | Evidence and remaining condition |
| --- | --- |
| Original backup identities | Owner reported three matching hashes/sizes and full local preflight PASS on High Sierra; Codex has not received or inspected private binaries |
| Original NVS structure | Owner reported compatible-within-verified-checks with zero findings; this is offline subset validation, not SDK runtime immutability or current-device freshness |
| SPIFFS | Owner-reported byte-identical roundtrip PASS; original 0x290000/0x170000 to proposed 0xE90000/0x160000 requires file-level repacking, never raw relocation |
| Arduino erase recovery | Stage18 no-auto-erase patch retained and checked; candidate adds a separate one-shot pre-init gate |
| SDK readonly | Stage21 actual source/API/native archive evidence retained; tested mutation paths denied with canonical readonly descriptor and ordinary main callback |
| Candidate gate | Correct actual startup path rejects missing/writable/misconfigured/ambiguous metadata before initializer; source tests + final native ELF support it |
| Canonical metadata/callback | Exact raw table and loaded descriptors checked, callback policy queried; mutable RAM, callback changes after query, forged pointers and raw/ROM writers remain outside guarantee |
| Early startup | 17 CORE hooks, 36 reverse constructors, 7 SECONDARY hooks inventoried; selected flash installation roots inspected. Complete transitive/ROM/closed-source write audit remains unresolved |
| Failed old/wrong table | Gate prevents its NVS initializer but cannot undo a pre-gate write; no candidate boot authorized on original writable layout |
| Iterator ownership | Gate iterators released; pinned callback scan may retain one iterator on denial. Candidate queries once, does not fix general SDK repeated-denial path |
| Quiescence | Production safe setup/loop source tested, no settings/mounts/application HID/MSC backing/web/CLI/payload/arming. Earlier USB descriptors/CDC and RTOS activity can exist |
| Artifacts | Normal/safe remain production writable profiles. Candidate table/app/ELF are separate labeled review artifacts with exact pins and hash validation, not a deployment manifest |
| Existing table/device | Owner-recorded original layout is distinct; no new live table/flash/security check occurred, no assumption of migrated device |
| Recovery | Independently retain complete original16MiB backup and4096-byte table backup, approved repacked SPIFFS, owner ROM download/recovery evidence; fresh cable/power/port/recovery readiness remains separately reviewed |
| macOS10.13.6 | Owner local Python3.8/esptool4.12/private preflight worked; native compiler, real USB feedback/storage/timing/heap/task behavior remain untested |
| Normal transition | Requires separate explicit review/authorization, preserved-data and settings/autorun review, approved writable profile/table. No automatic candidate arming/transition exists |

Owner-recorded originals:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| evilduck-16m-backup.bin | 16777216 | d1712805e3282e59395efc4f10bd9496b7d338e1b18710379c1112f35248bda7 |
| partition-table-backup.bin | 4096 | 8edc409c4d09a6ac4cb2b3029ad9aaf2edcd2c5e0e89137861b1018a7d21ee15 |
| new-spiffs-0x160000.bin | 1441792 | fea8c95f9a0b49878e69fe9e9afec7472ce52f6b3d7c1b35db43e905470043fe |

No physical commands or executable migration steps are supplied. Original NVS remains
0x9000/0x5000; the production proposed CSV is unchanged, and all prior deployment
artifacts remain untouched. Future exact NVS-excluded artifact/range review, recovery
prerequisites, fresh evidence and owner authorization are still required. No full-chip
erase or padded merged normal migration image is appropriate.

**Recommended Stage23 scope, for review only:** investigate the pinned iterator retention
with actual target evidence and a minimal separately pinned cleanup proposal; extend the
early SDK/bootloader/transitive write audit and callback stability analysis. Do not infer
that stage count or successful compilation resolves physical gates. Stage23 is not started.
