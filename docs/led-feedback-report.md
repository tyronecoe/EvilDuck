# LED feedback boundary update

**Outcome: instrumented diagnostic candidate awaiting hardware evidence.**
The misleading diagnostic meanings are corrected. No evidence establishes the
Mac's actual LED packet format or a Mac-specific routing repair. Caps Lock output
and host LED feedback remain **physically unverified**. No hardware, flashing,
OTA, real HID, owner-script or host-sender execution occurred.

## Baseline and evidence

Started clean at0d100caa120d11920341e493019e5fc016c05a4f on the identified custom
branch, not main/upstream. Prior ZIP2,155,369B/SHA b5b238c0... and application
1,381,776B/SHA573a8671... match the committed package. Public release receipts
identify those bytes but do not show a live board readback or a subsequent owner
installation receipt. Earlier public notes described c20 as working; they do
not establish which image produced the newer screenshots. Current exact board
image remains UNKNOWN. No reinstall was requested just to identify it.

Owner evidence is recorded as reported: Mac physical Caps light toggled; four
fresh snapshots had zero downstream callbacks/reports and unknown feedback;
ordinary text subsequently typed. Earlier1,887–1,935million-us versus later
29,364,602-us timestamps are consistent with a boot/timebase reset, not continuous
boot proof. Ordinary text is not a Caps test. The visible409 storage/fixed-message
messages do not establish an LED cause; unrelated queue/storage behavior was not
changed. New visible build ID: LED-FEEDBACK-BOUNDARY-20261018-v1.

## Changes and preservation

New branch led-feedback-boundary-diagnostics; source/build commit43aa0c7
(full source identity is in the package manifest). The selected source layer is
an additive pinned overlay after tests/caps_queue, not edits to overwritten root
firmware. See led-feedback-design.md for exact boundaries and field semantics.

- Adds raw SET_REPORT entry, original instance/type/ID/length/protocol, actual
  keyboard registry/object identity, routing attempts/dispatches/rejection reason
  and receiver rejection counters. FEATURE and LED OUTPUT remain separate.
- Preserves routing decisions, including the unresolved unprefixed one-byte ID0
  case. No blanket ID0-to-keyboard workaround, descriptor or USB identity change.
- Adds real TinyUSB bus/configuration/suspend/readiness samples, explicit5-second
  LED validity, boot correlation nonce, uptime and current-session metadata.
  Legacy connected remains feedback history and is clearly deprecated; callbacks
  remains the derived handler counter. Neither is silently redefined.
- Synchronously invalidates feedback on actual core mount/unmount/suspend/resume
  before asynchronous Arduino notifications. Receiver rejects SDK-unconfigured,
  suspended and stale-session input without fabricating all-off feedback.
- Adds Caps-only queue-return and actual core completion timestamps/counters.
  Usage0x39 and unchanged press/later-step release are tested. No guessed dwell,
  global delay, general HOLD/RELEASE or language change is introduced.
- GET/Observe remains authenticated and read-only; no receive/start/reset/clear,
  storage mount, key injection or counter reset is performed by refresh.
- New Mac installer retains app-only/fresh-ROM checks and exact image guards,
  defaults to read-only, and prints numbered operation start/PASS/FAIL messages.
  Rollback is explicitly the identified prior573a8671 package, not a claim about
  the current board image and not a silently older c20/de24 selection.

All counters are saturating/fixed metadata; no payload log or arbitrary key data
is stored. Callback code uses short independent critical sections and no executor
lock, allocation, filesystem, network or logging. Existing upstream USB event
queue waits are not represented as newly eliminated. Core source changes exist
only in a disposable isolated copy; historical profiles, pins and verifiers,
production root files, partitions, installed tools, SDK archives and old packages
are unchanged.235 frozen Stage26 files pass byte-identity verification.

## Reproducible core and linked build

ArduinoCLI1.3.1 / core3.3.0 publisher archive; ESP-IDF5.5 precompiled libraries;
Xtensa GCC14.2.0;16MiB custom partitions; PSRAM disabled; USB-OTG/TinyUSB/CDC;
QIO80/240MHz build and DIO80/16MiB app header. Original HID/NVS patches are retained,
then the separate diagnostic patch applies with zero fuzz. Exact pins:

| Artifact | SHA-256 |
|---|---|
| Additional core patch |8c96735814cead97e95ffca8accf286ac0765cfddb1273f852600d86a9a68572|
| Resulting USBHID.cpp |aba054156d04bceee833a4708abab2de2f8dd380325fd1ab61d13ecae32d4e84|
| Resulting USB.cpp |8d7b8283bc3ee978de14229382d43628ae48c1f01acbbaa15837bf2ced01571f|
| Full patched core tree |a79b9c7e42e7ea2066815271117eeac23fe0a27e65fa00657dc268b70c22c53a|
| Application |2c657f0c74f1d12c88aa1e6fa6daf5cc76de36e8e68bc41a325f39b19c9045a7|
| ELF |aaaf61d163bed557dd1dc0ccfb6978eff94fe6f8a2f083cfb50d7e2e726de13e|

