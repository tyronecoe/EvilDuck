# Stage 1: isolated, cooperative execution

Run from the repository root:

```sh
python3 tests/stage1/run_tests.py
```

Only Python 3 and an existing `g++` are required. The runner compiles the real
S3 command executor, script loader/control flow, variables, key parser, locale
translator/tables, HID backend, CLI, and script log against the headers in
`mocks/`. No additional firmware dependencies are introduced. The build enables
AddressSanitizer and UndefinedBehaviorSanitizer. GNU C++17 matches the firmware's
use of GNU extensions, including its pre-existing empty US locale arrays.
Build output defaults to a new temporary directory; `--build-dir <path>` selects
a reusable directory outside the checkout. Each test runs in a separate process
with a 20-second timeout; any compilation, assertion, sanitizer, or timeout
failure makes the runner fail.

The fixtures use RAM-only SPIFFS/SD storage, an explicitly advanced `millis()`
clock, recorded keyboard reports/text, recorded LED colors, and a command-output
callback. USB readiness can be withheld to test backpressure and release retry.
No real USB device, serial port, host keyboard, or payload from the repository's
script collection is opened. Only harmless synthetic output fixtures are used.
The mock `delay()` counts calls; tests require zero. A call to the legacy
blocking `Keyboard.print()` fails the test.

## Production changes

`com.cpp` owns one bounded session: command phase, timer remainder, repeat
history/count, text position and up to two locale strokes, one six-key report,
key ownership, and command errors. `duckscript.cpp` resets its `RunState` on each
new run. The existing sixteen-variable table is exclusively owned by this
session, cleared at script start/end, and inaccessible to live commands while
a script owns it. Variable strings are released on clear. No AST, unbounded
command queue, parser dependency, or background worker is added.

`duckscript::update()` reads up to eight skipped/control lines or submits one
executable line. `com::update()` advances one phase, token groups yield after
sixteen tokens, and text translation advances one character at a time. Repeat
execution is iterative. Completion callbacks no longer recursively read the
next line. Timers use unsigned elapsed subtraction, including `millis()` wrap.

Runtime presses and releases use the already-linked TinyUSB endpoint queue,
checking readiness and queue acceptance without waiting for completion. Reports
retain the existing modifiers, six-key cap, duplicate suppression, and raw
modifier-usage handling. A press holds for at least the existing five-millisecond
interval; release waits cooperatively if the endpoint is busy. STOP invalidates
all pending work and queues a priority zero-key release if a runtime key is
held. The main loop services cancellation releases even when execution is idle;
a new press cannot bypass a pending release. Physical delivery of a release
requires a connected, ready USB endpoint.

One recursive execution guard serializes main-loop work, asynchronous web/CLI
submissions, cancellation, status snapshots, and script-log access. Delays and
text never hold the guard while waiting across loop iterations. Legacy public
HID helpers remain available with their original synchronous semantics; runtime
execution does not call them. SPIFFS/SD drivers, web assets, settings, USB
initialization/descriptors, and the Arduino Micro firmware are unchanged.

## Intentional compatibility changes

* Every new script starts with zero default delay, empty repeat history, empty
  variables, fresh control flags, and cleared run errors. Finishing or stopping
  discards the session's pending operations and variables. Idle live commands
  can still share their own state until a script starts or STOP clears it.
* CLI `send`, HTTP `/send`, and HTTP `/run?cmd=...` now acknowledge **Accepted**
  after submission, rather than implying synchronous completion. Timed/keyboard
  work completes through the loop. Command errors are logged. A second live
  command receives a busy response until the first completes. All live Ducky
  commands receive busy while a script owns execution, including gaps between
  its lines. HTTP uses status 409 for busy, 400 for command rejection, and 200
  for acceptance. The shared `executeNow` signature is preserved.
* Starting a script during a pending live operation fails without resetting that
  operation. Existing CLI/WebSocket `stop` remains the out-of-band cancellation
  control and can interrupt a script or live operation.
* Standalone script `STOP` now halts execution; it previously fell through to
  unknown-word literal typing. Use `STRING STOP` to type those letters. A live
  `/send` submission is still subject to the ownership gate, so use CLI/
  WebSocket `stop` to interrupt an active script.
* REPEAT/REPLAY applies the default delay once per repeated keyboard command.
  The prior implementation accidentally applied it twice. With a fake 1ms
  loop and a 20ms default delay, the three `x` reports arrive with gaps of
  34ms and 33ms, including scheduler overhead, rather than a doubled delay.
