# Deliberate rollback to the identified prior review package

rollback-application.bin is the prior Caps/Queue public package application:
1,381,776 bytes, SHA-256
573a86715f41f9d5e6628a8ff9117c176f178c8c014c5986d1f8e9bca01fc1bf
Package commit30310d08b6b833af146b46548ecb4141554180c0;
source/build ace54c7aeecbf7e7dda6fff9ebb8fa3ad1673d59.

This baseline's bytes are verified, but the image currently running on the board
has NOT been independently identified. Do not describe this as an exact readback
of the current board. It is a deliberate return to the named review baseline,
not a silent selection of the older c20 or de24 image. Earlier packages remain
untouched in the repository. A new private backup captures the current device
before any later authorized update; it is never automatically restored.

Read INSTALL-MAC.md, verify/fresh-extract the ZIP, check Python3.8+/esptool4.12.0,
rediscover the fresh ROM port, and obtain separate owner authorization. Stay in
ROM after a partial update. First perform the default read-only check:

```bash
bash install-macos.sh --port /dev/cu.REPLACE_WITH_FRESH_ROM_PORT
```

Then deliberately select rollback:

```bash
bash rollback-macos.sh --port /dev/cu.REPLACE_WITH_FRESH_ROM_PORT
```

The helper freshly checks chip/security/layout/OTA, creates a private full backup,
displays both app ranges, requires typed ROLLBACK, repeats identity/metadata/hash
checks, writes the exact573a baseline into both apps and compares each slot.
Step messages indicate progress. It cannot be overridden to install through a
forwarded --action. No reboot, retry, full-chip erase or automatic restore occurs.
No NVS/filesystem/bootloader/table/OTA/coredump is written. Two-slot writes are
not power-loss atomic. A mismatch or unknown metadata means stop for review,
not bypass the guard. Successful comparisons do not establish physical boot,
Caps Lock or LED behavior. No recovery or flashing was executed by Codex.
