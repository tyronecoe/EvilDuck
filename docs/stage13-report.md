# Stage 13 implementation and verification report

Baseline: `stage12-internal-variables-lock-feedback` at `f3841747fee7ff79c381723d1e578e5d65410011`. Delivery branch: `stage13-duckyscript-preprocessing`. This report and all source files are committed together; the Git commit containing this document is the exact delivery revision. No Stage14 implementation or physical operation.

## Outcome

706 regular PASS, 0 FAIL, 5 retained historical XPASS, 0 XFAIL. 471,670 assertions including 12 diagnostic sanity assertions and 574 separate observation assertions. Stage13 adds 122 tests (9,081 assertions). All 79 Stage9 observations matched; unsupported observations are not counted as compatibility passes. ASan/UBSan clean in all applicable production-source host suites and allocation probes. Partition/build/migration tests use Python/Espressif offline tools. No physical host compatibility is established.

## Reference-backed source features and compatibility decisions

* `REM_BLOCK DOCUMENTATION` and bare `REM_BLOCK` match argument-free `END_REM`; comment content never expands or executes. Only the documented heading is added. Ordinary REM and EvilDuck `//` remain supported.
* Fourteen block-only STRING/STRINGLN aliases: POWERSHELL, BATCH, BASH, JAVASCRIPT, PYTHON, RUBY, HTML. STRING aliases close only with END_STRING; STRINGLN aliases close only with END_STRINGLN. Suffixed terminator-looking text remains literal; a missing proper terminator fails preflight. Exact base-family mismatches reject. No embedded-language interpreter.
* STRING aliases strip leading spaces/tabs, concatenate physical lines without separators and preserve trailing content. STRINGLN aliases strip exactly one initial literal tab and press Enter per body line, including blanks. Empty blocks emit nothing. Existing bounded DEFINE expansion then EvilDuck numeric/text variable interpolation remains; source formatting is removed before replacement. Literal command-looking bodies never enter the statement parser.
* `EXTENSION name` / `END_EXTENSION` are transparent source wrappers. VERSION is optional dotted-decimal metadata, once before body content, never a runtime command. Up to 16 unique included extension identifiers of 32 bytes; nested/crossing wrappers reject. Functions/globals/ordinary statements within wrappers work. No arbitrary inclusion, downloads, online version checking or namespaced/local variables.
* `IF_DEFINED_TRUE label`, `IF_NOT_DEFINED_TRUE label`, `ELSE_DEFINED`, `END_IF_DEFINED`: exact tokens; one DEFINE label for opening directives, no arguments for delimiters. Undefined is false; tested defined flags must be literal TRUE/FALSE. Nested inclusion depth 8, separate from combined runtime IF/WHILE depth 8. Excluded ordinary unsupported syntax is not semantically validated or inventoried; lexical/comment/text, wrapper and preprocessor structure remain checked.
* Included DEFINE collection and inclusion decisions occur in physical source order. Excluded DEFINE has no effect; flags inside an excluded parent are not evaluated. Decisions freeze before symbol inventory/semantic preflight. Existing global forward macro substitution in included ordinary statements remains, while a later flag definition does not retroactively affect an earlier preprocessing directive. No recursive macro or fixed-point compilation.
* A 1024-byte physical-line bitmap replaces the old collection state inside the existing run object. Subsequent inventory, validation and runtime read the same bounded source and consult fixed membership even after function calls, returns and WHILE backedges. No source text/AST/cache or unbounded interval metadata is retained. All physical lines, including excluded ones, retain reader size/line/encoding/I/O checks and source diagnostics.
* Raw delimiters and metadata are protected from DEFINE manufacturing. The existing single expression engine, variable semantics, held-key ownership, scheduler, delays, history, cancellation and source bounds are preserved. Structural metadata never replaces REPEAT history. New source/metadata/LED/alias names follow the existing reserved-function-name rule; previously custom functions with those names now reject, an explicit compatibility restriction.
* `LED_R`, `LED_G`, `LED_OFF`: red/green/black on the existing one-pixel RGB backend, respecting user disable-LED. Canonical commands override default status/idle colors until the next script. Existing error-red priority remains; legacy `LED r g b`/`LED OFF` semantics and normal idle behavior remain. No independent LED channels, blink policy or writable canonical LED-status variables are claimed.

