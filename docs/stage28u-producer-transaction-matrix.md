# Stage28U producer and transaction matrix

References identify unchanged parent sources; the exact scratch delta and final
output hashes are in the manifest. A compiled object is not an executed handler.

| Path | Candidate disposition | Evidence / remaining limitation |
| --- | --- | --- |
| `duckscript.cpp:276–339`, run/stop/update/running | Explicit RouteB API, preparing/clearing busy, engine-aware STOP and owner update; legacy default | Actual native dispatch, target object |
| `com.cpp:386–454`, live/script/callback/update | Portable fast permission before guard, scoped owner progression, legacy callback/timing preservation inherited | Actual native and default-off comparison |
| `hid_backend.cpp:246–401`, report/held/raw/update/cancel | Portable lease before mutation; typed outcome and permanent ambiguity/loss quarantine retained | Actual backend native; target object; USB lower fake |
| `hid_backend.cpp:49–54`, USB stopped | Bounded loss publication only, owner handles quarantine | Actual callback synthetically invoked; real event context unexecuted |
| `cli.cpp:319–326`, parse | During RouteB: exact stop/status accepted, other input rejects before String/command execution; legacy behavior otherwise | Actual native CLI U35/U59; broad unsafe legacy commands not executed |
| `keyboard_locale.cpp:10–50`, begin/setters | Reject during ownership before guarded mutation; recheck under execution guard | Actual native mode tests and target object |
| `attackmode.cpp:10–42`, begin/setters/apply/cancel | Same immutable session policy; actual state machine, lower MSC stub | Actual native U44/U48; no real MSC/personality operation |
| Existing MSC requested/active/preparing state | Start/service admission rejects conservatively even without a token | Actual attackmode getters over mocked lower media, U62–U64 |
| `storage.cpp:73,149,174,196,369`, mount/remove/write/append/copyToSd | Service transaction before first mutation; copyToSpiffs reaches guarded writeFile | Target object only; native startup regression is selector-off, not enabled handler proof |
| `webserver.cpp:216,handleSetLed`, settings/LED | Transaction around synchronous handler before mutations | Target object only; network/task execution not tested |
| `webserver.cpp:318,369,685+`, file/firmware upload and restart | Fail closed with503 in enabled offline candidate; no writable upload/restart transaction implemented in network callbacks | Target object only; generic Token/chunk API tested separately, no claim real uploads pass |
| `webserver.cpp:139,handleSaveScript`, file edits/deletes | Actual storage writer admission is intended lower boundary | Object compilation only, auth/network lifecycle still needs review |
| `webserver.cpp:162,391,549`, run/status/send | Existing calls reach engine-aware duckscript/com; no RouteB HTTP selection added | Backend/dispatch native; whole web handler object compiled, not native-executed |
| `EvilDuckS3.ino:37–123`, startup/loop | Existing safe/controlled/NVS gates preserved; owner registration only in operational loop | Startup regression unchanged; candidate target object; no startup executed on target |
| Direct settings/spiffs/sd_card/usb_msc/core APIs and raw USB lifecycle | Can bypass selected wrappers; not certified excluded | Explicit production integration blocker |

The generic transaction API exercises Settings/Files/Layout/Hid/Storage/Upload/
Ota/Restart admission and token/chunk lifetime without executing those hardware
operations. A model/API gate test is not a network handler PASS. Network uploads
are deliberately unavailable in this enabled candidate rather than trusting a
one-time running check across callbacks. A future real handler must own a bounded
request context/token, call enter/leave around each chunk, and defer abort until
all admitted work has left. No borrowed request/payload pointers may outlive a
callback, and pointer equality alone does not establish callback identity.

Direct settings callers outside the guarded web/CLI wrappers, direct storage/
MSC/core calls, unreviewed restart/remount routes and cross-task lifetimes remain
blockers. The candidate does not claim complete production producer exclusion.
Nothing changes production USB descriptors, identities or partition geometry.
