# Stage28I integration feasibility matrix — STATIC REVIEW ONLY

Baseline28857c2b1895f96a8e29c5fd69a69495237a1347. Source anchors/spans and SHA256 are in
stage28i-source-evidence.json, independently checked by tests/stage28i/audit_sources.py.
CONFIRMED = inspected source contract/mismatch, not physical validation. INFERRED = proposed
engineering implication. BLOCKED = insufficient contract/authorization. UNKNOWN = evidence absent.
Severity describes future integration impact, not an assertion that existing firmware is broken.
Line citations refer to unchanged repository or exact pinned dependency, not guessed interfaces.

## Actual interface inventory

- Preview Program: core.h:37–53, compile in core.cpp:410–413; noncopyable, fixed IR/text/symbols,
  ready only after successful compilation. CompileSession core.h:73–92/core.cpp:382–408 uses
  exact-size Reader with read/seek/context (core.h:54–69), bounded32-byte chunks/work, two passes,
  stable source contract and65536-step cap. Input8192B, line256B, code128, text4096B (core.h:6–9).
- Runtime: core.h:99–131/core.cpp:415–426,462–477,503–515; start/tick/cancel, pending Event4B,
  Accept enum and Sink callback (core.h:94–97), uint16 globals, expression/call continuations,
  caller-provided uint32 clock. Delay begins on accepted Event, source advances only on ack.
  Completion releases Program borrow but getters may still reference original Program; it must
  stay alive until new session/destruction or no further Program-dependent observation.
- Planner: keyboard.h:5–20,30–48; Report8B, four owners, six distinct nonmodifier keys/eight modifier
  bits. keyboard.cpp:29–48 atomic proposed union and fresh confirmed ownership operations;
  step/failure/cancel/drain:67–83. Retry does not advance pending report; cancel is logical only.
- Bridge: bridge.h:14–46 owns Runtime+Planner and callback context, not separate objects;
  bridge.cpp:15–28 start/sync/borrow,39–92 source window/intent/reentrancy/cancel/drain. One Runtime
  tick OR one report attempt; reports Accepted before source ack, no field-equality dedup of
  new identical events. Single-thread; context alive through future step/drain, prompt callbacks.
- Firmware: EvilDuckS3/duckscript.cpp:276–397 run/stop/update/File/preflight passes; com.cpp:392–451
  command dispatch/script-live arbitration and callbacks; com.cpp:454–578 report scheduler;
  EvilDuckS3.ino:114–123 main loop duckscript/update then com/update then CLI/delay1, guarded by
  startup profile/failure gates. These are two independent engines, not already integrated.

## Source-line-backed seams