* Keyboard output is cooperative, so wall-clock typing time includes loop and
  USB readiness overhead. Hosts receive an entire modifier/key report together.
  The logical combinations are unchanged. Latency/performance needs hardware
  validation before setting typing-speed expectations.
* Locale translation checks the remaining input bytes, and locale ASCII reads
  use actual table lengths. The existing DE table contains 115 records but used
  to advertise 128; out-of-range bytes are now skipped rather than reading
  unrelated memory. Its incorrect contents/alignment remain a documented bug.

Whole-line key lookup, permissive number parsing, string trimming, comment
prefix recognition, unknown-word fallback, and existing control-flow syntax are
otherwise retained. These known language limitations are **not** compatibility
requirements for future stages.

## Executed regression tests

| Exact test name | Expected | Actual | Status |
| --- | --- | --- | --- |
| `supported_commands_and_mock_interfaces` | Preserve supported commands through mocks | `Hello`, `OK`, branch/loop text, READ output from both volumes, STRINGLN enter, left/right combinations, KEYCODE, locale/dead-key translation, LED suppression, attack-mode behavior and log verified | PASS |
| `script_run_state_isolation` | Fresh timing/history/variables/errors/control flags on each run | No inherited 100ms delay, no inherited repeat history/variables; invalid VAR stops at line 2 and new run clears error; missing storage error verified | PASS |
| `cooperative_delay_and_text_cancellation` | Yield during waits/text, cancel pending work and release keys | Delay/text/queued live work/default state cancelled, script STOP verified, shifted held key released, USB-busy release retried, unavailable USB resumes losslessly, timer wrap verified; zero blocking delay calls | PASS |
| `repeat_timing_and_control_loop_yield` | Correct repeat count, one default delay, cancellable control loops/repeat | `xxx`, report gaps 34ms/33ms; infinite control-only loop returns from updates; long repeat and active default delay cancel without trailing output | PASS |
| `live_commands_cannot_mutate_running_script` | Reject live interference and serialize callers | Busy before the first line and during delay, blocked VAR/default/text/locale/attack-mode mutations, 100 concurrent rejections, intact `OKOK`, CLI accepted/busy output and live backpressure verified | PASS |

The source of truth is the runner's actual output; result counts are not inferred
from source inspection. The five regression tests executed 127 assertions and passed with no unexpected
failures or sanitizer findings. The separate `documented_language_gaps` process
asserts desirable behavior as diagnostics and labels existing failures XFAIL;
these are not counted as passing language behavior:

| Exact diagnostic name | Desired | Actual | Result |
| --- | --- | --- | --- |
| `known_nested_if` | `good` | `badgood` | XFAIL |
| `known_canonical_if` | `good` with `IF (...) THEN` / `END_IF` | `badENDIF` | XFAIL |
| `known_false_while` | `good` after a false loop | empty output | XFAIL |
| `known_f13_mapping` | HID usage 104 (`0x68`) | 70 (`0x46`) | XFAIL |
| `known_german_ascii_table` | 128 correctly aligned records | 115 records; content still incorrect | XFAIL |

A later fix will produce XPASS rather than a regression failure. Additional
language gaps remain: typed arithmetic/expressions, proper constants, functions,
arguments/returns, lexical scopes, nested block stacks, canonical block markers,
and strict command boundaries. Stage 1 does not claim DuckyScript 3.0 completeness.

## Firmware build and size

Verified with Arduino CLI 1.3.1, ESP32 core 3.3.0, the existing libraries, and:

```sh
arduino-cli compile --jobs 2 \
  --fqbn esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc \
  --build-path /tmp/evilduck-s3-build EvilDuckS3
```

In this cloud workspace the CLI and configuration are at
`/workspace/tooling/arduino/bin/arduino-cli` and
`/workspace/tooling/arduino/arduino-cli.yaml`; pass `--config-file` before
`compile`. The verified environment also sets `ARDUINO_DIRECTORIES_DATA`,
`ARDUINO_DIRECTORIES_USER`, `ARDUINO_DIRECTORIES_DOWNLOADS`, and `XDG_CACHE_HOME`
to their corresponding directories under `/workspace/tooling/arduino`.
No upload/flash operation was performed.

| Measurement | Original baseline | Stage 1 | Change |
| --- | ---: | ---: | ---: |
| CLI program storage | 1,266,683 B | 1,272,311 B | +5,628 B |
| Free of 1,310,720 B application partition | 44,037 B | 38,409 B | -5,628 B |
| Static RAM | 65,376 B | 65,512 B | +136 B |

