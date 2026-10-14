# Stage28C cooperative source/preflight report

**GO: isolated offline review only. NOT FLASH-AUTHORIZED.**
**NO-GO: Stage26 integration, production adapters, physical flashing/boot/OTA or real HID.**

Exact baseline: e184f2837d008d2d732b97dcd5aab839bec3f502, Stage28B.
Delivery branch: stage28c-cooperative-source-preflight. No merge or automatic next stage.
Stage27A remains separately owner-controlled using frozen Stage26
968c8e0aaf459b0b8b652cc57fe88225894ab64b. No hardware or private owner files accessed.

## Genuine cooperative behavior

CompileSession::start/step/cancel provides Idle/Compiling/Complete/Cancelled/Error states.
A step performs one reader/seek callback, consumes<=32 buffered bytes, processes one<=256-byte
line, visits one CFG node, validates one numeric instruction/expression, or transitions a phase.
The existing parser and checked expression evaluator are reused, not duplicated. Function return
inventory now retains work/visited state and processes one node at a time; all numeric contexts
are revalidated one instruction at a time afterward. A separate Publish step commits readiness.
No whole-source parse or CFG walk is hidden inside step. Atomic line expansion, expression
parsing and jump patching remain strictly bounded; see design for exact operation caps.

RAM-only Reader declares exact length and supplies read/seek/context callbacks. Data with fewer
bytes than requested represents partial reads; Eof/Retry/Error are distinct. Zero-byte Data,
premature EOF, bad counts/statuses and exceptions fail closed. End-of-source uses a zero-capacity
read to confirm explicit EOF without reading beyond declared bytes. Initial seek and pass-two
rewind are checked separate steps. Repeated Retry consumes the independent65536-step budget.
BOM, CRLF, raw text, line lengths and physical diagnostics persist across arbitrary chunk splits.
No filesystem, Arduino, SD/SPIFFS, network or USB adapter is implemented.

Program::compile preserves its signature as a synchronous RAM convenience and drives the SAME
state machine. It is deliberately not a cooperative call; its caller-stack cost increases because
it owns a local session. Cooperative callers own a reusable fixed session outside a small stack.
All Stage28B caps/grammar/whitespace/DEFINE/control/function/runtime semantics remain unchanged.
There are no new DuckyScript commands or changes to the compatibility matrix's language statuses.

## Cancellation, lifetime and fail-closed readiness

New compilation clears the prior result/readiness/revision and reserves the Program. Partial,
failed and cancelled results cannot start Runtime; tests explicitly assert zero events. Active
Runtime borrowing rejects compilation while preserving the running result. Multiple sessions,
reentrant step/start and Program mutation reject without damaging active compilation. A cancel
inside a reader callback keeps reservation until unwinding, preventing concurrent mutation.
No more read/seek callbacks occur after cancellation. Terminal states detach reader callbacks;
getters/destruction do not dereference expired reader contexts. Restart resets definitions,
loops, function masks, error and arena state; no stale globals/declarations leak.

Program/session/reader must outlive active compilation; callbacks obey capacity and return
promptly. The API is single-threaded, not cross-thread synchronization or callback preemption.
Reader bytes must be stable across rewind. A rolling64-bit FNV fingerprint detects accidental
cross-pass changes before publication; it is not cryptographic authentication or a collision-
proof snapshot. No private values are logged. Runtime code itself is unchanged.

## Fresh actual verification

| Suite | PASS groups | FAIL | Assertions |
|---|---:|---:|---:|
| Stage27B complete regression | 25 | 0 | 2543 |
| Stage28A complete continuation suite | 23 | 0 | 526 |
| Stage28B complete multiline suite | 26 | 0 | 4733 |
| Stage28C new compiler/reader suite | 17 | 0 | 390573 |
| Total | 91 | 0 | 398375 |

All four fresh runs pass ASan/UBSan and leak detection. Exact names/counts/stdout/commands are
in test-results.md/.json. No skipped/XFAIL/XPASS in these preview suites. Historical firmware
XPASS/XFAIL/observations remain unchanged, not rerun or counted as new language conformance.
The large assertion count includes per-step bounds and readiness checks;17 new groups are not
inflated into a group per seed. Prior500+400 mutation corpora rerun;150 new chunk mutations added.

New coverage includes sizes1/2/3/7/16/64/256 and mixed short reads; splits in BOM/CRLF/DEFINE/
functions/terminators; empty/EOF/max-source/no-final-newline; source/line/arena/code/nesting/
symbol/function/constant bounds;256-byte lines with16 constants and63-token/16-depth expressions;
forced pass-one/pass-two errors and seek failures; thrown callbacks; zero Data/premature EOF/
wrong counts; Retry and full compiler budget; cancellation at every exposed phase and partial
line/block boundary; reentrant calls; shared Program/session/runtime ownership; reader expiry
only after terminal state; restart and changed-source rejection; zero C++new on tested core paths.
Earlier text/delay/function/control/mock-event tests remain unchanged and pass.