| Seam / status / severity | Preview producer/contract | Existing production consumer / exact evidence | Mismatch / proposed future verification (NOT executed) |
|---|---|---|---|
| Report transport **CONFIRMED / critical** | ds_preview::Event/Sink core.h:94–97; Bridge turns events into Planner Report8 | hid_backend.h:27–31 beginReport/releaseReport; hid_backend.cpp:254–286 queueRaw | Event is NOT report; beginReport merges with backend-owned keys, not a verbatim snapshot sink. No public raw-snapshot API. Contract review must choose one ownership authority; cannot wire Bridge Sink to com::send or beginReport and assume byte equivalence. |
| Ownership ledger **CONFIRMED / high** | Planner four Owner records, sorted union keyboard.cpp:11–20,29–48; script owner3 bridge.cpp:24–25 | One global Owned in hid_backend.cpp:25–28; hold/release:288–318 | Four sources versus one global ledger; same-key owner release and ordering differ. Idempotent firmware hold can return true without enqueue at295, whereas confirmed preview commands demand fresh report. Future mock cases must model shared claims, unchanged reports, six-key rejection and competing live/script submissions. |
| Invocation vs acceptance **CONFIRMED / critical** | Bridge receive:43–61 Wait/Ackable; keyboard.cpp:68–77 | com::executeNow:434–451 accepts scheduled work; queueRaw:254–261 bool direct tud_hid_n_report; backend false also readiness/disconnect/in-flight at256,279 | HTTP/CLI 'Accepted', scheduler admission, USB queue accepted, transfer-complete and OS delivery are different. Review explicit adapter ack level and Retry/Failed classification, never convert void helper/API call to accepted output. |
| Completion correlation **UNKNOWN / critical** | Current one-intent current-report association; no real asynchronous completion queue | Patched core USBHID.cpp:331–335 report-complete wakes global semaphore, ignores report/id/instance parameters; SendReport:337–373 takes mutex/waits | Raw backend bypasses SendReport completion wait; no per-Bridge token exposed. Exact linked TinyUSB/DCD transfer/failure semantics and stale callback correlation need separately reviewed non-device evidence. Header declaration is not proof of linked-library transfer behavior. No second global callback may be introduced casually. |
| Descriptor/report ID/protocol **CONFIRMED mismatch; runtime UNKNOWN / high** | Planner eight bytes, no ID/descriptor/boot protocol | hid_backend.cpp:260–261 hardcodes keyboard ID; protected core USBHIDKeyboard.cpp:33–46 descriptor with keyboard ID; USBHID.cpp:348–362 selects effective ID0 in supported boot protocol | Direct queueRaw bypasses core wrapper's conditional normalization. Actual interface protocol depends on constructors: backend HID then Keyboard at12–22; core USBHID.h:75 defaults NONE, USBHID.cpp:282–290 initializes once. Current linked constructor/protocol/host negotiation not newly proven. This is a future protocol review gate, NOT a demonstrated physical defect or descriptor-change authorization. |
| Neutral/cancel/restart **CONFIRMED / critical** | Bridge.cancel:86–88 clears intent/owners; drain:90–92 plus81 requires current zero action; Planner accepted snapshot retained | hid_backend.cancelReport:347–353 immediately attempts zero then update:332–345 retries; com endScript:403–411 resets command state | Explicit preview drain versus automatic production clearing; zero snapshot can be merged with foreign owned state via releaseReport. Need future cancellation/queue-refusal/disconnect mock journal proving current action; no 'host keys released' claim while disconnected. |
| Delay/dwell/jitter **CONFIRMED / high** | Runtime.deliver:462–469 stores accepted Delay clock, tick:475–477 wrap subtraction; bridge.cpp:54 no report | com.waitFor:105–109, Wait:526–534 millis wrap; Press:550–555 adds5ms dwell; jitterWait:117–129; Finish:602–611 default delay | Sending Event Delay back through com duplicates clock ownership; preview has no production jitter/default-dwell behavior. One authoritative clock/timing layer required. Future mocked wrap/deadline/queue-delay tests must define policy before integration. |
| Progress/scheduler limits **CONFIRMED / high** | core.h:9 10000 instructions/100000 ticks/30000ms; planner256 attempts/30000ms; Bridge.step:71–84 one unit | ino:114–123; duckscript.cpp:348–354 uses256-byte/8-line budgets from config.h:44–45; production loop/call limits config.h:28–41 | Not equivalent budgets; preview30s total cap can reject long valid waits. Identify future fairness/STOP owner and work budget. No measured latency, IRQ scheduling or web responsiveness from object code. |
| Thread/ownership boundaries **CONFIRMED mismatch / critical** | Bridge single-thread guards (bridge.cpp:39–41,71–72), no mutex/atomic cross-thread promise | execution_guard.h:28–50 recursive RTOS mutex/portMAX_DELAY or TryGuard; webserver.cpp:549–566,573–585 calls com/CLI; CLI:193–207 | Can't expose Bridge callbacks/start/cancel directly to async web/USB tasks. Future proposal must serialize requests, callbacks and UI observation without lock inversion or unbounded lock holds; fixed handoff design not implemented here. |
| File reader/source stability **CONFIRMED / high** | Reader raw bytes Data/Eof/Retry/Error+seek, exact stable bytes, core.h:54–69; CompileSession:382–408 detached on terminal | storage.cpp:208 openRead; duckscript.cpp:291–305 owns File; script_source.cpp:7–75 line/64-byte chunk/size/position checks | Existing line Reader is not raw-byte Reader. Preview Program is compiled memory IR/text, not runtime streamed256KiB file execution. Need File-context lifetime, same-size mutation/removal/seek failure mock plan; no storage adapter exists. Source fingerprint is accidental-change detection, not authentication. |
| Input/capacity compatibility **CONFIRMED / high** |8192B source/256B line/128IR/4096B arena/32 symbols/16nest core.h:6–8 | config.h:12–53 source256KiB/line512/8192 lines/16vars/8blocks/128expr tokens | Preview rejects some previously supported files even if SD present; merely streaming compile cannot remove fixed IR/arena caps. Owner must explicitly select opt-in subset versus future capacity plan; do not silently replace whole parser. |
| Numeric policy **CONFIRMED / high** | core.cpp:113–127 rejects overflow/underflow,0^0; eager bounded expression continuations | duck_expr.cpp:135–165 truncates uint16 results, modular exponentiation;0^0 result1 | Source-derived examples:65535+1 production0 vs preview error;0-1 production65535 vs error. Not newly executed production comparisons or official-oracle claims. Semantic choice/regression fixtures needed; not an adapter-only issue. |
| Diagnostics/preflight **CONFIRMED / medium** | Error code+physical line/column core.h:11–16, core.cpp:416; raw text records:482–485; start requires ready | duckscript.cpp:68–79 includes path/callee/log+stop; run/preflight:276–397; API getters:341–344 | Typed preview errors need reviewed UI/log mapping, filename lifetime/truncation64B and physical line preservation; don't expose untrusted full source/credentials. Invalid compile must not start output. Future mock UI outcomes must distinguish preflight/run/transport fault. |
| Locale/Unicode/text **CONFIRMED / high** | Planner.mapUS keyboard.cpp:55–66; ASCII-only source; preview text interpolation not implemented | keyboard_locale.h:7–16, cpp:28–105 US/DE+conditional tables/UTF8/dead keys; com.cpp:569–577 interpolation/translation path and skipped-character warning | Direct preview US map bypasses locale handling and unsupported-scalar policy. Held modifiers intentionally OR into output, no host-case guarantee. Future opt-in subset/locale design required; no arbitrary Unicode support or host correctness claim. |
| Language/device extensions **BLOCKED / high** | Stage28F nonmodifier HOLD/RELEASE; modifier prefix/RESET blocked; no random/internal vars/storage/LED/ATTACKMODE | com.cpp:198–225 existing RESET/HOLD/INJECT_MOD engineering behavior; config/preprocessor, internal_vars and random modules separate | Existing firmware policy is not independent canonical oracle. No guessed prefix/RESET scope from reuse. Replacing dispatcher removes extensions/settings feedback; not full DuckyScript compatibility. Keep unsupported features rejected in future optional path. |
| Startup/settings/profile **CONFIRMED / critical** | Preview is never booted/armed; caller alone starts Program | ino:37–80 fail latches/safe return/controlled layout+settings+SPIFFS;88–111 HID/services; legacy autorun101–108; settings.cpp:52–64,125–177; spiffs.cpp:20–27 | Safe/controlled/legacy are distinct. Legacy allows examples/autorun/autoformat; controlled gates those and strict settings. Future integration must not bypass profiles, write settings or select an arming path. Checked saves not atomic. Existing Stage27A independent; no new boot authorization. |
| Partition/core/USB coexistence **CONFIRMED repository; physical UNKNOWN / high** | Unlinked object checks share pinned flags, not deployment | tools/s3_validation.py:14–43 core3.3.0/16MiB/QIO80/CPU240/PSRAMoff/USB0/CDC1 and CSV; build_s3_patched.py:18–31 isolated patches; attackmode.cpp:10–42 requested vs active MSC | Repo map standard app0+dual0x740000 confirmed unchanged. Historical installed map differs; current device layout/CDC/HID/MSC coexistence not rechecked here. No personality/descriptors/pins/table changes proposed. Full linked integration resource/constructor proof absent. |
| Web/OTA/staging surfaces **CONFIRMED / critical** | No network or update path in preview | webserver.cpp:369–388 application updater;685–695 update route/restart;549–566 live /send; CLI:193–207; tools/s3_validation.py:22–35 old/new geometry | App-only OTA is not partition migration nor bootstrap approval. Do not invoke it. Future supervised plan must block concurrent live commands/settings/uploads/OTA and establish artifact/recovery approval separately; no executable deployment plan in this audit. |
| Memory/lifetime feasibility **INFERRED; production margin UNKNOWN / high** | target Program6936 +CompileSession2408 +Bridge5020 =14364B; Bridge ALREADY includes Runtime4872/Planner84 | Static RunState duckscript.cpp:22–45; Session com.cpp:21–58; dynamic String/File and mutex allocations | Additive/replacement peak cannot be inferred from isolated objects. Need future placement/lifetime ledger including reader input/context, driver/UI, existing contexts and compiler stack; never allocate all large objects as nested loop-task locals. No production heap/stack/OTA headroom measured. |

