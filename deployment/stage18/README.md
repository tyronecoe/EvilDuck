# Stage 18 provisional protected-NVS artifacts

Non-owner binaries and inventory only. Both initial proposed application writes use
safe-app.bin; normal-app.bin is not an initial migration image. No owner backup,
external approved SPIFFS, padded merged full-flash image or physical writer is included.
Stage17 artifacts remain unchanged/historical.

The known Arduino whole-partition recovery erase is disabled and errors latch a
quiescent application. SDK-internal NVS page recovery may still mutate data. This is
not a read-only initialization guarantee, owner-evidence verification or authorization
to boot/migrate. Review [report](../../docs/stage18-report.md),
[readiness](../../docs/stage18-hardware-readiness.md) and
[reproduction](../../docs/stage18-reproduction.md). Original partition compatibility,
backups, NVS readability/recovery policy and individual owner approval remain gates.
