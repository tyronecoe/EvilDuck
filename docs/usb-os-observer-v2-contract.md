# USB observer v2: bounded evidence correction

**CAPTURE ONLY — NO CLASSIFIER — NO AUTOMATIC PAYLOAD OR HOST PROBE.**

The owner approved the subsequent evidence-assessment plan for implementation.
This explicitly revises the original one-observer-stage restriction to permit
one new v2 review image and one later owner-operated development capture. It is
not permission for automatic installation, repeated capture campaigns, an OS
label, whitelist relaxation or an always-UNKNOWN detector success claim.

## Baseline and preserved observations

The source parent is publication `fe6ed1c291a2af234793cca86aa9b8c979ac6d8e`,
firmware checkpoint `7472de1e0edf123a9fcdf9d1d4feb1b38250280e`,
`ROUTEB-USB-ENUM-OBSERVER-H1-v1`, application SHA-256
`e60af8a1b53ab2ba9e7c79b4ff821719ddd06a0a55384dd987288c4189aed6a9`.
The owner reports installation and a displayed running build ID. This is not
independent full-flash readback or current typing acceptance. The iPhone was the
Wi-Fi dashboard client; the High Sierra Mac was the USB host. Exact cable/hub
topology remains unknown.

[Original evidence](usb-os-observer-v2-evidence.json) preserves the handoff and
all five JSON byte strings with their original hashes. They represent three boots,
not five enumerations. All have been examined; none is held out. Repeated exports
of boot c5cf10e225fcc49a differ only in export time. No original observation,
acceptance milestone, published v1 package or source is rewritten.

V1's counter-before-filter logic explains missing order 21: observed22 equals
retained21 plus ignored1, with unsupported reason2. It does not identify the
missing class/interface request, show a lost packet or prove SDK rejection.
V1 can downgrade COMPLETE after closure without changing old timestamps; therefore
its INCOMPLETE/configured=false is not necessarily the value at the deadline.
A later live sample does not reconstruct that history. Speed0 means full speed.
The expected unchanged composite is MSC0/HID1/CDC2-3, including MSC while media is
inactive. GET_IDLE, GET_PROTOCOL or MSC initialization are competing examples,
not identifications of the missing header. Do not blame owner procedure or infer
broken keyboard behavior from these diagnostic states.

## Concrete questions and unchanged capture scope

V2 answers: what first class/interface header was filtered, when were selected
request headers observed, which SDK-status samples were available before closure,
and did relevant request/configuration activity continue immediately afterward?
It cannot recover v1's omitted header or event times, prove transaction acceptance,
or establish that a sequence uniquely identifies an operating system.

Retain port0, the first64 selected headers and the exact v1 whitelist/exclusions.
Standard device/interface and declared HID-initialization-shaped headers remain
selected. Known SOF, transfer completion, suspend/resume and deferred callbacks
remain ordinary ignored events, without payload inspection or new timing work.
No vendor/other-recipient data, descriptor or string contents, report contents,
keystrokes, host files or credentials are collected. Capture raw metadata
separately from unsupported/integrity interpretation. Do not alter USB identity,
descriptors, modes, interface numbers, dependencies, partitions or owner settings.

## Clocks, prefix and diagnostic tail

Use one boot-relative uint32 millisecond clock derived from the pinned
`esp_timer_get_time()`. Its early-startup availability and ISR-safe existing
Arduino use are verified against the approved core/SDK. Inject clock values in
native tests. Zero is a valid timestamp, not an absence marker; use explicit
presence flags/null. Natural wrap is supported within these bounded windows;
clock faults and exhaustion are explicit, never silently clamped.

Store an observation timestamp with every retained request and generation start.
These are callback/SDK-sampling times, not USB wire timestamps. The first
foreground service establishes the same five-second prefix anchor, including
bounded early boot records. Callback time gates prevent prefix additions at or
after start+5000ms, even if foreground service is delayed. A service exactly at
the cutoff may supply a coherent status sample before sealing; a sample after
it cannot promote or rewrite the prefix. Distinguish the nominal deadline from
the time closure was actually observed. Preserve maximum foreground-service gap.

Once sealed, prefix records/counters/state and the last coherent pre-cutoff SDK
configured sample plus its actual sample time are immutable for that generation.
An absent or raced sample is unknown. A true sample is neither an assertion of
continuous/exact-deadline wire configuration nor proof that the stack processed
that generation's events. COMPLETE remains a bounded capture-policy state.
Later loss/recovery belongs to separate live fields, never a rewrite of history.

Pass an expected generation around the existing USB boolean sample and reject
application when reset/unplug changed the observer generation. Export the sampled
and current generation context, observation time and mismatch/unknown explicitly.
This rejects an observer-boundary race; it does not prove that asynchronous
TinyUSB task state already belongs to that generation. No positive classifier
or read-only script OS variable is implemented here.

