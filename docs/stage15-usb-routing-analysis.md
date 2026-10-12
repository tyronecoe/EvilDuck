# Pinned USB routing findings and evidence

Scope: Arduino ESP32 core3.3.0 and ESP32-S3 qio_qspi SDK
idf-release_v5.5-b66b5448-v1. Exact source/archive hashes:
[upstream record](stage15-upstream-sources.json). No installed dependency, firmware
HID backend, descriptor, USB personality or MSC implementation changed.

## Actual boundary

USBHID.cpp stores devices/report IDs in a fixed10-device registry. The keyboard's
report ID is1, eight-byte IN payload and one-byte LED OUTPUT (Num/Caps/Scroll/
Compose/Kana plus three padding bits). LED feedback accepts the first three bits
as observed values, permits descriptor-defined bits3/4, rejects padding5..7 and
requires an exact one-byte normalized payload and live USB session.

The actual callback bodies and actual report-ID lookup/dispatch helpers are extracted
from the installed source for tests, with source SHA verification. The production
FeedbackKeyboard receives these through mocked endpoint/registry adapters. Full
Arduino descriptor allocation, RTOS/TinyUSB controller and physical bus are not compiled
by the slice harness; no stronger robustness claim is made.

| Finding | Evidence | Shipped status |
| --- | --- | --- |
| ID0 empty/null extraction | Callback calls buffer[0], buffer+1, bufsize-1 after report0 lookup fails; sanitizer null/onepast probes reproduce unsafe reads | Upstream; remains unfixed in installed/shipped core |
| Zero valid transfer with allocated backing | Realistic64-byte backing buffer and size0 forwards size65535 after unsigned narrowing; actual downstream receiver rejects it | Logical length underflow proved without claiming a physical memory crash |
| Nonzero control OUTPUT | Actual callback dispatches to _onSetFeature, discarding OUTPUT/FEATURE distinction | Stage12 workaround delivers ordinary control LEDs but cannot authenticate report type |
| FEATURE/INPUT/invalid types | ID1 valid byte reaches same FEATURE hook and is accepted as LED by shipped workaround | Proven boundary behavior; not evidence of physical malicious traffic |
| Invalid HID instance | Core callback ignores instance; manually invalid255 still dispatches | Source/API issue; real controller normally supplies valid class instance |
| Debug type-string indexing | Unknown ID/type255 indexes a four-element log table; sanitizer reproduces when debug arguments evaluated | Debug-only concern; pinned default logging is off |
| Stock keyboard hook | _onOutput dereferences buffer[0] without null/length guard; stock sanitizer probes fail | EvilDuck already bypasses it with Stage12 derived handler; not a new firmware defect |
| Stock event posting | portMAX_DELAY passed to Arduino event queue | Policy observed; actual queue-full stall not reproduced |
| Received IDs/length/padding | Valid ID-prefixed interrupt normalizes once; ordinary nonzero control byte reaches receiver; malformed normalized lengths/padding reject | Production-source tests pass, no host compatibility proof |

Null/onepast callback probes are API safety reproductions, not demonstrations that a
physical host can choose a C pointer. The installed SDK has64-byte HID buffers. A
zero-length actual transfer can still have valid allocated storage, so callback
logical overread/underflow does not by itself establish an on-wire ASan-equivalent
crash. Unknown normalized payloads cannot be treated as trustworthy feedback merely
because memory exists. Do not report malformed-USB robustness from downstream checks.

## TinyUSB boundary and execution context

Installed headers report TinyUSB0.18.0. hid_device.h declares SET_REPORT for control
and interrupt OUT (ID0, OUTPUT). Supporting tagged upstream hid_device.c verifies
control request length against CFG_TUD_HID_EP_BUFSIZE, strips an ID only for a matching
nonzero requested ID with length>1, then supplies ID/type/normalized length. Interrupt
OUT supplies ID0/OUTPUT and transferred bytes. This source is supporting evidence,
not certified byte-identical Espressif SDK source. The installed libarduino_tinyusb.a
was independently inspected: relocation/call sites in hidd_control_xfer_cb and
hidd_xfer_cb reference the actual tud_hid_set_report_cb symbol. Source/archive hashes
identify what was examined; no physical controller or complete linked-source execution.

esp32-hal-tinyusb.c usb_device_task loops tud_task and documents invoking callbacks.
These callbacks are task-context, not an invented ISR callback. USB.cpp posts mount/
unmount/suspend/resume events with portMAX_DELAY to a separate Arduino event loop.
Event delivery can lag and full queues could block; this is a source-derived latency
concern, not an executed RTOS contention finding. SET_IDLE/SET_PROTOCOL also post
blocking event requests. The proposed SET_REPORT patch does not solve every event
or descriptor allocation issue in the stack.

EvilDuck's receiver takes a dedicated short feedback portMUX section for fixed copies/
bit counters, never the executor lock, filesystem, sends, logs, allocation or event
queue. USB-stopped listener sets the atomic loss flag and invalidates evidence; main
update also polls mounted-state loss. Snapshot counters retain rapid/repeated-state
transitions. Existing Stage12 concurrency/session tests and Stage11 release tests
remain passing under ASan/UBSan; no RTOS high-water or ThreadSanitizer certification.

Feedback is independent of persistent IN ownership; actual routing during a held
Ctrl/delay fixture updates observed state without releasing keys, and STOP clears
ownership normally. CDC/MSC share the controller/task: a callback/event-loop stall
can delay all classes. Stage10 transfer bounds/offsets/short-I/O quarantine and
nonblocking lock admission remain unchanged. ATTACKMODE is truthful logical/media
state, not re-enumeration; MSC success is not host mount/filesystem verification.

LED reports carry no session/transaction epoch. Captured stale tokens reject, but a
packet first delivered after reconnect cannot identify its previous origin; a matching
transition is evidence of observed state, not proof caused by our injection. Passive
values have no age timeout; they represent last observed evidence. Mac Num/Scroll and
control-versus-interrupt report behavior remain physically unknown.

## Paired proposal, not active mitigation

[Core proposal](../proposals/arduino-esp32-3.3.0-hid-routing.patch) guards instance/null/
OUTPUT length before extraction, preserves type and rejects INPUT/invalid dispatch,
and avoids unsafe log indexing. [Companion](../proposals/evilduck-hid-feature-companion.patch)
removes the FEATURE-as-LED workaround once the core routes OUTPUT correctly.
Both are applied/tested only in temporary copies. Core-only still accepts FEATURE
via the firmware workaround; companion-only loses legitimate control OUTPUT on
unpatched3.3.0. Neither installed core nor shipped firmware was modified.

The proposal preserves report0 payloads and supports valid ID-prefixed interrupt and
nonzero-ID control OUTPUT. Generic zero-length FEATURE remains device-defined;
EvilDuck advertises no LED FEATURE and the companion inherits a no-op hook. A reviewed
follow-up requires full patched-core compilation, dependency pin/hash/wrapper/IDE
strategy, all report/device types and logging configurations, descriptor allocation/
bounds review, and separately authorized normal-host validation. No entire stack
vendoring, weak-symbol replacement or linker shim is silently introduced.

## Results interpretation

Baseline Stage1–14 passes remain separate. New passing routing cases include
unpatched valid behavior and temporary paired-proposal behavior; they do not imply
the current binary contains the patch. Seven unchanged-bad-routing/policy observations
are matched separately. Six sanitizer faults are explicit upstream XFAIL, not hidden
failures or historical language XFAIL relabeling. Stock fault probes remain expected
upstream defects, even though the firmware bypasses that stock hook.