A costly source cannot finish in one step. Tests measure32-byte maximum consumption, one callback,
one line and one post-parse expression, and enforce one CFG node per step. An8192-byte newline
source with one-byte reads completes within the same65536 budget. A permanently Retry reader
terminates without extra I/O. Work-category instrumentation is not a physical latency measurement.
Cancellation inside atomic bounded parsing is observed on the next caller turn, not halfway through
an individual token operation. External callbacks/exception machinery are outside allocation claims.

Development issues were surfaced and corrected: friend-declaration insertion compile error;
null memory source error classification regression (adapter restored InvalidSource); unnecessary
empty Consume transition near max-source budget; C++ BOM fixture literal typo; and a test checking
not-ready after Complete merely because phase remains Publish. Final expectations retain pre-
publication rejection and existing error semantics; no cap, old test or dependency pin weakened.

## Pinned target object-only verification

Arduino3.3.0 original/isolated protected core, ESP-IDF5.5 SDK archive/config and Xtensa compiler
hash checks PASS. Exact Stage28B/Stage26 flags retain16MiB/QIO80/CPU240, PSRAM disabled and
TinyUSB/USB-OTG/CDC. Only core.o and type-metadata sizes.o are generated. Metadata includes the
internal Compiler type through a separate unlinked translation unit; its48-byte readonly size
section is not firmware. No ELF/BIN, partition image, deployable profile or production rebuild.
Target-build/source-hashes JSON record exact commands and dependency/source/object identities.

| Target measurement | Stage28B B | Stage28C B | Delta |
|---|---:|---:|---:|
| Program | 6932 | 6936 | +4 |
| Runtime | 4872 | 4872 | 0 |
| Program+Runtime | 11804 | 11808 | +4 |
| CompileSession | absent | 2408 | new fixed transient ownership |
| Internal Compiler | prior stack local | 2312 | inside session storage |
| Reader / MemoryReader | absent | 16 / 12 | caller-owned mocks |
| Selected object text | 11309 | 13007 | +1698 |
| Literal | 1704 | 1856 | +152 |
| Read-only data | 1712 | 1838 | +126 |
| Writable data/BSS | 0/0 | 0/0 | unchanged |

Program's compile-ownership flag adds4B through padding/alignment. CompileSession contains2368B
aligned storage plus bookkeeping; target Compiler2312B and host Compiler2368B fit static
size/alignment assertions. The initially reserved2560 storage was narrowed to2368 after actual
size checks. Active Program+Runtime+Session totals14216 target bytes, excluding external source/
reader/sink. Partial line/chunk buffers257+32B and CFG arrays384B reside inside Compiler; no
whole-source duplicate or dynamic table. Instruction12/Event4/TextCursor14/Continuation516/
CallFrame6/ExprToken6 stay unchanged. Selected object sections are NOT deployable flash usage
or OTA measurements; production firmware/artifacts remain frozen.

Target frames: cooperative CompileSession::step32B, Compiler::step144B, Compiler::line160B,
statement336B, expression validation112B, recursive parser64B/frame (max16). Old Compiler::compile
448B and valueInventory544B whole-walk frames disappear; CFG state is stored in session. The
cooperative deepest selected parsing chain is roughly2KiB plus callers/libc, versus Stage28B's
roughly3.8KiB with stack-owned compiler. The synchronous Program::compile frame is2496B versus
1600B previously and can make its complete peak roughly4.5KiB; stack reduction applies to the
cooperative API, not all callers. Source-derived estimates exclude external callback/libc/SDK
cost and are not full stack proofs. No physical heap/high-water/latency measurements performed.

## Freeze, remote refs and readiness

All235 protected Stage26 files compare byte-identical against immutable Git baseline, including
production source, reviewed artifacts, tools, Stage26 docs and dependency proposals. Historical
Stage27B/28A/28B docs/tests remain unchanged. Only preview source/README, new tests and Stage28C
records change. No Arduino Micro, partitions, USB identity, migration/recovery or global core/SDK
modification. Original firmware remains OWNER CONFIRMED — AVAILABLE EXTERNALLY; no search or
private owner data request. No real HID/USB, hardware discovery, stored payload or physical operation.

27 remote heads existed at start (the26 prior to Stage28B plus Stage28B itself); all are compared
before/after publishing only the new Stage28C branch. Source hashes and frozen-file receipts are
reviewable in this branch. No previous remote ref is moved, rewritten or merged.

Remaining limits: exact-size stable readers only, synchronous bounded line/expression inner work,
no reader preemption, no production adapters, no locale/modifier/Unicode/hardware language support,
no independent official compiler oracle for previously documented language ambiguities. No unexpected
final failure or missing required tool. No full DuckyScript3.0 or physical compatibility claim.

Recommended next separate milestone: mock-only persistent keyboard/modifier ownership and exact
report planning with rollover/release/cancellation tests, prior to any hardware adapter. Also review
stack admission and source lifetime contracts before integration. No next milestone started.
**GO offline preview review only; NO-GO integration/flashing/boot/OTA/real HID/automatic execution.**
