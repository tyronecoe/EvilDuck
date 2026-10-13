# Stage28A bounded expression-function continuations report

**GO for isolated offline preview review only. NOT FLASH-AUTHORIZED.**

Baseline: stage27b-duckyscript3-offline commit a570786a932bdf2312061d9a2e6105c0dcb89f3b.
Delivery branch: stage28a-expression-function-continuations. No automatic merge or next milestone.
Stage27A remains the separate owner-controlled hardware track using only frozen Stage26 commit
968c8e0aaf459b0b8b652cc57fe88225894ab64b and its independently reviewed approval process.
Original firmware remains OWNER CONFIRMED — AVAILABLE EXTERNALLY. No search/request/download,
legacy-data preservation requirement, private backup access or owner-file modification occurred.

## Implemented scope

Zero-argument numeric/Boolean function calls now suspend/resume in VAR declarations, assignments,
RETURN expressions, IF/ELSE IF, WHILE conditions and DELAY arguments. Calls combine with the
existing grouping, arithmetic, comparison, logical and bitwise operators. Forward definitions,
standalone calls, functions containing IF/WHILE, nested calls and return-of-call work. No
parameters/local scopes/string returns/dynamic names are invented. Calls are not delegated to
the old EvilDuck interpreter and no proprietary compiler code is used.

The required DOUBLE() fixture evaluates12+5=17 and emits mock math-ok followed by ENTER.
Tests also demonstrate variable capture before a side-effecting call, fresh variable reads after
it, multiple calls without duplicate events, eager FALSE&&F()/TRUE||F(), right-associative power
with left-to-right calls, and WHILE condition calls on every reevaluation including zero iterations.

## Cooperative architecture and safeguards

The original precedence front end optionally emits fixed postfix tokens into one of nine
continuation slots. Each token records its kind/index/value and source column. One tick prepares
a bounded plan, consumes one token, completes one instruction or attempts one event. A call
saves return-PC/numeric-context/column, advances the parent cursor, yields to its body and later
pushes a returned value once. Parent plans are not recompiled or replayed after suspension and
previous variable values remain captured. Callee bodies/RETURN expressions use their own slots.
The same checked arithmetic implementation serves validation and runtime postfix operators.

The shared function-call cap remains8; standalone and expression calls consume the same stack.
Nine slots account for root plus eight functions. Recursion policy is unchanged from Stage27B:
terminating recursion within this cap can succeed, while direct/mutual cycles exceeding it fail
CallLimit; no C++ function-body recursion is used. Loop, instruction, tick and elapsed budgets
remain unchanged, and no caller may raise them. All source/instruction/operand/symbol/function/
constant/token/parser-depth bounds also remain unchanged.

Post-structure preflight uses a bounded per-function CFG walk and a16-bit value-return mask.
Constant-condition edges, including dominating Boolean facts, can prove value returns unreachable.
The postfix still contains eager operands/calls: preflight never executes them or changes their
runtime order. Unknown functions, malformed arity/parentheses and no-reachable-value functions
used numerically reject before any mock events. Mixed value/void paths are intentionally runtime
checks; bare/implicit void fails VoidValue at the caller's source line/column and cannot become0
or reuse a previous return. The analysis is conservative, not a general interprocedural proof of
all-path return or termination. Unused bodies and inactive expressions are still validated.

Cancellation/STOP_PAYLOAD/error drops active continuations, call depth and stale lastReturn;
restart resets globals/call state. Program borrow/revision protection, reentrancy rejection,
callback exception/failure handling, backpressure and uint32 wrap timing remain tested. DELAY
waits once from accepted final delay event. Evaluating its argument now takes cooperative ticks;
this preparation time is not an additional requested DELAY. Earlier pure-literal delay tests were
updated to measure from event acceptance instead of assuming the first tick performs evaluation.

Numeric/Boolean model and engineering edge policies are preserved: uint16, TRUE1/FALSE0,
nonzero truth, checked overflow/underflow/division/modulo/shift/power errors, eager logical
operands and stated precedence. Errors have Program source location, physical line and column
within the expanded operand. Callee failures point within the callee; void-use errors point at
caller tokens. No rollback of already accepted events or callee global side effects is claimed.

## Reference evidence and limits

The Stage27B saved official functions, quick-reference, operators and variables pages were
independently hash-rechecked. Official examples establish function returns inside conditions;
precise unparenthesized order/evaluation effects and implicit-return edge behavior lack an
independent official compiler/runtime oracle. Prior current retrieval returned HTTP403. No
new latest-content, licensed Hak5 firmware or full DuckyScript3.0 compatibility claim is made.
See stage28a-reference-evidence.json and the updated design/compatibility matrix. Eager ordering
and checked arithmetic remain explicitly preview safety decisions, not invented reference facts.

## Exact executed verification

| Fresh suite | PASS groups | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| New expression-function tests | 23 | 0 | 526 |
| Stage27B preview regressions rerun on changed core | 25 | 0 | 2543 |
| **Total** | **48** | **0** | **3069** |

