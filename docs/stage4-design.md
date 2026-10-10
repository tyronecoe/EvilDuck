# Stage 4 implementation contract

Stage 4 implements canonical conditionals only. No WHILE enhancements, hardware
access, physical migration, real HID or Stage 5 work is authorized.

## Reference and syntax

The [Hak5 conditional reference](https://docs.hak5.org/hak5-usb-rubber-ducky/operators-conditions-loops-and-functions/conditional-statements.md)
was retrieved on 2026-10-09. It establishes `IF expression THEN`, optional
`ELSE IF expression THEN`/`ELSE`, `END_IF`, nesting, and a single variable without
parentheses. Parentheses are recommended for compound expressions; this firmware
also accepts unparenthesized compound expressions using Stage 3's documented
precedence. THEN must be the last complete token; trailing garbage is rejected.
Keywords retain EvilDuck's case-insensitive recognition and tab separators.
No ELSEIF/ELIF spelling is added.

## Plan and architecture

1. Add a fixed eight-frame conditional stack storing parent activity, current
   activity, whether a branch was taken and whether ELSE occurred. No recursive
   execution, source buffering, branch scan or heap allocation in this stack.
2. Parse canonical IF/ELSE IF conditions and route syntax/runtime evaluation to
   the single Stage 3 engine. Keep explicit legacy no-THEN atom/equality aliases,
   ENDIF and END IF. Legacy text atoms use a compatibility adapter, not a new
   arithmetic/operator parser. Canonical THEN conditions never accept text.
3. Extend streaming preflight: validate every branch expression, ordering, nesting,
   symbol reference and delimiter before any HID. Metadata remains conservative,
   not a simulation of runtime branch values. Mixed IF/WHILE nesting stays deferred;
   standalone legacy WHILE is unchanged, including its existing known defect.
4. Execute only selected branches. Track inactive nested IFs without evaluating
   their conditions. ELSE IF conditions execute only if the parent is active and
   no earlier branch matched. Every structural line yields within existing source
   and line budgets and never enters command/replay history.
5. Protect raw conditional keywords from macro replacement while allowing DEFINE
   expansion inside conditions. Reject macros manufacturing conditional markers.
6. Add mocked conditional fixtures, side-effect/cancellation/boundary/error/replay
   tests, a fixed-stack allocation probe, all-stage ASan/UBSan runs, and a clean
   pinned 16 MiB firmware build. Export a Stage 4-only patch and stop.

## Compatibility decisions made before implementation

Existing legacy `IF 0`, `IF 1`, `IF $flag`, and simple no-THEN equality remain
explicit aliases. Existing text comparisons such as `IF $word == OK` remain a
legacy-only extension. Their string atoms are mapped to numeric identity tokens
for equality through the existing evaluator. Legacy text truthiness is adapted
to TRUE/FALSE; canonical numeric conditions use nonzero truth unchanged.
Undefined variables are errors, including in legacy conditions. Malformed numeric
expressions cannot fall back to the text extension. Numeric-only legacy equality
uses numeric Stage 3 semantics; values such as `01` compare equal to `1`.
Expressions outside the old atom/equality grammar require THEN.

Conditional macros may replace condition operands but may not synthesize or
replace IF/ELSE IF/ELSE/END_IF structures. This extends Stage 3's literal-mode
safety restriction to the newly supported conditional structures.

All branch expressions are syntax/type checked during preflight, including
inactive branches. Constant divide-by-zero is rejected even in an inactive branch;
variable-dependent errors are evaluated only in eligible runtime conditions.
Declarations in any branch contribute preflight metadata; if the branch never
runs, a later runtime use still fails safely. This does not add local scope or
path-sensitive analysis. Canonical DEFINE remains global preprocessing even when
its declaration appears in an inactive branch, as established in Stage 3.

REPEAT/REPLAY retain the most recent actually executed repeatable keyboard
command. Inactive commands and conditional markers never replace that history.
STOP is effective only in an active branch; external cancellation remains effective
in every phase. Every run and STOP clears the fixed conditional stack.

The no-THEN legacy aliases and text identity adapter are EvilDuck extensions,
not canonical Hak5 syntax. No Hak5 compiler/runtime or physical device was used
as a reference oracle; other Stage 3 numeric ambiguities remain unchanged.
