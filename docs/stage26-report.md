# Stage26 final installation readiness report

REVIEW ONLY — NOT AUTHORIZED FOR FLASHING

Baseline: Stage25 controlled-first-boot commit f929bdf2353e0022f10c164d2c09cb3db2564a5a.
Delivery branch: stage26-installation-readiness. Stage27 is not started.

**Original firmware: OWNER CONFIRMED — AVAILABLE EXTERNALLY.** No firmware availability
blocker, request, search, download or reconstruction. Exact old firmware/NVS/settings/scripts/
filesystem preservation is not required. Existing backups stay untouched. Actual physical
recovery capability and artifact compatibility remain distinct from resource availability.

## Completed preparation — PASS offline

No production firmware, DuckyScript engine, settings schema, USB identity, partition metadata
or existing profile behavior changed. Stage25's controlled candidate is the future installation
selection; legacy normal is not substituted. Existing readonly and safe profiles remain separate.

Added a public seven-file review set, representing seven initial public roles (the application
is reused for both slots) plus a separate quiescent fallback. Bootloader/table/OTA/controlled
application are from new clean protected-core builds. Empty SPIFFS and all-FF coredump data
are generated and checked. A machine-readable manifest defines each role, purpose, bytes,
SHA-256, offset, region boundary, rounded erase footprint and false authorization status.
No padded full-chip image or private owner NVS is published.

The new validator rejects wrong target/header/table/address/geometry, overlaps, missing/corrupt
images, unsafe erase footprints, oversized applications, wrong OTA metadata, mixed profiles,
symlinks and mismatched trusted pins. It checks both application positions. Exact pin trust
comes from the reviewed checkout, not self-authenticating image manifests or digital signatures.

Private provisioning reuses pinned Stage24/25 generators. Stage26 preparation requires both
passwords to be at least12 UTF-8 bytes, rejects the public legacy AP password, and retains explicit
SSID/AP/web inputs. This is a preparation policy, not a change to Stage25 runtime semantics or
an entropy proof. Strong distinct random passwords are recommended. The tool regenerates and
byte-compares the complete typed NVS schema, rather than assuming that structural validity
means safe credentials. Autorun is false and path empty. Private SPIFFS must equal the public
empty filesystem. Private receipt adds the sole missing NVS role at0x9000/0x5000 and validates
all eight ranges. No owner values are logged. Outputs cannot replace an existing directory;
interrupted public publication leaves no accepted manifest.

No physical flash writer exists in these tools. The planned fresh NVS replacement is a future
explicit authorization item; existing preserved-NVS migration validators were not weakened.

## Startup verification

Actual selected production source is tested with synthetic typed NVS, partition, storage, USB,
clock and application-service adapters. Successful fresh startup and failures for credentials,
NVS reads/types, layout, SPIFFS mount, Wi-Fi mode/AP creation and interrupted startup are checked.
The candidate uses SPIFFS.begin(false), skips bundled examples, rejects stored autorun and stops
critical services on failure. A failed setup cannot automatically re-arm. Application HID
infrastructure is only initialized after the relevant critical checks; no payload executes.
This is not complete native SDK startup or host USB evidence. SDK writable NVS may perform
normal recovery or Wi-Fi writes; original-byte immutability is neither promised nor required.

## Executed tests

| Group | PASS | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| New artifact/provisioning/real generation and interruption checks | 41 | 0 | 41 |
| Affected production-source startup regressions | 30 | 0 | 635 |
| Production AP helper fault regressions | 6 | 0 | 23 |
| **Total current execution** | **77** | **0** | **699** |

C++ startup/network tests are ASan/UBSan clean; startup enables leak detection. New Python/file
checks really execute the pinned NVS generator and mkspiffs. ASan does not apply to Python or
prove the precompiled desktop filesystem tool's internals. No actual owner files were tested;
synthetic credentials and temporary files were removed. Public re-preparation produces the
same pinned set, and fault injection during publication prevents acceptance of partial output.
All exact test names/results are in stage26-test-index.md and stage26-results.json.

Only relevant regressions were rerun, as requested. Historical language XPASS, upstream USB
XFAIL, Stage9 observations and earlier SDK/NVS risks remain unchanged and were not relabeled
or added to these totals. Earlier complete-stage counts are not presented as current execution.

## Clean builds and resources

