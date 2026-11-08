# Bounded DEFINE-label review download

**PUBLISHED FOR REVIEW — NOT INSTALLED — DEFINE HARDWARE ACCEPTANCE PENDING.**

[Download the Mac review ZIP](../downloads/evilduck-routeb-define-labels-h1-macos-review-v1.zip?raw=true).
This publication copies the verified archive byte-for-byte. It does not rebuild
or repackage firmware, install anything or run an owner payload.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| ZIP | 2,691,374 | `b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed` |
| Application | 1,438,048 | `167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30` |
| Exact older source/text-v2 rollback | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

Actual candidate build ID: **`ROUTEB-DEFINE-LABELS-H1-v1`**.
Implementation/build checkpoint: `5d9176dd15f722ffe20d219d33684da7461d1754`.
Package checkpoint: `2f8567a2547d133f54de7aa122aff05fe71629d7`.
Completed delivery/evidence checkpoint: `3a4533331784c7c8a6ef177ed98bbe2bba0b8e0e`.
The later dedicated publication commit preserves these source identities.

The latest owner-installed record is DEL. Its scoped integrity, installer and
TextEdit observations are recorded in [the owner closeout](del-alias-owner-closeout.md).
Full running dashboard ID and request/Completed evidence were unavailable; this
does not erase the reported installation or require repeated DEL tests. No
DEFINE installation or physical acceptance is claimed here.

## Offline review on High Sierra

Download to the Intel Mac running macOS High Sierra 10.13.6. With EvilDuck
**unplugged**, verify the ZIP hash:

```bash
shasum -a 256 evilduck-routeb-define-labels-h1-macos-review-v1.zip
```

Stop on mismatch. Extract to a new folder. From that extracted folder run only:

```bash
python3 preflight.py --directory .
```

Expect integrity PASS, exit 0, `installed_metadata=NOT_SUPPLIED`,
`plan_ready=false`, empty `selected_write_ranges`, and both hardware access and
installation authorization false. This standard-library-only offline check does
not contact hardware or download dependencies. Keep the existing kit's High
Sierra/Bash 3.2/Python 3.8/esptool 4.12 installation and rollback instructions.
This publication adds no new physical operation or device path.

## What improved and what was verified

DEFINE labels accept 31 bytes excluding NUL, including optional `#`; sixteen
32-byte name cells retain the existing bounded collection/expansion/flag path.
Variable/function names stay at their old limits. Source, line, IR, text,
workspace and execution budgets stay unchanged. The maximum is EvilDuck policy,
not a claimed official DS3 maximum.

[Full report](define-labels-release-delivery.md),
[measurements/results/source inventory](define-labels-release-results.json),
[source contract](define-labels-design.md), and
[short owner sheet](define-labels-owner-check.md) accompany the code and ZIP.
The completed run passed **691 fresh native cases / 28,547 assertions**, clean
ASan/UBSan/leak checks, a clean approved-profile build, all 190 inherited release
assertions, 30 release controls and package checks 7/73/83/38. The 86 web groups
were explicitly reused with unchanged-source/input evidence, not rerun. Delivery
hash/download checks do not relabel those receipts as new tests or physical
acceptance.

Actual ESP32 Compiler size grows 3,800 to 3,928 bytes, alignment 8, leaving 168
bytes in the unchanged 4,096-byte workspace. Host size grows 3,856 to 3,984 bytes.
All 72 emitted core stack frames remain unchanged. Application size increases 160
bytes; static RAM remains 113,896 bytes. DWARF and unlinked compile-only layout
objects agree. No target heap, physical stack peak or host timing claim is made.

For later separately owner-operated checks, the three fixtures are both in the
ZIP and available here:

- [27-byte official name](define-labels-owner-fixtures/D01_DEFINE_27.txt):
  DEFINE27OK and one newline, matching Completed.
- [31-byte boundary](define-labels-owner-fixtures/D02_DEFINE_31.txt):
  DEFINE31OK and one newline, matching Completed.
- [32-byte rejection](define-labels-owner-fixtures/D03_DEFINE_32_Rejected.txt):
  compile error at line 1/code 6 and blank TextEdit.

They only substitute harmless constants. No shell, network, credential access,
input collection or OS probe is involved. No new broad acceptance campaign is
required, and no fixture is automatically executed.

## Remaining boundaries and recovery

[The unchanged official OS extension now rejects at line 54/code 18](define-labels-os-progress.md)
instead of the historical line 50/code 6. Only the DEFINE prerequisite is resolved.
Counter read/reset and its exact runtime contract, OS symbols, indicators,
lock restoration, USB modes/identities/reconnect and host accuracy remain
separate. Unknown lock feedback stays unknown. No detector, fabricated counter,
manual OS substitute or USB hook was added. H1 remains opt-in/experimental;
canonical Hak5 numeric encoding remains unresolved.

The exact rollback is the older standalone source/text-v2 application. It lacks
later privacy/dashboard repairs and is not a full-device/filesystem restore.
Existing published DEL packages, recovery files and private backups are
untouched. The installer retains its documented private full-flash backup before
final confirmation and guarded application-only writes; no automatic reboot,
formatting, settings reset or script execution is authorized here.

Only the new review branch is published. Default/accepted branches and existing
tags/refs are preserved; no merge or force-push. No hardware access, serial
operation, HID output, flashing or OTA occurred during this task.