Complete197-file materialized source inventory, compiler/core/object hashes,
282 linked inputs,3 response files,13 linker scripts and all177 unchanged SDK
archives are in led-feedback-build.json. Original led_receiver.cpp remains
7b8743a007487db970c8a777aa95dc60bee35c86b0fa96d9ac62ec473ec6916e.
The partition table and bootloader hashes equal the prior build; neither is a
planned write. The paired NVS original-error/no-auto-erase startup, settings and
storage-before-HID checks, no examples/autorun, single-owner/STOP paths,5-tick HTTP
wait and8KiB loop stack remain linked and verified.

Final ELF verification proves six callback-to-diagnostic paths. GCC outlines the
SET_REPORT diagnostic lambda; verification requires BOTH the actual callback's
call to that exact outlined symbol and its call to the strong diagnostic hook.
It does not weaken this to a mere string/symbol-presence check. The four lifecycle
callbacks and HID completion callback directly call their strong hooks.
ELF-to-image regeneration is byte-identical to the published application.

Early compile checks found a missing explicit TinyUSB header and a native duplicate
include guard; both were corrected. Intermediate compiled candidates were not
published. Final source/build and linked checks pass. The first new link check's
direct-call assumption was corrected to verify the actual outlined two-edge path.
No source/SDK identity or safety predicate was bypassed to obtain a pass.
The supplemental probe initially hit a native main-macro redefinition; a
name-only copy adaptation resolved it without weakening compiler warning flags.

| Measurement | New | Prior573a build | Change |
|---|---:|---:|---:|
| Program bytes |1,386,023|1,381,631|+4,392|
| BIN bytes |1,386,176|1,381,776|+4,400|
| Static RAM |107,688|107,488|+200|
| Free OTA bytes, each0x740000 slot |6,216,000|6,220,400|-4,400|
| Free OTA percentage |81.7660628%|81.8239409%|-0.0578781points|
| LED HTTP compiler frame |3,680|1,024|+2,656|

The3072-byte bounded JSON buffer is stack-local; this HTTP handler now has the
largest recorded application frame. The pinned AsyncTCP default task allocation
is16KiB, but frame size is not call-chain usage or measured high-water. Callback
storage is fixed; no dynamic report queue is introduced. Native leak checks are
clean; physical heap, scheduling latency, stack high-water, Caps dwell and USB
acceptance have not been measured. Normal writable SDK NVS mutation risks remain.

## Fresh focused verification

| Suite | PASS | Unexpected FAIL | Tracked assertions |
|---|---:|---:|---:|
| Real pinned core slices + composed application,22 new +125 prior cases |147|0|6,849|
| Relevant unchanged backend/diagnostic regressions |63|0|2,650|
| Actual embedded JavaScript in Node VM |18|0|31|
| New core/dependency guard and prior-profile preservation |14|0|case counts|
| Actual pinned esptool4.12 parser vectors, no dispatcher |14|0|case counts|
| Focused Caps timing/allocation probe |1|0|6|
| Extracted package/image/layout negatives |37|0|case counts|
| Bound installer with actual validator/images and injected device data |38|0|case counts|

**332 passing cases, zero final unexpected failures.** C++9,505 assertions;
JS31 assertions. Python case totals are not invented assertion counts.
ASan/UBSan/leak detection clean for the native147+63 cases and the focused probe. No ThreadSanitizer,
complete Xtensa SDK runtime or physical USB execution is claimed.
Host environment: Python3.12.14, GCC14.2.0, Node24.19.0. Bundled Python3.8 grammar
and Bash syntax pass; actual High Sierra serial execution remains owner-local.

The core test slices are extracted from hash-verified source, not hand-written
stand-ins for dispatcher decisions. Actual virtual dispatch reaches the composed
FeedbackKeyboard, receiveLockReport and LED receiver. Lifecycle slices call the
real application invalidation hook. Tests cover prefixed/nonzero/ID0 registration,
malformed length/null/type/instance, FEATURE, boot/report observation, missing
registration, session invalidation, repeated feedback, concurrent snapshots,
Caps submission/completion, authentication, normal typing, STOP and storage guards.
Synthetic metadata/clock/USB registration/event-post/endpoint seams remain mocks.

Historical T34/X13/X15 exclusions retain their previous meanings; no prior
XPASS/XFAIL or unsupported observation is relabeled. No unrelated full-history
rerun is claimed. Prior archive guard still passes its original core AND rejects
this separate instrumented core; historical original guard still rejects it.

## Package and owner next step

