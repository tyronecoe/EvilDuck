# Review-only application package — no installation authorization

The proposed candidate uses the approved archive-based protected Arduino ESP32 core 3.3.0/ESP32-S3 profile, 16 MiB flash, PSRAM disabled and unchanged USB-OTG/TinyUSB/CDC and partition table. This is an application-only candidate, not a full-chip migration or format package. Keep the working installed application and all previous packages untouched.

Before any future owner-authorized installation: verify the public ZIP checksum, its bound preflight/installer/support hashes and source identity; require independently read device/partition/security prerequisites and exact existing 16 MiB layout. The expected table SHA-256 is `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`. The partition geometry remains unchanged:

| Partition | Offset | Size |
|---|---:|---:|
| NVS | `0x9000` | `0x5000` |
| OTA data | `0xE000` | `0x2000` |
| App0 | `0x10000` | `0x740000` |
| App1 | `0x750000` | `0x740000` |
| SPIFFS | `0xE90000` | `0x160000` |
| Coredump | `0xFF0000` | `0x10000` |

Mismatch is a stop condition; this stage does not authorize migration, partition replacement, erase, formatting or OTA.

Package preflight without installed-layout evidence must not output an executable write plan. Installer operations remain separately owner-authorized; no serial device or real esptool execution was used in offline tests. The package includes a byte-verified rollback to the current lock-feedback application, not the older keyboard-control release. See `ROLLBACK-MAC.md`.

Keep autorun off and stored scripts unchanged; preparation or installation must never execute them automatically. Only after a separate review and explicit owner approval may a controlled installation and acceptance trial occur. No recovery bypass, USB identity change, global toolchain patch or dynamic source download is needed. This package is not evidence that new firmware booted on hardware.
