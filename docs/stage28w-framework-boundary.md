# Stage28W supported framework boundary and lifetime evidence

This owner instruction expressly permits an offline link without excluding every
conceivable raw SDK/VFS caller. It does not retroactively pass V's earlier gate.
The supported boundary is the enumerated application entry points in this selected
controlled build, the existing portable owner, and the pinned framework APIs they
use. Arbitrary injected code, unregistered SDK writers and external media changes
are excluded assumptions, not newly blocked capabilities. Historical V48 remains
a valid raw-File capability observation; it is not an escaped enabled handler.

Pinned consumed packages are ESP32Async ESP Async WebServer3.12.1 and Async TCP3.5.0.
Their `library.properties`, complete file inventories and deterministic tree hashes
are in the source manifest. No Git revision is present in these installed library
copies; a publisher version/hash is not invented as a commit attestation. Actual
compile commands select these directories, and final map/object/archive provenance
records their linked implementation. No package is downloaded or modified.

Primary evidence paths, relative to ESP_Async_WebServer/src:

* `ESPAsyncWebServer.h:652–660`, `WebRequest.cpp:1208+`,
  `WebResponses.cpp:261+`: a normal String response constructs AsyncBasicResponse;
  `_content = content` owns a String copy. It does not retain the handler's local
  String or File. W's synchronous source read closes its File before returning
  the body; admission spans response construction. Response/network buffers may
  remain asynchronously owned by the framework after handler return.
* `WebResponses.cpp:722+` opens File in AsyncFileResponse; the File constructor
  overload at781 retains it in `_content`; `_fillBuffer` at817 reads later.
  `WebResponseImpl.h:122–145` closes the File in the **response destructor**.
* `WebRequest.cpp:95+` destroys the response from request destruction.
  `_onDisconnect:283+` calls the user disconnect hook **before** moving the `_this`
  shared pointer toward destruction. Other strong references can delay destruction.
  A disconnect hook, handler return or timeout is therefore not a File-cleanup ACK.
* `WebResponses.cpp:893–905`, `WebResponseImpl.h:192+`: Progmem response retains
  a const data pointer and an index. App `webfiles.h` arrays are static const
  PROGMEM for application lifetime; no template callback is supplied by these
  routes. This is a suitable lifetime for the retained immutable pointer.
* `Async_TCP/src/AsyncTCP.cpp:331+` dispatches queued events in `_async_service_task`;
  request/ack/disconnect callbacks use this path. Native fake tasks and network
  registration are not execution of this FreeRTOS/AsyncTCP task.

Chosen small restriction: **filesystem-backed static responses are disabled for
this compiled candidate at all times**, including idle/legacy execution before
Route B admission. There is no accepted asynchronous File to reserve or retire.
The compiled selector cannot hot-switch inside the process; a previously running
legacy firmware's HTTP objects cannot migrate into this process. Native W01/02
prove no File opens or responses; the enabled final ELF contains **zero
AsyncFileResponse symbols**, versus nine in the selector-off link. Built-in
immutable pages remain. No guessed completion hook, timeout release or fake lease
is added. Raw external File handles remain outside this boundary.

Synchronous dynamic script/list/library/storage requests acquire the existing
Mutation guard before opening media or copying mutable metadata. They finish File
work before an engine reservation can start; response construction copies the
body, so it may outlive that guard without retaining media access. Denied work
returns409 before the lower action. Existing settings and log snapshots are also
serialized; authentication snapshots fail closed if the mutex is unavailable.
An authenticated HTTP retry can then succeed. This does not promise instantaneous
HTTP STOP while authentication cannot safely snapshot settings.

WebSocket CLI dispatch is disabled in the enabled profile. The actual registered
callback sends a fixed503-equivalent refusal for DATA without reading frame data,
calling CLI, or retaining a client pointer. CONNECT/DISCONNECT are no-ops at the
application boundary. Existing framework handshakes/frames still occur; this is
not USB-detached or network-detached behavior. Selector-off retains legacy WS policy.
Authenticated HTTP selection/status/STOP and local CLI remain the supported paths.

Uploads, firmware chunks, their completion callbacks and restart stay503, with
no File/Update/reboot action. All these restrictions are compile-time candidate
policy, not new language grammar, an authentication protocol or automatic arming.

Selected exact File/Progmem classes, constructors, read and destructor bodies run
natively in five component tests. Abstract-response/File boundaries are mocked;
MIME inference is deliberately an unexecuted throwing stub. Request disconnect
ordering is inspected source and illustrated, not actual request-task execution.
No test proves actual AsyncTCP cancellation races, RTOS scheduling, OOM behavior,
physical media stability, USB delivery, endpoint retirement or host release.
