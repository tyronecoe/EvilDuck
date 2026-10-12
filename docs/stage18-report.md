# Stage 18 early NVS preservation and startup hardening report

Baseline Stage17 bb2ea299e667225e7d9f30f535496df2afcffafb. Delivery branch
stage18-nvs-preservation-hardening; the GitHub commit containing this report identifies
the exact source revision. Stage19 has not begun.

## Implemented and verified

Removed Arduino3.3.0's known whole-NVS erase/retry on initialization errors through a
minimal isolated-core patch. Every nonzero SDK return is preserved, logged as signed
error and stops further Arduino hooks. A strong status API initialized unknown/error
feeds a boot-lifetime application failure latch. Normal and safe profiles enter bounded
serial-diagnostic/quiescent behavior before any EvilDuck settings, autorun, filesystem,
keyboard, storage, CLI/web or execution scheduler. Later core retry cannot arm a failed
application. Successful initialization and healthy normal/safe behavior are preserved.
No recovery command, replacement partition, default writes, new language features,
USB identities/descriptors or automatic arming mechanism are introduced.

Important scope: **Arduino's explicit whole-partition error-recovery erase is fixed;
SDK initialization itself is not certified read-only.** It can recover/mutate pages
before returning. No guessed/destructive SDK change is made. Strict protection against
all SDK/global/bootloader mutations remains unestablished; hardware migration remains
NO-GO. The actual SDK is not executed by the host fault harness.

[Startup analysis](stage18-startup-analysis.md), [source/pin](stage18-dependency-pin.json),
[patch](../proposals/arduino-esp32-3.3.0-nvs-preservation.patch),
[reference evidence](stage18-reference-evidence.json),
[reproduction/rollback](stage18-reproduction.md),
[readiness](stage18-hardware-readiness.md).

## Startup and safety contract

ROM/IDF core init and C++ constructors precede Arduino. Pinned app_main configures CPU/
USB-on-boot before initArduino; configured rollback verification precedes NVS and can
update OTA metadata. Those existing hooks/SDK/global actions remain. After nvs_flash_init
returns, the new policy captures its exact32-bit error and never calls erase/lookup/
retry/default initialization as error recovery. Failure returns before BT release,
init and initVariant; successful path is unchanged. app_main creates loopTask afterward.

EvilDuck setup reads the status before either operating profile, latches any error,
logs through existing serial and returns. Loop yields1ms on the latched failure.
No SPIFFS.begin(true), SD init, example install, settings load/write, autorun, HID init,
MSC backing activation or web/CLI startup occurs. Safe+valid NVS remains quiescent;
normal+valid NVS retains the existing setup/autorun contract. No application retry or
reboot is triggered. Diagnostics are best effort: fatal earlier flash/boot/task/heap/USB
failure can prevent delivery. Serial formatting uses a bounded message; dynamic String
and driver allocation/delivery are not physically verified. Critical USB/RTOS tasks
are not blocked by an infinite policy loop.

NVS initialization success does not certify every namespace/key or prevent later
explicit normal-operation writes. SDK PageManager recovery can erase/write before
an eventual error; compiled archive call references and supporting official v5.5
source show that limitation. A stand-in SDK write before failure is separately OBSERVED,
not falsely labeled as an executed SDK failure or preservation pass.

## Reproducible dependency integration

Original installed3.3.0 remains unchanged. The Stage16 HID patch and companion source
hashes are intact. New whole-tree pin requires exactly HID+NVS changes in a disposable
copy, original/patched misc source hashes, NVS archive/config and existing nine-source
checks. Version, source, patch, partial tree and application companion mismatches fail.
Native compile requires EVILDUCK_VERIFIED_NVS_PRESERVATION=1, supplied only after
verification; missing strong status API fails linking even if a flag is manually set.

Final ELF checks: one status hook, failure latch, actual startup call, exact compiled
contract header/body, initArduino call to NVS with no erase call, paired HID callback,
object/map/core identity, profile marker/flags and byte-exact ELF→BIN conversion. Full
normal/safe firmware builds, not only test slices, pass. Xtensa sequential disassembly
can misalign at unreachable linker padding; bounded explicit branch-target decoding
confirms the actual final setup status call. Source/linked evidence is retained below.
This correction did not relax existing dependency/header/image guards.

Original misc source SHA256 `ce5c88b08640235938cb6b23433c482d024f5662223b581856c25886329be94e`.
Patched misc source SHA256 `b119be330cc02e07c5cd53dae83a2dc2784b0cdd614ed89c6e902f68b029b73d`.
NVS patch SHA256 `a2eee87eb2ada400223760a7148b029b3f8dbf6b0358ca9be4348454ab7efcc5`.
Combined patched source tree SHA256 `81c11f59e01c1e6263d387a008d3f3211319d94feb4751ddfa11af35a2a57ed3`.
NVS SDK archive SHA256 `a1ac62b0f8b69ef2ac08e82dd1c57f58d53db74147bc309f070e36a148067a2e`.
Remaining HID/original-tree/SDK-config/companion hashes are in the immutable pin.

## Actually executed tests

| Group | PASS | FAIL | Other | Assertions |
| --- | ---: | ---: | --- | ---: |
| Stage1–17 prior regressions | 889 | 0 | Historical classes below | 634953 |
| Stage18 exact-core/actual-setup NVS | 28 | 0 | 5 OBSERVED | 528 |
| Stage18 dependency/final link | 9 | 0 | None | 9 |

Current/prior total **926 PASS / 0 unexpected FAIL**.
Exact total **635490 assertions**, including observations and12diagnostic sanity
checks. Historical Stage15 additionally retains39PASS/6upstreamXFAIL/7OBSERVED/174assertions;
its passes are not new active protection claims. Total PASS records including that
separate harness:965. Five language XPASS remain unchanged;
zero language XFAIL. Stage9 retains79matched observations/0mismatches/574assertions.
Stage16 stock policy OBSERVED and Stage17 two original risks remain historical evidence,
not silently deleted. Stage17 uses the verified original core for its old erase observation;
current NVS protection is established by Stage18 separately.

NVS harness compiles exact hash-checked original/patched initArduino and getter/storage
with actual setup/loop, mocked SDK and instrumented20KiB NVS. Both profiles cover success,
no-free-pages, new-version, invalid-state metadata, missing partition, flash/read/timeout/
initialization failures, no-memory, unexpected positive/negative codes, initial unknown,
explicit repeated attempts and retry latch. Every normal injected failed initializer
without internal side effects causes zero policy erase/write calls and preserves every
protected byte; no second initialization occurs automatically. Three original-core
whole-erase/error-replacement cases and two SDK-side-effect examples are OBSERVED.
SDK recovery is not emulated. Invalid metadata/read errors are injected return codes,
not independently decoded corrupt NVS pages. Owner backups are not fabricated or required.

ASan/UBSan pass for current production-mock suites and new startup cases. Six historical
USB fault probes deliberately reproduce sanitizer faults and remain separately classified.
Python checks are not ASan targets. All previous C++ allocation probes pass; no unbounded
queue/table/AST or new dependency is introduced. Existing bounded String/line/library
allocations remain, and actual device heap/latency/task high-water is unmeasured.

## Clean final firmware builds and resources

Arduino3.3.0, GCC14.2.0 esp-14.2.0_20241119, CLI1.3.1, pinned IDF5.5 SDK;16MiB custom
partitions, QIO80MHz/DIO image,240MHz, PSRAMoff, USB-OTG/TinyUSB, CDC and unchanged
boot MSC/DFU settings. Both final fresh isolated copies pass full source/provenance and
native compilation checks. Binary identity across paths/times/hosts is not promised.

| Measurement | Stage17 normal | Stage18 normal | Stage17 safe | Stage18 safe |
| --- | ---: | ---: | ---: | ---: |
| Program bytes | 1329019 | 1329359 | 1066655 | 1067031 |
| Application BIN bytes | 1329168 | 1329504 | 1066800 | 1067184 |
| Static RAM bytes | 82232 | 82232 | 78288 | 78288 |
| Free bytes/OTA slot | 6273008 | 6272672 | 6535376 | 6534992 |
| Free percent/OTA slot | 82.51595332704741 | 82.51153353987068 | 85.96717571390086 | 85.96212452855603 |

Normal growth:340program/336BIN bytes;
safe growth:376program/384BIN bytes.
Reported static RAM growth0both profiles; two new32-bit globals total8bytes of fixed
state despite unchanged overall linker RAM accounting. No heap-based status registry.
Normal exceeds original140000 slot by18784bytes; safe
byte size fitting an old slot does not authorize the16MiB/table/filesystem transition.

Application module stack maxima remain unchanged (largest duckscript1072bytes).
Normal setup96/loop32; safe setup80/loop32 (safe setup +16 vsStage17). Status getter32
and initArduino48bytes compiler frames, excluding callees/SDK/interrupts. Main task8192
configuration unchanged; real task high-water/heap/unavailable physical measurements
are not inferred from estimates. Detailed [application frames](stage18-stack-results.json)
and [startup frames](stage18-startup-stack.json).

Normal BIN SHA256 `862ef9f77da8ad1cee185a04d860050092208b0d6e5815bcfbf876296e2522e8`.
Safe BIN SHA256 `471bf9c36a4a15c582bb2c2e64f91554e9bd8de882da19929dfb0b2405eb67e1`.
Exact ELF/compiler/esptool/core hashes:
[normal provenance](stage18-normal-provenance.json), [safe provenance](stage18-safe-provenance.json).
Linked init evidence: [normal](stage18-normal-linked-nvs.txt), [safe](stage18-safe-linked-nvs.txt).
Actual setup status calls: [normal](stage18-normal-linked-startup.txt), [safe](stage18-safe-linked-startup.txt).

## Offline artifacts and preserved migration safeguards

