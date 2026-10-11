# Stage 8 HID and keyboard locales: verified report

Stage 8 is based on approved Stage 7
`68f44b7a7bd1478064b32316fa49a62f68d8527b`, isolated on
`stage8-duckyscript-hid-locale`. GitHub authentication and push permission were
checked. Main, previous stage branches, Arduino Micro, partitions/build profile
and migration safeguards are preserved. No hardware was accessed, no real HID
was sent, no flash/erase/OTA/format operation was performed and Stage 9 was not
started. The original Stage 4 migration ZIP remains byte-for-byte unchanged;
this Stage 8 build is not a migrated-device or migration-package claim.

## Implemented corrections

Reviewed the previous stage contracts/reports/tests, USB HID Usage Tables 1.5
keyboard usage page 0x07, official Hak5 keystroke/holding documentation, Arduino
ESP32 3.3.0 USBHIDKeyboard/TinyUSB descriptor and independent German PC/ISO
xkeyboard-config rows. [Design decisions](stage8-design.md) distinguish evidence
and compatibility changes; [the capability matrix](stage8-keyboard-compatibility.md)
records limitations and physical validation still required.

* F1–F12 retain usages `0x3A`–`0x45`. **F13–F24 now use `0x68`–`0x73`**.
  The previous contiguous formula wrongly assigned F13 PrintScreen's `0x46`.
  Tests execute every F1–F24 mapping and compare exact reports.
* DE's 115-pair table is replaced by exactly **128 indexed ASCII pairs**, with
  correct control slots, printable alignment and DEL. Its incorrectly intended
  `&` mapping is corrected to Shift+7 (`02 24`). US keeps its existing 128-pair
  mappings. Both tables have compile-time size assertions and independent tests
  for every index and every printable runtime character.
* Explicit chord modifiers now accompany locale punctuation/dead-key strokes.
  `CTRL !` produces `{modifier=0x03,key=0x1E}` then zero release, rather than
  releasing Ctrl before typing `!`. Dead-key second strokes preserve the explicit
  chord mask. Normal STRING auto-modifiers remain unchanged.
* Documented hyphen key combinations and `OPTION` as left Alt are supported.
  A single `-` remains a literal. Empty/malformed segments fail preflight.
* Duplicate named keys no longer occupy six-key slots and drop a later key.
  A seventh distinct named key in one report is diagnosed before any script HID.
* Bare `END` and valid END chords now reach the navigation-key mapping. Only
  `END IF` and `END WHILE` are structural aliases. Their nesting/validation stay
  unchanged. Literal parentheses/chords no longer accidentally enter function
  parsing; genuine named invocations keep existing Stage 6 checks.
* Unsupported text retains the compatibility skip policy, now consuming each
  valid UTF-8 scalar as one bounded unit and warning once per text operation.
  Invalid UTF-8 consumes one byte safely. No OS Unicode-entry sequence,
  normalization or broad Unicode support is invented.

All reported usages are on page 0x07. The on-wire keyboard payload is eight bytes:
modifier, reserved zero, six zero-padded key slots; report ID 1 is passed separately.
The combined press report contains modifiers and keys atomically, followed by an
all-zero release after the existing minimum 5 ms dwell. No USB descriptor change
or new dependency is made.

## Compatibility decisions and limits

The incomplete DE table was a known bug, not preserved output behavior. German
text will now generate its intended PC/ISO reports instead of displaced entries.
One Stage 1 assertion specifically expecting ASCII 127 to be skipped by the short
table now expects Delete (`0x4C`); its assertion count is unchanged. Existing
truncated-UTF-8 bounds and cancellation checks remain. Historical diagnostic
names and desired expectations remain intact and independently evaluated.

More-than-six distinct named key groups now reject rather than silently truncate.
Duplicate keys are permitted and do not use extra slots. KEYCODE keeps its
existing at-most-six input bytes and filtering: modifiers E0–E7 fold into the
mask, duplicate keys collapse, zero and >=0xA5 nonmodifier bytes are ignored.
Standalone modifiers, raw KEYCODE and case-insensitive physical bare letter/digit
keys remain EvilDuck extensions. OPTION joins the existing function-name/key-name
collision rule, so a legacy function named OPTION must be renamed.

Locale selection changes the firmware's output map, not the host input source.
US and DE are the only registered locales. DE assumes standard German PC/ISO,
not Apple German, nodeadkeys or deadtilde; right Alt represents AltGr. Existing
spacing ^, grave and acute sequences are retained; standard DE tilde is a single
AltGr+plus stroke. Unicode character support is the finite DE table, not arbitrary
Latin/emoji/CJK. CapsLock/NumLock are not automatically discovered or compensated.

