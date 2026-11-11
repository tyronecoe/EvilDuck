# Admission diagnostics v1: local review delivery

**BUILT AND PACKAGED FOR REVIEW — NOT INSTALLED — NOT OWNER-HARDWARE-VERIFIED.**

The current request now owns its source-admission diagnostic. Invalid byte/BOM
requests report existing InvalidSource **code 2** and their own physical line,
before output; previous requests, refused prepares and cleanup cannot replace
that cause. Later valid requests complete with clean diagnostics.

Branch: `routeb-admission-diagnostics-v1`.
Starting HEAD: `eb4c5d721e30893f7df908ac610d287d7541acf5`.
First implementation checkpoint: `f24b0fd8dca6ca7b75a2153e5f02afc61c7b25b6`.
**Verified firmware checkpoint:** `c9fd36c3e03b2d7ffa318b289398ff7dc1c9fd44`.
**Package checkpoint:** `0c799d9bb72447409c9f6c23b2f78edaaa849a9a`.
Build ID: **ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1**.

The last owner-reported installed build remains observer v2. This task performs
no installation or board readback. The separate USB-only OS-estimate design stays
paused; no OS variable, heuristic, host helper or probe is added. Existing accepted
DEFINE/DEL/H1/right-modifier/lock-wait/LED milestones are not reopened.

## Root cause, implementation and source inventory

The old admission gate could fail before the current compiler was initialized.
`Adapter::diagnostic()` then returned the compiler's old error: either None/0/0 on
a fresh adapter or a prior request's error. Admission rejection itself still
worked; this was reporting/state isolation rather than a demonstrated bypass.

The [behavior patch](../tests/admission_diagnostics/application.patch) adds one
fixed Error snapshot and a physical-line counter. Eligibility guards run before
resetting them. An accepted new prepare clears old diagnostic ownership before
reader validation/seek; a refused busy/reentrant/leased prepare changes nothing.
The first fault copies its current compiler/runtime/lock or explicit admission
error before cancellation. Other failure reasons remain unchanged and cannot
borrow a stale compiler error. Deferred cancellation is cleared only when a new
eligible request begins. LF advances physical lines; CRLF counts once and bare
CR remains the compiler's responsibility. Accepted bytes, copying, raw size/BOM
identity, error precedence and existing source/execution bounds are unchanged.

The actual target [201-file inventory](admission-diagnostics-source-inventory.json)
has only these three differences from the reviewed observer-v2 composition:

| Target file | Change |
|---|---|
| `adapter.cpp` | New-request reset, first-cause diagnostic capture and admission-line reporting. |
| `adapter.h` | Eight declared bytes of fixed state, typed fail parameter and request-owned accessor. |
| `caps_trial.h` | Build identity literal only. |

The remaining **198 files are byte-identical**, including compiler/runtime,
coordinator, keyboard mapping/backend, dashboard/privacy code and USB observer.
The normal preparation chain selects the correction through the new exact source
and release manifests. Historical builders/manifests are unchanged. The canonical
[build entry](../tools/build_routeb_candidate.py) selects this new stage.

New test/build/package tools live under `tests/admission_diagnostics`,
`tests/admission_diagnostics_release` and `tests/admission_diagnostics_package`.
The current inventory documents the uninstalled candidate. Exact changed paths,
artifacts and hashes are recorded in [the artifact manifest](admission-diagnostics-artifacts.json).
No Pico code or eval implementation is copied.

## Fresh verification and retained controls

| Verification | Fresh result |
|---|---|
| Pre-fix negative controls | **2 PASS / 12 assertions:** expected defect reproduced, source rejected, zero new reports. |
| Admission-focused composed tests | **40 PASS / 384 assertions**. |
| Existing composed native regressions | **636 PASS / 27,376 assertions**. |
| Observer-v2 regressions | **34 PASS / 10,767 assertions**. |
| DEFINE regressions | **28 PASS / 374 assertions**. |
| Total current-source native cases | **738 PASS / 0 final FAIL / 38,901 assertions**. |
| Build integration controls | **16 PASS**, including actual nested selection, omitted-fix/old-identity negatives and active-hook committed-source guards. |
| Additional target/resource checks | **25 PASS**. |
| Mandatory release chain | **PASS; all 190 inherited assertions retained**, none removed. |
| Package policy | **11 PASS**. |
| Package artifact/mutation checks | **151 PASS**. |
| Bound-installer mock checks | **38 PASS**. |
| Archive and offline preflight | **80 members**, clean CRC and member hashes; fresh extraction passes for application and rollback, no write plan/hardware authorization. |

The [original pre-fix receipt](admission-diagnostics-negative-controls.json) is
immutable at SHA-256
`56ae3e9bdeddc090e11724ab1e2ef8f8ba30929fc04bd88719309a360a1a8360`.
It records fresh invalid source showing code 0/line 0, and prior compiler code
15/line 3 being incorrectly reused for a new invalid request expected at line 1.
Both old requests were refused with no lease and zero request-attributable reports.
The executed control driver is preserved; supplemental bindings are separate.

The [native receipt](admission-diagnostics-native-results.json) covers fresh/reused
adapters, prior compiler/runtime errors, valid-invalid-valid, LF/CRLF, chunk/Retry,
initial/split/malformed/partial/repeated/misplaced BOM, NUL/non-ASCII/UTF-16 bytes,
reader/seek/size failures, loading/compiling cancellation, ineligible prepares,
first fault, actual coordinator/HTTP status and per-request report deltas. Later
valid requests assert exact expected keyboard reports. ASan, UBSan and leak
checking are clean; final test-process stderr is empty.

