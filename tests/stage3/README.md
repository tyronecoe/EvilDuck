# Stage 3: implementation and executed validation

**Historical stage results:** owner evidence supplied on 2026-10-10 corrected
the installed SPIFFS map. Any old raw-relocation validation listed below used
an assumed map and is superseded by [the migration correction](../../docs/s3-migration-correction-results.md).
Original test results remain recorded; they do not authorize that old workflow.

Stage 3 only is complete. No physical hardware was accessed, flashed, erased,
formatted or sent real HID output. No physical 16 MiB migration was performed.
Stage 4 was not started. The repository's 16 MiB build profile is for compilation;
it does not establish the flash capacity or migration state of an individual unit.

The implementation plan, documentary references, exact operator precedence,
numeric semantics, bounded architecture and compatibility decisions are in
[the Stage 3 implementation contract](../../docs/stage3-design.md).

## Reproduce

The following commands were actually executed successfully in the cloud workspace:

```sh
python3 tests/stage2/run_tests.py \
  --build-dir /workspace/tooling/arduino/build/stage3-host
python3 tests/stage3/run_tests.py \
  --build-dir /workspace/tooling/arduino/build/stage3-host
XDG_CACHE_HOME=/workspace/tooling/arduino/cache python3 tools/build_s3.py \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli \
  --config-file /workspace/tooling/arduino/arduino-cli.yaml \
  --build-dir /workspace/tooling/arduino/build/stage3-final-s3-16m --jobs 2
python3 tests/stage25/run_tests.py \
  --core-dir /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /workspace/tooling/arduino/build/stage3-final-s3-16m
python3 tools/s3_validation.py \
  --core-dir /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /workspace/tooling/arduino/build/stage3-final-s3-16m
```

The Stage 2 runner includes the complete Stage 1 suite. Choose a new empty
firmware output directory when repeating the build; the wrapper performs a clean
build and rejects stale output. Arduino CLI 1.3.1 and ESP32 core **3.3.0** were used.

Exact FQBN, unchanged from Stage 2.5:

