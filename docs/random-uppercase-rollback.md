# Exact lowercase rollback — review only

The rollback application is accepted `ROUTEB-RANDOM-LOWER-20261024-v1`, **1,409,952 bytes**, SHA-256 `0a4faafeba059c9578cd938e260eedcf03be2c34b53731e6bbfc5178799fd774`. Its source public archive is untouched `evilduck-routeb-random-lowercase-macos-v1.zip`, SHA-256 `b2c93548e5239e79fef5ffac09cb5231f5edc2873cc0b7774832fe426aecbef5`. Codex verifies those public bytes; it does not assume an independent hardware readback.

Package assembly must verify the exact application size/hash, image identity, table geometry, source receipts and bound installer. The older preprocessing and lock-feedback applications are not this candidate's rollback target. Preserve the existing working package and all owner backups unchanged.

Future restoration requires separate explicit owner authorization and independently satisfied installed-layout, image, security and ROM recovery prerequisites. Stop on any discrepancy. This stage performs no hardware access or physical recovery verification. Application rollback does not promise transactional restoration of settings or files; the uppercase change adds no settings schema or storage changes.

After separate owner authorization, the existing bound launcher's future command shape is:

```bash
bash rollback-macos.sh --port OWNER_CONFIRMED_SERIAL_PORT
```

This is a review example, not an instruction to perform recovery now. No rollback command is executed against hardware during development.
