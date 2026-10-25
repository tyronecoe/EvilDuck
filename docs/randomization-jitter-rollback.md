# Exact uppercase rollback — review only

The rollback application is accepted `ROUTEB-RANDOM-UPPER-20261025-v1`, **1,410,016 bytes**, SHA-256 `2cdb3e182dbbc3f2f2be21154cc49516e74337ed5c0c52a75aa772d1ef8eb098`. Its source public archive is untouched `evilduck-routeb-random-uppercase-macos-v1.zip`, SHA-256 `f3aa611dea7ba10cc133a3e7b58d22e3747f40bc88c410cd955f6bfd8253fbae`. Codex verifies those public bytes; it does not assume an independent hardware readback.

Package assembly must verify the exact application size/hash, image identity, table geometry, source receipts and bound installer. The older preprocessing and lock-feedback applications are not this candidate's rollback target. Preserve the existing working package and all owner backups unchanged.

Future restoration requires separate explicit owner authorization and independently satisfied installed-layout, image, security and ROM recovery prerequisites. Stop on any discrepancy. This stage performs no hardware access or physical recovery verification. Application rollback does not promise transactional restoration of settings or files; the randomization/jitter change adds no settings schema or storage changes.

After separate owner authorization, the existing bound launcher's future command shape is:

```bash
bash rollback-macos.sh --port OWNER_CONFIRMED_SERIAL_PORT
```

This is a review example, not an instruction to perform recovery now. No rollback command is executed against hardware during development.
