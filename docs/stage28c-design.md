# Stage28C design — mock-only cooperative preflight

Before implementation: preserve Stage28B grammar/runtime. Add a noncopyable CompileSession
with fixed owned compiler storage, explicit phases and cancellation. Program is exclusively
reserved during compilation and is not ready until a separate final publication step.
Reader/context/Program must outlive the active session, callbacks must return promptly and
source bytes must remain identical across checked rewind. No filesystem/hardware adapter.

Reader declares exact byte size and has read and seek callbacks. Data accepts short reads;
Eof requires zero bytes at the declared end, Retry requires zero bytes, Error is terminal.
A zero-capacity read at the declared end checks explicit EOF without reading beyond source.
Zero-byte Data, premature EOF, contradictory counts and exceptions are errors. One read or
seek callback per step; retries consume a fixed compiler step budget. Chunk capacity32 bytes.

A step performs one callback, consumes at most32 buffered source bytes, processes at most one
256-byte physical line, visits one CFG node, validates one numeric expression, or transitions
one phase. Inner line expansion is capped by256 bytes and16 constants (names23/value63),
expression parsing by64 lexical tokens/16 frames, and line jump patching by128 instructions.
These strictly bounded inner operations remain atomic; no whole-source scan or complete CFG
walk occurs in a step. Cancellation occurs between atomic steps, including pending partial I/O.
All existing caps remain. New compiler maximum65536 steps includes Retry/stalled readers.

BOM/CRLF recognition is persisted across chunks, raw multiline bytes are preserved before
ordinary trimming in both passes, and forward symbols/constants/functions remain two-pass.
CFG work/visited arrays are persistent and reused per function. Readiness is published only
following structure, return inventory and all numeric-context checks. Failed/cancelled compile
invalidates prior compiled content; restart resets all tables/state. Reentrant operations and
concurrent runtime/program/session mutation reject. The convenience API remains synchronous
by explicit caller choice and allocates its session on its caller stack; long-lived cooperative
callers should own the fixed session outside a small task stack.

## Detailed ownership / publication contract

Reader{read,seek,context,bytes} is copied as callbacks plus caller-owned context, not source.
MemoryReader contains only pointer/length/cursor. Data plus bytes<requested capacity explicitly
represents a partial read; Retry is NOT EOF. No unknown-length reader is provided. Initial seek0
and rewind0 are separate steps; all callback exceptions fail closed. Reader functions must obey
buffer capacity and return promptly; a callback that overwrites memory or blocks cannot be made
safe by checking its returned count. This is a single-threaded API, not a mutex/thread-safe API.

Cancel from inside a callback marks cancellation immediately but keeps the Program reserved
until that callback/step unwinds, preventing a second compiler from modifying the same Program.
No subsequent callbacks occur. Reader references are detached at every terminal state. Program,
session and reader context must stay alive through an active step; self-destruction inside a
callback is outside the contract. Terminal getters use stored status/errors, not the old reader.
Rejected concurrent/reentrant requests do not mutate the active compile. Active Runtime borrowing
rejects compile attempts and preserves its current ready result; a real new compile invalidates
old readiness/revision and clears all tables. Failure/cancellation does not restore an old result.

A64-bit rolling FNV fingerprint checks accidental cross-pass source changes before readiness.
It is NOT authentication or a collision-proof snapshot. The Reader contract requires stable
bytes; hostile mutable readers cannot be proven identical without a retained source snapshot.
No private source bytes are logged. No dynamic source buffer is allocated. Terminal errors are
stable; source read/seek/budget errors have current physical line/column where available.

Start performs bounded clearing of Program arrays plus placement construction of fixed compiler
state before any callback. Placement new uses owned aligned storage, never allocating new.
Actual target Compiler2312B fits2368 storage; host Compiler2368B determines the portable cap,
with compile-time size/alignment assertions. Session target2408B includes bookkeeping. Source
buffers are just257-byte partial line plus32-byte chunk. CFG visited/work arrays total384B and
are reused per function. No whole-source duplicate buffer, AST or global writable storage.

## Atomic work bounds and stack

Read/seek steps: at most one callback, read capacity0..32, no parse work. Consume: at most32
source bytes, halts at a physical newline. Line: one raw line<=256; constant lookup<=16 entries
per input position with identifiers<=23/value<=63; output<=256. A line may parse one numeric
expression (<=64 lexical tokens, depth<=16) or patch<=128 already emitted jumps. CFG: one node,
up to two enqueues, at most one bounded expression. Validate: one instruction, at most one
bounded expression. InventoryStart clears128 visited slots, Structure checks state, Publish
commits ready. None executes functions or mock events. Work records count consumed bytes,
callbacks, lines, CFG nodes and post-parse expressions; line-expression work is charged by the
one-line category, not double-counted as post-parse expression work. These are operation caps,
not measured latency guarantees. External callback execution time is unbounded by this API.

The17 new groups test max32 consumption and callback/line/expression caps,256-byte lines with
all16 constants,63-token valid expressions and16-level grouping plus prior exact/over-limit tests.
The8,192-byte one-byte newline source finishes within65536 steps; indefinitely Retry terminates
CompileLimit. One budget-failure step is terminal without I/O (steps() can report limit+1).
Standalone cooperative Compiler::step144B / CompileSession::step32B replace the old whole-compile
stack ownership; Compiler::line160B and statement336B remain bounded. The synchronous wrapper
frame2496B now owns the session, versus old1600B wrapper plus448B compiler frame. Its peak can
be larger; no claim of universal stack reduction. Task-stack and physical latency remain unmeasured.
