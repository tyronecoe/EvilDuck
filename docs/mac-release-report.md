# Mac caps/queue package completion

**GO: software build/package review and owner-local read-only preflight.**
**No physical installation, application boot, OTA or HID testing was authorized
or performed.** Caps Lock output and keyboard LED feedback remain physically
unverified. This is a diagnostics-first candidate with the previously reviewed
source fixes, not a confirmed physical Caps Lock repair.

## Approval and source identity

Starting HEAD f47e46dec2fa19ef7310ea6ffd36fed8a23aefb3 was clean. The owner explicitly
approved the separate publisher-archive build proposed there. Work is on the new
caps-queue-macos-install-release branch. The additive build/source revision is
ace54c7 (full immutable identity in the package manifest). Firmware composition
is the unchanged tests/caps_queue composition from d32a60b. No historical file,
profile, verifier, pin, firmware source, partition, USB identity or existing
package was modified. The new profile does not purport to reconstruct the
historical unavailable full core tree. The original proposal stays unapproved
as a historical proposal; the new dependency pin records this separate approval.

Source selection preserves compact STOP/details, request-correlated execution
receipts, authenticated SD/library deletion, LED exact download/endpoint fixes,
callback counters and failed-save/stale-run protection. No language behavior,
Caps tap timing, general HOLD/RELEASE capability or guessed ID0 routing was added.
See firmware notes for remaining LED and host-release limits.

## Build and linked provenance

Clean ArduinoCLI1.3.1 build used ESP32 core3.3.0, ESP-IDF5.5 precompiled SDK,
Xtensa GCC14.2.0, 16MiB custom partition profile, PSRAM disabled, USB-OTG/TinyUSB,
CDC on boot, QIO80/240MHz configuration and DIO80/16MiB application image header.
Existing HID and NVS patches apply with zero fuzz to an independent core copy.
The installed raw core and SDK are untouched. All177 consumed SDK archives match
both Stage28W and the working STOP/LED receipt, compared by SDK-relative path.
No SDK archive is rebuilt or substituted. Full-tree fingerprints and patch hashes
are in mac-release-dependency-pin.json; compiler/source/object/archive/script,
source195-file inventory and allocated ELF-to-image evidence are in
mac-release-build.json. The exact original/patched inventories remain in the
historical mac-install-core-inventory.json.

The initial compile stopped at a missing NeoPixel header. Restoring the previously
recorded NeoPixel1.15.5 using the publisher checksum resolved that setup failure;
its complete source tree is separately pinned. A subsequent clean compile passed.
The first supplemental post-link library comparison exposed a Python tuple/list
serialization mismatch in the new checker; normalizing the representation fixed
the comparison, with identical file hashes. Final closure passed:281 linked
inputs,3 linker response files,13 linker scripts,177 SDK archives. No target
source or safety predicate was relaxed to resolve either issue.

The additive final-link adapter checks the unchanged historical verifier SHA,
substitutes only the new core guard and the existing bounded Xtensa disassembly
decoders, retaining all safety predicates. Actual linked evidence confirms the
single strong HID SET_REPORT callback, OUTPUT handler, no FEATURE-as-LED
workaround, NVS original-error hook/no automatic Arduino erase, controlled
startup readiness/storage-before-HID, no examples/autorun, Route B selection,
8KiB loop stack,5-tick bounded HTTP wait and instrumented diagnostic calls.

| Measurement | New | Current c20 build | Difference |
|---|---:|---:|---:|
| Compiler program | 1,381,631 | 1,376,423 | +5,208 |
| Application BIN | 1,381,776 | 1,376,576 | +5,200 |
| Static RAM | 107,488 | 107,480 | +8 |
| Free bytes per0x740000 OTA slot | 6,220,400 | 6,225,600 | -5,200 |
| Free OTA percentage | 81.8239409% | 81.8923424% | -0.0684015 points |

Application SHA-256:
573a86715f41f9d5e6628a8ff9117c176f178c8c014c5986d1f8e9bca01fc1bf
ELF SHA-256:
bcc8b0ce6fe2d5f6f46ebb709aa2115f312e107d2670d887475b2099af241b12

Compiler frames: Program::compile2496B, diagnostics1888B, CLI parse1728B; these
are individual compiler estimates, not call-chain totals or physical stack
high-water. No new dynamic key queue/ownership structure was added. Native
allocation/leak checks cover mocks; no embedded heap/latency/transport claim is
made. Normal writable SDK NVS recovery risks are unchanged.

## Mac package and exact plan

Download evilduck-caps-queue-macos-install-v1.zip. Exact size, SHA and complete
20-member inventory are in mac-release-integrity.json. No private owner data,
credentials, backup, merged image, bootloader write or source dependency installer
is included. Existing prior firmware packages remain byte-identical.

The ZIP includes new application.bin; exact c20dc399 rollback-application.bin;
INSTALL-MAC.md/ROLLBACK-MAC.md; check-default Bash launcher; separate deliberate
rollback launcher; bound Python3.8 installer; strict preflight; inspection-only
partition table; manifests/build receipts/source provenance; pinned partition
parser and licenses. Executable bits are unnecessary: invoke launchers with bash.
No host LED sender runs during installation.

Package checks do not authorize writes. The installer requires a fresh supplied
ROM port and observed S3/16MB/security state, exact current table/OTA state and
package identities, creates a new private full16MiB backup before confirmation,
then re-identifies/rereads/revalidates. It writes a single selected image into
both apps and explicitly verifies each slot. No automatic reboot/retry occurs.
There is no full-chip or separate erase API. Two-slot updates are not atomic.
Interrupted/failed writes require staying in ROM and a deliberate fresh rollback
review, not booting a possibly partial image.