New non-owner binaries/inventory are [deployment/stage18](../deployment/stage18/README.md).
Stage17 originals remain historical/unmodified. No owner full backup, partition sector
or approved external SPIFFS is included. No padded merged image/physical writer.
NVS9000/5000 is excluded from every proposed write and sector erase. Old SPIFFS290000/
170000→newE90000/160000 remains file-level only. Proposed partitions unchanged: NVS,
OTAE000/2000, app010000/740000, app1750000/740000, SPIFFSE90000/160000,
coredumpFF0000/10000. Both initial apps are the same safe image, app0 OTA initializer
CRC checked, new coredump erased inside its region. Normal application is not an initial
write. Legacy pre_setup_nvs_erase_risk_unresolved field conservatively remains true for
SDK-level mutation; new arduino_nvs_auto_erase_disabled/sdk_nvs_mutation_risk_unresolved fields disambiguate it.
No software protection flag substitutes for actual owner backup verification.

| Role | Offset | Bytes | SHA256 |
| --- | --- | ---: | --- |
| bootloader  | 0x0 | 20256 | 95b966ad240a05bf8a804cd4519eebac5271b662e51417668da488652b7354bf |
| partitions  | 0x8000 | 4096 | ee076434a9676c96f034af8911c4d2f1134e52a761eda75a10e5aa96a125801c |
| otadata  | 0xe000 | 8192 | f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0 |
| app0  | 0x10000 | 1067184 | 471bf9c36a4a15c582bb2c2e64f91554e9bd8de882da19929dfb0b2405eb67e1 |
| app1  | 0x750000 | 1067184 | 471bf9c36a4a15c582bb2c2e64f91554e9bd8de882da19929dfb0b2405eb67e1 |
| spiffs EXTERNAL | 0xe90000 | 1441792 | fea8c95f9a0b49878e69fe9e9afec7472ce52f6b3d7c1b35db43e905470043fe |
| coredump  | 0xff0000 | 65536 | 71189f7fb6aed638640078fba3a35fda6c39c8962e74dcc75935aac948da9063 |

## GO / NO-GO and remaining risks

GO for owner-controlled local offline backup/plan/dependency review. Known Arduino
whole-NVS erase is software-verified disabled; both profiles fail safely at the
application layer on reported initialization errors.

Conditional GO for separately authorized ROM read-only checks after exact-device/port/
power/security/recovery gates; no such action is performed here. Owner is separately
verifying the three known files on High Sierra; they are absent here. Actual16MiB/current
installed table, NVS compatibility/readability, verified original recovery images,
filesystem roundtrip, autorun policy, exact artifact/region manifest and individual
migration authorization remain required. Mac compiler/bundled-tool support is unverified;
Python3.8/esptool4.12 ROM reads do not need forced upgrade for this work.

NO-GO for migration/application boot/OTA now. SDK init page/item recovery can mutate
before returning; missing/bad metadata or fatal flash/boot can precede our diagnostic.
Successful NVS init is not every-key integrity or a transactional snapshot guarantee.
No physical NVS/USB/storage/diagnostic/timing/heap/task-stack validation. Existing rollback
hooks before NVS are unchanged and are not health-based protection for this failure.
Any destructive repair/restore must have explicit owner approval and independently
verified backups/current-data/region review; none is attempted or commanded.

Recommend Stage19 review of SDK page-recovery/data-preservation limits and actual owner
backup evidence/NVS compatibility, then justified settings-read hardening if needed.
Do not automatically proceed. No physical hardware, flash/erase/format/OTA, real HID,
owner payload execution, global core/toolchain change, partition/identity/personality
change or Arduino Micro modification. Main/prior branches remain protected.

## Exact executed test results

### Stage1

| Test | Status | Assertions |
| --- | --- | ---: |
| supported_commands_and_mock_interfaces | PASS | 29 |
| script_run_state_isolation | PASS | 22 |
| cooperative_delay_and_text_cancellation | PASS | 33 |
| repeat_timing_and_control_loop_yield | PASS | 24 |
| live_commands_cannot_mutate_running_script | PASS | 19 |

### Stage2

| Test | Status | Assertions |
| --- | --- | ---: |
| stage2_rem_comments | PASS | 6 |
| stage2_required_rem_block_fixture | PASS | 12 |
| stage2_comment_block_literal_commands | PASS | 6 |
| stage2_unterminated_rem_block_zero_hid | PASS | 9 |
| stage2_unmatched_end_rem_zero_hid | PASS | 9 |
| stage2_lf_source | PASS | 6 |
| stage2_crlf_source | PASS | 6 |
| stage2_utf8_bom | PASS | 21 |
| stage2_missing_final_newline | PASS | 12 |
| stage2_blank_lines | PASS | 12 |
| stage2_spaces_tabs_and_payload_preservation | PASS | 7 |
| stage2_maximum_line_length | PASS | 12 |
| stage2_overlong_line_zero_hid | PASS | 18 |
| stage2_source_byte_limits | PASS | 16 |
| stage2_source_line_limits | PASS | 15 |
| stage2_mismatched_control_blocks_zero_hid | PASS | 18 |
| stage2_unterminated_control_blocks_zero_hid | PASS | 36 |
| stage2_duplicate_else_zero_hid | PASS | 18 |
| stage2_block_depth_limit_zero_hid | PASS | 9 |
| stage2_text_blocks_literal_mode_and_deferred_runtime | PASS | 30 |
| stage2_unterminated_text_blocks_zero_hid | PASS | 18 |
| stage2_unmatched_text_terminators_zero_hid | PASS | 18 |
| stage2_mismatched_text_terminators_zero_hid | PASS | 27 |
| stage2_unknown_commands_zero_hid | PASS | 27 |
| stage2_keyword_prefixes_are_not_commands | PASS | 128 |
| stage2_malformed_statements_zero_hid | PASS | 210 |
| stage2_supported_extensions_and_bare_keys | PASS | 8 |
| stage2_storage_read_seek_faults | PASS | 25 |
| stage2_preflight_cooperative_stop_and_live_ownership | PASS | 18 |
| stage2_live_validation_and_limits | PASS | 34 |

### Stage2.5

| Test | Status | Assertions |
| --- | --- | ---: |
| stage25_reviewed_partition_layout | PASS | 15 |
| stage25_overlapping_partitions_rejected | PASS | 1 |
| stage25_unaligned_application_rejected | PASS | 1 |
| stage25_reviewed_offsets_sizes_flags_enforced | PASS | 10 |
| stage25_core_version_pin_enforced | PASS | 1 |
| stage25_application_size_boundary | PASS | 3 |
| stage25_image_header_configuration_enforced | PASS | 6 |
| stage25_build_configuration_and_app_address_enforced | PASS | 22 |
| stage25_generated_16m_build_artifacts | PASS | 4 |
| stage25_corrupt_partition_binary_rejected | PASS | 1 |
| stage25_merged_image_wrong_address_rejected | PASS | 1 |
| stage25_stale_4m_partition_artifact_rejected | PASS | 1 |
| stage25_saved_physical_flash_capacity_guard | PASS | 7 |
| stage25_offline_source_archives_require_file_migration | PASS | 11 |
| stage25_offline_preparation_rejects_invalid_backups | PASS | 6 |
| stage25_offline_preparation_never_overwrites | PASS | 2 |
| stage25_build_wrapper_requires_clean_output | PASS | 3 |
| stage25_verified_device_map_differs_from_core_default | PASS | 3 |
| stage25_raw_spiffs_size_mismatch_refused | PASS | 3 |
| stage25_recorded_backup_hash_guards | PASS | 4 |
| stage25_file_level_extract_repack_roundtrip | PASS | 8 |
| stage25_file_level_empty_filesystem | PASS | 1 |
| stage25_file_level_capacity_and_overwrite_guards | PASS | 7 |
| stage25_corrupt_or_wrong_geometry_extraction_refused | PASS | 4 |
| stage25_alternative_layout_maximum_equal_slots | PASS | 4 |
| stage25_review_only_plan_preserves_nvs_and_initializes_both_apps | PASS | 24 |
| stage25_write_and_erase_region_guards | PASS | 13 |
| stage25_ota_initializer_selects_app0_deterministically | PASS | 7 |
| stage25_plan_refuses_unverified_files_and_backup_provenance | PASS | 16 |
| stage25_mac_old_core_rejected_before_compile | PASS | 1 |

### Stage3

| Test | Status | Assertions |
| --- | --- | ---: |
| stage3_addition | PASS | 3 |
| stage3_subtraction | PASS | 3 |
| stage3_multiplication | PASS | 3 |
| stage3_division | PASS | 3 |
| stage3_modulo | PASS | 3 |
| stage3_exponentiation | PASS | 3 |
| stage3_equality | PASS | 3 |
| stage3_inequality | PASS | 3 |
| stage3_less_than | PASS | 3 |
| stage3_greater_than | PASS | 3 |
| stage3_less_or_equal | PASS | 3 |
| stage3_greater_or_equal | PASS | 3 |
| stage3_logical_and | PASS | 3 |
| stage3_logical_or | PASS | 3 |
| stage3_bitwise_and | PASS | 3 |
| stage3_bitwise_or | PASS | 3 |
| stage3_left_shift | PASS | 3 |
| stage3_right_shift | PASS | 3 |
| stage3_precedence_and_grouping | PASS | 54 |
| stage3_literals_booleans_and_whitespace | PASS | 54 |
| stage3_arithmetic_boundaries | PASS | 57 |
| stage3_invalid_literals_and_unsupported_operators | PASS | 54 |
| stage3_malformed_expressions_and_limits | PASS | 54 |
| stage3_numeric_declarations_assignment_and_no_hid | PASS | 9 |
| stage3_required_fixture_spiffs_and_sd | PASS | 12 |
| stage3_variable_references_types_and_atomic_failure | PASS | 24 |
| stage3_text_compatibility_alias_and_read | PASS | 41 |
| stage3_identifier_validation_and_table_exhaustion | PASS | 91 |
| stage3_preflight_zero_hid_and_runtime_errors | PASS | 46 |
| stage3_define_global_forward_and_word_matching | PASS | 24 |
| stage3_define_single_pass_and_declaration_exemption | PASS | 32 |
| stage3_define_comment_and_text_modes | PASS | 24 |
| stage3_define_duplicates_invalid_and_table_limits | PASS | 76 |
| stage3_define_expansion_and_pool_boundaries | PASS | 32 |
| stage3_expression_timing_counts_and_cancellation | PASS | 17 |
| stage3_collection_preflight_stop_and_state_isolation | PASS | 27 |
| stage3_interpolation_overflow_runtime_safe_stop | PASS | 6 |
| stage3_syntax_mode_does_not_evaluate_runtime_values | PASS | 3 |
| stage3_bounded_expression_fuzz | PASS | 3001 |
| stage3_expression_hot_path_no_heap | PASS | 10022 |

