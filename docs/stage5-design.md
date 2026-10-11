# Stage 5: WHILE and mixed conditional control flow

This stage extends the approved Stage 4 source at
`c3e9c34f887015a6c8bcc3146835ebac54432b58`. It does not implement functions,
change expressions, alter partitions or firmware migration procedures, enable
PSRAM, or access a physical device. The Stage 4 migration archive remains a
Stage 4 artifact; compiling Stage 5 does not migrate a device.

## Syntax and reference

The official [Hak5 loops documentation](https://docs.hak5.org/hak5-usb-rubber-ducky/operators-conditions-loops-and-functions/loops)
establishes `WHILE condition` ... `END_WHILE`, evaluation before the first body
entry, and reevaluation at the opening WHILE after every completed iteration.
Parentheses are recommended, not an added THEN delimiter. `WHILE TRUE` is
explicitly documented for infinite loops. No reference hardware/compiler was
used to claim exact Hak5 compatibility beyond those documented semantics.

All numeric conditions use the existing Stage 3 evaluator: unsigned 16-bit
values, zero false/nonzero true, unchanged operators/precedence/errors. Global
variables, DEFINE expansion, and IF / ELSE IF / ELSE semantics are unchanged.
The legacy EvilDuck aliases `ENDWHILE` and `END WHILE`, case-insensitive command
keywords, and bare `$text` WHILE truthiness are retained. A bare numeric variable
uses numeric truth. Parenthesized text or text in numeric expressions remains an
error. No comparison-to-string WHILE extension is added. BREAK, CONTINUE,
functions, FOR, and DO loops remain unsupported. REPEAT remains the existing
previous-command replay extension; it is not a block loop.

## Bounded architecture

A single nonrecursive typed stack holds at most eight **combined** IF/WHILE
frames. Each frame holds parent/branch state, a WHILE header source offset and
line, and progress snapshots. Inactive parents suppress all condition evaluation
and ordinary runtime commands, but their nested delimiters are tracked. An
inactive loop scans forward cooperatively to its matching END_WHILE and pops;
it cannot leave the old global skip flag set.

An active END_WHILE checks progress and seeks to the header. The frame stays on
the stack while the header is reread; reevaluation updates that frame rather than
pushing another. A false condition subsequently skips the final body and pops at
END_WHILE. The streaming Reader records a completed line's start across partial
reads, BOM/CRLF and budget yields, resets read-ahead on seek, and restores source
line diagnostics. Source bytes, loop bodies and ASTs are not cached. The same
256-byte consumed-source and eight-line per-update limits apply on forward scans
and loop back edges, including control-only loops. The 64-byte read-ahead buffer
can perform bounded extra storage reads after a seek; this is not a real-time
latency guarantee for a slow or failing SD device.

Preflight uses the existing typed eight-frame validator. It validates conditions
with the Stage 3 syntax/type resolver in all branches, nesting/terminator order,
unknown symbols, and constant-only expression failures before any HID. It does
not simulate path-dependent variable values; such failures remain runtime
errors. DEFINE expands WHILE operands only, cannot replace literal structural
keywords, and cannot manufacture WHILE or END_WHILE. REM_BLOCK and text block
contents remain literal; Stage 7 text runtime support remains deferred.

Structural markers never enter REPEAT history. Only selected executable commands
do. A loop header/back edge thus preserves the previous selected command. File
seek/read/size failures stop, report source/line, and release runtime-owned keys.
STOP uses the same Stage 1 cancellation/ownership path, including pending output,
delays and deferred USB release. Each new run resets stack, counters and state.

## Explicit EvilDuck safety limits (compatibility decision)

Hak5 permits intentional infinite loops. EvilDuck now enforces two firmware
safety bounds; these are not claimed as canonical language rules:

* `DUCKSCRIPT_MAX_LOOP_ITERATIONS`: 100,000 active WHILE body entries **total per
  script**, including nested/sequential loops. False/inactive headers do not
  consume entries. The last false condition after exactly the limit is allowed.
* `DUCKSCRIPT_MAX_STALLED_ITERATIONS`: 1,024 consecutive completed iterations of
  an individual loop without an actual numeric/text variable change or an
  executed ordinary command. Declaration of a new symbol counts as a change;
  assigning an identical value does not. IF/WHILE/DEFINE/comment/empty structural
  statements do not count as actions. Delays (including zero), replay, file,
  LED/settings and keyboard commands count when dispatched; cooperative command
  completion still gates the next source line.

Exceeding either bound is a diagnosed runtime error, not a silent success.
Bounds are positive, compile-time configurable and checked with static asserts.
These heuristics do not prove mathematical progress. A toggling variable or
side-effect loop can evade the stalled bound but remains subject to the total
bound. A command waiting for USB readiness or a long delay remains cooperatively
cancellable; these loop guards do not introduce a transport/timer timeout.
Changing or resetting a counter in an outer frame cannot mask an unchanged inner
loop. Global variable revisions intentionally permit changes to unrelated globals
to count as progress; this limitation is covered by the total bound.

The unified stack and condition hot path allocate no heap. Existing Arduino
String tokenization, command storage and compatibility text operations still
allocate; this stage does not claim a heap-free entire interpreter or bound the
legacy READ whole-file text extension. Host allocation observation and target
build resource measurements are recorded in the Stage 5 report.

## Verification and remaining scope

Tests use RAM-only SPIFFS/SD, clock, HID and output mocks with ASan/UBSan. They
cover valid/inactive/nested/mixed loops, both boundaries, source markers and
faults, syntax preflight, replay/assignments/DEFINE, timers/keys/STOP, live command
ownership and repeat runs. Existing Stage 2 invalid-structure fixtures now use
WHILE FALSE so an undefined symbol cannot mask the intended structural error;
its seek-fault fixture now targets the header. Stage 4's formerly deferred mixed
structure test is replaced by terminating positive cases in both directions.
The false-WHILE XFAIL can legitimately become XPASS. HID/locale XFAILs remain.

Physical SD seek/removal behavior, USB timing/release retries, web responsiveness
under actual storage latency, heap fragmentation and sustained operation still
require later authorized hardware validation. Nothing in these host tests
verifies a physical migration or asserts full DuckyScript 3.0 compatibility.
