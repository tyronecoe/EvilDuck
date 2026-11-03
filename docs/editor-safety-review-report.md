# Editor safety — High Sierra review-package report

**REVIEW ONLY — NOT INSTALLED — NOT OWNER-HARDWARE-VERIFIED.** This stage prepares
and publishes a review package from the exact existing verified application. It
adds no firmware, DuckyScript, HID, collection or platform capability. No rebuild,
installer execution, hardware access, script/file mutation, flashing or OTA occurs.
Downloading or validating a package does not authorize installation.

## Exact candidate, checkpoint and preserved evidence

Application: **1,437,696 bytes**, SHA-256
`e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0`.
ELF: **23,645,104 bytes**, SHA-256
`51e918c98249af4fb79dbd79a31a2ecdbcb92a0045e2d6f213c99cd86e755057`.
Static label remains **`ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1`**; firmware was not
changed merely to rename it. The label is static identity, not proof of installed
bytes or current board state.

Original build base: `805d989c3ac50cb96025862c95916830c59f8ba7`, plus 17 exact
then-local inputs. Raw local-input manifest SHA-256:
`525fc3f9e95c65f81a1233f3f31eac1f321233d0dd87ac2517d5a4c2f2eab768`.
The eight prior editor-review files and all 14 integration files were checked;
none changed. All 201 composed sources, the actual compiled header/object/map
binding, new identity and five complete embedded resources reconcile with the
build and test receipts. Privacy Fix 1 remains in actual CLI/server/settings
sources; no prerequisite or overlay was dropped.

New isolated branch: `routeb-editor-safety-review-v1`. Source checkpoint
**`1664d4f25593e6cc99dba43ff0e5d74531555a51`** adds exactly those 22 files to the
baseline without changing historical files. It records the existing source
**after the build**. The package attestation matches all 17 original source-input
Git blobs to that checkpoint. Original base/local-digest provenance remains
unchanged; no future commit is misrepresented as the original build context.
The earlier reports' no-commit/no-package statements describe their original
stages and are preserved, not retroactively edited.

The frozen normal builder still requires its original base. A new developer-only
source reconstruction helper materialized the checkpoint's exact inputs on a
fresh detached `805d989` worktree and reproduced the identical raw input manifest
without invoking a compiler. The normal command, exact prerequisites and this
constraint are documented in [reproduction](editor-safety-review-reproduction.md).
No manually copied generated header or new firmware image is substituted.

## Fresh checks versus reused software evidence

Fresh packaging-stage checks:

- Exact application/ELF bytes, original source/input hashes, rollback member and
  historical ZIP were rechecked before use.
- Independent target verification matched all 201 entries and **five complete,
  NUL-terminated dashboard/settings resource byte sequences exactly once in both
  actual ELF and actual application BIN**, alongside compiler/header/object/map
  evidence. This is not a synthetic-marker or source-existence-only claim.
- Full inherited linked/disassembly verification reran: **six frozen layers PASS**,
  all **190 static Assert nodes retained**, with no unrelated guard removed.
  This is an AST preservation count, not 190 independently executed test cases.
- Fresh source reconstruction verified the 17 Git blobs and original builder
  input manifest without a rebuild.
- Final package, installer-mock, preflight, publication/download checks are recorded
  in accompanying package/publication receipts after this packaging-source report.

Reused results, with their exact source/candidate identities demonstrably unchanged:

| Software evidence | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| Editor/dashboard/STOP/source checks | 64 | 0 | 551 |
| Native privacy/settings cases | 28 | 0 | 736 |
| Existing native composed regressions | 558 | 0 | 23,901 |
| Composition/negative controls | 9 | 0 | Not separately counted |

ASan, UBSan and leak detection were clean for the completed 586 native cases;
all case stderr records were empty. These sanitizer/browser suites were **not
rerun merely to increase packaging totals**. The native harness's repeated
9-group/207-assertion browser check is historical/reused, not extra platform
coverage. The pre-fix overwrite control and omitted/old resource controls remain
preserved; expected unsafe-fixture rejection is not a candidate failure.