### Stage4

| Test | Status | Assertions |
| --- | --- | ---: |
| stage4_simple_true_if | PASS | 6 |
| stage4_simple_false_if | PASS | 6 |
| stage4_if_else_true_path | PASS | 6 |
| stage4_if_else_false_path | PASS | 6 |
| stage4_nested_true_true | PASS | 6 |
| stage4_nested_true_false | PASS | 6 |
| stage4_outer_false_nested_inactive | PASS | 6 |
| stage4_multiple_nesting_levels | PASS | 6 |
| stage4_exact_nesting_limit | PASS | 7 |
| stage4_nesting_limit_plus_one | PASS | 7 |
| stage4_else_if_first_true | PASS | 6 |
| stage4_else_if_middle_true | PASS | 6 |
| stage4_else_if_final_else | PASS | 6 |
| stage4_else_if_multiple_entries | PASS | 6 |
| stage4_nested_else_if_chains | PASS | 6 |
| stage4_no_branch_true_without_else | PASS | 6 |
| stage4_selected_assignments_and_later_conditions | PASS | 6 |
| stage4_inactive_side_effects | PASS | 9 |
| stage4_required_fixture_spiffs_and_sd | PASS | 12 |
| stage4_define_conditions_and_protected_keywords | PASS | 6 |
| stage4_macro_manufactured_structures_rejected | PASS | 56 |
| stage4_compound_hex_boolean_conditions | PASS | 6 |
| stage4_malformed_expressions_zero_hid | PASS | 77 |
| stage4_undefined_and_text_variables | PASS | 28 |
| stage4_missing_end_if | PASS | 7 |
| stage4_unexpected_end_if | PASS | 7 |
| stage4_duplicate_else | PASS | 7 |
| stage4_else_outside_if | PASS | 14 |
| stage4_malformed_then_and_else_if | PASS | 84 |
| stage4_invalid_branch_ordering | PASS | 21 |
| stage4_rem_block_conditional_text | PASS | 6 |
| stage4_text_blocks_preserve_literal_modes | PASS | 26 |
| stage4_stop_active_and_inactive_branches | PASS | 12 |
| stage4_external_cancel_delay_text_and_keys | PASS | 18 |
| stage4_repeat_active_inactive_and_structural_history | PASS | 18 |
| stage4_clean_state_between_runs_and_live_ownership | PASS | 9 |
| stage4_runtime_errors_only_in_eligible_conditions | PASS | 11 |
| stage4_cooperative_large_inactive_region_and_preflight | PASS | 18 |
| stage4_legacy_compatibility_aliases | PASS | 12 |
| stage4_keyword_boundaries_whitespace_and_case | PASS | 34 |
| stage4_mixed_while_nesting | PASS | 12 |
| stage4_conditional_stack_no_heap | PASS | 60012 |

### Stage5

| Test | Status | Assertions |
| --- | --- | ---: |
| stage5_false_while_following_commands | PASS | 6 |
| stage5_zero_iteration_expressions | PASS | 36 |
| stage5_single_iteration | PASS | 7 |
| stage5_multiple_iterations | PASS | 7 |
| stage5_decrementing_numeric_no_hid | PASS | 9 |
| stage5_shared_expression_operators | PASS | 84 |
| stage5_condition_reevaluated_at_header | PASS | 8 |
| stage5_nested_two_loops | PASS | 8 |
| stage5_nested_three_loops | PASS | 7 |
| stage5_sequential_loops | PASS | 6 |
| stage5_if_inside_while_else_if | PASS | 6 |
| stage5_while_inside_if_else | PASS | 6 |
| stage5_mixed_nested_structures | PASS | 6 |
| stage5_fixture_spiffs_and_sd | PASS | 12 |
| stage5_false_outer_suppresses_nested_conditions | PASS | 6 |
| stage5_inactive_side_effects_and_assignments | PASS | 10 |
| stage5_nested_updates_outer_variable | PASS | 8 |
| stage5_global_declarations_reused | PASS | 7 |
| stage5_exact_loop_depth | PASS | 6 |
| stage5_mixed_exact_depth | PASS | 6 |
| stage5_depth_plus_one_zero_hid | PASS | 14 |
| stage5_malformed_conditions_zero_hid | PASS | 98 |
| stage5_undefined_and_text_expression_rejection | PASS | 28 |
| stage5_missing_unmatched_and_crossed_terminators | PASS | 42 |
| stage5_keyword_boundaries_and_aliases | PASS | 52 |
| stage5_legacy_bare_text_truthiness | PASS | 12 |
| stage5_define_conditions_and_protected_keywords | PASS | 6 |
| stage5_macro_manufactured_loop_delimiters_rejected | PASS | 28 |
| stage5_define_collection_inside_inactive_loop | PASS | 6 |
| stage5_rem_block_loop_text_ignored | PASS | 6 |
| stage5_text_blocks_keep_literal_modes | PASS | 12 |
| stage5_bom_crlf_no_final_newline_backedges | PASS | 6 |
| stage5_header_across_read_budgets | PASS | 6 |
| stage5_reader_marker_and_seek_boundaries | PASS | 12 |
| stage5_runtime_seek_error | PASS | 7 |
| stage5_runtime_read_error_after_backedge | PASS | 7 |
| stage5_runtime_source_size_changed | PASS | 7 |
| stage5_runtime_condition_error_and_inactive_skip | PASS | 12 |
| stage5_runtime_undefined_path_dependent_variable | PASS | 6 |
| stage5_repeat_structural_and_inactive_history | PASS | 6 |
| stage5_repeat_expression_in_loop | PASS | 6 |
| stage5_keyboard_combinations_in_loop | PASS | 7 |
| stage5_expression_delays_in_loop | PASS | 7 |
| stage5_stop_in_active_and_inactive_loops | PASS | 12 |
| stage5_cancel_delay_inside_mixed_loop | PASS | 6 |
| stage5_cancel_text_inside_nested_loop | PASS | 7 |
| stage5_cancel_held_keys_and_usb_pressure | PASS | 8 |
| stage5_control_only_loop_cooperative_and_live_ownership | PASS | 47 |
| stage5_stalled_empty_loop_boundary | PASS | 7 |
| stage5_stalled_same_assignment_and_inactive_actions | PASS | 7 |
| stage5_nested_stall_not_masked_by_outer_progress | PASS | 6 |
| stage5_variable_progress_beyond_stall_threshold | PASS | 8 |
| stage5_total_iteration_limit_and_clean_restart | PASS | 13 |
| stage5_exact_total_iteration_boundary | PASS | 9 |
| stage5_variable_revision_atomic_and_reset | PASS | 9 |
| stage5_cancellation_then_new_source | PASS | 11 |
| stage5_large_inactive_region_cooperative | PASS | 11 |
| stage5_small_nested_loop_reference_cases | PASS | 175 |
| stage5_mixed_control_stack_no_heap | PASS | 91039 |

### Stage6

