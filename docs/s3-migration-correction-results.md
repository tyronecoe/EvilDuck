# Real-device migration correction: executed offline results

Date: 2026-10-10. This corrects Stage 2.5's assumed installed filesystem map;
it does not implement Stage 5 or perform migration. No hardware was accessed,
flashed, erased or formatted; no real HID was sent. PSRAM remains disabled.

## Evidence and architecture decision

The owner reported ROM-download verification with esptool 4.12.0: ESP32-S3
revision v0.2, 16 MB physical flash, quad/3.3 V flash, Secure Boot and Flash
Encryption disabled, SPI_BOOT_CRYPT_CNT zero, embedded 8 MB PSRAM. The supplied
raw-flash and partition-sector sizes/hashes are recorded in
[the corrected migration guide](s3-flash-migration.md#reported-real-device-evidence-and-corrected-installed-map).
The backup files themselves were not supplied to the cloud; their actual hashes,
contents and old filesystem decoding were not independently validated here.

The verified installed map has **five partitions**, SPIFFS at `0x290000` with
size **`0x170000`**, ending at `0x400000`, and **no coredump**. Earlier assumptions
came from the current Arduino core default CSV, which is not the device's table.
That assumption was wrong. The old helper's exact-map check would have rejected
this actual table before output; it did not have a valid migration path for it.
The corrected helper understands the real map and archives the full old data.

Retain the repository's reviewed A layout unchanged:

```csv
nvs,data,nvs,0x9000,0x5000,
otadata,data,ota,0xE000,0x2000,
app0,app,ota_0,0x10000,0x740000,
app1,app,ota_1,0x750000,0x740000,
spiffs,data,spiffs,0xE90000,0x160000,
coredump,data,coredump,0xFF0000,0x10000,
```

Alternative B retains old `0x170000` SPIFFS plus coredump but limits equal OTA
slots to `0x730000` each (7.1875 MiB), with an unused 64 KiB alignment gap.
Without coredump, B retains `0x740000` slots. Tests enumerate allowed 4 KiB
sizes with 64 KiB app-offset alignment and verify these maxima using Espressif's
tooling. A preserves approved OTA capacity and useful crash capture enabled in
the pinned core; full old filesystem capacity without coredump improves no OTA
headroom over A. Keep A **subject to proving actual files fit**. The 64 KiB
filesystem reduction is 4.35%; no file usage assumption is made. If exports
cannot fit safely, revisit B before migration rather than silently changing A.

## Corrected safety and file-level workflow

* `prepare` accepts the actual installed map, preserves the full `0x170000`
  source archive and NVS recovery bytes, and checks optional expected hashes.
  It invents no old coredump data. Destinations are null and raw relocation is
  explicitly disallowed in its archive manifest. Source size mismatch is explicit.
* The raw size guard rejects `0x170000 -> 0x160000`, short images and truncation.
  There is no flash-writing helper, serial discovery or device interface.
* `extract-files` optionally decodes the saved source with tested mkspiffs 0.2.3
  geometry after configuration/name/size checks. This must succeed on the actual
  backup locally; cloud synthetic success is not proof of that device's geometry.
* `inventory` hashes complete file sets; `pack-files` builds a **new `0x160000`**
  image, includes hidden/empty/binary/nested files, unpacks it and compares every
  path, size and hash. Data above 75% raw capacity is refused conservatively;
  metadata/GC overhead still requires successful packing and roundtrip checks.
* `verify-files` compares an independent later export of restored files with the
  saved file-level inventory. Migration remains incomplete until on-device file
  verification succeeds. Independent pre-migration exports remain recommended.

NVS stays at `0x9000`, size `0x5000`, and should be preserved in place. A full-chip
erase or padded merged-image write would destroy it and is not a migration path.
OTA metadata must be deliberately initialized for new app addresses. Coredump
must be initialized as a **new** region, not restored from imaginary old crash
storage. SD remains independent data storage and should be backed up separately.
`SPIFFS.begin(true)` remains unchanged; its automatic-format risk requires a
reviewed first-boot/restore plan, including autorun/HID isolation.

## Executed verification

Actual command:

```sh
python3 tests/stage25/run_tests.py \
  --core-dir /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /workspace/tooling/arduino/build/migration-final-stage4-16m
```

The unchanged firmware regression commands were also rerun:

```sh
python3 tests/stage2/run_tests.py --build-dir /workspace/tooling/arduino/build/migration-final-host
python3 tests/stage3/run_tests.py --build-dir /workspace/tooling/arduino/build/migration-final-host
python3 tests/stage4/run_tests.py --build-dir /workspace/tooling/arduino/build/migration-final-host
```

Stage 2 includes Stage 1. All completed with exit status zero.

| Suite | PASS | FAIL | XPASS | XFAIL | Assertions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Stage 1 regressions | 5 | 0 | 0 | 0 | 127 |
| Original language diagnostics | 0 | 0 | 2 | 3 | 12 sanity checks |
| Stage 2 | 30 | 0 | 0 | 0 | 797 |
| Corrected Stage 2.5 | 30 | 0 | 0 | 0 | 190 |
| Stage 3 | 40 | 0 | 0 | 0 | 13,815 |
| Stage 4 | 42 | 0 | 0 | 0 | 60,630 |
| **Total** | **147** | **0** | **2** | **3** | **75,571** |

No ASan/UBSan reports occurred in the instrumented C++ suites. Python validation
and the installed mkspiffs executable are not sanitizer-instrumented. No test
was skipped. The two prior conditional diagnostics remain resolved XPASS;
`known_false_while`, `known_f13_mapping`, `known_german_ascii_table` remain XFAIL.
The old `stage25_offline_spiffs_relocation_preserves_data` test is superseded by
source-archive and size-refusal tests, not treated as safe current functionality.

| Exact test name | Result | Assertions |
| --- | --- | ---: |
| `stage25_reviewed_partition_layout` | PASS | 15 |
| `stage25_overlapping_partitions_rejected` | PASS | 1 |
| `stage25_unaligned_application_rejected` | PASS | 1 |
| `stage25_reviewed_offsets_sizes_flags_enforced` | PASS | 10 |
| `stage25_core_version_pin_enforced` | PASS | 1 |
| `stage25_application_size_boundary` | PASS | 3 |
| `stage25_image_header_configuration_enforced` | PASS | 6 |
| `stage25_build_configuration_and_app_address_enforced` | PASS | 22 |
| `stage25_generated_16m_build_artifacts` | PASS | 4 |
| `stage25_corrupt_partition_binary_rejected` | PASS | 1 |
| `stage25_merged_image_wrong_address_rejected` | PASS | 1 |
| `stage25_stale_4m_partition_artifact_rejected` | PASS | 1 |
| `stage25_saved_physical_flash_capacity_guard` | PASS | 7 |
| `stage25_offline_source_archives_require_file_migration` | PASS | 11 |
| `stage25_offline_preparation_rejects_invalid_backups` | PASS | 6 |
| `stage25_offline_preparation_never_overwrites` | PASS | 2 |
| `stage25_build_wrapper_requires_clean_output` | PASS | 3 |
| `stage25_verified_device_map_differs_from_core_default` | PASS | 3 |
| `stage25_raw_spiffs_size_mismatch_refused` | PASS | 3 |
| `stage25_recorded_backup_hash_guards` | PASS | 4 |
| `stage25_file_level_extract_repack_roundtrip` | PASS | 8 |
| `stage25_file_level_empty_filesystem` | PASS | 1 |
| `stage25_file_level_capacity_and_overwrite_guards` | PASS | 7 |
| `stage25_corrupt_or_wrong_geometry_extraction_refused` | PASS | 4 |
| `stage25_alternative_layout_maximum_equal_slots` | PASS | 4 |

The actual installed partition tool and mkspiffs executable ran against synthetic
saved backups/file trees, not the owner's backups or device. Synthetic file
roundtrips included NUL/non-UTF-8 bytes, hidden files, .DS_Store, empty files,
nested names and spaces. Oversized/corrupt images, mismatched hashes, wrong maps,
links, long names, export-tree output, overwrites and capacity violations were
actually rejected. No actual-device filesystem extraction/restore is claimed.

## Firmware/build preservation

No `.cpp`, `.h`, `.ino`, partition CSV or build profile was changed by this
correction. A new clean firmware compilation completed successfully using the repository
wrapper in a new output directory. It validated the final Stage 4 build: core 3.3.0, PSRAM disabled,
16 MiB configuration, dual `0x740000` OTA slots, standard app0 `0x10000` and
reviewed table. Actual measurements from the new completed build are:

* Program: 1,297,079 bytes; application `.bin`: 1,297,232 bytes.
* Static RAM: 69,912 bytes.
* Free per OTA slot: 6,304,944 bytes / 82.9360%.
* Firmware/RAM growth for this Python/documentation-only correction: zero.

## Every changed/created repository file

Modified: `tools/s3_validation.py`, `tools/s3_migration.py`,
`tests/stage25/run_tests.py`, `docs/s3-flash-migration.md`,
`tests/stage25/README.md`, `tests/stage3/README.md`, `tests/stage4/README.md`.
The historical reports now warn that old assumed-map/raw-relocation results are
superseded; original executed results remain intact. Created:
`docs/s3-migration-correction-results.md` (this report) and
`tools/s3_write_plan.py` (review-only offline artifact/region planner).

## Additional requirements from the completed owner instruction

The full instruction is now reviewed. No language or firmware source change was
needed. Additional implementation adds a **review-only** region-plan generator
and five tests: NVS-safe writes/sector erases, identical apps in both slots,
OTA initializer validation, input/provenance/capacity refusals, and explicit
rejection of the Mac's core 2.0.17. The migration guide now specifies these facts:

* NVS is preserved in place; the write plan excludes `0x9000..0xE000`, including
  sector-rounded erases. Partition-table padding stops at `0x9000`. Check NVS
  readback before boot and settings after boot; raw preservation does not prove
  compatibility with a different old core. No normal-migration full erase/merged
  write is acceptable.
* OTA metadata contains sequence/slot/state, not absolute addresses. Preserving
  it may select the relocated app1 with stale/missing contents. Replace both
  sectors with pinned 3.3.0 `boot_app0.bin` (sequence 1, undefined state, valid
  CRC), selecting app0. Install the same compiled/mock-tested Stage 4 image
  at `0x10000` and `0x750000`; physical boot validation remains pending.
* Initial migration requires individual new bootloader, partition sector,
  metadata, both applications, complete new-size repacked filesystem and
  erased-state coredump images. The plan is not a hardware-writing helper.
  Newly introduced coredump is all 0xFF initially, not imaginary historical data.
* The guide includes an explicitly labeled **destructive manual recovery**
  example using the verified original full image in ROM mode, preserving original
  headers with esptool 4.12.0 `keep` flags. Full recovery restores old matching
  regions/NVS together. Read-only readback must reproduce recorded full/sector
  hashes. No destructive command is run by a test or helper.
* Python 3.8.10/esptool 4.12.0 remain adequate; no mandatory upgrade. Mac core
  2.0.17 must be replaced/selected as pinned 3.3.0 for compilation. The wrapper
  rejects the wrong active core before compilation. Mac tool/OS compatibility
  for 3.3.0 is not proven in this Linux cloud.
* If actual old SPIFFS geometry cannot be established, use an explicitly reviewed,
  HID-isolated device-assisted **byte-level file export/restore**. Confirm every
  path, hidden/binary file and hash; editor text export or basename-only upload
  is not sufficient for all files. Do not guess geometry or silently omit files.

Additional incorrect assumptions corrected: same-size raw relocation, imaginary
old crash storage, treating generic core defaults as the installed table,
implicitly trusting retained OTA selection after relocation, and treating a
new table/application-only OTA as a sufficient migration. Earlier 5.x examples
are retained as optional alternatives, not a requirement for this Mac. The Mac's
installed core version is not evidence of the core used by the old firmware.

Clean-build command actually executed:

```sh
XDG_CACHE_HOME=/workspace/tooling/arduino/cache python3 tools/build_s3.py \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli \
  --config-file /workspace/tooling/arduino/arduino-cli.yaml \
  --build-dir /workspace/tooling/arduino/build/migration-final-stage4-16m --jobs 2
```

Build exit status: zero. Compiler program usage 1,297,079 B (17%), application
1,297,232 B, static RAM 69,912 B (21%), reported remaining RAM 257,768 B.
Application/RAM growth versus approved Stage 4: **0 B / 0 B**. Each slot remains
7,602,176 B with 6,304,944 B free (82.9360436%). New application SHA-256:
`bfdbb34f11be48723d25d01c7e5f2f4c9047a7cb10a32ac87922e67ceab3cb90`.
Fresh build artifacts/headers/properties validate ESP32-S3, 16 MiB/80 MHz,
PSRAM disabled, custom partition table, app0 at `0x10000`, and pinned core 3.3.0.
The build report's `hardware_verified: false` means compilation offers no hardware
verification; it does not negate the owner's separately reported physical evidence.
Python 3.8 syntax checks passed for all three migration/validation helpers; running
them on the actual Mac and its mkspiffs executable remains a local check.

## Complete exact test results from this rerun

All tests below were actually executed. Stage 1–4 fixtures use mocked HID,
clock/storage/output; none delivers real HID. ASan/UBSan-instrumented C++ tests
completed without sanitizer/leak reports. Python helpers and installed mkspiffs
are not sanitizer-instrumented. No tests skipped. Twelve original diagnostic
sanity assertions are included in the total 75,571; XPASS/XFAIL remain separate
from the 147 passing regression/validation cases.

| Exact test name | Result | Assertions |
| --- | --- | ---: |
| `supported_commands_and_mock_interfaces` | PASS | 29 |
| `script_run_state_isolation` | PASS | 22 |
| `cooperative_delay_and_text_cancellation` | PASS | 33 |
| `repeat_timing_and_control_loop_yield` | PASS | 24 |
| `live_commands_cannot_mutate_running_script` | PASS | 19 |
| `stage2_rem_comments` | PASS | 6 |
| `stage2_required_rem_block_fixture` | PASS | 12 |
| `stage2_comment_block_literal_commands` | PASS | 6 |
| `stage2_unterminated_rem_block_zero_hid` | PASS | 9 |
| `stage2_unmatched_end_rem_zero_hid` | PASS | 9 |
| `stage2_lf_source` | PASS | 6 |
| `stage2_crlf_source` | PASS | 6 |
| `stage2_utf8_bom` | PASS | 21 |
| `stage2_missing_final_newline` | PASS | 12 |
| `stage2_blank_lines` | PASS | 12 |
| `stage2_spaces_tabs_and_payload_preservation` | PASS | 7 |
| `stage2_maximum_line_length` | PASS | 12 |
| `stage2_overlong_line_zero_hid` | PASS | 18 |
| `stage2_source_byte_limits` | PASS | 16 |
| `stage2_source_line_limits` | PASS | 15 |
| `stage2_mismatched_control_blocks_zero_hid` | PASS | 18 |
| `stage2_unterminated_control_blocks_zero_hid` | PASS | 36 |
| `stage2_duplicate_else_zero_hid` | PASS | 18 |
| `stage2_block_depth_limit_zero_hid` | PASS | 9 |
| `stage2_text_blocks_literal_mode_and_deferred_runtime` | PASS | 36 |
| `stage2_unterminated_text_blocks_zero_hid` | PASS | 18 |
| `stage2_unmatched_text_terminators_zero_hid` | PASS | 18 |
| `stage2_mismatched_text_terminators_zero_hid` | PASS | 27 |
| `stage2_unknown_commands_zero_hid` | PASS | 27 |
| `stage2_keyword_prefixes_are_not_commands` | PASS | 128 |
| `stage2_malformed_statements_zero_hid` | PASS | 210 |
| `stage2_supported_extensions_and_bare_keys` | PASS | 8 |
| `stage2_storage_read_seek_faults` | PASS | 25 |
| `stage2_preflight_cooperative_stop_and_live_ownership` | PASS | 18 |
| `stage2_live_validation_and_limits` | PASS | 34 |
| `stage25_reviewed_partition_layout` | PASS | 15 |
| `stage25_overlapping_partitions_rejected` | PASS | 1 |
| `stage25_unaligned_application_rejected` | PASS | 1 |
| `stage25_reviewed_offsets_sizes_flags_enforced` | PASS | 10 |
| `stage25_core_version_pin_enforced` | PASS | 1 |
| `stage25_application_size_boundary` | PASS | 3 |
| `stage25_image_header_configuration_enforced` | PASS | 6 |
| `stage25_build_configuration_and_app_address_enforced` | PASS | 22 |
| `stage25_generated_16m_build_artifacts` | PASS | 4 |
| `stage25_corrupt_partition_binary_rejected` | PASS | 1 |
| `stage25_merged_image_wrong_address_rejected` | PASS | 1 |
| `stage25_stale_4m_partition_artifact_rejected` | PASS | 1 |
| `stage25_saved_physical_flash_capacity_guard` | PASS | 7 |
| `stage25_offline_source_archives_require_file_migration` | PASS | 11 |
| `stage25_offline_preparation_rejects_invalid_backups` | PASS | 6 |
| `stage25_offline_preparation_never_overwrites` | PASS | 2 |
| `stage25_build_wrapper_requires_clean_output` | PASS | 3 |
| `stage25_verified_device_map_differs_from_core_default` | PASS | 3 |
| `stage25_raw_spiffs_size_mismatch_refused` | PASS | 3 |
| `stage25_recorded_backup_hash_guards` | PASS | 4 |
| `stage25_file_level_extract_repack_roundtrip` | PASS | 8 |
| `stage25_file_level_empty_filesystem` | PASS | 1 |
| `stage25_file_level_capacity_and_overwrite_guards` | PASS | 7 |
| `stage25_corrupt_or_wrong_geometry_extraction_refused` | PASS | 4 |
| `stage25_alternative_layout_maximum_equal_slots` | PASS | 4 |
| `stage25_review_only_plan_preserves_nvs_and_initializes_both_apps` | PASS | 24 |
| `stage25_write_and_erase_region_guards` | PASS | 13 |
| `stage25_ota_initializer_selects_app0_deterministically` | PASS | 7 |
| `stage25_plan_refuses_unverified_files_and_backup_provenance` | PASS | 16 |
| `stage25_mac_old_core_rejected_before_compile` | PASS | 1 |
| `stage3_addition` | PASS | 3 |
| `stage3_subtraction` | PASS | 3 |
| `stage3_multiplication` | PASS | 3 |
| `stage3_division` | PASS | 3 |
| `stage3_modulo` | PASS | 3 |
| `stage3_exponentiation` | PASS | 3 |
| `stage3_equality` | PASS | 3 |
| `stage3_inequality` | PASS | 3 |
| `stage3_less_than` | PASS | 3 |
| `stage3_greater_than` | PASS | 3 |
| `stage3_less_or_equal` | PASS | 3 |
| `stage3_greater_or_equal` | PASS | 3 |
| `stage3_logical_and` | PASS | 3 |
| `stage3_logical_or` | PASS | 3 |
| `stage3_bitwise_and` | PASS | 3 |
| `stage3_bitwise_or` | PASS | 3 |
| `stage3_left_shift` | PASS | 3 |
| `stage3_right_shift` | PASS | 3 |
| `stage3_precedence_and_grouping` | PASS | 54 |
| `stage3_literals_booleans_and_whitespace` | PASS | 54 |
| `stage3_arithmetic_boundaries` | PASS | 57 |
| `stage3_invalid_literals_and_unsupported_operators` | PASS | 54 |
| `stage3_malformed_expressions_and_limits` | PASS | 54 |
| `stage3_numeric_declarations_assignment_and_no_hid` | PASS | 9 |
| `stage3_required_fixture_spiffs_and_sd` | PASS | 12 |
| `stage3_variable_references_types_and_atomic_failure` | PASS | 24 |
| `stage3_text_compatibility_alias_and_read` | PASS | 41 |
| `stage3_identifier_validation_and_table_exhaustion` | PASS | 91 |
| `stage3_preflight_zero_hid_and_runtime_errors` | PASS | 46 |
| `stage3_define_global_forward_and_word_matching` | PASS | 24 |
| `stage3_define_single_pass_and_declaration_exemption` | PASS | 32 |
| `stage3_define_comment_and_text_modes` | PASS | 25 |
| `stage3_define_duplicates_invalid_and_table_limits` | PASS | 76 |
| `stage3_define_expansion_and_pool_boundaries` | PASS | 32 |
| `stage3_expression_timing_counts_and_cancellation` | PASS | 17 |
| `stage3_collection_preflight_stop_and_state_isolation` | PASS | 27 |
| `stage3_interpolation_overflow_runtime_safe_stop` | PASS | 6 |
| `stage3_syntax_mode_does_not_evaluate_runtime_values` | PASS | 3 |
| `stage3_bounded_expression_fuzz` | PASS | 3001 |
| `stage3_expression_hot_path_no_heap` | PASS | 10022 |
| `stage4_simple_true_if` | PASS | 6 |
| `stage4_simple_false_if` | PASS | 6 |
| `stage4_if_else_true_path` | PASS | 6 |
| `stage4_if_else_false_path` | PASS | 6 |
| `stage4_nested_true_true` | PASS | 6 |
| `stage4_nested_true_false` | PASS | 6 |
| `stage4_outer_false_nested_inactive` | PASS | 6 |
| `stage4_multiple_nesting_levels` | PASS | 6 |
| `stage4_exact_nesting_limit` | PASS | 7 |
| `stage4_nesting_limit_plus_one` | PASS | 7 |
| `stage4_else_if_first_true` | PASS | 6 |
| `stage4_else_if_middle_true` | PASS | 6 |
| `stage4_else_if_final_else` | PASS | 6 |
| `stage4_else_if_multiple_entries` | PASS | 6 |
| `stage4_nested_else_if_chains` | PASS | 6 |
| `stage4_no_branch_true_without_else` | PASS | 6 |
| `stage4_selected_assignments_and_later_conditions` | PASS | 6 |
| `stage4_inactive_side_effects` | PASS | 9 |
| `stage4_required_fixture_spiffs_and_sd` | PASS | 12 |
| `stage4_define_conditions_and_protected_keywords` | PASS | 6 |
| `stage4_macro_manufactured_structures_rejected` | PASS | 56 |
| `stage4_compound_hex_boolean_conditions` | PASS | 6 |
| `stage4_malformed_expressions_zero_hid` | PASS | 77 |
| `stage4_undefined_and_text_variables` | PASS | 28 |
| `stage4_missing_end_if` | PASS | 7 |
| `stage4_unexpected_end_if` | PASS | 7 |
| `stage4_duplicate_else` | PASS | 7 |
| `stage4_else_outside_if` | PASS | 14 |
| `stage4_malformed_then_and_else_if` | PASS | 84 |
| `stage4_invalid_branch_ordering` | PASS | 21 |
| `stage4_rem_block_conditional_text` | PASS | 6 |
| `stage4_text_blocks_preserve_literal_modes` | PASS | 28 |
| `stage4_stop_active_and_inactive_branches` | PASS | 12 |
| `stage4_external_cancel_delay_text_and_keys` | PASS | 18 |
| `stage4_repeat_active_inactive_and_structural_history` | PASS | 18 |
| `stage4_clean_state_between_runs_and_live_ownership` | PASS | 9 |
| `stage4_runtime_errors_only_in_eligible_conditions` | PASS | 11 |
| `stage4_cooperative_large_inactive_region_and_preflight` | PASS | 18 |
| `stage4_legacy_compatibility_aliases` | PASS | 12 |
| `stage4_keyword_boundaries_whitespace_and_case` | PASS | 34 |
| `stage4_mixed_while_nesting_stays_deferred` | PASS | 14 |
| `stage4_conditional_stack_no_heap` | PASS | 60012 |
| `known_nested_if` | XPASS | included in 12 diagnostic sanity assertions |
| `known_canonical_if` | XPASS | included in 12 diagnostic sanity assertions |
| `known_false_while` | XFAIL | included in 12 diagnostic sanity assertions |
| `known_f13_mapping` | XFAIL | included in 12 diagnostic sanity assertions |
| `known_german_ascii_table` | XFAIL | included in 12 diagnostic sanity assertions |

## Remaining local/device work — migration is not authorized

The owner's backup files are not present here. Consequently actual file usage,
complete old-file inventory and exact old SPIFFS decode cannot be established
from their hashes alone. Migration must refuse unless a complete trusted export
fits the conservative budget and successful new-image pack/roundtrip verification.
If content does not fit, revisit layout B with review; do not discard files.

Keep original backups untouched and verify their recorded hashes locally. Decode
only with established geometry or perform separately authorized complete exports;
inventory, prove capacity, repack and compare independently. Review the offline
region plan, NVS preservation, pinned OTA initializer, new coredump and first-boot
HID/autorun isolation before any migration authorization. Physical boot, NVS
compatibility, filesystem mount/restored hashes, SD, USB, coredump capture,
alternate-slot web OTA and power-loss recovery remain untested. Core 3.3.0 tools
must work on a suitable build machine; esptool 4.12.0 remains the tested Mac ROM
interface. No hardware was accessed, destructive commands executed or physical
migration performed. Stage 5 was not started. Stop for review.
