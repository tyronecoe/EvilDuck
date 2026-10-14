# Stage28E mock Runtime/planner acknowledgement bridge

**GO isolated offline review only. NOT FLASH-AUTHORIZED.**
**NO-GO Stage26 integration, physical flashing/boot/OTA, real HID or production adapters.**

Exact baseline: d44582884da33c4028612fa595e07384a08f9c84, Stage28D.
Delivery branch: stage28e-mock-runtime-planner-bridge. No merge or automatic next stage.
Stage27A remains independently owner-controlled using frozen Stage26
968c8e0aaf459b0b8b652cc57fe88225894ab64b. No private backups/firmware/device access.

## Implemented bridge and acknowledgement boundary

Opt-in language_preview/bridge.h/.cpp owns a Runtime and Planner. begin queues initial neutral
sync; step finishes it before Prepared. Optional Prepared owner setup is internal mock API only.
start borrows a ready Program and begins the owned Runtime. Existing standalone Runtime/Sink
usage remains supported independently; core.cpp/core.h are byte-identical to Stage28D.
Planner only gains pure static validUsage, reusing its own usage domain. No existing rule or
structure size changes; no language command, parser, OS/HID/USB adapter or firmware source change.

One driver step executes either one Runtime tick OR one Planner step, not both. A first keyboard
source callback admits exactly one action, binds intent Waiting and returns Retry. Only accepted
press AND accepted restoration make that intent Ackable. The next owned Runtime callback returns
Accepted once and clears intent. A subsequent identical source event starts a fresh action; no
field-equality deduplication or fake ID shortcut. Equality detects only mismatched retries of a
current intent. Sync or setup readiness cannot stand in for source action completion.

Guarded sourceSink rejects calls outside the owned Runtime window, null contexts and reentrancy.
Report callbacks cannot start another bridge session, mutate setup owners, recursively step or
inject source events. Getters expose const observations, not external stepping authority. Program
borrowing/revision and compile-readiness protections remain unchanged. Source/event counters track
actual admissions and keyboard/Delay acknowledgements; no FIFO/string buffer or unbounded trace.

Character uses existing fixed US mapping; KeyTap uses validated page07 usages. Values outside
those domains reject, as do held-tap conflict or seventh-key proposals. Pure domain tests cover
fabricated invalid events unreachable from ordinary source preflight, and actual malformed source
is rejected before Runtime start. Persistent setup modifiers survive transient restoration; host
case/text interpretation is not guaranteed. No Unicode/DE/dead-key/host-lock/descriptor/report-ID
support. Synthetic eight-byte snapshots are opaque mock vectors, not physical keyboard behavior.

## Delay, deadlines and bounded execution

Delay produces no keyboard report. With no outstanding intent and Planner Ready, acknowledge it
immediately as a timing request; the serialized Runtime scheduler owns the wait from that accepted
clock value and prevents upcoming keyboard events advancing ahead. It does not start at initial
admission/Retry/press acceptance. Zero/two delays, delayed restoration, wrap and stuck clocks are
tested. Source Delay acknowledgment is not proof that the requested interval completed.

Planner256-attempt/30000ms caps and Runtime10000 instructions/100000 ticks/30000ms caps remain;
caller may narrow, not raise. A pending planner turn does not extend Runtime's elapsed deadline:
the driver invokes Runtime's original timeout path first when that deadline expires, before any
further report. Runtime tick/instruction budgets count Runtime turns/instructions, while planner
attempts count planner turns; no hidden repeated stepping. Caller clock is uint32 with existing
wrap assumptions. No actual sleep/wall-clock query or callback preemption. Existing numeric,
function continuation, control-flow, compiler and multiline semantics remain unchanged.

## Failure, completion, cancellation and explicit neutral recovery

Bridge error snapshots retain first reason/current event/planner reason/phase, then copy Runtime
error after propagation through its existing Failed-sink/error path. Report failure becomes
Failing for one bounded Runtime turn, never a fabricated Accepted. Invalid admission fails in
its original source callback. Source/callee/body diagnostics remain useful. Planner live getters
also describe later cleanup faults without replacing original source error. Runtime terminal kinds
Completed/Cancelled/Error are preserved; cancellation before script start leaves Runtime Idle.

