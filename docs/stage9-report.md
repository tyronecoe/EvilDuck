# Stage 9 compatibility audit report

Baseline branch: `stage8-duckyscript-hid-locale`.
Baseline commit: `d59562b7d08ff7833cbe1eddb07c32359138faac`.
Delivery branch: `stage9-duckyscript-compatibility-audit`.

Audit completed against29 current official Hak5 pages,144 inventory records (including38 individually listed internal/extension variables), the actual Stage8 sources/adapters/UI/USB implementation, schematic and prior-stage documents/tests. No production firmware modifications or new runtime features. All163 EvilDuckS3 files match their baseline Git blobs. Micro, prior tests, tools, partitions and migration safeguards unchanged. Stage10 not started.

## Deliverables

* [Full command/behavior matrix](stage9-compatibility-matrix.md), backed by [machine-readable inventory](stage9-compatibility-inventory.json). Every row includes canonical behavior, source location/absence path, status, existing coverage, observation, gap/impact, complexity, priority and reference URL.
* [Reference/source/behavioral analysis](stage9-reference-analysis.md), [official source metadata](stage9-reference-sources.json), [production source hashes](stage9-source-inventory.json).
* [Ranked roadmap and first Stage10 acceptance criteria](stage9-roadmap.md).
* [Harmless fixture library](../tests/stage9/README.md), [fixture manifest](../tests/stage9/fixtures.json) and [exact observed diagnostics/results](stage9-observations.json).
* [Complete baseline test-name/assertion results](stage9-results.json), [clean build log](stage9-build.log), [compiler stack estimates](stage9-stack-results.json).

## Main findings

| Area | Audit conclusion |
|---|---|
| Ordinary variables/expressions/IF/WHILE/functions/text blocks | Implemented with documented bounds; not a proof of all official arithmetic/return/expansion edge behavior. |
| Keyboard injection/layouts | Corrected US/DE and F1–F24 exact bytes remain passing; real host behavior unverified; persistent key commands absent. |
| Canonical comment form | Bare REM_BLOCK works; official REM_BLOCK DOCUMENTATION rejects before any HID. |
| Source compatibility |14 language-specific string aliases, extension wrappers/metadata and compile-time IF_DEFINED family absent. |
| Internal variables |38 reference names inventoried including extension-defined $_OS; native device bindings absent. Explicit VAR can create an inert fake setting. |
| ATTACKMODE | Logical gates/media state do not implement canonical detach/USB personality. Actual failing-MSC probe proves false-success and suppressed retry. |
| MSC callbacks | Source discards nonzero offset and ignores seek/range errors; production callback fault tests still needed.4MiB disk image starts unformatted and creation blocks. |
| Timing/reference discrepancies | Official DELAY minimum20ms differs from preserved0/sub20ms EvilDuck compatibility. Eager logical operands, arithmetic edge policies and implicit value returns lack independent reference confirmation. |
| Hardware-specific features | Button GPIO0 needs post-boot wiring/safety validation; RESET means HID clear. Compiled inject.bin hiding differs from streamed storage; Key Croc MATCH/SAVEKEYS excluded. |

First Stage10 recommendation: truthful and bounded USB-storage operation, with real failure propagation/retry and offset/seek/range fault tests, before adding persistent key ownership or status variables. Roadmap ranks useful official features separately; no compatibility percentage or full DS3 claim.

## Executed verification

All baseline suites actually ran this audit; regression counts intentionally remain independent of new observation cases.

| Suite | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| Stage 1 | 5 | 0 | 127 |
| Stage 2 | 30 | 0 | 791 |
| Stage 25 | 30 | 0 | 190 |
| Stage 3 | 40 | 0 | 13,814 |
| Stage 4 | 42 | 0 | 60,626 |
| Stage 5 | 59 | 0 | 92,019 |
| Stage 6 | 65 | 0 | 60,726 |
| Stage 7 | 68 | 0 | 40,520 |
| Stage 8 | 41 | 0 | 43,666 |
| Diagnostic sanity | — | 0 | 12 |
| **Baseline total** | **380** | **0** | **312,491** |

**Historical diagnostics:5 XPASS,0 XFAIL**, unchanged expectations: `known_nested_if`, `known_canonical_if`, `known_false_while`, `known_f13_mapping`, `known_german_ascii_table`. Underlying supported behavior has separate feature tests; historical XPASS labels were not removed to improve counts. Exact outputs appear in stage9-results.json. No known baseline failures appeared.