A mixed group of named physical keys and literal locale characters is released
between groups, preserving the prior grouping extension. It is not arbitrary
simultaneous text-character NKRO. HOLD/RELEASE/INJECT_MOD and consumer/media usages
remain unsupported and are listed for the next compatibility audit.

## Scheduling, release and transport

The Stage 1 single-session cooperative scheduler is retained. One text modifier
byte and a one-warning flag use existing session padding: measured static RAM
remains unchanged. Locale translation retains at most two strokes; report storage
is the existing six-key payload, not a growing queue. Token parsing still uses
bounded Strings; no parser engine or whole-text blocking output is introduced.

Accepted press ownership persists until accepted release. The mock now records
exact bytes/instance/ID and can refuse a queue submission independently of USB
readiness. Refused presses/releases retry without duplicate accepted reports.
STOP cancels text, repeats and tail commands, and a pending zero release has
priority over any subsequent script/live press. All nonzero modifier masks were
cancelled during a held key. Script faults and storage failures stop safely and
leave released state; prior ownership/concurrency/control-flow suites still pass.
Source reads and subsequent runtime statements are gated until a chord finishes,
so the storage/arithmetic fault fixtures occur after its accepted release. The
held-key failure path actually exercised is cancellation during blocked release,
not a fabricated simultaneous source-read/runtime fault.

A disconnected physical host cannot receive a release until transport is ready.
Releasing keys cannot undo an already pending host dead-key compose state; the
firmware deliberately sends no unsolicited Escape/other cleanup action. Actual
USB disconnect/re-enumeration/delivery and host behavior remain unverified.

## Executed verification

**380 PASS, 0 FAIL, 5 historical XPASS, 0 XFAIL; 312,491 assertions**, including
12 diagnostic sanity assertions. XPASS is kept separate from passing regression
counts. Stage 8 contributes 40 integration cases plus an allocation probe.

| Suite | PASS | FAIL | Assertions |
| --- | ---: | ---: | ---: |
| Stage 1 | 5 | 0 | 127 |
| Stage 2 | 30 | 0 | 791 |
| Stage 2.5 offline partitions/build/migration | 30 | 0 | 190 |
| Stage 3 | 40 | 0 | 13,814 |
| Stage 4 | 42 | 0 | 60,626 |
| Stage 5 | 59 | 0 | 92,019 |
| Stage 6 | 65 | 0 | 60,726 |
| Stage 7 | 68 | 0 | 40,520 |
| Stage 8 | 41 | 0 | 43,666 |
| Historical diagnostic sanity | separate | 0 | 12 |

All runner exit statuses were zero. ASan/UBSan were enabled and clean for all C++
suites, including allocation probes. Stage 2.5 is Python offline validation, not
sanitizer-instrumented. All interfaces are mocked: no real USB endpoint or serial
port was opened. Existing Stage 6 test_main.cpp:128 misleading-indentation warning
is unchanged; it is not a sanitizer finding. The final firmware compile has no
warnings or errors.

| Original historical diagnostic | Current status | Evidence |
| --- | --- | --- |
| known_nested_if | XPASS | Existing Stage 4 fix |
| known_canonical_if | XPASS | Existing Stage 4 fix |
| known_false_while | XPASS | Existing Stage 5 fix |
| known_f13_mapping | XPASS | Expected/actual 104; all 24 F mappings and runtime reports verified |
| known_german_ascii_table | XPASS | Expected/actual 128; every pair/stroke and runtime printable sequence verified |

No expected outcome was silently relabeled. Zero remaining historical XFAILs does
not mean zero compatibility gaps. Initial development attempts had test-source
compile errors (hex literal spacing and missing FS mock include), two new fixture
failures (real END parser defect and a wrong expected locale-diagnostic spelling)
and the obsolete Stage 1 short-DE-table assertion. They were corrected explicitly;
the complete final rerun, not those attempts, is reported above. The later literal
parenthesis classifier audit has its own exhaustive punctuation regression.

Exact executed names/status/assertion counts follow below and are machine-readable
in [stage8-results.json](stage8-results.json). That report includes build/hash,
per-suite logs' SHA-256/exit statuses, historical observations, baseline comparison,
compiler stack estimates and source snapshot verification.