After the original prefix, permit only a separate five-second diagnostic tail,
ending at start+10000ms. Callback time gates enforce that hard end independently
of foreground scheduling. Keep bounded counters, a first late relevant SETUP
witness and a first late SET_CONFIGURATION witness, with timestamps and flags.
Keep tail metadata separate; it cannot turn an invalid five-second prefix into
COMPLETE. No full second trace, data-stage capture or automatic extension occurs.
A missing transition within ten seconds is insufficient evidence, not OFF/zero.

## First rejected header and session integrity

Keep one dedicated first unsupported SETUP witness: exact header, order, time,
reason and presence. Do not place it in or renumber the selected64 prefix. Track
additional distinct unsupported headers explicitly; repeated identical headers
must not masquerade as different kinds merely because their order/time changed.
This witness is separate collection-wide metadata: it may first appear in the
prefix or the tail and carries that phase explicitly. Tail orders use the tail's
own observed counter; never merge them with prefix orders. The tail's first
SETUP witness is the first selected header, not a record of every late request.
Unsupported reasons still invalidate the corresponding evidence. An unknown DCD
identifier never permits copying an unused event union.

Reset/unplug starts or invalidates a generation, clearing old witnesses and live
correlation rather than mixing sessions. Overflow, missing reset, clock error,
counter exhaustion and witness insufficiency remain explicit. Exporting never
restarts collection. Script STOP retains its existing injection-cleanup meaning;
it is not a USB capture reset or host-process terminator.

Live mismatch describes the latest sample rather than a retained race history.
Tail unsupported counts can include unknown DCD events without any SETUP header;
do not infer a missing header's identity from an absent witness. Closure flags
advance on foreground/relevant-event processing; a pending flag seen after the
nominal cutoff does not extend capture, because the next event's hard gate still
refuses records outside the window. Missing-reset/boot speed is null; a known
full-speed reset remains numeric zero.

## Interfaces, resource limits and validation

Build ID: `ROUTEB-USB-ENUM-OBSERVER-H1-v2`.
Version the JSON as `evilduck-usb-observer-v2`; preserve v1's files verbatim.
Keep the same authenticated header-only GET `/routeb/usb-observations`, manual
View/Download controls, safe text rendering and no-store response. Show immutable
prefix, separately sampled live status and diagnostic tail as distinct sections.
The response remains bounded by12288 bytes. No automatic poll, upload, start,
clear/reset control, new credentials or password-retention behavior is added.

State plus guard plus conservative observer-owned callback frames must remain
within2048 bytes; no individual callback frame may exceed256. Measure external
clock callee frames separately and record limitations. Keep64 records and the
compiler workspace4096 bytes (existing3928 used). Do not raise budgets to pass.
No heap, logging, filesystem, HTTP, execution mutex or USB control operation is
permitted inside the callback; always forward the exact event/ISR arguments once.

Test real composed modules with deterministic clocks and mocked DCD/HID/HTTP:
pre-cutoff and late configuration, immutable closed state, zero/wrap timestamps,
reset between sample and apply, coherent live loss/recovery, missed foreground
service, hard5s/10s boundaries, witness first/repeated/distinct handling, accounting,
overflow/exhaustion, session isolation, authentication, STOP and cleanup. Retain
relevant inherited native/browser regressions and sanitizers; reuse unchanged
receipts explicitly. Clean-build with the same approved isolated ESP32 3.3.0
archive profile and committed-source/dependency guards. Bind actual linked SDK
SETUP dispatch, wrapper/clock paths, resources, memory and original190 assertions.

## One later owner development capture and exact return

Prepare one review ZIP. No hardware access, real HID output, live collection,
flashing, OTA, formatting, settings reset or automatic reboot/retry occurs during
development. Offline Mac check remains `python3 preflight.py --directory .` with
the device unplugged, Bash3.2/Python3.8/esptool4.12 compatibility preserved.

After a later deliberate owner installation, record the running v2 build ID,
connect normally to the known High Sierra Mac, allow at least ten seconds after
the dashboard is ready, and manually download one development capture. No host
helper or active lock probe supplies an answer. Re-downloads read stored results.
Keep owner steps short; do not repeat DEL/DEFINE/H1/lock-wait campaigns.

If that capture is insufficient, ambiguous, truncated or indicates regression,
stop and use the exact original working DEFINE kit. Do not automatically extend
time, enlarge capture, create another observer or claim a positive match.
Only if a prospective rule gains independent justification may a separately
scoped fresh, unexamined enumeration validate it. None of the old exports can be
retroactively held out; a known Mac label is not a classifier input or proof of
cross-OS uniqueness. Detection plus harmless branching remains a later gate.

The ZIP must contain unchanged `working-define-labels-macos-review-v1.zip`,
2691374 bytes, SHA-256
`b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed`,
restoring working app1438048 bytes SHA-256
`167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`.
Extract it separately, run its offline preflight and follow its original guarded
install/ROM-entry/rediscovered-port instructions. The outer rollback instead
selects older source/text-v2 app1413200 bytes SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It lacks later privacy/dashboard repairs and is not a full-device restore. Keep
both recovery roles, all published artifacts and private backups unchanged.