New audit library: **39 fixtures ×2 mocked source profiles +1 production attackmode probe =79 observations**, **0 mismatches**, **596 additional observation assertions**. Both mocked SPIFFS and SD produced expected current behavior. These are not79 new compatibility passes. Canonical fixture labels: DIVERGENT=3, EXTENSION=2, GAP=22, SUPPORTED=9, UNRESOLVED=3. GAP remains unsupported; UNRESOLVED has no established reference expectation. Production MSC failure is a confirmed gap, not a working feature.

Combined executed assertion accounting:312,491 baseline +596 observations = **313,087**. Baseline PASS count stays380. No new XFAIL label hides audit gaps; no expected outcomes were silently changed.

ASan/UBSan: Stage1/2/3/4/5/6/7/8 production-runtime mocks, Stage9 fixture executable and production attackmode probe ran with both sanitizers; **0 findings**. Stage2.5 is Python offline validation, not sanitizer-instrumented C++. A preexisting misleading-indentation compiler warning in tests/stage6/test_main.cpp:128 remains; no new warning was fixed by unrelated source edits.

## Clean build and resource verification

| Measurement | This audit | Growth from Stage8 |
|---|---:|---:|
| Compiler program usage |1,308,883 bytes (17%) |0 B |
| Actual application .bin |1,309,024 bytes |0 B |
| StaticRAM |80,408 bytes (24% of327,680) |0 B |
| Compiler RAM remaining for dynamic use |247,272 bytes |0 B |
| Each OTA slot |7,602,176 bytes (0x740000) |0 B |
| Each slot free |6,293,152 bytes /82.780930% |0 B |

Clean build succeeded using Arduino ESP32 core **3.3.0** and the repository wrapper. Application offset0x10000, two unchanged OTA slots; generated image headers/partition invariants and independent slot-size checks passed. PSRAM disabled. FQBN:

```
esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default
```

QIO80MHz build profile retained; ESP image DIO header nibble is the pinned SDK boot convention documented by existing validators, not an unintended4MiB build. The16MiB field and ESP32-S3 chip header were validated. No upload invoked. Application SHA-256: `dd96b4636725e22cd7d41cc95ff00fa3ca4d66ef42fa588cc73b24832fc92929`. Its hash differs from the previous build snapshot although source/size are identical; build timestamps/metadata mean byte-identical rebuilds are not promised.

Compiler stack estimates were rerun for ten runtime/keyboard modules using temporary objects, not firmware replacement. Largest selected frames: enterFunction/returnFunction1,056B each, beginEvaluation1,040B, stop672B, constant expansion592B. These match the unchanged production architecture. Per-function estimates exclude callee/library stack and are not board high-water measurements. Existing allocation probes remain clean in their narrowly scoped paths; docs/fixtures add no firmware buffers, persistent storage or code. String parsing/file/web APIs are not claimed allocation-free. Device heap/fragmentation/task high-water cannot be measured without hardware.

Pinned partition map preserved:

```csv
# EvilDuck S3: verified 16 MiB hardware ONLY. See docs/s3-flash-migration.md.
# Name,   Type, SubType, Offset,   Size,     Flags
nvs,      data, nvs,     0x9000,   0x5000,
otadata,  data, ota,     0xE000,   0x2000,
app0,     app,  ota_0,   0x10000,  0x740000,
app1,     app,  ota_1,   0x750000, 0x740000,
spiffs,   data, spiffs,  0xE90000, 0x160000,
coredump, data, coredump,0xFF0000, 0x10000,
```

Stage2.5 tests revalidated partition/layout/build/image/OTA-initializer/NVS protection and migration mismatch rejection. User-supplied16MiB verification is recorded in existing notes; build report hardware_verified=false means this audit did not independently interrogate hardware. No new migration package, physical write approval, PSRAM enablement or Stage4 backup modification.

## Reproduction (software only)

Install the pinned Arduino core3.3.0/dependencies as described in the existing build instructions. Run commands from this branch. Substitute local tooling paths; there is no port argument.

```sh
python3 tests/stage2/run_tests.py --build-dir /tmp/audit-stage12
python3 tests/stage3/run_tests.py --build-dir /tmp/audit-stage3
python3 tests/stage4/run_tests.py --build-dir /tmp/audit-stage4
python3 tests/stage5/run_tests.py --build-dir /tmp/audit-stage5
python3 tests/stage6/run_tests.py --build-dir /tmp/audit-stage6
python3 tests/stage7/run_tests.py --build-dir /tmp/audit-stage7
python3 tests/stage8/run_tests.py --build-dir /tmp/audit-stage8
python3 tests/stage9/run_tests.py --build-dir /tmp/audit-stage9 --results /tmp/audit-observations.json
python3 tools/build_s3.py --arduino-cli arduino-cli --build-dir /tmp/audit-s3 --jobs 2
python3 tests/stage25/run_tests.py --core-dir /path/to/esp32/3.3.0 --build-dir /tmp/audit-s3
python3 tools/analyze_s3_stack.py --build-dir /tmp/audit-s3 --output /tmp/audit-stack.json
```

