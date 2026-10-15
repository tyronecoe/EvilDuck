# Stage28V producer and handler evidence matrix

Line numbers below refer to exact **scratch outputs**, not edits to tracked
firmware. Reproduce with `prepare_sources.py`; all19 output hashes and56 patch
hunks are in the source manifest. Source index/body receipts are supplementary,
not inferred runtime coverage. No row is linked into a controlled candidate.

N = real native body executed over named lower mocks; O = pinned target object
compiled; L = linked candidate; B = unverified/blocked boundary. N/O are cumulative
columns, not equivalent forms of evidence.

| Actual entry / caller | Context and first effect / boundary | Native evidence | N | O | L | Remaining B |
| --- | --- | --- | --- | --- | --- | --- |
| `webserver.cpp:172` handleRunScript, `/run` registration | Network callback; copied request before engine ownership, nonblocking execution probe; authenticated HTTP | V01 registered route, V03 busy, V37–40 bounded/mode/auth | yes | yes | no | Actual network task and request transport lifetime |
| `webserver.cpp:446,426` status/STOP registrations | Status copies snapshot; STOP only publishes flag; no borrowed callback retained | V04/31/32/33/34/35/46/51/56 | yes | yes | no | Network delivery of reply is unproven |
| `webserver.cpp:580,146` save/edit/delete | Synchronous Mutation before parsing or opening/truncating/removing | V06/07/14/47/52/54 | yes | yes | no | Partial writes not atomic; SDK raw handles outside wrapper |
| `webserver.cpp:238,492` settings/LED | Mutation through actual typed settings/save and actual NeoPixel setColor | V08/09/15/16/53 | yes | yes | no | NVS/LED lower APIs simulated; multi-key save not atomic |
| `webserver.cpp:619` send line | Mutation rejects before com/HID; legacy flow stays available while idle | V10; legacy commands separately covered in production comparison | yes, denial | yes | no | HTTP transport and legacy network authorization |
| `webserver.cpp:344,399,431,438` file chunks / firmware chunks / both completion callbacks | Enabled candidate returns503 before open/write/Update/restart on every callback, including no-data completion | V11–13/55, both fwUpdateOk values | yes | yes | no | SDK upload/update code deliberately unreachable in enabled path |
| `webserver.cpp:646` onWsEvent → CLI | Frame bound/null rejection, synchronous CLI scope; existing execution mutex serializes active client pointer | V45/50; no client pointer retained by new coordinator | yes, selected paths | yes | no | Real callback/disconnect concurrency and existing WS authentication not closed |
| `webserver.cpp:717,733` prepareControlledNetwork/begin | Mutation before WiFi mode/AP or handler registration | Fixture startup and V49 owner denial | yes | yes | no | Mock WiFi/server only; no AP/TCP/TLS execution |
| Web library/load/static/file-response handlers | Existing read-only paths; load fallback can reach guarded storage.writeFile | Included in native TU; not invoked as individual requests | no | yes | no | Async File response lifetime/read effects remain unexecuted |
| `storage.cpp:80,163+,195+,224+,388+,408+` begin/remove/write/append/copy | Mutation spans mount/parent creation/open/truncate/write/remove, nested guards share admitted task | V21/25; V01/02 actual FileSource | yes | yes | no | Lower FS mocks; raw aliases not fenced |
| `spiffs.cpp:23` begin; create/remove/rename/append/format/stream APIs | Mutation before SPIFFS calls; existing open stream refuses Start; no writes admitted during ownership | V19/24/25/26/27/28/29/30/52 | yes | yes | no | External/raw VFS changes cannot be excluded; V48 boundary observation |
| `sd_card.cpp:32` begin, mkdir/remove/rename/write/append | Mutation before mount or writable File; explicit `sd:` stays selected | V02/20/25 | yes | yes | no | Removable hardware and driver calls simulated |
| `usb_msc.cpp:52,68,85,103,119` read/write/start-stop/begin/update/end | Guard before cursor or media state effects; stale callbacks return busy/refuse; actual pending/active state blocks Start | V22/43/44 | yes | yes | no | USBMSC/VFS lower fakes; no TinyUSB task or host traffic |
| `settings.cpp:55+,132,load/setters/resetChecked` direct public mutation | Mutation before cached changes/NVS open; save error not substituted with success | V17/15/53; selector-off startup comparison | yes, listed paths | yes | no | SDK NVS recovery not executed by this harness |
| `led.cpp:38,47` begin/setColor | Mutation before actual NeoPixel methods | V18/16 | yes | yes | no | GPIO/electrical action mocked |
| `script_library.cpp:64` installIfNeeded | Mutation before loop or marker File; no bundled example body executed in tests | V23 denial | yes, denial | yes | no | Real installation deliberately not exercised |
| `cli.cpp:323` parse; serial/WS callers | Copied bounded routeb prefix, ordinary run legacy; exact status/STOP during ownership | V02/05/32/45, immutable U/T and production comparison | yes, parse | yes | no | Serial update drains available bytes in an existing unbounded loop; real CDC concurrency not run |
| `duckscript.cpp` run/runRouteB/stop/update/status | Existing U dispatch preserved; old backend paths reserved while queued/capturing/clearing/quarantined | V01/02/04/31–36, unchanged U64 cases | yes | yes | no | File/VFS and target scheduler waits are not hard bounded by native success |
| `com.cpp`, `hid_backend.cpp` report/held/raw/live/helper entry points | U fast task/permission guard before potentially blocking execution mutex; typed lower outcome, no ambiguous retries | V34/35/36, immutable T47/U64 | yes | yes | no | HID lower queue fake; no transport acceptance/retirement proof |
| `attackmode.cpp`, `keyboard_locale.cpp` setters and apply | Existing U immutable-session guards retained; actual MSC state queried | U44/U48 and V43 | yes | yes | no | Personality/locale physical behavior not executed |
| `EvilDuckS3.ino` setup/loop | Existing safe/controlled/layout/NVS/credentials/storage/autorun gates unchanged; bind only operational loop | 30 unchanged startup cases on original and selector-off patched sources; enabled owner loop body not executed | partial, selector-off | yes | no | Enabled full firmware task/startup not linked/executed |
| Core USB/CDC/TinyUSB, raw File/NVS/flash/driver lifecycle | Starts before app ownership or operates under SDK/framework APIs; no new SDK policy installed | Read-only source/pin audit; V48 proves raw VFS can bypass wrapper admission in native boundary | no | declarations only | no | **BLOCKED**: no complete core/framework producer exclusion or asynchronous lifetime attestation |

MSC callback registration is actual production code; only USBMSC and SD/File are
fakes. Report generation is actual com/backend; only lower readiness/submission
is fake. Settings code is actual; its typed NVS API is fake, not an SDK emulator.
The FS fake uses a single memory map with distinct `/x.txt` vs `/scripts/x.txt`
paths: it establishes exact selection through these APIs, not independent physical
volume semantics. Fake request send/registration does not execute AsyncTCP.

V48 is a deliberate boundary observation: a raw writable File obtained outside
the wrappers can change the memory filesystem while Route B owns admission. It
does **not** establish that a currently enabled web handler bypasses its guard.
The absence of a source-index match is also not a proof no SDK writer exists.
No row is certified as complete production service isolation.
