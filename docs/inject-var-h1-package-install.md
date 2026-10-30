# High Sierra H1 installation preparation

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING.** The steps that access a board or write flash below are a future owner-operated procedure requiring separate approval. Codex has performed no board access, installation, boot, HID output or physical test in preparing this package.

## 1. Offline package review — safe first command

Unpack into a new directory, preserve the original ZIP, and open Terminal in that directory. Do not unpack over an older release. Verify the published ZIP SHA-256 with `shasum -a 256` before trusting its contents. Then run:

```bash
python3 preflight.py --directory .
```

This uses only package files; it does not enumerate USB, open a port or make network requests. Expect exit 0, `package_integrity: PASS`, `installed_metadata: NOT_SUPPLIED`, `plan_ready: false`, `hardware_access: false`, and `installation_authorized: false`. The latter fields are deliberate: package integrity does not authorize or prove device readiness. Stop on rejection. The offline checker also verifies both image checksums/appended digests, the expected table, support-file identities and bounded app-slot plans.

Compatible preparation interfaces are **macOS High Sierra 10.13.6**, **Bash 3.2**, **Python 3.8.10** and **esptool 4.12.0**. Python/esptool must already be available in the selected `python3`; this package does not download or install dependencies. `python3 --version` and `python3 -m esptool version` inspect the local tool versions without accessing the device. Linux package/mock results do not claim native High Sierra execution.

The candidate `application.bin` is 1,414,080 bytes, SHA-256 `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd`. Its expected dashboard build ID is `ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1`. Keep `rollback-application.bin`, the accepted 1,413,200-byte source/text v2 image with SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`, separately available. Neither file is a merged image or complete recovery set.

## 2. Before any separately authorized physical operation

Record the **actual** current dashboard build ID and any existing installer-recorded app hash; this package does not know what is installed or turn an installer hash into a physical readback. Preserve existing backups and packages unchanged. Verify ROM download access and recovery readiness using the owner’s established board procedure. Compatible stock firmware remains owner-confirmed available externally; its availability is not a claimed physical recovery test.

Before entering ROM mode, confirm the existing authenticated dashboard reports autorun **disabled**. The actual firmware Home page has an **Autorun** card whose current-state display says `disabled`; authenticated `/status` exposes `autorunEnabled: false`. A screenshot or sanitized field capture may record this without publishing credentials, SSID, script names or raw status bodies. If autorun is enabled or cannot be confirmed, stop. The package never changes it. A separately deliberate owner settings action through the existing **Autorun** input and **Save** control (empty value disables it), followed by re-verification, is distinct from installation; no reset or automatic settings write is proposed.

Close other serial clients before the device check. After every reconnect or mode change, rediscover and verify the current port rather than reuse an old suffix:

```bash
ls /dev/cu.usbmodem*
```

This enumeration and all remaining commands belong to the later separately approved physical procedure. Replace `/dev/cu.usbmodemCURRENT` with the verified current port; do not run the placeholder literally.

## 3. Future read-only device check — separate approval required

```bash
bash install-macos.sh --action check --port /dev/cu.usbmodemCURRENT
```

The default launcher action is also `check`, but requires a real port and reads hardware. It is not an offline command. The check uses esptool `--before no_reset --after no_reset --no-stub` at 115200 baud; ROM entry is owner-controlled. It checks ESP32-S3, 16 MB flash, expected chip ID, disabled Secure Boot/flash encryption and zero boot crypt count. It reads the installed table and OTA metadata into a new private Desktop evidence folder. Do not upload that folder or existing backups.

The supported table must match exactly:

| Partition | Offset | Size |
|---|---:|---:|
| NVS | 0x9000 | 0x5000 |
| OTA data | 0xE000 | 0x2000 |
| App0 | 0x10000 | 0x740000 |
| App1 | 0x750000 | 0x740000 |
| SPIFFS | 0xE90000 | 0x160000 |
| Coredump | 0xFF0000 | 0x10000 |

No partition may be encrypted or read-only in this writable experimental application profile. Expected 3,072-byte table SHA-256 is `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`; a 4,096-byte read also requires the reviewed erased trailer. OTA metadata must match the narrowly reviewed app0 initializer, SHA-256 `f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0`. This is not a general active-slot decoder. Any other valid-looking table, active-slot state or OTA history is **unsupported pending separate review**. Do not rewrite metadata, bypass a refusal or infer readiness from old files.

## 4. Future deliberate application installation — separate approval required

Only after approval and a successful current device check:

```bash
bash install-macos.sh --action install --port /dev/cu.usbmodemCURRENT
```

Before any write the installer repeats validation, creates a **new private full-flash backup** on the Desktop, records its size/hash and checks that its table/OTA bytes agree with the just-read metadata. It does not modify or replace existing backup files. Keep adequate free disk space and preserve the newly printed evidence location. The installer prints its scoped plan and requires typing `INSTALL`. It then rechecks chip identity, fresh table/OTA metadata and image identity before writing the same candidate to **both** app slots and comparing both written regions.

Only image-rounded application sectors are programmed: candidate ranges are `[0x10000, 0x16A000)` and `[0x750000, 0x8AA000)`. The installer calculates and independently checks these ranges. Bootloader, partition table, NVS, OTA data, SPIFFS and coredump are outside the write plan. Programming necessarily erases the affected app sectors; there is no separate erase-flash/erase-region, format, NVS reset, forced write or partition repair. Preserving data outside these ranges does not prove that the later running application will never write settings/storage.

No automatic reset, reboot, retry, upload, script Start or HID action occurs. After comparisons, the installer reports `boot_tested: false`. A deliberate exit from ROM/application boot and the acceptance sheet require their own approval. If a write or comparison fails, stay in ROM, preserve output and evidence, and stop; use **ROLLBACK-MAC.md** only as a separately deliberate recovery action. Do not automatically replay an interrupted operation.
