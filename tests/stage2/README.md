# Stage 2: bounded source reading and structural preflight

Stage 2 is complete. Stage 3 has not started. No hardware was flashed, and no
payload or real HID output was sent to the development host. The older Arduino
Micro firmware is unchanged.

## Reproduce the automated checks

From the repository root:

```sh
python3 tests/stage2/run_tests.py --build-dir /tmp/evilduck-stage2-tests
```

This runs the complete Stage 1 and Stage 2 suites. It uses the existing Python 3
and GNU C++17 compiler, AddressSanitizer, UndefinedBehaviorSanitizer, a separate
process per test, and a 20-second timeout per process. A compilation failure,
failed assertion, sanitizer failure, or timeout makes the runner fail. Generated
build files stay outside the checkout. The Stage 1 runner remains independently
usable. Its shared build function compiles the actual S3 executor, script reader,
parser/validator, variables, key parser, HID backend, locale code, CLI, and log
against the existing RAM-only HID/storage/clock/output mocks. Wi-Fi and actual
SPIFFS/SD/USB drivers are verified by the firmware build, not simulated as
running hardware.

## Implementation

`script_source::Reader` streams the same SPIFFS/SD `File` supplied by the existing
storage interfaces. It retains one fixed line buffer and a 64-byte read-ahead
buffer. It handles LF, CRLF, optional initial UTF-8 BOM, missing final newline,
empty files, and blank lines. The BOM is special only at byte zero. It does not
use `readStringUntil`, its timeout, or whole-file source loading.

Limits are configurable in `config.h`: 512 UTF-8 bytes per physical line
(excluding BOM/line ending), 256 KiB of raw source including BOM/line endings,
8,192 physical lines, and eight control-block frames. Oversized input is rejected
with a diagnostic; it is never truncated. NUL and bare CR are rejected. An exact
maximum-size source/line remains valid. An update consumes at most 256 source
bytes and parses at most eight lines. A cached chunk may read ahead at most 63
extra bytes; there is no unbounded scanning loop. Underlying storage calls remain
synchronous, so their device-specific latency still requires hardware testing.

`Reader` compares the advertised source size and expected read position, verifies
complete chunk reads before that EOF, and verifies every seek/rewind. Read,
position, source-size/unavailable, and seek faults have different diagnostics
from normal EOF. The Arduino `File` API does not expose complete filesystem
errno/metadata-error information; these checks cannot report information that
the driver itself does not expose.

`script_parser` recognizes whole case-insensitive command tokens with space/tab
boundaries. One shared parser serves source preflight, runtime dispatch, and live
commands. It validates supported statement shapes without executing them:
literal delay/repeat counts, existing string VAR/DEFINE assignments, READ,
SAVE/APPEND payload separators, KEYCODE byte/count limits, LOCALE availability,
RGB LED values, ATTACKMODE tokens, STOP arguments, legacy IF conditions, and
variable-only WHILE headers. Numeric literals are bounded; no numeric variables,
constants, expressions, canonical IF evaluation, WHILE expressions, or functions
are implemented. Existing string interpolation and DEFINE's string-assignment
alias remain unchanged.

The lexer has normal, REM_BLOCK, STRING-block, and STRINGLN-block modes. Only
END_REM closes a comment block; its other content is ignored, including fake
control statements or text-block markers. Text-block content is literal: IF,
WHILE, REM_BLOCK, END_IF, END_REM, and unknown commands inside it do not execute
or enter normal statement parsing. Matching END_STRING/END_STRINGLN close text
modes; a mismatched text terminator is an error.

The validator has a fixed stack for IF/WHILE/ELSE structure and checks unmatched,
duplicate, mismatched, and unterminated markers. EOF diagnostics identify the
opening line of unfinished blocks. Diagnostics include the resolved volume/name
and source line; malformed statements also include their offending source text.

`duckscript::run()` reserves the Stage 1 execution session immediately and begins
cooperative preflight. Only after the entire source validates and its rewind
succeeds does execution start on a second streaming pass. Preflight neither
emits HID nor applies VAR, LED, locale, mode, file-write, or timer commands. CLI/
WebSocket STOP can cancel preflight, and live commands remain busy during it.
Runtime reading and control-only loops also yield under the same budgets. WHILE
uses the reader's logical source offset rather than the underlying read-ahead
file position. A seek failure stops safely. Stage 1 text scheduling, repeat
timing, held-key ownership, cancellation, and nonblocking USB transport remain
intact.

Text blocks are structurally recognized, but their execution is explicitly
rejected before HID output with a Stage 7 deferral diagnostic. They are not
silently skipped or partially executed. Balanced nested IF/WHILE blocks are
also recognized, then rejected before output because the current executor still
uses single-level control flags. This stage does not claim nested evaluation.
Structural faults take precedence over these deferred-runtime diagnostics.

## Compatibility changes

* Unknown words and unsupported language statements now produce diagnostics
  instead of accidental typing. REMARK/REMINDER are not REM comments. Use STRING
  to type literal words. Single printable/UTF-8 characters, named keys, and
  recognized modifier/key combinations remain supported. Existing unknown-word
  fallback is retained only for these validated bare characters.