| Test | Status | Assertions |
| --- | --- | ---: |
| stage6_declarations_skipped | PASS | 6 |
| stage6_statement_invocation | PASS | 6 |
| stage6_multiple_calls | PASS | 6 |
| stage6_forward_invocation_and_globals | PASS | 6 |
| stage6_fixture_spiffs_and_sd | PASS | 12 |
| stage6_explicit_void_return | PASS | 6 |
| stage6_implicit_void_return | PASS | 6 |
| stage6_integer_return_assignment | PASS | 6 |
| stage6_boolean_return_conditions | PASS | 6 |
| stage6_statement_discards_return_value | PASS | 6 |
| stage6_void_value_rejected | PASS | 12 |
| stage6_top_level_and_live_return_compatibility | PASS | 11 |
| stage6_enter_and_modifier_return_inside_function | PASS | 7 |
| stage6_return_unwinds_nested_control | PASS | 6 |
| stage6_caller_control_restored | PASS | 6 |
| stage6_nested_statement_calls | PASS | 6 |
| stage6_nested_return_expressions | PASS | 6 |
| stage6_multiple_calls_in_expression | PASS | 6 |
| stage6_earlier_variable_operand_preserved | PASS | 6 |
| stage6_eager_logical_calls | PASS | 6 |
| stage6_inactive_conditions_do_not_call | PASS | 6 |
| stage6_while_condition_calls_reevaluate | PASS | 6 |
| stage6_while_condition_changes_count_as_progress | PASS | 6 |
| stage6_else_if_function_condition | PASS | 6 |
| stage6_numeric_commands_with_calls | PASS | 7 |
| stage6_function_globals_text_and_file_commands | PASS | 6 |
| stage6_define_function_operands_and_names | PASS | 6 |
| stage6_macro_structural_creation_rejected | PASS | 28 |
| stage6_rem_and_text_modes | PASS | 12 |
| stage6_literal_text_does_not_invoke | PASS | 6 |
| stage6_names_case_sensitive | PASS | 13 |
| stage6_malformed_names_parameters_and_collisions | PASS | 91 |
| stage6_unknown_calls_zero_hid | PASS | 21 |
| stage6_invalid_call_arguments_and_whitespace | PASS | 35 |
| stage6_duplicate_and_nested_declarations | PASS | 21 |
| stage6_unterminated_and_unmatched_functions | PASS | 28 |
| stage6_return_syntax_and_context_errors | PASS | 21 |
| stage6_unused_body_preflight_errors_zero_hid | PASS | 21 |
| stage6_function_table_boundary | PASS | 13 |
| stage6_function_identifier_boundary | PASS | 13 |
| stage6_nested_call_depth_boundary | PASS | 6 |
| stage6_recursive_depth_exhaustion | PASS | 6 |
| stage6_recursive_expression_and_global_visibility | PASS | 6 |
| stage6_shared_control_depth_exhaustion | PASS | 6 |
| stage6_runtime_undefined_initialization | PASS | 6 |
| stage6_runtime_arithmetic_after_calls | PASS | 12 |
| stage6_repeat_history_around_calls | PASS | 6 |
| stage6_stop_active_and_inactive_function_branches | PASS | 12 |
| stage6_cancel_pending_function_delay | PASS | 6 |
| stage6_cancel_nested_function_text | PASS | 7 |
| stage6_cancel_held_keys_in_call | PASS | 7 |
| stage6_cancel_call_under_usb_backpressure | PASS | 8 |
| stage6_cancel_expression_then_clean_run | PASS | 12 |
| stage6_live_ownership_and_stop | PASS | 7 |
| stage6_seek_error_entering_function | PASS | 5 |
| stage6_seek_error_returning_to_caller | PASS | 6 |
| stage6_read_error_and_source_change_in_function | PASS | 6 |
| stage6_runtime_body_read_failure | PASS | 7 |
| stage6_bom_crlf_header_and_final_newline | PASS | 6 |
| stage6_empty_function_loop_stalls | PASS | 6 |
| stage6_total_call_budget | PASS | 6 |
| stage6_postfix_arithmetic_matches_existing_evaluator | PASS | 39 |
| stage6_expression_bounds_and_postfix_errors | PASS | 11 |
| stage6_long_declaration_skip_is_cooperative | PASS | 11 |
| stage6_postfix_call_state_no_heap | PASS | 60012 |

### Stage7

| Test | Status | Assertions |
| --- | --- | ---: |
| stage7_empty_blocks | PASS | 6 |
| stage7_single_line_string | PASS | 6 |
| stage7_single_line_stringln | PASS | 6 |
| stage7_string_multiline_no_separators | PASS | 6 |
| stage7_stringln_multiline_enters | PASS | 7 |
| stage7_string_blank_lines | PASS | 6 |
| stage7_stringln_blank_lines | PASS | 6 |
| stage7_string_leading_and_trailing_whitespace | PASS | 6 |
| stage7_stringln_removes_one_leading_tab | PASS | 6 |
| stage7_internal_tabs_preserved | PASS | 6 |
| stage7_literal_command_keywords | PASS | 6 |
| stage7_terminator_prefixes_are_literal | PASS | 6 |
| stage7_case_and_indented_delimiters | PASS | 6 |
| stage7_inline_compatibility_unchanged | PASS | 6 |
| stage7_lf_and_crlf_equivalent | PASS | 12 |
| stage7_bom_only_at_source_start | PASS | 6 |
| stage7_no_final_newline | PASS | 6 |
| stage7_quoted_text_no_unescaping | PASS | 6 |
| stage7_numeric_boolean_and_text_interpolation | PASS | 6 |
| stage7_unknown_host_variables_are_literal | PASS | 6 |
| stage7_variable_replacement_is_single_pass | PASS | 6 |
| stage7_define_hash_and_word_replacement | PASS | 6 |
| stage7_define_body_not_collected_or_expanded | PASS | 6 |
| stage7_define_single_pass_and_variable_order | PASS | 6 |
| stage7_expansion_cannot_close_or_execute | PASS | 6 |
| stage7_value_whitespace_after_source_dedent | PASS | 6 |
| stage7_maximum_body_line | PASS | 12 |
| stage7_overlong_body_zero_hid | PASS | 7 |
| stage7_define_expansion_boundary | PASS | 13 |
| stage7_interpolation_boundary_and_overflow | PASS | 12 |
| stage7_inactive_interpolation_has_no_runtime_effect | PASS | 6 |
| stage7_unterminated_after_output_zero_hid | PASS | 14 |
| stage7_mismatched_or_argument_terminators_zero_hid | PASS | 21 |
| stage7_unmatched_terminators_zero_hid | PASS | 14 |
| stage7_literal_openers_inside_body | PASS | 6 |
| stage7_fixture_spiffs_and_sd | PASS | 12 |
| stage7_if_else_active_inactive_blocks | PASS | 6 |
| stage7_zero_iteration_loop_blocks | PASS | 6 |
| stage7_nested_loops_interpolate_current_values | PASS | 6 |
| stage7_function_repeat_calls_and_return | PASS | 6 |
| stage7_nested_functions_with_blocks | PASS | 6 |
| stage7_recursive_calls_with_blocks | PASS | 6 |
| stage7_repeat_literal_text_and_whitespace | PASS | 6 |
| stage7_repeat_blank_stringln | PASS | 6 |
| stage7_empty_string_does_not_replace_history | PASS | 6 |
| stage7_repeat_interpolates_again | PASS | 6 |
| stage7_default_delays_per_body_line | PASS | 7 |
| stage7_cancel_default_delay | PASS | 7 |
| stage7_cancel_halfway_through_typing | PASS | 6 |
| stage7_cancel_held_shift_and_usb_release_retry | PASS | 7 |
| stage7_usb_backpressure_lossless_and_no_readahead | PASS | 8 |
| stage7_stop_command_after_block | PASS | 6 |
| stage7_live_ownership_and_clean_run | PASS | 14 |
| stage7_live_block_opener_rejected | PASS | 5 |
| stage7_preflight_source_errors_zero_hid | PASS | 6 |
| stage7_rewind_seek_error_zero_hid | PASS | 6 |
| stage7_runtime_body_read_error_spiffs_and_sd | PASS | 12 |
| stage7_runtime_source_change | PASS | 7 |
| stage7_loop_backedge_seek_error | PASS | 6 |
| stage7_function_return_seek_error | PASS | 7 |
| stage7_large_block_streamed_and_cooperative | PASS | 7 |
| stage7_cancel_large_block_preflight | PASS | 6 |
| stage7_source_limits_zero_hid | PASS | 13 |
| stage7_hid_disabled_block_has_no_output | PASS | 6 |
| stage7_malformed_later_control_zero_hid | PASS | 7 |
| stage7_control_nesting_boundaries | PASS | 26 |
| stage7_text_blocks_do_not_execute_calls | PASS | 6 |
| stage7_bounded_line_allocation_probe | PASS | 40005 |

### Stage8

| Test | Status | Assertions |
| --- | --- | ---: |
| stage8_f1_f24_reference | PASS | 346 |
| stage8_invalid_f_names | PASS | 12 |
| stage8_navigation_editing_aliases | PASS | 330 |
| stage8_named_punctuation_keys | PASS | 176 |
| stage8_keypad_reference | PASS | 144 |
| stage8_all_modifier_masks | PASS | 3072 |
| stage8_modifier_aliases | PASS | 110 |
| stage8_hyphen_combinations | PASS | 34 |
| stage8_malformed_hyphens_zero_hid | PASS | 24 |
| stage8_case_tabs_and_order | PASS | 12 |
| stage8_modifier_only_release | PASS | 23 |
| stage8_six_key_limit_and_duplicates | PASS | 15 |
| stage8_literal_punctuation_chord_us | PASS | 15 |
| stage8_literal_punctuation_chord_de | PASS | 27 |
| stage8_all_literal_punctuation_chords | PASS | 797 |
| stage8_report_filter_and_raw_modifiers | PASS | 99 |
| stage8_keycode_bounds_zero_hid | PASS | 12 |
| stage8_us_ascii_table | PASS | 129 |
| stage8_de_ascii_table | PASS | 129 |
| stage8_us_ascii_translation | PASS | 358 |
| stage8_de_ascii_translation | PASS | 360 |
| stage8_printable_ascii_runtime_all_locales | PASS | 1934 |
| stage8_de_utf8_reference | PASS | 89 |
| stage8_de_dead_keys | PASS | 70 |
| stage8_locale_registration_and_switching | PASS | 28 |
| stage8_named_keys_are_physical_not_locale_text | PASS | 17 |
| stage8_unsupported_unicode_skip_warning | PASS | 14 |
| stage8_utf8_bounds_and_invalid_sequences | PASS | 16 |
| stage8_no_warn_supported_controls | PASS | 6 |
| stage8_repeat_define_and_stringln_reports | PASS | 63 |
| stage8_multiline_control_function_keyboard | PASS | 36 |
| stage8_queue_refusal_press_and_release | PASS | 16 |
| stage8_disconnect_mid_chord_recovery | PASS | 15 |
| stage8_cancel_held_modifier_all_masks | PASS | 3060 |
| stage8_cancel_release_priority_new_live_command | PASS | 14 |
| stage8_stop_and_runtime_error_release | PASS | 15 |
| stage8_cancel_between_dead_key_strokes | PASS | 12 |
| stage8_storage_fault_after_chord_release | PASS | 10 |
| stage8_hid_disabled_and_live_ownership | PASS | 15 |
| stage8_new_run_no_modifier_leak | PASS | 11 |
| stage8_translation_report_allocation_probe | PASS | 32001 |

### Stage10

