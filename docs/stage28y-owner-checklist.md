# Stage28Y host, recovery and authorization decisions

PUBLIC PACKAGE INTEGRITY: PASS offline. PRIVATE WORKFLOW: PASS synthetic tests.
OWNER PRIVATE FINALIZATION: PENDING. RUNTIME/PHYSICAL: NOT AUTHORIZED / NOT EXECUTED.

## Host checks, no device connected

Select the actual future computer/OS; previously used macOS10.13.6 is not assumed
selected now. On that host, with EvilDuck disconnected, use Python3.8+ to run the
bundled host_preflight.py against a fresh safely extracted public package. Report
only exit status, Python version/system, PASS/FAIL and generic diagnostic; no paths,
credentials or private files. This is PENDING OWNER RUN. No compiler, Arduino,
USB driver, Git, network, tool installation or enumeration is needed for public
inspection. Local unsigned manifest/code trust still needs reviewed Git/hash evidence.

Private finalization additionally needs verified Arduino3.3.0 tool files, pinned
SDK source subset/generator0.1.9, compatible cryptography and native mkspiffs0.2.3.
Actual mkspiffs and real generator executed successfully on Linux; High Sierra native
compatibility is PENDING, not established by Python syntax or Linux tests. Use the
existing pinned verify-only helpers and README commands; do not auto-upgrade the
Mac, downgrade core or silently fall back to a different filesystem tool. Python
source portability, native tool execution and later USB/driver/ROM operation are
three separate checks. Python3.8.10/esptool4.12.0 were historically owner-used; esptool
is not needed by Y preparation. No version5 requirement is introduced.

## Recovery review

Original firmware: OWNER CONFIRMED: AVAILABLE EXTERNALLY. Do not search, request,
reconstruct or download it. Exact original firmware, NVS/settings/scripts/FS is not
a preservation requirement. Existing backups remain untouched, optional resources.

A specific future recovery set still needs its bootloader, partition table, app(s),
OTA initializer where applicable, SHA-256, byte sizes and exact offsets checked as
a whole. ESP32-S3/revision/security compatibility, flash mode/frequency and table
bounds must match the selected set, not necessarily the new table. A stock old-table
restore can replace the upgraded layout/data; loss is acceptable only within the
separately approved recovery ranges. Do not combine stock app bytes with arbitrary
new/old tables or assume web/OTA remains available after a failed boot.

The existing tools/stage25_recovery_check.py can perform offline structure/hash/range
checks on an owner-selected recovery-review.json and its local files. It checks both
reviewed layouts and S3 image integrity/entry/revision/flash context. It does NOT
establish physical known-good recovery. No stock bundle was inspected here. Owner
historically confirmed16MiB quad3.3V S3v0.2 and ROM access; current-device identity,
layout/security and ability to re-enter ROM using known board procedure, cable,
stable power and host driver remain checks for a separately authorized session.
No guessed button wiring, flashing offset or full-chip erase is prescribed.

## Separate future approvals — none granted by package completion

1. Current-device/layout/security/ROM checks, explicitly including any USB/serial
   communication. Historical evidence is not a new measurement.
2. Complete exact approved write set and sector footprints, including deliberate
   fresh NVS [0x9000,0xE000) and empty SPIFFS [0xE90000,0xFF0000) replacement. Private
   receipt must bind the selected X public manifest and all eight roles. Both app
   slots use identical X bytes. No whole-slot/unlisted-gap erase; no full-chip image.
3. First boot/idle observation with no script selected. USB initialization/enumeration
   and idle status are NOT an assertion of no USB traffic. Controlled credential,
   mount/AP, no-format/no-examples/no-autorun and no-auto-arming gates must hold.
4. Benign finite manually started prepare/cancel and competing-refusal trials:
   **NO VISIBLE TEXT EXPECTED, not NO HID OUTPUT.** Neutral synchronization/clearing
   reports can be submitted even by a Delay-only fixture. Their authorization must
   be explicit. This corrects the ambiguous X gate heading without editing X history.
5. Separate tiny literal text authorization in a deliberately focused blank editor,
   on owner-controlled host with chosen layout, then finite Delay/loop/STOP trials.
   No terminal, modifier chord, credentials, owner payload, persistence or automatic
   script. Validate each fixture against the unchanged subset before saving.
6. Optional disconnect/loss testing only under its own explicit approval. Do not
   treat cancellation/unplug or local clearing as proof a host released keys.

Carry X's staged durations forward: idle60s at<=1 status/sec; prepare/cancel<=10s
per trial/2min group; each tiny literal/timing trial<=10s; initial session<=5min.
Provisional abort thresholds for review: two responsive1s status observations with
no tick advance; observed interval/work>250ms; loop minimum free<2048B; free8<32768B;
largest8<16384B; new clock error, quarantine/loss, persistent refusal/no progress,
critical mount/settings error, unexpected activity or focus/characters. These are
unvalidated trial thresholds, not demonstrated hardware limits. AsyncTCP high-water
is unavailable. Heap minima have per-region historical semantics.

STOP may be behind unread serial backlog (64 reads/loop), or HTTP may return401/409
under authentication/execution contention. Do not flood either channel or infer
acceptance from a call attempt. Loss of observation is an abort, not success. Recover
only under the separately reviewed ROM plan, never guessed automatic repair/replay.
LOCAL_SCHEDULER_DONE/LOCAL_CLEARING_SUBMITTED remain LOCAL; visible text, endpoint
retirement and host key release are distinct evidence. Strict Route A is unresolved.

Remaining concrete choices: intended host/OS/layout and non-device local run;
owner-local private finalization; selected recovery-package compatibility review;
current-device/layout/ROM confirmation plan; approval of exact complete artifact/range
set; approved observation channel/thresholds and individually scoped boot/neutral/
literal/loss tests. None invalidates completed public integrity checks. No hardware
trace in Y has been performed; no Stage28Z is authorized automatically.
