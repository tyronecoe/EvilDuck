# Stage 26 partition and artifact compatibility

REVIEW ONLY — NOT AUTHORIZED FOR FLASHING

Original firmware: **OWNER CONFIRMED — AVAILABLE EXTERNALLY**. Availability is not a blocker.
Physical recovery has not been newly tested. No original firmware was searched for, requested or downloaded.

## Final proposed production table

```csv
# EvilDuck S3: verified 16 MiB hardware ONLY. See docs/s3-flash-migration.md.
# Name,   Type, SubType, Offset,   Size,     Flags
nvs,      data, nvs,     0x9000,   0x5000,
otadata,  data, ota,     0xE000,   0x2000,
app0,     app,  ota_0,   0x10000,  0x740000,
app1,     app,  ota_1,   0x750000, 0x740000,
spiffs,   data, spiffs,  0xE90000, 0x160000,
coredump, data, coredump,0xFF0000, 0x10000,
```

The installed owner-recorded table remains the old 4 MiB layout: app0 0x10000/0x140000,
app1 0x150000/0x140000, SPIFFS 0x290000/0x170000; same NVS/OTA metadata locations and no coredump.
Nothing establishes that the proposed table is already installed. Production flags remain writable/zero.
The separate experimental readonly table is excluded. App offsets are 64 KiB-aligned; data offsets/sizes
are sector-aligned. Final end is exactly 0x1000000. Both OTA slots are 7602176 bytes.

## Required public image review set

| Role | File | Offset | Bytes | Sector erase footprint [start,end) | SHA-256 |
|---|---|---:|---:|---|---|
| bootloader | bootloader.bin | 0x0 | 20256 | 0x0..0x5000 | `95b966ad240a05bf8a804cd4519eebac5271b662e51417668da488652b7354bf` |
| partitions | partitions.bin | 0x8000 | 3072 | 0x8000..0x9000 | `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e` |
| otadata | ota-app0.bin | 0xE000 | 8192 | 0xE000..0x10000 | `f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0` |
| app0 | controlled-stage26.bin | 0x10000 | 1329760 | 0x10000..0x155000 | `a2087f560f60b03990f8133591dffa218f0414e15dc87530c215f8949a4758c4` |
| app1 | controlled-stage26.bin | 0x750000 | 1329760 | 0x750000..0x895000 | `a2087f560f60b03990f8133591dffa218f0414e15dc87530c215f8949a4758c4` |
| spiffs | empty-spiffs.bin | 0xE90000 | 1441792 | 0xE90000..0xFF0000 | `f19dc5da480ce1eff46d82376f45a8c1c425148016f9a8c34acef7a330552233` |
| coredump | coredump-erased.bin | 0xFF0000 | 65536 | 0xFF0000..0x1000000 | `71189f7fb6aed638640078fba3a35fda6c39c8962e74dcc75935aac948da9063` |

Fallback only: `deployment-safe-stage26.bin`, 1066128 bytes, SHA-256 `93160306c9668e59e7e8f03577c498b5ea43ef9e4c71b0b0686116889c793127`. It is not in the initial write set.

Private fresh NVS: 20480 bytes, offset 0x9000, footprint [0x9000,0xE000). Its SHA-256 must be
generated locally from explicit owner credentials; no private NVS or fabricated owner hash is published.

## Actual image checks

Pinned Arduino3.3.0 partition tooling checked canonical MD5, exact table bytes and zero flags.
Both compiled bootloader/application headers have ESP image magic 0xE9, chip ID9 (ESP32-S3),
flash-size code4 (16 MiB) and frequency nibble15 (80MHz). **Actual flash mode byte2 is DIO**,
despite the retained QIO80 build selection; no claim that the header says QIO. This is the existing
Arduino image generation behavior and a quad-compatible mode. XOR segment checksum/appended SHA,
standard S3 IRAM entry addresses and revision-v0.2 bounds are verified. The ELF is converted back
to the exact application bytes by the mandatory build verifier. Bootloader is at0; table at0x8000.
OTA initializer has sequence1, valid CRC and second invalid record: deterministic app0 selection.
This is not evidence of host USB, physical boot or health-based rollback.

Controlled BIN1329760 exceeds the old 1310720-byte slot by19040 bytes. App-only OTA into the
installed layout is unsuitable. Same controlled image is planned at both proposed slots.
Fallback deployment-safe BIN fits the new layout and is quiescent; do not infer old-layout
compatibility just because its application is smaller. Its reviewed table remains the proposed layout.

SPIFFS is0x160000/block4096/page256; actual pinned mkspiffs0.2.3 packing/unpacking produces zero files.
The new coredump region has a0x10000-byte all-FF initialization image. Sector erasure alone could
establish the same state, but the review set chooses an explicit image for a single checked write plan.
No old coredump exists to preserve. Old SPIFFS contents are optional and are never raw-relocated.

Trust boundary: SHA-256 is an integrity check against this trusted checkout, not a digital signature.
Changing both the trusted pin and arbitrary files is outside that trust boundary. A runtime application
layout check occurs after Arduino/SDK initialization; an installed table must be verified before boot.
