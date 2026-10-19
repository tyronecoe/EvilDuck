# Ordinary Mac Caps timing — focused upgrade report

Baseline report:baddb8f2d3bb6060e0f72e6cbe58377c894c86bb. New branch:
mac-caps-timing-profile. BuildId: **MAC-CAPS-TIMING-20261019-v1**.

## Result and owner evidence

Owner-operated evidence confirms the PRIOR500ms diagnostic changed EvilDuck-
generated case and delivered genuine Caps LED OUTPUT on High Sierra10.13.6.
Laptop and Razer state can remain independent. The laptop's light is not a new
acceptance criterion. See mac-caps-owner-evidence.md for exact handoff attribution,
trial8/9 timing and limits. Codex did not run hardware or independently inspect the
owner's source video/photo/private backups. Only500ms is confirmed; no minimum
threshold or100/250ms success is inferred.

This upgrade makes500ms available to ordinary standalone Route B CAPSLOCK through
an explicit authenticated RAM-only setting. Default stays5ms. Each queued run
captures its value at admission, exposed separately from the future selection.
Settings changes cannot shorten/lengthen an admitted press. Chords/modifiers and
other keys remain unchanged. Diagnostic baseline/100/250/500 remain independent.
No parser, broad ownership language, global Mac setting, USB identity/descriptor,
settings schema, core/SDK patch, boot/storage/OTA behavior or automatic replay changes.

GET/POST /caps-timing and dashboard controls show selectedMs and requestCapsMs.
Only mode=standard/mac is accepted; lifetime ends at reboot. POST does not start
execution or persist settings. /run returns effectiveCapsMs; /status captures
routeBCapsMs coherently with request ID. New LED age/last-known fields distinguish
fresh/stale/unknown without weakening5-second validity or session checks.
Compact STOP, deletion authentication/confirmation and failed-save protections stay.

The report encoding gate is reportModifiers0,count1,usage0x39. Actual composer
com.cpp schedules waitFor after successful beginReport; no blocking sleep or delayed
work survives ownership. Existing backend lease, STOP, deadlines, cleanup readiness
polling and ambiguous-submit quarantine remain. A cancelled/failed Caps operation
is not guaranteed to restore a host lock or release all host keys.

## Verification actually executed

| Suite | PASS | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| Actual composed native code:32 new +175 inherited |207|0|7,257|
| Relevant unchanged backend/diagnostic tests |63|0|2,650|
| Embedded UI in Node VM |34|0|57|
| Existing additive-core negative/positive guards |14|0|Case-accounted|
| Real esptool4.12 parser AST, dispatcher omitted |14|0|Case-accounted|

C++ counted assertions9,907; JS57. Native and related suites pass ASan/UBSan/leak
detection. Python guards are case-accounted, not invented assertion totals. The
initial harness configuration failed before the intended new suite; it was corrected.
The final native run rebuilt after refining the suspend mock to model not-ready
without inventing an unmount/loss. No failed or aborted run is counted as a pass.
Historical sources are unchanged; only copied buildId literals follow this release.
T34/X13/X15 exclusions retain documented previous reasons. No historical XFAIL or
XPASS is relabeled. Protected235-file Stage26 freeze and actual linked descriptor
checks pass separately. No unrelated regression suites were added to inflate totals.
Package fault-injection37/37 and bound-installer38/38 also passed after archive
construction. There are407 case-accounted PASS cases/groups, zero unexpected
failures, plus separately reported linked-descriptor and freeze checks. Actual
public download verification is recorded in the publication receipt. Software results are not a new physical acceptance pass.

## Clean build and resource comparison

The approved isolated archive-based Arduino ESP32 core3.3.0 profile and all177
ESP-IDF5.5 archives are unchanged. Xtensa GCC14.2.0/ArduinoCLI1.3.1; existing
ESP32-S3/16MiB/custom partitions, PSRAM-disabled and USB-OTG/CDC settings.
Post-link verification retains historical guards and verifies the real com update
call to the admitted Caps value, strong feedback hooks and exact regenerated BIN.

