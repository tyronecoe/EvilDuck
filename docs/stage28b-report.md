# Stage28B bounded multiline strings report

**GO: isolated offline preview review only. NOT FLASH-AUTHORIZED.**
**NO-GO: Stage26 integration, physical flashing, boot, OTA or real HID under this assignment.**

Exact baseline: Stage28A9422ac34c3c7954c0be07076ee2ee719378b783d.
Delivery branch: stage28b-bounded-multiline-strings. No automatic merge or next milestone.
Stage27A hardware work remains separate, using only frozen Stage26
968c8e0aaf459b0b8b652cc57fe88225894ab64b with its own owner authorization.

## Implemented behavior

Standalone STRING/END_STRING and STRINGLN/END_STRINGLN blocks compile into one instruction
per block. Both compiler passes preserve raw body bytes before ordinary statement trimming.
Body comment/declaration/control-looking words are data; they never collect symbols/functions/
constants or affect runtime nesting. Exact wrong/extra/suffixed terminators, missing terminators
and nested standalone openers fail preflight before any mock event. Embedded terminator words
and underscore-suffixed lookalikes are literal. Any nonempty STRING/STRINGLN argument remains
the existing inline form; it is not interpreted as a malformed block opener.

STRING removes leading ASCII spaces/tabs per line, preserves trailing bytes and joins lines
without ENTER. STRINGLN removes exactly one leading tab and preserves spaces, additional tabs,
trailing bytes and blank lines; each body line emits exactly one ENTER. Empty blocks emit
nothing. Saved official prose establishes leading-whitespace/newline stripping and first-tab
wording. Space-indented examples do not fully resolve formatting edges; these exact choices
are conservative preview policies, not claimed official compiler oracle results. Both fixtures
emit abc / a-ENTER-b-ENTER-c-ENTER respectively; STRINGLN fixture uses actual tabs.

Forward DEFINE replacement in block data uses existing nonrecursive #anywhere and bare
space-boundary rules after indentation normalization, with256-byte expansion limits. Raw
closing delimiters are recognized before expansion; replacements cannot manufacture structure.
A body DEFINE line is text and not a definition (it can undergo text replacement like other data).
Numeric variable interpolation stays literal ($n), matching inline preview behavior. Aliases,
Unicode, locales/modifiers, parameters/string returns and hardware commands remain unsupported.
No proprietary compiler code, SDK behavior or production interpreter dispatch is borrowed.

Blocks work inside eligible IF/ELSE IF/ELSE, WHILE and functions; inactive blocks emit nothing.
Forward/nested standalone and expression calls can emit blocks then return values without
replaying accepted events. Tests cover function-internal IF/WHILE, conditions that call a block-
emitting function on every reevaluation, zero/one/many loop iterations, shared call-depth limits
and ordinary inline behavior. Stage28A eager left-to-right expression continuation semantics
and numeric/void diagnostics remain unchanged.

## Bounded cooperative architecture

Four-byte line/length headers and expanded bytes share Program's existing4096-byte text arena.
One block instruction stores offset/span; no per-line/character instruction or allocated index.
Headers are byte-addressed little-endian, avoiding unaligned uint16 loads. Checked sums stay
within arena/uint16 bounds. Empty lines cost4 bytes;1024 blank lines fit exactly,1025 reject.
Thus metadata consumes the existing arena budget, not extra hidden storage. Empty blocks use
zero arena bytes but count one instruction. Source8192, line256, code128 and all prior caps stay.

A fixed TextCursor holds current/next/end offsets, length, character position, physical line and
active/loaded flags. One tick loads one checked record, attempts one event, or transitions a
finished line/block. Character positions advance only after Accepted. STRINGLN advances the
record only after its ENTER is accepted; Retry preserves the same pending event. STRING's
no-event end-of-line transition is bounded. Parent continuation slots remain suspended intact.
Cancellation, STOP_PAYLOAD and errors clear the block cursor and continuations; restart clears
state. Runtime failures while a record is loaded identify its physical body line; columns remain
within normalized/expanded text (no complete macro/indent source-column map claimed).

Program borrowing/revision checks, multiple-runtime rejection, reentrant tick/start refusal,
sink failures/exceptions, wrap-safe clocks, step/tick/time budgets and zero-progress rejection
remain. Already accepted events cannot be rolled back. Callbacks must return promptly and this
single-thread API is not a cross-thread synchronization primitive. No blocking output loop,
real keyboard state or transport-level release is implemented in this synthetic preview.

## Fresh executed verification

