# Stage 4: implemented conditional execution and executed validation

**Historical stage results:** owner evidence supplied on 2026-10-10 corrected
the installed SPIFFS map. Any old raw-relocation validation listed below used
an assumed map and is superseded by [the migration correction](../../docs/s3-migration-correction-results.md).
Original test results remain recorded; they do not authorize that old workflow.

Stage 4 only is complete. No physical hardware was accessed, flashed, erased,
formatted, migrated or sent real HID output. Stage 5 was not started. The 16 MiB
profile is a repository compilation configuration, not verification of an
individual EvilDuck module or authorization to upload this build.

[The implementation contract](../../docs/stage4-design.md) records the plan,
reference, exact syntax, compatibility choices and scope restrictions made before
implementation. No Arduino Micro files or Stage 3 expression-engine files changed.

## Syntax and architecture

Canonical syntax is `IF expression THEN`, optional `ELSE IF expression THEN`
entries, optional final `ELSE`, and `END_IF`. ELSE IF is one branch chain, not a
new frame. THEN is required as a final complete token in canonical forms.
Parentheses/grouping use the Stage 3 evaluator. Statements retain EvilDuck's
case-insensitive keywords and spaces/tabs. ELSEIF/ELIF are not accepted.

The runtime uses eight fixed frames, each containing four booleans: parent
activity, current activity, branch already taken, and final ELSE seen. Including
the depth counter, the stack uses **33 bytes**. IF pushes one frame; ELSE IF and
ELSE update the top frame; END_IF pops it. The first eligible true condition wins.
Inactive nested IFs still push/pop frames but do not evaluate runtime conditions.
An ELSE IF expression is evaluated only when its parent is active and no earlier
branch matched. Runtime conditions call the existing Stage 3 engine directly;
no second numeric evaluator or expression parser was introduced.

Inactive command statements never reach `com::send`: no HID, delay/default-delay,
repeat, assignment/declaration, READ/SAVE/APPEND, locale, LED, attack mode or STOP
side effects. Canonical DEFINE remains global preprocessing even if its source
line is in an inactive branch, preserving Stage 3's definition semantics.

Preflight validates every branch expression and uses its existing bounded frame
stack to check ordering, nesting and terminators before any HID. It checks syntax,
known constant faults and symbol types/references without evaluating runtime
variable values. Branch declarations add conservative global metadata; skipped
runtime declarations may still cause later runtime undefined-variable errors.
Mixed IF/WHILE or nested WHILE structures remain rejected/deferred; standalone
legacy WHILE behavior and its known false-WHILE defect are unchanged.

All passes retain 256-byte/eight-line update budgets. Execution streams inactive
regions without scanning ahead or buffering a script. STOP clears conditional
state, cancels pending work and retains the existing key-release/retry mechanism.
Conditional markers and inactive commands never enter keyboard replay history;
REPEAT/REPLAY use the most recent actually executed repeatable keyboard command.

DEFINE may expand condition operands. Raw IF/ELSE IF/ELSE/END_IF prefixes and a raw
terminal THEN are protected from replacement. Macros cannot manufacture these
conditional delimiters, including THEN. Comment/text lexical modes remain literal;
STRING/STRINGLN block runtime support stays deferred to Stage 7.

## Reproduce

All commands below were executed successfully in the cloud workspace:

```sh
python3 tests/stage2/run_tests.py \
  --build-dir /workspace/tooling/arduino/build/stage4-host
python3 tests/stage3/run_tests.py \
  --build-dir /workspace/tooling/arduino/build/stage4-host
python3 tests/stage4/run_tests.py \
  --build-dir /workspace/tooling/arduino/build/stage4-host
XDG_CACHE_HOME=/workspace/tooling/arduino/cache python3 tools/build_s3.py \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli \
  --config-file /workspace/tooling/arduino/arduino-cli.yaml \
  --build-dir /workspace/tooling/arduino/build/stage4-verified-s3-16m --jobs 2
python3 tests/stage25/run_tests.py \
  --core-dir /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /workspace/tooling/arduino/build/stage4-verified-s3-16m
```

