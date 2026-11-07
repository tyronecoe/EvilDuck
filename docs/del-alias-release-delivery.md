# DEL alias — local review delivery

**BUILT — PACKAGED — NOT INSTALLED — NOT OWNER-HARDWARE-VERIFIED — NOT PUSHED.**

`ROUTEB-DEL-ALIAS-H1-v1` adds exact uppercase `DEL` as the documented `DELETE`
alias, usage 0x4c (forward delete). Existing `DEL()` functions, numeric function
calls, `$DEL`, literal text, modifiers, held state and bounded REPEAT remain
valid. H1 stays opt-in and experimental; canonical Hak5 numeric encoding remains
unresolved. [Exact grammar and preservation contract](del-alias-design.md).

Branch: `routeb-del-alias-h1-v1`. Firmware/verification checkpoint:
`2e3efa295d46aef55b4d39af9cf3a9a40bb70422`. Package checkpoint:
`af579243978006fe4951236452b98719b351868c`. Both are local; no remote publication
or merge occurred. The previous REPEAT release remains the owner-recorded
installed build; no new device readback or physical acceptance is claimed.

## Review artifacts and identities

[High Sierra review ZIP](/workspace/scratch/del-alias-release/evilduck-routeb-del-alias-h1-macos-review-v1.zip)
— 2,644,497 bytes, 43 members, SHA-256:

```text
6dbc548c0e58714511c77f29ef50449f07d3ed94ef4422d09fe755e3f4b0f116
```

[Application BIN](/workspace/scratch/del-alias-release/build-v1/build/EvilDuckS3.ino.bin)
— 1,437,888 bytes, SHA-256:

```text
d1571be81619e464ee997d0ba8ebbf7e7b8a8b4252e4debc9d9144b9ebe6b379
```

ELF: 23,643,224 bytes, SHA-256
`d47c6f0e4fc7339029efaf89a885223c54d023473b40ff36109e42626eebb86f`.

[Manifest](/workspace/scratch/del-alias-release/package-v1/manifest.json),
[three-trial owner sheet](/workspace/scratch/del-alias-release/package-v1/OWNER-CHECK.md),
and [complete results, changed-file inventory and 201-source inventory](del-alias-release-results.json).

The archive contains the exact older source/text-v2 rollback application,
1,413,200 bytes, SHA-256:

```text
cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02
```

It is byte-identical to the prior published kit's rollback. It is standalone
application recovery, not a complete flash/filesystem restore, and lacks later
privacy/dashboard/editor fixes. Preserve all existing recovery files. The
faulty e825 editor candidate is not a known-good rollback.

## Verification actually completed

| Group | PASS | FAIL | Assertions/checks |
| --- | ---: | ---: | ---: |
| Focused DEL actual-module cases | 27 | 0 | 797 assertions |
| Existing composed native regressions | 636 | 0 | 27,376 assertions |
| Web/component groups | 86 | 0 | 1,518 assertions |
| Source composition/refusal controls | 7 | 0 | 36 assertions |
| Release-verifier controls, actual candidate included | 25 | 0 | No skips |
| Package source policies | 6 | 0 | Checks |
| Package negative controls | 58 | 0 | Checks |
| Archive/layout controls | 83 | 0 | Checks |
| Actual bound-installer mocks | 38 | 0 | Checks |
| Independent fresh extraction/offline preflight | 1 | 0 | Exit 0 |

Distinct native total: **663 cases, 28,173 assertions**. ASan, UBSan and leak
checking passed. Native tests compile the actual core, adapter, scheduler and
backend against RAM-only transport/storage/clock mocks. They cover alias/report
parity, modifiers, cross-alias ownership/collision, rollover refusal, retries,
STOP/disconnect/quarantine, restart, subsequent runs, DEFINE, literal text,
DEL() preservation and retained malformed-source rejection. Historical mock
build labels are disclosed in the focused receipt; final target identity is
independently checked against all 201 sources.

An old-source control demonstrates that the original compiler rejects DEL,
accepts DELETE and permits DEL() functions. Existing REPEAT causal controls
remain explicitly historical parent contrasts. No old physical trial was
repeated or relabelled as a new pass.

