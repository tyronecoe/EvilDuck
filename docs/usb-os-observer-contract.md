# USB-only milestone: one bounded capture stage

**CAPTURE ONLY — NO OS CLASSIFIER — NO AUTOMATIC HID OUTPUT.**

Before this candidate is built, this contract fixes what it captures and which
question the evidence can answer. The owner selected a USB-only EvilDuck-specific
path, allowed one capture stage if existing data is insufficient, and required
the working identity, keyboard and recovery path to remain intact.

## Evidence gate and purpose

[The existing-evidence gate](usb-os-evidence-gate.json) finds no supported positive
High Sierra USB rule. Existing typing/LED results and the installed HID trace do
not contain early SETUP sequences. The pinned official counter heuristic does
not establish its own runtime contract or an independent High Sierra signature.
No additional broad research, compiler investigation or OS probe is needed to
justify this one missing observation.

**Question:** Which early request-header and ordering features, if any, support
a reproducible positive High Sierra profile under the unchanged EvilDuck USB
descriptors? Capturing the owner's known Mac supplies observations and
repeatability evidence; it does not prove uniqueness across operating systems.
Developing and validating a rule on the same sample is insufficient.

No detector API, canonical Hak5 counter, OS constant, manual OS label or fake
classification is added in this capture stage. Exports explicitly say UNKNOWN /
NO_VALIDATED_RULE. A complete detector-and-branching release follows only if
independent justification and held-out observations support a positive rule.

## Exact capture boundary

Observe only USB port 0. Per selected SETUP request, record the decoded eight-byte
header fields **bmRequestType, bRequest, wValue, wIndex, wLength**, plus request
order and port. Values are observed requests before TinyUSB processes them;
they do not prove acceptance, completed transfers or the host's OS.

The fixed header whitelist is:

| bmRequestType | Permitted bRequest values |
| --- | --- |
| 0x80 or 0x81 (standard IN, device/interface) | 0, 6, 8, 10 |
| 0x00 or 0x01 (standard OUT, device/interface) | 1, 3, 5, 9, 11 |
| 0xa1 (class IN, interface) | 1 |
| 0x21 (class OUT, interface) | 9, 10, 11 |

The class/interface codes cover HID-initialization-shaped requests
GET_REPORT/SET_REPORT/SET_IDLE/SET_PROTOCOL. Only headers are recorded; interface
indices remain visible for interpretation against the fixed composite profile.
The observer does not infer a class or a successful transaction merely from
these codes. No other class/vendor headers or data stages are recorded.

Track reset/unplug generation boundaries, their saturating counts and reset
link speed. Keep at most the **first 64 whitelisted records**, never overwrite
the oldest prefix. A 65th permitted request marks overflow. The observed/ignored
counters concern SETUP attempts during collection, not keyboard/CDC transfer
activity. SOF, transfer-completion and other events are forwarded without
inspecting their unions or maintaining activity counters.

Capture state is statically ready before Arduino app_main starts USB. Starting
in setup() would miss enumeration. Early boot records are retained, then the
window closes after **5,000 ms from the first foreground observer service**.
There are no per-event wall-clock timestamps. This is a foreground window plus
bounded early records, not a claim that initial boot collection starts at a
measured interrupt timestamp. Reset starts a fresh generation; unplug invalidates
the previous one. No state or learned fingerprint is persisted to NVS/storage.

Configured state, missing-reset, overflow, exhaustion, clock and incomplete
flags describe capture validity. COMPLETE means only that this bounded header
window closed with a configured device, not that an OS was detected. Unknown,
incomplete or ambiguous evidence cannot yield a positive classification.

### Event categories and interpretation boundary

The exported `records` are raw selected request headers. Separate validity fields
do not relabel or rewrite that prefix. `unsupported` counts relevant unsupported
observations, saturating without wrapping; `unsupportedReasons` is a bitmask:

| Bit | Relevant unsupported observation |
| --- | --- |
| 1 | A standard device/interface SETUP header outside the declared whitelist |
| 2 | An unhandled class/interface SETUP header outside the explicitly excluded CDC shapes |
| 4 | An unknown or invalid DCD event identifier |

These reasons remain visible through the collection window. At its deadline an
otherwise complete generation becomes UNSUPPORTED when any reason is present;
its raw prefix remains available, but cannot support a positive interpretation.
The whitelist selects header shapes; it is not a complete USB protocol validator.
Retained values and reset speed remain observations, not proof of legal or
accepted transactions. A later rule must justify every raw field it uses.

Known SOF, transfer-completion, function-call, suspend and resume events are
ordinary ignored events: no selected feature depends on their payloads, and they
are forwarded before any observer lock or activity counter. Vendor requests and
endpoint/other-recipient requests are outside this device/interface-header
profile and are not inspected beyond header classification. They are not evidence
for a rule about those omitted features. Filtered SETUP requests increment
`ignored`; this differs from the unsupported subset counted above.

The only class/interface exclusions treated as ordinary ignored SETUP are these
CDC-initialization-shaped headers, with an interface index high byte of zero:
`21/20, wValue=0, wLength=7`; `a1/21, wValue=0, wLength=7`;
`21/22, wValue<=3, wLength=0`; and `21/23, wLength=0` (hex type/code).
This is an exclusion policy, not proof of an interface class or successful
transaction. An eventual rule requiring excluded information is unsupported by
this capture and must return UNKNOWN.

