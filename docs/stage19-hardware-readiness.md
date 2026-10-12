# Stage 19 readiness: migration remains NO-GO

## Proven software protections

- Original installed core is untouched. Exact Stage16 HID routing + Stage18 Arduino
  NVS policy hashes remain mandatory in isolated disposable builds and final ELF proof.
- Arduino's known whole-NVS automatic erase/retry path is removed. Original SDK error
  is preserved and both profiles stop application startup on any error.
- Normal startup now rejects invalid/unreadable settings before application services,
  autorun, filesystem mounting/autoformat, HID or MSC activation. Failure is latched.
- Safe-start never mounts SPIFFS/SD, initializes EvilDuck keyboard/MSC, loads settings,
  starts web/CLI or arms a script. No automatic transition or arming exists.
- Offline plan writes/sector erases cannot overlap protected NVS9000/5000. Unresolved
  NVS structural findings now block a checked plan. Neither result authorizes migration.

## Unresolved SDK and physical boundaries

nvs_flash_init and later SDK reads can change NVS before returning. Recovery can erase
pages, change entry bitmap bits, remove indexes/chunks and ignore some cleanup errors.
A clean return is not a health or immutability certificate. No SDK binary protection
is added; unverified rewriting would be less safe. Actual complete SDK startup, locks,
flash-program failures, bootloader/global constructors and physical USB are not exercised.
Existing configured rollback code before NVS can change OTA metadata. CDC/USB-on-boot
precedes EvilDuck setup; quiescent application does not mean zero SDK/USB activity.
Serial diagnostics can be unavailable after an earlier fatal failure.

## Evidence gates

| Gate | Current evidence | Required next action |
| --- | --- | --- |
| Physical16MiB/security/ROM recovery | Owner previously reported S3v0.2,16MiB quad3.3V, secureboot/encryption off, ROM USB working; not newly queried | Owner reconfirm relevance/current device under separate authorization |
| Three backup sizes/hashes | Owner locally verified all exact recorded values on High Sierra; Codex files absent | Keep private duplicates; run full local preflight |
| Original boot/app/partition integrity | Recorded original layout; current owner binaries not independently structurally inspected here | Local Stage17+19 verifier checks images/table and recovery app |
| NVS structure and settings | Synthetic tests only; actual owner region not inspected | Run private offline checker; resolve every issue and SDK preservation strategy |
| SPIFFS | Owner previously reported seven-file byte-identical repack; old170000 vs new160000 | Recheck file inventory/byte roundtrip/capacity with exact supplied images |
| SDK immutability | Not established; source tests demonstrate mutations | Independently justify a reviewed SDK preservation/compatibility strategy before boot |
| Firmware provenance | Both current isolated patched-core profiles built and linked checks pass | Review exact generated hashes/profile and non-owner artifact inventory |
| High Sierra tooling | Python3.8.10/esptool4.12.0/core3.3.0 owner reported; native compiler/CLI not newly tested | Verify file-only tools first; do not downgrade/bypass pins or change USBMode |
| Migration/recovery authorization | None | Separate explicit approval for any physical read/boot/write; no operation inferred from software approval |

## GO / NO-GO

GO: owner-controlled offline backup/report/dependency/plan review only. Read-only local
procedure is stage19-owner-preflight.md. Hash/size evidence is now owner-confirmed; full
structural and NVS compatibility gates remain open. Private NVS values need not be shared.

NO-GO: physical migration, firmware application boot, normal-profile transition or OTA.
Strict SDK preservation is unresolved. Even a compatible-within-checks report cannot
close that gate alone. Do not repair NVS, raw-copy SPIFFS170000 into160000, full-chip erase,
use a padded merged image, boot normal firmware with unknown autorun or expose writable
MSC. No writer, destructive command or physical operation is supplied/executed here.

Separately authorized future ROM checks require correct cable/data port/power, exact
serial target/chip/security/capacity and a known ROM recovery route. Stop on any mismatch.
Original full16MiB image remains recovery reference, partition backup4096 checks original
map; restoration overwrites live data and must be reviewed/authorized independently.
NVS and microSD/file backups must be independently retained. Old slots140000 are too
small for normal current firmware; app1 relocation/OTA metadata and SPIFFS relocation
must be handled by the separately reviewed safe-profile plan, not application-only OTA.
New coredump has no original partition to preserve.

After all gates close and individual physical approval, future acceptance must separately
check TextEdit harmless output on macOS10.13.6, releases/disconnect, host LED feedback,
SD/SPIFFS contents, startup settings/autorun policy, heap and task high-water. Simulated
reports/source tests and successful compilation prove none of those physical results.

Recommend Stage20: review owner-local structural evidence and independently validate a
source-pinned SDK preservation contract (or explicitly reviewed alternative preservation
architecture). Later save-error/read-error handling may need dedicated work. No Stage20
implementation or physical testing begins automatically.
