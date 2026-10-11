# Stage 7 streamed multiline text: implementation and verification

Baseline: Stage 6 `b636495a786554afdf3512bee788c6faaa26b229`; branch
`stage7-duckyscript-multiline`. Prior contracts, reports, test fixtures and migration
safeguards were reviewed. No hardware was accessed, no real HID was sent, and no
flash/erase/write/OTA operation was executed. Stage 8 was not started. Main and
Stage 4–6 branches, Micro firmware, custom partitions, pinned build profile and
migration tools are preserved. The original Stage 4 ZIP remains byte-identical.

## Implemented syntax and reference decisions

The official [Hak5 keystroke injection reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection.md)
was reviewed alongside [constants](https://documentation.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/constants.md)
and [variables](https://documentation.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/variables.md).
The decisions were recorded before implementation in `stage7-design.md`.
No physical Hak5 device/reference compiler was executed; complete DuckyScript 3.0
compatibility is not claimed.

```text
STRING
    a
    b
END_STRING
STRINGLN
	line one
	line two
END_STRINGLN
```

The sample emits `abline one` followed by Enter, then `line two` followed by Enter.
The indentation of STRINGLN above is a literal tab. Exact rules implemented:

| Property | STRING block | STRINGLN block |
| --- | --- | --- |
| Leading source whitespace | Remove all initial spaces/tabs | Remove exactly one leading literal tab; preserve spaces |
| Internal/trailing whitespace | Preserve | Preserve |
| Source line boundaries | Join with no inserted separator/Enter | One Enter after each body line |
| Blank/whitespace-only lines | No output after dedentation | Enter, preserving remaining whitespace |
| Immediately closed empty block | No output | No output |
| CRLF/LF | Reader removes source delimiters | Reader removes source delimiters; scheduler supplies Enter |

Formatting is applied before substitutions. This preserves spaces/tabs supplied
by a constant/variable value. Delimiters permit existing surrounding spaces/tabs
and case-insensitive keyword compatibility. Missing/mismatched/unmatched markers
and terminators with arguments still reject preflight before ANY HID.
Text uses lexical mode without consuming a control-stack frame. The obsolete
deferred-runtime depth charge is removed: text at eight nested control blocks
works, while control depth nine still fails preflight with zero HID.

Hak5 says STRINGLN strips the first tab, while rendered examples contain spaces;
one example also closes STRINGLN with END_STRING. We follow explicit prose and
the Stage 2 matching-terminator rule, rather than guessing a four-space indent or
accepting a mismatched marker. Empty-block behavior, substitution order and timing
boundaries are explicit deterministic choices without reference-runtime proof.
Tabs/Enter are HID key events; formatting in a host editor depends on its settings.

## Literal text, DEFINE and interpolation

Every body line becomes a distinct literal text-body kind, not an executable
statement. IF/WHILE/STOP/RETURN/FUNCTION/REM/READ/SAVE and invocation-looking text
are typed as data. Only raw matching END_STRING/END_STRINGLN leaves lexical mode;
expanded values cannot close blocks or invoke commands. REM_BLOCK bodies remain
non-executable and retain their old lexer behavior.

Body text uses existing bounded single-pass DEFINE expansion: # labels anywhere,
bare labels at existing whitespace word boundaries, no recursive rescanning.
DEFINE-looking body lines are data, are not collected as definitions, and retain
DEFINE-line substitution exemption. Unknown labels remain literal. All static
expansion overflows are caught during inventory/preflight, including inactive
branches, before output. No new quote stripping, escapes, expression interpolation
or language-specific STRING aliases are invented.

Known numeric/Boolean and text $variables interpolate using the EvilDuck extension;
unknown identifiers, including host-language $variables, remain literal. Values are
not rescanned. Constants expand before runtime variables. Path-dependent variable
values and interpolation overflows are runtime checks; errors stop safely and
release keys. Canonical numeric-variable declarations/expressions are unchanged.
The official variable page does not establish this arbitrary-text interpolation as
canonical; the extension is preserved explicitly. Whole-file legacy READ can still
allocate large values before interpolation rejects oversized output; Stage 7 does
not claim to repair that separate existing data-storage limitation.

Inline STRING/STRINGLN semantics are unchanged, including existing trimming rules.
The new block submission path preserves body whitespace exactly as specified.
Live/web/CLI commands cannot open a streamed block; they require a script source.

## Cooperative streaming and control flow

The existing reader consumes at most 256 source bytes / eight lines per update,
with its established bounded read-ahead, line and source limits. Each selected
body line is sent through a script-only literal-text API. This bypasses the command
parser and reuses existing variable expansion, locale translation, per-stroke
HID scheduling, release/retry and cancellation. It retains at most one body line;
no whole-block buffer, offsets table or new function/control frames are introduced.
The interpreter reads no next body line while its current output/default delay is
pending. Slow physical storage latency remains outside a hard real-time guarantee.

Active IF/WHILE branches type their body; inactive ones track only lexical mode.
Function definitions are skipped normally, repeated/nested/recursive calls stream
their blocks, and call/loop seeks occur after the text mode has closed. Functions
resembling invocations inside text are not evaluated. Source-read/seek/size failures
and malformed later structures retain source-location diagnostics and safe stopping.
Source content must remain stable; same-size edits are still not fully authenticated.

Default delay applies once after each dispatched body line, equivalent to separate
inline commands. Empty STRING lines emit nothing and do not replace history or add
a delay. Blank STRINGLN lines type Enter, delay, and become repeatable output.
Structural open/close markers do not enter history. A bounded discriminator records
raw literal payload plus Enter mode so REPEAT/REPLAY repeats the last output line,
never parses it as commands, and preserves whitespace. Runtime variables are
interpolated again when replayed, matching the existing inline extension. REPEAT
of a whole block is not invented.

STOP outside a block remains executable; STOP inside text is literal. External
STOP/cancellation clears pending text/delay/replay, calls and source state through
Stage 1 ownership. Held modifiers/keys release, including delayed retry under USB
backpressure. The next script starts clean. No blocking delay() or whole-string
HID output was introduced.

## Executed test results

All C++ suites/probes executed with mocked HID/storage/clocks and ASan/UBSan.
All exited zero with no sanitizer findings. Python partition/migration tests are
not sanitizer-instrumented. No physical device or host HID endpoint was opened.

| Suite | PASS | FAIL | Assertions |
| --- | ---: | ---: | ---: |
| stage 1 | 5 | 0 | 127 |
| stage 2 | 30 | 0 | 791 |
| stage 2 5 | 30 | 0 | 190 |
| stage 3 | 40 | 0 | 13,814 |
| stage 4 | 42 | 0 | 60,626 |
| stage 5 | 59 | 0 | 92,019 |
| stage 6 | 65 | 0 | 60,726 |
| stage 7 | 68 | 0 | 40,520 |
| Diagnostic sanity checks | — | — | 12 |
| Total | 339 | 0 | 268,825 |

Stage 7 contains 67 integration cases plus one bounded-line allocation probe.
A 4,096-line / 65,536-output-character fixture verifies streamed output, and a
separate 10,000-line probe measures line-sized allocations. Tests cover whitespace,
blank lines, raw delimiters, BOM/CRLF/LF/final newline, variables/constants, exact
512-byte boundaries and overflow, source limits, storage faults, both volumes,
USB backpressure, cancellation, delays, replay, and nested IF/WHILE/functions.
Exact names and per-test assertions appear below and in `stage7-results.json`.

The first development run had 65/66 integration passes: the source-limit fixture
incorrectly expected an oversized file to start. The fixture now asserts the
existing open-time rejection and separately checks preflight line-limit rejection;
all final tests pass. No production change was needed for that fixture failure.

Five historical deferred-runtime fixtures in Stage 2–6 now verify literal text
output instead of the removed Stage 7-deferred diagnostic. Their malformed-block
checks are retained. Assertion totals change because those valid cases now use
output assertions rather than invalid-script assertions; this is documented, not
a disabled regression. The Stage 2 test name retains its historical deferred label.

Additional historical diagnostics remain **3 XPASS / 2 XFAIL**, unchanged:

| Name | Result | Investigated behavior |
| --- | --- | --- |
| known_nested_if | XPASS | expected/actual good; Stage 4 fix |
| known_canonical_if | XPASS | expected/actual good; Stage 4 fix |
| known_false_while | XPASS | expected/actual good; Stage 5 fix |
| known_f13_mapping | XFAIL | expected HID usage 104, actual 70; noncontiguous F-key ranges mapped incorrectly |
| known_german_ascii_table | XFAIL | expected 128 records, actual 115; German table content/alignment still incorrect |

No expectations were manipulated to hide these results. A pre-existing GCC
misleading-indentation warning in Stage 6 test_main.cpp:128 is unchanged and also
appears in the Stage 6 baseline log. The clean firmware build has no warnings or
errors; the test-source warning is not a sanitizer finding.

## Clean pinned build and resource comparison

Arduino ESP32 **3.3.0**, ESP32S3 Dev Module, QIO/80 MHz, CPU 240 MHz,
USB-OTG/TinyUSB, CDC enabled, MSC/DFU boot disabled, PSRAM disabled. Exact FQBN:

```text
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

Generated boot/application headers and build properties passed offline validation
for ESP32-S3 and 16 MiB flash (expected SDK DIO header encoding for QIO builds).
Both OTA slots remain 0x740000; app0 remains 0x10000. All NVS/OTA/SPIFFS/coredump
regions and migration guards are unchanged. The offline report's hardware_verified
false means this tool performed no interrogation, not that prior user evidence
was invalidated. Compilation does not imply a physical migration.

| Measurement | Stage 6 | Stage 7 | Change |
| --- | ---: | ---: | ---: |
| Compiler program bytes | 1,307,503 | 1,307,871 | +368 |
| Actual application binary | 1,307,648 | 1,308,016 | +368 |
| Static RAM bytes | 80,408 | 80,408 | 0 |
| Free bytes per OTA slot | 6,294,528 | 6,294,160 | -368 |
| Free percentage per OTA slot | 82.7990% | 82.7942% | -0.0048 percentage points |

Slot size is 7,602,176 bytes. Compiler RAM maximum is 327,680 bytes; nominal
remaining static capacity is 247,272 bytes, not measured runtime free heap.
Application SHA-256: `8e791c641bb31d3f712a9d8be417124a7fbf7e14e35cbe81badde601117ebf9c`.

The scheduler adds four bool discriminators and the validator removes its obsolete
deferred-error fields; measured aggregate static RAM is unchanged. Line/history/text
Strings are reused, and no persistent block/call buffers are added. Existing source
limits remain 512 bytes per raw/expanded line, 256 KiB / 8,192 lines per source.
The host probe observed 50,006 allocation requests across 10,000 lines, maximum
single request 961 bytes; allocations do occur, but request size does not scale
with the block. This measures host std::string-backed mocks, not embedded live-heap
peaks, C malloc usage, fragmentation or library allocations. Call frames remain
976 host bytes / 7,812 bytes for the eight-frame stack, unchanged from Stage 6.

### Embedded task-stack estimates

`tools/analyze_s3_stack.py` recompiled seven actual translation units using the
build compilation database with GCC -fstack-usage, writing temporary objects only.
Its exact records are retained in the JSON report. The same analysis was executed
on preserved Stage 6 build snapshots, verified against the baseline commit. The
listed existing parser/loader/scheduler/call frame estimates are unchanged from
Stage 6; sendText adds a 32-byte helper frame on its new submission path.
Per-function estimates include:

| Function | Compiler frame estimate |
| --- | ---: |
| com::sendText | 32 bytes |
| com::startLine | 208 bytes |
| com::update | 64 bytes |
| duckscript::update | 128 bytes |
| loadNextLine | 176 bytes |
| Lexer::scan | 288 bytes |
| duck_constants::expand | 592 bytes |
| duck_vars::expand | 96 bytes |
| enterFunction / returnFunction | 1,056 bytes each |
| expression parser recursive frame | 80 bytes |

A selected text-read call chain contributes approximately 1,184 bytes from the
measured update/load/lexer/constant-expansion frames alone; output startup contributes
approximately 368 bytes from update/startLine/variable-expansion frames alone.
These are partial estimates, excluding Arduino Strings, libraries, error paths,
outer loop/framework frames and interrupts. The bounded expression parser still
has depth 16, contributing roughly 1.4 KiB of recursive frames at its boundary;
script function recursion is cooperative and does not multiply native C++ call
frames by call depth. Configuration specifies an 8,192-byte Arduino loop task
stack (separate ESP main-task setting 4,096). Do not reduce it based on partial
estimates; actual high-water and fragmentation require physical validation.

Memory opportunities: reuse line-expansion scratch buffers to reduce transient
String copies; investigate compact suspended-expression storage to reduce existing
fixed call-state RAM; separately bound/stream legacy READ data. None was pulled
into Stage 7 merely to optimize resources, and all require regression coverage.

## Reproduction and changed files

Offline commands; no hardware needed:

```sh
python3 tests/stage2/run_tests.py
python3 tests/stage3/run_tests.py
python3 tests/stage4/run_tests.py
python3 tests/stage5/run_tests.py
python3 tests/stage6/run_tests.py
python3 tests/stage7/run_tests.py
python3 tools/build_s3.py --build-dir /tmp/evilduck-stage7-clean --jobs 2
python3 tests/stage25/run_tests.py --core-dir /path/to/esp32/3.3.0 --build-dir /tmp/evilduck-stage7-clean
python3 tools/analyze_s3_stack.py --build-dir /tmp/evilduck-stage7-clean --output /tmp/stage7-stack.json
```

Stage 2's runner includes Stage 1 and historical diagnostics. Build output must be
empty and core 3.3.0 installed; --arduino-cli/--config-file may select its installation.
The stack tool is offline compilation only and compatible with Python 3.8+.

Modified: EvilDuckS3/com.cpp, com.h, duckscript.cpp, script_parser.cpp,
script_parser.h; tests/stage2/test_main.cpp, tests/stage3/test_main.cpp,
tests/stage4/test_main.cpp, tests/stage5/test_main.cpp, tests/stage6/test_main.cpp.
Created: docs/stage7-design.md, docs/stage7-report.md, docs/stage7-results.json;
tests/stage7/README.md, test_main.cpp, run_tests.py, bounded_text.cpp;
tools/analyze_s3_stack.py. All other firmware, build and migration files are unchanged.

## Remaining gaps and recommended Stage 8

Highest-priority Stage 8 work: correct and validate F13–F24 HID mappings and German
locale tables, then audit modifier combinations, locale/dead-key/unicode behavior,
release/backpressure and host-specific report interpretation. Resolve diagnostic
labels only when underlying behavior is proven fixed. Do not claim full language
compatibility. Documented language-specific text-block aliases, internal Hak5
variables/commands and compiler edge equivalence remain additional gaps.

Physical validation is pending for tabs/Enter in editors, USB enumeration/reports,
held-key release under disconnect/backpressure, real SD/SPIFFS seeks/read faults,
web/CLI concurrency and responsiveness under storage latency, and heap/task-stack
high-water. No hardware access or migration occurred, and Stage 8 was not begun.

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