Browser evidence is Linux Chromium 151.0.7922.173 / Playwright 1.62.0 with inert
HTTP, not native High Sierra/iPhone/Windows/Android acceptance. The current image
is still subject to the documented server-version/atomic Save/Run, byte-backup,
SD-path and browser-text limitations. This package does not repair already
changed files, alter SD identity, change the LED protocol or claim canonical
Hak5 H1 numeric encoding.

## Existing guarded package mechanism and recovery

The package uses the SHA-pinned reviewed packaging lineage. Installer/launcher
behavior is preserved; only its generated release binding changes. Read-only
preflight validates images, exact source/provenance/resource identities and the
supported table/OTA contract. A package PASS with no installed metadata leaves
`plan_ready: false` and no selected write ranges. It is not device authenticity,
boot, recovery-access or physical-layout evidence.

The unchanged future installer requires separate physical authorization and
explicit confirmation, checks chip/security/partition/OTA state, bounds writes to
both existing application slots, creates a new **private full-flash backup before
final write confirmation**, and verifies writes without automatic boot or retry.
That backup can contain credentials/scripts and remains even if final installation
is declined. No existing backup is deleted/overwritten or uploaded. Do not invoke
hardware checks or install/rollback launchers during this review.

The exact mandatory older source/text-v2 rollback is **1,413,200 bytes**, SHA-256:
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It contains **no Privacy Fix 1, dashboard cleanup or editor safety repair**.
It is a standalone application, not a merged-flash or full recovery image. An
application rollback does not restore deleted scripts, filesystem data or old
settings. Existing published packages and private backups stay untouched.

Four historical `rm-*.txt` package fixtures remain provenance only. They are not
requests to run stored scripts or repeat accepted keyboard tests. The four
right-modifier passes (including executed STOP variant), three lock-wait groups
and scoped privacy milestones remain closed; request gaps create no retest demand.

## Resource comparison and review boundary

| Compiler/build measurement | Earlier dashboard | Exact editor candidate | Change |
|---|---:|---:|---:|
| Compiler program bytes | 1,428,067 | **1,437,555** | +9,488 |
| Application BIN bytes | 1,428,208 | **1,437,696** | +9,488 |
| Static RAM | 113,896 | **113,896** | 0 |
| OTA slot capacity | 7,602,176 | **7,602,176** | 0 |
| Free bytes per slot | 6,173,968 | **6,164,480** | -9,488 |

These measurements are reused from the exact verified build, not a packaging
rebuild. They are not physical heap/stack/latency measurements. The approved
isolated Arduino ESP32 3.3.0 / ESP-IDF 5.5 archive-based environment, 16 MiB,
PSRAM-disabled profile, USB identity and production partition hash remain intact.
The ELF is provenance evidence; it is not included as a flashing image.

Owner first offline step from the extracted folder, **EvilDuck unplugged**:

```bash
python3 preflight.py --directory .
```

Use [the short acceptance sheet](editor-safety-review-acceptance.md) only as a
future separately approved observation plan: valid reads, visible separate errors,
page-RAM drafts/New and identity. Forced failures/stale replies/direct guards are
fixture tests only. No owner is asked to Save/Run/overwrite a stored script, produce
USB output, delete a file or trigger diagnostics for this review.

[Platform targets](editor-safety-review-platforms.md) distinguish browser access,
wired USB, installation and OS-specific scripts for High Sierra, newer macOS,
Windows 10/11, Linux, Android and iOS. Only actual evidence is claimed; no generic
HID, Linux mock or iPhone Wi-Fi observation proves another surface. No validated
Windows/Linux/mobile flashing workflow is supplied.

Final package/download identity and newly executed packaging totals are supplied
alongside this frozen source-checkpoint report. Installation remains separately
authorized. **Until a fixed build is separately installed and confirmed, continue
avoiding Save/editor Run after a failed load on the installed firmware.** Stop
here for owner review; do not execute the future acceptance or installer workflow.
