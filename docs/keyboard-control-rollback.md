# Deliberate rollback — owner review required

This package includes the owner-identified installed application:

- BuildId: `CAPS-STOP-TRACE-20261019-v1`.
- Filename: `rollback-application.bin`.
- Exact size: **1,404,640 bytes**.
- SHA-256: `25e17cadacf3b2ab5eb5ece32fc94f4bf36fb71eb90e91814dca7f7320bd5178`.
- Source/report baseline: `0803937b9b552fe4b6e6cb6d1dd60f80f098449c`.

This is the current known application, not the older MAC-CAPS-TIMING rollback.
The associated prior LED-return success is owner-operated evidence on the tested
Mac/EvilDuck configuration. It does not certify every feature or host platform.

Rollback is not automatic and is not authorized by package preparation. If the
owner has installed another application since confirming this identity, stop and
review the appropriate rollback before any physical operation.

First perform offline package review:

```bash
python3 preflight.py --directory . --image rollback
```

No hardware is accessed. Without fresh installed partition and OTA metadata,
the offline result deliberately has no selected write ranges.

Only after separate explicit owner authorization for physical rollback, use the
owner's known ESP32-S3 ROM-entry/recovery procedure and identify the current ROM
port. Do not assume a historical `/dev/cu.usbmodem...` path. From this exact
extracted package, substitute the actual port:

```bash
bash rollback-macos.sh --port /dev/cu.CURRENT_ROM_PORT
```

The launcher cannot be overridden into installation. It validates the package,
the rollback bytes, chip identity, security, flash size, installed partition
geometry and supported app0 OTA initializer. It saves a fresh private full-flash
backup without overwriting existing backups, then requires typed `ROLLBACK`.
Afterward it checks the same device, unchanged metadata and image identity again.

One write operation targets only the rollback application's exact bytes at
`0x10000` and `0x750000`. Rounded sector ranges remain inside the two application
slots. Bootloader, partition table, NVS, OTA metadata, SPIFFS and coredump are not
written or repaired. Two independent comparisons must succeed. There is no
automatic reset, reboot, retry, whole-chip erase, formatting or OTA operation.

If reading, writing or either comparison fails, stop and retain ROM mode, logs
and the new private evidence directory. Do not improvise offsets, erase or reset
the device to make a check pass. Review the stopped condition before deciding a
new owner-controlled action. A returned comparison result still does not prove
the application booted: manual boot and a bounded acceptance check are separate.

Original stock firmware remains **OWNER CONFIRMED: AVAILABLE EXTERNALLY**. This
app-only rollback does not attempt to obtain or package it, and does not replace
the need to verify any different recovery image before an authorized deployment.
