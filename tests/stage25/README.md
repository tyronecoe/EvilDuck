# Stage 2.5: historical executed build and offline validation

**Historical results below used an assumed installed map that differed from the
actual device. The old raw-relocation test is superseded; do not use that workflow.
See [the real-device migration correction](../../docs/s3-migration-correction-results.md)
and [the corrected migration guide](../../docs/s3-flash-migration.md).**

No physical hardware was accessed. No serial port, real USB HID output,
flash write/erase, or filesystem formatting was performed. Stage 3 was not
started. Firmware source behavior and all existing Stage 1/2 test sources were
unchanged. The five existing language XFAILs remain unresolved.

## Reproduce

See [build and migration instructions](../../docs/s3-flash-migration.md). The
tested cloud commands were:

```sh
export XDG_CACHE_HOME=/workspace/tooling/arduino/cache
python3 tools/build_s3.py \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli \
  --config-file /workspace/tooling/arduino/arduino-cli.yaml \
  --build-dir /workspace/tooling/arduino/build/stage25-s3-16m --jobs 2
python3 tests/stage2/run_tests.py \
  --build-dir /workspace/tooling/arduino/build/stage25-host
python3 tests/stage25/run_tests.py \
  --core-dir /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /workspace/tooling/arduino/build/stage25-s3-16m
```

Choose a new empty output directory to repeat the clean firmware build. Arduino
CLI 1.3.1 and ESP32 core 3.3.0 were used. Stage 1/2 C++ tests compile the actual
firmware execution sources with `-fsanitize=address,undefined`, using RAM-only
HID/clock/storage/output mocks. Stage 2.5 tests use Python stdlib, Espressif's
installed partition tooling, actual compiled artifacts and synthetic backups.
ASan/UBSan apply to the C++ suites; Python validation is not sanitizer-instrumented.

## Actual firmware measurements

| Measurement | Stage 2 | Stage 2.5 | Change |
| --- | ---: | ---: | ---: |
| Compiler program storage | 1,284,667 B | 1,284,779 B | +112 B |
| Application `.bin` | 1,284,816 B | 1,284,928 B | +112 B |
| OTA application slot | 1,310,720 B | 7,602,176 B | +6,291,456 B |
| Actual free bytes per slot | 25,904 B | 6,317,248 B | +6,291,344 B |
| Actual free percentage per slot | 1.976% | 83.0979% | |
| Static RAM | 66,256 B | 66,256 B | 0 B |

Compiler maximum program storage was 7,602,176 bytes. Compiler RAM maximum was
327,680 bytes, with 261,424 bytes remaining before runtime allocations. Actual
device heap was not measured. The configuration-only rebuild changed no parser,
HID, SD, EvilDuck command or web-updater code.

Application SHA-256:
`06f3e6b264b85c2875c52c889866aceb5bdaef6b93a1882f285fc0ae525a3a5d`.

Both generated image headers advertise 16 MiB, 80 MHz and ESP32-S3. DIO header
fields match Arduino's QIO boot recipe. Generated partition CSV/binary match the
reviewed table, and merged-image bootloader/table/OTA initializer/application
offsets were verified. The table ends at `0x1000000`. Each OTA slot is
`0x740000`, and the standard application address remains `0x10000`.

## Actual test results

Every listed PASS and XFAIL below was executed. No tests were skipped and no
unexpected failures occurred. There were **52 PASS, 0 FAIL and 5 language XFAIL**,
with **1,032 assertions**, including the 12 diagnostic sanity assertions.

| Suite | PASS | FAIL | XFAIL | Assertions |
| --- | ---: | ---: | ---: | ---: |
| Stage 1 regressions | 5 | 0 | 0 | 127 |
| Stage 1 language diagnostic | 0 | 0 | 5 | 12 sanity checks |
| Stage 2 | 30 | 0 | 0 | 797 |
| Stage 2.5 | 17 | 0 | 0 | 96 |

Stage 1 expected behavior and actual observations:

| Exact name | Expected and actual result | Status | Assertions |
| --- | --- | --- | ---: |
| `supported_commands_and_mock_interfaces` | Supported text, SPIFFS/SD writes, locale/LED/attack mode, key reports and logging verified | PASS | 29 |
| `script_run_state_isolation` | Timing/history/variables/control flags/errors reset; preflight error produces no output | PASS | 22 |
| `cooperative_delay_and_text_cancellation` | Delay/text/queued work cancel; key release, USB backpressure and clock wrap verified; zero blocking delay calls | PASS | 33 |
| `repeat_timing_and_control_loop_yield` | `xxx`, 34ms/33ms report gaps, bounded control-only loop updates | PASS | 24 |
| `live_commands_cannot_mutate_running_script` | Ownership rejects interference, including 100 concurrent submissions; CLI busy/accepted behavior and intact output verified | PASS | 19 |

The separately executed `documented_language_gaps` process completed its 12
sanity checks. Its desired language behavior did not pass:

| Exact diagnostic | Expected | Actual | Status |
| --- | --- | --- | --- |
| `known_nested_if` | `good` | Empty output | XFAIL |
| `known_canonical_if` | `good` | Empty output | XFAIL |
| `known_false_while` | `good` | Empty output | XFAIL |
| `known_f13_mapping` | HID usage 104 | HID usage 70 | XFAIL |
| `known_german_ascii_table` | 128 records | 115 records | XFAIL |

Stage 2 results:

| Exact test name | Status | Assertions |
| --- | --- | ---: |
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

Stage 2.5 results; invalid-input tests pass only when the invalid input is rejected:

| Exact test name | Status | Assertions |
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

ASan, UBSan and leak detection produced no reports in the executed C++ suites.
The offline validator was also run separately against the completed firmware
build and passed. Source inspection confirmed the web updater selects the next
OTA partition and uses its actual size; no updater source changes were needed.

## Remaining physical checks

Verify the individual module's detected flash capacity, actual table, security
state and ROM recovery before authorizing migration. Data relocation/restoration,
NVS preservation, physical SPIFFS/SD operation, coredump capture, USB enumeration,
harmless HID/STOP validation, runtime heap, alternate-slot web OTA, rollback and
power-loss recovery still require physical-device testing. The offline tests
do not claim to establish those results. SPIFFS autoformat and early OTA
acceptance/authentication concerns are documented and intentionally unchanged.
