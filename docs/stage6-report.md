# Stage 6 functions: implementation and verification report

Stage 6 is isolated on `stage6-duckyscript-functions`, based directly on approved
Stage 5 `1222fc6fb9307dd9680493b189b595cdd0c91b2f`. Authentication and push
permission were verified. Main, Stage 4, Stage 5, Arduino Micro, partition tables,
build profile and migration safeguards are unchanged. No physical hardware was
accessed, no real HID output was sent, and no destructive hardware operation was
executed. Stage 7 was not started. This compilation does not migrate a device.

## Reference and supported syntax

The official [Hak5 function reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/operators-conditions-loops-and-functions/functions.md)
was reviewed with Stage 1–5 contracts, reports, tests and migration documentation.
It documents `FUNCTION NAME()` / `END_FUNCTION`, named invocation `NAME()`, global
variables rather than positional parameters, and `RETURN` integer/Boolean values
usable in conditions. No Hak5 reference runtime was executed; this is not a claim
of complete or independently proven DuckyScript 3.0 compatibility.

Implemented forms:

```text
FUNCTION next()
    $n = ($n + 1)
    RETURN $n
END_FUNCTION
VAR $n = 0
VAR $result = next()
IF next() == 2 THEN
    STRINGLN functions-ok
END_IF
```

Declarations never execute sequentially. Functions can be invoked repeatedly,
forward-referenced, nested and recursively called within limits. A bare RETURN
or reaching END_FUNCTION returns void. Integer/Boolean return expressions retain
Stage 3 uint16 arithmetic, wraparound, TRUE=1/FALSE=0, precedence, eager logical
operators and diagnostics. Consuming void as a value is a runtime error.

Calls work in numeric VAR/assignment expressions, IF/ELSE IF/WHILE conditions,
RETURN expressions, DELAY/WAIT, DEFAULT_DELAY/DEFAULTDELAY and REPEAT/REPLAY
arguments. They are not evaluated in STRING/file payloads. All existing globals,
text-variable compatibility, DEFINE, cooperative keyboard operations, locale/LED,
file commands and web/CLI ownership behavior remain available.

## Bounded architecture and execution

The existing Stage 3 precedence parser optionally emits fixed postfix bytecode;
it retains the same grammar, operator implementation and syntax checker. There
is no second condition parser, dynamic AST, external engine or new dependency.
Evaluation suspends at a function operand and resumes once with its returned
value. Earlier operands retain their values across later function side effects;
functions are neither replayed nor evaluated twice. At most 16 instructions run
per update. A standalone call, return or declaration skip also yields.

Source remains streamed through the existing bounded SPIFFS/SD reader. Preflight
now has three bounded passes before execution: DEFINE collection, function/global
type inventory, and complete structural/expression validation. Inventory retains
only names, body/end byte offsets and line numbers. Every body is validated,
including unused bodies. Malformed declarations, unknown calls, invalid RETURN,
crossed IF/WHILE boundaries, missing terminators and known expression errors fail
before HID. Forward global type metadata validates a body without pretending its
variables have been initialized; path-dependent initialization errors remain
runtime diagnostics. Changing a source during execution is unsupported: size,
read and seek errors are caught, but same-size edits are not fully authenticated.

Each fixed call frame saves suspended evaluation, logical source return position,
function index and caller control-stack boundaries. Call entry isolates the
callee's active root even while evaluating an eligible ELSE IF whose caller
branch is inactive. Callees cannot pop caller IF/WHILE frames. RETURN discards
callee frames and restores the exact caller boundary/position. Recursive script
execution is not used. WHILE conditions containing functions capture progress
before condition evaluation, so global changes made by that condition count as
progress. Empty calls alone do not defeat the existing stalled-loop guard.

STOP/cancellation clears calls, evaluation, registry, loop state, pending timers,
text and keys through existing Stage 1 ownership/release behavior. Runtime errors
stop safely and include filename, source line and the current function/callsite.
The call/return seek paths are checked. RunState is reconstructed directly in
place to avoid a large aggregate temporary on the embedded main-loop task stack.

## Limits and memory

* 16 functions; 32-byte identifiers; 8 live calls; 100,000 total calls per run.
* Shared active IF/WHILE nesting remains 8 across callers and callees.
* Existing expression limits remain 256 bytes, 128 tokens and depth 16.
* Host sizeof measurements: postfix program 906 bytes; pending evaluation 960;
  call frame 976; fixed 8-frame call stack 7,812; function table 836; control stack
  196. These are host measurements, not a hardware stack high-water claim.
* The isolated postfix/call probe performed 10,000 suspend/resume cycles and
  observed zero C++ heap allocations. String-based statement parsing/logging and
  source handling still use bounded strings; this is not a zero-allocation claim
  for the whole firmware. Device heap fragmentation and task-stack margins remain
  unmeasured. No full script or function body is held in RAM.

## Compatibility decisions and uncertainties