Overflow, missing startup/reset, unplug/reset generation changes, exhausted
counters, clock errors and incomplete configuration are distinct integrity
boundaries. Do not merge snapshots or interpret an absent value as zero/OFF.
Only one coherent current-generation snapshot may be considered, and no positive
classifier exists in this image, including for a COMPLETE capture.

Record no payload bytes, descriptor/string contents, HID reports or their
contents, unrelated keystrokes, host files, credentials, packets from other
devices, or owner scripts. Never copy whole dcd_event_t storage: unused union
members/padding can be uninitialized. Boot marker and export-time millis are
separate context samples, not event timestamps or an independent OS identity.

## Engineering and access boundaries

Use one transparent GNU link wrapper around dcd_event_handler. Forward the exact
original event pointer and in_isr flag **once for every event**, including ignored
ones, after leaving the short observer critical section. Do not change the SDK,
descriptors, VID/PID, USB modes, endpoints or original handler behavior.

The callback may only perform bounded field copies/counters under its independent
task/ISR-safe guard. No heap allocation, logging, filesystem, HTTP, HID command,
execution mutex or classifier is permitted in that callback. Capture state plus
its guard has a **2 KiB ceiling**, independently measured on the target. The
compiler's existing 3,928/4,096-byte workspace is separate and is not enlarged.

Expose a coherent copied snapshot at authenticated, header-only
GET /routeb/usb-observations. The new endpoint requires X-Duck-Password and does
not advertise query credentials. Existing authentication/settings behavior
elsewhere remains unchanged. Add manual Diagnostics View/Download JSON controls
using the existing header/authentication and safe text rendering. No automatic
poll, upload, start/reset/clear control or host-side OS helper is introduced.

Collection is automatic on the observer profile's USB generation, independently
of payload execution. Script STOP retains its existing meaning: it stops injection
and prioritizes cleanup; it is not a USB collection or host-process terminator.
The capture closes on its own finite window. Exports and screenshots created by
the owner persist independently of device RAM; no secure erasure is claimed.

## One later owner capture session

No hardware is accessed during preparation. The published capture kit is for
review before a separately owner-operated installation. Use the existing guarded
installer/ROM-entry procedure and rediscover the current USB port; do not copy
an old suffix. Keep the USB identity/profile and connection path unchanged.

After a normal connection to the known Intel High Sierra 10.13.6 Mac, wait until
the dashboard is ready and at least five seconds have elapsed. On the iPhone,
open Diagnostics, View USB observations, then Download JSON. Save this as
capture A before disconnecting. Record the known host version/connection path as
owner context, not as an automatically detected fact.

Optionally run one ordinary benign TextEdit marker to check that keyboard output
still works, after the capture window has closed. No broad earlier test campaign
is requested. Stop and return to working firmware if USB/keyboard behavior is
unexpected.

Reconnect normally once using the **same observer image** for an independent
enumeration. If USB power reset the board, rejoin its Wi-Fi and allow startup to
finish. View/Download capture B after the window closes. Preserve both original
files; boot marker/generation prevent accidental merging. Opening Diagnostics
does not restart capture. There is no second capture firmware or automatic test.

Keep capture B unchanged locally and provide A first for development. Freeze a
prospective rule and its independent justification before examining B for
validation. If B is used to develop the rule, it is no longer held out. Two
enumerations on one Mac establish neither uniqueness nor cross-OS accuracy.

If either capture is truncated/incomplete, or no justified positive discriminator
exists, report the result as inconclusive. Do not fabricate MACOS, relabel known
host context as detection, or expand this into another observer installation.

## Exact return path

The kit includes **working-define-labels-macos-review-v1.zip**, the original
unchanged working DEFINE package: 2,691,374 bytes, SHA-256
`b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed`.
Its working application is 1,438,048 bytes, SHA-256
`167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`.

For return, extract that ZIP into a separate new directory, run its original
offline preflight, and follow its unchanged guarded INSTALL-MAC.md procedure to
install the working DEFINE application. This is the **WORKING_DEFINE_RETURN**
role, not the outer kit's older rollback action. If observer boot fails, use the
owner-established ROM-entry procedure and the same known working kit. Do not
format, reset settings, erase flash or automatically retry an ambiguous write.

The outer kit also retains the mandatory **older** source/text-v2 rollback,
1,413,200 bytes, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It lacks later privacy/dashboard repairs and is not a full-device/filesystem
restore. Both recovery roles must be verified and physically available before
an owner chooses to install the observer. Existing private backups and historical
packages remain untouched.

## Finish line and next gate

This stage delivers a software/target-verified capture image, one review package,
short owner observation instructions and exact working return bytes. It does
not deliver a working OS detector. A future classifier requires a trace-backed
positive rule, independent justification/comparison, held-out validation and a
known-host conditional-output result. Other hosts remain untested until observed.
Do not ship an always-UNKNOWN detector as completion or repeat small parser
packages. Preserve STOP, cleanup, execution limits, privacy, H1's experimental
status and its unresolved canonical numeric contract throughout.
