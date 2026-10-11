# Stage 5 host verification

Run from the repository root:

```sh
python3 tests/stage2/run_tests.py --build-dir /tmp/evilduck-host
python3 tests/stage3/run_tests.py --build-dir /tmp/evilduck-host
python3 tests/stage4/run_tests.py --build-dir /tmp/evilduck-host
python3 tests/stage5/run_tests.py --build-dir /tmp/evilduck-host
```

The Stage 2 runner also executes all five Stage 1 regressions and the separate
language diagnostic fixture. Each C++ executable compiles the real interpreter,
parser, evaluator and executor against RAM-only storage, output, HID and clock
mocks with AddressSanitizer/UndefinedBehaviorSanitizer. It opens no hardware.
The Stage 5 allocation probe exercises the actual unified control stack and
Stage 3 numeric evaluator/resolver, instrumenting C++ new/new[]. It does not claim
that the entire String-based interpreter or all C malloc calls allocate nothing.

For a clean compilation and migration-safeguard tests, retain core **3.3.0**:

```sh
python3 tools/build_s3.py --arduino-cli arduino-cli \
  --config-file /path/to/arduino-cli.yaml --build-dir /tmp/evilduck-stage5-16m --jobs 2
python3 tests/stage25/run_tests.py \
  --core-dir /path/to/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /tmp/evilduck-stage5-16m
```

These commands compile and validate offline only. They never migrate hardware.
The unchanged build wrapper selects TinyUSB/USB-OTG (`USBMode=default`), CDC on
boot, QIO/80 MHz, CPU 240 MHz, PSRAM disabled and the custom 16 MiB partition CSV.
Do not substitute a Hardware CDC/JTAG IDE setting for this tested profile.
The original Stage 4 migration archive remains distinct from Stage 5 builds.

There are 58 integration cases in `run_tests.py` and one mixed-stack/evaluator
allocation probe. Coverage includes:

* false/zero/one/many iterations, condition reevaluation and all Stage 3 operators;
* nested loops and mixed IF/ELSE IF/ELSE, inactive side effects and global variables;
* combined depth 8 and rejection at 9, malformed/undefined/text conditions,
  structural/DEFINE protections and zero-HID preflight rejection;
* SPIFFS/SD fixture execution, BOM/CRLF/missing newline/partial line markers,
  fresh-header read failures, seek failure, source size change and closed source;
* REPEAT history, expression delays, modifier reports, active/inactive STOP,
  pending text/delay cancellation, USB pressure, ownership and fresh runs;
* stalled threshold 1,024, variable/action progress, total active body-entry
  threshold 100,000, acceptance at exactly that total, failure before 100,001;
* a 25-case small nested-loop comparison against host-computed results.

Numeric values are directly observed **while the run is alive**; completion,
STOP and errors deliberately clear variables as established in Stage 1.
Ctrl/Alt chords are verified through HID report records, not printable-text
assumptions. The harmless visible nested fixture is embedded in `test_main.cpp`
and runs through both storage namespaces.

Exact executed outcomes, assertion totals, build measurements, remaining XFAILs,
compatibility limitations and the changed-file list are in
[`docs/stage5-report.md`](../../docs/stage5-report.md) and its JSON companion.