The pre-implementation [design](stage13-design.md) records reference ambiguities and safety/profile decisions. [Reference provenance](stage13-reference-sources.json) verifies five saved official pages; fresh relevant Markdown/image retrieval returned 403. Hak5-owned payload repository examples establish unsuffixed alias terminators; community examples do not prove an independent compiler oracle. No fabricated canonical expectations for arbitrary flag truthiness, forward-condition references, general extension titles/version grammars or recursive expansion.

## Architecture and limits

| Item | Bound / storage |
| --- | --- |
| Source | 256 KiB; 8192 physical lines ; 512 UTF-8 bytes per line |
| Per update | 256 consumed source bytes, at most 8 physical lines; existing 64-byte reader cache |
| Inclusion map | 1024 bytes; one bit per physical line; no allocation per membership read |
| Preprocessing frames | 8 ×8bytes =64 bytes; no recursion |
| Included extension-name table | 16 ×33bytes =528 bytes |
| Complete Filter | 1636 bytes; inside the global run state, not on task stack |
| Runtime control/calls/functions | Existing combined IF/WHILE depth 8, call depth 8, function table 16; unchanged budgets |
| Run state ELF object | 13416 bytes vs 11776 at Stage12 (+1640); directly placement-constructed in global storage |
| Command Session ELF object | 168 bytes unchanged; LED Boolean fits existing storage |

All passes remain cooperative, streamed from SPIFFS or SD, with no recursion through scripts. Included unmatched raw comment/text closers are validated in the expanded inventory pass so an earlier illegal macro-created boundary retains its proper diagnostic; excluded closers are raw-validated immediately. All detected preflight errors precede HID. Reader faults and STOP cancel pending work and release runtime-owned keys via unchanged Stage11 scheduling. No second condition evaluator or preprocessor expression grammar was introduced.

## Automated verification

| Suite | PASS | Assertions |
| --- | ---: | ---: |
| Stage1 | 5 | 127 |
| Stage2 | 30 | 791 |
| Stage2.5 | 30 | 190 |
| Stage3 | 40 | 13814 |
| Stage4 | 42 | 60626 |
| Stage5 | 59 | 92019 |
| Stage6 | 65 | 60726 |
| Stage7 | 68 | 40520 |
| Stage8 | 41 | 43666 |
| Stage10 | 52 | 1608 |
| Stage11 | 72 | 20409 |
| Stage12 | 80 | 127507 |
| Stage13 | 122 | 9081 |
| Stage9 separate observations | 79 matched /0 mismatches | 574 |
| Historical diagnostic sanity | 5 XPASS /0 XFAIL | 12 |

Historical XPASS names retained unchanged: `known_nested_if`, `known_canonical_if`, `known_false_while`, `known_f13_mapping`, `known_german_ascii_table`. No expectations were relabelled to conceal failures. Five Stage9 former source gaps (comment heading, aliases, extension wrapper, preprocessing, LED_G) are now labelled RESOLVED_STAGE13 with actual expected output; other unsupported observations remain gaps. Their successful paths use 10 fewer observation assertions than Stage12; this is path-specific accounting, not dropped tests.

Initial development runs exposed fixture-dispatch/assertion errors, an earlier raw-marker diagnostic changing the Stage3 macro test, and a Stage7 literal-terminator-prefix regression. All were corrected; final unchanged prior tests pass. No production semantics were removed to manipulate XFAIL/XPASS. Final run logs are represented in [machine-readable results](stage13-results.json); exact names/counts appear below.