## What acknowledgement can and cannot mean

1. Command/API invocation: code called or com::executeNow admitted work. NOT report acceptance.
2. Mock Accepted: fixture sink accepted current bytes; source acknowledgement waits for its required
   action(s). NOT USB activity.
3. tud_hid_n_report true: firmware treats this as enqueue acceptance. Need pinned linked-driver
   evidence to settle exact ownership/copy/refusal side effects, and separately specify adapter mapping.
4. Transfer-complete callback: USB stack event; current Arduino callback only wakes shared semaphore.
   It does not itself identify a preview transaction/session or prove OS/application interpretation.
5. Actual host key state/text: unknown without separately authorized supervised physical evidence.
   Even observed host response cannot retroactively make a disconnected release delivery guaranteed.

## Security/safety boundary for future review

Current work is source hashes, static reading, existing memory mocks and unlinked target objects.
No credentials, owner payloads/private backups, web request, device enumeration or USB/HID output.
Future gate C remains entirely synthetic, no network/OS shell. Future gate D is a DESIGN review
only after explicit authorization: owner supervises inert short text/neutral reports, approved
profile/artifacts, no autorun, no concurrent command paths, bounded STOP/recovery, no credentials,
stealth, persistence, exfiltration, destructive tests or host shell execution. Physical test
execution requires a further explicit approval; not granted by this matrix or Linux/native smoke.
