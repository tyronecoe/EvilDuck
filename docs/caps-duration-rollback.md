# Deliberate rollback to the currently installed owner baseline

Exact application:2c657f0c74f1d12c88aa1e6fa6daf5cc76de36e8e68bc41a325f39b19c9045a7,
1,386,176bytes, buildId LED-FEEDBACK-BOUNDARY-20261018-v1. This is not573a8671,
c20dc399 or de24. Owner reported the installation verification and matching boot ID;
Codex has not independently read the current board. Original backups stay untouched.

If separately authorized, with a fresh explicitly determined ROM port and the
reviewed package directory as current directory:

```bash
bash rollback-macos.sh --port /dev/cu.CURRENT_ROM_PORT
```

The wrapper cannot be overridden into install. It repeats the same chip/security,
layout/OTA, NEW private full backup, typed ROLLBACK and repeat revalidation gates.
Only the two application slots are written. Both receive separate independent
comparisons; no automatic reset, boot, retry or nonapplication modification occurs.
If checks disagree or a write/verification fails, stay in ROM mode and stop for
review. No claim that an interrupted write preserves a bootable app is made.
Keep the prior package and backup separately accessible before any owner operation.
