# Stage 25 report — recovery verification and controlled first boot

Baseline `54b3ee184f98308783e7b78c253b15fce2b30a87`.
Branch `stage25-controlled-first-boot`.

**PASS: focused software startup hardening, artifact validation and clean isolated builds.**
**BLOCKED: actual owner recovery resource and physical deployment evidence/authorization.**
**FAIL: zero unexpected failures in final executed suites.**

Exact original firmware/settings/scripts/filesystem preservation is not required. Existing
backups remain untouched optional resources. No stock search/download, hardware operation,
real HID output or owner-script execution occurred. No Stage26 implementation was started.

## Measurable corrections

The explicit `--controlled-normal-start` candidate fixes the startup blockers without
rewriting the language engine or replacing production SDKs:

- Missing namespace/security fields, blank/legacy/invalid credentials, type/read/allocation
  failures and stored autorun are rejected. No legacy credential fallback or settings repair.
- A bounded application-level SDK descriptor check rejects the installed old layout,
  readonly experimental layout, missing/extra/conflicting partitions and wrong main-chip
  identity before settings/media/services. Iterators are released on owned failure exits.
- Required SPIFFS mount uses false formatting flag. Failure latches off the application
  before SD, HID, MSC, CLI, web and scheduling. No example installer or autorun call.
- AP startup is checked before application HID/CLI/web activation; mode/softAP failure
  attempts shutdown without pretending a physical acknowledgement. Controlled startup does
  not log SSID/passwords. HTTP/USB operation still requires physical acceptance.
- One setup attempt per boot and an explicit completion latch prevent unintended re-arming
  or scheduling after failed/interrupted initialization.
- Controlled settings reset cannot restore insecure legacy defaults. Controlled setters
  cannot clear credentials or enable autorun. Healthy explicit saves remain supported;
  multi-key persistence is still non-atomic. Typed settings schema is unchanged.

Existing normal behavior is deliberately distinct and unchanged in functionality; it is
not the recommended first-install image. Deployment-safe remains quiescent. Experimental
readonly retains Stage22 pre-init gate and Stage24 cleanup/fail-closed SDK, with no writable
transition. Stage16 USB and Stage18 original-error/no-auto-erase safeguards remain pinned.
No Arduino Micro, partition geometry/flags, USB identity, parser or HID semantics changed.

[First-boot contract](stage25-first-boot-contract.md) records boundaries including early SDK
NVS activity, optional SD, normal-profile legacy behavior, and physical transport limits.

## Recovery and artifact compatibility

`tools/stage25_recovery_check.py` performs file-only header/chip/revision/IRAM-entry,
checksum/digest/trusted-hash, table/MD5/padding, geometry/capacity/clock/mode and bounded
sector-footprint checks. Its synthetic format vectors are not executable recovery firmware.
Compiled artifacts are independently checked, but no supplied stock recovery resource was
inspected. Missing resource returns **BLOCKED**, not a manufactured PASS or hardware FAIL.

The verifier accepts reviewed legacy4MiB images/layout on the owner-reported16MiB context,
and reviewed proposed16MiB geometry; it rejects a header capacity smaller than its table.
Bootloader offset0, table8000, OTAE000 and app10000 are checked. Canonical OTA initializer
selects app0. The controlled1329760-byte image exceeds old140000 slots by19040 bytes.
An app-only update cannot establish the new installed layout.

[Recovery/readiness](stage25-recovery-readiness.md) gives the precise owner-private resource
input, supported subset, source versus actual header evidence, ROM prerequisites and a
non-executable future region plan. Original backup hash/preflight results remain previously
owner-reported evidence; private binaries are not claimed inspected by Codex.

Four actual non-owner review binaries are provided in `review/stage25-controlled`, each
hashed/sized, explicitly **NOT AUTHORIZED FOR FLASHING**. They exclude NVS/owner credentials,
SPIFFS/owner scripts and merged full-flash images, and are not a complete migration package.
This makes review/download possible without asserting High Sierra GCC compatibility.

## Actual focused tests

| Group | Final result | Assertions |
|---|---|---:|
| Controlled production startup/settings/SPIFFS/storage/layout | 30 PASS | 635 |
| Actual AP helper source, Wi-Fi result adapters | 6 PASS | 23 |
| Recovery/provenance/range/factory-policy vectors | 28 PASS | 28 |
| Affected legacy normal/safe settings and checked persistence | 81 PASS, 1 retained interrupted-save observation | 573 |
| Existing Stage1 scheduler/cancellation/ownership | 5 PASS; 5 historical language XPASS separate | 139 including12 diagnostic sanity assertions |
| **Executed total** | **150 PASS, 0 unexpected FAIL** | **1398** |

