# Caps/STOP HID diagnostic report — 2026-10-19

**Root cause UNRESOLVED. Software diagnostic build PASS; physical High Sierra
validation PENDING OWNER. No behavioral workaround or timing-policy change.**

Owner confirmed currently installed MAC-CAPS-TIMING-20261019-v1 application
5e10009fd3e5a0a862b4f7bed1f7f28ba8464f7bb1066fd8091c6e01b2ed4a59. That exact
public application is freshly download-verified and retained as rollback. No board
readback, hardware access, flashing, boot, OTA or real HID occurred in this task.

Baseline5e22569709f44bd4a6c429beb43a055d94d39257; new isolated caps-stop-hid-trace
branch. All1,735 existing files byte-identical;235 frozen Stage26 files unchanged.
All63 prior remote refs must also match the final publication receipt. The working
firmware and prior package remain untouched. This is not a new numbered stage.

## Findings and scope

High Sierra10.13.6 is the target. Polled HIDSystem/Combined flags agreeing does
not identify a keyboard or synchronize its LED. The owner reports that unexplained
transitions cease when EvilDuck is unplugged; this does not prove repeated USB
keypresses. No physical trace proving post-STOP sends has been received. Mac
reconciliation, in-flight delivery, another Start/path and continued firmware output
remain competing hypotheses. See caps-stop-compatibility.md for evidence boundaries.

Added a default-OFF120second/128record ring and explicit authenticated dashboard
controls. Captures admission/run/dwell, dequeue, phases, operation queue boundaries,
STOPpublished/observed, terminal, actual report API attempts/returns, SDK completion/
failure and raw/accepted LED feedback. Records contain categories only; no typed
characters, arbitrary key usages, paths or private data. Ring gaps are explicit.
Callbacks have run0/op0; no invented USB transfer identity. HTTP202-prepared is a
receipt preparation, not owner acknowledgement, completed cleanup or host delivery.

Actual composed sources/functions/line numbers and hashes are listed in
caps-stop-source-references.json; overlay hunks are tests/caps_stop/application.patch.
Architecture and decoding: caps-stop-design.md. Raw synthetic timestamped sequences:
caps-stop-traces.json (G04 STOPduring500ms:Caps accepted275000us, STOPpublished275000,
owner observes276000, neutral accepted276000, terminalCancelled276000; **not a board
capture**). G06 shows STOP after completion adds no send; G18 shows distinct run IDs.

No source evidence justifies claiming a Caps synchronization fix. The patch observes
behavior; existing STOP scheduling, ownership, quarantine, source closure and neutral
cleanup stay intact. Accepted input cannot be retracted. Simulations prohibit new
key reports after owner-observed STOP, allow neutral cleanup, and find no later idle
worker/reconnect replay. They do not establish a host release or no report accepted
between STOP publication and the owner's next cancellation check.

## Fresh verification

|Executed suite|PASS|FAIL|Assertions/vectors|
|---|---:|---:|---:|
|Composed production-source native,24new+207inherited|231|0|7,470 assertions|
|Relevant unchanged backend/diagnostic cases|63|0|2,650 assertions|
|Actual embedded JS in Node VM|40|0|64 assertions|
|Isolated core/source/old-guard checks|14|0|Not separately instrumented|
|Real esptool4.12 parser AST only|14|0|14 input vectors|
|Portable observer privacy-filter case|1|0|6 vectors|

Native and related cases run ASan/UBSan with leak detection; final runs clean.
New24 include STOP four windows, malformed/auth/busy, finite ring/expiry/clock,
USB failure/disconnect, refusal/quarantine, run correlation, concurrent callbacks,
HTTP receipt race attribution and no text leakage. Related T34/X13/X15 remain
explicitly excluded for historical host-thread/old-buffer assumptions, with existing
K25/H15 replacements retained. No historical expectations/classifications changed.
These focused relevant checks are not represented as a rerun of every historical
project stage. Initial G08 failed because the test omitted mock keyboard registration;
corrected setup preserves original assertions. Development evidence retained in
caps-stop-test-development.json. An intermediate227case rerun also passed;
only the final231cases/7470assertions are counted above. Package and bound installer tests appear in
separate receipts after archive construction; no physical operations in those mocks.

Native IOHID/AppleClang/High Sierra execution:SKIP_ENVIRONMENT, pending owner. Optional
foreground tool uses public IOHIDManager to filter ONLY Caps/modifiers on matched
Apple/EvilDuck services, no injection/seize/persistence/drivers. It may not expose
array-keyboard Caps changes; absence is inconclusive. See caps-stop-host-observer.md.
Neither Linux nor a modern macOS assumption establishes High Sierra behavior.

## Clean target build and resource review

