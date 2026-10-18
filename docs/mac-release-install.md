# Caps/queue review candidate — Mac installation

This package prepares a deliberate **application-only ROM update**. Codex has not
accessed the board or authorized an installation. Caps Lock output and keyboard
LED feedback remain **physically unverified**. This is a diagnostics-first
candidate, not a confirmed physical Caps Lock fix. HOLD/RELEASE remain rejected
by this Route B composition. Do not repeat the unsupported long-hold test.

1. Keep EvilDuck unplugged while checking the download. Save
   `evilduck-caps-queue-macos-install-v1.zip` in Downloads. Compare both results
   with the exact published size/SHA-256 in the release reply and
   `docs/mac-release-integrity.json`:

```bash
cd "$HOME/Downloads" && wc -c evilduck-caps-queue-macos-install-v1.zip && shasum -a 256 evilduck-caps-queue-macos-install-v1.zip
```

Stop if either differs. Extract into a NEW folder, never over an old package:

```bash
DUCK_PACKAGE=$(mktemp -d "$HOME/Desktop/evilduck-caps.XXXXXX") && unzip "$HOME/Downloads/evilduck-caps-queue-macos-install-v1.zip" -d "$DUCK_PACKAGE" && cd "$DUCK_PACKAGE" && python3 preflight.py --directory .
```

Expected: package_integrity PASS, plan_ready false, empty selected_write_ranges.
Do not add files inside this immutable package directory. Its manifest is an
unsigned integrity inventory, not an authenticated signature.

2. Check the already installed tools:

```bash
python3 --version && python3 -m esptool version
```

Require **Python 3.8+ and esptool 4.12.0**. Python 3.8.10 is supported. No Arduino,
compiler, Homebrew, Xcode, sudo, OS upgrade or network installation is needed.
If the versions do not match, stop and report them. The command parser was
verified on Linux; native macOS 10.13.6 serial execution remains owner-local.

3. Close serial monitors, clients and payload tools. Use a stable data cable and
power. Discover the **current ROM port**, not a remembered application port.
List before connection and again after entering ROM download mode using the
board's already identified BOOT and RESET controls (hold BOOT, pulse RESET,
release BOOT). Do not guess GPIO wiring or use a drag-and-drop disk.

```bash
ls /dev/cu.*
```

The changed `/dev/cu.*` character device is the candidate port. If ambiguous,
stop. Substitute its entire freshly observed name below; the literal example
will be rejected. Running the launcher without an install action is read-only:

```bash
bash install-macos.sh --port /dev/cu.REPLACE_WITH_FRESH_ROM_PORT
```

Expected: READ_ONLY_CHECK_PASS and writes 0. The helper checks exact tool version,
ESP32-S3, 16 MB flash, disabled Secure Boot/encryption and zero crypt counter. It
freshly reads partition and OTA sectors into a new private Desktop evidence
folder. It accepts only the reviewed six-partition layout and exact app0 OTA
initializer. A different valid OTA state requires separate review; do not change
OTA metadata or flags to force a pass. Port and chip identity are observations,
not cryptographic device authentication.

4. **Only after separate owner review and authorization to install**, in the same
fresh ROM session and extracted package directory, use:

```bash
bash install-macos.sh --action install --port /dev/cu.REPLACE_WITH_FRESH_ROM_PORT
```

This makes a new private complete 16 MiB backup before asking you to type
**INSTALL**. Keep that folder private; it may contain credentials. Never upload
it. Existing backups are not opened or overwritten. Read the exact two app
write/rounded erase ranges in the plan. The helper identifies the chip again,
rereads table/OTA, and revalidates package/image before writing. Changing ports,
reconnecting, resetting or another writer invalidates earlier observations: start
a fresh invocation. Do not run two helpers concurrently.

Only application.bin is written at **0x10000 and 0x750000**; each partition is
0x740000 bytes. Each write erases only its image-rounded sectors. No separate
erase command, full-chip image, bootloader, partition table, NVS, OTA, SPIFFS or
coredump write exists in this plan. Embedded web assets require no filesystem
upload. Firmware settings and scripts are retained by this app-only method;
normal SDK/settings behavior after a later boot is not byte-level NVS immutability.
Autorun remains disabled by the controlled profile.

The helper explicitly verifies each slot and reports
BOTH_APPLICATION_COMPARISONS_PASS only if both comparisons succeed. It never
reboots the board. This is not an atomic two-slot transaction or power-loss
immunity. If interrupted or any command fails, **stay in ROM**, retain the error
and private backup, and follow ROLLBACK-MAC.md after deliberate review. No
automatic rollback, retry, boot or payload execution is performed.

5. After comparisons pass, review the report before any separately authorized
manual application boot. First confirm idle/autorun-off state. Later, under
supervision with a blank TextEdit document, perform one explicitly requested Run
per harmless test: basic literal text and correlated completion; Caps tap and
observed text; callback counter changes; compact STOP; disposable SD deletion.
Do not infer host key release from local cleanup submission. If Caps is unclear,
record request/status/counters once rather than repeatedly running scripts.
Pause/Resume is excluded. No host helper is part of this installation path.
Only after raw Caps **and Num** feedback are established on the chosen host may
a separately reviewed finite visible 17-byte `EVILDUCK TEST 123` RAM-only roundtrip
be considered. Missing Num feedback can make that transport unsupported.
