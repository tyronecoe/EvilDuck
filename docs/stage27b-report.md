# Stage27B independent language preview report

**NOT FLASH-AUTHORIZED.** Stage27A remains an independent owner-operated hardware track,
using only Stage26 reviewed controlled-normal-start files/hashes and separate approval.

Baseline: stage26-installation-readiness commit968c8e0aaf459b0b8b652cc57fe88225894ab64b.
Delivery branch: stage27b-duckyscript3-offline. No automatic merge or later stage is started.
Original firmware: OWNER CONFIRMED — AVAILABLE EXTERNALLY. No stock search/request/download,
backup modification or original-data retention requirement was introduced.

## Implemented capability

Original code in language_preview/core.h/.cpp is entirely separate from EvilDuckS3's Arduino
source tree. It has a bounded two-pass preflight/compiler, immutable fixed IR while executing,
a single independent numeric expression evaluator and cooperative runtime. No proprietary
compiler code, external parser library, general scripting framework, AST or dynamically growing
storage is used. The new parser does not reuse legacy bare-command/key fallback semantics.

Implemented and tested:

- Exact REM and REM_BLOCK/END_REM comment recognition; DOCUMENTATION heading supported.
- ASCII single-line STRING/STRINGLN as mock Character events and final ENTER; literal
  command-looking text; LF/CRLF, BOM and missing final newline; no numeric text interpolation.
- DELAY expression/variable events with cooperative clock waits and wrap-safe uint32 deltas.
- Global unsigned16 numeric/Boolean declarations, assignments and VAR redeclarations.
- DEFINE #labels and space-delimited bare labels; bounded, nonrecursive operand expansion.
- Decimal/hex/grouped expressions and all documented binary arithmetic, comparison, logical
  and bitwise operators; ^ is exponentiation. One evaluator serves all numeric consumers.
- IF/ELSE IF/ELSE chains, nested IF and WHILE, zero-iteration and mixed control structures.
- Top-level zero-argument functions, forward standalone calls, nested calls, global access,
  explicit integer/Boolean/void and implicit void returns. Returned values can be inspected
  through the preview API; calls within expressions/conditions are NOT implemented.
- Ten representative named keys as structured mock tap events, never HID reports.
- STOP_PAYLOAD/API cancellation, deterministic error states, retries, sink exception handling,
  no-progress/step/time budgets, call limits, session cleanup and program borrow protection.

The harmless fixture produces ready/middle/ready/complete, each with a mock ENTER. The invalid
fixture rejects before emitting its initial STRINGLN. No host command, credentials, exfiltration,
real HID or stored owner script is executed.

## Reference and deliberate limitations

Requested current Hak5 quick-reference URL and official Markdown alternate returned HTTP403.
The saved official Stage9 quick reference and nine relevant explanatory pages were independently
hash-checked against their recorded HTTPS provenance. Their exact URLs/hashes/retrieval dates
are in stage27b-reference-evidence.json. No claim of current latest content, independent official
compiler equivalence or physical Rubber Ducky reference testing is made. Documentation footer
agent instructions were not used as project instructions; full copyrighted pages were not copied.

Reference establishes uint16 globals, nonzero truth, documented binary operators, parentheses,
THEN, WHILE, zero-argument functions and returns. It does not resolve the full unparenthesized
precedence, eager/short-circuit effects, overflow/underflow or every error edge. This preview uses
explicit TESTED SAFETY POLICIES: checked uint16 arithmetic, eager evaluation, shifts0..15 and
rejection of0^0. Overflow/underflow and zero division/modulo fail rather than wrap. Precedence
and right-associative power are defined in stage27b-design.md; they are not falsely labeled as
independently proved Hak5 edge semantics. Portable fixtures use grouping.

Function expression calls, multiline strings/language aliases, text interpolation, parameters,
internal variables, modifiers/persistent ownership, randomization/jitter, ATTACKMODE, USB identity,
feedback, extensions/conditional preprocessing and other hardware statements remain unsupported
in this NEW core. Legacy firmware functionality remains unchanged. Rejection tests prove safety,
not conformance of missing commands. The144-entry Stage9 audit inventory (including extension/
unestablished rows) is enumerated separately in stage27b-compatibility-matrix.md/.json; it is not
claimed to cover every latest undocumented feature.

Constants do not manufacture structural keywords or identifiers. Global declarations are
collected before validation, but reading a declaration that never executed is a runtime error.
All bodies/inactive branches are preflight-validated. Literal errors fail before execution;
variable-dependent errors stop at their source line without undoing earlier accepted events.
Error codes/messages include physical source line, Program location and operand-relative column.

## Bounds and scheduling