Owner cancel/STOP/runtime errors clear ordinary intent and logical ownership, never accepted
snapshot evidence. Report callback cancel followed by Accepted still records that actual report;
Retry keeps prior evidence; throw/failure marks uncertainty. Cancellation after restoration but
before source ack still does not fabricate the source ack. Completion also clears owners, so
accepted persistent holds can remain nonneutral and block restart. No destructor report delivery.

Explicit drain is a separate bounded operation that publishes only zero. It completes only when
its OWN planner action leaves Working as Cancelled and neutral is confirmed, not merely because
an earlier zero report was accepted. New fault testing caught and fixed that stale-neutral gate
bug. Retry/error/cancel keep current drain unconfirmed; no scripts execute while draining. Restart
requires appropriate neutral evidence, synchronizes again and resets handshake/counters/runtime
state in fixed placement storage, with no allocating new or stale variable/event IDs.

Single-thread API; no mutex/cross-thread/self-destruction guarantee. Bridge must outlive callbacks;
Program remains alive while its owned Runtime/Program-dependent observations may reference it,
until next successful begin or destruction. Report context stays alive for any future step/drain
or is replaced after successful begin. Const inspection is not permission to mutate internals.
Blocking/malicious memory-writing callbacks are outside contract. No physical release assertion.

## Fresh actual verification

| Suite | PASS groups | FAIL | Assertions |
|---|---:|---:|---:|
| Stage27B complete regression | 25 | 0 | 2543 |
| Stage28A complete continuation suite | 23 | 0 | 526 |
| Stage28B complete multiline suite | 26 | 0 | 4733 |
| Stage28C complete reader/preflight suite | 17 | 0 | 390573 |
| Stage28D complete planner suite | 21 | 0 | 14989 |
| Stage28E new bridge suite | 24 | 0 | 109591 |
| Total | 136 | 0 | 522955 |

All six fresh suites pass ASan/UBSan and leak detection, preserving warnings-as-errors and pins.
Exact names/assertions/stdout/commands are in test-results.md/.json. Prior tests/runners are
unchanged, not recycled historical results. Historical production XPASS/XFAIL/observations remain
untouched; no skipped/XFAIL/XPASS in preview runners. Unsupported-domain rejection is not feature
support. Assertions include repeated budget/report invariants, not522955 distinct features.

New tests use actual Runtime, Planner and Bridge: initial sync; aa/AAA/ENTER neighbors; literal
US punctuation; multiline blank/TAB/ENTER; expression-called functions and IF/WHILE; wait-before-
ack counters;100 press plus100 release retries without replay; Delay timing after retries; zero/
two delays; uint32 wrap; full stuck-clock tick exhaustion; Prepared persistent SHIFT; held-tap/
rollover; failures/throws at press/restoration; cancel at all intent/Delay boundaries; callback
cancel Accepted/Retry/throw; explicit drain outcomes and exhaustion; source elapsed/attempt caps;
STOP/arithmetic/step limits; source/report reentry; compilation borrowing/multi-bridge ownership;
restart/destruction;40 seeded backpressure runs; callee body-line error; zero C++new on tested
normal pipeline. Prior500+400+150 source mutations and500 planner property operations freshly pass.

Development findings: initial nested helper main-macro collision fixed by including only the
Stage27B helpers; the drain-budget fault test revealed a real stale-neutral completion bug, fixed
in bridge code without weakening its expectation; null-source-context guard and source-line
checks added. Final24 new groups pass after all bridge code fixes. No unresolved unexpected failure.

Separate portable fixed-buffer smoke also PASS on Linux GCC ASan/UBSan/leak:9 exact reports,
4 keyboard acks and1 Delay. Not added to group/assertion totals. Native macOS/Apple clang is
SKIP_ENVIRONMENT: unavailable here (clang++ lookup/build failed); no native High Sierra execution
claim. stage28e-macos-smoke.md provides a manual host-only native Apple recipe without Linux
linker flags, assumed sanitizer availability, board access or installations. Optional Mac absence
is not a missing mandatory Xtensa/host verification tool. Physical host behavior remains untested.

