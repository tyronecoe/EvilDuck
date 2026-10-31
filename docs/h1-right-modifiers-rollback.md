# Exact accepted v2 rollback for the right-modifier H1 candidate

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING.** Recovery commands below are prepared for a separately approved, owner-controlled operation; none has been executed by Codex.

`rollback-application.bin` is the exact accepted **ROUTEB-SOURCE-TEXT-PORTABILITY-v2** application: **1,413,200 bytes**, SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. Its bytes are copied from `application.bin` in the preserved public `evilduck-routeb-source-text-portability-macos-v2.zip`, not rebuilt and not confused with that ZIP’s older rollback member. The original ZIP has 2,395,166 bytes and SHA-256 `589c277b48838777a9333304e29ba7c1052a0a022558fa5f2bf0a1ffe7d2f1d0`. Source revision is `71a62ea1bd775bc260052d099b5784b06ba3fc12`; release revision is `789815a70544e0b8f3967f8ab68d9f4f1f4e5f62`. The separate rollback build receipt is included.

First run the package’s offline checks from the unpacked directory:

```bash
python3 preflight.py --directory . --image rollback
```

This verifies files, not the board. After separate approval, confirmed ROM access and rediscovery of the correct current port, the existing deliberate interface is:

```bash
bash rollback-macos.sh --port /dev/cu.usbmodemCURRENT
```

The wrapper cannot be redirected to another action. It uses the same fail-closed chip/security/table/OTA checks as installation, creates a new private prewrite full-flash backup, requires typing `ROLLBACK`, reidentifies the chip and metadata, and writes/verifies the exact rollback application in both app slots. Image-rounded rollback ranges are `[0x10000, 0x16A000)` and `[0x750000, 0x8AA000)`; the installer derives and validates them. It does not write the bootloader, partition table, OTA data, NVS, SPIFFS or coredump. It does not reboot, repair metadata, format, reset settings or retry automatically.

If unsupported table/OTA/security state is reported, stop for review rather than changing metadata to satisfy the installer. If programming/comparison fails, stay in ROM and preserve the new evidence. A full recovery procedure for incompatible bootloader/layout/security state is outside this app-only package; the existence of these application bytes is not proof of physical ROM/recovery readiness.

Rollback restores application code, not a previous settings/filesystem snapshot. The experimental H1, configurable lock-wait and new right-side source modifier features will no longer be present. Existing owner data and backups remain untouched by this preparation task. Autorun must have been separately confirmed disabled before the first experiment; do not assume a firmware rollback resets it. Boot and any subsequent payload execution require separate approval.