8192 raw source bytes;256-byte physical/expanded lines;4096 stored operand bytes;128 instructions;
32 variables;16 functions;16 constants;23-byte identifiers;63-byte constant values;16 structural
levels;64 expression tokens;16 evaluator frames;8 function call frames;10000 instructions;
100000 ticks;30000 elapsed milliseconds. Step/time budgets may be lowered, not increased.
Large scripts beyond this preview bound are rejected, not truncated or buffered without limit.
Storage-backed cooperative compilation/streaming remains an integration milestone.

One tick performs one instruction or attempts one event. Text emits one ASCII character at a
time. Retry keeps the same pending event without duplicating acceptance; timeouts/tick limits
prevent stalled mocks from retrying forever. The delay begins on accepted delay event. Callback
exceptions become SinkFailure. Callbacks must return promptly; arbitrary blocking external code
cannot be preempted. Reentrant tick/start is rejected; callback cancellation is allowed. Program
cannot be recompiled while active; terminal introspection becomes invalid after recompilation.
Single-threaded API and caller lifetime requirements are explicit. There is no physical held-key
state; a future adapter must implement release separately.

## Actual verification

**25 PASS groups,0 FAIL,2553 assertions. ASan/UBSan and leak detection clean.**
Exact case names, per-case assertions and captured results are in stage27b-test-results.md/.json.
The suite includes every implemented operator, nested control flow, global/function behavior,
preflight zero events, source/table/expression boundary and boundary+1 cases, invalid syntax,
checked arithmetic, cancellation, clock wrap, backpressure, sink failure/exception, reentrancy,
borrow protection, repeated sessions and no-progress budgets. One meaningful safety group runs
500 seeded source mutations; it is not counted as500 independent compatibility features.
A normal compile/evaluate probe counts zero C++ new allocations. Exception machinery/external
sink allocation, libc internals and physical heap behavior are outside that probe.

Actual pinned Xtensa object compilation PASS: original Arduino3.3.0 core identity, compiler hash,
ESP-IDF5.5 NVS archive and QIO_QSPI sdkconfig hashes verified; source compiled using the frozen
Stage26 flags. This is not a full linked preview firmware or an executed Xtensa SDK. The core
references libc and exception/unwind support only, not any USB/storage/device API. Target object
section totals: text8068B, literal1396B, rodata1560B, data0/BSS0. These are object sections, NOT
final application flash growth; linker/dependency effects have not been measured in a preview BIN.

Target storage: Program6932B, Runtime184B, Event4B, Instruction12B (one Program+Runtime7116B).
Compiler temporary data is stack-resident. Largest frame: Program::compile1600B; additional
Compiler::compile432B, statement336B, numeric-validation112B and recursive expression parsing
80B/frame. An indicative deepest compile chain is around4KiB before callers/libc/SDK costs;
this is a conservative source/frame review, not runtime high-water or a complete stack proof.
Runtime tick frame128B plus evaluator/callees; future integration must provision these costs.
No unbounded allocation or embedded persistent report queue is introduced.

No Stage27B firmware image/profile exists. Production source/review artifact bytes are proven
identical to the Stage26 Git commit in stage27b-stage26-freeze.json. Stage26's frozen controlled
BIN1329760B/staticRAM82248B/freeOTA6272416B (82.508166%) and safe BIN1066128B/staticRAM78280B
are historical reviewed measurements, NOT freshly repeated builds. Default firmware compile
inputs and partition/USB profiles are unchanged; the preview is not linked and cannot alter
Stage27A deployment. Source/target/compiler hashes are in stage27b-source-hashes.json and
stage27b-target-build.json. Production installers/manifests were not regenerated.

Initial warnings-as-errors rejected memset on default-initialized typed IR structs; bounded
per-element assignments corrected that before final tests. A target provenance helper initially
looked at the wrong sdkconfig directory; it was corrected to the actual pinned QIO_QSPI path
and failed closed before compilation. Final guarded target check passes; no upstream pin was
changed to hide either resolved development issue.

Historical suites/XPASS/XFAIL/Stage9 observations were not rerun, relabeled or added to totals.
Relevant new preview tests plus target check and baseline byte verification executed. No production
source change requires repeating earlier full firmware/language tests for this isolated milestone.

## Delivery and next incremental milestone

See stage27b-integration-plan.md for actual web/CLI/run/scheduler/storage/HID call sites,
candidate retirement boundaries and a narrow future armed event adapter. No old component is
retired now and no application service is changed. All added files are in stage27b-files.md.

Recommended next software milestone: bounded cooperative function-call continuations inside
expressions/conditions/assignments/RETURN, with explicit void-return and evaluation-order tests.
Then address source streaming/text-block semantics and a separately reviewed mock adapter before
any real transport integration. Do not introduce guessed INJECT_VAR encodings or hardware status.

GO for review of the implemented mock-only subset. Stage27B is NOT FLASH-AUTHORIZED. Stage27A
physical readiness/possible installation is independent and must use Stage26 frozen materials
and its own explicit authorization. No hardware access, flash/erase/format/OTA, real HID, owner
payload/backup access, global toolchain modification or original-firmware search occurred.