The Stage 2 runner includes all Stage 1 tests. Choose a new empty firmware build
directory for a repeat build. The wrapper enforces a clean build and pins
Arduino ESP32 **3.3.0**; Arduino CLI **1.3.1** was used.

The unchanged FQBN is:

```text
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

Generated headers/configuration/partition artifacts were validated as 16 MiB,
80 MHz, ESP32-S3. The existing Arduino QIO recipe emits DIO image-header fields.
The repository layout and both `0x740000` OTA slots are unchanged; app0 remains
at `0x10000`. No partition migration or upload was attempted.

## Actual test results

**134 PASS, 0 FAIL, 2 resolved XPASS diagnostics, 3 unresolved XFAIL diagnostics;
75,477 assertions**, including 12 diagnostic sanity checks. All listed tests ran;
none were skipped. Stage 4 includes 41 integration tests and one separate
allocation/state probe. Exact names and assertion counts follow below.

| Suite | PASS | FAIL | XPASS | XFAIL | Assertions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Stage 1 regressions | 5 | 0 | 0 | 0 | 127 |
| Stage 1 diagnostics | 0 | 0 | 2 | 3 | 12 sanity checks |
| Stage 2 | 30 | 0 | 0 | 0 | 797 |
| Stage 2.5 | 17 | 0 | 0 | 0 | 96 |
| Stage 3 | 40 | 0 | 0 | 0 | 13,815 |
| Stage 4 | 42 | 0 | 0 | 0 | 60,630 |

ASan, UBSan and enabled leak checks produced **no reports** in the C++ suites.
Python Stage 2.5 validation is not sanitizer-instrumented. HID, clock, SPIFFS/SD,
command output and supporting interfaces were mocked; no real USB output occurred.

The required fixture ran through both mocked SPIFFS and SD. Actual visible output:

```text
outer-true
inner-true
x=6
```

Each line had Enter; no inactive-branch strings appeared. The selected-assignment
fixture produced `x=5` then `later`, confirming a later conditional observes the
assignment. Malformed structure/expressions after an earlier STRINGLN produced
zero HID. Variable-dependent runtime errors in eligible conditions stopped safely;
conditions in inactive parents or after an earlier matching branch were skipped.

The allocation probe executed 10,000 evaluator/branch-state chains, exercising
nested selection, final ELSE suppression, restoration, exact depth, overflow,
clear and underflow guards. It observed zero C++ heap allocations. This proves the
fixed-stack/evaluator path in that probe, not all parser String operations or an
ESP32 runtime heap watermark. Legacy text adaptation and existing String-based
line parsing retain bounded allocations. The 1,500-line inactive-region test
verified both preflight rewinds before measuring execution's eight-line yield
budget and cancelling before later output.

### Stage 1 and Stage 2

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

### Stage 2.5

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
| `stage25_offline_spiffs_relocation_preserves_data` | PASS | 12 |
| `stage25_offline_preparation_rejects_invalid_backups` | PASS | 6 |
| `stage25_offline_preparation_never_overwrites` | PASS | 2 |
| `stage25_build_wrapper_requires_clean_output` | PASS | 3 |

### Stage 3

| Exact test name | Result | Assertions |
| --- | --- | ---: |
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

| Exact test name | Result | Assertions |
| --- | --- | ---: |
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

### Original diagnostics, unchanged test expectations

The two resolved diagnostics printed XPASS because their actual behavior now
matches the original desired output. Their fixtures/assertions were not weakened
or relabelled. New Stage 4 assertions independently require these behaviors.

| Exact diagnostic | Expected | Actual | Status |
| --- | --- | --- | --- |
| `known_nested_if` | `good` | `good` | XPASS, resolved |
| `known_canonical_if` | `good` | `good` | XPASS, resolved |
| `known_false_while` | `good` | Empty output | XFAIL |
| `known_f13_mapping` | HID usage 104 | HID usage 70 | XFAIL |
| `known_german_ascii_table` | 128 records | 115 records | XFAIL |

## Final clean-build measurements

| Measurement | Stage 3 | Stage 4 | Growth |
| --- | ---: | ---: | ---: |
| Compiler program storage | 1,293,555 B | **1,297,079 B** | +3,524 B |
| Actual application `.bin` | 1,293,696 B | **1,297,232 B** | +3,536 B |
| Static RAM | 69,880 B | **69,912 B** | +32 B |
| Free bytes per OTA slot | 6,308,480 B | **6,304,944 B** | -3,536 B |
| Free percentage per OTA slot | 82.9826% | **82.9360%** | |

Each OTA slot is 7,602,176 bytes. Compiler RAM maximum is 327,680 bytes; 257,768
bytes remain before runtime allocations. Actual physical heap is unmeasured.
Application SHA-256:
`0a2b9eb030d43bd9bb2cdc6b3ef08b3119b61d9e0da512abc6a65b8dfed9fbe6`.

Final-source ESP32 compiler frame estimates: condition helper 176 bytes,
preflight Validator::accept 160 bytes, duckscript::update 192 bytes, and run
initialization 1,536 bytes. Conditional nesting does not add recursive executor
frames. The Stage 3 evaluator's bounded recursion remains unchanged. The ELF
RunState is 1,444 bytes, versus 1,412 in Stage 3; its old one-byte IF flag is
replaced by the 33-byte stack. These are compiler/static estimates, not complete
call-stack certification or physical high-water measurements.

## Every changed or created repository file

Modified:

* `EvilDuckS3/script_parser.h`: ELSE IF kind, legacy-condition flag and shared
  condition-evaluation interface.
* `EvilDuckS3/script_parser.cpp`: canonical syntax, explicit legacy text adapter,
  Stage 3 evaluator integration, conditional macro protection and nested preflight.
* `EvilDuckS3/duckscript.cpp`: fixed conditional runtime stack, eligible branch
  evaluation, side-effect suppression and cancellation/reset.

Created:

* `EvilDuckS3/conditional_state.h`: pure fixed-size conditional state.
* `docs/stage4-design.md`: pre-implementation plan/reference/compatibility contract.
* `tests/stage4/test_main.cpp`: 41 mocked integration/conditional tests.
* `tests/stage4/run_tests.py`: ASan/UBSan compilation and execution runner.
* `tests/stage4/no_alloc.cpp`: evaluator/stack allocation and boundary probe.
* `tests/stage4/README.md`: this detailed executed-results report.

No prior test sources were changed. Arduino Micro, WHILE implementation, HID,
SD/web commands, variables, expression semantics and the build/partition profile
were not changed. A Stage 4-only patch is provided separately against a
SHA-256-verified snapshot of the approved Stage 3 repository.

## Compatibility, uncertainty and physical checks

Retained explicit EvilDuck aliases: no-THEN atom/equality IF, legacy text equality
and text truthiness, ENDIF and END IF. Text identity tokens/truth values are adapted
before entering the sole expression evaluator. Canonical THEN expressions never
accept text variables. Numeric-only legacy equality now uses uint16 numerical
semantics (`01 == 1` is true); undefined legacy variables now fail clearly rather
than being literal/false. IF expressions outside the old grammar require THEN.
Conditional macro synthesis is newly rejected. These intentional differences were
recorded before implementation and have dedicated tests.

The documented ELSE IF spelling and nesting were verified against Hak5's page;
no official compiler/runtime or physical device served as an oracle. Compound
expressions without enclosing parentheses are accepted per the user's examples;
the reference recommends parentheses in nearly all cases. Stage 3's documented
arithmetic/precedence uncertainties and eager expression operators are unchanged.
Path-sensitive declaration validation and mixed IF/WHILE execution remain deferred.
Text-block runtime support, functions and other later-stage language work remain
outside this stage.

Physical checks remain pending: individual flash capacity and recovery verification,
separately authorized migration, harmless USB HID/Enter and locale behavior,
STOP/key release under real USB backpressure, actual storage/file faults, web/CLI
concurrency, runtime heap/stack watermarks, LED/mode commands, dual-slot OTA and
NVS/SPIFFS/coredump preservation. No hardware results are claimed.

Stage 4 ends here. Stage 5 and physical migration must wait for separate review
and authorization.
