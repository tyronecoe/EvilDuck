# Stage 7 streamed text-block implementation contract

Baseline: Stage 6 `b636495a786554afdf3512bee788c6faaa26b229`. Work is isolated
on `stage7-duckyscript-multiline`. Stage 1–6 architecture, regression reports and
tests and the existing migration safeguards were reviewed. No hardware access,
Micro changes, PSRAM changes, partition changes or Stage 8 work is authorized.

## Official references and decisions before implementation

Reviewed 2026-10-11:

* [Hak5 keystroke injection](https://documentation.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection.md): STRING blocks strip leading whitespace and ignore newlines; STRINGLN blocks strip the first tab and preserve other formatting; inline STRINGLN presses Enter after its text.
* [Hak5 constants](https://documentation.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/constants.md): DEFINE is preprocessing, # labels replace anywhere, bare labels replace words, DEFINE lines are exempt and expansion is not recursive.
* [Hak5 variables](https://documentation.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/variables.md): variables are global integers. This page does not establish interpolation of arbitrary shell/code text as a canonical STRING-block feature.

No official compiler or physical reference runtime is used. The STRINGLN prose
says first tab while rendered examples contain spaces, and one example wrongly
closes STRINGLN with END_STRING. Follow the explicit rules: remove exactly one
leading literal tab, preserve spaces and all remaining tabs, and require the
matching END_STRINGLN established by Stage 2. No guessed four-space dedentation.

STRING removes all initial spaces/tabs from each source body line, preserves
trailing/internal whitespace and emits no separators. STRINGLN removes one tab
only if it is the first byte, preserves remaining content, and adds one Enter per
body line, including blank lines. An opener immediately followed by a terminator
has zero body lines and emits nothing. CRLF/LF source line endings do not become
literal CR/LF data. Indentation is removed before constant/variable replacement,
so whitespace supplied by a value is preserved. These boundary/order decisions
are explicit and tested, rather than claimed as independently proven Hak5 edges.

DEFINE expansion uses the existing bounded, single-pass rules on text data, with
literal delimiters recognized before expansion. DEFINE-looking body lines remain
data and retain the existing DEFINE-line substitution exemption; they never
declare constants. Macro/variable output cannot create executable statements or
terminators. Unknown labels remain literal. No escape, quote, parameter or embedded
language alias syntax is invented. Documented language-specific STRING variants
are a remaining gap, outside these two requested block forms.

Existing numeric/text interpolation is an EvilDuck extension: known $identifiers
replace their value, unknown identifiers remain literal, substitutions are not
rescanned, and final per-line expansion is limited to 512 bytes. Arbitrary host
language $variables must not silently become numeric-expression errors. Inline
STRING/STRINGLN behavior is preserved; full raw whitespace preservation is added
only to the newly enabled block path.

## Plan

1. Preserve Stage 2 lexical modes/terminator validation; emit distinct literal
   text-body kinds, with indentation and bounded constant expansion, never parse
   body text as statements. Remove only the runtime-deferred preflight rejection.
2. Add a script-owned literal-text submission path to the existing cooperative
   command scheduler. It bypasses statement parsing, preserves whitespace and
   reuses variable expansion, locale translation, report/release and cancellation.
3. Stream one body line at a time through existing source budgets. Active bodies
   dispatch text; inactive ones only track lexical structure. Definitions remain
   skipped and loop/function seeks occur only with the lexical mode closed.
4. Apply existing default delay per dispatched body line (matching equivalent
   inline commands). Structural markers never enter REPEAT history. Preserve a
   raw text-history discriminator so REPEAT cannot parse text as commands or trim
   trailing whitespace. Empty STRING lines have no output/history/delay; empty
   STRINGLN lines are real Enter operations. No whole-block repeat is invented.
5. Replace only prior tests asserting deliberately deferred text-block support,
   retain structural-error cases, add comprehensive mocked runtime/resource tests,
   rerun all suites with ASan/UBSan and clean-build pinned ESP32 core 3.3.0.

Memory stays bounded by the existing line/source limits, independent of block
length. No extra control/call frames or whole-block buffers are required. Actual
device task-stack/heap watermarks cannot be measured without hardware; compiler
stack-usage analysis and host allocation probes can provide qualified estimates.

Boundary review: the deferred Stage 2 validator charged a text opener against
control depth despite not allocating a control frame. Remove that obsolete check
when enabling runtime support, allowing text at combined IF/WHILE depth eight;
actual control depth nine remains rejected. This intentional relaxation affects
newly enabled text only and avoids inconsistent behavior between inline bodies
and function bodies. Matching/unterminated text validation remains unchanged.
