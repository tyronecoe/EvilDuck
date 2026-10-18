# Mac update — LED boundary diagnostic candidate

Software preparation only. Installation/boot require separate owner approval.
Use macOS10.13.6, Python3.8.10 (3.8+), esptool4.12.0. No Arduino compilation,
Homebrew, Xcode, sudo, driver installation or OS upgrade is needed. No executable
dependencies are downloaded by the helper. Native High Sierra serial execution
of this new helper remains owner-local, not established by Linux tests.

1. With EvilDuck unplugged, download evilduck-led-feedback-macos-install-v1.zip.
Compare BOTH byte count and SHA-256 with the published integrity receipt:

```bash
cd "$HOME/Downloads" && wc -c evilduck-led-feedback-macos-install-v1.zip && shasum -a 256 evilduck-led-feedback-macos-install-v1.zip
```

Stop on mismatch. Extract into a new folder and check the package offline:

```bash
DUCK_PACKAGE=$(mktemp -d "$HOME/Desktop/evilduck-led.XXXXXX") && unzip "$HOME/Downloads/evilduck-led-feedback-macos-install-v1.zip" -d "$DUCK_PACKAGE" && cd "$DUCK_PACKAGE" && python3 preflight.py --directory .
```

Expected package_integrity PASS, plan_ready false, no selected_write_ranges.
Keep the folder immutable; evidence/backups belong outside it. The manifest is
an unsigned integrity inventory, not cryptographic device authentication.

2. Check existing tools. Stop on a different version; do not install upgrades:

```bash
python3 --version && python3 -m esptool version
```

After separate approval for owner-local ROM checks, close serial clients. Use the
board's already identified BOOT/RESET controls and a stable data cable/power to
enter ROM mode. Compare ports before/after with `ls /dev/cu.*`. Do not guess a
remembered application port. Replace the entire placeholder below with the fresh
ROM character-device name. The default action ONLY reads:

```bash
bash install-macos.sh --port /dev/cu.REPLACE_WITH_FRESH_ROM_PORT
```

Expect numbered Step messages, then READ_ONLY_CHECK_PASS, writes0. The helper
checks exact esptool version, ESP32-S3/16MB, disabled security/zero crypt counter,
fresh partition table and exact reviewed app0 OTA initializer. Unknown metadata,
including a different valid OTA state, stops for review; do not rewrite OTA to
force acceptance. No package-only PASS grants write permission.

3. Only after separate owner authorization to write:

```bash
bash install-macos.sh --action install --port /dev/cu.REPLACE_WITH_FRESH_ROM_PORT
```

The helper creates a NEW private16MiB backup on Desktop before requesting typed
INSTALL. Existing backups are untouched. Read the exact two app ranges displayed
in the plan. It re-identifies the chip, rereads table/OTA, revalidates images and
package, writes ONLY the apps at0x10000 and0x750000 and explicitly compares each.
Its Step messages identify check/read/write/compare progress. Failure stops with
an error; no auto-retry or reset. Success is BOTH_APPLICATION_COMPARISONS_PASS,
boot_tested false, automatic_reboot false. This is not an atomic transaction or
proof of physical boot, USB delivery or key release. Never disconnect or run two
writers concurrently. New invocation required after reconnect/reset/another writer.

No bootloader/table/NVS/OTA/SPIFFS/coredump write, erase-all, formatting, migration
or filesystem upload is included. Current table must already match the reviewed
six-partition16MiB layout. All app writes and image-rounded erases fit within
0x740000 slots; nonapplication regions are excluded. Autorun remains disabled.
Normal writable SDK operation after a future boot does not promise NVS immutability.

If interrupted or comparison fails: stay in ROM, retain private backup/error,
and read ROLLBACK-MAC.md. Do not boot partial firmware, erase all, force metadata
or automatically restore a full-chip image. Read OWNER-CHECK.md only before a
separately authorized supervised boot/test; Caps/LED remain physically unverified.
No host sender runs in this installation path.
