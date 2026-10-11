# Stage 6 implementation contract

Baseline: Stage 5 `1222fc6fb9307dd9680493b189b595cdd0c91b2f`. Prior implementation
contracts, all regression reports and flash/migration safeguards were reviewed.
No hardware access/migration, PSRAM changes, Micro changes or Stage 7 work.

Official reference: [Hak5 functions](https://documentation.hak5.org/hak5-usb-rubber-ducky/operators-conditions-loops-and-functions/functions.md),
retrieved 2026-10-11. It establishes FUNCTION NAME(), END_FUNCTION, NAME()
invocation, global variables (not positional arguments), optional RETURN and
integer/Boolean returned values usable in conditions. Names start with a letter
or underscore and contain letters/digits/underscore. Reference examples declare
functions before the globals they read. No reference runtime/device was executed.

## Plan

1. Extend the existing Stage 3 precedence parser with zero-argument function
   operands and optional bounded postfix emission. Preserve its operator
   implementation, precedence, arithmetic, syntax limits and eager logical rules.
2. Add a cooperative source inventory pass after DEFINE collection and before
   preflight. Store only names and body/end byte/line markers for <=16 functions;
   collect global declaration type metadata for function-body preflight.
3. Extend full preflight for declarations, calls, returns and block boundaries,
   including forward calls and body references to globals declared later. Keep
   main-statement declaration ordering checks; validate every function body before
   any HID even when never called. Reject nested/conditional declarations.
4. Add <=8 suspended call frames. Postfix evaluation retains earlier operand
   values across callees' side effects, avoiding replay/double execution. Each
   update processes a bounded instruction count. Share the existing control stack
   and save a base depth so RETURN unwinds only callee IF/WHILE frames.
5. Preserve executor/timers/replay/STOP, test all prior and new suites under
   ASan/UBSan, clean-build core 3.3.0, measure resource growth and publish separately.

## Decisions established before implementation

* Canonical forms: FUNCTION NAME(), END_FUNCTION, NAME(), RETURN expression.
  Zero-argument () is literal and adjacent to the name. No parameter/local-scope,
  CALL, END FUNCTION, ENDFUNCTION or argument syntax is invented. Names are
  case-sensitive; statement keywords preserve case-insensitive EvilDuck behavior.
* Definitions register globally (including forward references) and are skipped
  in sequential execution. Definitions must be top level; nested/conditional
  definitions, duplicate names and collisions with command/key/modifier names
  reject. Forward references and top-level-only definitions are deterministic
  choices where the supplied reference does not fully specify compiler behavior.
* Values are Stage 3 unsigned 16-bit integers; TRUE=1, FALSE=0. Void explicit
  RETURN / implicit END_FUNCTION is valid for a statement call. Consuming void
  in an expression is an error rather than guessing a canonical default value.
* Compatibility: bare top-level/live RETURN stays Enter; bare RETURN in a
  function returns void. CTRL RETURN remains a key combination in every context.
  RETURN expression outside a function rejects preflight. Use ENTER to type
  Enter inside a function. This intentional context-dependent change is tested.
* Calls are supported in numeric assignments, canonical IF/ELSE IF and WHILE
  conditions, RETURN expressions and existing expression-based delay/count
  commands. STRING remains literal/interpolated text, not expression execution.
  Unsupported legacy IF without THEN does not silently accept new calls.
* Globals have no local scope. Body preflight uses collected global types;
  initialization/call paths are runtime-dependent and errors stop safely. It does
  not pretend a function has executed merely because its body was declared.
* Recursion is permitted but bounded: eight live calls, 100,000 total invocations
  per script. Shared IF/WHILE depth remains eight across active calls. Exceeding
  depth/budget rejects runtime safely. Existing WHILE progress/iteration guards
  stay unchanged; calling an empty function alone is not useful loop progress.
* Suspended evaluation is a fixed postfix program, not an AST or second grammar.
  Existing Stage 3 parsing/arithmetic compile it. Evaluation order is left-to-right
  for operands, including eager &&/||; earlier variable operands retain their
  values if a later called function mutates globals. This side-effect order is an
  explicit deterministic choice not independently matched to Hak5 boundaries.
* Function/call metadata, operand and instruction storage are fixed-size. Source
  bodies continue streaming from SPIFFS/SD. STOP clears calls, pending evaluation,
  source state, variables/constants and held keys. Seeks/errors carry source line.
* DEFINE may expand operands/body expressions but cannot manufacture declaration,
  call-name declaration, END_FUNCTION or RETURN structural syntax. Function names
  on literal declarations and standalone invocation are protected.

No claims of full DuckyScript compatibility. Stage 7 text-block runtime semantics,
internal Hak5 variables, parameter syntax, and existing HID/locale defects remain
outside this stage. Physical SD/USB/web timing and runtime high-water measurements
remain for later separately authorized testing.

## Verified integration details

Implementation retains eight fixed call frames and a separate bounded registry.
Each call stores the caller's pending postfix program, source return marker and
control-stack base. Entry isolates the callee root from the caller's inactive
ELSE IF branch; return removes callee frames and restores caller boundaries.
The main-loop update advances at most 16 expression instructions before yielding.
The enlarged RunState is reconstructed in place, avoiding a large aggregate
temporary on the embedded task stack.

WHILE conditions with functions snapshot variable/action progress before the
condition runs. Condition-side-effect assignments therefore count as progress;
empty function calls alone do not. The original iteration and stalled-loop limits
are retained. The 1,100-iteration condition-side-effect test exceeds the stalled
threshold and verifies this interaction.

Final clean-build static RAM is 80,408 bytes, growth 10,336 bytes over Stage 5.
The isolated postfix/call-state probe observed zero C++ allocations. Host sizeof
measurements and exact executed tests are in `stage6-report.md` and
`stage6-results.json`; device stack high-water and heap fragmentation remain
unmeasured. All malformed-body preflight, cancellation and storage-error tests
use mocked hardware only. No Stage 7 work or hardware migration was performed.
