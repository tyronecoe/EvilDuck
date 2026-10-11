# Stage 5 implementation and verification report

Stage 5 implements canonical WHILE with nested/mixed IF control flow on the
approved Stage 4 commit `c3e9c34f887015a6c8bcc3146835ebac54432b58`. Work is isolated
on `stage5-duckyscript-while`, branched directly from Stage 4 in a separate clone.
GitHub authentication and repository push permissions were verified. Main and
`stage4-duckyscript-migration` are preserved. The Stage 4 migration ZIP remains
3,002,964 bytes with SHA-256
`208e6afda9a73bf2b3f9e1bd96795530c02a7c59770099bf3e3090c9d32d1083`.

No physical hardware was accessed. No HID was sent to the development host.
No flash, OTA, erase, formatting or other destructive hardware command was
executed. Stage 6 was not started. No physical migration is implied by this build.

## Implemented behavior

* `WHILE condition` ... `END_WHILE` evaluates before entering and reevaluates the
  opening condition after every iteration, using only the existing Stage 3 engine.
* False and zero-iteration loops correctly resume after their terminator, fixing
  `known_false_while` without preserving its old stuck skip-state defect.
* Nested WHILE, WHILE inside IF/ELSE IF/ELSE, and IF chains inside WHILE use one
  typed fixed stack; maximum **combined nesting is eight**. Depth nine, crossed
  terminators, missing terminators and malformed conditions reject during
  preflight before any HID output. Runtime stack methods also check bounds/type.
* Inactive bodies produce no ordinary runtime side effects and do not evaluate
  nested runtime conditions. Their structural nesting is still tracked.
* Variable changes remain global and use existing 16-bit semantics. DEFINE
  operands expand deterministically; constants cannot manufacture structural loop
  delimiters. Existing text interpolation is unchanged.
* Header byte markers survive partial reads, budgets, BOM, CRLF and missing final
  newline. Loops stream both SPIFFS and SD; no whole-script cache or AST is added.
  Seek/read/size failures remain distinct from EOF and safely stop execution.
* Source work retains per-update byte/line budgets. Control-only and inactive
  loops yield. Timers, text, USB-pressure release retries, STOP and live-command
  ownership use Stage 1 cooperative scheduling; no blocking delay was added.
* Structural/inactive loop lines do not replace repeat history. REPEAT/REPLAY
  continue replaying the last actually executed repeatable keyboard command;
  expression arguments and existing delays/default delay/modifier reports remain.
* Two configurable bounds stop unsafe execution: 100,000 total active WHILE body
  entries per script and 1,024 consecutive iterations in one loop without an
  actual variable change or dispatched ordinary action. Both boundaries and a
  fresh run after guard errors were executed under sanitizers.

The complete architecture, safety policy and references are in
[stage5-design.md](stage5-design.md). The official Hak5 loops reference establishes
header reevaluation and `WHILE TRUE`; no physical Hak5 reference oracle was used.

## Compatibility decisions and limitations

`ENDWHILE`, `END WHILE`, case-insensitive keywords and bare text-variable WHILE
truthiness are preserved EvilDuck extensions. Numeric compound conditions use
Stage 3 expressions. No THEN, string-comparison WHILE, BREAK, CONTINUE, FOR,
functions or new REPEAT block semantics are introduced. Text runtime blocks stay
deferred to Stage 7. Expressions keep existing precedence, eager logical behavior,
16-bit wrap and error decisions; expression/HID/locale semantics were not changed.

Hak5 permits infinite loops; the new finite iteration/stalled bounds are explicit
EvilDuck safety differences. A value-changing or action-producing infinite loop
can evade the stalled heuristic but cannot evade the total body-entry bound.
Same-value assignments do not count as progress. Zero-delay/replay commands do
count as dispatched actions even if they produce no visible effect. This is a
heuristic, not a proof of useful progress. Pending USB/delay commands remain
cancellable; the guards do not add timeouts to those operations. Constants are
still global preprocessing, including declarations in inactive branches.

Preflight still does not simulate path-dependent variable values. Runtime-only
undefined/divide-by-zero conditions fail at their source header. After a condition
becomes false, the body is streamed inactive to the matching end rather than
jumped using a cached block index; this bounds RAM and per-update work at the cost
of additional storage reads. Same-size concurrent source modifications are not
fully authenticated: Reader detects size/position/read failures and reentry checks
header kind/location, but it does not checksum every source byte. Editing a
running script is unsupported. No caching/file-lock architecture is introduced.

