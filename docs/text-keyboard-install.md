# Text and keyboard utilities application package — review only

Candidate: `ROUTEB-TEXT-KEYBOARD-v1`. This is a single application-only Mac review package using the approved isolated archive-based Arduino ESP32 core3.3.0 profile: ESP32-S3,16MiB flash, PSRAM disabled, existing USB-OTG/TinyUSB/CDC and CPU/flash configuration. No installation is authorized by this document.

Before a future separately authorized installation, verify the ZIP/member hashes, bound helpers, source and application identities, installed partition/OTA metadata, chip/security identity and ROM recovery prerequisites. Expected partition-table SHA-256: `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

| Partition | Offset | Size |
|---|---:|---:|
| NVS |0x9000|0x5000|
| OTA data |0xE000|0x2000|
| App0 |0x10000|0x740000|
| App1 |0x750000|0x740000|
| SPIFFS |0xE90000|0x160000|
| Coredump |0xFF0000|0x10000|

Stop on any mismatch. Application-only plans must exclude bootloader, partition table, NVS, OTA metadata, SPIFFS and coredump. No migration, format, erase, forced metadata adjustment or OTA is approved. Without the required installed metadata, offline preflight must not produce an executable write plan. No serial device is opened by offline package checks.

Exact rollback is accepted `ROUTEB-RANDOMIZATION-JITTER-v1`: **1,411,088 bytes**, SHA-256 `2e1d8345417c6f23a5df3d884db42dd2a0f9f305120ee494c56a58048e677496`. Read `ROLLBACK-MAC.md` and `OWNER-CHECK.md`. Keep prior working packages and private backups untouched.

The **new Route B text/keyboard utilities behavior is software-tested only** once the required receipts pass. Its physical acceptance is pending. The package preserves High Sierra10.13.6, Bash3.2, Python3.8 and esptool4.12 interfaces; Linux checks do not prove native Mac or USB behavior.

After a separate explicit owner authorization, the existing bound launcher's future command shape is:

```bash
bash install-macos.sh --action install --port OWNER_CONFIRMED_SERIAL_PORT
```

This is a review example, not authorization to run it now. Preserve identity/layout/security/image gates and explicit owner confirmation. Do not add force, erase, format or partition-write options. Keep autorun disabled and do not execute stored scripts automatically.