* CLI command words also use complete-token recognition; `stopper` and
  `helpful` are unknown commands, while tab-separated `send` works. STOP takes
  no arguments. Read/status/stop operations and live-command ownership remain
  available through the existing serial/WebSocket CLI.
* Function-key recognition requires a complete numeric suffix. `F1garbage` is
  rejected; `F1 F2` is a key combination rather than the previous accidental
  first-key-only prefix match. The existing incorrect F13–F24 map is not fixed.
* Bare RETURN remains Enter, and CTRL RETURN remains a key combination.
  RETURN arguments are rejected as unsupported function syntax rather than
  typing Enter plus the argument. Standalone script STOP and out-of-band CLI/
  WebSocket STOP retain Stage 1 behavior.
* Recognized malformed statements, negative/overflowing delay/count literals,
  out-of-range RGB/KEYCODE bytes, extra KEYCODE keys, and invalid mode/locale
  tokens are rejected. They no longer silently coerce, wrap, or ignore bad input.
  The full unsigned timer-literal range uses `strtoul` rather than signed
  Arduino `toInt`; this adds no expression or numeric-variable implementation.
* Spaces/tabs work consistently at command boundaries and parameter separators.
  STRING/STRINGLN preserve existing inline payload/interpolation semantics,
  including an extra leading payload space and legacy trailing-line trimming.
  SAVE/APPEND separators recognize the complete STRING token, including mixed
  case, without normalizing their payload text.
* END_IF/END_WHILE and END IF/END WHILE are structural aliases for existing
  single-level control execution. Canonical `IF (...) THEN`, ELSE IF, and WHILE
  expressions are explicitly unsupported rather than incorrectly evaluated.
* Validation covers the entire source, including skipped branches and text after
  STOP. A later detectable syntax/structural error prevents all earlier output.
  This intentionally changes the Stage 1 regression that previously expected
  `B` before `VAR invalid = 3`: it now expects zero HID while retaining the same
  source-line, error-reset, variable, timing, and history-isolation checks.
* A bare STRING/STRINGLN line is reserved as a text-block opener. Its complete
  runtime semantics are deferred to Stage 7; it no longer types its keyword.
  Existing inline STRING and STRINGLN commands remain supported.

There are no firmware dependencies, partition changes, SD caches, dynamically
allocated ASTs, background parser workers, or source-file snapshots added.

## Required fixtures: actual results

The required valid fixture was executed against mocked SPIFFS and SD:

```text
REM ordinary comment
REM_BLOCK
IF this is deliberately not executable
STRINGLN this-must-not-appear
END_REM
STRINGLN parser-ok
```

Actual output: `parser-ok` followed by Enter. PASS on both volumes.

The required malformed fixture was executed:

```text
STRINGLN this-must-not-appear
REM_BLOCK
STRINGLN hidden
END_IF
```

Actual: `sd:invalid.txt: Error at line 2: Unterminated REM_BLOCK`; zero HID presses
and zero visible output, including from the first STRINGLN. PASS. END_IF is
comment content; EOF exposes the unclosed REM_BLOCK.

## Build, flash and physical-flash evidence

Final ESP32-S3 compilation passed with Arduino CLI 1.3.1, ESP32 core 3.3.0, the
existing libraries and FQBN
`esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc`. In this cloud environment:

```sh
export ARDUINO_DIRECTORIES_DATA=/workspace/tooling/arduino/data
export ARDUINO_DIRECTORIES_USER=/workspace/tooling/arduino/user
export ARDUINO_DIRECTORIES_DOWNLOADS=/workspace/tooling/arduino/downloads
export XDG_CACHE_HOME=/workspace/tooling/arduino/cache
/workspace/tooling/arduino/bin/arduino-cli \
  --config-file /workspace/tooling/arduino/arduino-cli.yaml compile --jobs 2 \
  --fqbn esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc \
  --build-path /workspace/tooling/arduino/build/s3 EvilDuckS3
```

| Measurement | Approved Stage 1 | Stage 2 | Growth/change |
| --- | ---: | ---: | ---: |
| Compiler program-storage usage | 1,272,311 B | 1,284,667 B (98%) | +12,356 B |
| Compiler application-slot free space | 38,409 B | 26,053 B | -12,356 B |
| Actual application `.bin` | 1,272,464 B | 1,284,816 B | +12,352 B |
| Actual free space in 1,310,720 B app slot | 38,256 B | 25,904 B (~25.3 KiB) | -12,352 B |
| Static RAM | 65,512 B | 66,256 B | +744 B |

The linker reports 261,424 bytes left for dynamic memory before runtime heap,
task stacks and other allocations. That is not measured free heap. Hardware
heap/fragmentation could not be sampled in the cloud; the existing CLI `ram`
command remains available for hardware checks. Mock ESP heap values are not
reported as physical measurements.

