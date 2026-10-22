# Mac application-only package — review before installation

Candidate buildId: `ROUTEB-KEYBOARD-CONTROL-20261022-v1`.
The new Route B keyboard-control behavior is software-tested only. Its physical
High Sierra acceptance is pending. The earlier fixed-message LED-return milestone
is owner-confirmed for `CAPS-STOP-TRACE-20261019-v1`; that result is not physical
verification of this new application. Read `OWNER-CHECK.md` and `ROLLBACK-MAC.md`.

The earlier fixed-message Mac kit deliberately accepts only its original buildId.
It remains unchanged and will refuse this new candidate rather than silently
relaxing identity checks. If an optional later LED-return recheck is justified,
use the separately version-bound host launcher prepared for this candidate.
That changes only the expected application identity, not EDR1 framing, timing,
authentication or acceptance rules. Repeating the full LED test is not a routine
prerequisite for this keyboard-control release.

This is a review package, not authorization to install, boot, run payloads or
perform OTA. The cloud prepared and tested software without opening a serial
port or calling the esptool hardware dispatcher. A separate owner installation
decision and fresh device checks are still required.

## Required review

- Verify the ZIP SHA-256 against the published commit-pinned download receipt.
  Extract into a new directory. Do not combine files from different releases.
- Confirm the currently installed build is still
  `CAPS-STOP-TRACE-20261019-v1`, with installer-recorded application SHA-256
  `25e17cadacf3b2ab5eb5ece32fc94f4bf36fb71eb90e91814dca7f7320bd5178`.
  This is a known artifact identity, not a fresh physical flash measurement.
  If the board has changed, stop and review rollback identity before installation.
- Keep the existing backups untouched. Do not upload private backups, NVS,
  credentials or settings. This update performs no provisioning, defaults reset,
  script deletion or filesystem migration.
- Use macOS 10.13.6, Python 3.8.10, esptool 4.12.0 and Bash 3.2. The package does
  not install or download dependencies. Review the bundled manifest's exact
  image sizes, SHA-256 values and sector-rounded ranges.
- Installation requires the established 16 MiB writable partition geometry and
  the supported app0 OTA initializer. This package does not migrate the original
  small application slots or rewrite OTA metadata to make checks pass.

## Offline package review

From the extracted package directory:

```bash
python3 preflight.py --directory .
```

This performs no device access. `package_integrity=PASS` means only that the
public package, image headers/checksums/digests, rollback, partition template and
support-file hashes pass. Without current installed metadata, `plan_ready=false`
and no selected write ranges are returned. That is deliberate, not an install
failure.

## Future separately authorized owner actions

The following commands are documentation for an owner-controlled installation
review. Do not run them until physical device access has been authorized.
The historical serial port is not a safe default: determine a fresh ROM download
port using the owner's established ROM-entry procedure. Substitute that actual
port for `/dev/cu.CURRENT_ROM_PORT`.

```bash
bash install-macos.sh --port /dev/cu.CURRENT_ROM_PORT
```

The default action is read-only. It identifies exactly ESP32-S3/16 MiB, checks
disabled Secure Boot and flash encryption and reads the installed partition
sector and OTA data. Any unsupported layout, flags, active-slot record, security
state or ambiguous identity stops. It writes neither a full backup nor firmware
during `check`. Do not reinitialize metadata to bypass a refusal.

Only after separate owner approval for installation:

```bash
bash install-macos.sh --action install --port /dev/cu.CURRENT_ROM_PORT
```

The installer revalidates the package, creates a **new private 16 MiB backup**
under Desktop and checks its size and embedded table/OTA bytes before asking for
typed `INSTALL`. A full ROM read at 115200 baud may take many minutes. Numbered
`Step N: operation`, `PASS` and `FAIL` messages report actual subprocess outcomes.
A quiet backup is not permission to start another operation.

After confirmation it re-identifies the same device, re-reads table/OTA metadata,
requires unchanged exact image bytes and performs one application-only write
operation. The image goes to `0x10000` and `0x750000`; each rounded erase/write
range fits its `0x740000` application slot. Bootloader, partition table, NVS,
OTA data, SPIFFS and coredump are excluded. Each application slot receives an
independent comparison. There is no separate erase, full-chip erase, automatic
retry, reset, reboot or OTA action.

On any write/comparison failure, stop and retain ROM mode and the private receipt.
Do not retry blindly. Use a separately reviewed deliberate rollback with fresh
identity and metadata checks. Even two successful comparisons leave
`boot_tested=false`; owner boot and the short `OWNER-CHECK.md` acceptance are
separate. No claim is made that local HID submission proves host key release.
