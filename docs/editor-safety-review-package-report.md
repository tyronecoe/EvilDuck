# Editor safety review package — completed verification

**REVIEW ONLY — NOT INSTALLED — NOT OWNER-HARDWARE-VERIFIED.** The exact existing
editor-safety application was packaged without rebuilding firmware. Installation
and future owner observations remain separate steps. No hardware, HID output,
flashing, OTA or owner-file mutation occurred.

## Source and publication identity

- Isolated branch: `routeb-editor-safety-review-v1`.
- Existing reviewed-source checkpoint: `1664d4f25593e6cc99dba43ff0e5d74531555a51`.
- Packaging-source checkpoint: `e12bedce330b1a00685127ac21dec979af405ee6`.
- Original compilation context: base `805d989c3ac50cb96025862c95916830c59f8ba7`
  plus 17 then-local inputs. The source checkpoint is a later attestation of those
  exact bytes, not the commit originally compiled.
- Original local-input manifest:
  `525fc3f9e95c65f81a1233f3f31eac1f321233d0dd87ac2517d5a4c2f2eab768`.

The eight reviewed editor files and 14 integration files are checkpointed without
changes. All 2,394 historical files/modes remain unchanged. Publication and a
download of the commit-pinned ZIP are recorded separately in the publication
receipt. No existing branch or tag is selected for publication.

## Artifact identities

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `evilduck-editor-safety-h1-macos-review-v1.zip` | 2,538,965 | `ea00a7da38d775d62b28624d232de48102c459eee24195b55e185ae70d117638` |
| `application.bin` | 1,437,696 | `e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0` |
| Original ELF (provenance, not a ZIP flashing image) | 23,645,104 | `51e918c98249af4fb79dbd79a31a2ecdbcb92a0045e2d6f213c99cd86e755057` |
| `rollback-application.bin` | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

The unchanged static build ID is `ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1`.
Historical H1 IDs inside frozen verification layers identify their ancestors;
they do not identify this application. The exact application hash distinguishes
the candidate. It was not rebuilt merely to rename it.

The rollback is the exact older source/text-v2 application, **without Privacy
Fix 1 or the dashboard/editor repairs**. It is not a merged recovery image.
Application rollback does not restore scripts, filesystem data or old settings.
All historical packages and existing private recovery files remain untouched.

## Newly executed software verification

| Check | PASS | FAIL |
|---|---:|---:|
| Editor-specific package/source/provenance/resource checks | 44 | 0 |
| Inherited package, archive, image/layout and negative checks | 83 | 0 |
| Bound installer with mocked transport/security/flash/confirmation | 38 | 0 |
| Focused source/AST/Python 3.8 policy groups | 5 | 0 |

The fresh actual-ELF/BIN release check passed all six preserved verification
layers. It retains all 190 static Assert nodes; this count is not 190 separately
executed tests. All five complete NUL-terminated dashboard/settings resources
were matched exactly once in the actual ELF and actual BIN. The package preflight
also checks those resources in the bundled application by offset, size and hash.
The fresh release receipt is bundled as `build-receipt.json`, SHA-256
`96800befe9fa4dba4386b9819d345c6f4f42fd368b7a461153674375767bd1d1`.

Source reconstruction in a fresh detached base worktree reproduced all 17 input
blobs and the exact original local-input digest without invoking a compiler.
The installer and shell launchers match the reviewed lineage except for the
generated release binding. Existing security, partition, OTA, bounded app-only
write, private-backup, confirmation and refusal paths remain in place. Negative
controls cover tampered/missing evidence, swapped images, wrong layout/chip,
security state, corrupt OTA, missing backup/readback and write/verify failure.
Installer behavior was exercised only through mocks, never a serial device.

The exact ZIP was extracted into a fresh directory and its actual offline command
returned exit 0, `package_integrity: PASS`, `plan_ready: false`, no selected write
ranges, `hardware_access: false` and `installation_authorized: false`.

Fresh receipts: [package summary](editor-safety-review-package-results.json),
[editor-specific](editor-safety-review-evidence/editor-package.json),
[inherited package](editor-safety-review-evidence/inherited-package.json),
[mock installer](editor-safety-review-evidence/mock-installer.json),
[policy](editor-safety-review-evidence/policy.json),
[source reconstruction](editor-safety-review-evidence/source-reconstruction.json),
[independent input verification](editor-safety-review-evidence/independent-input-review.json),
and [extracted offline preflight](editor-safety-review-evidence/offline-preflight.json).

## Reused evidence and resource measurements

Exact source and firmware hashes establish that the existing tested inputs did
not change. The following were reused, not rerun during packaging:

| Existing software checks | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| Editor/dashboard/STOP/source | 64 | 0 | 551 |
| Native privacy/settings | 28 | 0 | 736 |
| Existing composed native regressions | 558 | 0 | 23,901 |
| Composition controls | 9 | 0 | Not separately counted |

The recorded ASan, UBSan and leak checks remain clean for those exact native
inputs. Browser evidence is Linux Chromium/Playwright with inert fixtures, not
native High Sierra or iPhone acceptance. No accepted owner milestone was reopened.

Compiler program: **1,437,555 bytes**. Application: **1,437,696 bytes**, **+9,488**
versus the preceding dashboard application. Static RAM: **113,896 bytes**, unchanged.
OTA slot: **7,602,176 bytes**, with **6,164,480 bytes** free. Measurements are from
the verified existing build, not a new build or a physical runtime measurement.
The approved Arduino ESP32 3.3.0 archive-based profile, USB identity, dependency
guards, partitions and PSRAM-disabled configuration remain unchanged.

## First owner step and acceptance boundary

Download and extract the review ZIP. With **EvilDuck unplugged**, run only this
from the extracted folder:

```bash
python3 preflight.py --directory .
```

Require exit 0 and `package_integrity: PASS`; absent installed metadata, expect
`plan_ready: false` and no write ranges. Do not invoke an installer/device-check
or rollback launcher during this offline review.

The [short acceptance sheet](editor-safety-review-acceptance.md) separates later
owner-authorized read-only/page-RAM observations from already completed mock
failure/stale-response/guard tests. It requests no owner Save, Run, delete,
overwrite, upload, USB output or repeated keyboard/lock-wait/privacy trials.
The [platform evidence table](editor-safety-review-platforms.md) and
[reproduction guide](editor-safety-review-reproduction.md) state the limits.

The unchanged future installer creates a private full-flash backup before its
final write confirmation; that backup may contain credentials and scripts.
Neither the installer nor that backup stage was used here. A later installed
application must be evaluated separately; offline integrity does not establish
native High Sierra, device authenticity, installed bytes or physical recovery.

**Until a separately installed fix is confirmed, continue avoiding Save/editor
Run after a failed load on the installed firmware.** Server atomic/versioned
Save/Run, SD-path identity and browser text transformations remain limitations.
H1 stays opt-in and experimental; canonical Hak5 encoding remains unresolved.