Allocation observations: bitmap membership across every boundary with selected first/last bits made0 C++ allocations; Filter storage1636 bytes. Prior expression/control/call/text/HID/storage/feedback probes also pass. String parsing/substitution still uses bounded Arduino String allocations; C++ new probes do not measure all malloc/library/web/filesystem/task activity. ASan/UBSan is not ThreadSanitizer or a physical heap/stack measurement.

## Clean embedded build and resources

| Measurement | Stage12 | Stage13 | Growth |
| --- | ---: | ---: | ---: |
| Compiler program bytes | 1321255 | 1326643 | +5388 |
| Actual application binary bytes | 1321408 | 1326784 | +5376 |
| Static RAM bytes | 80504 | 82224 | +1720 |
| Free application bytes per slot | 6280768 | 6275392 | -5376 |
| Free percentage per slot | 82.6180% | 82.547313% | |

Application SHA256: `a9bf3d7cc0b6cfdce6aba2ad80c1044a25986bf6cacc29021abf56578338d015`. Static RAM remaining compiler budget: 245456bytes; this is not runtime free heap. Core3.3.0, QIO80MHz,240MHz, USB-OTG/TinyUSB with CDC on, boot MSC/DFU default, PSRAM disabled. Exact FQBN:

`esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default`

Clean build wrapper verified ESP32-S3 image headers/16MiB configuration, repository CSV, app0 address0x10000 and each0x740000 slot. [Build log](stage13-build.log) and results JSON retain measurements. All 30 Stage2.5 tests passed, including raw SPIFFS mismatch rejection, NVS exclusion, backup hashes/provenance, OTA initializer/slot placement, offline write-plan validation and old local core refusal. No partition or migration changes. The build report hardware_verified=false means this compilation made no physical query; it does not revoke earlier user-supplied verification. Generated merged output is not a migration artifact and was never flashed.

Compiler per-function stack estimates ([records](stage13-stack-results.json)):

| Module | Stage12 maximum | Stage13 maximum |
| --- | ---: | ---: |
| attackmode.cpp | 112 | 112 |
| com.cpp | 224 | 224 |
| duck_constants.cpp | 592 | 592 |
| duck_expr.cpp | 96 | 96 |
| duck_keys.cpp | 96 | 96 |
| duck_vars.cpp | 112 | 112 |
| duckscript.cpp | 1056 | 1072 |
| hid_backend.cpp | 80 | 80 |
| keyboard_locale.cpp | 64 | 64 |
| script_functions.cpp | 64 | 64 |
| script_parser.cpp | 288 | 288 |
| script_preprocessor.cpp | new | 160 |
| sd_card.cpp | 160 | 160 |
| usb_msc.cpp | 592 | 592 |

Filter::accept 160 bytes; RawBlocks::scan 144 bytes; per-function maximum 1072 bytes (returnFunction) vs 1056. These are individual compiler estimates excluding callees, recursion, interrupts and libraries. Loop task configured 8192 bytes; real high-water and task/web/SD contention remain unmeasured. Global fixed state avoids a large task-stack temporary. No new unbounded report queue, AST, symbol table or heap hot-path state.

## Preservation, unresolved limits and next review

No changes to Arduino Micro, partition CSV, migration safeguards, Stage10 MSC/SD/attackmode, Stage11 HID backend or Stage12 internal-variable/feedback implementation. Existing remote branch hashes were compared before/after verification. No physical USB/HID/storage/flash/erase/format/OTA operations or destructive commands; only mocked RAM I/O and offline compilation/tooling.

Remaining gaps include randomization/jitter, packed INJECT_VAR, restart, buttons, full LED-status variables and real USB personality/identity/host activity. Stage12 upstream ID0 zero-length routing dereference, control SET_REPORT report-type erasure and absence of wire-session identity remain documented in [USB feedback analysis](stage12-usb-feedback-analysis.md) for a dedicated investigation. Unknown lock states still fail truthfully, never become FALSE. No new HID routing claim.

