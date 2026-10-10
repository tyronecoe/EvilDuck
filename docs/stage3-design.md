# Stage 3 implementation contract

Stage 3 adds constants, typed global variables and one bounded expression engine.
It does not add canonical IF/WHILE evaluation, functions, local scopes, text-block
runtime semantics, physical migration or hardware access.

## Sources and certainty

Official Hak5 documentation consulted on 2026-10-09:

* [Variables](https://docs.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/variables.md): unsigned 0..65535, global scope, TRUE/FALSE and nonzero truth, names containing letters/digits/underscore.
* [Operators](https://docs.hak5.org/hak5-usb-rubber-ducky/operators-conditions-loops-and-functions/operators.md): arithmetic/comparison/logical/bitwise operators, `^` exponentiation, grouping, hexadecimal example, repeated VAR assignments.
* [Constants](https://docs.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/constants.md): preprocessor replacement, `#` labels anywhere, bare labels as space-delimited words, DEFINE lines excluded from replacement.
* [Quick reference](https://docs.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference.md): variable arguments to DELAY.
* [Delays](https://docs.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/delay.md): milliseconds and a Hak5-specific minimum of 20 ms.

No official reference compiler/runtime or physical Hak5 device was executed.
The documentation says parentheses establish precedence, without specifying a
complete precedence/associativity table. Choices below are deterministic EvilDuck
decisions, not claims of conclusively matching undocumented Hak5 behavior.

## Implementation order

1. Add explicit limits and a pure, allocation-free precedence evaluator; verify
   operators, malformed input, arithmetic boundaries and parser limits directly.
2. Add typed global symbols, numeric assignment and retained quoted text/READ
   interpolation; test lifecycle and type errors independently.
3. Add bounded, immutable constants and cooperative raw-definition collection.
   Rewind for expanded structural/syntax preflight, then rewind for execution.
4. Integrate assignment and delay/count consumers into existing scheduling, with
   preflight symbol metadata and unchanged legacy control-flow execution.
5. Run all existing/new mocked suites with sanitizers and the pinned clean 16 MiB
   firmware build; measure resource growth and export only Stage 3 changes.

## Expression model

A small precedence-climbing parser evaluates spans directly. It retains no AST,
postfix program or dynamic token list. Syntax-only evaluation uses unknown values
for variable references and can validate symbol existence/types without executing
assignments. Fully known subexpressions are checked during preflight. Variables
remain runtime-dependent; their values are not simulated during preflight.

Precedence from highest to lowest:

| Operators | Associativity |
| --- | --- |
| grouping `( )`, literals, variable references | explicit grouping |
| `^` exponentiation | right |
| `* / %` | left |
| `+ -` | left |
| `<< >>` | left |
| `< <= > >=` | left |
| `== !=` | left |
| `&` | left |
| `\|` | left |
| `&&` | left |
| `\|\|` | left |

`=` is statement assignment, not an expression operator. `^` is never XOR.
Unary `!`, `~`, unary signs, `**`, word AND/OR/NOT and XOR are rejected: the
consulted operator reference does not establish them. `(x == FALSE)` and
`(x ^ 0)` are not interchangeable with undocumented negation operators.

Literal values must fit 0..65535. Decimal and `0x`/`0X` hexadecimal forms are
supported; leading zero decimal values are decimal, not octal. TRUE=1, FALSE=0;
comparison/logical results are 1 or 0 and every nonzero operand is logically true.
Keywords TRUE/FALSE and symbol/constant names are case-sensitive; statement
keywords retain existing case-insensitive recognition.

Arithmetic wraps modulo 65536 after each operation, including subtraction,
multiplication, exponentiation and left shift. Division truncates unsigned
quotients; modulus is unsigned remainder. Divide/modulo by zero are errors.
Shift counts must be 0..15; larger counts are errors. Exponentiation uses bounded
integer repeated squaring, never floating point; `0 ^ 0` is defined as 1.
Logical operators evaluate both operands; they do not mask invalid RHS values
through short circuit. Wrap behavior, shift handling, `0^0`, eagerness, mixed
precedence and right-associated exponentiation are compatibility decisions whose
exact Hak5 boundary behavior is not established by the available references.

Defaults: expressions <=256 UTF-8 bytes, <=128 tokens and <=16 recursive Pratt
descents (root depth zero). Each exponentiation requires at most 16 iterations.
All syntax errors report expression columns, with script filename/line added by
the existing executor. No heap allocation occurs in expression evaluation.

## Variables and compatibility

The bounded global symbol table retains 16 slots shared by numeric and text
variables. Names start with `$`, followed by letters/digits/underscore only,
and have at most 32 bytes including `$`. Digits after `$` remain permitted,
matching the documented character rule and prior EvilDuck behavior. Names are
case-sensitive; automatic Hak5 internal variables are not added in this stage.

`VAR $n = expression` creates or updates a numeric variable. `$n = expression`
requires an existing numeric variable. Repeated VAR uses the old value when
referenced, as documented. Evaluation failure does not partially update a symbol.
There is no block/local scope. Type changes are rejected rather than coerced.

The default EvilDuck compatibility profile retains `VAR $word = "text"`,
`DEFINE $word = "text"` as a VAR alias, READ-created text variables and text/
decimal-number interpolation in STRING/STRINGLN and file payloads. Text variables
cannot be used numerically, even if their contents look like numbers. Undefined
interpolation remains literal, preserving existing text behavior; undefined
numeric references are errors. Text assignment requires an explicitly quoted
value. Unquoted `VAR $word = OK` must become `VAR $word = "OK"`; this intentional
change prevents malformed numeric expressions silently succeeding as text.
READ may not overwrite an existing numeric variable. Interpolated command output
is capped at the expanded-line limit; legacy READ's whole-file allocation remains
outside the expression hot path and is not a new streaming READ implementation.

DELAY/WAIT, DEFAULT_DELAY/DEFAULTDELAY and REPEAT/REPLAY use the same evaluator for
expressions and variables. Plain unsigned decimal literals, optionally `+`-prefixed,
retain the original 32-bit range as an EvilDuck compatibility path. This path is
lexically distinct and cannot rescue malformed expressions. Expression results
are 16-bit. Delays below Hak5's documented 20 ms minimum remain supported to
preserve existing EvilDuck timing and tests. Scheduler and STOP behavior stay
cooperative; no blocking delays or whole-string HID writes are introduced.

## Constants and cooperative preflight

Canonical DEFINE is distinct from variables. A first bounded source pass collects
definitions outside raw REM/REM_BLOCK and STRING/STRINGLN blocks, independently
of legacy IF branches. Definitions apply throughout the source, including before
their declaration. The existing reader budgets and source limits apply to every
pass; STOP can cancel collection/preflight.

DEFINE values are the remainder after the label's first separator, including
additional whitespace. Labels optionally start with `#`, contain letters/digits/
underscore, and are <=32 bytes. Values and expanded lines are <=512 bytes; there
are <=16 constants and a <=2048-byte value pool including terminators. Duplicate
canonical labels are rejected, including identical redefinitions. The documentation
does not establish redefinition behavior, so this is a conservative decision.

`#LABEL` matches anywhere, even adjacent to other characters. Overlapping labels
use the longest match at each original-source position. Bare labels match whole
space/tab-delimited words or source boundaries. Tabs are treated as spaces as an
EvilDuck boundary convention. Replacement is a single pass over original input;
inserted values are never rescanned. DEFINE declarations (including the legacy
`DEFINE $name` alias) never undergo constant replacement. Constants do not alter
mutable variable storage. In comment/text bodies, expansion is suppressed to
preserve literal-mode handling.

Macro replacement may produce supported statements, but may not synthesize
DEFINE declarations or comment/text-block delimiters. Literal declarations and
delimiters are protected from replacement and keep collection and validation modes consistent without recursive
preprocessing or SD caches. This is an explicit Stage 3 restriction; full Hak5
macro interactions and overlap/recursion behavior are not established here.

After collection, expanded structural/syntax validation occurs before HID.
Preflight stores only bounded symbol names/types, not runtime variable values.
Malformed expressions, known constant arithmetic faults, use-before-declaration,
type errors, declaration exhaustion and expansion overflow prevent all output.
Variables declared inside legacy branches may not exist at runtime; runtime
errors still stop execution safely with source diagnostics and key release.
No canonical conditional or loop evaluation is introduced.