```text
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

Final generated configuration and both image headers were validated as ESP32-S3,
16 MiB, 80 MHz; DIO header fields match the existing Arduino QIO boot recipe.
Generated CSV/binary and merged-image offsets match the repository table.
App0 remains at `0x10000`; both OTA slots remain `0x740000`. No partition or build
profile changes were made during Stage 3, and no generated image was uploaded.

## Executed test summary

**92 PASS, 0 FAIL, 5 unresolved language XFAIL; 14,847 assertions**, including
12 diagnostic sanity assertions. All names below were executed; no test was
skipped. A diagnostic process's successful exit does not turn its XFAILs into
passing language tests.

| Suite | PASS | FAIL | XFAIL | Assertions |
| --- | ---: | ---: | ---: | ---: |
| Stage 1 regression | 5 | 0 | 0 | 127 |
| Stage 1 language diagnostic | 0 | 0 | 5 | 12 sanity checks |
| Stage 2 | 30 | 0 | 0 | 797 |
| Stage 2.5 | 17 | 0 | 0 | 96 |
| Stage 3 | 40 | 0 | 0 | 13,815 |

ASan, UBSan and the enabled leak checks produced **no reports** in the executed
C++ suites, including the pure evaluator allocation probe. Python Stage 2.5
validation is not sanitizer-instrumented. Tests use actual execution modules with
RAM-only HID, clock, SPIFFS/SD storage and command-output mocks.

The required fixture ran through both mocked SPIFFS and mocked SD. Actual output
was `ready\nn=9\n`, with an Enter after each STRINGLN. A numeric-only fixture
produced zero HID output and directly verified `x=21`, `yes=1`, `wrap=65535`.
Malformed expressions after an earlier STRINGLN failed preflight with **zero HID
output**. Runtime-only variable arithmetic errors stopped safely, suppressed
subsequent output and released owned keys. STOP during definition collection,
preflight, active delay and text execution, and live-command ownership isolation
were exercised. The pure evaluator/numeric-resolver probe executed 10,020 calls
and observed **zero C++ heap allocations**; bounded fuzz exercised 3,000 inputs.

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

### Unresolved diagnostic results

The separate `documented_language_gaps` process completed 12 sanity assertions.
Its five language defects remain unresolved and were actually observed:

| Exact diagnostic | Expected | Actual | Result |
| --- | --- | --- | --- |
| `known_nested_if` | `good` | Empty output | XFAIL |
| `known_canonical_if` | `good` | Empty output | XFAIL |
| `known_false_while` | `good` | Empty output | XFAIL |
| `known_f13_mapping` | HID usage 104 | HID usage 70 | XFAIL |
| `known_german_ascii_table` | 128 records | 115 records | XFAIL |

## Final clean firmware measurements

| Measurement | Stage 2.5 | Stage 3 | Growth |
| --- | ---: | ---: | ---: |
| Compiler program storage | 1,284,779 B | **1,293,555 B** | +8,776 B |
| Actual application `.bin` | 1,284,928 B | **1,293,696 B** | +8,768 B |
| Static RAM | 66,256 B | **69,880 B** | +3,624 B |
| Free bytes in each OTA slot | 6,317,248 B | **6,308,480 B** | -8,768 B |
| Free percentage in each OTA slot | 83.0979% | **82.9826%** | |

Each slot is 7,602,176 bytes. Compiler RAM maximum is 327,680 bytes; 257,800 bytes
remain before runtime allocations. This number is not a device heap measurement.
Actual application SHA-256:
`1a47938c1e7416dac6a9245fb744d86cf2722427251813baf90c3a1918ad2f11`.

The evaluator has no global scratch storage, AST or dynamic token array. Final
ESP32 compiler stack reports show 80 bytes per recursive evaluator frame and
80 bytes for the evaluator entry. Root plus the configured 16 descents permits
at most 17 recursive frames: 1,440 bytes for these frames plus entry, excluding
callers, resolver and library functions. Constant expansion uses a 513-byte
bounded local buffer; its compiler frame is 592 bytes. These are individual
compiler frame estimates, not a whole-call-stack watermark or proof of hardware
stack margins. Physical stack/heap measurements remain pending.

Final ELF symbol measurements: constants use 2,755 bytes before alignment
(704-byte metadata, 2,048-byte pool, 3-byte counters). Runtime variable storage
uses 833 bytes before alignment (545-byte metadata, 32-byte numbers, 256-byte
String handles). Preflight contains one 545-byte metadata table. Existing text
Strings and READ file contents can allocate dynamically; only the numeric
expression hot path is allocation-free. No new whole-source buffer is retained.

## Changed and created files

Modified:

* `EvilDuckS3/config.h`: explicit expression/symbol/constant/expansion bounds.
* `EvilDuckS3/duck_vars.h`, `EvilDuckS3/duck_vars.cpp`: typed uint16/text globals,
  declarations/assignments, identifier/type validation and bounded interpolation.
* `EvilDuckS3/script_parser.h`, `EvilDuckS3/script_parser.cpp`: statement recognition,
  syntax evaluator integration, bounded preflight symbol metadata and macro modes.
* `EvilDuckS3/duckscript.cpp`: cooperative definition collection, expanded preflight,
  execution preprocessing and reset/cancellation of constants.
* `EvilDuckS3/com.cpp`: typed assignments, shared delay/count expression evaluation,
  checked text expansion and live/script preprocessing ownership.
* `tests/stage1/run_tests.py`: compile the new engine/constant modules into mocks.
* `tests/stage1/test_main.cpp`: quote the text-variable compatibility fixture.
* `tests/stage2/test_main.cpp`: replace a formerly invalid DEFINE fixture now
  made valid by canonical constants with a genuinely malformed definition.

Created:

* `EvilDuckS3/duck_expr.h`, `EvilDuckS3/duck_expr.cpp`: pure bounded evaluator.
* `EvilDuckS3/duck_constants.h`, `EvilDuckS3/duck_constants.cpp`: immutable bounded
  definitions, single-pass expansion and streaming collector.
* `docs/stage3-design.md`: plan, references, semantics and compatibility contract.
* `tests/stage3/test_main.cpp`, `tests/stage3/run_tests.py`: 39 integration/expression
  tests against actual modules and mocked hardware.
* `tests/stage3/no_alloc.cpp`: separate pure evaluator/numeric-resolver heap probe.
* `tests/stage3/README.md`: this executed-results report.

The Arduino Micro firmware is unchanged. Existing HID, locale, LED, SD, filesystem,
web updater, partition table and 16 MiB build tooling were not changed in Stage 3.

## Compatibility and remaining uncertainty

Intentional changes: unquoted text VAR/legacy DEFINE aliases now require quotes;
invalid numeric expressions never fall back to text. Numeric and text variable
types cannot replace each other. Canonical constants are immutable and duplicate
labels are errors. Raw literal-mode delimiters are protected from macros; macros
cannot synthesize DEFINE or comment/text block delimiters. Expansion is bounded.
These changes and their tests are detailed in the implementation contract.
Quoted text retains literal escape bytes; no new escape decoding is introduced.

Retained: quoted text variables and DEFINE-$ aliases, READ-created text,
interpolation of text/decimal numeric values, undefined interpolation as literal,
32-bit plain decimal delay/count compatibility, sub-20ms delays, old IF/WHILE
behavior, cooperative scheduling/STOP, replay history, source streaming and
web/CLI ownership. No canonical IF/WHILE execution was introduced.

Exact Hak5 overflow/underflow, shift-width handling, power associativity, complete
mixed precedence, eager/short-circuit behavior, `0^0`, constant overlap/forward
replacement and duplicate definitions were not conclusively matched against a
reference runtime. Our deterministic choices are documented and tested. Unary
`!`, `~`, unary signs, XOR, `**` and word AND/OR/NOT are rejected because the
consulted operator reference does not establish them. User/device migration is
still unverified; do not upload this 16 MiB build to an unverified installation.

Physical validation still required, after separately authorized flash verification
and migration: USB HID/Enter timing and locale behavior, STOP key release under
real USB backpressure, real SPIFFS/SD read faults and file commands, web/CLI
concurrency, LED/attack modes, runtime heap/stack watermarks, alternate-slot OTA,
NVS/SPIFFS/coredump preservation and recovery. No hardware results are claimed.

Recommended next stage, only after review: reuse this evaluator and preflight
metadata for canonical IF/ELSE IF/ELSE, while retaining bounded streaming and
legacy compatibility tests. That Stage 4 work has not begun.
