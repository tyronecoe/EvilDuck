# Previous-command REPEAT v1 — local review delivery

**BUILT — PACKAGED — REVIEW ONLY. HARDWARE-VERIFIED = NO. INSTALLED = NO. PUSHED = NO.**

Build ID: **`ROUTEB-PREVIOUS-COMMAND-REPEAT-v1`**.

- Firmware/verification checkpoint: `820a575a45e5a4f644921d663a650110667a6ab2`.
- Packaging checkpoint: `fe6a6c4fcfca4fdf64023c998975cb3f7eb05e13`.
- Branch: `routeb-previous-command-repeat-v1`, descended from
  `fcba0385ce21662c7a504e0c9b6fba0dfa2c4f8d`.
- All commits are local. No push, merge, serial/network device connection,
  installation, real HID output, flashing or OTA occurred.

Relative to the original baseline, the only modified pre-existing path is
`tools/build_routeb_candidate.py`. Additions are the eight accepted source-stage
files in `tests/previous_command_repeat/`, nine release-integration files in
`tests/previous_command_repeat_release/`, four packaging files in
`tests/previous_command_repeat_package/`, and six stage/design/results/delivery
documents. [Focused firmware source diff](../tests/previous_command_repeat/application.patch)
and the [complete code/package diff through the packaging checkpoint](/workspace/scratch/previous-command-repeat-release/release-source-diff.patch)
are available for review. Historical firmware files, overlays, packages and
recovery images remain unchanged.

## Review artifacts

[Review ZIP](/workspace/scratch/previous-command-repeat-release/evilduck-routeb-previous-command-repeat-h1-macos-review-v1.zip)
— **2,605,305 bytes**, 40 members.

ZIP SHA-256:

```text
9ab478df75fcec25648572320229ed9b31b167fa4f1af4f18ea200f2b97f4fbb
```

[Application BIN](/workspace/scratch/previous-command-repeat-release/build-v3/build/EvilDuckS3.ino.bin)
— **1,437,888 bytes**, SHA-256:

```text
13cec88262afdfa641eb0fb4927fe7903abf2863295344ff316418707ba49b7f
```

[ELF, provenance only](/workspace/scratch/previous-command-repeat-release/build-v3/build/EvilDuckS3.ino.elf)
— **23,644,796 bytes**, SHA-256
`9fb92daca3bc71ef1e0d7b60070290e718828df7c36d1125acc8db1f493e6f35`.

[Package manifest](/workspace/scratch/previous-command-repeat-release/package-v1/manifest.json)
and [short owner checklist](/workspace/scratch/previous-command-repeat-release/package-v1/OWNER-CHECK.md)
are also inside the archive. Nothing was published remotely. Local artifact
paths are supplied for review.

## Build, composition and guard evidence

The actual normal entry executed its original committed-source guard on all
**47 selected Git inputs**, then used `arduino-cli compile --clean --verbose`
through the approved isolated archive-based Arduino ESP32 **3.3.0** profile.
Compiler: **Xtensa GCC 14.2.0**, crosstool-NG `esp-14.2.0_20241119`, SHA-256
`d968578945d9f62c2769e03a786d8853eb0ba226cfff1e8ee6588550927941a3`.
Dependency, SDK archive, startup, USB, partition, NVS and PSRAM guards remain.
The target is ESP32-S3, 16 MiB flash, QIO, 240 MHz, custom unchanged partitions,
PSRAM disabled and the existing explicit H1/controlled Route B profile.

Freshly generated target sources match all **201** final source hashes used by
the fresh native/browser checks. Relative to the prior static-response image,
only the bounded REPEAT compiler and build-ID literal change. No runtime/HID,
storage, authentication, dashboard resource or LED protocol implementation changed.
The previously uncommitted implementation/test/doc inputs remain byte-identical
except for the intentionally advanced canonical selector.

[Committed guard receipt](/workspace/scratch/previous-command-repeat-release/committed-guard-v3/guard-verification.json)
and [complete release receipt](/workspace/scratch/previous-command-repeat-release/build-v3/previous-repeat-release-verification.json)
bind the actual source, compilation, objects, dependencies, ELF and application.
The complete six-layer chain passes with **190 inherited assertion nodes
preserved, none removed**. The REPEAT witness follows executable calls:
`Compiler::step → line → statement → statementImpl`, then identifies linked
standalone-branch source lines and actual modifier-handler calls. Static
response dispatch, pointer/length arguments and complete embedded resources
also pass. This is stronger than checking a build label or an isolated host mock.

The active verifier's bytes match its Git blob at the compilation checkpoint.
Last-touch revision is recorded separately; there is **no post-compilation
verifier/source exception** for this image.

| Resource | New value | Change from static-response candidate |
|---|---:|---:|
| Application BIN | 1,437,888 bytes | +192 |
| Compiler program | 1,437,735 bytes | +188 |
| Static RAM | 113,896 bytes | 0 |
| Free space per 7,602,176-byte application slot | 6,164,288 bytes | -192 |