| Test | Status | Assertions |
| --- | --- | ---: |
| startup_success_truthful | PASS | 6 |
| startup_missing_card | PASS | 6 |
| startup_missing_image_no_create | PASS | 6 |
| startup_wrong_size_no_truncate | PASS | 22 |
| startup_open_failure | PASS | 4 |
| startup_probe_seek_failure | PASS | 5 |
| startup_probe_short_read | PASS | 4 |
| startup_sdk_failure_cleanup | PASS | 6 |
| retry_failed_startup | PASS | 3 |
| repeated_begin_idempotent | PASS | 3 |
| retry_ejected_media | PASS | 7 |
| stale_host_load_after_off | PASS | 5 |
| stale_host_load_after_cancel | PASS | 5 |
| writable_reset_after_end | PASS | 8 |
| read_nonzero_offset | PASS | 6 |
| write_nonzero_offset | PASS | 7 |
| cross_sector_unaligned | PASS | 6 |
| last_byte_and_exact_end | PASS | 7 |
| invalid_range_and_overflow | PASS | 12 |
| zero_length_null | PASS | 5 |
| null_nonzero | PASS | 5 |
| transfer_limit | PASS | 6 |
| read_seek_failure_no_wrong_read | PASS | 9 |
| write_seek_failure_no_wrong_write | PASS | 9 |
| short_read_quarantines | PASS | 9 |
| short_write_prefix_and_quarantine | PASS | 10 |
| card_removal_callback | PASS | 9 |
| card_removal_main_loop | PASS | 7 |
| backing_size_changed | PASS | 8 |
| fault_cleanup_and_explicit_recovery | PASS | 6 |
| eject_load_and_power_stop | PASS | 9 |
| cancel_before_open | PASS | 3 |
| cancel_after_open | PASS | 3 |
| timeout_wrap_safe | PASS | 6 |
| media_absent_until_validated | PASS | 4 |
| script_waits_for_storage | PASS | 7 |
| script_startup_failure_stops_tail | PASS | 6 |
| stop_pending_startup | PASS | 6 |
| stop_preserves_active_media | PASS | 8 |
| live_cli_ownership_while_preparing | PASS | 9 |
| script_and_host_activity | PASS | 206 |
| function_condition_storage_startup | PASS | 7 |
| live_cli_failure_status_and_retry | PASS | 7 |
| callback_lock_contention_busy | PASS | 6 |
| callback_error_storm_no_io | PASS | 1004 |
| concurrent_callback_mode_stop | PASS | 5 |
| sd_adapter_interleaving | PASS | 7 |
| sd_adapter_removal_and_remount | PASS | 3 |
| off_cancels_pending | PASS | 1 |
| repeated_failure_recovery | PASS | 81 |
| no_callback_heap_allocation | PASS | 5 |
| build_without_msc_reports_unavailable | PASS | 4 |

### Stage11

| Test | Status | Assertions |
| --- | --- | ---: |
| hold_release_key | PASS | 13 |
| all_eight_persistent_modifiers | PASS | 104 |
| selective_modifier_release | PASS | 24 |
| selective_key_release_order | PASS | 18 |
| idempotent_hold_release | PASS | 13 |
| six_persistent_keys | PASS | 15 |
| seventh_hold_fails_no_drop | PASS | 14 |
| transient_chord_merges_persistent | PASS | 18 |
| all_modifier_masks_merge | PASS | 2308 |
| string_shift_punctuation_enter | PASS | 24 |
| de_altgr_and_dead_key_merge | PASS | 24 |
| held_shift_with_german_spacing | PASS | 18 |
| persistent_duplicate_transient_no_edge | PASS | 24 |
| merged_seventh_transient_fails | PASS | 10 |
| saturated_duplicate_and_modifier_allowed | PASS | 12 |
| raw_modifier_keycode_merges | PASS | 12 |
| inject_mod_inline | PASS | 12 |
| inject_mod_restores_owned | PASS | 15 |
| inject_mod_prefix_reference | PASS | 18 |
| reset_continues_variables | PASS | 13 |
| stop_payload_tail_and_release | PASS | 10 |
| stop_inside_function_loop | PASS | 12 |
| inactive_ownership_commands | PASS | 8 |
| functions_loops_share_ownership | PASS | 18 |
| define_repeat_ownership_and_text | PASS | 19 |
| default_delay_ownership | PASS | 8 |
| eof_releases_owned | PASS | 9 |
| cancel_during_delay | PASS | 9 |
| cancel_during_string | PASS | 10 |
| cancel_dead_key_second_stroke | PASS | 10 |
| runtime_error_releases_owned | PASS | 9 |
| function_depth_error_releases | PASS | 9 |
| loop_budget_error_releases | PASS | 9 |
| storage_read_error_releases | PASS | 10 |
| hold_queue_refusal_no_commit | PASS | 11 |
| release_refusal_clears_logical_owner | PASS | 13 |
| stop_release_refusal_priority | PASS | 16 |
| reset_refusal_waits_before_tail | PASS | 15 |
| disconnect_poll_cancels_owned | PASS | 13 |
| disconnect_event_reconnect_between_ticks | PASS | 11 |
| backpressure_is_not_disconnect | PASS | 8 |
| live_disconnect_clears_idle_hold | PASS | 10 |
| new_script_clears_live_hold | PASS | 12 |
| web_cli_cannot_release_script_hold | PASS | 9 |
| live_holds_survive_commands_until_reset | PASS | 20 |
| new_script_after_cancel_no_leak | PASS | 10 |
| hid_mode_off_releases_owner | PASS | 12 |
| multiline_owned_reports_spiffs_sd | PASS | 42 |
| malformed_hold_zero_hid | PASS | 35 |
| malformed_release_zero_hid | PASS | 28 |
| malformed_inject_mod_zero_hid | PASS | 28 |
| reset_stop_args_zero_hid | PASS | 14 |
| ownership_command_prefixes_rejected | PASS | 35 |
| new_command_function_collisions | PASS | 35 |
| comment_text_literals_not_ownership | PASS | 7 |
| case_tabs_and_modifier_aliases | PASS | 18 |
| direct_report_overflow_null_validation | PASS | 8 |
| repeated_ownership_stress | PASS | 8005 |
| transient_release_refusal_restores_owned | PASS | 13 |
| eof_release_refusal_clears_logical_owner | PASS | 11 |
| cancel_pending_hold_before_acceptance | PASS | 7 |
| disconnect_during_text_cancels_tail | PASS | 11 |
| while_condition_runtime_error_releases | PASS | 9 |
| function_return_seek_error_releases | PASS | 10 |
| source_changed_while_owned_releases | PASS | 10 |
| next_script_after_disconnect_recovery | PASS | 10 |
| atomic_event_callback_no_execution_lock | PASS | 11 |
| implicit_function_return_owner_lifetime | PASS | 15 |
| unsupported_inactive_hold_preflight | PASS | 7 |
| live_stop_payload_releases_idle_hold | PASS | 9 |
| latched_disconnect_blocks_enqueue_before_update | PASS | 10 |
| ownership_allocation_probe | PASS | 9002 |

### Stage12

| Test | Status | Assertions |
| --- | --- | ---: |
| initial_unknown_not_false | PASS | 6 |
| all_led_masks_and_padding | PASS | 288 |
| invalid_ids_lengths_null_padding | PASS | 10 |
| actual_keyboard_output_virtual_hook | PASS | 3 |
| actual_keyboard_control_set_report_hook | PASS | 4 |
| duplicates_do_not_count_changes | PASS | 1003 |
| per_key_transition_counters | PASS | 3 |
| first_report_auto_saves_attach_state | PASS | 8 |
| explicit_save_updates_saved_state | PASS | 9 |
| save_unknown_fails_truthfully | PASS | 5 |
| saved_unknown_expression | PASS | 5 |
| readonly_assignment_preflight | PASS | 3 |
| fake_internal_declaration_preflight | PASS | 3 |
| fake_internal_define_alias_preflight | PASS | 3 |
| read_cannot_shadow_internal | PASS | 3 |
| unsupported_read_preflight | PASS | 3 |
| unsupported_write_preflight | PASS | 3 |
| all_native_registry_names_reserved | PASS | 75 |
| os_extension_and_user_variables_preserved | PASS | 5 |
| timeout_extension_assignment_and_limits | PASS | 6 |
| timeout_assignment_expression_shared_evaluator | PASS | 5 |
| constant_invalid_timeout_preflight | PASS | 3 |
| live_wait_stop_cancellable | PASS | 3 |
| timeout_resets_between_scripts | PASS | 10 |
| no_internal_symbol_table_consumption | PASS | 18 |
| canonical_on_off_waits_all_keys | PASS | 36 |
| wait_already_desired_is_immediate | PASS | 5 |
| unknown_off_does_not_succeed | PASS | 5 |
| wait_unknown_becomes_observed_off | PASS | 6 |
| change_unknown_first_report_is_baseline | PASS | 6 |
| change_duplicate_reports_do_not_finish | PASS | 5 |
| rapid_changes_between_ticks_not_lost | PASS | 5 |
| change_all_three_independent | PASS | 18 |
| timeout_wrap_safe | PASS | 5 |
| malformed_lock_command_preflight | PASS | 3 |
| malformed_save_restore_preflight | PASS | 3 |
| lock_commands_function_collision | PASS | 3 |
| inactive_branch_no_wait_or_save | PASS | 5 |
| lock_variables_if_define_function_return | PASS | 5 |
| lock_variables_while_updates | PASS | 6 |
| wait_inside_nested_control_and_function | PASS | 5 |
| numeric_interpolation_observed_state | PASS | 5 |
| unknown_interpolation_runtime_error | PASS | 5 |
| unsupported_interpolation_runtime_error | PASS | 5 |
| restore_noop_no_keyboard_output | PASS | 5 |
| restore_unknown_current_saved_rejected | PASS | 5 |
| restore_requires_hid_enabled | PASS | 5 |
| restore_rejects_held_modifier | PASS | 5 |
| restore_rejects_held_key | PASS | 5 |
| restore_three_keys_ack_exact_reports | PASS | 51 |
| restore_no_ack_times_out_no_retoggle | PASS | 5 |
| restore_wrong_feedback_not_ack | PASS | 5 |
| restore_rechecks_pending_toggle_after_backpressure | PASS | 24 |
| restore_default_delay_after_success | PASS | 5 |
| restore_backpressure_timeout | PASS | 6 |
| stop_cancels_wait_and_releases_hold | PASS | 4 |
| stop_payload_inside_function_preserves_feedback | PASS | 7 |
| reset_preserves_observed_and_saved_state | PASS | 5 |
| runtime_timeout_releases_held_keys | PASS | 5 |
| cancel_restore_during_press | PASS | 4 |
| disconnect_immediate_unknown_and_stale_token | PASS | 7 |
| unmounted_reports_rejected | PASS | 3 |
| disconnect_cancels_wait_and_reconnect_clean | PASS | 9 |
| feedback_survives_separate_script_runs | PASS | 9 |
| live_cli_excluded_during_script_wait | PASS | 3 |
| live_save_restore_state | PASS | 4 |
| wait_command_backpressure_independent | PASS | 5 |
| feedback_during_input_preserves_reports | PASS | 6 |
| callback_does_not_wait_on_executor_lock | PASS | 2 |
| concurrent_feedback_and_snapshot_reads | PASS | 10001 |
| concurrent_disconnect_never_revives_old_session | PASS | 100 |
| transition_counter_crosses_16bit_boundary | PASS | 65538 |
| storage_requested_failed_registry_truthful | PASS | 8 |
| storage_preparing_active_ejected_registry | PASS | 13 |
| storage_retry_and_off_registry | PASS | 8 |
| attackmode_does_not_fabricate_lock_state | PASS | 5 |
| storage_read_error_after_wait_releases_keys | PASS | 4 |
| sd_spiffs_lock_fixture | PASS | 10 |
| saved_state_invalidated_on_backend_begin | PASS | 1 |
| feedback_registry_allocation_probe | PASS | 50002 |