Both suites pass ASan/UBSan with leak detection. The fresh regression suite includes the prior
500 seeded source mutations, not500 separately inflated compatibility passes. Exact cases,
stdout and counts are in stage28a-test-results.md/.json. No old-stage results are added as newly
executed; historical reports/XPASS/XFAIL remain unchanged. Two former expression-call rejection
vectors legitimately moved into positive coverage; their old Stage27B records were preserved.
No unsupported-feature observation is counted as implementation conformance.

Coverage includes every supported operator with call operands; both assignment forms;
forward/nested calls and nested returns; conditional eligibility; loop reevaluation; delay/wrap/
Retry acceptance; static/dynamic void; nonexistent functions/invalid syntax/arity; call-depth
boundary+1, direct/mutual cycles and terminating bounded recursion; token/parser/instruction/
operand/source bounds; source-mapped arithmetic errors; cancellation/STOP during suspension;
called delay cancellation/restart; sink failure/exception, timeout/stuck clock/step exhaustion;
Program borrowing, reentrancy and zero C++ new on the tested compile/evaluate continuation path.
External sink and exception machinery allocation are not covered by that zero-allocation claim.

One initial new budget test failed because its20,000-tick harness cutoff assumed the old
synchronous expression work. It was corrected to assert an explicit200-instruction budget under
the new cooperative model; no production cap was raised. Final executed suites have no failures.
A resource review found an avoidable72-byte operator pointer table; making pointers const moves
it to read-only object storage. No SDK/core pin or sanitizer requirement was weakened.

## Target compilation and measured resources

Pinned Xtensa compiler/object checks PASS using unchanged Arduino3.3.0/ESP-IDF5.5/Stage26 flags,
PSRAM disabled and existing QIO/USB/TinyUSB/CDC/CPU configuration. Original and protected core,
SDK archive/config and compiler identities are verified. Only objects and raw sizeof metadata
are generated, not a firmware ELF/BIN or deployable profile. Source/object/dependency hashes,
commands and stack estimates are in stage28a-target-build.json and source-hashes.json.

| Target type | Stage27B B | Stage28A B | Change B |
|---|---:|---:|---:|
| Program | 6932 | 6932 | 0 |
| Runtime | 184 | 4860 | +4676 |
| Event | 4 | 4 | 0 |
| Instruction | 12 | 12 | 0 |
| Continuation | absent | 516 | 9 fixed slots |
| CallFrame | 2-byte resume PC | 6 | 8 shared frames |
| ExprToken | absent | 6 | 64 per slot |

The4676-byte Runtime increase is exactly9*516 continuation bytes plus8*(6-2) richer call-frame
bytes. It is justified fixed storage, not an increased user budget or dynamic allocation. One
Program+Runtime totals11792B. The value-function mask fits previous Program padding. No new
writable global data/BSS is allocated by the module object.

| Selected object sections | Stage27B B | Stage28A B | Change B |
|---|---:|---:|---:|
| Text | 8068 | 10166 | +2098 |
| Literal | 1396 | 1572 | +176 |
| Read-only data | 1560 | 1680 | +120 |
| Data / BSS | 0 / 0 | 0 / 0 | 0 / 0 |

These selected object sections exclude debug/unwind/linker/dependency effects and are NOT
application flash growth or a new OTA headroom measurement. No preview firmware is linked.
Compiler frames: Program::compile1600B; Compiler::compile432B; valueInventory544B;
statement336B; expression validation112B; recursive compile-time parser64B/frame (max16);
Runtime tick112B; evaluationStep144B. A realistically deep compile chain is roughly3.8KiB
of selected frames before callers/libc/SDK costs; runtime plan preparation roughly1.3KiB,
without multiplying by function-call depth. Callee bodies are not nested C++ evaluation stacks.
These are compiler/source-derived estimates, not full stack proofs or physical high-water.

## Frozen hardware track and next work

All235 protected Stage26 files were rechecked byte-for-byte against their
immutable Git baseline, including bootloader, table, BINs, manifest/hashes, production source, preparation tools,
Stage26 documentation and dependency patch proposals.
Receipt: stage28a-stage26-freeze.json. No production interpreter/storage/HID/USB/Wi-Fi/startup/
partition/migration/recovery or Arduino Micro file changed. Old remote refs are checked after
push. The hardware track cannot substitute a Stage28A object for Stage26 firmware.

Unsupported multiline STRING/aliases, parameterized/local/string-return functions, hardware/
OS/internal variables, HID modifiers, packed injection encoding, attack modes and transport
integration remain explicit gaps. Next recommended incremental coding milestone: bounded mock
multiline STRING/STRINGLN semantics, followed by source-streaming/cooperative compilation and
reviewed armed adapters before real integration. Nothing in that next scope is started here.

**GO: isolated offline preview review only. NO-GO: integration into Stage26, physical flashing,
boot, OTA or real HID under this assignment.** Stage27A remains independently owner-controlled.
No hardware access, stored payload execution, owner-file modifications, global toolchain edits,
physical operation or automatic merge occurred.