## Clean firmware compilation and resources

A fresh output directory and `arduino-cli compile --clean` were used via the
repository wrapper with Arduino ESP32 **3.3.0**, ESP32S3 Dev Module, CPU 240 MHz,
QIO/80 MHz, USB-OTG/TinyUSB, CDC enabled, MSC/DFU boot disabled and **PSRAM disabled**.
Arduino CLI 1.3.1, NeoPixel 1.15.5, AsyncTCP 3.5.0 and ESPAsyncWebServer 3.12.1
remain the established toolchain/libraries. Exact FQBN:

```text
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

Partition/layout/image/build/migration tests all passed. Generated application
and bootloader headers describe ESP32-S3 / 16 MiB (the expected SDK DIO header
encoding for this QIO profile). App0 remains `0x10000`; dual slots remain
`0x740000`; all NVS/OTA/SPIFFS/coredump offsets/flags are unchanged. The build
report's hardware_verified=false means the tool interrogated no hardware; it
does not invalidate the owner's earlier physical 16 MiB verification.

| Measurement | Stage 7 | Stage 8 | Change |
| --- | ---: | ---: | ---: |
| Compiler program bytes | 1,307,871 | 1,308,883 | +1,012 |
| Actual app .bin bytes | 1,308,016 | 1,309,024 | +1,008 |
| Static RAM bytes | 80,408 | 80,408 | 0 |
| Free bytes per OTA slot | 6,294,160 | 6,293,152 | -1,008 |
| Free percentage per slot | 82.7942% | 82.7809% | -0.0133 percentage points |

Each OTA slot is 7,602,176 bytes. Compiler nominal remaining RAM is 247,272 of
327,680 bytes, not measured free heap. Final application SHA-256:
`d8356e2c4f61f3736d849e25fe1c91de44f2cd8a75e8864364b6abc30c41874b`.
Binary growth differs slightly from compiler usage because of image alignment.

### Allocation and stack analysis

The Stage 8 probe measured **zero C++ new requests** during 10,000 repeated locale
translation groups and 1,000 report press/release pairs, with host vectors
pre-reserved. Stroke[2] occupies four bytes; keyboard payload occupies eight. No
firmware report queue was added. This does not measure C malloc, embedded heap
watermarks, TinyUSB allocations, command String parsing or warning-log allocation.
Stage 7's separate bounded-line probe remains 50,006 requests / maximum 961 bytes;
working storage does not scale with multiline block length.

The offline stack tool now includes keyboard_locale, duck_keys and hid_backend.
It recompiled ten actual translation units from each preserved Stage 7 and final
Stage 8 build snapshot with GCC -fstack-usage, into temporary objects only. Source
snapshots were verified against the baseline revision/current source. Estimates:

| Function (exclusive compiler frame) | Stage 7 | Stage 8 |
| --- | ---: | ---: |
| keyboard_locale::translate | 32 | 32 |
| hid_backend::queueReport | 64 | 64 |
| duck_keys::next | 80 | 96 |
| com::update | 64 | 64 |
| startText | 32 | 32 |
| startLine | 208 | 208 |
| script_parser::parse | 240 | 240 |

These exclude callee/library costs and do not prove ESP32 task-stack high-water.
An ordinary Keys path through update/next/modifier lookup adds 16 estimated bytes
at next; callback/parser/evaluator stack concerns from previous stages remain.
There is no new recursive HID execution. Eight function/control limits and fixed
call state are unchanged. Physical task-stack/heap measurements remain pending;
no PSRAM was enabled or used.

## Reproduce and changed files

Run from repository root; use your own paths for the already pinned CLI/core:

```sh
python3 tests/stage2/run_tests.py  # includes Stage 1 and historical diagnostics
python3 tests/stage3/run_tests.py
python3 tests/stage4/run_tests.py
python3 tests/stage5/run_tests.py
python3 tests/stage6/run_tests.py
python3 tests/stage7/run_tests.py
python3 tests/stage8/run_tests.py
XDG_CACHE_HOME=/workspace/tooling/arduino/cache python3 tools/build_s3.py \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli \
  --config-file /workspace/tooling/arduino/arduino-cli.yaml \
  --build-dir /workspace/tooling/arduino/build/stage8-final-clean-16m-v2 --jobs 2
python3 tests/stage25/run_tests.py \
  --core-dir /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /workspace/tooling/arduino/build/stage8-final-clean-16m-v2
