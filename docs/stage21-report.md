# Stage 21 read-only NVS protection and quiescent boot validation

Baseline: `stage20-nvs-preservation-contract`,
`7c4559132251340b03bcb68a3d66d04d1659e503`. Development branch:
`stage21-readonly-nvs-quiescent-validation`. The commit containing this report identifies
the delivered investigation/tests. Production source remains byte-identical to the baseline.

## Answer

**Qualified yes at the verified SDK software boundary; not yet a certified complete
first-boot preservation profile.** The pinned environment supports readonly NVS and
blocks all tested standard mutation paths with that property active. A second main-flash
OS guard also rejects ordinary direct main-chip writes/erases and writable aliases by
consulting canonical readonly table regions. Complete early boot, RTOS/ROM/driver paths,
physical flash behavior and a fail-closed paired profile/table selector are not established.

This stage is **design/test-only**, with no production patch, partition change, replacement
SDK, or third experimental firmware. Existing normal and deployment-safe profiles were
clean-built and verified. A flagged table is generated only in a temporary offline test,
explicitly experimental; existing production builders reject it. It is not a deployment
artifact. Physical migration, application boot and OTA remain **NO-GO**. Stage22 has not
begun.

## Main findings

1. Official tooling encodes `readonly` as partition flag bit1, mask2. Native loader
   instructions extract that bit into descriptor byte42; actual target headers confirm
   that offset. Native `NVSPartition::get_readonly()` loads the flag through its descriptor.
2. Partition write/raw/erase checks return NOT_ALLOWED before reaching the lower driver.
   This applies during Page scanning, not merely after `setup()`.
3. The deeper `main_flash_region_protected` callback first checks all canonical readonly
   regions, before its dangerous-write exemption. `CHECK_WRITE_ADDRESS` dispatches it
   in main-chip write/erase source. Actual flash archive evidence supports the callback,
   API and OS-function installation paths. Disabling dangerous-write protection does
   not disable this readonly check.
4. Early permissive-adapter trials did not model that second guard and allowed direct/
   alias writes. They are **not evidence of a default SDK main-driver bypass**. Final
   native tests execute exact region scan/callback/dispatch source; main direct/alias and
   pointer-initializer attempts are denied without synthetic byte changes.
5. Missing callbacks, deliberately altered canonical metadata and custom/ROM/raw routes
   remain limitations. A null partition iterator makes the readonly scan return writable;
   this is not proof that the complete driver would then permit writing, since other
   checks may fail/abort. It reinforces the need for a pre-init expected-descriptor gate.
6. Read-only initialization may return success with FREEING/no-spare recovery skipped,
   or denied orphan/index cleanup ignored. This is not a health certificate. Read-only
   handles on writable partitions still allow SDK corrupt-read cleanup.
7. Actual production settings loading via the real source C API preserves healthy
   synthetic settings; corrupt-read denial latches application failure before services.
   Safe-start skips settings loading and application services even with valid NVS.
8. Normal-profile code still activates services when its NVS happens to be readonly.
   A readonly table alone is not a quiescent profile. No existing profile was silently
   changed to become permanently readonly.

Detailed [contract](stage21-preservation-contract.md),
[startup-path analysis](stage21-startup-analysis.md),
[bypass analysis](stage21-bypass-analysis.md),
[readiness](stage21-readiness.md), [reproduction](stage21-reproduction.md).

## Owner evidence and startup scope

The owner reports local High Sierra10.13.6 full preflight/summary PASS, matching all three
expected backup hashes/sizes, original firmware/partition checks PASS, SPIFFS roundtrip
PASS, and NVS compatible-within-verified-checks with zero findings. Migration authorization
remains false. Recorded in [stage21-owner-evidence.json](stage21-owner-evidence.json),
with earlier Stage19/20 reports unchanged. No original binary/private report was supplied
or independently inspected here; current physical NVS freshness is not measured.

Both linked ELFs contain **36 ordinary constructor entries and24 system-init records**,
all inventoried against actual native addresses. Selected disassembly/source establishes
system-init before constructors, USB/CDC before Arduino NVS initialization, then loop-task
setup. The linked flash-init hook calls `esp_flash_init_default_chip` and
`esp_flash_app_init`; this is instruction/source evidence, not execution of that entire
driver chain. Source and compiled identities are separate from source/binary equivalence.

Global HID and MSC registration precedes app guards: safe-start does not promise absent
USB descriptors or silent USB enumeration. MSC starts with media absent and no backing
callbacks, while its SDK writable boolean defaults true. No backing image is activated
by safe-start. OTA rollback verification and coredump initialization can involve their
own flash regions; these are not NVS writes. Complete transitive/ROM/closed-source audit
and physical behavior remain open.