### Stage13

| Test | Status | Assertions |
| --- | --- | ---: |
| alias_POWERSHELL | PASS | 6 |
| alias_BATCH | PASS | 6 |
| alias_BASH | PASS | 6 |
| alias_JAVASCRIPT | PASS | 6 |
| alias_PYTHON | PASS | 6 |
| alias_RUBY | PASS | 6 |
| alias_HTML | PASS | 6 |
| alias_ln_POWERSHELL | PASS | 6 |
| alias_ln_BATCH | PASS | 6 |
| alias_ln_BASH | PASS | 6 |
| alias_ln_JAVASCRIPT | PASS | 6 |
| alias_ln_PYTHON | PASS | 6 |
| alias_ln_RUBY | PASS | 6 |
| alias_ln_HTML | PASS | 6 |
| new_keyword_prefixes_rejected | PASS | 28 |
| documentation_heading | PASS | 6 |
| ordinary_comment_forms | PASS | 6 |
| invalid_comment_heading | PASS | 8 |
| unterminated_documentation | PASS | 8 |
| alias_cross_terminator | PASS | 8 |
| alias_suffixed_terminator | PASS | 8 |
| alias_suffixed_end_is_literal_data | PASS | 6 |
| alias_inline_rejected | PASS | 8 |
| alias_unknown_rejected | PASS | 8 |
| alias_unterminated | PASS | 8 |
| alias_define_interpolation_order | PASS | 6 |
| alias_literal_preprocessing | PASS | 6 |
| alias_empty_block | PASS | 6 |
| alias_bom_crlf_no_newline | PASS | 6 |
| alias_lowercase_tabs | PASS | 6 |
| extension_functions | PASS | 6 |
| extension_sequential_body | PASS | 6 |
| extension_version_optional | PASS | 6 |
| extension_duplicate | PASS | 8 |
| extension_nested | PASS | 8 |
| extension_invalid_name | PASS | 8 |
| extension_missing_end | PASS | 8 |
| extension_unmatched_end | PASS | 8 |
| extension_end_arguments | PASS | 8 |
| extension_version_duplicate | PASS | 8 |
| extension_version_misplaced | PASS | 8 |
| extension_version_outside | PASS | 8 |
| extension_version_malformed | PASS | 8 |
| extension_control_boundary | PASS | 8 |
| extension_function_boundary | PASS | 8 |
| extension_not_top_level | PASS | 8 |
| extension_exact_limit | PASS | 6 |
| extension_limit_plus_one | PASS | 7 |
| preprocess_true_false_else | PASS | 6 |
| preprocess_not_true_undefined | PASS | 6 |
| preprocess_bare_label | PASS | 6 |
| preprocess_order_forward_definition | PASS | 6 |
| preprocess_excluded_define_inert | PASS | 6 |
| preprocess_included_define_global_expansion | PASS | 6 |
| preprocess_text_flag_ambiguous_rejected | PASS | 8 |
| preprocess_recursive_flag_rejected | PASS | 8 |
| preprocess_invalid_label | PASS | 8 |
| preprocess_extra_condition_tokens | PASS | 8 |
| preprocess_missing_end | PASS | 8 |
| preprocess_unmatched_end | PASS | 8 |
| preprocess_unmatched_else | PASS | 8 |
| preprocess_duplicate_else | PASS | 8 |
| preprocess_marker_arguments | PASS | 8 |
| preprocess_nested_parent_exclusion | PASS | 6 |
| preprocess_exact_depth | PASS | 6 |
| preprocess_depth_plus_one | PASS | 8 |
| preprocess_excluded_runtime_not_validated | PASS | 6 |
| preprocess_excluded_function_not_inventoried | PASS | 7 |
| preprocess_excluded_variable_not_inventoried | PASS | 7 |
| preprocess_excluded_storage_hid_inert | PASS | 7 |
| preprocess_comment_directives_literal | PASS | 6 |
| preprocess_excluded_text_structural_error | PASS | 8 |
| preprocess_excluded_comment_missing_end | PASS | 8 |
| preprocess_wrapper_crossing | PASS | 8 |
| preprocess_wrapper_end_crossing | PASS | 8 |
| macro_cannot_create_wrapper | PASS | 7 |
| macro_cannot_create_preprocessor | PASS | 7 |
| macro_cannot_create_alias | PASS | 7 |
| checked_in_source_fixture | PASS | 7 |
| checked_in_exclusion_fixture | PASS | 7 |
| integration_spiffs | PASS | 6 |
| integration_sd | PASS | 6 |
| frozen_flags_after_function_seek | PASS | 6 |
| frozen_flags_after_loop_seek | PASS | 6 |
| selected_structure_validated_before_hid | PASS | 7 |
| preprocess_repeat_history | PASS | 6 |
| maximum_line_inside_exclusion | PASS | 6 |
| overlong_line_inside_exclusion | PASS | 8 |
| source_limit_inside_exclusion | PASS | 6 |
| exact_line_bitmap_boundary | PASS | 6 |
| bitmap_boundary_plus_one | PASS | 7 |
| excluded_read_fault | PASS | 6 |
| preprocessing_rewind_fault | PASS | 6 |
| cancellation_during_preprocessing | PASS | 7 |
| cancellation_during_alias_typing | PASS | 6 |
| alias_usb_backpressure | PASS | 6 |
| large_streamed_alias | PASS | 6 |
| canonical_led_colors_and_override | PASS | 7 |
| canonical_led_arguments_rejected | PASS | 8 |
| canonical_led_inactive_branch | PASS | 7 |
| canonical_led_error_priority | PASS | 6 |
| canonical_led_new_script_defaults | PASS | 14 |
| canonical_led_open_error_priority | PASS | 8 |
| new_command_function_names_reserved | PASS | 42 |
| live_metadata_rejected | PASS | 2 |
| excluded_duplicate_constants_ignored | PASS | 6 |
| included_duplicate_constants_rejected | PASS | 8 |
| excluded_extension_names_do_not_exhaust | PASS | 6 |
| macro_cannot_create_version | PASS | 7 |
| macro_cannot_create_wrapper_direct | PASS | 7 |
| constant_text_cannot_escape_alias | PASS | 6 |
| comment_define_not_collected_in_alias | PASS | 6 |
| combined_preprocess_runtime_depth | PASS | 6 |
| preprocess_no_expansion_of_flag_name | PASS | 6 |
| preprocess_define_whitespace_literal_boolean | PASS | 6 |
| canonical_led_disabled_setting | PASS | 5 |
| canonical_led_stop_retains_override | PASS | 7 |
| legacy_rgb_behavior_retained | PASS | 5 |
| function_seek_fault_after_preprocessing | PASS | 6 |
| preflight_cancellation_live_isolation | PASS | 7 |
| run_state_inclusion_isolation | PASS | 12 |
| preprocessing_bitmap_allocation_probe | PASS | 8195 |

### Stage14

