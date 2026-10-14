# Independent DuckyScript preview — offline only

Not included by any Arduino sketch/build profile. NOT FLASH-AUTHORIZED.

core.h/core.cpp contain original fixed-storage parser/evaluator/runtime code. There are no
Arduino, filesystem, USB, HID, network or SDK calls. Program compile/preflight produces
bounded IR; Runtime consumes it cooperatively through a caller-supplied mock event sink.
See docs/stage28b-design.md and docs/stage28a-design.md (current) and docs/stage27b-design.md (historical) for limits and deliberately partial language semantics.

No proprietary compiler code was copied. This is an independent compatibility effort, not
Hak5 firmware, endorsement or complete DuckyScript3.0 compatibility. Stage27A hardware work
remains separate and must retain Stage26 reviewed binaries, hashes and authorization gates.

Stage28A adds cooperative numeric expression function calls in fixed continuations.
The runtime is still mock-only, unlinked and NOT FLASH-AUTHORIZED.

Stage28B adds bounded multiline STRING/STRINGLN via one instruction per block and
compact line records in the existing text arena. STRING strips leading spaces/tabs,
concatenates lines and preserves trailing bytes. STRINGLN strips exactly one leading
tab and emits ENTER per body line; spaces/rest tabs/trailing bytes remain literal.
Empty blocks emit nothing. These formatting edge policies are documented, not
independently established official compiler results. Forward DEFINE substitution
is bounded/nonrecursive; $variable text stays literal. Aliases remain unsupported.
See docs/stage28b-report.md for fresh tests, limits and object-only resource evidence.
No storage/USB/HID adapter, installable firmware or arming path exists in this preview.

Stage28C adds CompileSession::start/step/cancel for RAM-only Reader callbacks.
Each step has a bounded callback/byte/line/CFG/expression operation; only final
publication makes Program ready. Sources declare exact size and stable two-pass
bytes; read/seek/context and Program must outlive active compilation. Terminal
completion/error/cancellation detaches reader callbacks. MemoryReader is the only
provided adapter; no filesystem, USB, Arduino or network reader exists.
Program::compile remains a synchronous convenience that drives the same session,
with a larger caller-stack cost. Prefer an externally owned CompileSession for
cooperative scheduling; see docs/stage28c-design.md and reproduction/report.
Grammar/runtime semantics, Stage28B whitespace and every existing cap are unchanged.

Stage28D's keyboard.h/keyboard.cpp define an independent ds_keyboard::Planner.
It plans eight-byte mock snapshots with four idempotent persistent owners,
ascending six-key union, transient press/restoration, strict overflow rejection,
and explicit accepted neutral cleanup. It does not consume Runtime events or
add HOLD/RELEASE parser syntax. mapUS/character use a fixed printable-US ASCII
model, not locale/Unicode/host text guarantees. See docs/stage28d-design.md.
No real HID/USB/OS adapter exists. Core compiler/runtime source remains unchanged.

Stage28E adds opt-in ds_bridge::Bridge, owning an independent Runtime and Planner.
begin/step establishes mock neutral sync; optional Prepared owner setup precedes
start(program). Each driver step advances one Runtime tick or one planner report
attempt. A keyboard source event is acknowledged only after its press AND restoration
finish; next identical events remain distinct. Delay is acknowledged without a report
and timed by Runtime. cancel clears local intent; explicit drain confirms mock neutral
before restart. See docs/stage28e-design.md and the host-only Mac smoke recipe.
Existing core/Sink ABI is untouched. Planner adds only a pure validUsage query.
No production transport, real HID, firmware image, arming or host control exists here.

Stage28F adds the narrow, mock-only HOLD key / RELEASE key source subset. Lowercase
letters, digits and the existing ten named nonmodifier keys only. Modifier source
commands, INJECT_MOD and RESET/release-all remain unsupported with reference gaps
recorded in docs/stage28f-command-contract.md. Programs containing ownership commands
reserve script owner3; older programs retain all four Prepared setup owners. Every
source ownership command requires fresh union-report acceptance, even if idempotent.
No tap/restoration is invented for HOLD. Runtime terminal cleanup remains logical;
explicit drain is necessary to establish mock neutral. Event layout and original
numeric enum values are preserved; EventType now appends Hold/Release, so a standalone
Sink must explicitly handle or reject them. There is no production adapter.
