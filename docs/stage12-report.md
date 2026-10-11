# Stage 12 implementation and verification report

Baseline: `stage11-duckyscript-hold-release`, commit `3714866f88ac8a42cbfffc93bf2ba7572bd3a7b7`.
Delivery branch: `stage12-internal-variables-lock-feedback`. This report is included in the delivery commit; use `git rev-parse HEAD` for its exact SHA.

## Delivered behavior

A fixed device-backed registry protects all37 audited native names, separately from the16 ordinary symbols. Seven native lock variables are implemented;30 native names remain explicitly unsupported. The38th audit name, `$_OS`, remains an extension-defined user global, with no built-in OS detection. Eight explicitly named EvilDuck extensions expose truthful logical/media state and a bounded executor timeout. No dynamic registry/table or second evaluator. See [complete38-name matrix](stage12-internal-variable-matrix.md), [preimplementation design](stage12-design.md), and [pinned USB contract](stage12-usb-feedback-analysis.md).

The single Stage3 expression evaluator receives distinct Unsupported/Unavailable lookup diagnostics. Syntax preflight recognizes known numeric types without requiring feedback or creating native symbols. VAR/DEFINE compatibility aliases/READ cannot shadow reserved properties. Read-only and unsupported assignments reject during preflight, including inside inactive branches. Unsupported reads in numeric expressions fail preflight; unknown runtime lock reads fail safely. Interpolation uses actual observed values or reports unknown/unsupported instead of silently typing a fake setting. Ordinary user/extension variables, text compatibility and existing expression limits remain unchanged.

HID feedback is delivered through a derived USBHIDKeyboard overriding the pinned output/control hooks while preserving descriptors, report ID1 and8-byte input reports. Normalize-and-validate expects ID1, exactly one nonnull LED byte and zero upper padding bits. Five descriptor LED bits are accepted; Num/Caps/Scroll bits0/1/2 drive state. Initial/current/saved unknown state remains unavailable, not FALSE. The received flag reports absence/presence of valid evidence. First valid report saves attach state; explicit SAVE replaces it. USB loss or backend reinitialization invalidates both states and transition counters. Script completion/STOP/RESET does not erase device evidence. No settings/NVS writes are introduced.

Canonical no-argument commands: `WAIT_FOR_CAPS_ON`, `WAIT_FOR_CAPS_OFF`, `WAIT_FOR_CAPS_CHANGE`, the corresponding NUM and SCROLL forms, `SAVE_HOST_KEYBOARD_LOCK_STATE`, `RESTORE_HOST_KEYBOARD_LOCK_STATE`. ON/OFF waits require an observed desired bit. Unknown CHANGE first establishes a baseline; repeated reports do not count as changes. Dedicated per-lock uint32 counters preserve rapid transitions between ticks. All commands use the existing cooperative scheduler, support cancellation and source/line errors, and do not replace legacy repeat history.

Restore refuses unknown saved/current state, disabled HID or persistent ownership. It schedules/release one physical lock key at a time through Stage11 reporting and requires a subsequent observed matching transition. It rechecks a pending toggle after endpoint backpressure, refusing to knowingly undo an already restored bit. Total deadline and6 planned-toggle budget bound contention; no accepted report is used as host acknowledgment. Already observed matching saved/current state needs no injection. STOP/error/disconnect clears ownership and retains Stage11 priority release; physical reception while disconnected is not claimed.

## Compatibility policies and remaining uncertainties

* `$_EVILDUCK_LOCK_TIMEOUT` is explicitly an EvilDuck extension: uint16, default5000ms, assignments1..65535, reset with execution/user-variable state. Constant-zero arithmetic rejects preflight; runtime-derived invalid values diagnose safely. No new WAIT argument syntax. The finite timeout differs from the reference’s indefinite waiting semantics.
* Canonical lock variables are read-only here because the reference describes host-maintained evidence/save results and does not independently establish user-write permissions. Unsupported native mutable settings are rejected, never simulated. A future extension/runtime reference comparison must establish any broader write contract.
* First valid feedback, rather than mere USB attach, initializes saved state. Within a USB session values are last observed bits; passive values do not expire periodically. They cannot prove host synchronization, fresh continuous reporting or another attached keyboard’s state.
* Newly reserved documented native names can reject older scripts that created inert native-looking ordinary variables. `$_OS` and unknown ordinary `$_CUSTOM` extension names retain compatibility; variable case remains significant. Stage9 observation expectations change explicitly, historical reports/branches remain intact.
* Fresh official documentation requests returned HTTP403; the Stage9 HTTPS snapshots were hash-verified against recorded provenance. No latest-reference/independent Hak5 runtime conformance claim. Saved/write details, timeout and host race policies remain documented decisions.
* The pinned top-level ID0 routing dereferences buffer[0] before the derived hook on an empty raw request. Device-hook malformed-payload tests do not prove that upstream path safe. The pinned nonzero-ID control route drops report type, so an identical malformed FEATURE request cannot be distinguished at the device hook. These require a separate stack-hardening investigation before claiming complete malformed-USB robustness.
* Firmware session tokens reject stale captured callbacks, not magically identify an old wire packet first delivered after reconnect. LED packets lack injection transaction IDs; a matching observed transition is evidence of target state, not causal proof of our tap. USB sessions/transition counters wrap at2^32; no unlimited history is claimed.
* macOS High Sierra may not synchronize Num/Scroll or every Caps report. No simulated byte test establishes physical host behavior. Native CURRENT_ATTACKMODE remains unsupported because logical HID/storage gating does not implement host-visible personality changes.

## Verification results

All below ran against the final production source with RAM-only endpoints/storage/clock. [Machine-readable results](stage12-results.json) include individual test names/counts and Stage9 observed outputs. Observations of missing features are not language-compatibility passes.

| Suite | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| stage_1 | 5 | 0 | 127 |
| stage_2 | 30 | 0 | 791 |
| stage_25 | 30 | 0 | 190 |
| stage_3 | 40 | 0 | 13,814 |
| stage_4 | 42 | 0 | 60,626 |
| stage_5 | 59 | 0 | 92,019 |
| stage_6 | 65 | 0 | 60,726 |
| stage_7 | 68 | 0 | 40,520 |
| stage_8 | 41 | 0 | 43,666 |
| stage_10 | 52 | 0 | 1,608 |
| stage_11 | 72 | 0 | 20,409 |
| stage_12 | 80 | 0 | 127,507 |
| Historical diagnostic sanity | — | 0 | 12 |
| Stage9 observations | 79 matched separately | 0 mismatches | 584 |

**584 regular PASS,0 FAIL;5 historical XPASS,0 XFAIL;79 observations matched separately;462,599 total assertions.** Stage12 contributes80 PASS and127,507 assertions.

Historical labels remain unchanged and audited: `known_nested_if`, `known_canonical_if`, `known_false_while`, `known_f13_mapping`, `known_german_ascii_table` are still XPASS. None was silently reclassified, and no new XFAIL masks an implementation failure.

Stage9 `undefined_builtin` now observes an unknown runtime lock value rather than an undefined variable. `inert_builtin_declaration` now rejects before HID. `lock_wait` and `save_lock` now recognize canonical syntax; without feedback the former times out and latter refuses unknown state after the fixture’s harmless preceding text. Observation statuses and notes distinguish these from physical or full-language compatibility passes. Assertion changes reflect changed runtime/preflight paths, not removed checks.