| Test | Status | Assertions |
| --- | --- | ---: |
| checked_in_random_jitter_fixture | PASS | 8 |
| default_registry_values | PASS | 7 |
| inclusive_minimum_maximum | PASS | 3 |
| equal_bounds_no_entropy | PASS | 4 |
| full_uint16_range | PASS | 3 |
| reversed_range_atomic_failure | PASS | 2 |
| unbiased_rejection_then_acceptance | PASS | 2 |
| rejection_budget_exhaustion | PASS | 2 |
| all_range_residues_balanced | PASS | 1010 |
| every_uint16_singleton_boundary | PASS | 65537 |
| seeded_host_replay | PASS | 200 |
| invalid_literal_range_preflight | PASS | 7 |
| negative_literal_range_preflight | PASS | 7 |
| jitter_boolean_validation | PASS | 7 |
| atomic_internal_write_validation | PASS | 6 |
| numeric_bounds_follow_uint16_arithmetic | PASS | 14 |
| random_int_readonly | PASS | 7 |
| random_reserved_declaration | PASS | 7 |
| unsupported_seed_and_encoding | PASS | 7 |
| unsupported_scancode_variable | PASS | 7 |
| inject_var_still_deferred | PASS | 7 |
| restart_still_deferred | PASS | 7 |
| random_character_prose_alias_unconfirmed | PASS | 7 |
| random_string_syntax_not_invented | PASS | 7 |
| random_command_arguments_rejected | PASS | 7 |
| random_command_prefix_rejected | PASS | 7 |
| random_command_function_collision | PASS | 7 |
| syntax_evaluator_never_draws | PASS | 2 |
| compiled_program_never_draws | PASS | 2 |
| preflight_invalid_after_random | PASS | 7 |
| random_expression_each_reference_once | PASS | 7 |
| random_boolean_eager_expression | PASS | 7 |
| canonical_random_condition | PASS | 7 |
| legacy_random_condition_once | PASS | 7 |
| legacy_mixed_numeric_text_preserved | PASS | 6 |
| random_while_each_header_once | PASS | 7 |
| function_suspension_preserves_random_operand | PASS | 7 |
| function_return_random_bounds | PASS | 7 |
| excluded_preprocessing_no_rng | PASS | 7 |
| inactive_runtime_branch_no_rng | PASS | 7 |
| reversed_bounds_runtime_safe_stop | PASS | 7 |
| reversed_bounds_repaired_before_draw | PASS | 6 |
| raw_failure_releases_ownership | PASS | 7 |
| runtime_jitter_boolean_invalid | PASS | 6 |
| settings_reset_between_runs | PASS | 14 |
| random_command_all_sets_us | PASS | 42 |
| random_special_all_de_locale | PASS | 28 |
| random_letters_all_de_report_bytes | PASS | 58 |
| random_command_repeat_resamples | PASS | 7 |
| random_interpolation_compatibility | PASS | 7 |
| random_numeric_delay_consumer | PASS | 6 |
| random_function_argument_setting | PASS | 7 |
| random_live_settings_persist_until_reset | PASS | 5 |
| jitter_disabled_exact_existing_timing | PASS | 17 |
| jitter_zero_max_no_entropy | PASS | 7 |
| jitter_additive_per_press_timing | PASS | 24 |
| jitter_default_and_explicit_delay_independent | PASS | 12 |
| jitter_multiline_enter_and_blank | PASS | 7 |
| jitter_named_chord_report_bytes | PASS | 8 |
| jitter_persistent_modifier_text | PASS | 7 |
| jitter_german_deadkey_strokes | PASS | 7 |
| jitter_backpressure_no_redraw | PASS | 7 |
| jitter_random_command_backpressure | PASS | 7 |
| jitter_cancel_pending_interval | PASS | 7 |
| jitter_runtime_source_failure | PASS | 7 |
| jitter_release_refusal_safe_retry | PASS | 7 |
| jitter_disconnect_reconnect | PASS | 9 |
| jitter_clock_wrap_safe | PASS | 6 |
| jitter_hold_release_idempotence | PASS | 7 |
| jitter_maximum_bound | PASS | 7 |
| script_storage_read_fault_no_rng | PASS | 5 |
| script_seek_fault_no_rng | PASS | 5 |
| jitter_loop_runtime_seek_failure | PASS | 8 |
| jitter_live_ownership_isolation | PASS | 7 |
| long_seeded_randomized_loop | PASS | 7 |
| random_numeric_no_hid | PASS | 9 |
| random_source_null_default_adapter | PASS | 1 |
| random_range_allocation_probe | PASS | 20001 |

### Historical language diagnostics

* XPASS known_nested_if: expected 'good', actual 'good'
* XPASS known_canonical_if: expected 'good', actual 'good'
* XPASS known_false_while: expected 'good', actual 'good'
* XPASS known_f13_mapping: expected usage 104, actual 104
* XPASS known_german_ascii_table: expected 128 records, actual 128; exact content/alignment independently checked by Stage 8 when table is corrected

### Stage15 historical routing

| Test | Status | Assertions |
| --- | --- | ---: |
| unpatched known_hid_vectors_no_numeric_encoding | PASS | 22 |
| unpatched normalized_interrupt_output | PASS | 3 |
| unpatched legacy_type_zero_interrupt | PASS | 1 |
| unpatched nonzero_control_output | OBSERVED | 2 |
| unpatched feature_led_type_separation | OBSERVED | 2 |
| unpatched input_type_rejected | OBSERVED | 1 |
| unpatched invalid_type_rejected | OBSERVED | 1 |
| unpatched invalid_instance | OBSERVED | 1 |
| unpatched zero_transfer_backed_buffer | OBSERVED | 2 |
| unpatched report_id_only_interrupt | PASS | 1 |
| unpatched zero_length_control_output | PASS | 1 |
| unpatched null_control_output | PASS | 1 |
| unpatched unknown_report_id | PASS | 1 |
| unpatched zero_id_device_no_prefix_stripping | PASS | 2 |
| unpatched all_led_masks_through_actual_route | PASS | 33 |
| unpatched padding_and_length_rejection | PASS | 2 |
| unpatched repeated_report_not_transition | PASS | 1 |
| unpatched detached_feedback_rejection | PASS | 1 |
| unpatched stale_explicit_token_rejection | PASS | 2 |
| unpatched routing_during_owned_injection | PASS | 4 |
| unpatched stock_output_queue_wait_policy | OBSERVED | 1 |
| unpatched null_zero_interrupt | XFAIL | 0 |
| unpatched empty_onepast_interrupt | XFAIL | 0 |
| unpatched null_nonzero_interrupt | XFAIL | 0 |
| unpatched debug_invalid_type_unknown_id | XFAIL | 0 |
| unpatched stock_output_null | XFAIL | 0 |
| unpatched stock_output_empty_onepast | XFAIL | 0 |
| paired_proposal known_hid_vectors_no_numeric_encoding | PASS | 22 |
| paired_proposal normalized_interrupt_output | PASS | 3 |
| paired_proposal legacy_type_zero_interrupt | PASS | 1 |
| paired_proposal nonzero_control_output | PASS | 2 |
| paired_proposal feature_led_type_separation | PASS | 2 |
| paired_proposal input_type_rejected | PASS | 1 |
| paired_proposal invalid_type_rejected | PASS | 1 |
| paired_proposal invalid_instance | PASS | 1 |
| paired_proposal zero_transfer_backed_buffer | PASS | 2 |
| paired_proposal report_id_only_interrupt | PASS | 1 |
| paired_proposal zero_length_control_output | PASS | 1 |
| paired_proposal null_control_output | PASS | 1 |
| paired_proposal unknown_report_id | PASS | 1 |
| paired_proposal zero_id_device_no_prefix_stripping | PASS | 2 |
| paired_proposal all_led_masks_through_actual_route | PASS | 33 |
| paired_proposal padding_and_length_rejection | PASS | 2 |
| paired_proposal repeated_report_not_transition | PASS | 1 |
| paired_proposal detached_feedback_rejection | PASS | 1 |
| paired_proposal stale_explicit_token_rejection | PASS | 2 |
| paired_proposal routing_during_owned_injection | PASS | 4 |
| paired_proposal stock_output_queue_wait_policy | PASS | 1 |
| paired_proposal null_zero_interrupt | PASS | 1 |
| paired_proposal empty_onepast_interrupt | PASS | 1 |
| paired_proposal null_nonzero_interrupt | PASS | 1 |
| paired_proposal debug_invalid_type_unknown_id | PASS | 1 |

### Stage16 routing

| Test | Status | Assertions |
| --- | --- | ---: |
|  known_hid_vectors_no_numeric_encoding | PASS | 22 |
|  normalized_interrupt_output | PASS | 3 |
|  legacy_type_zero_interrupt | PASS | 1 |
|  nonzero_control_output | PASS | 2 |
|  feature_led_type_separation | PASS | 2 |
|  input_type_rejected | PASS | 1 |
|  invalid_type_rejected | PASS | 1 |
|  invalid_instance | PASS | 1 |
|  zero_transfer_backed_buffer | PASS | 2 |
|  report_id_only_interrupt | PASS | 1 |
|  zero_length_control_output | PASS | 1 |
|  null_control_output | PASS | 1 |
|  unknown_report_id | PASS | 1 |
|  zero_id_device_no_prefix_stripping | PASS | 2 |
|  all_led_masks_through_actual_route | PASS | 33 |
|  padding_and_length_rejection | PASS | 2 |
|  repeated_report_not_transition | PASS | 1 |
|  detached_feedback_rejection | PASS | 1 |
|  stale_explicit_token_rejection | PASS | 2 |
|  routing_during_owned_injection | PASS | 4 |
|  stock_output_queue_wait_policy | OBSERVED | 1 |
|  null_zero_interrupt | PASS | 1 |
|  empty_onepast_interrupt | PASS | 1 |
|  null_nonzero_interrupt | PASS | 1 |
|  debug_invalid_type_unknown_id | PASS | 1 |
|  integrated_feature_cannot_change_known_led | PASS | 1 |
|  integrated_all_report_types_and_ids | PASS | 65536 |
|  integrated_null_lengths_types | PASS | 1 |
|  integrated_empty_output_never_enters_stock_hook | PASS | 2 |
|  integrated_payload_boundaries | PASS | 6 |
|  integrated_bounded_callback_reentry | PASS | 2 |
|  integrated_executor_lock_independent | PASS | 1 |
|  integrated_concurrent_snapshots | PASS | 10001 |
|  integrated_input_backpressure_feedback | PASS | 2 |
|  integrated_disconnect_reconnect_unknown | PASS | 4 |
|  integrated_no_led_event_queue_post | PASS | 1 |