[Execution epochs](admission-diagnostics-native-execution-epochs.json) attribute
728 passing cases to the first current-source execution and ten to the corrected
dispatcher execution. Ten initial failures were harness routing errors: legacy
V20-V29 IDs were misrouted to four-character V2 IDs. Only those ten were rerun;
unchanged passing bodies and production bindings were retained. Two earlier
fixture-preparation guards caught identity-assertion count and test-ID collisions.
These [development findings](admission-diagnostics-development-notes.json) remain
recorded; no firmware failure is hidden or reclassified as a pass.

Unchanged browser, isolated DEL/DEFINE and earlier observer web receipts are
explicitly reused in [the software summary](admission-diagnostics-test-results.json).
They are historical, not additional fresh pass totals. The old Pico comparison's
39/712 and closeout's 44 checks were not rerun or counted here.

## Clean target, guards and resources

The [build receipt](admission-diagnostics-build.json),
[164 committed inputs](admission-diagnostics-build-inputs.json) and
[mandatory release proof](admission-diagnostics-release-verification.json)
bind the actual compiled adapter/coordinator sources, header dependencies,
linked objects and new typed diagnostic handler to the native-tested sources.
All original SDK/archive/dependency, USB, NVS, authentication, ownership and
source-profile safeguards remain. There is no post-build verifier exception.

The first target attempt stopped before compilation: the pinned parent driver
was reloaded while its own compiler hook was active. The fix loads that pinned
module before the hook and reuses it, while continuing hash checks and executing
the entire original committed-source guard. A new control covers this path.
The [attempt record](admission-diagnostics-build-attempts.json) preserves the
failure and the subsequent successful clean build; no guard was bypassed.

Arduino ESP32 **3.3.0**, S3 USB OTG, CDC on boot, **16 MiB QIO**, custom unchanged
partitions, **PSRAM disabled**, CPU 240 MHz and the approved archive-based profile
are retained. Both application slots remain 7,602,176 bytes; 6,151,232 bytes
remain free per slot. This package is standalone application-only, not merged
firmware or a filesystem image.

| Measurement | Observer v2 | Candidate | Delta |
|---|---:|---:|---:|
| Application image | 1,450,624 B | **1,450,944 B** | **+320 B** |
| Static RAM | 115,392 B | **115,400 B** | **+8 B** |
| Actual target Adapter object | 24,344 B | **24,352 B** | **+8 B** |
| Largest adapter compiler frame | 144 B | **176 B** | **+32 B** |

The [resource measurement](admission-diagnostics-resource-measurement.json) uses
actual ELF symbols and compiler `.su` records. Individual fail/reader-prepare
frames increase 32-to-48 and 64-to-80 bytes. These are compiler frame estimates,
not physical task/IRQ peaks or runtime latency acceptance. The separate native
64-bit Adapter size did not grow because of padding; it is not target RAM proof.
The 4096-byte compiler workspace and all execution budgets remain unchanged.

## Local artifacts and owner review

Application:
`/workspace/scratch/admission-diagnostics/build-v2/build/EvilDuckS3.ino.bin`

```text
1,450,944 bytes
SHA-256 fce91bca0774181a1be6bc691a1303d47f61caba49e979e89bfa678ef41f60f1
```

Local review ZIP:
`/workspace/scratch/admission-diagnostics-release/evilduck-routeb-admission-diagnostics-h1-macos-review-v1.zip`

```text
5,614,647 bytes; 80 members
SHA-256 05fdff0cdb7a0d4336f8dc219c3a501cc7349c9200f95c2f54a36bb9cccffd81
```

The [package receipt](admission-diagnostics-package-verification.json) and
[member identities](admission-diagnostics-archive-integrity.json) bind the images,
source/profile/dependencies, software controls and installer. The installer is
identical to its reviewed parent except the exact preflight hash binding.
High Sierra 10.13.6, Bash 3.2, Python 3.8 and esptool 4.12 conventions are preserved;
checks run in the development environment, not on the owner's Mac.

With EvilDuck unplugged, from the extracted review folder:

```bash
python3 preflight.py --directory .
```

Require integrity PASS, `plan_ready=false`, empty selected write ranges, and
hardware/installation authorization false. Installation is separately owner
operated; this development task does not perform it.

The [short owner sheet](admission-diagnostics-owner-check.md) and package
`BYTE-FIXTURES.md` describe optional later checks: byte-verified source with
unsupported UTF-8 C3 A9 on line 3 rejects code 2/line 3 with blank TextEdit; a later
valid request prints `ADMISSION_OK` plus newline with clean successful status.
Use the existing authenticated POST `/script` and GET readback path, not disabled
`/upload` or editor paste. The supplied optional prior-compiler fixture can check
different error lines. No payload is submitted automatically or executed here.

The nested original working DEFINE kit is unchanged: ZIP SHA-256
`b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed`,
application 1,438,048 bytes, SHA-256
`167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`.
Extract it separately and use its own guarded install action for a later chosen
DEFINE return. The outer rollback is older source/text-v2, 1,413,200 bytes,
SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It lacks later privacy/dashboard fixes and is not a full-device restore.
Preserve every private backup; neither application-only recovery restores
deleted scripts or past settings.

No hardware access, real HID output, physical payload, installation, flashing,
OTA, formatting, settings reset, private-file inspection, remote push, merge or
publication occurred. Physical acceptance is pending. Software and package
verification do not establish host receipt, global release or installed bytes.
