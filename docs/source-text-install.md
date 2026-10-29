# Source/text portability application package — review only

Candidate: `ROUTEB-SOURCE-TEXT-PORTABILITY-v1`. Package: `evilduck-routeb-source-text-macos-v1`. This single application-only Mac candidate uses the approved isolated archive-based Arduino ESP32 core3.3.0 profile: ESP32-S3,16MiB flash, PSRAM disabled, existing USB-OTG/TinyUSB/CDC and CPU/flash settings. No installation is authorized by this document.

Before a future separately authorized installation, verify ZIP/member hashes, release-bound helpers, source/application identity, installed partition/OTA metadata, chip/security identity and ROM recovery prerequisites. Expected partition-table SHA-256 remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

| Partition | Offset | Size |
|---|---:|---:|
| NVS |0x9000|0x5000|
| OTA data |0xE000|0x2000|
| App0 |0x10000|0x740000|
| App1 |0x750000|0x740000|
| SPIFFS |0xE90000|0x160000|
| Coredump |0xFF0000|0x10000|

Stop on mismatch. App-only plans exclude bootloader, partition table, NVS, OTA metadata, SPIFFS and coredump. No migration, formatting, erase, forced metadata adjustment or OTA is approved. Missing installed metadata must prevent an executable write plan. Offline package checks open no serial device.

Exact rollback is accepted `ROUTEB-PAYLOAD-RESTART-v1`: **1,412,688 bytes**, SHA-256 `1d4ea6394306885b832619adb3436eaeeccc0a67ce8b73e1f20dd0f9c7d0a060`. Read `ROLLBACK-MAC.md` and `OWNER-CHECK.md`. Keep previous working packages and private backups untouched.

The **new Route B source/text portability behavior is software-tested only** once the required receipts pass. Physical acceptance remains pending. Preserve High Sierra10.13.6, Bash3.2, Python3.8 and esptool4.12 interfaces; Linux checks do not establish native Mac or physical USB behavior.

After a separate explicit owner authorization, the bound launcher's future command shape is:

```bash
bash install-macos.sh --action install --port OWNER_CONFIRMED_SERIAL_PORT
```

This is a review example, not authorization to run it now. Preserve all identity/layout/security/image gates and explicit owner confirmation. Do not add force, erase, format or partition-write options. Keep autorun disabled; do not execute stored scripts automatically.
