# Randomization/jitter application package — review only

Candidate: `ROUTEB-RANDOMIZATION-JITTER-v1`. This is an application-only review package built with the approved isolated archive-feedback Arduino ESP32 3.3.0 profile: ESP32-S3, 16 MiB flash, PSRAM disabled and unchanged USB-OTG/TinyUSB/CDC, flash/CPU settings and partition geometry. No installation is authorized by this document.

Before a future separately authorized installation, verify the public ZIP hash, manifest/support bindings, candidate source and application identities, exact installed layout and existing security/ROM recovery prerequisites. Expected partition table SHA-256: `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

| Partition | Offset | Size |
|---|---:|---:|
| NVS | `0x9000` | `0x5000` |
| OTA data | `0xE000` | `0x2000` |
| App0 | `0x10000` | `0x740000` |
| App1 | `0x750000` | `0x740000` |
| SPIFFS | `0xE90000` | `0x160000` |
| Coredump | `0xFF0000` | `0x10000` |

Stop on any mismatch. This package does not authorize partition replacement, migration, erase, formatting or OTA. The approved application-only plans must exclude bootloader, table, NVS, OTA metadata, SPIFFS and coredump. Without required installed-layout evidence, offline preflight must not supply an executable write plan. No serial device is opened by the offline checks.

Exact rollback is the accepted random-uppercase application, **1,410,016 bytes**, SHA-256 `2cdb3e182dbbc3f2f2be21154cc49516e74337ed5c0c52a75aa772d1ef8eb098`. Keep that working package and private backups untouched. Read `ROLLBACK-MAC.md` and `OWNER-CHECK.md`.

The **new Route B randomization/jitter behavior is software-tested only**. Read `OWNER-CHECK.md` before considering installation.

The package retains High Sierra 10.13.6, Bash 3.2, Python 3.8 and esptool 4.12 interfaces. Native Mac/USB/install behavior is not established by Linux packaging tests. After a separate explicit owner authorization, the existing bound launcher's command shape is:

```bash
bash install-macos.sh --action install --port OWNER_CONFIRMED_SERIAL_PORT
```

This is a review example, not authorization to run it now. It must retain identity, layout, image and security checks and its explicit owner confirmation. Do not add force, erase, format or partition-write options. Keep autorun disabled; preparation and installation must not run stored scripts automatically.
