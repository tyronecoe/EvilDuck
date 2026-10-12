# Provisional Stage 17 artifacts — NOT authorized for flashing

Six non-owner binary files plus artifact-inventory.json are provided for review.
The initial proposed write set uses safe-app.bin in both new OTA slots. normal-app.bin
is deliberately excluded from initial migration and needs a separate normal-operation
review. No padded merged image, physical writer, original backup or new SPIFFS image
is included. The filesystem is externally supplied and must match the recorded hash.

These are software-only cloud build artifacts. All sizes/hashes/offsets and required
sector ranges are in the manifest. Never write them into the original partition map.
No owner evidence was verified here. Safe-start does not fix Arduino's pre-setup NVS
error-triggered erase. Migration/application boot remains NO-GO pending the documented
backup, dependency, NVS, recovery, autorun and individual authorization gates.

[Report](../../docs/stage17-report.md), [reproduction](../../docs/stage17-reproduction.md),
[owner checklist](../../docs/stage17-owner-checklist.md). Hardware measurements and host
compatibility remain unverified. No next development stage is started automatically.