ASan/UBSan: clean in all executed C++ targets. Stage2.5 Python validation is not sanitizer-instrumented; TSan was not run. The only final host compiler warning is the pre-existing Stage6 test-source misleading-indentation warning. No newly introduced target warning or sanitizer error remains. Narrow prior allocation probes still pass. Stage12 instruments10000 receive/registry/save cycles and observes0 C++ new allocations after initialization; parser Strings, real USB/SD/web heap and task-stack high-water are not covered.

Development failures are recorded honestly: the first embedded build rejected the incorrect lock-free atomic assumption, which was replaced by a dedicated portMUX guard. A new CLI test’s lower-case `busy` expectation did not match the existing `Busy` diagnostic and was corrected; the operation was properly rejected. Initial Stage3–6 allocation-probe link steps failed because they omitted new device-backed dependencies; their source linkage was corrected, without changing assertions or allocation scope. Subsequent final clean build and every final suite exit0; no failure remains unresolved.

## Clean build/resources

Pinned Arduino ESP32 **3.3.0**, existing USB-OTG TinyUSB/CDC profile, QIO80MHz,CPU240MHz,PSRAM disabled, unchanged16MiB custom partition table. Compilation only; the generic build report’s hardware_verified=false means this build did not probe a device. User-supplied prior16MiB physical evidence is not contradicted; migration was not performed.

```text
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

| Measurement | Stage11 | Stage12 | Growth |
|---|---:|---:|---:|
| Compiler program usage | 1,315,355 B | 1,321,255 B | +5,900 B |
| Actual application .bin | 1,315,504 B | 1,321,408 B | +5,904 B |
| Static RAM | 80,464 B | 80,504 B | +40 B |

Each unchanged `0x740000` OTA slot is7,602,176 bytes; free **6,280,768 bytes (82.61802936%)**. Static RAM remaining247,176 bytes of327,680; physical runtime heap is unmeasured.

Application SHA-256: `efc40b055716e4ef53e2f74a6456c7f4fb017bb662857c31c091af6c4fcdca07`.

Final build directory in this environment: `/workspace/tooling/arduino/build/stage12-final-16m`. The application address remains0x10000; build/header/partition tooling and all30 Stage2.5 safeguard tests pass. No partition, upload or migration tooling changes and no generated binaries committed as device-ready migration artifacts.

Fixed storage objects: native feedback snapshot20B, portMUX8B, timeout2B, scheduler Session168B versus144B (+24B). Object arithmetic is54B while net compiler/static-RAM growth is40B because linker section placement/alignment changes; report the measured aggregate rather than treating object sums as total RAM. Names/constants live in flash, ordinary symbol capacity is unchanged. No HID OUT event queue or whole-script/block buffer.

[Compiler stack evidence](stage12-stack-results.json): individual-frame estimates, not transitive maximum or measured runtime high-water. HID backend maximum80B unchanged; feedback receive/save/invalidate/snapshot each32B. Internal registry resolve96B; duck_vars module maximum112B unchanged. com maximum224B versus208B, update80B versus64B, startLine224B versus208B; begin/endScript208B versus192B. Parser maximum288B and runtime-function frames1056B unchanged. Existing8KiB loop task and core event-task stack remain unchanged; actual callback/main-loop latency, heap fragmentation and high-water require hardware.

## Reproduction

```sh
python3 tests/stage2/run_tests.py --build-dir /tmp/s12-stage2
for stage in 3 4 5 6 7 8 9 10 11 12; do
  python3 tests/stage${stage}/run_tests.py --build-dir /tmp/s12-stage${stage} || exit 1
done
python3 tools/build_s3.py --arduino-cli <arduino-cli> --config-file <arduino-cli.yaml> --build-dir <fresh-output-directory> --jobs 2
python3 tests/stage25/run_tests.py --core-dir <installed-esp32-3.3.0> --build-dir <completed-output-directory>
python3 tools/analyze_s3_stack.py --build-dir <completed-output-directory> --output /tmp/stage12-stack.json
```

These are build/mock/offline checks, not port discovery/flash/erase/OTA commands. Exact source fixtures are in tests/stage12/test_main.cpp. Example read/wait is harmless visible text after actual feedback, and intentionally times out without it:

```text
IF $_RECEIVED_HOST_LOCK_LED_REPLY THEN
    STRINGLN caps=$_CAPSLOCK_ON