## Executed tests

All existing Stage1–20 suites were actually rerun, including both Stage20 blob suites,
Stage2.5 migration/partition guards and the separately classified historical observations.
Exact every-test names/status/assertions/raw diagnostics and address records are in
[stage21-results.json](stage21-results.json).

| Group | PASS | Unexpected FAIL | Other |
| --- | ---: | ---: | --- |
| Existing Stage1–20 contract suites | 1170 | 0 | 636958 assertions including established separate observations/diagnostics |
| New actual source C API/settings/startup/region tests | 40 | 0 | 11 OBSERVED |
| New flag/target-archive/ELF/provenance tests | 10 | 0 | Inspect/compile; no hardware |
| Combined current suites | **1220** | **0** | Historical classifications separate |

**637970 assertions**, including1012 in the new source/integration tests and established
diagnostic/observation assertions. No unsupported observation is counted as a compatibility pass. Historical language
diagnostics remain **5 XPASS**. Historical upstream HID remains **39 PASS /6 expected
XFAIL /7 observations**. Stage9 remains **79 matched observations /0 mismatches**.
Stage16/17/18/20 prior risk observations remain separately retained.

All current native C++ suites pass ASan/UBSan, including actual plaintext C API, partition
lookup/manager/handle/Storage/Page and production settings/core/setup integration.
Actual Linux no-op lock branch, synthetic descriptors/flash/CRC/iterator and application
transport spies remain. The complete Xtensa library, RTOS/global-constructor execution,
SPI driver, ROM and physical device are not executed. Historical unpatched HID sanitizer
faults remain expected diagnostic XFAIL; Python/assembly inspection is not a sanitizer target.

Coverage includes clean/empty data, repeated init/failure, corrupt pages/entries/strings/
blobs, cross-page blobs, FREEING, interrupted writes, unsupported version, missing/encrypted
partition, read/partial-read errors, denied writes/erase/GC, canonical/global guards,
alias/pointer API, changed callbacks/metadata, source tampering, profile identity and
normal/safe startup with real settings reads. All protected-case snapshots remain exact;
intentional fixture preparation and observed writable/missing-policy cases use synthetic
RAM-backed flash only. Protected attempt and lower-operation ranges are recorded.

Development trials exposed adapter linkage/main-renaming issues and incorrect expectations
about source behaviors: no-spare readonly init can succeed, an initially malformed index
fixture did not represent intended orphan cleanup, and normal settings-error diagnostics
include three calls. Fixtures/assertions were corrected against inspected source, and
the final results rerun. No production workaround or historical classification was changed.
The deeper flash guard discovery is retained explicitly rather than misrepresenting the
weaker initial adapter as a real SDK bypass.

## Clean isolated firmware builds

Both builders applied only Stage16 HID and Stage18 Arduino patches in independent disposable
copies. Installed core/SDK stays unchanged. Final linked profile, routing, original-error
policy, settings validation/checked persistence and ELF-to-bin provenance were verified.

FQBN:

`esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default`

| Measurement | Normal | Deployment-safe |
| --- | ---: | ---: |
| Compiler program bytes | 1329491 | 1065971 |
| Actual application bytes | 1329632 | 1066112 |
| Static RAM bytes | 82248 | 78280 |
| Application growth vs Stage20 | 0 | -16 |
| Program growth vs Stage20 | 0 | -16 |
| Static RAM growth | 0 | 0 |
| Free bytes in each740000 OTA slot | 6272544 | 6536064 |
| Free percentage per slot | 82.509850% | 85.976226% |

The 16-byte safe difference is build-path/rodata/alignment-related; source is unchanged.
Fresh images embed new build timestamps and paths, so hash identity is not byte-identical
rebuild reproducibility. All455 normalized per-function compiler stack records match
Stage20 in each profile. Largest inspected frame is CLI executeCommand1184B, followed by
returnFunction1072B; these are estimates excluding callees, and safe LTO may discard a
function. No new production persistent buffers/allocations exist. Physical heap/task
high-water and flash-latency measurements are unavailable. Iterator allocation/locking
under denied lower calls remains a source ownership review item, not a certified target leak.

Normal application SHA256:
`b80c1c0e8d9e6a7018c3a49b8b82e203db93a64c848cc1ca7be4a1bdd75b460c`

Safe application SHA256:
`743a3db1c3e663323b750242e81908c55785e86f39dbd61fae0534cef09e7c95`

