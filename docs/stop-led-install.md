# STOP/LED installation — High Sierra owner guide

Use the **application-only ROM update** below. This is a prepared, conditional
procedure, not evidence that installation or native host tests have happened.
No hardware command in this guide was executed by Codex. Use a stable data cable
and power. Close serial monitors and other EvilDuck clients. Do not start payloads.
The embedded web assets need **no SPIFFS upload**. Do not use Arduino Upload,
UF2 drag-and-drop, an old migration image, or an OTA updater for this procedure.

## 1. Download and verify, with EvilDuck unplugged

Download **evilduck-stop-led-install-v1.zip** using the commit-pinned download
link in the publication reply. Save the actual ZIP to Downloads. The repository
also retains its package-specific size/hash in `docs/stop-led-install-integrity.json`.
Compare both outputs below with that publication receipt **before unzipping**:

```bash
cd "$HOME/Downloads" && wc -c evilduck-stop-led-install-v1.zip && shasum -a 256 evilduck-stop-led-install-v1.zip
```

Stop for any discrepancy. In Terminal, extract into a NEW directory (not over an
older package); keep this Terminal open because subsequent commands reuse variables:

```bash
DUCK_PACKAGE=$(mktemp -d "$HOME/Desktop/evilduck-stop-led.XXXXXX") && unzip "$HOME/Downloads/evilduck-stop-led-install-v1.zip" -d "$DUCK_PACKAGE" && cd "$DUCK_PACKAGE" && python3 preflight.py --directory .
```

Expected: `package_integrity: PASS`, `plan_ready: false`, no selected write ranges.
Package-only PASS is **not** permission or sufficient evidence to write. Do not add
files to the package folder; save owner evidence outside it. The manifest is an
unsigned integrity inventory, not a signature or proof of device authenticity.

Firmware source: `d18b7fddedaecef27be9fd7e486ad2d092a513c6`.
`application.bin`: **1,376,576 bytes**, SHA-256
`c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4`.
This is byte-identical to `downloads/evilduck-stop-led-review.bin`; no rebuild.

## 2. Tools and ROM port (read-only preparation)

Reuse the owner's existing **Python 3.8.10 / esptool 4.12.0**. Check:

```bash
python3 --version && python3 -m esptool version
```

Require Python 3.8+ and esptool **4.12.0** for these exact instructions. If absent
or different, stop and report the version; do not upgrade to the latest release
or install a new Arduino core to flash this binary. The verified 4.12.0 source
requires Python >=3.7; its CLI below was checked on Linux. High Sierra execution
and serial-driver compatibility remain owner-local checks, not a new claimed PASS.
No native compiler is required for installation. Native Windows/macOS sender
compilation is a separate, pending test.

List ports before connecting, then enter ESP32-S3 **ROM download mode**: hold the
board's already identified BOOT button, pulse RESET, release BOOT. Do not guess
GPIO wiring or use a drag-and-drop drive. List again:

```bash
ls /dev/cu.*
```

Identify the new ROM port by the before/after difference. It can differ from the
application port. Replace the entire example value, not with a remembered port:

```bash
DUCK_PORT='/dev/cu.REPLACE_WITH_OBSERVED_ROM_PORT'
duck_tool() { python3 -m esptool --chip esp32s3 --port "${DUCK_PORT:?Set actual ROM port}" --baud 115200 --before no_reset --after no_reset --no-stub "$@"; }
duck_tool flash_id && duck_tool get_security_info
```

These are read-only identification commands. They synchronize ROM and leave it
in download mode; no stub is uploaded. Require ESP32-S3, **16 MB detected flash**,
Secure Boot disabled, Flash Encryption disabled, SPI_BOOT_CRYPT_CNT=0. Check the
expected board identity against your own records. If output disagrees, is ambiguous,
or the port is unavailable, **stop**. Original stock firmware is owner-confirmed
available externally; locating it is not a prerequisite introduced here.

After personally reviewing those results, explicitly record the manual gate:

```bash
DUCK_IDENTITY_REVIEWED=YES
```

This variable records your review; it does not authenticate hardware automatically.

## 3. Fresh private backup and installed metadata (reads only)

Do this while still in ROM mode, in the SAME Terminal. This creates a new backup
directory, leaving all earlier backups untouched. Never upload it or put it in Git.

```bash
DUCK_BACKUP=$(mktemp -d "$HOME/Desktop/evilduck-before-stop-led.XXXXXX") && duck_tool read_flash 0x0 0x1000000 "$DUCK_BACKUP/current-flash.bin" && duck_tool read_flash 0x8000 0x1000 "$DUCK_BACKUP/current-partitions.bin" && duck_tool read_flash 0xE000 0x2000 "$DUCK_BACKUP/current-otadata.bin" && duck_tool read_flash 0x9000 0x5000 "$DUCK_BACKUP/current-nvs.bin" && wc -c "$DUCK_BACKUP/current-flash.bin" && shasum -a 256 "$DUCK_BACKUP/current-flash.bin" "$DUCK_BACKUP/current-nvs.bin"
```