The final `.ino.bin` is 1,272,464 bytes, leaving **38,256 bytes** in the actual
`0x140000`-byte app slot after image overhead. CLI usage is about 97.07%; the
binary occupies about 97.08%. Both existing OTA app slots retain the same size;
SPIFFS partition allocation is unchanged. Static RAM leaves 262,168 bytes before
runtime heap, task stacks, buffers, and the execution mutex allocation. This is
not a measured free-heap figure. The build passed; other board/core variants
were not claimed as verified.

## Remaining validation and Stage 2 recommendation

Physical hardware validation is still needed for USB enumeration, real report
delivery and release under disconnect/reconnect/suspend or backpressure,
modifier combinations and key rollover on each host OS, typing latency and
locale/dead-key behavior, serial/WebSocket/HTTP races on FreeRTOS, long-running
heap use, SPIFFS and real SD operations/MSC coexistence, and NeoPixel output.
Native tests execute the actual shared command gate and CLI; they do not run
the Wi-Fi/AsyncWebServer/TinyUSB stack. Those production sources compile in the
S3 build but require integration testing on the device.

Storage reads/writes, settings saves, LED driver calls, and parsing/expansion of
one whole input line remain synchronous; scheduling specifically removes delay
and keyboard waits. The existing unbounded line/value allocation and permissive
negative/invalid numeric parsing need later parser/resource-limit work. A USB
endpoint that never becomes ready leaves output waiting cooperatively until
STOP. Files edited or formatted during a run are not snapshotted by Stage 1.

After review, Stage 2 should introduce explicit command boundaries and bounded
line/token/value handling, preserving these five executor regressions. Convert
the relevant diagnostic failures into ordinary passing tests as their owning
language stages implement them. Track binary bytes as well as CLI flash usage;
the remaining app-slot budget is approximately 37.4 KiB. No Stage 2 source
changes are included here.

## Complete repository file manifest

Modified:

| File | Purpose |
| --- | --- |
| `EvilDuckS3/cli.cpp` | Serialize callbacks; report live acceptance/busy errors |
| `EvilDuckS3/com.cpp` | Session ownership, cooperative timers/text/repeat, cancellation, error handling |
| `EvilDuckS3/com.h` | Lifecycle, busy and error APIs; existing signatures retained |
| `EvilDuckS3/duck_keys.cpp` | Incremental bounded token/group traversal |
| `EvilDuckS3/duck_keys.h` | Token cursor and item API |
| `EvilDuckS3/duck_vars.cpp` | Clear variable strings and document session ownership |
| `EvilDuckS3/duckscript.cpp` | Fresh RunState, cooperative bounded loading, STOP and source errors |
| `EvilDuckS3/hid_backend.cpp` | Nonblocking atomic report transport and priority cancellation release |
| `EvilDuckS3/hid_backend.h` | Nonblocking transport API alongside legacy helpers |
| `EvilDuckS3/keyboard_locale.cpp` | Pure bounded character-to-stroke translation |
| `EvilDuckS3/keyboard_locale.h` | Stroke/translation API |
| `EvilDuckS3/locales.cpp` | Actual ASCII table bounds |
| `EvilDuckS3/script_log.cpp` | Serialize log reads/writes |
| `EvilDuckS3/webserver.cpp` | Serialize relevant handlers; acceptance and busy responses |

Created:

| File | Purpose |
| --- | --- |
| `EvilDuckS3/execution_guard.h` | Shared recursive FreeRTOS/native execution guard |
| `tests/stage1/README.md` | Test workflow, results, compatibility/build notes, complete file manifest |
| `tests/stage1/run_tests.py` | Compile real production sources and execute isolated test processes |
| `tests/stage1/test_main.cpp` | Five regression tests and separate known-language-bug diagnostics |
| `tests/stage1/mocks/Arduino.h` | Minimal String, clock and serial APIs |
| `tests/stage1/mocks/FS.h` | Independent RAM file handles with seek/read support |
| `tests/stage1/mocks/USB.h` | USB initialization mock |
| `tests/stage1/mocks/USBHID.h` | Nonblocking HID transport/readiness mock |
| `tests/stage1/mocks/USBHIDKeyboard.h` | Legacy keyboard mock and blocking-print trap |
| `tests/stage1/mocks/host.cpp` | Recorded HID/LED/output, fake clock, SPIFFS/SD and supporting services |
| `tests/stage1/mocks/host.h` | Shared mock fixtures and inspection helpers |
| `tests/stage1/mocks/pgmspace.h` | Native reads of locale table bytes |

All generated binaries, logs and the review patch are outside the checkout.
The older Arduino Micro firmware has no modifications.
