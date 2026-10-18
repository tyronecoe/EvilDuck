# Mac package — owner review before any physical action

Candidate buildId: CAPS-DURATION-20261018-v1. Caps/LED remain physically unverified.
Read OWNER-CHECK.md and ROLLBACK-MAC.md. Ordinary typing is preserved in software;
this new build has not been physically tested. The owner-installed rollback is
2c657f0c74f1d12c88aa1e6fa6daf5cc76de36e8e68bc41a325f39b19c9045a7 (1,386,176bytes).

Keep existing backups untouched. Never paste credentials or private backups into
GitHub/chat. No new credentials, settings reset or provisioning is part of this
app-only update. There is no automatic reboot, replay or recovery.

Use macOS10.13.6 with Python3.8.10, esptool4.12.0 and Bash. A full ROM read at115200
can take many minutes. Numbered Step start/PASS/FAIL messages identify operations;
a quiet read is not permission to run another installer. The cloud performed no
serial/USB actions. Physical installation requires separate owner authorization.

After extracting to a folder, use Terminal there. Determine a FRESH ROM download
port; the historical /dev/cu.usbmodem10 must not be assumed. Put the device in ROM
mode using the owner's known physical procedure. Substitute the current port:

```bash
python3 preflight.py --directory .
bash install-macos.sh --port /dev/cu.CURRENT_ROM_PORT
```

The second command defaults to read-only check. It requires exact ESP32-S3/16MiB,
disabled encryption/SecureBoot, supported installed partition sector and exact
reviewed app0 OTA initializer. An unexpected valid OTA state also stops for review;
this is intentionally not a general active-slot decoder. No full backup/write is
performed during check. Never rewrite metadata just to pass these checks.

Only AFTER separately authorizing installation, the explicit action is:

```bash
bash install-macos.sh --action install --port /dev/cu.CURRENT_ROM_PORT
```

It validates the package, identifies the chip/security, reads current table+OTA,
creates a NEW private full16MiB backup under Desktop, verifies it, asks for typed
INSTALL, re-identifies the same device and re-reads/revalidates metadata and image
identities. One write operation targets only the exact app bytes at0x10000 and
0x750000; each rounded sector range fits its0x740000 slot. Bootloader, table,NVS,
OTA metadata,SPIFFS,coredump are not written. Each slot receives its own independent
verify_flash comparison. There is no full-chip erase, automatic retry or reboot.

On failure STOP and retain ROM mode and receipts. Do not run another action blindly.
Follow deliberate rollback review. After both comparisons PASS, boot_tested remains
false until the owner separately performs manual reset and acceptance. This task
has not authorized or performed that installation/reset.
