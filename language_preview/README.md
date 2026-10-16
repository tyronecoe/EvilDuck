# Portable interpreter and the two execution paths

The portable engine is independent C++ in core.h/core.cpp. It is not included by
the ordinary Arduino sketch automatically. The reviewed X candidate composes it
with a cooperative output adapter in a separately built scratch sketch; a source
parser feature is not proof that this adapter accepts it. No complete DuckyScript
3.0 conformance or physical USB validation is claimed.

| Contract | Upgraded legacy interpreter | X Route B candidate |
| --- | --- | --- |
| Implementation | EvilDuckS3/duckscript.cpp + script_parser/duck_expr + com/hid_backend | core Program/CompileSession/Runtime + reviewed adapter/coordinator/FileSource and existing scheduler/backend |
| Default/selection | Ordinary CLI `run <script>` or authenticated `/run?s=<script>`; default path even with Route B compiled | Only when EVILDUCK_PORTABLE_ROUTE_B is compiled: explicit CLI `routeb <script>` or authenticated `/run?engine=routeb&s=<script>` |
| Main language | Global numeric/boolean variables, DEFINE, IF/WHILE, functions/returns, streamed text, keyboard commands | Bounded numeric/boolean variables, DEFINE, IF/WHILE, functions/returns, text, DELAY, restricted key taps, STOP_PAYLOAD |
| Extensions | Text interpolation, US/DE LOCALE, REPEAT/REPLAY, preprocessing/aliases, supported internal/RNG/jitter/LED/file commands and ownership operations | ASCII-only candidate input; explicit `sd:`/SPIFFS source selection; no implicit legacy features |
| Bounds | Source256KiB/8192 lines;16 ordinary variables; combined control depth8,16 functions/call depth8; other config.h limits | Source8192B,128 instructions,4096B text arena,32 symbols,16 functions/call depth8, nesting16; core.h runtime budgets |
| Unsupported input | Full preflight rejects detectable syntax/type/structure/unknown-command errors before script HID; runtime-only errors stop safely | Compile/capability failure before execution, no silent retry through legacy; actual X adapter rejects ownership IR even where standalone preview parses it |
| Output meaning | Cooperative local scheduling and persistent ownership with existing cleanup | Copied requests, one owner, capture/verify/preflight, backpressure, first-fault/permanent loss-or-ambiguity quarantine; no replay |

Boot does not select/arm Route B. Ordinary run never switches engines by content;
a failed explicit Route B request does not fall back. Competing work can be refused.
W/X restrictions remain: disabled mutating WebSocket CLI, asynchronous filesystem
responses and uploads/update/restart. These are candidate policies, not changes to
all historical production profiles. Controlled-start package has strict credentials,
no autoformat/examples/autorun; nothing in this comparison changes startup policy.

INJECT_MOD modifier-source semantics and RESET/release-all remain deliberately
blocked in the portable source contract. The legacy implementation has its documented
behavior; its success is not portable support. The four spellings RGUI, RWINDOWS,
RCOMMAND and ROPTION remain unsupported after audit; legacy RIGHTGUI/RIGHTWINDOWS
and RIGHTALT/RALT already provide the corresponding right-side functionality.
No canonical status was established for those extra spellings; no aliases are added
merely to match Pico-Ducky. See [the compatibility pass](../docs/compatibility-pass.md) for evidence and tests.

Mock/native tests establish specified source behavior and exact mocked reports;
target-linked receipts establish build identity. Neither establishes actual task
latency, physical media/heap/stack, USB delivery, endpoint retirement or host release.
LOCAL_SCHEDULER_DONE and LOCAL_CLEARING_SUBMITTED remain local observations. Existing
prepared X/Y images retain their published identity and remain subject to separate
owner authorization; this documentation/test pass adds no deployment prerequisite.

## Historical stage notes

The entries below describe each stage when originally delivered, including earlier
unlinked/mock-only status. The current X composition described above supersedes those
historical deployment statements without changing their source or feature contracts.

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