Reference uncertainties: source-order/forward preprocessing, nonliteral flag truthiness, general extension name/version grammar and recursive substitution lack an independent compiler comparison; bounded explicit profiles reject ambiguous forms. Known host-language `$name` interpolation collisions remain an EvilDuck extension limitation. Source mutation between passes is the existing unverified filesystem/concurrency risk; no new snapshot guarantee. Arbitrary Unicode, additional layouts and physical key composition remain limited as previously documented.

Physical validation remains separately authorized: one-pixel RGB color/order and default/error priorities; SPIFFS/SD latency/faults and cancellation under web activity; actual USB acceptance/disconnect/release and LED feedback; harmless High Sierra10.13.6 TextEdit output with the matching input source; heap/task-stack high-water. Mocked exact output and accepted reports do not prove physical host receipt. No firmware migration artifact or procedure was changed.

Recommended Stage14 scope after review: bounded device-backed randomization and cooperative per-keystroke jitter, deterministic mocked RNG/range/seed tests and reference-backed variable lifecycle. Defer packed INJECT_VAR until its encoding is independently established; keep upstream USB routing/personality work as a separate scoped investigation. Stage14 has not started.

## Reproduction (offline; no device)

```sh
python3 tests/stage13/run_tests.py --build-dir /tmp/evilduck-stage13 --results /tmp/stage13-results.json
# Run tests/stage2 through stage12 as documented in their existing runners.
# Stage2 includes all five Stage1 regressions and historical diagnostic observations.
python3 tools/build_s3.py --arduino-cli /path/to/arduino-cli --config-file /path/to/arduino-cli.yaml --build-dir /tmp/evilduck-stage13-clean --jobs 2
python3 tests/stage25/run_tests.py --core-dir /path/to/esp32/3.3.0 --build-dir /tmp/evilduck-stage13-clean
python3 tools/analyze_s3_stack.py --build-dir /tmp/evilduck-stage13-clean --output /tmp/stage13-stack.json
```

Use the existing documented toolchain/libraries and a new empty external build directory. The wrapper rejects the wrong core/profile; no port, upload, erase or OTA operation is invoked. Two checked-in `.duck` fixtures are executed verbatim by tests: source-compatibility → literal IF/WHILE text+Enter; excluded-source → included-only+Enter.

## Every modified/created file

* `EvilDuckS3/com.cpp`
* `EvilDuckS3/com.h`
* `EvilDuckS3/config.h`
* `EvilDuckS3/duck_constants.cpp`
* `EvilDuckS3/duck_constants.h`
* `EvilDuckS3/duckscript.cpp`
* `EvilDuckS3/script_functions.cpp`
* `EvilDuckS3/script_parser.cpp`
* `EvilDuckS3/script_parser.h`
* `EvilDuckS3/script_preprocessor.cpp`
* `EvilDuckS3/script_preprocessor.h`
* `docs/stage13-build.log`
* `docs/stage13-compatibility-inventory.json`
* `docs/stage13-compatibility-matrix.md`
* `docs/stage13-design.md`
* `docs/stage13-reference-sources.json`
* `docs/stage13-report.md`
* `docs/stage13-results.json`
* `docs/stage13-stack-results.json`
* `tests/stage1/run_tests.py`
* `tests/stage10/run_tests.py`
* `tests/stage12/run_tests.py`
* `tests/stage13/README.md`
* `tests/stage13/fixtures/excluded-source.duck`
* `tests/stage13/fixtures/source-compatibility.duck`
* `tests/stage13/no_alloc.cpp`
* `tests/stage13/run_tests.py`
* `tests/stage13/test_main.cpp`
* `tests/stage9/fixtures.json`
* `tools/analyze_s3_stack.py`

## Exact final regression names and assertion counts

All following entries actually executed with PASS status. Observations/XPASS remain separate as above.

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