Normal requires the proposed larger slot: it exceeds original140000 slots by18912B.
Safe fits the old size, but **is not approved for old-layout OTA/boot** and has no readonly
NVS requirement. Both compiled images use16MiB headers; neither indicates that the physical
device/table has migrated. Fresh build bins/ELFs stay in external build directories;
[artifact inventory](stage21-artifact-inventory.json) records exact hashes/sizes/regions,
not a write plan or deployment approval. Existing deployment/stage20 binaries are historical
and unchanged. Generated merged build output is not an approved migration artifact.

## Dependency identity

Arduino core3.3.0; ESP-IDF nominal commitb66b5448; GCC14.2.0; CLI1.3.1. Complete fields/hashes
are in [normal provenance](stage21-normal-provenance.json),
[safe provenance](stage21-safe-provenance.json), [source reference pin](stage21-reference-pin.json)
and native archive evidence inside stage21-results.json. Original/patched core trees,
patches, NVS archive/config pins are unchanged from Stage18:

- Original core tree: `27c2bae8bee6e4f8089417c048f41bfd255d7a80fab5e889bf74fb258112cb51`
- Patched core tree: `81c11f59e01c1e6263d387a008d3f3211319d94feb4751ddfa11af35a2a57ed3`
- NVS archive: `a1ac62b0f8b69ef2ac08e82dd1c57f58d53db74147bc309f070e36a148067a2e`
- SDK config: `06fcb22dee7956d54f1c7c05b0856ee87a362380697071fef2c26753fb14c271`

No SDK source rebuild, binary patch, guessed interception or globally installed modification.
New source files are references with immutable URLs/checksums, never toolchain replacements.

## Next reviewed milestone

Recommend Stage22 implement and verify an **isolated experimental quiescent profile**
with an exact pre-init descriptor/range/readonly requirement, keeping existing normal/safe
builders and production flags unchanged. Continue the boot/main-OS-installation and
missing-table/bypass closure audit. Tests must prove wrong/writable/missing metadata cannot
call the initializer; candidate identity must be distinct and never arm normal operation.
That milestone still does not authorize physical use.

GO for owner review and a separately authorized offline candidate milestone.
NO-GO for migration/application boot/OTA. No hardware, formatting, erase, update, real HID,
owner payload or private backup access occurred. Main/prior branches, Arduino Micro,
partitions and safeguards are preserved. Stage22 has not begun.

## Exact new test inventory

The following rows were executed in the final runs. Existing Stage1–20 names/results
are preserved in the complete stage21-results.json inventory.

| Test | Result | Assertions |
| --- | --- | ---: |
| readonly_clean | PASS | 15 |
| readonly_repeat | PASS | 25 |
| readonly_cross_page_blob | PASS | 16 |
| readonly_interrupted_entry | PASS | 17 |
| readonly_bad_entry_crc | PASS | 17 |
| readonly_bad_page_crc | PASS | 17 |
| readonly_invalid_state | PASS | 17 |
| readonly_freeing | OBSERVED | 15 |
| readonly_future_version | PASS | 13 |
| readonly_read_failure | PASS | 13 |
| readonly_partial_read | PASS | 13 |
| readonly_missing_partition | PASS | 13 |
| readonly_encrypted_partition | PASS | 13 |
| readonly_empty_partition | PASS | 13 |
| readonly_no_free_page | OBSERVED | 15 |
| readonly_orphan_blob | OBSERVED | 19 |
| readonly_mismatched_index | OBSERVED | 19 |
| readonly_corrupt_string | PASS | 22 |
| readonly_corrupt_blob | PASS | 24 |
| readonly_blob_gap | OBSERVED | 28 |
| readonly_open_write | PASS | 14 |
| readonly_set | PASS | 15 |
| readonly_erase_api | PASS | 18 |
| readonly_gc_request | PASS | 12 |
| partition_api_write | PASS | 11 |
| partition_api_raw | PASS | 11 |
| partition_api_erase | PASS | 11 |
| writable_readonly_handle_corrupt_string | OBSERVED | 13 |
| main_direct_write_rejected | PASS | 11 |
| main_direct_erase_rejected | PASS | 11 |
| main_descriptor_alias_rejected | PASS | 13 |
| callback_missing_write | OBSERVED | 6 |
| callback_missing_erase | OBSERVED | 6 |
| canonical_flag_changed | OBSERVED | 6 |
| main_region_no_protect | PASS | 9 |
| main_region_boundaries | PASS | 12 |
| readonly_retry_failure | PASS | 67 |
| readonly_backend_write_error | PASS | 17 |
| readonly_partition_ptr | PASS | 11 |
| main_partition_ptr_alias_rejected | PASS | 16 |
| region_scan_missing_table | OBSERVED | 9 |
| normal_healthy_writable | PASS | 21 |
| normal_healthy_readonly | OBSERVED | 22 |
| normal_invalid_readonly | PASS | 37 |
| normal_missing_readonly | PASS | 33 |
| normal_settings_corrupt_readonly | PASS | 43 |
| safe_healthy_writable | PASS | 32 |
| safe_healthy_readonly | PASS | 32 |
| safe_invalid_readonly | PASS | 37 |
| safe_missing_readonly | PASS | 33 |
| safe_settings_corrupt_readonly | PASS | 39 |
| readonly_flag_binary_roundtrip_and_production_rejection | PASS | 7 |
| readonly_flag_official_source_identity | PASS | 1 |
| actual_native_readonly_descriptor_abi | PASS | 1 |
| actual_target_archive_readonly_guards_and_startup_evidence | PASS | 12 |
| supplied_bootloader_entry_identity | PASS | 1 |
| early_startup_source_ordering | PASS | 2 |
| both_clean_linked_profiles_and_prior_guards | PASS | 4 |
| both_linked_startup_array_inventories_and_invalid_elf | PASS | 9 |
| owner_evidence_and_no_go_boundaries | PASS | 2 |
| modified_startup_reference_rejected | PASS | 1 |

