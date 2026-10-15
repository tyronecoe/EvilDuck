# Stage28W reachable caller and lifetime matrix

Scratch filenames/line references are indexed in source/provenance receipts;
tracked production files remain unchanged. N = actual native app body; F = selected
framework source body; L = final linked evidence; P = physical execution. Every
row has P=NO. Network/File/NVS/clock/task/USB/NeoPixel boundaries are named mocks
in N. F does not mean whole AsyncTCP/FreeRTOS execution.

| Reachable entry / context | First effect and retained authority | Admission / cleanup | Evidence / remaining limit |
| --- | --- | --- | --- |
| `EvilDuckS3.ino:41 setup`, Arduino loop task startup | Existing NVS/layout/settings/mount/AP/HID initialization, before owner admission | Controlled profile unchanged: one attempt, validated credentials, no format/examples/autorun; W marker only | N actual enabled success; unchanged30 startup cases selector-off; L protected startup disassembly; actual SDK startup not run |
| `EvilDuckS3.ino:121 loop` | Bind loop owner, update script/com, then CLI | Same single portable owner; no new task, implicit Start or arming; return through existing delay | N actual loop with continuous serial; L call ordering and owner registration |
| `cli.cpp:335 parse`, local CDC/explicit API | `routeb` copies at most95 path bytes, queue reserves engine before capture | Existing owned/busy guard; status/STOP priority; no legacy fallback | N W12/15–20/23/27; V/U/T regressions; L publisher and owner tick |
| `cli.cpp:364 update`, owner task | At most64 read attempts; static partial line buffer | Owner-only, reentry refusal,512-byte limit, discard whole invalid/overlong line until LF; no retained request | N always-available/fragment/overflow/NUL/backlog/full queue; L513-byte buffer, no old String lineBuffer |
| `/run` GET, `webserver.cpp:189`, AsyncTCP callback | Auth snapshot; copied Mode/path or existing manual/legacy submission | TryGuard + publisher; request may die without invalidating copied path | N registered auth/run/busy; L handle/publisher; actual task dispatch unexecuted |
| `/status`, `/stop`, `webserver.cpp:466/446` | Typed snapshot / priority flag only | Nonblocking status; authenticated STOP, retry if auth snapshot unavailable | N preparing/quarantine/STOP plus inherited clearing cases; L; no host-release guarantee |
| `/script` GET and `/script/load` POST, `:570/588` | Open/read source synchronously, copy body | Mutation before File access through response construction; close before response outlives callback | N W04/05/28; F copied-vs-retained rules inspected; actual network teardown unexecuted |
| `/library`, `/list`, `/storage`, `:122/114/156` | Existing directory/source/stat reads | Synchronous Mutation,409 while Route B owns; no retained File response | N W05; L; lower VFS/driver is trusted, not sandboxed |
| `/script` POST, `/delete`, `:606/163` | Parent creation/truncate/write/remove | Existing synchronous guard spans actual lower write; admitted operation not revoked by STOP | N W22/26 plus V handler suite; L; partial writes remain possible |
| `/settings` POST, `/led`, `:255/512` | Cached settings, typed NVS writes/commit, LED changes | Existing Mutation, nested same-task scopes; first-error reporting | N V actual handlers/W22; L; existing multi-key save is not atomic |
| `/settings` GET, authentication, `:343/39` | Copy mutable settings Strings | New TryGuard snapshot prevents concurrent CLI setter/read race; contention denies before snapshot | N W33/34; L; no TLS or new WS authentication claim |
| `/exec/log`, `:144` | Copy existing protected log Strings | TryGuard plus existing recursive log guard; response owns copy | L; selected whole-handler behavior not separately native-tested |
| `/send`, `:645` | Manual com/backend submission | Existing Mutation and fast scheduler/backend permission checks; rejects competing owner | N inherited V10; L; lower USB fake in native tests |
| Not-found/static, `:700` | Built-in immutable PROGMEM data only in candidate | Unknown/dynamic FS path503 **even while idle**; never call `send(FS,...)` | N W01–03; F Progmem chunks; L no AsyncFileResponse symbols |
| `/ws`, `:674`, AsyncTCP WS events | Fixed rejection text for DATA, none for CONNECT/DISCONNECT | No CLI dispatch, frame decode, borrowed client state or app reservation | N real registration, malformed/oversized/disconnect cases; L no activeWsClient/wsOut |
| File upload/update chunks and completions, `:364/419/451/458` | Refusal response only | Always503 when enabled; no streaming token or lower operation | N W21 real registrations/callbacks; L; no OTA/reboot/USB update |
| Direct `settings`, `storage`, `spiffs`, `sd_card`, `led`, library calls | Cached mutation/NVS/media/GPIO at module body | V guards unchanged; open writable stream excludes Start | N V direct calls, W22/29; L; raw unregistered File/SDK calls explicitly excluded |
| MSC begin/update/end + registered read/write/start-stop | Media state/File cursor/I/O | Existing synchronous guard; requested/preparing/active media blocks Start; stale callbacks refuse | N V actual MSC callbacks/W30; L; TinyUSB host traffic not executed |
| Personality/locale setters, com live/script callbacks, actual backend | Mode/key/report state | Existing fast permission and execution guard, no mutation by competing session | N unchanged V/U/T; L; local acceptance is not host ACK |
| USB stop/feedback callbacks, pinned core/CDC/TinyUSB | Existing bounded loss/feedback observation; no owner stepping in callback | Owner processes loss; permanent called-false/loss quarantine, first fault/no retry | N synthetic callback/loss regressions; L protected HID/NVS core; real event timing unknown |
| AsyncBasic/Progmem response/request lifetime | Network buffers owned by response or immutable static data | No media mutation authority retained by app after handler returns; request may retain response until teardown | F selected class bodies/source analysis; L actual framework compiled; full task/error/OOM lifetimes unexecuted |

No `serveStatic` registration, retained application filesystem response, arbitrary
file include or extra producer model is introduced. Source index/search supports
this finite inventory; it is not proof about every potential SDK caller. Arbitrary
code injection/unregistered writers are outside the declared boundary. Actual
framework paths remain in the runtime review, not dismissed as hypothetical.

Runtime integration remains NO-GO pending separately reviewed actual-task/network
cancellation/error/OOM and lower-driver behavior for the linked configuration.
The evidence here supports an offline BUILD REVIEW GO; it is not a demonstrated
current handler bypass or a target runtime failure. Physical deployment is NO-GO.

The newly linked coordinator/Adapter storage is static and default-initialized:
Program/CompileSession/Runtime constructors are defaulted (`language_preview/core.h`),
and the FileSource starts with an empty File. They do not arm an engine or perform
media/HID/NVS operations in their construction. Existing SDK/USB/CDC constructors
still precede application setup; this is not a new early-boot immutability proof.
