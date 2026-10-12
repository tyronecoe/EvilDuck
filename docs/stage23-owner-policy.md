# Stage 23 owner-authorized recovery policy addendum

This supersedes the **future acceptance criteria** in older preservation-oriented
readiness reports. Historical reports and evidence remain unchanged.

The owner states the original firmware was essentially stock, and exact preservation
of the old installation, NVS values, settings and scripts is no longer required.
Losing that data is acceptable during an **eventually separately authorized** migration.
A verified compatible stock EvilDuck S3 recovery installation is an acceptable recovery
outcome; the primary goal remains a functional upgraded firmware.

The original full-flash, partition-table and filesystem backups are **optional recovery
resources**, not mandatory byte-preservation gates. Do not delete, overwrite or modify
them. Owner-reported local verification remains recorded: three hashes/sizes matched,
full private preflight PASS, SPIFFS roundtrip PASS, NVS compatible-within-verified-checks,
zero findings, migration authorized False. No private binary was supplied to Codex.

Still mandatory before physical deployment:

- A verified compatible recovery image or reproducible build, including its bootloader
  and partition compatibility. Merely finding a stock repository is insufficient.
- Confirmed owner-controlled ROM download/recovery access and suitable cable/power/port.
- Exact chip/flash profile, image identities, offsets, partition geometry and OTA policy.
- Controlled writes confined to explicitly approved ranges; no accidental full-chip
  erase, filesystem formatting, settings reset or payload execution.
- A reviewed recovery procedure and explicit owner authorization for flashing,
  erasing, formatting, application boot or OTA.

The experimental readonly candidate remains valuable and is retained. Its current
protection contract/tests are not weakened because old data may be discarded later.
Normal/safe/candidate behavior, old migration validators and schemas are unchanged.
Existing preservation-oriented tools still implement their historical strict workflow;
a future recovery-first plan must be separately reviewed rather than silently bypassing
those validators. Any deliberate NVS/filesystem initialization would need its own
reviewed ranges and authorization. No such operation or command is introduced here.

**Physical migration, application boot and OTA remain NO-GO.** This addendum is not
physical authorization. No backup is deleted or altered, and Stage24 is not started.