An initial focused harness setup check caught a generated-mock binding issue
before compilation; its receipt remains preserved. No tests ran in that setup
attempt. The corrected focused suite passed. The first clean target build and
its full release chain passed. Two prebuild candidate-dependent checks were
temporarily skipped; all 25 passed once the actual ELF existed.

The normal build entry executed the unchanged committed-source guard, binding
**66 inputs** to the firmware checkpoint. It then performed a clean isolated
Arduino ESP32 **3.3.0** build with the approved archive/toolchain, USB identity,
custom partitions, 16 MiB flash and PSRAM disabled. No guard bypass or
post-compilation verifier change was used.

All **190 inherited assertions** remain and pass. In addition to existing
streamed-resource, ownership, H1, lock, startup and REPEAT proofs, the new target
verification decodes the linked named-key table and its pointer/usage rows:
distinct DEL and DELETE strings both map to 0x4c. Executable table bounds and
compiler reachability are verified. Arduino's generated header has a `#line`
prefix; verification proves the remaining bytes equal the reviewed header.

| Resource | DEL candidate | Change from REPEAT |
| --- | ---: | ---: |
| Application BIN | 1,437,888 bytes | 0 |
| Compiler program | 1,437,747 bytes | +12 |
| Static RAM | 113,896 bytes | 0 |
| Free per application slot | 6,164,288 bytes | 0 |

No physical heap, host timing, endpoint receipt or host-global release
measurement is claimed.

## Offline review and later owner checks

With EvilDuck **unplugged**, extract to a new folder. From that folder run only:

```bash
python3 preflight.py --directory .
```

Expect integrity PASS, `plan_ready=false`, empty write ranges,
`installed_metadata=NOT_SUPPLIED`, and installation/hardware authorization false.
This is a standard-library-only offline check. High Sierra 10.13.6, Bash 3.2,
Python 3.8 and esptool 4.12 compatibility is preserved by the unchanged guarded
installer. No installer, hardware connection or payload execution was performed.

The included owner sheet contains only three small TextEdit trials for a later,
separately owner-operated installation: DEL/DELETE produce `ac` on two lines;
standalone REPEAT produces `ade`; malformed `DEL extra` compile-rejects at line
2, code 13, before any text. Record visible output and request status separately.
STOP remains available. Do not automatically retry ambiguous trials or execute
the inherited rm-*.txt provenance fixtures as part of this release.

Future installation/rollback instructions preserve the existing guarded
application-only writes at 0x10000 and 0x750000. They exclude bootloader,
partition table, NVS, OTA metadata and filesystems, and do not automatically
reboot or start scripts. The helper creates a new private full-flash backup
before final confirmation; it may contain credentials/settings/scripts and
remains if the owner declines. Existing backups are never deleted here.

## Preservation and OS-fingerprinting follow-up

Only composed core.cpp, shortcut_keys.h and the candidate build-ID literal
differ from the 201-file parent; **198 sources remain identical**. In repository
history, only the canonical selector and consolidated inventory modify
pre-existing paths; **2,517 other historical files/modes and all 94 remote refs
remain unchanged**. New overlays, verifiers, package integration and receipts
are additive. Existing published ZIPs and recovery bytes are untouched.

The [updated inventory](routeb-current-compatibility.md) and
[separate roadmap](routeb-compatibility-roadmap-20261107.md) distinguish source,
runtime, USB and host evidence. Admission diagnostics remain a separate pending
repair, not silently included in this candidate.

The owner's later OS request is addressed in the
[targeted investigation](os-fingerprinting-compatibility-investigation.md).
Unmodified official OS_DETECT source rejects at line 50 because its DEFINE label
exceeds the current bound; further compile-only fixtures demonstrate missing
telemetry, OS symbols, indicator and lock/mode interfaces. Fifteen observations
are not physical detection evidence. No OS-detection firmware, fabricated
counter, manual-OS substitute, identity change or host probe was added.

**BUILT: YES; PACKAGED: YES; INSTALLED: NO; HARDWARE-VERIFIED: NO; PUSHED: NO.**