## Modified and created files

All changes are new Stage21 files; existing production/tests/partitions/patches and prior reports remain unchanged.

- `docs/stage21-archive-lib_libapp_update.a-esp_ota_mark_app_valid_cancel_rollback.txt`
- `docs/stage21-archive-lib_libesp_partition.a-ensure_partitions_loaded_part_0.txt`
- `docs/stage21-archive-lib_libesp_partition.a-esp_partition_erase_range.txt`
- `docs/stage21-archive-lib_libesp_partition.a-esp_partition_is_flash_region_writable.txt`
- `docs/stage21-archive-lib_libesp_partition.a-esp_partition_write.txt`
- `docs/stage21-archive-lib_libesp_partition.a-esp_partition_write_raw.txt`
- `docs/stage21-archive-lib_libnvs_flash.a-_ZN3nvs11PageManager4loadEPNS_9PartitionEmm.txt`
- `docs/stage21-archive-lib_libnvs_flash.a-_ZN3nvs12NVSPartition12get_readonlyEv.txt`
- `docs/stage21-archive-lib_libnvs_flash.a-nvs_flash_init.txt`
- `docs/stage21-archive-lib_libnvs_flash.a-nvs_flash_init_partition.txt`
- `docs/stage21-archive-qio_qspi_libesp_system.a-start_cpu0.txt`
- `docs/stage21-archive-qio_qspi_libspi_flash.a-esp_flash_app_enable_os_functions.txt`
- `docs/stage21-archive-qio_qspi_libspi_flash.a-esp_flash_erase_region.txt`
- `docs/stage21-archive-qio_qspi_libspi_flash.a-esp_flash_set_dangerous_write_protection.txt`
- `docs/stage21-archive-qio_qspi_libspi_flash.a-esp_flash_write.txt`
- `docs/stage21-archive-qio_qspi_libspi_flash.a-main_flash_region_protected.txt`
- `docs/stage21-artifact-inventory.json`
- `docs/stage21-bypass-analysis.md`
- `docs/stage21-normal-build.log`
- `docs/stage21-normal-linked-nvs.txt`
- `docs/stage21-normal-linked-routing.txt`
- `docs/stage21-normal-linked-startup.txt`
- `docs/stage21-normal-provenance.json`
- `docs/stage21-normal-resources.json`
- `docs/stage21-normal-stack.json`
- `docs/stage21-normal-startup-inventory.json`
- `docs/stage21-owner-evidence.json`
- `docs/stage21-preservation-contract.md`
- `docs/stage21-readiness.md`
- `docs/stage21-reference-pin.json`
- `docs/stage21-report.md`
- `docs/stage21-reproduction.md`
- `docs/stage21-results.json`
- `docs/stage21-safe-build.log`
- `docs/stage21-safe-linked-nvs.txt`
- `docs/stage21-safe-linked-routing.txt`
- `docs/stage21-safe-linked-startup.txt`
- `docs/stage21-safe-provenance.json`
- `docs/stage21-safe-resources.json`
- `docs/stage21-safe-stack.json`
- `docs/stage21-safe-startup-inventory.json`
- `docs/stage21-startup-analysis.md`
- `tests/stage21/README.md`
- `tests/stage21/integration_tests.py`
- `tests/stage21/mocks/esp_partition.h`
- `tests/stage21/mocks/sdkconfig.h`
- `tests/stage21/nvs_readonly.cpp`
- `tests/stage21/run_tests.py`
- `tests/stage21/startup_integration.cpp`
- `tools/inspect_startup_elf.py`
- `tools/startup_reference_prepare.py`
