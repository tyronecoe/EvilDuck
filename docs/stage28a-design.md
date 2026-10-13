# Stage28A expression continuation contract

GO for offline preview review only. NOT FLASH-AUTHORIZED. Stage27A remains separate and uses
only frozen Stage26 files from968c8e0aaf459b0b8b652cc57fe88225894ab64b.

## Representation and execution

The original Stage27B precedence front end now emits bounded postfix plans into a continuation
slot. It still handles grouping/validation/constant folding; the same checked operator routine
serves both validation and runtime operations. No new parser, dynamic AST or proprietary compiler
source is introduced. Program retains its4096-byte text/operand arena and128-instruction IR.

An ExprToken holds a kind, value/function/symbol/operator index and operand-relative column.
A Continuation stores64 tokens,64 uint16 values and length/cursor/stack/active counters. Nine
slots represent the top-level numeric instruction plus at most eight called-function levels.
A six-byte CallFrame records resume-PC, call column and numeric-value requirement. Standalone
and value calls share the SAME eight-frame budget; they cannot each claim eight extra frames.

When a numeric instruction begins, its plan is prepared once (bounded64 lexical tokens and
16 parser frames), then later ticks consume one postfix token or complete the instruction.
Literal/variable operands are captured when consumed. A Call token advances its cursor, saves
the calling PC and yields to the function body. No function body executes synchronously inside
Expression. Its RETURN expression can suspend in its own slot. A returned value is pushed once
into the saved parent stack; evaluation resumes at the next token, without reparsing the parent,
replaying accepted events or rereading earlier variables. Function bodies may use IF/WHILE,
other standalone/value calls, text and delays.

All function operands execute left-to-right even for right-associative power. Logical operators
remain eager: FALSE && F() and TRUE || F() still execute F() in an eligible expression. Inactive
IF regions and ineligible ELSE IF conditions jump over their expressions and make no calls.
WHILE starts a fresh plan on each condition reevaluation. These order/edge choices preserve the
Stage27B preview policy; the official reference does not establish every side-effect ordering rule.

One tick prepares a bounded plan, consumes one token, transitions one instruction, or attempts
one event. It never runs a whole called function. Postfix operator work is bounded; exponentiation
uses at most16 iterations. Accepted event retries/ownership remain unchanged. DELAY has one
clock owner in Runtime: its requested interval starts only after the final computed delay event
is accepted. Calculation/callee work is not silently added to the requested delay; callee delay
statements are separate delays. Computing even a literal now takes several preview ticks, so
old tests use acceptance time rather than assuming DELAY starts on the first tick.

## Value/void validation

After structural compilation, a bounded per-function CFG walk inspects reachable RETURN nodes.
It follows both dynamic IF edges, known constant-condition edges (including dominating FALSE/TRUE logical facts) only, and loop jumps; Return,
END_FUNCTION and STOP_PAYLOAD terminate paths. It never executes a function or mutates globals. Logical truth facts only guide this CFG walk; emitted postfix always retains both eager operands and all calls.
A16-bit Program mask records functions with a structurally reachable value-return path. This
fits existing Program padding; there is no Program-size growth. All numeric call contexts are
then revalidated, including unused function bodies and inactive branches.

A missing function or nonzero/malformed argument list fails preflight. A function with no
reachable value return fails VoidValue in numeric context, including unreachable value RETURN
after bare RETURN or constant-false branch. Mixed value/void bodies remain allowed because the
selected runtime path may be valid. If that path reaches bare RETURN or implicit END_FUNCTION,
Runtime restores the caller's PC and fails VoidValue at the call column. Void never becomes0,
never consumes an old lastReturn and never initializes an assignment destination. Standalone
calls continue to permit void. The CFG walk is conservative, not a general proof of termination
or data-dependent all-path return coverage. Transitive void return expressions are also checked.

## Bounds and failure cleanup

Every Stage27B cap remains:8192 raw bytes,256-byte line/expansion,4096-byte arena,128 instructions,
32 symbols,16 functions/constants,23-byte names,63-byte constant values,16 structure/parser
levels,64 expression tokens,8 calls,10000 instructions,100000 ticks and30000 elapsed ms.
NAME() counts as three lexical tokens; grouping remains part of the token/depth budget. Plans
and value stacks are fixed64 elements. Execution steps count source IR instructions, not each
postfix token; token work is independently charged to the existing tick/time budgets.

Recursion is NOT a new feature or an unbounded C++ mechanism. The Stage27B bounded runtime
policy is retained: direct/mutual calls may execute within eight shared frames, but exceeding
that bound fails CallLimit. Terminating recursive examples and runaway cycles are tested.
No called function nests C++ tick/evaluator stacks: all body transitions return to the caller's
external scheduler. Arbitrary non-returning loops are also bounded by step/tick/time caps.

Cancellation, STOP_PAYLOAD and errors discard all active continuation counters, reset call depth
and invalidate lastReturn. Old token/value bytes may remain in inaccessible fixed slots until
reuse; this is logical cleanup, not a cryptographic zeroization claim. Start resets all frame
counters/call frames/globals. Accepted events remain accepted; no later output occurs after
cancellation. Program borrow and revision checks, reentrant tick/start refusal, callback failure/
exception handling and uint32 clock-wrap behavior remain intact. Callback execution must return
promptly; a caller-provided blocking callback cannot be preempted by this preview.

Error locations use Program.location and physical source line, plus column within the expanded
operand. Runtime arithmetic faults point at the operator, callee faults at their own instruction,
and missing value faults at the caller token. Source edits/macros do not imply exact original
column mapping. No parameter/local/string-return/dynamic-name syntax is introduced.