The schematic `Schematic/S3-Schematic.jpg` labels U2 ESP32-S3-WROOM-1U-N16.
`Schematic/EvilDuckS3-BOM.xls`, BOM Report row 24, independently identifies that
same module. N16 specifies **16 MiB physical flash** for the documented design.
The actual connected unit was not interrogated, so this is source-documented
hardware capacity rather than a new device measurement. The existing generic
S3 board configuration defaults to **4 MiB**, and both application and bootloader
image headers advertise 4 MiB. The build's partition CSV confirms:

| Partition | Offset | Size |
| --- | --- | --- |
| nvs | `0x9000` | `0x5000` |
| otadata | `0xE000` | `0x2000` |
| app0 | `0x10000` | `0x140000` (1.25 MiB) |
| app1 | `0x150000` | `0x140000` (1.25 MiB) |
| spiffs | `0x290000` | `0x160000` (1.375 MiB) |
| coredump | `0x3F0000` | `0x10000` |

The table ends at 4 MiB. It does not allocate the additional flash specified by
the N16 module. Stage 2 still fits; no board flash-size option, partition table,
OTA slot allocation, or SPIFFS partition was changed.

## Remaining limits and hardware validation

Known language bugs remain separately XFAIL; missing later-stage features are
not described as supported. Structural validation does not fix false-WHILE
evaluation, locale table contents, key mapping, or later expression/scoping
semantics. Proper constants, numeric variables, functions and text-block runtime
semantics have not been added.

The two-pass validation assumes stable media. Runtime detects size changes,
missing sources, position/read failures and seek failures, but it is not a
snapshot or cryptographic integrity check. Same-size edits between passes or
external MSC writes are not guaranteed to be detected. Coordinate source edits
with STOP; a future storage policy can strengthen this without loading the whole
script into RAM. No SD-backed metadata/cache architecture was introduced.

Limits bound script input and parser metadata, not arbitrary data returned by
legacy READ or the eventual size of interpolated variable values. Storage/LED/
settings operations remain synchronous. Network request buffering belongs to
the existing server; this stage bounds the command admitted to the executor,
not every upstream HTTP allocation.

Physical EvilDuck S3 testing is still required for SPIFFS/SD read and seek fault
behavior, actual SD preflight throughput and STOP latency, serial/WebSocket/HTTP
integration on FreeRTOS, USB enumeration/report delivery/cancellation during
disconnect or backpressure, OS/locale/key combinations, LED and ATTACKMODE/MSC
coexistence, runtime heap/fragmentation, and verification of the shipped module's
actual flash capacity. No such hardware checks are claimed as passed here.

Stage 3 must wait for review. This parser foundation does not automatically
enable constants, numeric variables, expressions or function syntax.

## Exact executed test results

All five Stage 1 and all 30 Stage 2 regression tests were executed: **35 PASS,
0 FAIL, 924 regression assertions**. The diagnostic process executed **12 sanity
assertions**, for **936 total executed assertions**. Five desired-language
checks are **XFAIL** and are not counted as passing language behavior. No tests
were skipped. AddressSanitizer and UndefinedBehaviorSanitizer reported no
findings. The earliest Stage 2 run exposed incomplete punctuation decoding in
the mock and RETURN-argument ambiguity; both were corrected, and the full final
suites were re-executed. CLI boundary checks were included in the final full run.

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

The separate `documented_language_gaps` process completed with 12 sanity
assertions; its language outcomes are:

| Exact diagnostic name | Desired | Actual | Result |
| --- | --- | --- | --- |
| `known_nested_if` | `good` | no output; nested runtime rejected during preflight | XFAIL |
| `known_canonical_if` | `good` | no output; canonical evaluation rejected during preflight | XFAIL |
| `known_false_while` | `good` | empty output; existing skip flag bug persists | XFAIL |
| `known_f13_mapping` | usage 104 (`0x68`) | usage 70 (`0x46`) | XFAIL |
| `known_german_ascii_table` | 128 aligned records | 115 records; content still incorrect | XFAIL |

## Stage 2-only file manifest

| File | Change |
| --- | --- |
| `EvilDuckS3/cli.cpp` | Modified |
| `EvilDuckS3/com.cpp` | Modified |
| `EvilDuckS3/config.h` | Modified |
| `EvilDuckS3/duckscript.cpp` | Modified |
| `EvilDuckS3/hid_backend.cpp` | Modified |
| `EvilDuckS3/keyboard_locale.cpp` | Modified |
| `EvilDuckS3/keyboard_locale.h` | Modified |
| `EvilDuckS3/script_parser.cpp` | Created |
| `EvilDuckS3/script_parser.h` | Created |
| `EvilDuckS3/script_source.cpp` | Created |
| `EvilDuckS3/script_source.h` | Created |
| `tests/stage1/mocks/FS.h` | Modified |
| `tests/stage1/mocks/host.cpp` | Modified |
| `tests/stage1/run_tests.py` | Modified |
| `tests/stage1/test_main.cpp` | Modified |
| `tests/stage2/README.md` | Created |
| `tests/stage2/run_tests.py` | Created |
| `tests/stage2/test_main.cpp` | Created |

All Stage 1 changes are preserved. The review patch is relative to the approved
Stage 1 snapshot, rather than bundling that already-approved work again.