### Stage16 validation

| Test | Status | Assertions |
| --- | --- | ---: |
|  unpatched_tree_verified | PASS | 1 |
|  patched_tree_verified | PASS | 1 |
|  unpatched_core_rejected_for_stage16 | PASS | 1 |
|  patched_core_rejected_as_upstream_original | PASS | 1 |
|  unexpected_core_version_rejected | PASS | 1 |
|  unexpected_source_bytes_rejected | PASS | 1 |
|  installed_data_isolation_rejected | PASS | 1 |
|  installed_user_isolation_rejected | PASS | 1 |
|  existing_isolation_destination_rejected | PASS | 1 |
|  repository_isolation_destination_rejected | PASS | 1 |
|  build_requires_patched_core_argument | PASS | 1 |
|  ordinary_firmware_compile_rejected | PASS | 1 |
|  verified_firmware_compile_guard_enabled | PASS | 1 |
|  cli_unpatched_fallback_rejected_before_compile | PASS | 1 |
|  full_linked_production_firmware_provenance | PASS | 1 |

### Stage17

| Test | Status | Assertions |
| --- | --- | ---: |
|  stage17_synthetic_backup_roundtrip | PASS | 1 |
|  stage17_missing_backups | PASS | 1 |
|  stage17_owner_hashes_reject_synthetic_files | PASS | 1 |
|  stage17_custom_hashes_cannot_claim_owner_evidence | PASS | 1 |
|  stage17_old_new_size_raw_relocation_rejected | PASS | 1 |
|  stage17_wrong_backup_hash | PASS | 1 |
|  stage17_truncated_filesystem | PASS | 1 |
|  stage17_corrupt_partition_sector_hash | PASS | 1 |
|  stage17_invalid_spiffs_geometry_extractability | PASS | 1 |
|  stage17_partition_sector_full_backup_mismatch | PASS | 1 |
|  stage17_corrupted_partition_structure | PASS | 1 |
|  stage17_proposed_layout_not_original_backup | PASS | 1 |
|  stage17_valid_esp_image_checksum_digest | PASS | 1 |
|  stage17_invalid_esp_chip | PASS | 1 |
|  stage17_invalid_esp_checksum | PASS | 1 |
|  stage17_invalid_esp_digest | PASS | 1 |
|  stage17_invalid_esp_segment | PASS | 1 |
|  stage17_truncated_esp_digest | PASS | 1 |
|  stage17_legacy_flash_header_not_new | PASS | 1 |
|  stage17_actual_normal_artifact_checksum | PASS | 1 |
|  stage17_erased_recovery_image_rejected | PASS | 1 |
|  stage17_normal_firmware_exceeds_old_slots | PASS | 1 |
|  stage17_actual_patched_normal_link | PASS | 1 |
|  stage17_forged_safe_build_metadata_rejected | PASS | 1 |
|  stage17_rehashed_swapped_binary_rejected_by_elf | PASS | 1 |
|  stage17_actual_patched_safe_link | PASS | 1 |
|  stage17_complete_safe_plan_nvs_preserved | PASS | 1 |
|  stage17_old_app1_offset_rejected | PASS | 1 |
|  stage17_nvs_overlap_rejected | PASS | 1 |
|  stage17_overlapping_stored_erases_rejected | PASS | 1 |
|  stage17_non_aligned_stored_erases_rejected | PASS | 1 |
|  stage17_plan_nvs_metadata_rejected | PASS | 1 |
|  stage17_false_migration_authorization_rejected | PASS | 1 |
|  stage17_missing_plan_artifact_rejected | PASS | 1 |
|  stage17_path_traversal_rejected | PASS | 1 |
|  stage17_wrong_application_hash_rejected | PASS | 1 |
|  stage17_corrupt_otadata_even_with_rehashed_manifest | PASS | 1 |
|  stage17_corrupt_coredump_even_with_rehashed_manifest | PASS | 1 |
|  stage17_corrupt_partitions_even_with_rehashed_manifest | PASS | 1 |
|  stage17_corrupt_app0_even_with_rehashed_manifest | PASS | 1 |
|  stage17_corrupt_spiffs_even_with_rehashed_manifest | PASS | 1 |
|  stage17_normal_build_not_first_boot_safe | PASS | 1 |
|  stage17_sources_not_modified | PASS | 1 |
|  stage17_recovery_backup_exact_region | PASS | 1 |
|  stage17_checked_plan_generation_synthetic_only | PASS | 1 |
|  stage17_checked_plan_no_overwrite | PASS | 1 |
|  stage17_checked_plan_missing_owner_files | PASS | 1 |
|  stage17_checked_plan_wrong_owner_hashes | PASS | 1 |
|  stage17_failed_plan_creates_no_output | PASS | 1 |
|  stage17_provisional_artifact_inventory_not_authorization | PASS | 1 |
|  stage17_artifact_inventory_no_overwrite | PASS | 1 |
|  stage17_no_full_chip_erase_plan | PASS | 1 |
|  stage17_pre_setup_nvs_erase_risk_recorded | OBSERVED | 1 |
|  stage17_normal_spiffs_format_risk_preserved | OBSERVED | 1 |
|  stage17_normal_startup_compatibility | PASS | 10 |
|  stage17_safe_start_actual_setup_loop | PASS | 11 |
|  stage17_invalid_safe_profile_rejected | PASS | 1 |

### Stage18 NVS

| Test | Status | Assertions |
| --- | --- | ---: |
| historical_unpatched historical_no_free_pages_erase | OBSERVED | 3 |
| historical_unpatched historical_new_version_erase | OBSERVED | 3 |
| historical_unpatched historical_erase_failure_error_replaced | OBSERVED | 2 |
| normal protected_initial_unknown | PASS | 14 |
| normal protected_success | PASS | 4 |
| normal protected_no_free_pages | PASS | 17 |
| normal protected_new_version | PASS | 17 |
| normal protected_invalid_metadata | PASS | 17 |
| normal protected_missing_partition | PASS | 17 |
| normal protected_flash_read_failure | PASS | 17 |
| normal protected_flash_initialization_failure | PASS | 17 |
| normal protected_flash_operation_failure | PASS | 17 |
| normal protected_no_memory | PASS | 17 |
| normal protected_unexpected_positive | PASS | 17 |
| normal protected_unexpected_negative | PASS | 17 |
| normal protected_repeat_failure | PASS | 39 |
| normal protected_retry_never_arms_failed_app | PASS | 15 |
| normal observed_sdk_side_effect_outside_policy | OBSERVED | 13 |
| safe protected_initial_unknown | PASS | 14 |
| safe protected_success | PASS | 14 |
| safe protected_no_free_pages | PASS | 17 |
| safe protected_new_version | PASS | 17 |
| safe protected_invalid_metadata | PASS | 17 |
| safe protected_missing_partition | PASS | 17 |
| safe protected_flash_read_failure | PASS | 17 |
| safe protected_flash_initialization_failure | PASS | 17 |
| safe protected_flash_operation_failure | PASS | 17 |
| safe protected_no_memory | PASS | 17 |
| safe protected_unexpected_positive | PASS | 17 |
| safe protected_unexpected_negative | PASS | 17 |
| safe protected_repeat_failure | PASS | 39 |
| safe protected_retry_never_arms_failed_app | PASS | 15 |
| safe observed_sdk_side_effect_outside_policy | OBSERVED | 13 |

### Stage18 dependency

| Test | Status | Assertions |
| --- | --- | ---: |
|  stage18_original_source_preserved | PASS | 1 |
|  stage18_actual_init_before_setup_task | PASS | 1 |
|  stage18_combined_patched_source_verified | PASS | 1 |
|  stage18_hid_only_core_rejected | PASS | 1 |
|  stage18_modified_policy_bytes_rejected | PASS | 1 |
|  stage18_native_missing_policy_guard_rejected | PASS | 1 |
|  stage18_verified_policy_compile_guard | PASS | 1 |
|  stage18_missing_core_hook_cannot_link | PASS | 1 |
|  stage18_final_linked_nvs_policy | PASS | 1 |


Original initArduino compiler frame48bytes also verified with the same compiler/configuration; protected48bytes, no growth.

## Every modified and created file

* EvilDuckS3/EvilDuckS3.ino
* EvilDuckS3/nvs_startup.h
* deployment/stage18/README.md
* deployment/stage18/artifact-inventory.json
* deployment/stage18/bootloader.bin
* deployment/stage18/coredump-empty.bin
* deployment/stage18/normal-app.bin
* deployment/stage18/otadata-app0.bin
* deployment/stage18/partitions-sector.bin
* deployment/stage18/safe-app.bin
* docs/stage18-dependency-pin.json
* docs/stage18-hardware-readiness.md
* docs/stage18-normal-build.log
* docs/stage18-normal-linked-nvs.txt
* docs/stage18-normal-linked-startup.txt
* docs/stage18-normal-provenance.json
* docs/stage18-reference-evidence.json
* docs/stage18-report.md
* docs/stage18-reproduction.md
* docs/stage18-results.json
* docs/stage18-safe-build.log
* docs/stage18-safe-linked-nvs.txt
* docs/stage18-safe-linked-startup.txt
* docs/stage18-safe-provenance.json
* docs/stage18-stack-results.json
* docs/stage18-startup-analysis.md
* docs/stage18-startup-stack.json
* proposals/arduino-esp32-3.3.0-nvs-preservation.patch
* tests/stage17/run_tests.py
* tests/stage17/startup.cpp
* tests/stage18/README.md
* tests/stage18/dependency_tests.py
* tests/stage18/run_tests.py
* tests/stage18/startup.cpp
* tools/build_s3.py
* tools/deployment_inventory.py
* tools/deployment_plan.py
* tools/deployment_preflight.py
* tools/patched_core.py
* tools/verify_patched_firmware.py
