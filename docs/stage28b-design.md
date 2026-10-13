# Stage28B multiline preview contract

Offline mock-only; NOT FLASH-AUTHORIZED. Production Stage26 remains frozen.

Before implementation: STRING removes all leading ASCII spaces/tabs on each body line,
preserves trailing whitespace, and emits no source newline. STRINGLN removes exactly one
leading tab, preserves every other byte including spaces/trailing tabs, and emits ENTER
once per body line (including blank lines). Empty blocks emit nothing. This is a conservative
preview interpretation of the saved official prose; space-indented examples conflict with
its first-tab wording and no independent official compiler oracle is available.

Standalone trimmed openers/terminators are structural. A wrong terminator, terminator with
non-whitespace suffix, or standalone nested opener rejects the entire source. Embedded closing
words and underscore-suffixed lookalikes remain text. Inline STRING arguments remain supported
unchanged. Delimiters are recognized before expansion; macros cannot create delimiters.

Both compiler passes track raw body mode before ordinary trimming/comment/declaration handling.
Body DEFINE/VAR/FUNCTION/control lines are literal, not declarations. Forward constants collected
outside blocks expand once using existing #anywhere / bare space-boundary policy after indentation
normalization. Expansion is bounded to256 bytes per line and4096 total arena bytes. No numeric
variable interpolation is added: $n remains literal, as in the existing inline preview. Official
constants support replacement in STRING; precise block/order edge cases remain explicit preview policy.

One instruction represents each block; four-byte little-endian physical-line/length records and
expanded bytes share the existing4096-byte arena. No per-line IR or heap index. Empty lines cost
four bytes; an empty block has a zero-byte span. Checked sums cannot exceed the arena/uint16 domain.
Source8192, line256, code128 and every previous symbol/expression/call/budget cap stay unchanged.

Runtime uses a fixed cursor: next/end record offsets, current text offset/length/position/physical
line, active and loaded flags. Each tick loads one bounded record, attempts one character/ENTER,
or transitions a finished line/block. Accepted events alone advance position; Retry preserves
exact event and cursor. Parent expression continuation is untouched while its callee emits text.
Cancellation, STOP and errors clear the cursor and all existing continuation state. Failure during
a loaded line uses its physical body line. No real HID, locale, storage, network or startup adapter.

## Representation alternatives reviewed

Raw source spans would require retaining the caller's8192-byte buffer for runtime and retaining
constants/doing runtime expansion; current Program owns its compiled text independently of that
input lifetime. One IR per body line would exhaust128 instructions on short/blank blocks, while
one per character is still worse. Concatenating all characters into one flat operand loses body-
line error locations and STRINGLN line boundaries. Packed four-byte headers retain those facts
inside the existing arena without adding an unbounded index or source-lifetime dependency.
Compilation remains bounded synchronous preflight; cooperative compilation is a later review.