ZIP evilduck-led-feedback-macos-install-v1.zip:2,169,867 bytes, SHA-256
07069cafc83f1a7ad7c6a6e1646c2e3a9cc834611b490feebaf87b544a7ce55b.
Includes the new application, prior573a rollback, strict manifests/preflight,
Python3.8/Bash check-default installer, deliberate rollback, exact build receipts,
licenses, Mac guides and ONE short OWNER-CHECK.md. No private owner data or host
sender is included. Existing backups/packages are untouched.

Only the two apps are writable after fresh owner-local chip/security/table/OTA
checks, a new private full backup, explicit typed choice and repeat validation.
New image-rounded erase intervals are[0x10000,0x163000) and[0x750000,0x8a3000).
Rollback intervals are[0x10000,0x162000) and[0x750000,0x8a2000). All are inside
0x740000 app slots and exclude bootloader/table/NVS/OTA/SPIFFS/coredump. Two-slot
writes are not atomic. Failure never automatically reboots/retries. Other valid
OTA states or old partition layouts stop for separate review, not forced repair.

GO: software review and separately authorized owner read-only preparation.
No physical write/boot is authorized by this task. The next supervised check is
ordinary text once, then physical Mac Caps off/on/off with prompt<=5-second
refreshes and matching build/boot/session evidence; no Start receiving required.
Raw0 vs raw>0/keyboard0 vs keyboard>0/accepted0 vs accepted/UI disagreement
separates entry, routing, receiver and display seams. It does not prove wire
traffic, a blanket macOS limitation, host release or general DuckyScript3 support.
Test EvilDuck's own Caps press separately afterward. Fixed-message work waits
for basic Caps AND Num feedback; unsupported host feedback is not simulated.

Publication/download verification and prior-ref preservation are recorded in
led-feedback-publication.json only after actual push/download verification.

## Focused Caps/local-allocation measurement

The exact final source composition with a controlled1ms mock tick submitted Caps
at265ms and the release at271ms:6ms simulated queue interval. Queue-return
telemetry tracked265000/271000us. This is not physical USB dwell, a configured
minimum, a High Sierra requirement or proof of host delivery. No dwell change
was justified as a confirmed fix. The instrumentation supplies a bounded,
Caps-specific diagnostic for the next separately supervised observation.
After one warm-up call,1000 actual patched dispatcher -> derived handler ->
composed receiver calls caused0 native instrumented C++ new allocations.
This does not count all C malloc/OS operations or measure physical ESP32 heap.
Sanitizers/leak detection pass. Exact command/result: led-feedback-caps-probe.json.

## Complete changed-file inventory

All paths below are additions relative to the preserved0d100ca baseline; no
previous tracked path or mode changed. Publication receipt is saved after the
actual download check.

- `docs/led-feedback-bound-tests.json`
- `docs/led-feedback-build.json`
- `docs/led-feedback-caps-probe.json`
- `docs/led-feedback-dependency-pin.json`
- `docs/led-feedback-design.md`
- `docs/led-feedback-install.md`
- `docs/led-feedback-integrity.json`
- `docs/led-feedback-native.json`
- `docs/led-feedback-owner-check.md`
- `docs/led-feedback-package-tests.json`
- `docs/led-feedback-preservation.json`
- `docs/led-feedback-profile-tests.json`
- `docs/led-feedback-publication.json`
- `docs/led-feedback-related.json`
- `docs/led-feedback-report.md`
- `docs/led-feedback-reproduction.md`
- `docs/led-feedback-rollback.md`
- `docs/led-feedback-source-manifest.json`
- `docs/led-feedback-tool-parser.json`
- `docs/led-feedback-ui.json`
- `downloads/evilduck-led-feedback-macos-install-v1.zip`
- `downloads/evilduck-led-feedback-review.bin`
- `tests/led_feedback/application.patch`
- `tests/led_feedback/build_candidate.py`
- `tests/led_feedback/caps_probe.cpp`
- `tests/led_feedback/core-diagnostics.patch`
- `tests/led_feedback/feedback_diag.cpp`
- `tests/led_feedback/feedback_diag.h`
- `tests/led_feedback/package.py`
- `tests/led_feedback/preflight.py`
- `tests/led_feedback/prepare_core.py`
- `tests/led_feedback/prepare_sources.py`
- `tests/led_feedback/run_caps_probe.py`
- `tests/led_feedback/run_related.py`
- `tests/led_feedback/run_tests.py`
- `tests/led_feedback/startup_decode.py`
- `tests/led_feedback/test_bound_installer.py`
- `tests/led_feedback/test_core_profile.py`
- `tests/led_feedback/test_main.cpp`
- `tests/led_feedback/test_package.py`
- `tests/led_feedback/tool_parser_tests.py`
- `tests/led_feedback/verify_link.py`
- `tools/feedback_core.py`