Both relevant profiles clean-built in new disposable cores/output directories, using verified
Arduino ESP32 3.3.0, ESP-IDF5.5 and Xtensa GCC14.2. PSRAM stays disabled; CPU240MHz,
16MiB custom table, USB-OTG/TinyUSB/CDC and QIO80 configuration are retained. No globally
installed core/SDK was modified. Every linked provenance guard passed. No warning lines were
reported in the captured final build logs. Exact source/core/SDK/compiler/ELF/app hashes and
FQBN are in stage26-controlled-build.json and stage26-safe-build.json.

| Profile | Program B | BIN B | Static RAM B | Free/0x740000 slot B | Free % |
|---|---:|---:|---:|---:|---:|
| Controlled normal | 1329619 | 1329760 | 82248 | 6272416 | 82.508166 |
| Deployment-safe | 1065987 | 1066128 | 78280 | 6536048 | 85.976015 |

Program/BIN/RAM growth from corresponding Stage25 profiles: **0/0/0**. Application hashes
changed across fresh build metadata/output contexts and are pinned afresh; no runtime source
behavior changed. App SHA controlled: a2087f560f60b03990f8133591dffa218f0414e15dc87530c215f8949a4758c4.
App SHA safe: 93160306c9668e59e7e8f03577c498b5ea43ef9e4c71b0b0686116889c793127.

Selected compiler stack analysis produced457 controlled records,458 safe records; maximum
per-function estimate1184B in both. Controlled setup80B/loop32B/settings.load128B/checkedAP112B,
unchanged from Stage25. These estimates exclude callees/library costs; safe compiled-out paths
can still appear in source-level stack records. No physical heap, stack high-water, timing or
allocation measurements are claimed. Stage26 adds no embedded buffers or allocations.

Actual image headers advertise ESP32-S3/16MiB/80MHz/**DIO**, despite retained QIO build settings.
This existing quad-compatible Arduino encoding is explicitly checked/documented; it is not
silently reported as a QIO header. See stage26-compatibility.md for all hashes and intervals.
The controlled image is19040B too large for an original0x140000 app slot: app-only old-layout
installation is unsuitable. Matching new bootloader/table/OTA/both apps/fresh NVS/SPIFFS and
coredump initialization must be reviewed together. No full-chip erase is planned.

## Remaining genuine gates — BLOCKED, not technical FAIL

1. Owner-local explicit strong credentials, private fresh NVS generation/verification and
   receipt hash/range review. No credentials or original firmware are requested in chat.
2. Current physical session prerequisites: correct board/port, cable/power, ROM recovery,
   security and flash facts checked against previously supplied historical evidence. Actual
   new-candidate boot/recovery, USB and storage behavior remain untested.
3. Explicit owner approval of the complete fresh installation ranges, readback and controlled
   first boot. No physical operation is authorized by this software report.

High Sierra can inspect public prebuilt hashes without compiling. Python3.8.10/esptool4.12.0
are retained. Local compatible mkspiffs and cryptography availability are conditional private
preparation prerequisites; Linux compilation does not prove High Sierra compiler execution.
A separately reviewed environment can generate private files if local dependencies do not work.
No original-data retention requirement or further language feature is an installation prerequisite.

**GO:** owner-local private preparation and final installation review.
**NO-GO:** physical installation, boot, migration and OTA pending separate authorization.
Recommended Stage27: review the completed private/public image receipts, confirm physical ROM
readiness and authorize a tightly scoped owner-controlled installation/readback/first-boot session
when satisfied. Do not add another architecture or scripting stage before that practical milestone.

## Deliverable index

- stage26-compatibility.md: exact layout, hashes, ranges and image checks.
- stage26-installation-plan.md: non-executable installation/recovery ordering and stop conditions.
- stage26-private-preparation.md: private factory process and read-only High Sierra commands.
- stage26-readiness.md: simple offline/owner/authorization checklist.
- stage26-reproduction.md: clean isolated builds and focused test commands.
- stage26-results.json/test-index.md: exact executed evidence.
- stage26-controlled-build.json/safe-build.json and stack summaries: resource/provenance receipts.
- review/stage26-installation: seven public binary files, manifest, SHA256SUMS and review label.
- tools/stage26_installation.py/stage26_private.py/stage26_prepare.py and tests/stage26/run_tests.py.
- stage26-files.md: every added file; no existing tracked source was modified.

No hardware, flash/erase/format/OTA, real HID, stored owner script execution, owner-file edits,
stock-firmware search, private image upload or global dependency change occurred. All previous
branches must remain unchanged after the delivery push; that check is recorded in delivery.
Stage27 was not started. Physical installation remains unauthorized.
