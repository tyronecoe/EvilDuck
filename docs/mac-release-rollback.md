# Deliberate rollback to the current working STOP/LED application

Rollback target is the owner's current **c20dc399** application, not the older
shortcut image. rollback-application.bin: **1,376,576 bytes**, SHA-256:
`c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4`.
It is byte-identical to downloads/evilduck-stop-led-review.bin and independently
validated as an ESP32-S3 DIO/80 MHz/16 MiB application with appended digest.
Its original source is d18b7fddedaecef27be9fd7e486ad2d092a513c6; its original
package commit is 3dd4a083aa6634cf413ac7a43c36baaa749b7540.

No rollback has been executed by Codex. Obtain separate owner authorization
before writing. Read INSTALL-MAC.md first, verify the ZIP, use a fresh extraction,
check Python3.8+/esptool4.12.0 and rediscover the actual ROM-mode port. Stay in ROM
after an interrupted install; do not boot a partial image or start automatic retries.
Keep all existing backups. Run a fresh read-only check first:

```bash
bash install-macos.sh --port /dev/cu.REPLACE_WITH_FRESH_ROM_PORT
```

Then, only after deliberate review/authorization, select the separate rollback:

```bash
bash rollback-macos.sh --port /dev/cu.REPLACE_WITH_FRESH_ROM_PORT
```

It independently checks the package, current chip/security, supported partition
table and exact app0 OTA initializer; creates a new private complete backup; and
requires **ROLLBACK** after displaying the two-slot plan. It re-identifies the
chip and rereads table/OTA before writing the exact c20 image into both supported
application slots. Each slot is explicitly verified. It cannot be overridden to
install through a forwarded --action option. It never writes a bootloader,
partition table, NVS, OTA, filesystem or coredump, and never resets/reboots.

If the metadata, chip/security or tool differs, stop. Do not erase all, change
partitions, force OTA acceptance or automatically restore a merged backup. Keep
error evidence and arrange a separately reviewed recovery plan. A comparison
PASS proves bytes read by the tool match the image, not successful physical boot,
USB behavior or host key release. Two-slot writes are not power-loss atomic.