Require every read to succeed and the full backup size to be **16,777,216 bytes**.
Record its newly observed hash privately; do not compare a current image to an
older firmware backup hash and expect equality. Keep the backup directory and
this package. A new filename/directory is required for a later attempt; do not
reuse these names to overwrite existing evidence.

Now perform the mandatory preflight:

```bash
python3 preflight.py --directory . --installed-table "$DUCK_BACKUP/current-partitions.bin" --installed-otadata "$DUCK_BACKUP/current-otadata.bin" --require-installed
```

Require exit 0, `plan_ready: true`, and exactly two selected application ranges.
Missing metadata exits nonzero when `--require-installed` is used. Any rejection
means **no write**. Supply only the reason code and nonprivate identification
output for review; never send NVS or the full backup.

Supported installed layout (NOT the old stock 4 MiB layout):

| Region | Offset | Size |
|---|---:|---:|
| NVS | 0x9000 | 0x5000 |
| OTA metadata | 0xE000 | 0x2000 |
| app0 | 0x10000 | 0x740000 |
| app1 | 0x750000 | 0x740000 |
| SPIFFS | 0xE90000 | 0x160000 |
| coredump | 0xFF0000 | 0x10000 |

The 3,072-byte table SHA is
`b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`;
the remainder of its 4,096-byte sector must be erased padding. This narrow
workflow supports only the previously reviewed **app0 initializer OTA state**,
8,192 bytes, SHA
`f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0`.
Other valid OTA records also require separate review; this is not a generic OTA
decoder. Do not erase or replace OTA metadata to force acceptance. The check
uses supplied files, not authenticated or live device metadata. Repeat fresh
reads after any intervening boot, other writer, port change or reconnect.

## 4. Actual future write — only after every preceding gate passes

**This block modifies flash.** It is provided for the owner's deliberate use,
not run by Codex. Reconfirm no script is active and the board remains in ROM mode.
The same reviewed app is written to BOTH slots: no active-slot guess, OTA change,
bootloader change or partition migration. The supported supplied OTA state selects
app0. The backup and chip/security review above are mandatory independent gates.

```bash
if [ "${DUCK_IDENTITY_REVIEWED:-}" != YES ]; then
  echo 'STOP: chip/flash/security review not confirmed'
else
  python3 preflight.py --directory . --installed-table "${DUCK_BACKUP:?Missing fresh backup}/current-partitions.bin" --installed-otadata "$DUCK_BACKUP/current-otadata.bin" --require-installed &&
  test "$(wc -c < "$DUCK_BACKUP/current-flash.bin" | tr -d ' ')" = 16777216 &&
  duck_tool write_flash --flash_mode keep --flash_freq keep --flash_size keep --no-compress 0x10000 application.bin 0x750000 application.bin &&
  duck_tool verify_flash --flash_mode keep --flash_freq keep --flash_size keep 0x10000 application.bin 0x750000 application.bin
fi
```

Every `&&` is intentional; never run the write after a failed prerequisite.
No force/encryption bypass option is permitted. NOR programming intrinsically
erases the affected application sectors; there is **no separate erase command**.
The exact byte ranges are [0x10000,0x160140) and [0x750000,0x8A0140).
Sector erase footprints are [0x10000,0x161000) and [0x750000,0x8A1000),
each 0x151000 bytes. They fit wholly within the two 0x740000 slots and cannot
touch bootloader, table, NVS, OTA metadata, SPIFFS or coredump. Full-chip/slot
erasure, formatting, merged images and filesystem upload are excluded.
Header parameters are kept unchanged: application ESP32-S3/DIO/80MHz/16MiB;
the existing compatible QIO-profile bootloader is not rewritten.

Require both writes AND both explicit verifications to succeed. On any disconnect,
partial write or verification failure: **do not boot**. Retain ROM mode, check power
and cable, rediscover the actual port, and obtain fresh read-only metadata in a
NEW backup directory before a reviewed retry or the rollback below. Never erase
all flash as troubleshooting. If no port appears, check the known data cable,
power and manually entered BOOT/RESET sequence; do not guess a port or driver.

Optional read-only byte-for-byte checks before boot (new filenames only):

```bash
duck_tool read_flash 0x10000 0x150140 "$DUCK_BACKUP/after-app0.bin" && duck_tool read_flash 0x750000 0x150140 "$DUCK_BACKUP/after-app1.bin" && cmp application.bin "$DUCK_BACKUP/after-app0.bin" && cmp application.bin "$DUCK_BACKUP/after-app1.bin" && duck_tool read_flash 0x9000 0x5000 "$DUCK_BACKUP/after-nvs.bin" && cmp "$DUCK_BACKUP/current-nvs.bin" "$DUCK_BACKUP/after-nvs.bin"
```