| Measurement | Prior Caps-duration | Candidate | Change |
|---|---:|---:|---:|
| Compiler program bytes |1,392,063|1,397,819|+5,756|
| Application BIN bytes |1,392,208|1,397,968|+5,760|
| Static RAM bytes |107,768|107,776|+8|
| Free bytes per0x740000 OTA slot |6,209,968|6,204,208|-5,760|

Free slot81.610949%. Application SHA256:
`5e10009fd3e5a0a862b4f7bed1f7f28ba8464f7bb1066fd8091c6e01b2ed4a59`.
ELF SHA256:
`901bf12e8f6457b040957ba4a712a25262a1e3110697bf409d4ecf437974f92e`.
See mac-caps-build.json for exact source/object/archive/frame provenance. Core tree
remains a79b9c7e42e7ea2066815271117eeac23fe0a27e65fa00657dc268b70c22c53a.

Compiler frames:com update80B unchanged; coordinator tick368B vs352B; new timing
HTTP640B; LED diagnostics3712B vs3680B. Loop stack remains8192B; pinned AsyncTCP
default task16KiB. Added timing state/accessors use fixed storage; no dynamic collection/queue is
added. HTTP String/response framework allocations still occur. These are
source/compiler observations, not
physical heap, latency, stack high-water or whole-call-chain stack measurements.

## Compatibility and finite next steps

mac-caps-compatibility.md audits selected versus legacy features. Route B already
supports its bounded typing/expression/control/function subset independently of
another keyboard's LED. It does NOT connect legacy WAIT_FOR_CAPS_*, lock-state
save/restore or $_CAPSLOCK_ON into this compiler. Ownership commands still fail
the capability gate before output. No full DuckyScript3.0 compatibility is claimed.
Apple's retrieved per-service Caps code is consistent explanatory source, not an
owner OS capture; fresh Hak5 retrieval returned403, recorded honestly.

Caps OUTPUT addressed to EvilDuck is not a keystroke stream or physical sensor.
No Razer passthrough/descriptor change is promised to observe another keyboard.
The fixed RAM-only EVILDUCK TEST 123 protocol is custom EDR1, not Hak5 wire
compatibility. It uses Caps CLOCK + Num DATA; Scroll is not required. Num,
complete decode and native host helper remain unverified. The smallest finite
Num observation and a separately versioned CAPS-only alternative proposal are
provided without implementing a logger or broad host helper.

## Package, rollback and boundary

New package:evilduck-mac-caps-macos-install-v1.zip. Rollback MUST be the owner-tested
Caps-duration1,392,208byte application
58b0fb93cd39f614109fd3c0079d9e364597c8eb79ee4850955542b8d54caf72.
The immutable prior ZIP was freshly downloaded and that exact rollback checked;
older2c657f0c is not substituted. No whole-flash private image is bundled.

Default read-only, fresh chip/security/table/OTA checks, NEW private backup,
typed INSTALL/ROLLBACK, repeat revalidation and two independent app comparisons
remain. App-only slots0x10000/0x750000; all nonapplication regions and old backups
untouched. Numbered tool Step start/PASS/FAIL, bounded waits and no auto reboot,
retry or physical action retain High Sierra/Python3.8/Bash compatibility checks.
No global toolchain or historical fingerprint was modified.

GO: review the concrete package and, after separate owner authorization, use the
single A/B/A TextEdit acceptance fixture in OWNER-CHECK.md. Confirm opt-in500ms
again after reboot. NO-GO: cloud installation, OTA/HID/host tests, automatic replay,
claim of new physical acceptance or completed reflection/logger. Num-channel
observation is optional and finite. Stop on ambiguous output; do not blindly toggle.
Final publication receipt records exact commits, downloads, all changed files and
comparison of every prior remote ref. No further feature stage starts automatically.

## Release artifact identity

Source/build commit:9e4b7f763d9096b46d2d7edcf3e0dc5c377eaf85.
Package:evilduck-mac-caps-macos-install-v1.zip,2,226,536bytes,
SHA2562f3b398e04f755c751b1ae4aa3602eec133a2e70c44c3fc1e72474d09f2ac77f.
The public download verification receipt will record the immutable package commit,
all25 member hashes, candidate and exact prior-working rollback verification.
Serialized unified-diff patch context includes required blank-line space markers;
whitespace review excludes that serialization, not the actual source checks.
