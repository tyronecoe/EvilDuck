# Deliberate rollback to owner-confirmed installed application

BuildId MAC-CAPS-TIMING-20261019-v1,1,397,968bytes, SHA-256
5e10009fd3e5a0a862b4f7bed1f7f28ba8464f7bb1066fd8091c6e01b2ed4a59.
Owner confirmed installed ID and hash on2026-10-19; Codex did not read the board.
The new ZIP carries the exact application from the prior published package,
evilduck-mac-caps-macos-install-v1.zip, package commit
c18fff39e672164121783808e82420557bf9dc36. The previous ZIP SHA-256 is
2f3b398e04f755c751b1ae4aa3602eec133a2e70c44c3fc1e72474d09f2ac77f.
This is not the older58b,2c,c20dc399 or de24 application.

Only after separate owner authorization and fresh explicit ROM port selection,
from the reviewed package directory:

```bash
bash rollback-macos.sh --port /dev/cu.CURRENT_ROM_PORT
```

Wrapper cannot be overridden to install. Same strict ESP32-S3/security/table/OTA
checks, NEW private full backup, typedROLLBACK and repeat checks apply. One write
operation uses the exact rollback image in both app slots; two independent verify
comparisons. No automatic boot/reset/retry or data-partition writes. On disagreement
or failure stay in ROM and stop for review. Existing backups stay untouched. Keep
prior package independently accessible. Physical recovery/installation not tested
or authorized by this software-preparation work.
