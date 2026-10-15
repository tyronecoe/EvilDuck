# Stage28T producer and lifecycle inventory

Line references below identify unchanged parent sources; scratch patches are
separately hashed. Execution contexts of asynchronous services are not certified
by these host tests. An intercepted callee does not establish service ownership.

| Source / symbol | Native disposition and remaining boundary |
| --- | --- |
| `EvilDuckS3/com.cpp:386–451`, callbacks, begin/end, busy, send/sendText/executeNow | S seam retains callback slots, rejects foreign ingress, makes busy cover idle lease gaps; T30/T32; scoped native drive only |
| `com.cpp:454–624`, update and press/wait/release | Actual scheduler executes with T scoped backend permission; external/reentrant update denied during lease; delay/dwell retained |
| `hid_backend.cpp:254–289`, queueRaw, beginReport/releaseReport | Actual validation/Owned merging and fixed instance0/ID1/eight-byte submission; typed post-call result, quarantine and permission checks |
| `hid_backend.cpp:290–318`, hold/release | Denied before state changes during lease; existing persistent Owned state blocks acquire; legacy semantics unchanged when disabled |
| `hid_backend.cpp:320–353`, hasPersistent/clearing/error/loss/update/cancel | Read access retained; mutation scoped. Quarantine suppresses further lower calls; first fault retained; T23–T29/T38/T43 |
| `hid_backend.cpp:246–252,356–401`, raw modifiers/held/report/key/named/text/release helpers | All mutating helper entry points rejected during lease. Outside lease, raw Keyboard use conservatively latches unobserved software ownership; T31/T32/T47 |
| `hid_backend.cpp:123–129`, begin | Lifecycle reinitialization denied while leased; no callback registration replacement |
| `hid_backend.cpp:49–54`, USB stopped event; FeedbackKeyboard | Real stopped callback sets existing atomic loss/evidence invalidation; actual backend consumes it under scope. Host invokes callback synthetically. HID OUT routing/real USB callback thread not executed |
| `duckscript.cpp:276–310,317–339`, run/stop/update | Actual run refuses com busy (T30). Script stop is not the native Adapter API; production stop/dispatch must explicitly route to owner, not presume legacy callback completion |
| `duck_keys.cpp:94–104`, direct legacy chord helpers | Calls reach guarded backend helpers; no independent core access through this module |
| `keyboard_locale.cpp:14–18,47–50,111–128` | Setters remain available. T detects changed identity on next step and stops source. Translation executes actual locale table; write helpers reach guarded backend. Concurrent mode mutation prevention is not implemented |
| `attackmode.cpp:10–42`, HID/storage mode setters/update | Source inspected only; host fake getters/setters used. HID changes tested, real MSC/USB personality lifecycle unexecuted and outside lease |
| `cli.cpp:193–207`, run/stop/send; `webserver.cpp:171,549–566`, send | Actual CLI links; ingress ends in guarded com. Real network/CLI task scheduling not executed |
| `cli.cpp:115+`, settings; `webserver.cpp:247–294`, settings/layout | Not intercepted as complete transactions. `duckscript::running()` can be false while native lease active. Production integration must reconcile owner checks |
| `webserver.cpp:369–388,685–695`, Update/write/restart; file/storage routes | Read-only inventory only; no native producer or flash test. OTA, file mutation and settings services remain production integration blockers |
| `EvilDuckS3.ino:37–80,88–123`, startup, HID and loop/services | Source inspected, not executed. No startup profile, scheduling or autorun changes; future explicit dispatch required |
| `execution_guard.h:28–54` | Actual host recursive mutex used, including T34 foreign thread. Target recursive RTOS mutex/portMAX_DELAY, callback task affinity and contention latency unexecuted |
| Direct `USBHID::SendReport`, `tud_hid_n_report`, USB begin/end, CDC/MSC/core/DCD | External callers bypass this source-local lease; no complete production ownership claim. Shared semaphore is not correlation; no core/DCD patch |

The legacy raw ledger gap is source-backed: pinned Arduino 3.3.0
`libraries/USB/src/USBHIDKeyboard.cpp:202–210` clears `_keyReport` keys/modifiers
inside releaseAll. That source was read and hashed, not executed as the actual
USB class. Tests use the existing lower Keyboard platform mock. T47 checks the
backend's conservative latch, not physical host software state.

Only a future separately reviewed integration can unify real web/CLI/storage/OTA
ownership, task-affine drive, lifecycle changes and direct-core bypass exclusion.
An arbitrary caller able to invoke the internal owner API with its known IDs is
outside the non-adversarial module contract; the lease is not a security sandbox.
