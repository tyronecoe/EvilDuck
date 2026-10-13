# Stage27B independent preview contract (software only)

NOT FLASH-AUTHORIZED. Stage27A continues using the frozen Stage26 reviewed artifacts.

The original preview is in language_preview/, outside Arduino's EvilDuckS3 source tree. No
production entry point calls it. No serial, filesystem, USB, network or hardware APIs occur in
this core. Only a caller-supplied event callback exists; tests supply synthetic mock sinks.

Select a small bounded compile/execution split: physical source and preprocessing are validated
before Program.ready. A fixed instruction array uses explicit conditional/loop targets and a
fixed standalone-function call stack. Numeric evaluation is independent original code, not the
old duck_expr implementation or proprietary compiler code. No new expression AST/library.

Initial subset: exact uppercase REM, REM_BLOCK/END_REM (DOCUMENTATION heading), single-line
STRING/STRINGLN, DELAY, VAR/$assignment, DEFINE, IF/ELSE IF/ELSE/END_IF, WHILE/END_WHILE,
top-level FUNCTION NAME()/END_FUNCTION, standalone NAME(), RETURN expression or void, and
STOP_PAYLOAD. Ten named keys are tap events, never physical reports. Function return values are
observable through the preview API, but calls within expressions are unsupported and rejected.
Multiline strings, text interpolation, parameters, internal/device variables, modifiers and
hardware commands are deferred explicitly. A bare unknown word never becomes keyboard text.

Source/declaration first pass collects global numeric names, constants and functions. A second
pass validates every included statement/body and builds IR. Inactive branches are still parsed;
execution jumps over them. A declared-but-not-yet-executed variable fails at runtime. VAR
redeclaration can read an earlier initialized value. All variable storage is global. Constants
are one-pass, nonrecursive, longest-label-first replacements in operands; #labels match anywhere,
bare labels at space boundaries (not tabs). Declarations are not expanded. Structural command
manufacture, recursive expansion and duplicate constants are rejected/unsupported policies,
not a claim of unrestricted reference preprocessing equivalence.

The verified saved reference states uint16 variables and Boolean/nonzero truth. It requires
parentheses to establish precedence but does not define a complete unparenthesized grammar or
all arithmetic errors. This preview's explicit safety decisions: TRUE1/FALSE0; eager operators;
checked arithmetic fails on overflow/underflow, division/modulo0, shifts outside0..15 and0^0.
Hex/decimal literals must fit65535. Integer division truncates; unsigned modulo. Low to high:
||, &&, |, &, == !=, < <= > >=, << >>, + -, * / %, ^. Power is right-associative; others left.
These unparenthesized/edge policies are tested engineering decisions, not independently proved
Hak5 behavior. ^ means power, never XOR. Unary operators/++/+= are not invented. Grouping is
recommended for portable examples. Pure constant errors fail preflight; variable-dependent
errors stop runtime before the offending event, not retroactively undo earlier accepted events.

Bounds:8192 source bytes,256 physical/expanded line bytes,4096 total stored operand bytes,
128 instructions,32 variables,16 functions/16 constants,23-byte names,63-byte constant values,
16 structural levels,64 expression tokens/16 evaluator frames,8 function frames,10000 executed
instructions,100000 tick calls,30000 elapsed milliseconds. Caller may lower step/time budgets,
not raise them. ASCII source/text only (initial UTF8 BOM accepted); LF/CRLF/final EOF accepted,
lone CR and NUL rejected. STRING trailing horizontal whitespace omitted; after the first command
separator, leading content is retained. Variables in text stay literal; no legacy interpolation.
Empty multiline openers are unsupported. No unbounded script buffer: this pilot retains a
bounded small IR/text pool; large storage-backed compile/streaming is a later integration gate.

One tick executes at most one instruction or tries one event. Text is emitted one character per
event and STRINGLN finishes with ENTER. Retry does not advance or duplicate accepted events;
delay time starts only after its event is accepted, using uint32 clock differences. Tick/time
budgets also cover backpressure or a stuck clock. Cancellation/STOP_PAYLOAD discard pending
work. Sink failure or a callback exception is terminal. The callback must return promptly; this core cannot preempt blocking external callback code. This abstract tap model owns no physical held keys. A future
real adapter must provide release/arming independently. Reentrant tick/start from callbacks are
refused, cancellation is allowed; single-threaded use only. Program cannot recompile while
borrowed by an active Runtime. Program and sink context must outlive the borrowing Runtime.
The runtime is noncopyable and destruction cancels ownership. Completed/restarted sessions
reset globals, calls and pending events; runtime values remain inspectable until restart or Program recompilation (tracked by revision). Event references are valid only during the callback; sinks must copy them if retained.