| Image | Write offsets | Image bytes | Image-rounded erase intervals, end exclusive |
|---|---|---:|---|
| New application |0x10000,0x750000|1,381,776|[0x10000,0x162000),[0x750000,0x8a2000)|
| c20 rollback |0x10000,0x750000|1,376,576|[0x10000,0x161000),[0x750000,0x8a1000)|

Each interval is within its0x740000 application slot. Bootloader, table, NVS,
OTA metadata, SPIFFS and coredump are excluded. The new plan cannot migrate the
old installed partition layout; it rejects it. Exact app0 initializer state is a
narrow support contract, not a general OTA decoder. Different valid metadata
requires separate review; do not force acceptance by rewriting OTA.

Rollback SHA-256:
c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4
It is the immediate current-working STOP/LED build from d18b7fd/package3dd4a083,
not the older de24 shortcut rollback previously bundled with that package.

## Fresh relevant verification

| Executed suite | PASS | Unexpected FAIL | Assertions tracked |
|---|---:|---:|---:|
| caps_queue actual-source native composition |125|0|6,574|
| unchanged relevant backend/diagnostic regression cases |63|0|2,650|
| actual embedded UI JavaScript |18|0|31|
| historical proposal/profile rejection tests |21|0|case counts only|
| unbound installer engine tests |42|0|case counts only|
| additive archive guard tests |11|0|case counts only|
| real pinned esptool4.12 parser-only command vectors |14|0|case counts only|
| extracted package/image/layout negative tests |37|0|case counts only|
| bound release + actual validator + injected device responses |36|0|case counts only|

Total367 PASS cases,0 final unexpected failures. C++ assertions9,224; JS
assertions31; Python case totals are not invented assertion totals. Native C++
ASan/UBSan/leak checks clean. Python/Node are not reported as ASan tests. Relevant
unchanged regressions explicitly omit T34 (Linux-vs-RTOS identity premise) and
X13/X15 (old diagnostic-size assumptions); their classifications are preserved,
with the current identity/bound exercised by K25/H15. No historical XPASS/XFAIL
was relabeled and no full unrelated historical suite rerun is claimed.
235 frozen Stage26 files pass independent byte-identity verification.

Package negatives cover missing/corrupt/wrong images, chip/layout/OTA/security,
ports/tool versions, metadata changes, cancellation, backup failure/shortness,
write/verify failures, path injection, symlinks, changed helper and private extras.
The bound tests use actual image/header/hash/partition/OTA validators against
public release files and synthetic device data. The parser harness executes only
the verified esptool argument-parser AST; its operation dispatcher is omitted.
None of these checks sends a real command to a board. Python3.8 grammar and Bash
syntax pass; native High Sierra serial execution is still untested.

## Publication and remaining limits

Only the new branch is to be pushed. Pre-publication snapshot contains59 previous
remote refs. The publication receipt records the actual after-push comparison,
commit-pinned download, downloaded size/hash, all extracted bytes, and application
and c20 rollback checks. Do not infer download verification from ZIP creation.

Owner next step: download/hash-check/fresh-extract, inspect the guides, and only
then perform separately authorized read-only ROM checks. Physical installation
and boot still require separate owner authorization. No physical access, flash,
erase, OTA, HID output, owner script or host sender execution occurred here.

## Published result and file inventory

Package commit30310d08b6b833af146b46548ecb4141554180c0 was pushed, fetched over its
commit-pinned raw GitHub URL, size/SHA-checked, CRC/member checked, compared
byte-for-byte across all20 extracted files, and passed extracted package preflight.
ZIP2,155,369 bytes; SHA-256:
b5b238c04e4fb40cb19f41fcf22c7a072a26b605176e3ea52077de693e3fab71
The first download inspection imported its helper without suppressing Python's
cache output, correctly triggering the strict unexpected-file rejection. A fresh
extraction with bytecode disabled passed; the ZIP never contained that cache.
The released CLI already disables bytecode before importing its helper.
The publication receipt retains the actual downloaded file identities and prior
ref inventory. All59 prior refs remain unchanged; only the new branch was added.

Every file added in this follow-up (no existing file modified):
- `docs/mac-release-bound-tests.json`
- `docs/mac-release-build.json`
- `docs/mac-release-core-receipt.json`
- `docs/mac-release-dependency-pin.json`
- `docs/mac-release-firmware-notes.md`
- `docs/mac-release-historical-profile-tests.json`
- `docs/mac-release-install.md`
- `docs/mac-release-installer-engine-tests.json`
- `docs/mac-release-integrity.json`
- `docs/mac-release-native.json`
- `docs/mac-release-neopixel-pin.json`
- `docs/mac-release-package-tests.json`
- `docs/mac-release-profile-tests.json`
- `docs/mac-release-publication.json`
- `docs/mac-release-related.json`
- `docs/mac-release-report.md`
- `docs/mac-release-reproduction.md`
- `docs/mac-release-rollback.md`
- `docs/mac-release-tool-parser.json`
- `docs/mac-release-ui.json`
- `downloads/evilduck-caps-queue-macos-install-v1.zip`
- `downloads/evilduck-caps-queue-review.bin`
- `tests/mac_release/build_candidate.py`
- `tests/mac_release/package.py`
- `tests/mac_release/preflight.py`
- `tests/mac_release/prepare_core.py`
- `tests/mac_release/run_tests.py`
- `tests/mac_release/startup_decode.py`
- `tests/mac_release/test_archive_profile.py`
- `tests/mac_release/test_bound_installer.py`
- `tests/mac_release/tool_parser_tests.py`
- `tests/mac_release/verify_link.py`
- `tools/archive_core.py`