ArduinoCLI1.3.1; pinned ArduinoESP32core3.3.0 isolated approved archive-feedback
profile; ESP-IDF5.5 SDK,177archives unchanged; Xtensa GCC14.2.0;16MiB custom table;
PSRAM disabled; existing OTG/CDC/CPU/flash profile. Source/core/compiler/archive/
linker/response/ELF/BIN identities and disassembly checks: caps-stop-build.json.
New failure callback is one strong symbol, calls trace and overrides pinned weak
no-op; USB descriptor/report ID1/eight-byte input and routing remain unchanged.
No global dependencies modified. Clean source compilation, no warning/error lines
found in retained build log. Post-link closure PASS284inputs/3responses/13scripts.

|Measurement|Owner baseline|New trace|Growth|
|---|---:|---:|---:|
|Compiler program bytes|1,397,819|1,404,495|6,676|
|Application BIN bytes|1,397,968|1,404,640|6,672|
|Static RAM bytes|107,776|111,992|4,216|
|Free OTA bytes/slot|6,204,208|6,197,536|-6,672|
|Free OTA percent|81.610949%|81.523185%|-0.087764pp|

Application SHA-256:25e17cadacf3b2ab5eb5ece32fc94f4bf36fb71eb90e91814dca7f7320bd5178.
ELF SHA-256:83cd318a8d18f62a4b208a66cbca77b9dfa51a8c8faa7587af981fb3f632ab15.
Table SHA-256:b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e.
Ring4096bytes; fixed metadata/counters. Event path has no allocation/network/storage.
Individual compiler frames:handler3184bytes,trace note48,append48,failedcallback32.
Loop selected8192; pinned AsyncTCP default16384 (no compile override). These are
not runtime stack high-water/call-chain proof. HTTP response allocation and real
latency/contention/heap require physical observation. Source lock-order audit finds
no trace-to-execution/publication/feedback inversion; native concurrency test covers
200publish attempts/128retained/72overwrites with coherent sequences, not ESP32 timing.

## Package and owner next step

New application buildId:CAPS-STOP-TRACE-20261019-v1. App-only Mac package includes
candidate, exact prior application rollback, pinned table and strict read-only-default
installer. Manifest is unsigned integrity, not device authenticity. Fresh chip/security/
layout/OTA and NEW private backup checks, typedconfirmation and repeat revalidation
precede any separately authorized two-slot update. No cloud installer/device command
was executed. No automatic reboot/replay/recovery or nonapplication writes. Current
bootloader/table/NVS/OTA/SPIFFS/coredump stay outside proposed app erase/write ranges.

Human checklist:caps-stop-owner-check.md; installed ID/hash evidence:caps-stop-owner-
evidence.md; rollback public-download proof:caps-stop-rollback-verification.json;
reproduction:caps-stop-reproduction.md. INSTALL/ROLLBACK guides are package preparation,
not authorization. New trace, native Mac observer and physical STOP/LED/Caps behavior
remain UNVERIFIED until owner supervision. Keep the working build/package accessible.

**GO:**review source/trace/finite lab checklist and download-integrity evidence.
**NO-GO:**claiming a proven physical cause/fix, full Caps synchronization, host release,
or automatically installing/running a payload. Next useful evidence is one gap-free,
source-tagged finite capture alongside separately recorded High Sierra service/global
flags, physical LED/case and STOP phase. No further feature work started.

## File inventory

All changes are additions under tests/caps_stop/, docs/caps-stop-*, and the new
public candidate BIN/ZIP in downloads/. Exact paths and hashes are recorded in
caps-stop-files.json at final publication; historical paths/modes are unchanged.

## Package verification and publication

Package-only fault tests:37PASS/0FAIL; actual bound installer with
injected tool/device responses:38PASS/0FAIL. These execute no esptool
operation dispatcher or physical device I/O. Aggregate current counted groups:
438PASS/0FAIL, including six privacy vectors as one filter case. Recorded assertion
total for instrumented native/related/UI suites:10,184; filter adds six Boolean
vectors. Python package/guard case assertions are not separately counted, so no
invented grand assertion total is given.

Source/build commit:79581baf8b5461399c302df7c7a3bbd0ab062404.
ZIP:`evilduck-caps-stop-macos-install-v1.zip`, 2,238,783bytes.
SHA-256:`40a646b389345b1aadfc3845507642ad676fbab6fc28d2bf8f95ca469b0cb7f3`. Exact members and source binding:caps-stop-integrity.json.
Package includes candidate, exact rollback, table, manifest, read-only preflight,
reviewed bound installer/launchers, pinned partition tool, build/dependency/test
evidence, human guides and optional observer source. No private owner data.

Publication is separately recorded in caps-stop-publication.json only after an actual
commit-pinned public download matches ZIP size/hash and every member, including both
application hashes and downloaded preflight PASS. Review the receipt for URL/commit,
previous63refs and unchanged1,735baseline files. Successful publication is software
delivery, not approval to flash, boot, type or claim physical behavior.