python3 tools/analyze_s3_stack.py \
  --build-dir /workspace/tooling/arduino/build/stage8-final-clean-16m-v2 \
  --output /tmp/stage8-stack.json
```

Choose a fresh empty build directory for a clean reproduction. These are offline
compile/test commands, not upload/migration instructions.

Modified:

* EvilDuckS3/hid_backend.cpp — discontinuous F-key mapping.
* EvilDuckS3/locale/locale_de.h — complete, indexed DE map and ampersand fix.
* EvilDuckS3/locale/locale_us.h — compile-time US table size invariant.
* EvilDuckS3/locales.cpp — remove obsolete short-DE-table comment.
* EvilDuckS3/keyboard_locale.cpp and .h — bounded unsupported UTF-8 skip contract.
* EvilDuckS3/duck_keys.cpp — punctuation modifier carry, duplicate suppression, OPTION.
* EvilDuckS3/com.cpp — text modifier/warning state through cooperative scheduling.
* EvilDuckS3/script_parser.cpp — safe chords/six-key validation, END and parenthesis fixes.
* tests/stage1/mocks/USBHID.h, host.h, host.cpp — exact accepted payload capture and queue refusal.
* tests/stage1/test_main.cpp — replace known-short-table assertion; retain diagnostic labels.
* tools/analyze_s3_stack.py — include the three HID/keyboard translation units.

Created:

* docs/stage8-design.md, stage8-report.md, stage8-results.json, stage8-keyboard-compatibility.md.
* tests/stage8/README.md, run_tests.py, test_main.cpp, no_alloc.cpp.

## Outstanding work and next review

The keyboard matrix separates supported reports, partial behaviors, unsupported
features, EvilDuck extensions and physical checks. No arbitrary Unicode, host
layout discovery, lock-state compensation, persistent HOLD/RELEASE/INJECT_MOD,
media/NKRO or Mac German profile is claimed. Actual High Sierra TextEdit typing,
modifier releases/timing, disconnect/reconnect, SD/SPIFFS behavior, concurrency
under real storage latency and device heap/task-stack require later authorized
physical tests. Cancellation can leave a host compose state pending even after
keys are released. No simulator proves physical host behavior.

Recommend Stage 9 as a focused official-command compatibility inventory, including
HOLD/RELEASE/lock feedback, internal variables, STRING aliases, extended ATTACKMODE
and uncertain expression/macro boundaries. Separate hardware-inapplicable features
and EvilDuck extensions before selecting further implementations. Stage 9 has not
begun; stop here for Stage 8 review.

## Exact executed test results

| Suite | Exact test name | Result | Assertions |
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
| stage_3 | `stage3_bounded_expression_fuzz` | PASS | 3,001 |
| stage_3 | `stage3_expression_hot_path_no_heap` | PASS | 10,022 |
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
| stage_4 | `stage4_conditional_stack_no_heap` | PASS | 60,012 |
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
| stage_5 | `stage5_mixed_control_stack_no_heap` | PASS | 91,039 |
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
| stage_6 | `stage6_postfix_call_state_no_heap` | PASS | 60,012 |
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
| stage_7 | `stage7_bounded_line_allocation_probe` | PASS | 40,005 |
| stage_8 | `stage8_f1_f24_reference` | PASS | 346 |
| stage_8 | `stage8_invalid_f_names` | PASS | 12 |
| stage_8 | `stage8_navigation_editing_aliases` | PASS | 330 |
| stage_8 | `stage8_named_punctuation_keys` | PASS | 176 |
| stage_8 | `stage8_keypad_reference` | PASS | 144 |
| stage_8 | `stage8_all_modifier_masks` | PASS | 3,072 |
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
| stage_8 | `stage8_printable_ascii_runtime_all_locales` | PASS | 1,934 |
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
| stage_8 | `stage8_cancel_held_modifier_all_masks` | PASS | 3,060 |
| stage_8 | `stage8_cancel_release_priority_new_live_command` | PASS | 14 |
| stage_8 | `stage8_stop_and_runtime_error_release` | PASS | 15 |
| stage_8 | `stage8_cancel_between_dead_key_strokes` | PASS | 12 |
| stage_8 | `stage8_storage_fault_after_chord_release` | PASS | 10 |
| stage_8 | `stage8_hid_disabled_and_live_ownership` | PASS | 15 |
| stage_8 | `stage8_new_run_no_modifier_leak` | PASS | 11 |
| stage_8 | `stage8_translation_report_allocation_probe` | PASS | 32,001 |
