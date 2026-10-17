# STOP/LED installation package preparation

Prepared on `stop-led-installation-package`, directly from reviewed source
`d18b7fddedaecef27be9fd7e486ad2d092a513c6`. This completes the new Revision 2
installation-document/package request. No firmware features changed or rebuilt.
The earlier handoff's statement that installation instructions had not been
requested is superseded by the owner's new task.

## Owner deliverable

[Installation guide](stop-led-install.md), also `README.md` inside
`downloads/evilduck-stop-led-install-v1.zip`.

- ZIP: **2,133,598 bytes**.
- SHA-256: `d7fe3e6400deb689dc807b0a08285dcb06f5682caf134c90aba38e986b83c255`.
- [Full member hashes and range inventory](stop-led-install-integrity.json).
- Fourteen flat public members: `README.md`, `manifest.json`, `application.bin`,
  `rollback-application.bin`, `expected-partitions.bin`, `preflight.py`,
  `gen_esp32part.py`, `APACHE-2.0.txt`, `source-LICENSE.txt`, `build-receipt.json`,
  `rollback-build-receipt.json`, `firmware-report.md`, `tool-evidence.json`,
  `host-cleanup-revision.json`.
- No owner backups, credentials, NVS/settings images, user scripts, flash writer,
  merged image, bootloader image or OTA initializer are included.
  `expected-partitions.bin` is **inspection only**, not a planned write.

Application: **1,376,576 bytes**, SHA-256
`c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4`.
Identical to the retained reviewed BIN and retained composed-build artifact.
The builder checked the retained ELF, partition table, bootloader and pinned
protected-core source tree against the original unmodified build receipt.
Existing build evidence (not rerun compilation): program **1,376,423 B**, static
RAM **107,480 B**, free per OTA slot **6,225,600 B (81.892342403%)**.
The full source inventory, ELF hash, 177 SDK identities and isolated core pin
remain in the bundled original receipt. Existing working packages are unchanged.

Rollback: prior `5c19f0d` application **1,359,808 B**, SHA-256
`de241287b972c24e510d3e8d22d888a17f13d1e972142559ba3df19f6195b41d`.
The retained earlier package and its commit-pinned location are in the guide.
Both binaries include valid ESP32-S3/DIO/80MHz/16MiB image headers, segment
checksums and appended SHA-256. The QIO-profile bootloader is preserved.

## Conditional installation policy

The established method is retained: application-only ROM programming of the
same reviewed image into BOTH 0x740000 slots, at 0x10000 and 0x750000. No active
slot is guessed. All other flash regions are excluded from write/erase plans.
Sector-rounded image footprints are checked independently for update and rollback.
No separate erase, erase-all, filesystem repair/upload or OTA rewrite is proposed.
App programming necessarily erases the covered application sectors; the guide
explicitly discloses this rather than claiming erase-free NOR programming.

Fresh real device metadata has NOT been supplied for this preparation. The guide
provides read-only chip/security, full current backup, table, OTA and NVS reads.
It demands the precise existing proposed production layout, the previously
supported pinned app0 initializer OTA state, ESP32-S3/16MiB and disabled security
features. A different valid OTA state requires review, not rewriting metadata to
force acceptance. Current layout and OTA state are not inferred from old reports.
The minimal metadata commands are table read 0x8000/0x1000 and OTA read
0xE000/0x2000; the full backup and identity review are additional owner gates.

The preflight has no serial/network/write operation. Package-only validation
returns no selected ranges. New `--require-installed` causes missing evidence
to fail with exit 1. The actual future write and rollback blocks chain this check
with `&&`; they also check a fresh full backup size and require manual identity
review. File evidence is not authenticated device identity or freshness. Future
physical execution stays owner-controlled. Runtime SDK/settings writes are outside
an app-only programming-range guarantee; no runtime NVS immutability is claimed.

## Narrow sender-only correction

Both defects were present at the reviewed source. macOS restoration used `||`
with short circuiting, potentially skipping Num. Windows used one try for both
restores and retained an earlier successful return after restoration failed.
Both now attempt Caps and Num independently, and unconfirmed restoration produces
failure. Windows preserves send/cancellation failure and returns only after cleanup.
No diagnostic sender was run; no OS key event was emitted. The separate host-tool
source hashes are bundled in `host-cleanup-revision.json`; these changes do not
alter the d18b7fd firmware provenance. No new host senders are installed by the ZIP.

## Fresh focused verification

| Check | Result | Scope |
|---|---|---|
| Package/preflight | 37 PASS, 0 FAIL | Public/synthetic metadata, corruption/rejection, rollback, CLI exits, read-only inputs, exact ZIP, deterministic rearchive, Bash syntax, Python 3.8 grammar |
| esptool4.12 parser | 9 PASS, 0 FAIL | Actual source AST truncated after parse_args; no connection or flash dispatcher compiled into harness |
| macOS cleanup statements | 8 combinations PASS | Extracted actual cleanup block, fake value API, Linux C runtime |
| Windows cleanup source | 3 checks PASS | Exact independent try/catch structure and failure-return propagation; not C# execution |
| Cleanup sanitizer harness | PASS | GCC ASan + UBSan + leak detection, halt-on-error |
| Native Windows/High Sierra build/run | NOT TESTED | OS toolchains and real host APIs unavailable here |
| Physical installation/STOP/LED/rollback | NOT TESTED | Owner-controlled future steps only |

No broad firmware suite or compilation was repeated for this documentation/package
and host-only change. Prior firmware test results remain historical, not counted
as freshly executed. First cleanup-harness invocation found no `clang`; the
compiler was corrected to available GCC `cc` without weakening sanitizer flags,
and the completed execution passed. Expected cleanup-negative cases print
`LED restoration unconfirmed`; they are successful checks of failure reporting.

Published esptool4.12.0 source archive was retrieved with its PyPI SHA-256 checked
before isolated installation. Its Python requirement is >=3.7, compatible at
the version-constraint level with the owner's Python3.8.10. Linux version/help
and parser checks are not High Sierra serial compatibility claims. No upgrade
is required. See tool evidence and reproduction instructions.

## Changed files and preservation

New docs: `stop-led-install.md`, `stop-led-install-report.md`,
`stop-led-install-reproduction.md`, `stop-led-install-integrity.json`,
`stop-led-install-preservation.json`, `stop-led-install-tool-evidence.json`,
`stop-led-install-host-cleanup.json`, `stop-led-install-results.json`,
`stop-led-install-cleanup-results.json`, `stop-led-install-parser-results.json`.

New tooling: `tests/stop_led_package/{package.py,preflight.py,run_tests.py,
sender_cleanup_tests.py,tool_parser_tests.py}`.

New archive: `downloads/evilduck-stop-led-install-v1.zip`.
Only existing files modified: `host_tests/led_return/send-macos.c` and
`host_tests/led_return/WindowsSender.cs` (cleanup only).
No firmware, earlier reports, partitions, dependencies or existing packages changed.
Baseline remote refs and original public artifact pins are recorded separately;
publication verification compares all prior refs and downloads the new ZIP through
its commit-pinned URL before reporting success.

**GO:** package review, download/integrity check and owner read-only identification.
**CONDITIONAL:** application-only installation only after every guide gate matches
and the owner deliberately executes the reviewed write. Missing/currently unverified
facts are live layout, supported OTA state and current chip/security/backup evidence.
No unconditional deployment or new physical test PASS is claimed. Original stock
availability is owner-confirmed external and not a new blocker. No hardware access,
flashing, erase operation, OTA, real HID or host diagnostic launch occurred here.