Stage2 runner includes the complete five Stage1 tests and the historical diagnostic process. Tests compile actual runtime into RAM-only mocks; they do not send reports to the host USB keyboard. Stage9 README explains the observation versus compatibility distinction.

## Physical work and review boundaries

Outstanding physical evidence: USB enumeration/HID and MSC personalities, real report/release timing and backpressure/disconnect recovery, US/DE characters and AltGr/dead keys on High Sierra10.13.6, lock LED replies, board button/LED channels, SD/SPIFFS faults/concurrent activity, task-stack/heap and migration recovery. Schematic/user flash evidence does not prove these. First host test remains harmless visible TextEdit output after separate authorization.

No hardware accessed; no real HID sent; no destructive command, firmware upload, erase, OTA, format or migration executed. Stage10 not begun. Main and prior stage branches protected. The known Stage4 ZIP and user backups were not altered.

## Created files

* `docs/stage9-build.log`
* `docs/stage9-compatibility-inventory.json`
* `docs/stage9-compatibility-matrix.md`
* `docs/stage9-observations.json`
* `docs/stage9-reference-analysis.md`
* `docs/stage9-reference-sources.json`
* `docs/stage9-report.md`
* `docs/stage9-results.json`
* `docs/stage9-roadmap.md`
* `docs/stage9-source-inventory.json`
* `docs/stage9-stack-results.json`
* `tests/stage9/README.md`
* `tests/stage9/attackmode_probe.cpp`
* `tests/stage9/fixtures.json`
* `tests/stage9/fixtures/basic_text.duck`
* `tests/stage9/fixtures/button_wait.duck`
* `tests/stage9/fixtures/comment_block.duck`
* `tests/stage9/fixtures/conditional_compile.duck`
* `tests/stage9/fixtures/define_command.duck`
* `tests/stage9/fixtures/define_nonrecursive.duck`
* `tests/stage9/fixtures/define_structural.duck`
* `tests/stage9/fixtures/define_words.duck`
* `tests/stage9/fixtures/delay_below_reference_minimum.duck`
* `tests/stage9/fixtures/documented_comment_heading.duck`
* `tests/stage9/fixtures/eager_side_effect.duck`
* `tests/stage9/fixtures/extension_wrapper.duck`
* `tests/stage9/fixtures/hide_payload.duck`
* `tests/stage9/fixtures/hold.duck`
* `tests/stage9/fixtures/implicit_value.duck`
* `tests/stage9/fixtures/inactive_unknown.duck`
* `tests/stage9/fixtures/inert_builtin_declaration.duck`
* `tests/stage9/fixtures/inject_mod.duck`
* `tests/stage9/fixtures/inject_variable.duck`
* `tests/stage9/fixtures/inline_trailing.duck`
* `tests/stage9/fixtures/language_string.duck`
* `tests/stage9/fixtures/led_green.duck`
* `tests/stage9/fixtures/lock_wait.duck`
* `tests/stage9/fixtures/loop_function.duck`
* `tests/stage9/fixtures/multiline_literal.duck`
* `tests/stage9/fixtures/numeric_boolean.duck`
* `tests/stage9/fixtures/random_character.duck`
* `tests/stage9/fixtures/reference_self_assignment.duck`
* `tests/stage9/fixtures/release.duck`
* `tests/stage9/fixtures/reset.duck`
* `tests/stage9/fixtures/restart_payload.duck`
* `tests/stage9/fixtures/save_lock.duck`
* `tests/stage9/fixtures/save_mode.duck`
* `tests/stage9/fixtures/selected_assignment.duck`
* `tests/stage9/fixtures/stop_payload.duck`
* `tests/stage9/fixtures/storage_wait.duck`
* `tests/stage9/fixtures/undefined_builtin.duck`
* `tests/stage9/fixtures/usb_identity.duck`
* `tests/stage9/fixtures/wrap_underflow.duck`
* `tests/stage9/observe.cpp`
* `tests/stage9/run_tests.py`

All changes are audit documentation, source/reference/result inventories and offline fixture/probe tooling. No existing production or prior-stage source file modified. The exact delivery commit is supplied after committing/pushing; this report does not embed its own hash.