| Suite | PASS groups | FAIL | Assertions |
|---|---:|---:|---:|
| Stage27B entire regression | 25 | 0 | 2543 |
| Stage28A entire continuation suite | 23 | 0 | 526 |
| Stage28B new multiline suite | 26 | 0 | 4733 |
| Total | 74 | 0 | 7802 |

All three runners freshly compile actual current core; ASan/UBSan and leak detection clean.
Exact names/assertions/stdout/commands are in stage28b-test-results.md/.json. No skipped,
XFAIL or XPASS cases in these preview suites. Previous production historical diagnostic
classifications/documents remain unchanged and are not reused as fresh passes.

Coverage includes LF/CRLF/BOM/EOF, raw text/whitespace, structural failures with zero events,
forward/constants boundaries, exact and over-limit source/line/text/code/expansion bounds,
1024 blank records,16/+1 nesting,8/+1 calls, every cancellation output boundary, ENTER retries,
body-line sink errors/exceptions, borrow/restart/reentrancy, wrapped/stuck clocks, all budgets,
large text loops,400 new seeded mutations plus existing500 mutations and zero C++new on tested
core compilation/block-output/suspended-expression paths. External sinks/exception machinery,
C allocator behavior and physical heap are outside that allocation claim.

Initial new test failure: bare WORD! was mistakenly expected to expand despite punctuation.
Expectation corrected to the preserved space-boundary rule; no language rule or bound was
changed to make it pass. Final suites were executed after all core changes; the final new suite
also includes added mixed function/control-flow cases. No remaining unexpected failure/blocker.

## Target object/resource evidence

Exact pinned Arduino3.3.0/ESP-IDF5.5 compiler/SDK/config/core/source checks PASS. Only Xtensa
objects and32-byte sizeof metadata are produced, never a linked firmware ELF/BIN or installable
profile. Existing PSRAM-disabled16MiB/QIO80/CPU240/TinyUSB/CDC target flags are reused without
global toolchain or frozen build modifications. Exact hashes and commands are in target-build
and source-hashes JSON. Undefined symbols include libc/exception support only; no hardware API.

| Target measurement | Stage28A B | Stage28B B | Delta B |
|---|---:|---:|---:|
| Program | 6932 | 6932 | 0 |
| Runtime | 4860 | 4872 | +12 |
| Program+Runtime | 11792 | 11804 | +12 |
| Instruction | 12 | 12 | 0 |
| TextCursor | absent | 14 | fixed bounded metadata |
| Selected object text | 10166 | 11309 | +1143 |
| Literal | 1572 | 1704 | +132 |
| Read-only data | 1680 | 1712 | +32 |
| Writable data/BSS | 0/0 | 0/0 | 0/0 |

Event4, ExprToken6, Continuation516 and CallFrame6 remain unchanged. Cursor occupies14B but
uses2B prior Runtime padding, giving12B net. Per-line metadata consumes4 existing arena bytes.
No new writable global storage. Selected object sections are not final application flash usage,
OTA headroom or a deployable BIN size; the frozen production firmware is not rebuilt here.

Compiler frames: Program::compile1600B (unchanged), Compiler::compile448B (+16), textLine320B,
statement336B, valueInventory544B, expression validation112B, recursive parser64B/frame (max16),
Runtime::tick112B, evaluationStep144B, deliver/completeInstruction32B. A deeply nested expression
compile chain remains roughly3.8KiB plus callers/libc; block line processing roughly2.5KiB and
runtime plan preparation roughly1.3KiB of selected frames. No large Program/whole-block stack
copy. These estimates do not prove a full embedded stack budget or physical high-water.

## Freeze, delivery and next scope

All235 protected Stage26 files rechecked byte-identical against Git baseline, including source,
reviewed artifacts, preparation tools, docs and dependency proposals. Receipt independently
checks the235-file Git scope. No Arduino Micro, production source, startup/storage/HID/USB,
partition/settings/migration safeguard or prior historical test/report is changed.
26 preexisting remote heads were captured before branching; publication checks all remain
unchanged and the new remote HEAD matches the delivered commit. Source inventory is listed in
stage28b-files.md; review the branch diff against the exact Stage28A baseline.

Original firmware remains OWNER CONFIRMED — AVAILABLE EXTERNALLY. No owner backups/private
contents, hardware discovery/access, stored payload execution, physical operation or global
core/SDK modification occurred. Mock fixtures are harmless data events only.

Recommended next separate milestone: bounded cooperative source/preflight reader interfaces
with mock read/seek faults and cancellation, and compile-stack reduction before any production
adapter work. Current source is bounded caller memory, not SPIFFS/SD streaming. No next stage
started. GO for offline preview review; NO-GO for integration/flashing/boot/OTA/real HID.
