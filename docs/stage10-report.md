# Stage 10 implementation and verification report

Baseline: `stage9-duckyscript-compatibility-audit`, `24e8a88f56dd4445d7d69924220f7dc2d66f0fa2`. Delivery branch: `stage10-usb-storage-reliability`. The delivery commit contains this report; obtain its exact identity with `git rev-parse HEAD`.

## Implemented changes

Production MSC initialization is now three cooperative steps with truthful requested/preparing/active/failed/ejected state, an elapsed deadline, explicit retry and cancellation. ATTACKMODE waits for completion rather than reporting false success. Existing image files are opened nontruncating, never implicitly created, formatted, resized or replaced. Failed initialization and transfers quarantine media and retain useful errors. CLI and web report actual local media state separately from the request.

Callbacks implement the pinned TinyUSB byte-address contract using 64-bit arithmetic, whole-range checks, a 4096-byte SDK transfer bound, checked seeks, short-I/O quarantine, zero-length handling and contention-aware nonblocking lock admission. SDK callback addresses remain stable during deactivation to avoid pointer teardown races. SD adapters and web upload chunks share the existing execution lock. See [design](stage10-design.md) for exact source contracts, compatibility decisions and failure policies.

## Verification actually executed

All test names, outcomes, assertion counts and observation stdout are recorded in [machine-readable results](stage10-results.json). Observations are not claims of canonical compatibility.

| Suite | PASS | FAIL | Assertions |
| --- | ---: | ---: | ---: |
| stage_1 | 5 | 0 | 127 |
| stage_2 | 30 | 0 | 791 |
| stage_25 | 30 | 0 | 190 |
| stage_3 | 40 | 0 | 13814 |
| stage_4 | 42 | 0 | 60626 |
| stage_5 | 59 | 0 | 92019 |
| stage_6 | 65 | 0 | 60726 |
| stage_7 | 68 | 0 | 40520 |
| stage_8 | 41 | 0 | 43666 |
| Previous diagnostic sanity checks | — | 0 | 12 |
| Stage 9 observations | 79 matches | 0 mismatches | 596 |
| Stage 10 production-source faults | 52 | 0 | 1,608 |

**432 regular PASS, 0 FAIL; 5 historical XPASS, 0 XFAIL; 79 audit observations matched separately; 314,695 total assertions.** Historical XPASS labels remain auditable: `known_nested_if`, `known_canonical_if`, `known_false_while`, `known_f13_mapping`, `known_german_ascii_table`. Their expectations were not silently changed.

The Stage 9 actual attackmode failure probe legitimately changes from observing false success/retry suppression to `RESOLVED_STAGE10`: failed startup returns false, active remains false, requested remains true, and an identical request retries. This does not resolve native USB personality conformance. Historical Stage 9 report/results are retained.

ASan/UBSan: zero findings across all executed C++ mock/probe targets. Stage 2.5 Python validation is not sanitizer-instrumented. The previous allocation probes pass. The new callback probe performs 2,000 accepted transfers with zero observed C++ new allocations; real ESP SD/FatFS/USB heap behavior remains unmeasured. An existing Stage 6 test-source misleading-indentation warning is unchanged; final Stage 10 target compiles without warnings. An initial firmware compile detected an accidentally duplicated web Guard declaration; it was removed and the subsequent clean build passed. No failure remains.

## Clean build and resource comparison

Build wrapper: `python3 tools/build_s3.py --arduino-cli <arduino-cli> --config-file <arduino-cli.yaml> --build-dir <fresh-directory> --jobs 2`. Arduino ESP32 **3.3.0**, QIO 80 MHz, USB-OTG TinyUSB, CDC on boot enabled, MSC/DFU boot defaults, CPU 240 MHz, PSRAM disabled.

Exact FQBN:

```text
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

| Measurement | Stage 9 | Stage 10 | Growth |
| --- | ---: | ---: | ---: |
| Compiler program usage | 1,308,883 B | 1,312,631 B | 3,748 B |
| Actual application binary | 1,309,024 B | 1,312,784 B | 3,760 B |
| Static RAM | 80,408 B | 80,416 B | 8 B |
| Remaining compiler RAM | — | 247,264 B | — |

Both unchanged `0x740000` OTA slots retain **6,289,392 B / 82.73147%** free. Application SHA-256: `27f664b8a2c8237f7ad542056ec607efe6c3a46ccb58a5081cbf83b2cbc69078`. Build/image checks confirm ESP32-S3, intended 16 MiB configuration, standard app0 address and custom partitions. SDK bootloader header mode convention is retained. [Compiler build log](stage10-build.log) records actual successful compilation. No migration image or partition changes were introduced.

[Compiler stack results](stage10-stack-results.json) cover 13 modules; [baseline storage estimates](stage10-baseline-storage-stack.json) were independently compiled from the exact Stage 9 source using pinned compiler flags. Preparation frame: 592 B (512 B probe), versus old blocking image-creation frame 576 B (+16 B). Read/write callback frames: 48 B each. Former ten-module function frames remain unchanged. These are individual compiler estimates, not transitive call-chain/task high-water measurements; driver stack and real heap require physical validation.

## Exact new test results

| Test | Result | Assertions |
| --- | --- | ---: |
| `startup_success_truthful` | PASS | 6 |
| `startup_missing_card` | PASS | 6 |
| `startup_missing_image_no_create` | PASS | 6 |
| `startup_wrong_size_no_truncate` | PASS | 22 |
| `startup_open_failure` | PASS | 4 |
| `startup_probe_seek_failure` | PASS | 5 |
| `startup_probe_short_read` | PASS | 4 |
| `startup_sdk_failure_cleanup` | PASS | 6 |
| `retry_failed_startup` | PASS | 3 |
| `repeated_begin_idempotent` | PASS | 3 |
| `retry_ejected_media` | PASS | 7 |
| `stale_host_load_after_off` | PASS | 5 |
| `stale_host_load_after_cancel` | PASS | 5 |
| `writable_reset_after_end` | PASS | 8 |
| `read_nonzero_offset` | PASS | 6 |
| `write_nonzero_offset` | PASS | 7 |
| `cross_sector_unaligned` | PASS | 6 |
| `last_byte_and_exact_end` | PASS | 7 |
| `invalid_range_and_overflow` | PASS | 12 |
| `zero_length_null` | PASS | 5 |
| `null_nonzero` | PASS | 5 |
| `transfer_limit` | PASS | 6 |
| `read_seek_failure_no_wrong_read` | PASS | 9 |
| `write_seek_failure_no_wrong_write` | PASS | 9 |
| `short_read_quarantines` | PASS | 9 |
| `short_write_prefix_and_quarantine` | PASS | 10 |
| `card_removal_callback` | PASS | 9 |
| `card_removal_main_loop` | PASS | 7 |
| `backing_size_changed` | PASS | 8 |
| `fault_cleanup_and_explicit_recovery` | PASS | 6 |
| `eject_load_and_power_stop` | PASS | 9 |
| `cancel_before_open` | PASS | 3 |
| `cancel_after_open` | PASS | 3 |
| `timeout_wrap_safe` | PASS | 6 |
| `media_absent_until_validated` | PASS | 4 |
| `script_waits_for_storage` | PASS | 7 |
| `script_startup_failure_stops_tail` | PASS | 6 |
| `stop_pending_startup` | PASS | 6 |
| `stop_preserves_active_media` | PASS | 8 |
| `live_cli_ownership_while_preparing` | PASS | 9 |
| `script_and_host_activity` | PASS | 206 |
| `function_condition_storage_startup` | PASS | 7 |
| `live_cli_failure_status_and_retry` | PASS | 7 |
| `callback_lock_contention_busy` | PASS | 6 |
| `callback_error_storm_no_io` | PASS | 1004 |
| `concurrent_callback_mode_stop` | PASS | 5 |
| `sd_adapter_interleaving` | PASS | 7 |
| `sd_adapter_removal_and_remount` | PASS | 3 |
| `off_cancels_pending` | PASS | 1 |
| `repeated_failure_recovery` | PASS | 81 |
| `no_callback_heap_allocation` | PASS | 5 |
| `build_without_msc_reports_unavailable` | PASS | 4 |

## Previous regression results by test

| Suite | Test | Result | Assertions |
| --- | --- | --- | ---: |
| stage_1 | `supported_commands_and_mock_interfaces` | PASS | 29 |
| stage_1 | `script_run_state_isolation` | PASS | 22 |
| stage_1 | `cooperative_delay_and_text_cancellation` | PASS | 33 |
| stage_1 | `repeat_timing_and_control_loop_yield` | PASS | 24 |
| stage_1 | `live_commands_cannot_mutate_running_script` | PASS | 19 |
| stage_2 | `stage2_rem_comments` | PASS | 6 |
| stage_2 | `stage2_required_rem_block_fixture` | PASS | 12 |
| stage_2 | `stage2_comment_block_literal_commands` | PASS | 6 |
| stage_2 | `stage2_unterminated_rem_block_zero_hid` | PASS | 9 |
| stage_2 | `stage2_unmatched_end_rem_zero_hid` | PASS | 9 |
| stage_2 | `stage2_lf_source` | PASS | 6 |
| stage_2 | `stage2_crlf_source` | PASS | 6 |
| stage_2 | `stage2_utf8_bom` | PASS | 21 |
| stage_2 | `stage2_missing_final_newline` | PASS | 12 |
| stage_2 | `stage2_blank_lines` | PASS | 12 |
| stage_2 | `stage2_spaces_tabs_and_payload_preservation` | PASS | 7 |
| stage_2 | `stage2_maximum_line_length` | PASS | 12 |
| stage_2 | `stage2_overlong_line_zero_hid` | PASS | 18 |
| stage_2 | `stage2_source_byte_limits` | PASS | 16 |
| stage_2 | `stage2_source_line_limits` | PASS | 15 |
| stage_2 | `stage2_mismatched_control_blocks_zero_hid` | PASS | 18 |
| stage_2 | `stage2_unterminated_control_blocks_zero_hid` | PASS | 36 |
| stage_2 | `stage2_duplicate_else_zero_hid` | PASS | 18 |
| stage_2 | `stage2_block_depth_limit_zero_hid` | PASS | 9 |
| stage_2 | `stage2_text_blocks_literal_mode_and_deferred_runtime` | PASS | 30 |
| stage_2 | `stage2_unterminated_text_blocks_zero_hid` | PASS | 18 |
| stage_2 | `stage2_unmatched_text_terminators_zero_hid` | PASS | 18 |
| stage_2 | `stage2_mismatched_text_terminators_zero_hid` | PASS | 27 |
| stage_2 | `stage2_unknown_commands_zero_hid` | PASS | 27 |
| stage_2 | `stage2_keyword_prefixes_are_not_commands` | PASS | 128 |
| stage_2 | `stage2_malformed_statements_zero_hid` | PASS | 210 |
| stage_2 | `stage2_supported_extensions_and_bare_keys` | PASS | 8 |
| stage_2 | `stage2_storage_read_seek_faults` | PASS | 25 |
| stage_2 | `stage2_preflight_cooperative_stop_and_live_ownership` | PASS | 18 |
| stage_2 | `stage2_live_validation_and_limits` | PASS | 34 |
| stage_25 | `stage25_reviewed_partition_layout` | PASS | 15 |
| stage_25 | `stage25_overlapping_partitions_rejected` | PASS | 1 |
| stage_25 | `stage25_unaligned_application_rejected` | PASS | 1 |
| stage_25 | `stage25_reviewed_offsets_sizes_flags_enforced` | PASS | 10 |
| stage_25 | `stage25_core_version_pin_enforced` | PASS | 1 |
| stage_25 | `stage25_application_size_boundary` | PASS | 3 |
| stage_25 | `stage25_image_header_configuration_enforced` | PASS | 6 |
| stage_25 | `stage25_build_configuration_and_app_address_enforced` | PASS | 22 |
| stage_25 | `stage25_generated_16m_build_artifacts` | PASS | 4 |
| stage_25 | `stage25_corrupt_partition_binary_rejected` | PASS | 1 |
| stage_25 | `stage25_merged_image_wrong_address_rejected` | PASS | 1 |
| stage_25 | `stage25_stale_4m_partition_artifact_rejected` | PASS | 1 |
| stage_25 | `stage25_saved_physical_flash_capacity_guard` | PASS | 7 |
| stage_25 | `stage25_offline_source_archives_require_file_migration` | PASS | 11 |
| stage_25 | `stage25_offline_preparation_rejects_invalid_backups` | PASS | 6 |
| stage_25 | `stage25_offline_preparation_never_overwrites` | PASS | 2 |
| stage_25 | `stage25_build_wrapper_requires_clean_output` | PASS | 3 |
| stage_25 | `stage25_verified_device_map_differs_from_core_default` | PASS | 3 |
| stage_25 | `stage25_raw_spiffs_size_mismatch_refused` | PASS | 3 |
| stage_25 | `stage25_recorded_backup_hash_guards` | PASS | 4 |
| stage_25 | `stage25_file_level_extract_repack_roundtrip` | PASS | 8 |
| stage_25 | `stage25_file_level_empty_filesystem` | PASS | 1 |
| stage_25 | `stage25_file_level_capacity_and_overwrite_guards` | PASS | 7 |
| stage_25 | `stage25_corrupt_or_wrong_geometry_extraction_refused` | PASS | 4 |
| stage_25 | `stage25_alternative_layout_maximum_equal_slots` | PASS | 4 |
| stage_25 | `stage25_review_only_plan_preserves_nvs_and_initializes_both_apps` | PASS | 24 |
| stage_25 | `stage25_write_and_erase_region_guards` | PASS | 13 |
| stage_25 | `stage25_ota_initializer_selects_app0_deterministically` | PASS | 7 |
| stage_25 | `stage25_plan_refuses_unverified_files_and_backup_provenance` | PASS | 16 |
| stage_25 | `stage25_mac_old_core_rejected_before_compile` | PASS | 1 |
| stage_3 | `stage3_addition` | PASS | 3 |
| stage_3 | `stage3_subtraction` | PASS | 3 |
| stage_3 | `stage3_multiplication` | PASS | 3 |
| stage_3 | `stage3_division` | PASS | 3 |
| stage_3 | `stage3_modulo` | PASS | 3 |
| stage_3 | `stage3_exponentiation` | PASS | 3 |
| stage_3 | `stage3_equality` | PASS | 3 |
| stage_3 | `stage3_inequality` | PASS | 3 |
| stage_3 | `stage3_less_than` | PASS | 3 |
| stage_3 | `stage3_greater_than` | PASS | 3 |
| stage_3 | `stage3_less_or_equal` | PASS | 3 |
| stage_3 | `stage3_greater_or_equal` | PASS | 3 |
| stage_3 | `stage3_logical_and` | PASS | 3 |
| stage_3 | `stage3_logical_or` | PASS | 3 |
| stage_3 | `stage3_bitwise_and` | PASS | 3 |
| stage_3 | `stage3_bitwise_or` | PASS | 3 |
| stage_3 | `stage3_left_shift` | PASS | 3 |
| stage_3 | `stage3_right_shift` | PASS | 3 |
| stage_3 | `stage3_precedence_and_grouping` | PASS | 54 |
| stage_3 | `stage3_literals_booleans_and_whitespace` | PASS | 54 |
| stage_3 | `stage3_arithmetic_boundaries` | PASS | 57 |
| stage_3 | `stage3_invalid_literals_and_unsupported_operators` | PASS | 54 |
| stage_3 | `stage3_malformed_expressions_and_limits` | PASS | 54 |
| stage_3 | `stage3_numeric_declarations_assignment_and_no_hid` | PASS | 9 |
| stage_3 | `stage3_required_fixture_spiffs_and_sd` | PASS | 12 |
| stage_3 | `stage3_variable_references_types_and_atomic_failure` | PASS | 24 |
| stage_3 | `stage3_text_compatibility_alias_and_read` | PASS | 41 |
| stage_3 | `stage3_identifier_validation_and_table_exhaustion` | PASS | 91 |
| stage_3 | `stage3_preflight_zero_hid_and_runtime_errors` | PASS | 46 |
| stage_3 | `stage3_define_global_forward_and_word_matching` | PASS | 24 |
| stage_3 | `stage3_define_single_pass_and_declaration_exemption` | PASS | 32 |
| stage_3 | `stage3_define_comment_and_text_modes` | PASS | 24 |
| stage_3 | `stage3_define_duplicates_invalid_and_table_limits` | PASS | 76 |
| stage_3 | `stage3_define_expansion_and_pool_boundaries` | PASS | 32 |
| stage_3 | `stage3_expression_timing_counts_and_cancellation` | PASS | 17 |
| stage_3 | `stage3_collection_preflight_stop_and_state_isolation` | PASS | 27 |
| stage_3 | `stage3_interpolation_overflow_runtime_safe_stop` | PASS | 6 |
| stage_3 | `stage3_syntax_mode_does_not_evaluate_runtime_values` | PASS | 3 |
| stage_3 | `stage3_bounded_expression_fuzz` | PASS | 3001 |
| stage_3 | `stage3_expression_hot_path_no_heap` | PASS | 10022 |
| stage_4 | `stage4_simple_true_if` | PASS | 6 |
| stage_4 | `stage4_simple_false_if` | PASS | 6 |
| stage_4 | `stage4_if_else_true_path` | PASS | 6 |
| stage_4 | `stage4_if_else_false_path` | PASS | 6 |
| stage_4 | `stage4_nested_true_true` | PASS | 6 |
| stage_4 | `stage4_nested_true_false` | PASS | 6 |
| stage_4 | `stage4_outer_false_nested_inactive` | PASS | 6 |
| stage_4 | `stage4_multiple_nesting_levels` | PASS | 6 |
| stage_4 | `stage4_exact_nesting_limit` | PASS | 7 |
| stage_4 | `stage4_nesting_limit_plus_one` | PASS | 7 |
| stage_4 | `stage4_else_if_first_true` | PASS | 6 |
| stage_4 | `stage4_else_if_middle_true` | PASS | 6 |
| stage_4 | `stage4_else_if_final_else` | PASS | 6 |
| stage_4 | `stage4_else_if_multiple_entries` | PASS | 6 |
| stage_4 | `stage4_nested_else_if_chains` | PASS | 6 |
| stage_4 | `stage4_no_branch_true_without_else` | PASS | 6 |
| stage_4 | `stage4_selected_assignments_and_later_conditions` | PASS | 6 |
| stage_4 | `stage4_inactive_side_effects` | PASS | 9 |
| stage_4 | `stage4_required_fixture_spiffs_and_sd` | PASS | 12 |
| stage_4 | `stage4_define_conditions_and_protected_keywords` | PASS | 6 |
| stage_4 | `stage4_macro_manufactured_structures_rejected` | PASS | 56 |
| stage_4 | `stage4_compound_hex_boolean_conditions` | PASS | 6 |
| stage_4 | `stage4_malformed_expressions_zero_hid` | PASS | 77 |
| stage_4 | `stage4_undefined_and_text_variables` | PASS | 28 |
| stage_4 | `stage4_missing_end_if` | PASS | 7 |
| stage_4 | `stage4_unexpected_end_if` | PASS | 7 |
| stage_4 | `stage4_duplicate_else` | PASS | 7 |
| stage_4 | `stage4_else_outside_if` | PASS | 14 |
| stage_4 | `stage4_malformed_then_and_else_if` | PASS | 84 |
| stage_4 | `stage4_invalid_branch_ordering` | PASS | 21 |
| stage_4 | `stage4_rem_block_conditional_text` | PASS | 6 |
| stage_4 | `stage4_text_blocks_preserve_literal_modes` | PASS | 26 |
| stage_4 | `stage4_stop_active_and_inactive_branches` | PASS | 12 |
| stage_4 | `stage4_external_cancel_delay_text_and_keys` | PASS | 18 |
| stage_4 | `stage4_repeat_active_inactive_and_structural_history` | PASS | 18 |
| stage_4 | `stage4_clean_state_between_runs_and_live_ownership` | PASS | 9 |
| stage_4 | `stage4_runtime_errors_only_in_eligible_conditions` | PASS | 11 |
| stage_4 | `stage4_cooperative_large_inactive_region_and_preflight` | PASS | 18 |
| stage_4 | `stage4_legacy_compatibility_aliases` | PASS | 12 |
| stage_4 | `stage4_keyword_boundaries_whitespace_and_case` | PASS | 34 |
| stage_4 | `stage4_mixed_while_nesting` | PASS | 12 |
| stage_4 | `stage4_conditional_stack_no_heap` | PASS | 60012 |
| stage_5 | `stage5_false_while_following_commands` | PASS | 6 |
| stage_5 | `stage5_zero_iteration_expressions` | PASS | 36 |
| stage_5 | `stage5_single_iteration` | PASS | 7 |
| stage_5 | `stage5_multiple_iterations` | PASS | 7 |
| stage_5 | `stage5_decrementing_numeric_no_hid` | PASS | 9 |
| stage_5 | `stage5_shared_expression_operators` | PASS | 84 |
| stage_5 | `stage5_condition_reevaluated_at_header` | PASS | 8 |
| stage_5 | `stage5_nested_two_loops` | PASS | 8 |
| stage_5 | `stage5_nested_three_loops` | PASS | 7 |
| stage_5 | `stage5_sequential_loops` | PASS | 6 |
| stage_5 | `stage5_if_inside_while_else_if` | PASS | 6 |
| stage_5 | `stage5_while_inside_if_else` | PASS | 6 |
| stage_5 | `stage5_mixed_nested_structures` | PASS | 6 |
| stage_5 | `stage5_fixture_spiffs_and_sd` | PASS | 12 |
| stage_5 | `stage5_false_outer_suppresses_nested_conditions` | PASS | 6 |
| stage_5 | `stage5_inactive_side_effects_and_assignments` | PASS | 10 |
| stage_5 | `stage5_nested_updates_outer_variable` | PASS | 8 |
| stage_5 | `stage5_global_declarations_reused` | PASS | 7 |
| stage_5 | `stage5_exact_loop_depth` | PASS | 6 |
| stage_5 | `stage5_mixed_exact_depth` | PASS | 6 |
| stage_5 | `stage5_depth_plus_one_zero_hid` | PASS | 14 |
| stage_5 | `stage5_malformed_conditions_zero_hid` | PASS | 98 |
| stage_5 | `stage5_undefined_and_text_expression_rejection` | PASS | 28 |
| stage_5 | `stage5_missing_unmatched_and_crossed_terminators` | PASS | 42 |
| stage_5 | `stage5_keyword_boundaries_and_aliases` | PASS | 52 |
| stage_5 | `stage5_legacy_bare_text_truthiness` | PASS | 12 |
| stage_5 | `stage5_define_conditions_and_protected_keywords` | PASS | 6 |
| stage_5 | `stage5_macro_manufactured_loop_delimiters_rejected` | PASS | 28 |
| stage_5 | `stage5_define_collection_inside_inactive_loop` | PASS | 6 |
| stage_5 | `stage5_rem_block_loop_text_ignored` | PASS | 6 |
| stage_5 | `stage5_text_blocks_keep_literal_modes` | PASS | 12 |
| stage_5 | `stage5_bom_crlf_no_final_newline_backedges` | PASS | 6 |
| stage_5 | `stage5_header_across_read_budgets` | PASS | 6 |
| stage_5 | `stage5_reader_marker_and_seek_boundaries` | PASS | 12 |
| stage_5 | `stage5_runtime_seek_error` | PASS | 7 |
| stage_5 | `stage5_runtime_read_error_after_backedge` | PASS | 7 |
| stage_5 | `stage5_runtime_source_size_changed` | PASS | 7 |
| stage_5 | `stage5_runtime_condition_error_and_inactive_skip` | PASS | 12 |
| stage_5 | `stage5_runtime_undefined_path_dependent_variable` | PASS | 6 |
| stage_5 | `stage5_repeat_structural_and_inactive_history` | PASS | 6 |
| stage_5 | `stage5_repeat_expression_in_loop` | PASS | 6 |
| stage_5 | `stage5_keyboard_combinations_in_loop` | PASS | 7 |
| stage_5 | `stage5_expression_delays_in_loop` | PASS | 7 |
| stage_5 | `stage5_stop_in_active_and_inactive_loops` | PASS | 12 |
| stage_5 | `stage5_cancel_delay_inside_mixed_loop` | PASS | 6 |
| stage_5 | `stage5_cancel_text_inside_nested_loop` | PASS | 7 |
| stage_5 | `stage5_cancel_held_keys_and_usb_pressure` | PASS | 8 |
| stage_5 | `stage5_control_only_loop_cooperative_and_live_ownership` | PASS | 47 |
| stage_5 | `stage5_stalled_empty_loop_boundary` | PASS | 7 |
| stage_5 | `stage5_stalled_same_assignment_and_inactive_actions` | PASS | 7 |
| stage_5 | `stage5_nested_stall_not_masked_by_outer_progress` | PASS | 6 |
| stage_5 | `stage5_variable_progress_beyond_stall_threshold` | PASS | 8 |
| stage_5 | `stage5_total_iteration_limit_and_clean_restart` | PASS | 13 |
| stage_5 | `stage5_exact_total_iteration_boundary` | PASS | 9 |
| stage_5 | `stage5_variable_revision_atomic_and_reset` | PASS | 9 |
| stage_5 | `stage5_cancellation_then_new_source` | PASS | 11 |
| stage_5 | `stage5_large_inactive_region_cooperative` | PASS | 11 |
| stage_5 | `stage5_small_nested_loop_reference_cases` | PASS | 175 |
| stage_5 | `stage5_mixed_control_stack_no_heap` | PASS | 91039 |
| stage_6 | `stage6_declarations_skipped` | PASS | 6 |
| stage_6 | `stage6_statement_invocation` | PASS | 6 |
| stage_6 | `stage6_multiple_calls` | PASS | 6 |
| stage_6 | `stage6_forward_invocation_and_globals` | PASS | 6 |
| stage_6 | `stage6_fixture_spiffs_and_sd` | PASS | 12 |
| stage_6 | `stage6_explicit_void_return` | PASS | 6 |
| stage_6 | `stage6_implicit_void_return` | PASS | 6 |
| stage_6 | `stage6_integer_return_assignment` | PASS | 6 |
| stage_6 | `stage6_boolean_return_conditions` | PASS | 6 |
| stage_6 | `stage6_statement_discards_return_value` | PASS | 6 |
| stage_6 | `stage6_void_value_rejected` | PASS | 12 |
| stage_6 | `stage6_top_level_and_live_return_compatibility` | PASS | 11 |
| stage_6 | `stage6_enter_and_modifier_return_inside_function` | PASS | 7 |
| stage_6 | `stage6_return_unwinds_nested_control` | PASS | 6 |
| stage_6 | `stage6_caller_control_restored` | PASS | 6 |
| stage_6 | `stage6_nested_statement_calls` | PASS | 6 |
| stage_6 | `stage6_nested_return_expressions` | PASS | 6 |
| stage_6 | `stage6_multiple_calls_in_expression` | PASS | 6 |
| stage_6 | `stage6_earlier_variable_operand_preserved` | PASS | 6 |
| stage_6 | `stage6_eager_logical_calls` | PASS | 6 |
| stage_6 | `stage6_inactive_conditions_do_not_call` | PASS | 6 |
| stage_6 | `stage6_while_condition_calls_reevaluate` | PASS | 6 |
| stage_6 | `stage6_while_condition_changes_count_as_progress` | PASS | 6 |
| stage_6 | `stage6_else_if_function_condition` | PASS | 6 |
| stage_6 | `stage6_numeric_commands_with_calls` | PASS | 7 |
| stage_6 | `stage6_function_globals_text_and_file_commands` | PASS | 6 |
| stage_6 | `stage6_define_function_operands_and_names` | PASS | 6 |
| stage_6 | `stage6_macro_structural_creation_rejected` | PASS | 28 |
| stage_6 | `stage6_rem_and_text_modes` | PASS | 12 |
| stage_6 | `stage6_literal_text_does_not_invoke` | PASS | 6 |
| stage_6 | `stage6_names_case_sensitive` | PASS | 13 |
| stage_6 | `stage6_malformed_names_parameters_and_collisions` | PASS | 91 |
| stage_6 | `stage6_unknown_calls_zero_hid` | PASS | 21 |
| stage_6 | `stage6_invalid_call_arguments_and_whitespace` | PASS | 35 |
| stage_6 | `stage6_duplicate_and_nested_declarations` | PASS | 21 |
| stage_6 | `stage6_unterminated_and_unmatched_functions` | PASS | 28 |
| stage_6 | `stage6_return_syntax_and_context_errors` | PASS | 21 |
| stage_6 | `stage6_unused_body_preflight_errors_zero_hid` | PASS | 21 |
| stage_6 | `stage6_function_table_boundary` | PASS | 13 |
| stage_6 | `stage6_function_identifier_boundary` | PASS | 13 |
| stage_6 | `stage6_nested_call_depth_boundary` | PASS | 6 |
| stage_6 | `stage6_recursive_depth_exhaustion` | PASS | 6 |
| stage_6 | `stage6_recursive_expression_and_global_visibility` | PASS | 6 |
| stage_6 | `stage6_shared_control_depth_exhaustion` | PASS | 6 |
| stage_6 | `stage6_runtime_undefined_initialization` | PASS | 6 |
| stage_6 | `stage6_runtime_arithmetic_after_calls` | PASS | 12 |
| stage_6 | `stage6_repeat_history_around_calls` | PASS | 6 |
| stage_6 | `stage6_stop_active_and_inactive_function_branches` | PASS | 12 |
| stage_6 | `stage6_cancel_pending_function_delay` | PASS | 6 |
| stage_6 | `stage6_cancel_nested_function_text` | PASS | 7 |
| stage_6 | `stage6_cancel_held_keys_in_call` | PASS | 7 |
| stage_6 | `stage6_cancel_call_under_usb_backpressure` | PASS | 8 |
| stage_6 | `stage6_cancel_expression_then_clean_run` | PASS | 12 |
| stage_6 | `stage6_live_ownership_and_stop` | PASS | 7 |
| stage_6 | `stage6_seek_error_entering_function` | PASS | 5 |
| stage_6 | `stage6_seek_error_returning_to_caller` | PASS | 6 |
| stage_6 | `stage6_read_error_and_source_change_in_function` | PASS | 6 |
| stage_6 | `stage6_runtime_body_read_failure` | PASS | 7 |
| stage_6 | `stage6_bom_crlf_header_and_final_newline` | PASS | 6 |
| stage_6 | `stage6_empty_function_loop_stalls` | PASS | 6 |
| stage_6 | `stage6_total_call_budget` | PASS | 6 |
| stage_6 | `stage6_postfix_arithmetic_matches_existing_evaluator` | PASS | 39 |
| stage_6 | `stage6_expression_bounds_and_postfix_errors` | PASS | 11 |
| stage_6 | `stage6_long_declaration_skip_is_cooperative` | PASS | 11 |
| stage_6 | `stage6_postfix_call_state_no_heap` | PASS | 60012 |
| stage_7 | `stage7_empty_blocks` | PASS | 6 |
| stage_7 | `stage7_single_line_string` | PASS | 6 |
| stage_7 | `stage7_single_line_stringln` | PASS | 6 |
| stage_7 | `stage7_string_multiline_no_separators` | PASS | 6 |
| stage_7 | `stage7_stringln_multiline_enters` | PASS | 7 |
| stage_7 | `stage7_string_blank_lines` | PASS | 6 |
| stage_7 | `stage7_stringln_blank_lines` | PASS | 6 |
| stage_7 | `stage7_string_leading_and_trailing_whitespace` | PASS | 6 |
| stage_7 | `stage7_stringln_removes_one_leading_tab` | PASS | 6 |
| stage_7 | `stage7_internal_tabs_preserved` | PASS | 6 |
| stage_7 | `stage7_literal_command_keywords` | PASS | 6 |
| stage_7 | `stage7_terminator_prefixes_are_literal` | PASS | 6 |
| stage_7 | `stage7_case_and_indented_delimiters` | PASS | 6 |
| stage_7 | `stage7_inline_compatibility_unchanged` | PASS | 6 |
| stage_7 | `stage7_lf_and_crlf_equivalent` | PASS | 12 |
| stage_7 | `stage7_bom_only_at_source_start` | PASS | 6 |
| stage_7 | `stage7_no_final_newline` | PASS | 6 |
| stage_7 | `stage7_quoted_text_no_unescaping` | PASS | 6 |
| stage_7 | `stage7_numeric_boolean_and_text_interpolation` | PASS | 6 |
| stage_7 | `stage7_unknown_host_variables_are_literal` | PASS | 6 |
| stage_7 | `stage7_variable_replacement_is_single_pass` | PASS | 6 |
| stage_7 | `stage7_define_hash_and_word_replacement` | PASS | 6 |
| stage_7 | `stage7_define_body_not_collected_or_expanded` | PASS | 6 |
| stage_7 | `stage7_define_single_pass_and_variable_order` | PASS | 6 |
| stage_7 | `stage7_expansion_cannot_close_or_execute` | PASS | 6 |
| stage_7 | `stage7_value_whitespace_after_source_dedent` | PASS | 6 |
| stage_7 | `stage7_maximum_body_line` | PASS | 12 |
| stage_7 | `stage7_overlong_body_zero_hid` | PASS | 7 |
| stage_7 | `stage7_define_expansion_boundary` | PASS | 13 |
| stage_7 | `stage7_interpolation_boundary_and_overflow` | PASS | 12 |
| stage_7 | `stage7_inactive_interpolation_has_no_runtime_effect` | PASS | 6 |
| stage_7 | `stage7_unterminated_after_output_zero_hid` | PASS | 14 |
| stage_7 | `stage7_mismatched_or_argument_terminators_zero_hid` | PASS | 21 |
| stage_7 | `stage7_unmatched_terminators_zero_hid` | PASS | 14 |
| stage_7 | `stage7_literal_openers_inside_body` | PASS | 6 |
| stage_7 | `stage7_fixture_spiffs_and_sd` | PASS | 12 |
| stage_7 | `stage7_if_else_active_inactive_blocks` | PASS | 6 |
| stage_7 | `stage7_zero_iteration_loop_blocks` | PASS | 6 |
| stage_7 | `stage7_nested_loops_interpolate_current_values` | PASS | 6 |
| stage_7 | `stage7_function_repeat_calls_and_return` | PASS | 6 |
| stage_7 | `stage7_nested_functions_with_blocks` | PASS | 6 |
| stage_7 | `stage7_recursive_calls_with_blocks` | PASS | 6 |
| stage_7 | `stage7_repeat_literal_text_and_whitespace` | PASS | 6 |
| stage_7 | `stage7_repeat_blank_stringln` | PASS | 6 |
| stage_7 | `stage7_empty_string_does_not_replace_history` | PASS | 6 |
| stage_7 | `stage7_repeat_interpolates_again` | PASS | 6 |
| stage_7 | `stage7_default_delays_per_body_line` | PASS | 7 |
| stage_7 | `stage7_cancel_default_delay` | PASS | 7 |
| stage_7 | `stage7_cancel_halfway_through_typing` | PASS | 6 |
| stage_7 | `stage7_cancel_held_shift_and_usb_release_retry` | PASS | 7 |
| stage_7 | `stage7_usb_backpressure_lossless_and_no_readahead` | PASS | 8 |
| stage_7 | `stage7_stop_command_after_block` | PASS | 6 |
| stage_7 | `stage7_live_ownership_and_clean_run` | PASS | 14 |
| stage_7 | `stage7_live_block_opener_rejected` | PASS | 5 |
| stage_7 | `stage7_preflight_source_errors_zero_hid` | PASS | 6 |
| stage_7 | `stage7_rewind_seek_error_zero_hid` | PASS | 6 |
| stage_7 | `stage7_runtime_body_read_error_spiffs_and_sd` | PASS | 12 |
| stage_7 | `stage7_runtime_source_change` | PASS | 7 |
| stage_7 | `stage7_loop_backedge_seek_error` | PASS | 6 |
| stage_7 | `stage7_function_return_seek_error` | PASS | 7 |
| stage_7 | `stage7_large_block_streamed_and_cooperative` | PASS | 7 |
| stage_7 | `stage7_cancel_large_block_preflight` | PASS | 6 |
| stage_7 | `stage7_source_limits_zero_hid` | PASS | 13 |
| stage_7 | `stage7_hid_disabled_block_has_no_output` | PASS | 6 |
| stage_7 | `stage7_malformed_later_control_zero_hid` | PASS | 7 |
| stage_7 | `stage7_control_nesting_boundaries` | PASS | 26 |
| stage_7 | `stage7_text_blocks_do_not_execute_calls` | PASS | 6 |
| stage_7 | `stage7_bounded_line_allocation_probe` | PASS | 40005 |
| stage_8 | `stage8_f1_f24_reference` | PASS | 346 |
| stage_8 | `stage8_invalid_f_names` | PASS | 12 |
| stage_8 | `stage8_navigation_editing_aliases` | PASS | 330 |
| stage_8 | `stage8_named_punctuation_keys` | PASS | 176 |
| stage_8 | `stage8_keypad_reference` | PASS | 144 |
| stage_8 | `stage8_all_modifier_masks` | PASS | 3072 |
| stage_8 | `stage8_modifier_aliases` | PASS | 110 |
| stage_8 | `stage8_hyphen_combinations` | PASS | 34 |
| stage_8 | `stage8_malformed_hyphens_zero_hid` | PASS | 24 |
| stage_8 | `stage8_case_tabs_and_order` | PASS | 12 |
| stage_8 | `stage8_modifier_only_release` | PASS | 23 |
| stage_8 | `stage8_six_key_limit_and_duplicates` | PASS | 15 |
| stage_8 | `stage8_literal_punctuation_chord_us` | PASS | 15 |
| stage_8 | `stage8_literal_punctuation_chord_de` | PASS | 27 |
| stage_8 | `stage8_all_literal_punctuation_chords` | PASS | 797 |
| stage_8 | `stage8_report_filter_and_raw_modifiers` | PASS | 99 |
| stage_8 | `stage8_keycode_bounds_zero_hid` | PASS | 12 |
| stage_8 | `stage8_us_ascii_table` | PASS | 129 |
| stage_8 | `stage8_de_ascii_table` | PASS | 129 |
| stage_8 | `stage8_us_ascii_translation` | PASS | 358 |
| stage_8 | `stage8_de_ascii_translation` | PASS | 360 |
| stage_8 | `stage8_printable_ascii_runtime_all_locales` | PASS | 1934 |
| stage_8 | `stage8_de_utf8_reference` | PASS | 89 |
| stage_8 | `stage8_de_dead_keys` | PASS | 70 |
| stage_8 | `stage8_locale_registration_and_switching` | PASS | 28 |
| stage_8 | `stage8_named_keys_are_physical_not_locale_text` | PASS | 17 |
| stage_8 | `stage8_unsupported_unicode_skip_warning` | PASS | 14 |
| stage_8 | `stage8_utf8_bounds_and_invalid_sequences` | PASS | 16 |
| stage_8 | `stage8_no_warn_supported_controls` | PASS | 6 |
| stage_8 | `stage8_repeat_define_and_stringln_reports` | PASS | 63 |
| stage_8 | `stage8_multiline_control_function_keyboard` | PASS | 36 |
| stage_8 | `stage8_queue_refusal_press_and_release` | PASS | 16 |
| stage_8 | `stage8_disconnect_mid_chord_recovery` | PASS | 15 |
| stage_8 | `stage8_cancel_held_modifier_all_masks` | PASS | 3060 |
| stage_8 | `stage8_cancel_release_priority_new_live_command` | PASS | 14 |
| stage_8 | `stage8_stop_and_runtime_error_release` | PASS | 15 |
| stage_8 | `stage8_cancel_between_dead_key_strokes` | PASS | 12 |
| stage_8 | `stage8_storage_fault_after_chord_release` | PASS | 10 |
| stage_8 | `stage8_hid_disabled_and_live_ownership` | PASS | 15 |
| stage_8 | `stage8_new_run_no_modifier_leak` | PASS | 11 |
| stage_8 | `stage8_translation_report_allocation_probe` | PASS | 32001 |

## Remaining limitations and required physical validation

- Missing/wrong-sized images now fail instead of creating unchecked zero media or silently exposing a prefix. This intentional safety compatibility change was documented before implementation. No valid existing image is altered by startup. Provisioning remains separately reviewed user work.
- Active means locally validated raw block media, not a verified filesystem or host-visible re-enumerated device. A zero image remains non-mountable even if raw activation succeeds. No USB descriptor/detach/identity changes are implemented.
- Cooperative phases remove the 8,192-write preparation loop; an individual SD open/seek/read/flush or SDK call cannot be preempted. Deadlines are checked between phases, not hard driver timeouts. Real callback latency and USB busy retry behavior require hardware/host testing.
- SD cardType is cached. Physical removal may only be detected by subsequent I/O failure. Same-size external image mutation is not detected; do not edit the active backing image. Physical remount may be needed.
- Short writes can leave an in-range prefix changed. Void flush/close APIs cannot establish durable completion. No transactional or atomic-sector guarantee is made.
- Actual production MSC/attackmode/SD adapter/CLI/scheduler/parser/HID sources are fault tested; SDK, clock and filesystem endpoints are RAM mocks. Script storage adapters remain mocked. Real AsyncWebServer HTTP requests and complete storage.cpp adapter integration are not covered end-to-end. Web upload locking is source-reviewed and firmware-compiled.
- Stable callbacks avoid SDK callback-pointer clearing races. Library-internal concurrency, host eject/load semantics, disconnect/reconnect, macOS High Sierra mounting and physical SD behavior remain unverified. ASan/UBSan do not substitute for ThreadSanitizer or device tests.

## Modified and created files

- `EvilDuckS3/attackmode.cpp`
- `EvilDuckS3/attackmode.h`
- `EvilDuckS3/cli.cpp`
- `EvilDuckS3/com.cpp`
- `EvilDuckS3/execution_guard.h`
- `EvilDuckS3/sd_card.cpp`
- `EvilDuckS3/usb_msc.cpp`
- `EvilDuckS3/usb_msc.h`
- `EvilDuckS3/webserver.cpp`
- `docs/stage10-baseline-storage-stack.json`
- `docs/stage10-build.log`
- `docs/stage10-design.md`
- `docs/stage10-report.md`
- `docs/stage10-results.json`
- `docs/stage10-stack-results.json`
- `tests/stage1/mocks/host.cpp`
- `tests/stage10/README.md`
- `tests/stage10/mocks/FS.h`
- `tests/stage10/mocks/SD.h`
- `tests/stage10/mocks/SPI.h`
- `tests/stage10/mocks/USBMSC.h`
- `tests/stage10/run_tests.py`
- `tests/stage10/test_main.cpp`
- `tests/stage10/unavailable.cpp`
- `tests/stage9/attackmode_probe.cpp`
- `tests/stage9/run_tests.py`
- `tools/analyze_s3_stack.py`

## Next reviewed milestone

Recommend Stage 11 persistent HID key ownership and reliable HOLD/RELEASE behavior, with separately researched INJECT_MOD semantics, cancellation/error release and exact mocked reports. Do not combine this with physical storage validation or silently expand ATTACKMODE. Stage 11 has not started.

No physical hardware was accessed, no real HID emitted, and no physical erase/flash/format/write/OTA operation was executed. Tests write only mock RAM media and local build/report files. Main, earlier branches, Arduino Micro, parser semantics, partitions and migration safeguards are preserved. Physical validation remains separately authorized; stop here for review.