Heap use, physical USB completion and precise host timing are not measured here.

## Fresh software and package results

| Group | PASS | FAIL | Assertions/checks |
|---|---:|---:|---:|
| REPEAT native | 50 | 0 | 2,739 assertions |
| Privacy native | 28 | 0 | 736 assertions |
| Existing composed native regressions | 558 | 0 | 23,901 assertions |
| Static-response native | 33 | 0 | 976 assertions |
| Streamed-resource browser | 3 | 0 | 26 assertions |
| Dashboard browser | 9 | 0 | 207 assertions |
| Editor browser | 41 | 0 | 309 assertions |
| Old/new causal controls | 2 | 0 | 8 checks |
| Core edge probe | 1 | 0 | 2 checks |
| Profile refusals | 12 | 0 | Expected rejections |
| Release-verifier controls | 17 | 0 | Tests |
| Builder architecture controls | 4 | 0 | Tests |
| Package source policies | 6 | 0 | Tests |
| New release-package controls | 47 | 0 | Tests |
| Inherited package/archive controls | 83 | 0 | Tests |
| Actual extracted bound-installer mocks | 38 | 0 | Tests |
| Supplementary synthetic engine controls | 42 | 0 | Tests, reported separately |
| Fresh extracted offline preflight | 1 | 0 | Exit 0 |

Distinct native total: **636 PASS, 27,376 assertions**; web/component total:
**86 PASS, 1,518 assertions**. ASan, UBSan and leak checks passed. The identical
nine dashboard groups rerun by the native wrapper are not counted twice. The
42 supplementary engine checks are not added to the 38 required bound-installer
tests as unique independent coverage.

The regression run was fresh against the exact final 201-file composition.
It was reused after host-only verifier corrections because production bytes
remained identical; the broad native/browser suite and accepted physical trials
were not gratuitously rerun. Original test files, values and failed development
receipts remain unchanged. Linux mocks and Chromium do not establish native
High Sierra/iPhone or owner hardware success.

The first two clean compilations passed target checks but their full release
checks correctly refused host-verifier integration errors: first the old direct
parser-handler name, then filename reuse between generated nested verifier units.
Both attempts and their images remain under `build-v1` and `build-v2`, with
`build-attempt-v1.json` and `build-attempt-v2.json`. Only the fresh `build-v3`
passed the complete chain and supplied this ZIP. Corrections retarget exactly
two right-modifier handler-selector constants in the verified logical unit;
all 23 assertions in that unit and all 190 total remain. No rejected attempt
was substituted, relabeled or packaged.

[Machine-readable results and artifact hashes](previous-command-repeat-release-results.json)
reference the complete build, regression and package receipts. Historical
source-only results are kept separate from these fresh release-stage checks.

## High Sierra offline review and future acceptance

Keep EvilDuck **unplugged**. Extract the ZIP into a new folder. From that
extracted folder in Terminal, run only:

```bash
python3 preflight.py --directory .
```

Use the existing Python 3.8+ installation. This standard-library check does not
install dependencies or contact the board. Expect exit 0 and:

```text
package_integrity: PASS
installed_metadata: NOT_SUPPLIED
plan_ready: false
selected_write_ranges: []
installation_authorized: false
hardware_access: false
```

Fresh extraction verified all 40 members byte-for-byte and produced those values.
Do not substitute the installer launcher for this offline step. The future
guarded installer retains Bash 3.2, Python 3.8 and esptool 4.12 compatibility,
image/partition/security/backup/rollback and bounded application-write checks.
Its private full-flash backup occurs before final INSTALL confirmation and can
contain credentials/scripts; no private backup was accessed during preparation.

After separately authorized owner installation, the checklist requests only
baseline status/STOP availability, exact `T05R:xxxx:DONE` plus newline and matching
Completed, exact `T05I:xxx:DONE` plus newline and matching Completed, and first-line
REPEAT rejection at line 1/code 14 with blank TextEdit. A small held-Shift STOP
check is optional if needed. Record text, dashboard and request observations
separately; HTTP 202 alone is not a pass. No automatic retry is authorized.

The eight T00–T04/T06–T08 owner-reported passes, old T05R Request 11 line-4/code-15
failure, T05W pass and T05I Request 14 pass remain scoped historical evidence.
Unavailable request/session identifiers remain unknown. Older lock-wait and
right-modifier milestones are preserved and not reopened. H1 remains opt-in and
experimental; canonical Hak5 numeric encoding remains unresolved. The bounded
REPEAT policy is not blanket DuckyScript 3.0 certification.

Exact rollback included unchanged: **1,413,200 bytes**, SHA-256:

```text
cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02
```

This is the older source/text-v2 standalone application, without subsequent
privacy/dashboard/editor repairs; it is not a full-device/filesystem restore.
Installation, flashing, OTA, physical acceptance and remote publication remain
outside this completed preparation stage.