## Target object-only provenance and resources

Pinned original/protected Arduino3.3.0, ESP-IDF5.5 SDK/config and Xtensa compiler/flags checks PASS.
Retain16MiB/QIO80/CPU240, PSRAM disabled, TinyUSB/USB-OTG/CDC compile configuration. Generate only
core.o, keyboard.o, bridge.o and unlinked size metadata object.72-byte readonly dump includes18
sizes; not USB metadata, descriptors, firmware ELF/BIN or a deployable profile. Exact commands,
source/dependency/object hashes and module frame estimates are in target-build/source-hashes JSON.

| Target sizeof | Stage28D B | Stage28E B | Delta |
|---|---:|---:|---:|
| Program | 6936 | 6936 | 0 |
| Runtime | 4872 | 4872 | 0 |
| CompileSession | 2408 | 2408 | 0 |
| Planner | 84 | 84 | 0 |
| Bridge | absent | 5020 | owns Runtime+Planner plus64B bookkeeping |
| Bridge Diagnostic | absent | 14 | included in Bridge |
| Program+CompileSession+Bridge | previous equivalent14300 | 14364 | +64 |

Do not add Runtime/Planner/Diagnostic again to Bridge. No adapter FIFO: one Event/intent, fixed
counters, two pointers and guards; no new writable globals. Report8/Owner7/OwnerTable28/Event4
and source Sink ABI are unchanged. Only the pure validUsage symbol extends Planner API; no
public existing field/layout or language behavior change. Placement reset clears fixed Runtime
storage directly, not a large automatic temporary.

| Selected object sections | Stage28D B | Stage28E B |
|---|---:|---:|
| Core text/literal/rodata | 13007/1856/1838 | unchanged |
| Planner text/literal/rodata | 2021/160/47 | 2063/160/47 |
| Bridge text/literal/rodata | absent | 1476/160/0 |
| All writable data/BSS | 0/0 | 0/0 |

These are module-only sections, NOT deployable flash/RAM/OTA usage or headroom measurements.
Bridge undefined symbols are existing Runtime/Planner, memset/exception support only; no USB/
Arduino/OS/storage API. No global toolchain or frozen firmware build modified.

Bridge step/runtimeStep/sourceSink/receive/report frames32B, begin/start/validEvent48B. Callback
forwarding adds about64B selected frames to the existing Planner step64B or Runtime tick112B
paths, plus validation/admission/helper frames. Bounded expression preparation remains roughly
1.5KiB selected frames before callers/libc; report path roughly128B before sink/exception costs.
No recursive report draining or task-stack/heap high-water/latency measurements. User callbacks
can add unmeasured work/allocation; zero-new claim covers only tested core hot paths.

## Freeze, remote refs and stop

All235 protected Stage26 files independently compare byte-identical to immutable baseline;
core source also independently compares to exact Stage28D. Historical docs/tests remain intact.
No production/Arduino Micro/partition/USB identity/startup/migration/recovery change or private
owner-file access. Original firmware remains OWNER CONFIRMED — AVAILABLE EXTERNALLY.

29 existing remote refs/branch heads were captured before publication, including Stage28D; all
are checked before/after pushing only Stage28E. No old ref is moved, rewritten or merged. Exact
file inventory, source/object/dependency fingerprints and freeze receipts are reviewable here.
No hardware discovery/access, physical operation, OTA, real keyboard output or owner payload.

Recommended next separate milestone: reference-backed mock source admission/preflight for a
reviewed persistent-ownership command subset and neutral/cancel contract. No Stage28F is started.
Outstanding limits: US model only; no transport/locale/Unicode/dead-key/lock feedback, host timing
or physical delivery proof; callback lifetime/single-thread and fixed compile/runtime memory caps.
**GO isolated offline review; NO-GO Stage26 integration, flashing/boot/OTA or real HID.**
