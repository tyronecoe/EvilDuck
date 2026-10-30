# Experimental H1 High Sierra package delivery

**GO: review-only package publication. Physical installation, boot and payload execution remain separately authorized. Hak5 runtime encoding remains unresolved.**

Prepared on Linux from the exact existing H1 artifacts. No firmware source edits, rebuild, hardware access, real HID output, flashing, OTA, formatting, settings reset, owner-file access or private backup modification occurred. The current physical board's installed build remains unknown to this packaging stage. The accepted source/text v2 application and all earlier artifacts remain unchanged.

## Package and image identities

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `evilduck-routeb-inject-var-h1-experimental-macos-v1.zip` | 2,450,845 | `229da835898e6739e31e4a6c08dd1ee9b5d74ded0458c7a0d850c899f5d2c639` |
| H1 `application.bin` | 1,414,080 | `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd` |
| Accepted v2 `rollback-application.bin` | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

Build ID: **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1**. Firmware source-stage review commit: `a15b8e218935b2c6a69b71eeac3aaf378c3c0c03`; underlying source implementation commit: `4377e298d5f48dbe3dc8d73ba8655cf3aa83a7ca`. Packaging tools/docs identity bound into the ZIP: `ad224daa1c983acbe8945730ff823bb0ac79ea2a`. This distinction avoids presenting the packaging commit as a new firmware compilation. Publication URL and downloaded-byte verification are recorded separately in `inject-var-h1-package-publication.json` after push.

The packager requires the exact original H1 link-receipt hash `cf00b9a66e9b9dfb270f10d418e2145af083e7a58a64cc21f2b57842fbe0d4d0`, then verifies its generated source inventory and BIN/ELF/map/bootloader/table bytes against the available artifacts. The actual executed H1 build/link wrappers are checked separately from preserved parent wrappers; no absent inherited receipt field is fabricated. Missing or altered artifacts stop packaging. The preserved isolated core source identity is rechecked. The original archive/config/compiler/link/177-SDK-archive evidence is inherited from the completed build, not described as a new SDK rebuild or complete rerun.

Rollback is extracted from **application.bin** in the exact public accepted v2 ZIP, not that ZIP's older rollback member. Its source/release provenance and separate build receipt are included. It is a standalone application, not a full merged recovery image. This does not prove ROM access, installed metadata or physical recovery readiness.

## Focused fresh verification

| Final executed group | PASS | FAIL |
|---|---:|---:|
| Package, image/support integrity and fault injection | 75 | 0 |
| Bound installer with synthetic tool/device responses | 38 | 0 |

**113 final checks passed.** These are case counts, not newly invented assertion totals. Coverage includes image swaps/corruption, exact rollback, all four fixture bytes, H1 source/wrapper/selector/safety identity, rejection of unsupported compatibility claims, canonical table/OTA state, bounded writes, no unintended retries/reboots, partial operation failures, preserved old backup fixtures, deterministic archive bytes, Python 3.8 grammar and shell syntax. Tests never invoke a real serial/esptool device dispatcher.

The first attempt recorded package **74 PASS / 1 FAIL**, and installer **38 PASS / 0 FAIL**: the install guide lacked its explicit OWNER-CHECK.md reference. The guide was corrected, historical-report context clarified and a new ZIP generated. Final suites were rerun against that ZIP without weakening expectations. Initial results are retained in `inject-var-h1-package-tests.json`; final results there are distinct from that first attempt.

An independent extracted-ZIP review also verified all 28 unique flat regular members, the exact images/fixtures and the offline check's exit 0, PASS, no selected ranges, no authorization and no hardware access. The final report/publication receipts will verify downloaded bytes as a separate step. Public ZIP is ordinary Git blob data, not Git LFS.

Host for fresh checks: Linux, Python 3.12.14, Bash 5.2.37, Git 2.52.0. Python 3.8 grammar and shell syntax checks support the intended **High Sierra 10.13.6 / Python 3.8.10 / Bash 3.2 / esptool 4.12.0** interfaces. Native Mac execution of this new package is pending. No downloader/compiler installer is bundled.

The unchanged H1 source stage's **522 native passes / 23,124 assertions**, separate source probes/default-refusal checks and clean ASan/UBSan/leak results are reused evidence, **not rerun here**. Python package logic does not receive fictitious sanitizer results. `firmware-report.md` and `test-results.json` in the ZIP are explicitly labeled historical source-stage evidence; their earlier statements that no installation package existed describe that earlier stage.

## No build or resource change

Existing compiler usage: **1,413,931 bytes**; application: **1,414,080 bytes**; static RAM: **113,896 bytes**; OTA slot: **7,602,176 bytes**; free per slot: **6,188,096 bytes**. Packaging changes each value by **zero**. The earlier H1-vs-accepted-v2 deltas remain +876 compiler bytes, +880 BIN bytes and +8 static RAM bytes. Selected compiler frame estimates remain decoder48/eval144/completeInstruction48/statement352 bytes; they are not physical task-stack/heap/latency measurements.

ELF SHA-256: `c33c612cfa704b15d6b9c7908d37b8dc17767384270c8a52893f650bfc0763c0`. Partition SHA-256: `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`. Arduino ESP32 3.3.0 approved archive profile, ESP32-S3, 16 MiB, PSRAM disabled, existing USB/CDC/OTG identity and writable production geometry are preserved. The source pin and original build receipt carry the compiler/core/SDK details.

## Owner review path and boundaries

After externally verifying the published ZIP checksum and extracting into a new directory, the first **fully offline** check is:

```bash
python3 preflight.py --directory .
```

Expect package integrity PASS; `installed_metadata=NOT_SUPPLIED`, `plan_ready=false`, empty write ranges, `installation_authorized=false` and `hardware_access=false`. This is distinct from the launcher's default check, which needs a real port and reads hardware. Read INSTALL-MAC.md and ROLLBACK-MAC.md before seeking separate physical approval.

The reviewed installer is bound to the exact offline preflight. Future owner-operated installation/rollback checks S3/16MB/chip/security, exact current table and narrowly supported app0 OTA initializer, makes a new private full-flash prewrite backup, requires explicit INSTALL/ROLLBACK, rechecks metadata/chip/image and programs/verifies only both application ranges. It performs no automatic reboot/retry or script Start, and does not write bootloader/table/NVS/otadata/SPIFFS/coredump. Unsupported metadata must be separately reviewed, never repaired to satisfy a guard. Autorun must be confirmed disabled through existing authenticated controls before any later experiment; this package never changes settings. Later application execution retains ordinary existing settings/storage behavior and is not a quiescent profile.

OWNER-CHECK.md and four exact fixture files cover `aaA00!!` capture/copy/reassignment, held-Shift STOP without `999bad`, retained malformed rejection with blank TextEdit, and optional two-identical-random-lowercase capture. Use explicit Route B only, record actual request/session evidence and never automatically replay. The inherited configurable lock-wait delta is software-tested but not newly physically accepted. EDR1 and the established LED protocol remain unchanged; no special helper is needed.

A practical H1 pass would validate this EvilDuck convention on the tested Mac only. The next decisive **canonical** experiment remains a separately authorized genuine DS3 observation of calibrated raw scalar bytes correlated with copy and repeated injection. No such hardware result exists here. Preserve unresolved official runtime values and test alternative encodings rather than promote H1 to compatibility.

See `inject-var-h1-package-artifacts.json` for full member hashes, `inject-var-h1-package-tests.json` for fresh/initial results, and preservation/publication receipts for historical file/ref checks. All changes are additive packaging docs, tools, fixtures, receipts and this ZIP; firmware implementation files are unchanged.
