# Stage28X finite task, lock and failure map

Scope: the actual W composition plus X scratch delta; no installed package or
historical source is edited. Source hashes are in source-manifest and linked
receipts. Scratch line anchors are emitted by `audit.py`; installed framework
references below refer to those exact pinned files, not declarations alone.

| Context / actual implementation | Lock and lifetime order | Failure / evidence classification |
| --- | --- | --- |
| Arduino `loop`, `duckscript::update`, coordinator `tick` | Bound loop owner only; stepping rejects reentry. Publication Critical only fixed copies, never execution mutex or File/USB/log. Adapter and source have static lifetime. Tick backend calls can acquire recursive execution mutex outside publication. | SOURCE: single owner; native W/X progress under continuous serial. Actual core/priority starvation UNKNOWN until device. |
| CLI `update` / `parse` | After script/com in loop;64 read attempts,512-byte frame storage, reentry guard. Explicit `routeb` copied request, `stop` priority flag, new `diagnostics` fixed copy/format. Other legacy CLI holds recursive execution mutex. | SOURCE: arbitrary unread backlog delays STOP parsing. Native W15/X12 exercise bounded turns, not real CDC readiness. |
| AsyncTCP `_async_service_task`, `_get_async_event`, `handle_async_event` | AsyncTCP.cpp:237 pops under queue mutex; function returns/destroys guard before task:338 dispatches application callbacks. App TryGuard then short publication. Queue allocation and TCP-core operations use framework locks outside publication. | SOURCE: no app callback is dispatched with `_get_async_event` queue guard held. Queue growth, event coalescing, other TCP tasks and driver timing remain device unknown. |
| HTTP `/run`, status/auth, STOP, new `/routeb/diagnostics` | Request lifetime belongs to framework. Authentication cached String copy is protected by execution TryGuard; unavailable =>401/409 before unsafe snapshot. Start validates/copies path<=95. Diagnostic copy uses publication lock then releases it before snprintf/send. | NATIVE: authentication/try-lock refusal and pressure. SOURCE: slow network sends can retain response buffers; no synchronous-delivery assertion. Retry STOP via an available authorized local channel; never infinite request flood. |
| W dynamic readers, setters, File capture/verify | Mutation's TryGuard execution -> publication admission; short publication released before media/settings I/O. Same-task mutation nesting max32; transaction/chunk cleanup cannot be revoked mid-operation by STOP. Source capture and verify<=32 bytes/turn,8192 total, then File closes before Runtime. | SOURCE: individual File/VFS calls and NVS saves may block or fail/partially write. No timeout can safely retire a still-running lower call. X changes none of these semantics. |
| New owner diagnostic end hook | No publication lock during backend snapshot, three heap capability queries or current-task stack scan. Then fixed publication copy. End hook remains inside stepping scope; no second Runtime call. | NATIVE: unknown/zero resources, forbidden C++ allocations, sampling bounds. Target SDK allocation/scan locks and task timing unexecuted. Extra backend snapshot can wait for existing execution mutex; does not create reverse lock order. |
| HID backend and USB loss / feedback | Execution mutex protects owned/lease state. Separate feedback spinlock holds fixed data only; USB stop callback sets atomic loss and invalidates feedback without waiting on execution mutex. Owner later processes loss. | SOURCE + unchanged regressions: first-fault/permanent quarantine; no replay. Transport loss may leave host state unknown. Diagnostic observation never clears backend state. |
| Authenticated response construction | Pinned WebRequest.cpp:1208+ creates AsyncBasicResponse; WebResponses.cpp:261+ copies content. Diagnostic stack buffer does not escape; response owns its String. | SOURCE: allocation may fail in String/response/framework. Candidate does not claim OOM-proof network stack; native fail-all allocator proves owner telemetry path only. No network OOM repair or invented acknowledgment. |
| WebSocket / uploads / updates / static files | W restrictions retained: DATA fixed refusal, no frame parsing/CLI; no filesystem-backed async response even idle; upload/update/restart503. Immutable PROGMEM pointers live for app lifetime. | NATIVE W comparison + linked no AsyncFileResponse/wsOut/activeWsClient. Existing synchronous response buffers still use heap. |

Pinned framework implementation details: AsyncTCP.cpp:183–203 queue guard uses
portMAX_DELAY and private static task handle;331–357 service loop drains events;
385–400 mutex/task creation reports failure;429+ event allocation uses nothrow and
checks null at producer paths. Queue congestion is mitigated, not a bounded latency
contract. AsyncWebServer WebRequest.cpp:95+ deletes response,283+ disconnect callback
precedes shared ownership retirement. W correctly avoids treating disconnect as a
File lifetime fence. These source observations are not execution of AsyncTCP tasks.

No demonstrated new engine defect was found requiring a semantic fix. X introduces
observability only. Known risks remain: execution mutex first allocation uses
configASSERT; live legacy operations and synchronous media can stall; framework
response/event allocation and task creation can fail; repeated client pressure can
consume heap. No allocator, task scheduler or SDK was replaced to hide these risks.
Quarantine cannot be repaired by diagnostics or another Start. This finite map is
not a sandbox against injected SDK calls, unregistered writers or external media
changes. Actual framework/RTOS contention, driver failures and physical USB behavior
are NOT EXECUTED. Strict Route A retirement/host release is unresolved.