The old Stage 2 structural fixtures used undefined variables whose new validation
masked their intended mismatch/unterminated diagnostics; they now use WHILE FALSE.
Its runtime seek-fault fixture now targets the opening header. Stage 4's formerly
deferred mixed-control test is replaced by two terminating positive fixtures and
renamed `stage4_mixed_while_nesting`. These are intentional Stage 5 test updates.
All other prior passing behaviors remain tested.

During development, initial tests exposed those three obsolete Stage 2 fixture
assumptions, a nonexistent test submission API, and new fixture mistakes reading
variables after EOF or expecting Ctrl/Alt chords to generate printable mock text.
Fixtures were corrected to inspect variables while alive and verify chord reports.
Stage 1 cleanup and HID semantics were preserved. The final executed results
below have no unexpected failures; unresolved bugs remain separately labeled.

## Clean target compilation and resources

Arduino ESP32 core **3.3.0**, ESP32S3 Dev Module, custom repository partitions,
QIO 80 MHz, CPU 240 MHz, TinyUSB/USB-OTG with CDC enabled, MSC/DFU boot disabled,
**PSRAM disabled**. Exact tested FQBN:

```
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

`tools/build_s3.py` invoked `arduino-cli compile --clean`, with a fresh output
folder and two jobs. Independent image/partition/slot-size validation succeeded.
Bootloader and application headers target ESP32-S3 (chip id 9), 16 MiB, 80 MHz.
Arduino's QIO boot profile intentionally has a DIO image-header field; this
matches the pinned SDK and unchanged validation policy. No downgrade or Arduino
IDE menu substitution was used. Library environment remains NeoPixel 1.15.5,
AsyncTCP 3.5.0, ESPAsyncWebServer 3.12.1 and core-bundled SD 3.3.0.

| Measurement | Stage 4 | Stage 5 | Growth |
|---|---:|---:|---:|
| Compiler program usage | 1,297,079 | 1,298,255 | 1,176 bytes |
| Actual application BIN | 1,297,232 | 1,298,400 | 1,168 bytes |
| Static RAM | 69,912 | 70,072 | 160 bytes |

Both `0x740000` OTA slots hold 7,602,176 bytes each, leaving **6,303,776 bytes
(82.92068%) free per slot** for the new application. Compiler RAM budget is
327,680 bytes, leaving 257,608 bytes for local variables/heap; this is a linker
measurement, not actual runtime free heap. The unified stack is 196 bytes (eight
24-byte frames plus depth/padding), compared with the old 33-byte IF-only stack;
it replaces the old single-loop String/markers too. Reader markers add eight
bytes and global variable revision adds four bytes. No recursive execution is
used; existing expression recursion stays bounded at depth 16 and 128 tokens.

The mixed-stack/expression probe observed **zero C++ heap allocations** during
10,000 mixed chains. This does not characterize the entire interpreter's heap:
existing Arduino String parsing, command storage and legacy whole-file READ can
allocate. Physical peak heap/fragmentation and stack high-water marks remain
unmeasured. Firmware BIN SHA-256:

```
9a67de9106652ef54944243731cf449e4befb48af2f7707d77d4eca83c0d1e91
```

The offline build report's `hardware_verified=false` is a conservative guard:
this build itself did not interrogate any device. It does not contradict the
user's supplied 16 MiB real-device verification. The approved partition CSV,
NVS/SPIFFS/OTA/coredump layout, build wrapper and migration safeguards have **no
Stage 5 changes**. Arduino Micro files likewise have no changes. The Arduino core
may generate a padded merged image in its build directory; it was never used for
migration or uploaded. Stage 4 migration artifacts remain separately reviewed.

## Executed regression summary

| Suite | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| Stage 1 | 5 | 0 | 127 |
| Stage 2 | 30 | 0 | 797 |
| Stage 2.5 | 30 | 0 | 190 |
| Stage 3 | 40 | 0 | 13,815 |
| Stage 4 | 42 | 0 | 60,628 |
| Stage 5 | 59 | 0 | 92,021 |
| Diagnostic sanity checks | separate | 0 | 12 |
| **Total** | **206** | **0** | **167,590** |

Stage 5 includes 58 integration cases and one allocation probe. Stage 3/4
allocation probes are also included in their respective PASS counts. Three
**XPASS** language diagnostics are listed separately from ordinary PASS counts;
two **XFAIL** diagnostics are unresolved, not passing support claims.

All C++ suites and probes executed with ASan/UBSan and completed cleanly. No
sanitizer error or leak report occurred. Python partition/migration and mkspiffs
validation tests executed offline and are not ASan/UBSan-instrumented. Exact
machine-readable results and assertions are in [stage5-results.json](stage5-results.json).
The Stage 4 suite now has two fewer assertions than its old deferred-block test,
so the old 75,571 total becomes 75,569 before adding Stage 5's 92,021 assertions.

| Language diagnostic | Status | Actual result |
|---|---|---|
| `known_nested_if` | XPASS | expected 'good', actual 'good' |
| `known_canonical_if` | XPASS | expected 'good', actual 'good' |
| `known_false_while` | XPASS | expected 'good', actual 'good' |
| `known_f13_mapping` | XFAIL | expected usage 104, actual 70 |
| `known_german_ascii_table` | XFAIL | expected 128 records, actual 115; table content/alignment needs a later-stage fix |

The false-WHILE defect was legitimately fixed in Stage 5. F13 still maps to usage
70 instead of 104. The German ASCII table still has 115 records instead of 128,
with alignment/content unresolved. No Stage 8 HID/locale work was pulled forward.

## Remaining physical validation and Stage 6 recommendation

Later, separately authorized hardware tests should verify real SD back-edge seek,
card removal/error handling, USB scheduling and cancellation/release under host
backpressure, HTTP responsiveness during long inactive/control-only scripts,
heap/stack high-water marks and sustained runs. Use harmless visible fixtures.
Build success and mocks do not verify physical flash migration, OTA recovery or
complete Hak5 runtime equivalence.

Stage 6 should first confirm official function declaration/call/return syntax,
then design bounded call frames and return locations that coexist with this typed
control stack and the single expression evaluator. Preserve global variables,
preflight-before-HID, streaming source and cancellation; add recursion/call-depth
and execution limits with tests before implementing function semantics. This is a
recommendation only: no function implementation or Stage 6 work has begun.

## Every Stage 5 changed/created file

* `EvilDuckS3/config.h`
* `EvilDuckS3/control_flow.h (new)`
* `EvilDuckS3/duck_vars.cpp`
* `EvilDuckS3/duck_vars.h`
* `EvilDuckS3/duckscript.cpp`
* `EvilDuckS3/script_parser.cpp`
* `EvilDuckS3/script_source.cpp`
* `EvilDuckS3/script_source.h`
* `tests/stage1/mocks/FS.h`
* `tests/stage1/mocks/host.cpp`
* `tests/stage2/test_main.cpp`
* `tests/stage4/run_tests.py`
* `tests/stage4/test_main.cpp`
* `tests/stage5/test_main.cpp (new)`
* `tests/stage5/no_alloc.cpp (new)`
* `tests/stage5/run_tests.py (new)`
* `tests/stage5/README.md (new)`
* `docs/stage5-design.md (new)`
* `docs/stage5-results.json (new)`
* `docs/stage5-report.md (new)`

Firmware files implement bounded control/state/reader changes; mocks add source
size/read/seek observations; existing tests adjust the intentional Stage 5
supersession; new tests/docs report and verify the implementation. No dependencies,
partition table, migration tooling, Arduino Micro files or HID mappings changed.
The GitHub commit diff against the Stage 4 parent is the reviewable Stage 5-only
patch; the separate branch is `stage5-duckyscript-while`.

## Exact executed test names and assertion counts

### Stage 1

| Executed test | Result | Assertions |
|---|---|---:|
| `supported_commands_and_mock_interfaces` | PASS | 29 |
| `script_run_state_isolation` | PASS | 22 |
| `cooperative_delay_and_text_cancellation` | PASS | 33 |
| `repeat_timing_and_control_loop_yield` | PASS | 24 |
| `live_commands_cannot_mutate_running_script` | PASS | 19 |

### Stage 2

| Executed test | Result | Assertions |
|---|---|---:|
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

### Stage 2.5

| Executed test | Result | Assertions |
|---|---|---:|
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

### Stage 3

| Executed test | Result | Assertions |
|---|---|---:|
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

### Stage 4

| Executed test | Result | Assertions |
|---|---|---:|
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
| `stage4_mixed_while_nesting` | PASS | 12 |
| `stage4_conditional_stack_no_heap` | PASS | 60012 |

### Stage 5

| Executed test | Result | Assertions |
|---|---|---:|
| `stage5_false_while_following_commands` | PASS | 6 |
| `stage5_zero_iteration_expressions` | PASS | 36 |
| `stage5_single_iteration` | PASS | 7 |
| `stage5_multiple_iterations` | PASS | 7 |
| `stage5_decrementing_numeric_no_hid` | PASS | 9 |
| `stage5_shared_expression_operators` | PASS | 84 |
| `stage5_condition_reevaluated_at_header` | PASS | 8 |
| `stage5_nested_two_loops` | PASS | 8 |
| `stage5_nested_three_loops` | PASS | 7 |
| `stage5_sequential_loops` | PASS | 6 |
| `stage5_if_inside_while_else_if` | PASS | 6 |
| `stage5_while_inside_if_else` | PASS | 6 |
| `stage5_mixed_nested_structures` | PASS | 6 |
| `stage5_fixture_spiffs_and_sd` | PASS | 12 |
| `stage5_false_outer_suppresses_nested_conditions` | PASS | 6 |
| `stage5_inactive_side_effects_and_assignments` | PASS | 10 |
| `stage5_nested_updates_outer_variable` | PASS | 8 |
| `stage5_global_declarations_reused` | PASS | 7 |
| `stage5_exact_loop_depth` | PASS | 6 |
| `stage5_mixed_exact_depth` | PASS | 6 |
| `stage5_depth_plus_one_zero_hid` | PASS | 14 |
| `stage5_malformed_conditions_zero_hid` | PASS | 98 |
| `stage5_undefined_and_text_expression_rejection` | PASS | 28 |
| `stage5_missing_unmatched_and_crossed_terminators` | PASS | 42 |
| `stage5_keyword_boundaries_and_aliases` | PASS | 52 |
| `stage5_legacy_bare_text_truthiness` | PASS | 12 |
| `stage5_define_conditions_and_protected_keywords` | PASS | 6 |
| `stage5_macro_manufactured_loop_delimiters_rejected` | PASS | 28 |
| `stage5_define_collection_inside_inactive_loop` | PASS | 6 |
| `stage5_rem_block_loop_text_ignored` | PASS | 6 |
| `stage5_text_blocks_keep_literal_modes` | PASS | 14 |
| `stage5_bom_crlf_no_final_newline_backedges` | PASS | 6 |
| `stage5_header_across_read_budgets` | PASS | 6 |
| `stage5_reader_marker_and_seek_boundaries` | PASS | 12 |
| `stage5_runtime_seek_error` | PASS | 7 |
| `stage5_runtime_read_error_after_backedge` | PASS | 7 |
| `stage5_runtime_source_size_changed` | PASS | 7 |
| `stage5_runtime_condition_error_and_inactive_skip` | PASS | 12 |
| `stage5_runtime_undefined_path_dependent_variable` | PASS | 6 |
| `stage5_repeat_structural_and_inactive_history` | PASS | 6 |
| `stage5_repeat_expression_in_loop` | PASS | 6 |
| `stage5_keyboard_combinations_in_loop` | PASS | 7 |
| `stage5_expression_delays_in_loop` | PASS | 7 |
| `stage5_stop_in_active_and_inactive_loops` | PASS | 12 |
| `stage5_cancel_delay_inside_mixed_loop` | PASS | 6 |
| `stage5_cancel_text_inside_nested_loop` | PASS | 7 |
| `stage5_cancel_held_keys_and_usb_pressure` | PASS | 8 |
| `stage5_control_only_loop_cooperative_and_live_ownership` | PASS | 47 |
| `stage5_stalled_empty_loop_boundary` | PASS | 7 |
| `stage5_stalled_same_assignment_and_inactive_actions` | PASS | 7 |
| `stage5_nested_stall_not_masked_by_outer_progress` | PASS | 6 |
| `stage5_variable_progress_beyond_stall_threshold` | PASS | 8 |
| `stage5_total_iteration_limit_and_clean_restart` | PASS | 13 |
| `stage5_exact_total_iteration_boundary` | PASS | 9 |
| `stage5_variable_revision_atomic_and_reset` | PASS | 9 |
| `stage5_cancellation_then_new_source` | PASS | 11 |
| `stage5_large_inactive_region_cooperative` | PASS | 11 |
| `stage5_small_nested_loop_reference_cases` | PASS | 175 |
| `stage5_mixed_control_stack_no_heap` | PASS | 91039 |
