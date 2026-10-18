# Mac installation preparation — not a released installer

The requested new `evilduck-caps-queue-macos-install-v1.zip` has **not** been created:
there is no new application verified under an accepted build profile. Do not install
these source files or reuse an old image checksum as the identity of the new fixes.
[The profile decision](mac-install-build-profile-proposal.md) is the exact remaining
software gate. No Mac firmware compilation, stock-firmware search or physical
flashing is requested to resolve it.

## Independent work now prepared and tested

`tests/mac_install/installer.py` is an **unbound installer engine** with memory-only
fault tests. `install-macos.sh` and `rollback-macos.sh` are separate Bash launchers.
All CLI actions, including explicit install and rollback, currently exit2 with
`RELEASE_NOT_BOUND` **before any device access**. There is no CLI flag to bypass
that release gate. It must remain unbound until a reviewed target build/package
supplies exact image/layout/integrity checks. No installation ZIP is published.

The tested engine is designed to:

1. Default to read-only check, validate package through the final release's strict
   checker, check esptool4.12.0, validate a freshly supplied `/dev/cu.*` port and
   identify ESP32-S3/16MB with disabled secure boot/encryption and crypt count0.
2. Create a NEW private evidence directory outside the immutable extracted package;
   read table/OTA from the board and require the release's reviewed layout/OTA
   policy before showing any application plan. No old port/session evidence input
   is accepted by its CLI. Prefix is ROM/no-stub/no-reset, never automatic reboot.
3. For an explicit install/rollback action, make a new full16MiB backup, check its
   size and agreement with separately read metadata, and save its hash privately.
   Existing backups are never overwritten or automatically restored.
4. Require the owner to type INSTALL or ROLLBACK after the readable plan. Recheck
   identity, table/OTA, package and image immediately before writes. Changed or
   ambiguous evidence blocks the operation. A live authenticated hardware identity
   or power-loss immunity is not claimed.
5. Write only the reviewed image into app0/app1 (0x10000 and0x750000, each0x740000),
   only after the release-specific preflight verifies those current boundaries and
   OTA state. Derive sector footprints from that image, not the old byte count.
   No erase-all, migration, OTA rewrite, filesystem upload or format command exists.
6. Explicitly compare both written slots separately. On write/compare failure:
   stop, retain private evidence, no retry or reboot, and direct a deliberate
   fresh-evidence rollback. The two-slot operation is not atomic.

Tests use an injected package checker and a **synthetic non-firmware application**,
not a substitute verified image. They establish engine control flow and fail-closed
behavior, not new package integrity or real serial operation. Actual new image/ESP
header validation and package binding remain pending the build; the existing strict
preflight is the reference, not something silently repinned to an unbuilt image.

## Immediate rollback identity is fixed correctly

The next package must contain the **currently working c20dc399 application** as
`rollback-application.bin`, not the older shortcuts image:

- 1,376,576 bytes.
- SHA-256 `c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4`.
- Public verified input `downloads/evilduck-stop-led-review.bin` is unchanged.

The prototype enforces that exact rollback identity and its tests use those public
bytes. No owner backups or configuration files were read, modified or committed.

## Mac compatibility and future first command

Owner-recorded environment remains macOS10.13.6, Python3.8.10, esptool4.12.0;
it was **not newly observed** here. These preparations need no Homebrew, Xcode,
Arduino IDE, compiler, OS upgrade, sudo, drivers or security bypass on the Mac.
The esptool4.12.0 source archive was independently SHA-verified and its actual
argument parser tested without compiling any connection/operation dispatcher.
The scripts have Python3.8 grammar and stock Bash syntax checks. Native High Sierra
serial execution remains NOT TESTED. No dependency download occurs in the launcher.

There is deliberately **no new download/check/extract/install command** pretending
that the requested ZIP exists. Once the build/profile gate passes, the release
must supply a commit-pinned ZIP URL, ZIP byte count/SHA, final application bytes/SHA,
package manifest and numbered INSTALL-MAC.md/ROLLBACK-MAC.md. Extraction must be
fresh; backup/evidence paths stay outside it. `bash install-macos.sh` will then run
read-only check; install and rollback remain separate deliberate actions.

Do not launch a host LED helper during update. Keep autorun off. Future acceptance,
only after separate review/install: one basic-typing Run with matching Completed;
Caps tap plus actual host case/LED evidence; raw callback deltas; compact STOP;
then temporary SD deletion. **No HOLD test on Route B**: the adapter rejects it.
Only after both raw Caps and Num reports are established may the visible finite
sender attempt the17-byte `EVILDUCK TEST 123` RAM roundtrip. No Caps-specific timing
change or physical fix is claimed by this work.