Both app hashes must match the application SHA above. Unchanged NVS before first
boot does not guarantee SDK/application runtime immutability after boot.

## 5. Normal reboot and deliberately supervised acceptance

Only after verification succeeds, release BOOT and pulse RESET normally. The
application CDC port may re-enumerate. Reconnect to the previously configured
EvilDuck Wi-Fi and use your existing web address and credentials; none are in
this public package. Log in; use Chrome Cmd-Shift-R, or fully reload the iPhone
page, for the embedded UI. Do not format storage or reset settings for a login
failure. Confirm saved settings and script inventory are unchanged. Autorun is
kept disabled by this controlled-start candidate; do not enable it.

Firmware identity is established by the ROM readback hash, not a browser label.
If boot/login/storage fails, retain diagnostics and use the app-only rollback;
no automatic migration/repair is part of this package.

Supervised checks, all **NOT TESTED on hardware for this STOP/LED build**:

1. On Mac and iPhone confirm visible **STOP script**. With a harmless script
   `DELAY 10000` followed by `STRING STOP-TEST`, explicitly start Route B with a
   blank editor focused, then cancel well before ten seconds. Expect no text.
   Request acceptance is not cancellation completion: check idle/cancel reason
   and faults. Test actual modifier release separately; local clear submission
   is not proof the host received release. Do not infer that legacy Run uses Route B.
2. Inspect actual keyboard OUTPUT reports separately on Windows 11 and macOS
   10.13.6 by deliberately toggling Caps/Num. Missing Num feedback means the
   fixed-message method is unsupported on that setup, not a success.
3. Only after both outputs are observed, deliberately enable the finite LED
   receiver, then independently test **Stop receiving** and timeout. Test the
   fixed message `EVILDUCK TEST 123` only with the reviewed host sender in a
   separate session. Its tools are in `host_tests/led_return/`, not auto-launched
   or required by this installation ZIP. Native compilation remains pending.
   The packaging branch fixes independent Caps/Num cleanup and failure status;
   firmware provenance remains the reviewed d18b7fd commit. No payload capture,
   credentials or ordinary typing belongs in this diagnostic.
4. Mark Windows and Mac outcomes separately: observed reports, host API attempt,
   receiver integrity, host text and host release are distinct evidence.

## 6. Exact app-only rollback

The ZIP includes `rollback-application.bin`, previous shortcut candidate source
`5c19f0dacb25960bda36a97f4ff871937a3cc9e7`, **1,359,808 bytes**, SHA
`de241287b972c24e510d3e8d22d888a17f13d1e972142559ba3df19f6195b41d`.
Its earlier working package is retained at:
https://raw.githubusercontent.com/tyronecoe/EvilDuck/fb1c43c5de28cc9887368f9bd016be0b3fd04763/downloads/evilduck-shortcuts-5c19f0d-review.zip
(original ZIP SHA `466edeac41cf33182136d5b4d02809a1f641fff5c17ae79e1a8fd3f46b314e0f`).
Owner-reported earlier physical checks are not new Codex testing.

Return manually to ROM. Repeat Sections 2–3 with a **new** backup directory and
fresh actual port/metadata; do not reuse pre-boot files after running firmware.
Rollback has the SAME layout/OTA/chip/security gates. Then deliberately execute:

```bash
if [ "${DUCK_IDENTITY_REVIEWED:-}" != YES ]; then
  echo 'STOP: chip/flash/security review not confirmed'
else
  python3 preflight.py --directory . --installed-table "${DUCK_BACKUP:?Missing fresh backup}/current-partitions.bin" --installed-otadata "$DUCK_BACKUP/current-otadata.bin" --require-installed --image rollback &&
  test "$(wc -c < "$DUCK_BACKUP/current-flash.bin" | tr -d ' ')" = 16777216 &&
  duck_tool write_flash --flash_mode keep --flash_freq keep --flash_size keep --no-compress 0x10000 rollback-application.bin 0x750000 rollback-application.bin &&
  duck_tool verify_flash --flash_mode keep --flash_freq keep --flash_size keep 0x10000 rollback-application.bin 0x750000 rollback-application.bin
fi
```

Rollback byte ranges: [0x10000,0x15BFC0), [0x750000,0x89BFC0).
Erase footprints: [0x10000,0x15C000), [0x750000,0x89C000).
After both comparisons pass, reboot normally. This restores application bytes,
not an assertion that settings changed by later runtime are reversed. Any layout
or OTA mismatch is a stop-and-review condition, never an instruction to rewrite
data partitions. Keep original backups untouched and private.