END_IF
$_EVILDUCK_LOCK_TIMEOUT = 1000
WAIT_FOR_CAPS_ON
STRINGLN observed-caps-on
```

## Files changed/created

* `EvilDuckS3/com.cpp`
* `EvilDuckS3/duck_expr.cpp`
* `EvilDuckS3/duck_expr.h`
* `EvilDuckS3/duck_vars.cpp`
* `EvilDuckS3/hid_backend.cpp`
* `EvilDuckS3/hid_backend.h`
* `EvilDuckS3/internal_vars.h`
* `EvilDuckS3/script_functions.cpp`
* `EvilDuckS3/script_parser.cpp`
* `docs/stage12-build.log`
* `docs/stage12-design.md`
* `docs/stage12-internal-variable-matrix.md`
* `docs/stage12-reference-sources.json`
* `docs/stage12-report.md`
* `docs/stage12-results.json`
* `docs/stage12-stack-results.json`
* `docs/stage12-usb-feedback-analysis.md`
* `tests/stage1/mocks/USBHIDKeyboard.h`
* `tests/stage12/README.md`
* `tests/stage12/no_alloc.cpp`
* `tests/stage12/run_tests.py`
* `tests/stage12/test_main.cpp`
* `tests/stage3/run_tests.py`
* `tests/stage4/run_tests.py`
* `tests/stage5/run_tests.py`
* `tests/stage6/run_tests.py`
* `tests/stage9/fixtures.json`

Arduino Micro firmware, all previous stage production snapshots, main/prior branches, partitions and migration safeguards remain unchanged. Only the new Stage12 branch is delivered.

## Acceptance evidence: every executed PASS

| Suite | Exact test name | Result | Assertions |
|---|---|---|---:|
| 1 | `supported_commands_and_mock_interfaces` | PASS | 29 |
| 1 | `script_run_state_isolation` | PASS | 22 |
| 1 | `cooperative_delay_and_text_cancellation` | PASS | 33 |
| 1 | `repeat_timing_and_control_loop_yield` | PASS | 24 |
| 1 | `live_commands_cannot_mutate_running_script` | PASS | 19 |
| 2 | `stage2_rem_comments` | PASS | 6 |
| 2 | `stage2_required_rem_block_fixture` | PASS | 12 |
| 2 | `stage2_comment_block_literal_commands` | PASS | 6 |
| 2 | `stage2_unterminated_rem_block_zero_hid` | PASS | 9 |
| 2 | `stage2_unmatched_end_rem_zero_hid` | PASS | 9 |
| 2 | `stage2_lf_source` | PASS | 6 |
| 2 | `stage2_crlf_source` | PASS | 6 |
| 2 | `stage2_utf8_bom` | PASS | 21 |
| 2 | `stage2_missing_final_newline` | PASS | 12 |
| 2 | `stage2_blank_lines` | PASS | 12 |
| 2 | `stage2_spaces_tabs_and_payload_preservation` | PASS | 7 |
| 2 | `stage2_maximum_line_length` | PASS | 12 |
| 2 | `stage2_overlong_line_zero_hid` | PASS | 18 |
| 2 | `stage2_source_byte_limits` | PASS | 16 |
| 2 | `stage2_source_line_limits` | PASS | 15 |
| 2 | `stage2_mismatched_control_blocks_zero_hid` | PASS | 18 |
| 2 | `stage2_unterminated_control_blocks_zero_hid` | PASS | 36 |
| 2 | `stage2_duplicate_else_zero_hid` | PASS | 18 |
| 2 | `stage2_block_depth_limit_zero_hid` | PASS | 9 |
| 2 | `stage2_text_blocks_literal_mode_and_deferred_runtime` | PASS | 30 |
| 2 | `stage2_unterminated_text_blocks_zero_hid` | PASS | 18 |
| 2 | `stage2_unmatched_text_terminators_zero_hid` | PASS | 18 |
| 2 | `stage2_mismatched_text_terminators_zero_hid` | PASS | 27 |
| 2 | `stage2_unknown_commands_zero_hid` | PASS | 27 |
| 2 | `stage2_keyword_prefixes_are_not_commands` | PASS | 128 |
| 2 | `stage2_malformed_statements_zero_hid` | PASS | 210 |
| 2 | `stage2_supported_extensions_and_bare_keys` | PASS | 8 |
| 2 | `stage2_storage_read_seek_faults` | PASS | 25 |
| 2 | `stage2_preflight_cooperative_stop_and_live_ownership` | PASS | 18 |
| 2 | `stage2_live_validation_and_limits` | PASS | 34 |
| 3 | `stage3_addition` | PASS | 3 |
| 3 | `stage3_subtraction` | PASS | 3 |
| 3 | `stage3_multiplication` | PASS | 3 |
| 3 | `stage3_division` | PASS | 3 |
| 3 | `stage3_modulo` | PASS | 3 |
| 3 | `stage3_exponentiation` | PASS | 3 |
| 3 | `stage3_equality` | PASS | 3 |
| 3 | `stage3_inequality` | PASS | 3 |
| 3 | `stage3_less_than` | PASS | 3 |
| 3 | `stage3_greater_than` | PASS | 3 |
| 3 | `stage3_less_or_equal` | PASS | 3 |
| 3 | `stage3_greater_or_equal` | PASS | 3 |
| 3 | `stage3_logical_and` | PASS | 3 |
| 3 | `stage3_logical_or` | PASS | 3 |
| 3 | `stage3_bitwise_and` | PASS | 3 |
| 3 | `stage3_bitwise_or` | PASS | 3 |
| 3 | `stage3_left_shift` | PASS | 3 |
| 3 | `stage3_right_shift` | PASS | 3 |
| 3 | `stage3_precedence_and_grouping` | PASS | 54 |
| 3 | `stage3_literals_booleans_and_whitespace` | PASS | 54 |
| 3 | `stage3_arithmetic_boundaries` | PASS | 57 |
| 3 | `stage3_invalid_literals_and_unsupported_operators` | PASS | 54 |
| 3 | `stage3_malformed_expressions_and_limits` | PASS | 54 |
| 3 | `stage3_numeric_declarations_assignment_and_no_hid` | PASS | 9 |
| 3 | `stage3_required_fixture_spiffs_and_sd` | PASS | 12 |
| 3 | `stage3_variable_references_types_and_atomic_failure` | PASS | 24 |
| 3 | `stage3_text_compatibility_alias_and_read` | PASS | 41 |
| 3 | `stage3_identifier_validation_and_table_exhaustion` | PASS | 91 |
| 3 | `stage3_preflight_zero_hid_and_runtime_errors` | PASS | 46 |
| 3 | `stage3_define_global_forward_and_word_matching` | PASS | 24 |
| 3 | `stage3_define_single_pass_and_declaration_exemption` | PASS | 32 |
| 3 | `stage3_define_comment_and_text_modes` | PASS | 24 |
| 3 | `stage3_define_duplicates_invalid_and_table_limits` | PASS | 76 |
| 3 | `stage3_define_expansion_and_pool_boundaries` | PASS | 32 |
| 3 | `stage3_expression_timing_counts_and_cancellation` | PASS | 17 |
| 3 | `stage3_collection_preflight_stop_and_state_isolation` | PASS | 27 |
| 3 | `stage3_interpolation_overflow_runtime_safe_stop` | PASS | 6 |
| 3 | `stage3_syntax_mode_does_not_evaluate_runtime_values` | PASS | 3 |
| 3 | `stage3_bounded_expression_fuzz` | PASS | 3001 |
| 3 | `stage3_expression_hot_path_no_heap` | PASS | 10022 |
| 4 | `stage4_simple_true_if` | PASS | 6 |
| 4 | `stage4_simple_false_if` | PASS | 6 |
| 4 | `stage4_if_else_true_path` | PASS | 6 |
| 4 | `stage4_if_else_false_path` | PASS | 6 |
| 4 | `stage4_nested_true_true` | PASS | 6 |
| 4 | `stage4_nested_true_false` | PASS | 6 |
| 4 | `stage4_outer_false_nested_inactive` | PASS | 6 |
| 4 | `stage4_multiple_nesting_levels` | PASS | 6 |
| 4 | `stage4_exact_nesting_limit` | PASS | 7 |
| 4 | `stage4_nesting_limit_plus_one` | PASS | 7 |
| 4 | `stage4_else_if_first_true` | PASS | 6 |
| 4 | `stage4_else_if_middle_true` | PASS | 6 |
| 4 | `stage4_else_if_final_else` | PASS | 6 |
| 4 | `stage4_else_if_multiple_entries` | PASS | 6 |
| 4 | `stage4_nested_else_if_chains` | PASS | 6 |
| 4 | `stage4_no_branch_true_without_else` | PASS | 6 |
| 4 | `stage4_selected_assignments_and_later_conditions` | PASS | 6 |
| 4 | `stage4_inactive_side_effects` | PASS | 9 |
| 4 | `stage4_required_fixture_spiffs_and_sd` | PASS | 12 |
| 4 | `stage4_define_conditions_and_protected_keywords` | PASS | 6 |
| 4 | `stage4_macro_manufactured_structures_rejected` | PASS | 56 |
| 4 | `stage4_compound_hex_boolean_conditions` | PASS | 6 |
| 4 | `stage4_malformed_expressions_zero_hid` | PASS | 77 |
| 4 | `stage4_undefined_and_text_variables` | PASS | 28 |
| 4 | `stage4_missing_end_if` | PASS | 7 |
| 4 | `stage4_unexpected_end_if` | PASS | 7 |
| 4 | `stage4_duplicate_else` | PASS | 7 |
| 4 | `stage4_else_outside_if` | PASS | 14 |
| 4 | `stage4_malformed_then_and_else_if` | PASS | 84 |
| 4 | `stage4_invalid_branch_ordering` | PASS | 21 |
| 4 | `stage4_rem_block_conditional_text` | PASS | 6 |
| 4 | `stage4_text_blocks_preserve_literal_modes` | PASS | 26 |
| 4 | `stage4_stop_active_and_inactive_branches` | PASS | 12 |
| 4 | `stage4_external_cancel_delay_text_and_keys` | PASS | 18 |
| 4 | `stage4_repeat_active_inactive_and_structural_history` | PASS | 18 |
| 4 | `stage4_clean_state_between_runs_and_live_ownership` | PASS | 9 |
| 4 | `stage4_runtime_errors_only_in_eligible_conditions` | PASS | 11 |
| 4 | `stage4_cooperative_large_inactive_region_and_preflight` | PASS | 18 |
| 4 | `stage4_legacy_compatibility_aliases` | PASS | 12 |
| 4 | `stage4_keyword_boundaries_whitespace_and_case` | PASS | 34 |
| 4 | `stage4_mixed_while_nesting` | PASS | 12 |
| 4 | `stage4_conditional_stack_no_heap` | PASS | 60012 |
| 5 | `stage5_false_while_following_commands` | PASS | 6 |
| 5 | `stage5_zero_iteration_expressions` | PASS | 36 |
| 5 | `stage5_single_iteration` | PASS | 7 |
| 5 | `stage5_multiple_iterations` | PASS | 7 |
| 5 | `stage5_decrementing_numeric_no_hid` | PASS | 9 |
| 5 | `stage5_shared_expression_operators` | PASS | 84 |
| 5 | `stage5_condition_reevaluated_at_header` | PASS | 8 |
| 5 | `stage5_nested_two_loops` | PASS | 8 |
| 5 | `stage5_nested_three_loops` | PASS | 7 |
| 5 | `stage5_sequential_loops` | PASS | 6 |
| 5 | `stage5_if_inside_while_else_if` | PASS | 6 |
| 5 | `stage5_while_inside_if_else` | PASS | 6 |
| 5 | `stage5_mixed_nested_structures` | PASS | 6 |
| 5 | `stage5_fixture_spiffs_and_sd` | PASS | 12 |
| 5 | `stage5_false_outer_suppresses_nested_conditions` | PASS | 6 |
| 5 | `stage5_inactive_side_effects_and_assignments` | PASS | 10 |
| 5 | `stage5_nested_updates_outer_variable` | PASS | 8 |
| 5 | `stage5_global_declarations_reused` | PASS | 7 |
| 5 | `stage5_exact_loop_depth` | PASS | 6 |
| 5 | `stage5_mixed_exact_depth` | PASS | 6 |
| 5 | `stage5_depth_plus_one_zero_hid` | PASS | 14 |
| 5 | `stage5_malformed_conditions_zero_hid` | PASS | 98 |
| 5 | `stage5_undefined_and_text_expression_rejection` | PASS | 28 |
| 5 | `stage5_missing_unmatched_and_crossed_terminators` | PASS | 42 |
| 5 | `stage5_keyword_boundaries_and_aliases` | PASS | 52 |
| 5 | `stage5_legacy_bare_text_truthiness` | PASS | 12 |
| 5 | `stage5_define_conditions_and_protected_keywords` | PASS | 6 |
| 5 | `stage5_macro_manufactured_loop_delimiters_rejected` | PASS | 28 |
| 5 | `stage5_define_collection_inside_inactive_loop` | PASS | 6 |
| 5 | `stage5_rem_block_loop_text_ignored` | PASS | 6 |
| 5 | `stage5_text_blocks_keep_literal_modes` | PASS | 12 |
| 5 | `stage5_bom_crlf_no_final_newline_backedges` | PASS | 6 |
| 5 | `stage5_header_across_read_budgets` | PASS | 6 |
| 5 | `stage5_reader_marker_and_seek_boundaries` | PASS | 12 |
| 5 | `stage5_runtime_seek_error` | PASS | 7 |
| 5 | `stage5_runtime_read_error_after_backedge` | PASS | 7 |
| 5 | `stage5_runtime_source_size_changed` | PASS | 7 |
| 5 | `stage5_runtime_condition_error_and_inactive_skip` | PASS | 12 |
| 5 | `stage5_runtime_undefined_path_dependent_variable` | PASS | 6 |
| 5 | `stage5_repeat_structural_and_inactive_history` | PASS | 6 |
| 5 | `stage5_repeat_expression_in_loop` | PASS | 6 |
| 5 | `stage5_keyboard_combinations_in_loop` | PASS | 7 |
| 5 | `stage5_expression_delays_in_loop` | PASS | 7 |
| 5 | `stage5_stop_in_active_and_inactive_loops` | PASS | 12 |
| 5 | `stage5_cancel_delay_inside_mixed_loop` | PASS | 6 |
| 5 | `stage5_cancel_text_inside_nested_loop` | PASS | 7 |
| 5 | `stage5_cancel_held_keys_and_usb_pressure` | PASS | 8 |
| 5 | `stage5_control_only_loop_cooperative_and_live_ownership` | PASS | 47 |
| 5 | `stage5_stalled_empty_loop_boundary` | PASS | 7 |
| 5 | `stage5_stalled_same_assignment_and_inactive_actions` | PASS | 7 |
| 5 | `stage5_nested_stall_not_masked_by_outer_progress` | PASS | 6 |
| 5 | `stage5_variable_progress_beyond_stall_threshold` | PASS | 8 |
| 5 | `stage5_total_iteration_limit_and_clean_restart` | PASS | 13 |
| 5 | `stage5_exact_total_iteration_boundary` | PASS | 9 |
| 5 | `stage5_variable_revision_atomic_and_reset` | PASS | 9 |
| 5 | `stage5_cancellation_then_new_source` | PASS | 11 |
| 5 | `stage5_large_inactive_region_cooperative` | PASS | 11 |
| 5 | `stage5_small_nested_loop_reference_cases` | PASS | 175 |
| 5 | `stage5_mixed_control_stack_no_heap` | PASS | 91039 |
| 6 | `stage6_declarations_skipped` | PASS | 6 |
| 6 | `stage6_statement_invocation` | PASS | 6 |
| 6 | `stage6_multiple_calls` | PASS | 6 |
| 6 | `stage6_forward_invocation_and_globals` | PASS | 6 |
| 6 | `stage6_fixture_spiffs_and_sd` | PASS | 12 |
| 6 | `stage6_explicit_void_return` | PASS | 6 |
| 6 | `stage6_implicit_void_return` | PASS | 6 |
| 6 | `stage6_integer_return_assignment` | PASS | 6 |
| 6 | `stage6_boolean_return_conditions` | PASS | 6 |
| 6 | `stage6_statement_discards_return_value` | PASS | 6 |
| 6 | `stage6_void_value_rejected` | PASS | 12 |
| 6 | `stage6_top_level_and_live_return_compatibility` | PASS | 11 |
| 6 | `stage6_enter_and_modifier_return_inside_function` | PASS | 7 |
| 6 | `stage6_return_unwinds_nested_control` | PASS | 6 |
| 6 | `stage6_caller_control_restored` | PASS | 6 |
| 6 | `stage6_nested_statement_calls` | PASS | 6 |
| 6 | `stage6_nested_return_expressions` | PASS | 6 |
| 6 | `stage6_multiple_calls_in_expression` | PASS | 6 |
| 6 | `stage6_earlier_variable_operand_preserved` | PASS | 6 |
| 6 | `stage6_eager_logical_calls` | PASS | 6 |
| 6 | `stage6_inactive_conditions_do_not_call` | PASS | 6 |
| 6 | `stage6_while_condition_calls_reevaluate` | PASS | 6 |
| 6 | `stage6_while_condition_changes_count_as_progress` | PASS | 6 |
| 6 | `stage6_else_if_function_condition` | PASS | 6 |
| 6 | `stage6_numeric_commands_with_calls` | PASS | 7 |
| 6 | `stage6_function_globals_text_and_file_commands` | PASS | 6 |
| 6 | `stage6_define_function_operands_and_names` | PASS | 6 |
| 6 | `stage6_macro_structural_creation_rejected` | PASS | 28 |
| 6 | `stage6_rem_and_text_modes` | PASS | 12 |
| 6 | `stage6_literal_text_does_not_invoke` | PASS | 6 |
| 6 | `stage6_names_case_sensitive` | PASS | 13 |
| 6 | `stage6_malformed_names_parameters_and_collisions` | PASS | 91 |
| 6 | `stage6_unknown_calls_zero_hid` | PASS | 21 |
| 6 | `stage6_invalid_call_arguments_and_whitespace` | PASS | 35 |
| 6 | `stage6_duplicate_and_nested_declarations` | PASS | 21 |
| 6 | `stage6_unterminated_and_unmatched_functions` | PASS | 28 |
| 6 | `stage6_return_syntax_and_context_errors` | PASS | 21 |
| 6 | `stage6_unused_body_preflight_errors_zero_hid` | PASS | 21 |
| 6 | `stage6_function_table_boundary` | PASS | 13 |
| 6 | `stage6_function_identifier_boundary` | PASS | 13 |
| 6 | `stage6_nested_call_depth_boundary` | PASS | 6 |
| 6 | `stage6_recursive_depth_exhaustion` | PASS | 6 |
| 6 | `stage6_recursive_expression_and_global_visibility` | PASS | 6 |
| 6 | `stage6_shared_control_depth_exhaustion` | PASS | 6 |
| 6 | `stage6_runtime_undefined_initialization` | PASS | 6 |
| 6 | `stage6_runtime_arithmetic_after_calls` | PASS | 12 |
| 6 | `stage6_repeat_history_around_calls` | PASS | 6 |
| 6 | `stage6_stop_active_and_inactive_function_branches` | PASS | 12 |
| 6 | `stage6_cancel_pending_function_delay` | PASS | 6 |
| 6 | `stage6_cancel_nested_function_text` | PASS | 7 |
| 6 | `stage6_cancel_held_keys_in_call` | PASS | 7 |
| 6 | `stage6_cancel_call_under_usb_backpressure` | PASS | 8 |
| 6 | `stage6_cancel_expression_then_clean_run` | PASS | 12 |
| 6 | `stage6_live_ownership_and_stop` | PASS | 7 |
| 6 | `stage6_seek_error_entering_function` | PASS | 5 |
| 6 | `stage6_seek_error_returning_to_caller` | PASS | 6 |
| 6 | `stage6_read_error_and_source_change_in_function` | PASS | 6 |
| 6 | `stage6_runtime_body_read_failure` | PASS | 7 |
| 6 | `stage6_bom_crlf_header_and_final_newline` | PASS | 6 |
| 6 | `stage6_empty_function_loop_stalls` | PASS | 6 |
| 6 | `stage6_total_call_budget` | PASS | 6 |
| 6 | `stage6_postfix_arithmetic_matches_existing_evaluator` | PASS | 39 |
| 6 | `stage6_expression_bounds_and_postfix_errors` | PASS | 11 |
| 6 | `stage6_long_declaration_skip_is_cooperative` | PASS | 11 |
| 6 | `stage6_postfix_call_state_no_heap` | PASS | 60012 |
| 7 | `stage7_empty_blocks` | PASS | 6 |
| 7 | `stage7_single_line_string` | PASS | 6 |
| 7 | `stage7_single_line_stringln` | PASS | 6 |
| 7 | `stage7_string_multiline_no_separators` | PASS | 6 |
| 7 | `stage7_stringln_multiline_enters` | PASS | 7 |
| 7 | `stage7_string_blank_lines` | PASS | 6 |
| 7 | `stage7_stringln_blank_lines` | PASS | 6 |
| 7 | `stage7_string_leading_and_trailing_whitespace` | PASS | 6 |
| 7 | `stage7_stringln_removes_one_leading_tab` | PASS | 6 |
| 7 | `stage7_internal_tabs_preserved` | PASS | 6 |
| 7 | `stage7_literal_command_keywords` | PASS | 6 |
| 7 | `stage7_terminator_prefixes_are_literal` | PASS | 6 |
| 7 | `stage7_case_and_indented_delimiters` | PASS | 6 |
| 7 | `stage7_inline_compatibility_unchanged` | PASS | 6 |
| 7 | `stage7_lf_and_crlf_equivalent` | PASS | 12 |
| 7 | `stage7_bom_only_at_source_start` | PASS | 6 |
| 7 | `stage7_no_final_newline` | PASS | 6 |
| 7 | `stage7_quoted_text_no_unescaping` | PASS | 6 |
| 7 | `stage7_numeric_boolean_and_text_interpolation` | PASS | 6 |
| 7 | `stage7_unknown_host_variables_are_literal` | PASS | 6 |
| 7 | `stage7_variable_replacement_is_single_pass` | PASS | 6 |
| 7 | `stage7_define_hash_and_word_replacement` | PASS | 6 |
| 7 | `stage7_define_body_not_collected_or_expanded` | PASS | 6 |
| 7 | `stage7_define_single_pass_and_variable_order` | PASS | 6 |
| 7 | `stage7_expansion_cannot_close_or_execute` | PASS | 6 |
| 7 | `stage7_value_whitespace_after_source_dedent` | PASS | 6 |
| 7 | `stage7_maximum_body_line` | PASS | 12 |
| 7 | `stage7_overlong_body_zero_hid` | PASS | 7 |
| 7 | `stage7_define_expansion_boundary` | PASS | 13 |
| 7 | `stage7_interpolation_boundary_and_overflow` | PASS | 12 |
| 7 | `stage7_inactive_interpolation_has_no_runtime_effect` | PASS | 6 |
| 7 | `stage7_unterminated_after_output_zero_hid` | PASS | 14 |
| 7 | `stage7_mismatched_or_argument_terminators_zero_hid` | PASS | 21 |
| 7 | `stage7_unmatched_terminators_zero_hid` | PASS | 14 |
| 7 | `stage7_literal_openers_inside_body` | PASS | 6 |
| 7 | `stage7_fixture_spiffs_and_sd` | PASS | 12 |
| 7 | `stage7_if_else_active_inactive_blocks` | PASS | 6 |
| 7 | `stage7_zero_iteration_loop_blocks` | PASS | 6 |
| 7 | `stage7_nested_loops_interpolate_current_values` | PASS | 6 |
| 7 | `stage7_function_repeat_calls_and_return` | PASS | 6 |
| 7 | `stage7_nested_functions_with_blocks` | PASS | 6 |
| 7 | `stage7_recursive_calls_with_blocks` | PASS | 6 |
| 7 | `stage7_repeat_literal_text_and_whitespace` | PASS | 6 |
| 7 | `stage7_repeat_blank_stringln` | PASS | 6 |
| 7 | `stage7_empty_string_does_not_replace_history` | PASS | 6 |
| 7 | `stage7_repeat_interpolates_again` | PASS | 6 |
| 7 | `stage7_default_delays_per_body_line` | PASS | 7 |
| 7 | `stage7_cancel_default_delay` | PASS | 7 |
| 7 | `stage7_cancel_halfway_through_typing` | PASS | 6 |
| 7 | `stage7_cancel_held_shift_and_usb_release_retry` | PASS | 7 |
| 7 | `stage7_usb_backpressure_lossless_and_no_readahead` | PASS | 8 |
| 7 | `stage7_stop_command_after_block` | PASS | 6 |
| 7 | `stage7_live_ownership_and_clean_run` | PASS | 14 |
| 7 | `stage7_live_block_opener_rejected` | PASS | 5 |
| 7 | `stage7_preflight_source_errors_zero_hid` | PASS | 6 |
| 7 | `stage7_rewind_seek_error_zero_hid` | PASS | 6 |
| 7 | `stage7_runtime_body_read_error_spiffs_and_sd` | PASS | 12 |
| 7 | `stage7_runtime_source_change` | PASS | 7 |
| 7 | `stage7_loop_backedge_seek_error` | PASS | 6 |
| 7 | `stage7_function_return_seek_error` | PASS | 7 |
| 7 | `stage7_large_block_streamed_and_cooperative` | PASS | 7 |
| 7 | `stage7_cancel_large_block_preflight` | PASS | 6 |
| 7 | `stage7_source_limits_zero_hid` | PASS | 13 |
| 7 | `stage7_hid_disabled_block_has_no_output` | PASS | 6 |
| 7 | `stage7_malformed_later_control_zero_hid` | PASS | 7 |
| 7 | `stage7_control_nesting_boundaries` | PASS | 26 |
| 7 | `stage7_text_blocks_do_not_execute_calls` | PASS | 6 |
| 7 | `stage7_bounded_line_allocation_probe` | PASS | 40005 |
| 8 | `stage8_f1_f24_reference` | PASS | 346 |
| 8 | `stage8_invalid_f_names` | PASS | 12 |
| 8 | `stage8_navigation_editing_aliases` | PASS | 330 |
| 8 | `stage8_named_punctuation_keys` | PASS | 176 |
| 8 | `stage8_keypad_reference` | PASS | 144 |
| 8 | `stage8_all_modifier_masks` | PASS | 3072 |
| 8 | `stage8_modifier_aliases` | PASS | 110 |
| 8 | `stage8_hyphen_combinations` | PASS | 34 |
| 8 | `stage8_malformed_hyphens_zero_hid` | PASS | 24 |
| 8 | `stage8_case_tabs_and_order` | PASS | 12 |
| 8 | `stage8_modifier_only_release` | PASS | 23 |
| 8 | `stage8_six_key_limit_and_duplicates` | PASS | 15 |
| 8 | `stage8_literal_punctuation_chord_us` | PASS | 15 |
| 8 | `stage8_literal_punctuation_chord_de` | PASS | 27 |
| 8 | `stage8_all_literal_punctuation_chords` | PASS | 797 |
| 8 | `stage8_report_filter_and_raw_modifiers` | PASS | 99 |
| 8 | `stage8_keycode_bounds_zero_hid` | PASS | 12 |
| 8 | `stage8_us_ascii_table` | PASS | 129 |
| 8 | `stage8_de_ascii_table` | PASS | 129 |
| 8 | `stage8_us_ascii_translation` | PASS | 358 |
| 8 | `stage8_de_ascii_translation` | PASS | 360 |
| 8 | `stage8_printable_ascii_runtime_all_locales` | PASS | 1934 |
| 8 | `stage8_de_utf8_reference` | PASS | 89 |
| 8 | `stage8_de_dead_keys` | PASS | 70 |
| 8 | `stage8_locale_registration_and_switching` | PASS | 28 |
| 8 | `stage8_named_keys_are_physical_not_locale_text` | PASS | 17 |
| 8 | `stage8_unsupported_unicode_skip_warning` | PASS | 14 |
| 8 | `stage8_utf8_bounds_and_invalid_sequences` | PASS | 16 |
| 8 | `stage8_no_warn_supported_controls` | PASS | 6 |
| 8 | `stage8_repeat_define_and_stringln_reports` | PASS | 63 |
| 8 | `stage8_multiline_control_function_keyboard` | PASS | 36 |
| 8 | `stage8_queue_refusal_press_and_release` | PASS | 16 |
| 8 | `stage8_disconnect_mid_chord_recovery` | PASS | 15 |
| 8 | `stage8_cancel_held_modifier_all_masks` | PASS | 3060 |
| 8 | `stage8_cancel_release_priority_new_live_command` | PASS | 14 |
| 8 | `stage8_stop_and_runtime_error_release` | PASS | 15 |
| 8 | `stage8_cancel_between_dead_key_strokes` | PASS | 12 |
| 8 | `stage8_storage_fault_after_chord_release` | PASS | 10 |
| 8 | `stage8_hid_disabled_and_live_ownership` | PASS | 15 |
| 8 | `stage8_new_run_no_modifier_leak` | PASS | 11 |
| 8 | `stage8_translation_report_allocation_probe` | PASS | 32001 |
| 10 | `startup_success_truthful` | PASS | 6 |
| 10 | `startup_missing_card` | PASS | 6 |
| 10 | `startup_missing_image_no_create` | PASS | 6 |
| 10 | `startup_wrong_size_no_truncate` | PASS | 22 |
| 10 | `startup_open_failure` | PASS | 4 |
| 10 | `startup_probe_seek_failure` | PASS | 5 |
| 10 | `startup_probe_short_read` | PASS | 4 |
| 10 | `startup_sdk_failure_cleanup` | PASS | 6 |
| 10 | `retry_failed_startup` | PASS | 3 |
| 10 | `repeated_begin_idempotent` | PASS | 3 |
| 10 | `retry_ejected_media` | PASS | 7 |
| 10 | `stale_host_load_after_off` | PASS | 5 |
| 10 | `stale_host_load_after_cancel` | PASS | 5 |
| 10 | `writable_reset_after_end` | PASS | 8 |
| 10 | `read_nonzero_offset` | PASS | 6 |
| 10 | `write_nonzero_offset` | PASS | 7 |
| 10 | `cross_sector_unaligned` | PASS | 6 |
| 10 | `last_byte_and_exact_end` | PASS | 7 |
| 10 | `invalid_range_and_overflow` | PASS | 12 |
| 10 | `zero_length_null` | PASS | 5 |
| 10 | `null_nonzero` | PASS | 5 |
| 10 | `transfer_limit` | PASS | 6 |
| 10 | `read_seek_failure_no_wrong_read` | PASS | 9 |
| 10 | `write_seek_failure_no_wrong_write` | PASS | 9 |
| 10 | `short_read_quarantines` | PASS | 9 |
| 10 | `short_write_prefix_and_quarantine` | PASS | 10 |
| 10 | `card_removal_callback` | PASS | 9 |
| 10 | `card_removal_main_loop` | PASS | 7 |
| 10 | `backing_size_changed` | PASS | 8 |
| 10 | `fault_cleanup_and_explicit_recovery` | PASS | 6 |
| 10 | `eject_load_and_power_stop` | PASS | 9 |
| 10 | `cancel_before_open` | PASS | 3 |
| 10 | `cancel_after_open` | PASS | 3 |
| 10 | `timeout_wrap_safe` | PASS | 6 |
| 10 | `media_absent_until_validated` | PASS | 4 |
| 10 | `script_waits_for_storage` | PASS | 7 |
| 10 | `script_startup_failure_stops_tail` | PASS | 6 |
| 10 | `stop_pending_startup` | PASS | 6 |
| 10 | `stop_preserves_active_media` | PASS | 8 |
| 10 | `live_cli_ownership_while_preparing` | PASS | 9 |
| 10 | `script_and_host_activity` | PASS | 206 |
| 10 | `function_condition_storage_startup` | PASS | 7 |
| 10 | `live_cli_failure_status_and_retry` | PASS | 7 |
| 10 | `callback_lock_contention_busy` | PASS | 6 |
| 10 | `callback_error_storm_no_io` | PASS | 1004 |
| 10 | `concurrent_callback_mode_stop` | PASS | 5 |
| 10 | `sd_adapter_interleaving` | PASS | 7 |
| 10 | `sd_adapter_removal_and_remount` | PASS | 3 |
| 10 | `off_cancels_pending` | PASS | 1 |
| 10 | `repeated_failure_recovery` | PASS | 81 |
| 10 | `no_callback_heap_allocation` | PASS | 5 |
| 10 | `build_without_msc_reports_unavailable` | PASS | 4 |
| 11 | `hold_release_key` | PASS | 13 |
| 11 | `all_eight_persistent_modifiers` | PASS | 104 |
| 11 | `selective_modifier_release` | PASS | 24 |
| 11 | `selective_key_release_order` | PASS | 18 |
| 11 | `idempotent_hold_release` | PASS | 13 |
| 11 | `six_persistent_keys` | PASS | 15 |
| 11 | `seventh_hold_fails_no_drop` | PASS | 14 |
| 11 | `transient_chord_merges_persistent` | PASS | 18 |
| 11 | `all_modifier_masks_merge` | PASS | 2308 |
| 11 | `string_shift_punctuation_enter` | PASS | 24 |
| 11 | `de_altgr_and_dead_key_merge` | PASS | 24 |
| 11 | `held_shift_with_german_spacing` | PASS | 18 |
| 11 | `persistent_duplicate_transient_no_edge` | PASS | 24 |
| 11 | `merged_seventh_transient_fails` | PASS | 10 |
| 11 | `saturated_duplicate_and_modifier_allowed` | PASS | 12 |
| 11 | `raw_modifier_keycode_merges` | PASS | 12 |
| 11 | `inject_mod_inline` | PASS | 12 |
| 11 | `inject_mod_restores_owned` | PASS | 15 |
| 11 | `inject_mod_prefix_reference` | PASS | 18 |
| 11 | `reset_continues_variables` | PASS | 13 |
| 11 | `stop_payload_tail_and_release` | PASS | 10 |
| 11 | `stop_inside_function_loop` | PASS | 12 |
| 11 | `inactive_ownership_commands` | PASS | 8 |
| 11 | `functions_loops_share_ownership` | PASS | 18 |
| 11 | `define_repeat_ownership_and_text` | PASS | 19 |
| 11 | `default_delay_ownership` | PASS | 8 |
| 11 | `eof_releases_owned` | PASS | 9 |
| 11 | `cancel_during_delay` | PASS | 9 |
| 11 | `cancel_during_string` | PASS | 10 |
| 11 | `cancel_dead_key_second_stroke` | PASS | 10 |
| 11 | `runtime_error_releases_owned` | PASS | 9 |
| 11 | `function_depth_error_releases` | PASS | 9 |
| 11 | `loop_budget_error_releases` | PASS | 9 |
| 11 | `storage_read_error_releases` | PASS | 10 |
| 11 | `hold_queue_refusal_no_commit` | PASS | 11 |
| 11 | `release_refusal_clears_logical_owner` | PASS | 13 |
| 11 | `stop_release_refusal_priority` | PASS | 16 |
| 11 | `reset_refusal_waits_before_tail` | PASS | 15 |
| 11 | `disconnect_poll_cancels_owned` | PASS | 13 |
| 11 | `disconnect_event_reconnect_between_ticks` | PASS | 11 |
| 11 | `backpressure_is_not_disconnect` | PASS | 8 |
| 11 | `live_disconnect_clears_idle_hold` | PASS | 10 |
| 11 | `new_script_clears_live_hold` | PASS | 12 |
| 11 | `web_cli_cannot_release_script_hold` | PASS | 9 |
| 11 | `live_holds_survive_commands_until_reset` | PASS | 20 |
| 11 | `new_script_after_cancel_no_leak` | PASS | 10 |
| 11 | `hid_mode_off_releases_owner` | PASS | 12 |
| 11 | `multiline_owned_reports_spiffs_sd` | PASS | 42 |
| 11 | `malformed_hold_zero_hid` | PASS | 35 |
| 11 | `malformed_release_zero_hid` | PASS | 28 |
| 11 | `malformed_inject_mod_zero_hid` | PASS | 28 |
| 11 | `reset_stop_args_zero_hid` | PASS | 14 |
| 11 | `ownership_command_prefixes_rejected` | PASS | 35 |
| 11 | `new_command_function_collisions` | PASS | 35 |
| 11 | `comment_text_literals_not_ownership` | PASS | 7 |
| 11 | `case_tabs_and_modifier_aliases` | PASS | 18 |
| 11 | `direct_report_overflow_null_validation` | PASS | 8 |
| 11 | `repeated_ownership_stress` | PASS | 8005 |
| 11 | `transient_release_refusal_restores_owned` | PASS | 13 |
| 11 | `eof_release_refusal_clears_logical_owner` | PASS | 11 |
| 11 | `cancel_pending_hold_before_acceptance` | PASS | 7 |
| 11 | `disconnect_during_text_cancels_tail` | PASS | 11 |
| 11 | `while_condition_runtime_error_releases` | PASS | 9 |
| 11 | `function_return_seek_error_releases` | PASS | 10 |
| 11 | `source_changed_while_owned_releases` | PASS | 10 |
| 11 | `next_script_after_disconnect_recovery` | PASS | 10 |
| 11 | `atomic_event_callback_no_execution_lock` | PASS | 11 |
| 11 | `implicit_function_return_owner_lifetime` | PASS | 15 |
| 11 | `unsupported_inactive_hold_preflight` | PASS | 7 |
| 11 | `live_stop_payload_releases_idle_hold` | PASS | 9 |
| 11 | `latched_disconnect_blocks_enqueue_before_update` | PASS | 10 |
| 11 | `ownership_allocation_probe` | PASS | 9002 |
| 12 | `initial_unknown_not_false` | PASS | 6 |
| 12 | `all_led_masks_and_padding` | PASS | 288 |
| 12 | `invalid_ids_lengths_null_padding` | PASS | 10 |
| 12 | `actual_keyboard_output_virtual_hook` | PASS | 3 |
| 12 | `actual_keyboard_control_set_report_hook` | PASS | 4 |
| 12 | `duplicates_do_not_count_changes` | PASS | 1003 |
| 12 | `per_key_transition_counters` | PASS | 3 |
| 12 | `first_report_auto_saves_attach_state` | PASS | 8 |
| 12 | `explicit_save_updates_saved_state` | PASS | 9 |
| 12 | `save_unknown_fails_truthfully` | PASS | 5 |
| 12 | `saved_unknown_expression` | PASS | 5 |
| 12 | `readonly_assignment_preflight` | PASS | 3 |
| 12 | `fake_internal_declaration_preflight` | PASS | 3 |
| 12 | `fake_internal_define_alias_preflight` | PASS | 3 |
| 12 | `read_cannot_shadow_internal` | PASS | 3 |
| 12 | `unsupported_read_preflight` | PASS | 3 |
| 12 | `unsupported_write_preflight` | PASS | 3 |
| 12 | `all_native_registry_names_reserved` | PASS | 75 |
| 12 | `os_extension_and_user_variables_preserved` | PASS | 5 |
| 12 | `timeout_extension_assignment_and_limits` | PASS | 6 |
| 12 | `timeout_assignment_expression_shared_evaluator` | PASS | 5 |
| 12 | `constant_invalid_timeout_preflight` | PASS | 3 |
| 12 | `live_wait_stop_cancellable` | PASS | 3 |
| 12 | `timeout_resets_between_scripts` | PASS | 10 |
| 12 | `no_internal_symbol_table_consumption` | PASS | 18 |
| 12 | `canonical_on_off_waits_all_keys` | PASS | 36 |
| 12 | `wait_already_desired_is_immediate` | PASS | 5 |
| 12 | `unknown_off_does_not_succeed` | PASS | 5 |
| 12 | `wait_unknown_becomes_observed_off` | PASS | 6 |
| 12 | `change_unknown_first_report_is_baseline` | PASS | 6 |
| 12 | `change_duplicate_reports_do_not_finish` | PASS | 5 |
| 12 | `rapid_changes_between_ticks_not_lost` | PASS | 5 |
| 12 | `change_all_three_independent` | PASS | 18 |
| 12 | `timeout_wrap_safe` | PASS | 5 |
| 12 | `malformed_lock_command_preflight` | PASS | 3 |
| 12 | `malformed_save_restore_preflight` | PASS | 3 |
| 12 | `lock_commands_function_collision` | PASS | 3 |
| 12 | `inactive_branch_no_wait_or_save` | PASS | 5 |
| 12 | `lock_variables_if_define_function_return` | PASS | 5 |
| 12 | `lock_variables_while_updates` | PASS | 6 |
| 12 | `wait_inside_nested_control_and_function` | PASS | 5 |
| 12 | `numeric_interpolation_observed_state` | PASS | 5 |
| 12 | `unknown_interpolation_runtime_error` | PASS | 5 |
| 12 | `unsupported_interpolation_runtime_error` | PASS | 5 |
| 12 | `restore_noop_no_keyboard_output` | PASS | 5 |
| 12 | `restore_unknown_current_saved_rejected` | PASS | 5 |
| 12 | `restore_requires_hid_enabled` | PASS | 5 |
| 12 | `restore_rejects_held_modifier` | PASS | 5 |
| 12 | `restore_rejects_held_key` | PASS | 5 |
| 12 | `restore_three_keys_ack_exact_reports` | PASS | 51 |
| 12 | `restore_no_ack_times_out_no_retoggle` | PASS | 5 |
| 12 | `restore_wrong_feedback_not_ack` | PASS | 5 |
| 12 | `restore_rechecks_pending_toggle_after_backpressure` | PASS | 24 |
| 12 | `restore_default_delay_after_success` | PASS | 5 |
| 12 | `restore_backpressure_timeout` | PASS | 6 |
| 12 | `stop_cancels_wait_and_releases_hold` | PASS | 4 |
| 12 | `stop_payload_inside_function_preserves_feedback` | PASS | 7 |
| 12 | `reset_preserves_observed_and_saved_state` | PASS | 5 |
| 12 | `runtime_timeout_releases_held_keys` | PASS | 5 |
| 12 | `cancel_restore_during_press` | PASS | 4 |
| 12 | `disconnect_immediate_unknown_and_stale_token` | PASS | 7 |
| 12 | `unmounted_reports_rejected` | PASS | 3 |
| 12 | `disconnect_cancels_wait_and_reconnect_clean` | PASS | 9 |
| 12 | `feedback_survives_separate_script_runs` | PASS | 9 |
| 12 | `live_cli_excluded_during_script_wait` | PASS | 3 |
| 12 | `live_save_restore_state` | PASS | 4 |
| 12 | `wait_command_backpressure_independent` | PASS | 5 |
| 12 | `feedback_during_input_preserves_reports` | PASS | 6 |
| 12 | `callback_does_not_wait_on_executor_lock` | PASS | 2 |
| 12 | `concurrent_feedback_and_snapshot_reads` | PASS | 10001 |
| 12 | `concurrent_disconnect_never_revives_old_session` | PASS | 100 |
| 12 | `transition_counter_crosses_16bit_boundary` | PASS | 65538 |
| 12 | `storage_requested_failed_registry_truthful` | PASS | 8 |
| 12 | `storage_preparing_active_ejected_registry` | PASS | 13 |
| 12 | `storage_retry_and_off_registry` | PASS | 8 |
| 12 | `attackmode_does_not_fabricate_lock_state` | PASS | 5 |
| 12 | `storage_read_error_after_wait_releases_keys` | PASS | 4 |
| 12 | `sd_spiffs_lock_fixture` | PASS | 10 |
| 12 | `saved_state_invalidated_on_backend_begin` | PASS | 1 |
| 12 | `feedback_registry_allocation_probe` | PASS | 50002 |
| 25 | `stage25_reviewed_partition_layout` | PASS | 15 |
| 25 | `stage25_overlapping_partitions_rejected` | PASS | 1 |
| 25 | `stage25_unaligned_application_rejected` | PASS | 1 |
| 25 | `stage25_reviewed_offsets_sizes_flags_enforced` | PASS | 10 |
| 25 | `stage25_core_version_pin_enforced` | PASS | 1 |
| 25 | `stage25_application_size_boundary` | PASS | 3 |
| 25 | `stage25_image_header_configuration_enforced` | PASS | 6 |
| 25 | `stage25_build_configuration_and_app_address_enforced` | PASS | 22 |
| 25 | `stage25_generated_16m_build_artifacts` | PASS | 4 |
| 25 | `stage25_corrupt_partition_binary_rejected` | PASS | 1 |
| 25 | `stage25_merged_image_wrong_address_rejected` | PASS | 1 |
| 25 | `stage25_stale_4m_partition_artifact_rejected` | PASS | 1 |
| 25 | `stage25_saved_physical_flash_capacity_guard` | PASS | 7 |
| 25 | `stage25_offline_source_archives_require_file_migration` | PASS | 11 |
| 25 | `stage25_offline_preparation_rejects_invalid_backups` | PASS | 6 |
| 25 | `stage25_offline_preparation_never_overwrites` | PASS | 2 |
| 25 | `stage25_build_wrapper_requires_clean_output` | PASS | 3 |
| 25 | `stage25_verified_device_map_differs_from_core_default` | PASS | 3 |
| 25 | `stage25_raw_spiffs_size_mismatch_refused` | PASS | 3 |
| 25 | `stage25_recorded_backup_hash_guards` | PASS | 4 |
| 25 | `stage25_file_level_extract_repack_roundtrip` | PASS | 8 |
| 25 | `stage25_file_level_empty_filesystem` | PASS | 1 |
| 25 | `stage25_file_level_capacity_and_overwrite_guards` | PASS | 7 |
| 25 | `stage25_corrupt_or_wrong_geometry_extraction_refused` | PASS | 4 |
| 25 | `stage25_alternative_layout_maximum_equal_slots` | PASS | 4 |
| 25 | `stage25_review_only_plan_preserves_nvs_and_initializes_both_apps` | PASS | 24 |
| 25 | `stage25_write_and_erase_region_guards` | PASS | 13 |
| 25 | `stage25_ota_initializer_selects_app0_deterministically` | PASS | 7 |
| 25 | `stage25_plan_refuses_unverified_files_and_backup_provenance` | PASS | 16 |
| 25 | `stage25_mac_old_core_rejected_before_compile` | PASS | 1 |

Stage9 per-fixture/source observation outcomes and stdout/diagnostics are stored separately in stage12-results.json; all79 match current documented behavior. Unsupported observations are not added to the584 PASS count.

## Remaining validation and next-stage recommendation

Physical USB IN/OUT control/interrupt delivery, host lock synchronization (especially High Sierra), real held-key/restore behavior, disconnect/reconnect release acceptance, task contention/heap/stack and SD/web load remain unverified. Establish ROM recovery/backups and separately approve physical migration before any board work. This stage does not produce a new migration package or authorize one.

For Stage13, follow the Stage9 roadmap’s focused source-compatibility/preprocessing milestone: resolve REM_BLOCK heading syntax, canonical LED aliases, bounded EXTENSION metadata/IF_DEFINED exclusion, and language-string aliases against references. Keep randomization/USB identity/native LED settings as separately reviewed scopes. The upstream OUT-routing/type/empty-buffer limitations also need a separate hardening review before broad lock-feedback host claims. No Stage13 code was started.

**No physical hardware was accessed; no real HID output, flash, erase, formatting, OTA or destructive operation was executed. Stage13 was not begun.**