ASan/UBSan passes for executed C++ tests; leak detection enabled on normal native paths.
Intentional process interruption is an observation, not a passing atomicity/LSan claim.
SDK calls/services/USB/FS/partition tables are explicitly mocked where stated; production
settings/SPIFFS/storage/setup/loop/helper bodies run. The complete Xtensa SDK/ROM/RTOS and
physical device were not executed. New recovered format/checksum vectors do not prove
opcode behavior or physical recovery. Actual target ABI assertions and linked ELFs were checked.

The Stage24 full1551-pass baseline was not rerun or recycled as new results. Only affected
startup/settings/persistence and the five scheduler/ownership regressions were selected.
Historical USB/NVS observations remain in previous evidence, not reclassified to improve totals.
Exact names/stdout/status/assertions are in stage25-results.json and stage25-test-index.md.

Intermediate issues were resolved and retained in the work record: initial native mock File/
String APIs were incomplete; clean compilation initially passed but legacy validation
expected a padded merged image; separate-artifact validation was added only when actual
build.options records merge-hook suppression. Legacy merged validation remains when that
hook is not disabled. Initial compiles were revalidated; then meaningful AP hardening
changes triggered new final clean builds. No failing compiler/test is called successful.

## Final clean builds

Arduino ESP32 3.3.0 / ESP-IDF5.5 / GCC14.2, 16MiB custom table, PSRAM disabled,
QIO80/240MHz, USB-OTG/TinyUSB/CDC, original isolated core guards. Global core/SDK untouched.
Three production-dependency builds suppress Arduino's merged output; the existing isolated
readonly builder discards its automatic merged side output. No merged file is supplied.

FQBN: `esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default`.

| Profile | Program B | BIN B | Static RAM B | Free OTA B | Free % |
|---|---:|---:|---:|---:|---:|
| Existing normal | 1329487 | 1329632 | 82248 | 6272544 | 82.50985 |
| Deployment-safe | 1065987 | 1066128 | 78280 | 6536048 | 85.97602 |
| **Controlled normal candidate** | **1329619** | **1329760** | **82248** | **6272416** | **82.50817** |
| Experimental readonly | 1069995 | 1070144 | 78288 | 6532032 | 85.92319 |

Against Stage24: normal program -4/BIN0/RAM0; safe program+16/BIN+16/RAM0;
readonly0/0/0. Controlled versus Stage24 normal: program+128/BIN+128/RAM0.
Small binary/metadata/code differences are not physical memory measurements. Controlled
compiler estimates: setup80B, loop32B, settings.load128B, checked AP helper112B; maximum
per-function1184B. Callees, SDK costs, real heap and task-stack high-water remain unmeasured.
The gate has a fixed six-entry static flash table and one temporary SDK iterator, not a
new dynamic ownership structure. No new parser architecture or report queue is introduced.

All final app/ELF/bootloader/table hashes, core/SDK identities and profile/linked guard
receipts are in stage25-artifact-inventory.json and the four profile provenance files.
Application SHA-256:

- Normal: `6c36e73afc84b77d3105a107158c862409ac720dd217338ab1b705efa0632cf9`
- Safe: `b0b0b17a5fdf2761f89bc2d1131db9e0e4980686cf2092b65677929f9dae5020`
- Controlled: `f4c280322db16f345bd88523bec119b1014f9123d0026494527a800203778446`
- Readonly: `e3fff2a52b0814bc292c5a2f7e8012dda1a392faa0051ec4d195ea559f385695`

## Remaining NO-GO gates and next review

1. **BLOCKED:** verify an actual owner recovery image/build or owner-local privacy-safe
   resource receipt and known-good provenance. Stock source discovery is not needed.
2. **BLOCKED:** approve private fresh credentials/NVS and empty SPIFFS artifact identities,
   plus the exact paired bootloader/table/OTA/application/coredump range plan. Existing
   protected-NVS migration planners are not secretly reused for a fresh NVS replacement.
3. **BLOCKED:** owner-controlled ROM/cable/power/security/current-device readiness and
   separate physical installation/readback/first-boot authorization.

Physical USB, Wi-Fi/AP/authentication, SPIFFS/SD, timing/heap/stack acceptance follows an
approved controlled installation. It is not falsely marked failed or already passed.
Exact old-data preservation and further language development are not deployment prerequisites.

**GO for owner offline recovery/artifact review. NO-GO for physical installation/boot/OTA.**
Recommend Stage26 focus on owner resource/private artifact receipts and the deployment review,
not another architecture or language stage. No hardware, flash/erase/format/OTA, real HID,
owner-file modification or stored owner payload execution occurred. Stop for review.
