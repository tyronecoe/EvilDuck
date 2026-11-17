# Later owner installation — PENDING

REVIEW CANDIDATE / NOT INSTALLED. Downloading or preflighting grants no installation
authorization. Keep EvilDuck UNPLUGGED for the first and only offline command:

    python3 preflight.py --directory .

Expected: package_integrity PASS, plan_ready false, selected_write_ranges [],
installation_authorized false, hardware_access false. Use Python 3.8+.

Host requirements remain Intel macOS High Sierra 10.13.6, Bash 3.2 and preinstalled
esptool 4.12. Compatibility is inspected, not demonstrated by executing on a Mac
in this task. Do not install dependencies from this package.

Only after separate owner authorization: use the board's existing ROM-entry
procedure, rediscover its current /dev/cu.usbmodem* port, then follow the existing
guarded interface. CURRENT_PORT is a placeholder; never execute it literally.

    bash install-macos.sh --action check --port CURRENT_PORT
    bash install-macos.sh --action install --port CURRENT_PORT

These later commands access hardware. The default action is check. Installation
retains chip/flash/security, exact partition and supported OTA-state checks.
The helper reads and saves a new private full-flash backup before final INSTALL
confirmation. Declining confirmation leaves that backup intact. It may contain
credentials, scripts and settings: keep it private. Existing backups are not
removed or overwritten. Only application slots at 0x10000 and 0x750000 can be
written; bootloader, partition table, NVS, OTA metadata and filesystems are
excluded. No automatic reboot, retry, erase-all, format or settings reset.

The firmware source is de683669135fe5ccc5922f9883709194400672e5. Later verifier
and packaging checkpoints preserve/review source; they are not firmware builds.
Independent artifact verification passed; physical acceptance and runtime peak
stack remain unknown. Read OWNER-CHECK.md before any later payload execution.