Zero-argument literal adjacent `()` is required. No parameter syntax, CALL,
ENDFUNCTION or END FUNCTION aliases are invented. Function names are case-sensitive
and definitions must be top level. Duplicate/reserved command/key/modifier names
are rejected, including single-letter key names. Forward calls are supported.
These compiler policy choices are not independently matched to every Hak5 edge.

No local scope exists: callers/callees share global numeric and compatibility text
variables. Bare top-level/live RETURN remains the EvilDuck Enter alias; inside a
function it now returns void. Use ENTER to type Enter inside a function; CTRL
RETURN remains a key combination. RETURN with a value outside a function rejects.
The two Stage 2 fixtures formerly rejecting all FUNCTION/RETURN syntax now check
unterminated FUNCTION and out-of-function value RETURN diagnostics instead. Their
assertion counts are unchanged; historical diagnostic expectations are untouched.

Void consumed in an expression errors instead of inventing an undocumented return
value. Recursion, forward-reference policy, eager left-to-right side effects and
strict name collisions are explicit safe EvilDuck decisions where the reference
is incomplete. DEFINE may expand expression operands, including calls, but cannot
manufacture declaration/RETURN delimiters or standalone invocation lines; literal
function names on declarations/invocations are protected. Existing macro safety
and text-block modes remain intact. REPEAT repeats the prior runtime command,
not a function/control delimiter; after returning, the history reflects commands
actually executed by the callee.

## Executed verification

All tests used mocked HID, storage, clocks and supporting interfaces. Each C++
suite and allocation probe was built with ASan/UBSan; all exited successfully with
no sanitizer diagnostics. The Python partition/migration suite is not sanitizer
instrumented. Results below are from this execution, not inherited claims.

| Suite | PASS | FAIL | Assertions |
| --- | ---: | ---: | ---: |
| stage 1 | 5 | 0 | 127 |
| stage 2 | 30 | 0 | 797 |
| stage 2 5 | 30 | 0 | 190 |
| stage 3 | 40 | 0 | 13,815 |
| stage 4 | 42 | 0 | 60,628 |
| stage 5 | 59 | 0 | 92,021 |
| stage 6 | 65 | 0 | 60,727 |
| Diagnostic sanity checks | — | — | 12 |
| Total | 271 | 0 | 228,317 |

There are additionally **3 XPASS and 2 XFAIL** diagnostic outcomes:

| Name | Result | Investigated actual behavior |
| --- | --- | --- |
| known_nested_if | XPASS | expected/actual `good`; legitimately fixed by Stage 4 |
| known_canonical_if | XPASS | expected/actual `good`; legitimately fixed by Stage 4 |
| known_false_while | XPASS | expected/actual `good`; legitimately fixed by Stage 5 |
| known_f13_mapping | XFAIL | expected usage 104, actual 70; F13 incorrectly continues contiguous F1–F12 mapping |
| known_german_ascii_table | XFAIL | expected 128 records, actual 115; German ASCII table content/alignment remains incorrect |

These historical labels remain visible and were not changed to improve the
report. Neither remaining HID/locale defect is within Stage 6 scope. Exact test
names, individual assertion totals, build measurements and SHA-256s of execution
logs are recorded in `stage6-results.json`; a full exact-name table follows.

## Clean ESP32-S3 build

Pinned Arduino ESP32 core **3.3.0**. Repository custom partition CSV and PSRAM
disabled. FQBN:

```text
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

Clean build output and headers passed offline validation: ESP32-S3, 16 MiB flash,
80 MHz; QIO build configuration uses the expected SDK DIO image-header encoding.
Both 0x740000 OTA slots, standard app0 address, NVS, SPIFFS and coredump offsets
remain unchanged. No upload or OTA operation was executed.

| Measurement | Stage 5 | Stage 6 | Growth |
| --- | ---: | ---: | ---: |
| Compiler program bytes | 1,298,255 | 1,307,503 | 9,248 |
| Actual application .bin bytes | 1,298,400 | 1,307,648 | 9,248 |
| Static RAM bytes | 70,072 | 80,408 | 10,336 |

Each OTA slot is 7,602,176 bytes: **6,294,528 bytes free (82.7990%)**, 17.2010%
occupied. Compiler static RAM ceiling is 327,680 bytes; nominal remaining static
capacity 247,272 bytes is not a measured runtime free heap value. Application
SHA-256: `858b0d4dfbe6c305934aa56ce9e436134116a772be53b86d08f58246037462ab`.
Build tooling's `hardware_verified=false` means it performed no interrogation;
it does not invalidate the user's previous real-device evidence.

Reproduce offline from this branch:

```sh
python3 tests/stage1/run_tests.py
python3 tests/stage3/run_tests.py
python3 tests/stage4/run_tests.py
python3 tests/stage5/run_tests.py
python3 tests/stage6/run_tests.py
python3 tools/build_s3.py --build-dir /tmp/evilduck-stage6-clean --jobs 2
python3 tests/stage25/run_tests.py --core-dir /path/to/esp32/3.3.0 --build-dir /tmp/evilduck-stage6-clean
```

Stage 1's runner includes Stage 2 and the five historical diagnostics. Build output
directory must be empty. Use the pinned core; optional --arduino-cli/--config-file
arguments select the configured installation. No hardware commands are required.

## Changed and created files

Modified: `EvilDuckS3/com.cpp`, `config.h`, `control_flow.h`, `duck_expr.cpp`,
`duck_expr.h`, `duckscript.cpp`, `script_parser.cpp`, `script_parser.h`;
`tests/stage1/run_tests.py`, `tests/stage2/test_main.cpp`.

Created: `EvilDuckS3/script_functions.cpp`, `script_functions.h`;
`docs/stage6-design.md`, `docs/stage6-report.md`, `docs/stage6-results.json`;
`tests/stage6/README.md`, `test_main.cpp`, `run_tests.py`, `no_alloc.cpp`.

## Remaining validation and Stage 7 recommendation

Physical validation is still required for USB keyboard reports/backpressure and
held-key release, real SPIFFS/SD seeking/removal failures, HTTP/CLI responsiveness,
heap fragmentation and task-stack high-water margins. This work did not interact
with a device or authorize migration. All original migration/recovery guards and
archives are preserved. No Stage 7 implementation is included.

Recommended Stage 7 scope: documented multiline STRING/STRINGLN runtime behavior
and END_STRING/END_STRINGLN, streamed output, interpolation/DEFINE rules for text,
line endings, timing and cancellation. Preserve literal control-looking text and
all Stage 1–6 suites. Internal Hak5 variables, advanced firmware/device commands,
remaining F13/German locale fixes and complete reference equivalence require
separate work; no full DuckyScript compatibility claim is made.

## Exact executed test names

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
| stage_2 | `stage2_text_blocks_literal_mode_and_deferred_runtime` | PASS | 36 |
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
| stage_2_5 | `stage25_reviewed_partition_layout` | PASS | 15 |
| stage_2_5 | `stage25_overlapping_partitions_rejected` | PASS | 1 |
| stage_2_5 | `stage25_unaligned_application_rejected` | PASS | 1 |
| stage_2_5 | `stage25_reviewed_offsets_sizes_flags_enforced` | PASS | 10 |
| stage_2_5 | `stage25_core_version_pin_enforced` | PASS | 1 |
| stage_2_5 | `stage25_application_size_boundary` | PASS | 3 |
| stage_2_5 | `stage25_image_header_configuration_enforced` | PASS | 6 |
| stage_2_5 | `stage25_build_configuration_and_app_address_enforced` | PASS | 22 |
| stage_2_5 | `stage25_generated_16m_build_artifacts` | PASS | 4 |
| stage_2_5 | `stage25_corrupt_partition_binary_rejected` | PASS | 1 |
| stage_2_5 | `stage25_merged_image_wrong_address_rejected` | PASS | 1 |
| stage_2_5 | `stage25_stale_4m_partition_artifact_rejected` | PASS | 1 |
| stage_2_5 | `stage25_saved_physical_flash_capacity_guard` | PASS | 7 |
| stage_2_5 | `stage25_offline_source_archives_require_file_migration` | PASS | 11 |
| stage_2_5 | `stage25_offline_preparation_rejects_invalid_backups` | PASS | 6 |
| stage_2_5 | `stage25_offline_preparation_never_overwrites` | PASS | 2 |
| stage_2_5 | `stage25_build_wrapper_requires_clean_output` | PASS | 3 |
| stage_2_5 | `stage25_verified_device_map_differs_from_core_default` | PASS | 3 |
| stage_2_5 | `stage25_raw_spiffs_size_mismatch_refused` | PASS | 3 |
| stage_2_5 | `stage25_recorded_backup_hash_guards` | PASS | 4 |
| stage_2_5 | `stage25_file_level_extract_repack_roundtrip` | PASS | 8 |
| stage_2_5 | `stage25_file_level_empty_filesystem` | PASS | 1 |
| stage_2_5 | `stage25_file_level_capacity_and_overwrite_guards` | PASS | 7 |
| stage_2_5 | `stage25_corrupt_or_wrong_geometry_extraction_refused` | PASS | 4 |
| stage_2_5 | `stage25_alternative_layout_maximum_equal_slots` | PASS | 4 |
| stage_2_5 | `stage25_review_only_plan_preserves_nvs_and_initializes_both_apps` | PASS | 24 |
| stage_2_5 | `stage25_write_and_erase_region_guards` | PASS | 13 |
| stage_2_5 | `stage25_ota_initializer_selects_app0_deterministically` | PASS | 7 |
| stage_2_5 | `stage25_plan_refuses_unverified_files_and_backup_provenance` | PASS | 16 |
| stage_2_5 | `stage25_mac_old_core_rejected_before_compile` | PASS | 1 |
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
| stage_3 | `stage3_define_comment_and_text_modes` | PASS | 25 |
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
| stage_4 | `stage4_text_blocks_preserve_literal_modes` | PASS | 28 |
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
| stage_5 | `stage5_text_blocks_keep_literal_modes` | PASS | 14 |
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
| stage_6 | `stage6_rem_and_text_modes` | PASS | 13 |
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
