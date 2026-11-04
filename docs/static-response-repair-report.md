# Static-response repair — verified High Sierra review candidate

**REVIEW ONLY — NOT INSTALLED — NOT OWNER-HARDWARE-VERIFIED.**

Build ID: **`ROUTEB-STATIC-RESPONSE-REPAIR-v1`**. The candidate repairs static
resource serving while preserving the existing editor safety, credential privacy,
dashboard, STOP and composed Route B functionality. It adds no payload, HID,
storage, USB-descriptor or host-data collection feature.

## Failure evidence and scope

The previous editor-safety application
`e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0`
was installed by the owner; its installer reported both application comparisons
passing. The owner then captured Chrome **116.0.5845.187** on the reported High
Sierra 10.13.6 host receiving `index.js` as HTTP 200 with **Content-Length: 0**.
The password handler was undefined and both Checking labels remained unchanged.
An isolated GET separately returned the exact 31,932-byte JavaScript body.

The owner also reports Chrome on iPhone connected to EvilDuck Wi-Fi; the supplied
iPhone screenshot shows the same initial Checking display. The LTE indicator does
not disprove that report, and no cause for the icon is inferred from Low Data
Mode. Detailed response-length evidence is from the Mac, not the iPhone.

This establishes the earlier **empty-response failure**, not an incorrect saved
password. The earlier package-integrity/software passes did not establish a
working dashboard on physical hardware. The e825 image is preserved as **faulty
historical evidence**, never a known-good recovery target. The favicon's separate
unsupported-path 503 remains outside the repair.

The SDK's char-pointer `send_P` selected a whole-body heap `String` response.
Allocation failure can leave status 200 and length zero; controlled tests with
actual SDK/WString code reproduce that path. Heap pressure is a supported
explanation, not a directly measured owner-device heap condition.

## Source, compile and verifier identities

| Role | Revision |
|---|---|
| Preserved source-only repair checkpoint | `7c3ed81238b89b89b92924c366ecbb9afe391856` |
| **Actual clean compiler checkpoint C** | `68f7fb2de5af2988a3136eb9222fb8c3e7dee8f5` |
| Host decoder/provenance correction D | `89d499fdb4dde13782cb09c7882ab55cc604a4dd` |
| Verification-only completion helper E | `520716462ffd66858a686e6c3a06eae037b3c5d4` |

The normal `tools/build_routeb_candidate.py` entry now selects the maintained
streaming-response composition. All historical layers remain hash-pinned and
ordered: H1, Privacy Fix 1, dashboard cleanup, reviewed editor safety, reviewed
static-response repair and metadata-only final identity. There is no manual
generated-source replacement.

All **201** final source entries are verified. Relative to the previous editor
image, only **`webserver.cpp` and the build-ID literal in `caps_trial.h`** change;
199 files, including the complete `webfiles.h`, remain identical. Relative to the
Privacy Fix 1 comparison manifest, the cumulative change count is **3/198**.
These are different comparison bases, not contradictory inventory totals.

Eleven static sends use the SDK's explicit immutable byte-pointer/length overload
with `sizeof(resource)-1`. This covers twelve portable aliases and nine literal
resources, plus the inactive legacy error-page fallback. Statuses, MIME types,
routing, content and the existing unknown-path refusal remain unchanged. Static
lifetime and per-response cursors preserve ownership and independent reads.
The SDK still needs smaller object/header/TCP buffers; this is not a claim that
every allocation failure is impossible.

## One clean compile; explicit post-link correction

Exactly **one** clean target compile/link ran through the normal entry using the
approved isolated Arduino ESP32 **3.3.0** archive-based profile. The profile,
dependency guards, USB identity, partitions, 16 MiB flash and PSRAM-disabled
settings are unchanged. The original 26 committed compiler-input rows and raw
compile report are preserved. Input manifest SHA-256:

```text
9a3ff6f4f4ff312bd0b353bf72fbbf1e17fe82d2a28f97ad62c4ed7c17295d0d
```

The first host verifier stopped because its length extractor recognized direct
immediates/literal words but missed valid signed `MOVI` plus `ADDMI` forms. For
example, the compiler forms the HTML length as `152 + 0x2f00 = 12,184` and CSS as
`-25 + 0x7d00 = 31,975`. This was a verifier decoding gap, not missing resource
data or incorrect target code.

Revision D explicitly decodes actual pointer/length registers at all **ten**
compiled asset-send callsites, covering all nine resources. Negative controls
reject corrupted immediates, pointers, extra NUL lengths and stale/missing
witnesses. Original C Git blobs are all checked; only the exact host-verifier row
may differ at D, recorded with its old/new size, hash and last-touch revision.
The compiled source inventory and images do not change. D is never represented
as the original compiler context.

The recorded post-compile tail was completed without rerunning the fresh-only
compile prefix. Its exact extraction, skipped prefix, source hashes and process
trace are retained. The completion guard initially refused an inherited compiler
tool-path query. Revision E permits **only** the pinned compiler's two-argument
`-print-prog-name=ld` query; compilation, linking, other compiler queries, shell
and hardware operations remain refused. The original failed metadata is retained.
No release assertion was removed to accommodate either correction.

Full release verification passed after that completion: **six frozen layers,
190 inherited Python verifier Assert nodes retained, zero removed, zero unrelated
expected hashes changed**. This is a source-predicate count, not 190 separately
enumerated unit cases. The application, ELF, original compiler-input manifest and
all 201 source entries have identical before/after hashes. The completion receipt
records `firmware_recompiled: false` and is included in the review ZIP.

## Actual target evidence and artifacts

The actual object and linked ELF show the asset dispatcher selecting the
byte-pointer/length API, the factory calling `AsyncProgmemResponse`, and the
streaming fill implementation. This is bound to the actual compiler dependency,
source/object hashes and map LOADs. It is not inferred merely from resource
presence or function names elsewhere in the image. The legitimate small ordinary
503 response is preserved; globally banning all ordinary responses would be wrong.

All five complete NUL-terminated dashboard/settings resources occur exactly once
in both ELF and BIN. All nine wire bodies, pointer/length pairs, MIME/status
metadata, partial reads and independent cursors are covered separately.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Application BIN | 1,437,696 | `d5fe0932fe915443a5e53030969c6792409f719d427681304a7102355b2d7946` |
| ELF, provenance only | 23,642,852 | `4f530f7e0eb330585faaed3311de7b6b4227514b2517f6d6c36615da128e9c44` |
| Full release receipt | 2,573,624 | `e971ec9476db6371af96b4dd45d703508b56ffbf37f9b9d99853beb22f5ebd10` |
| Post-compile completion receipt | See included file | `329829851a14e7d8fca2d213f013c54ea1a197f815f2949624112cd01d9efdfa` |

The application is not a merged migration image. The ELF is evidence, not a
flashing image, and is not included as an install target. ZIP/download identities
and actual packaging checks are recorded separately after constructing and
downloading the archive, avoiding a self-referential embedded report.

## Fresh checks and reused evidence

| Fresh checks | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| Native SDK response cases | 33 | 0 | 976 |
| Inert browser using SDK-reconstructed bodies | 3 | 0 | 26 |
| Source-repair composition controls | 7 | 0 | 32 |
| Affected native privacy cases | 28 | 0 | 736 |
| Existing composed native regressions | 558 | 0 | 23,901 |
| Inherited inert dashboard browser groups | 9 | 0 | 207 |
| Target composition/old-image controls | 8 | 0 | Not separately counted |
| Actual decoder and C/D provenance controls | 11 | 0 | Not separately counted |
| Completion/no-rebuild policy controls | 6 | 0 | Not separately counted |

The independent rerun repeats the same 43 response/browser/source groups; it is
not another 43 unique cases. Native ASan, UBSan and leak checks are clean and
stderr is empty. The privacy runner preserves all historical C++ cases and
sanitizer flags, binds four actual application inputs, and adds only the missing
byte/length API to generated mocks. It does not model streaming; the separate
actual-SDK suite does that. Initial mock/browser setup failures are preserved.

The earlier 64-group/551-assertion editor suite is **reused historical evidence**
only: its exact header input remains unchanged. It is not counted as fresh here.
Mocks do not measure real ESP32 heap/TCP behavior or establish native High Sierra,
iPhone, newer macOS, Windows, Linux-desktop or Android acceptance.

[Results and full test receipts](static-response-repair-results.json) ·
[Full linked build receipt](static-response-repair-build.json) ·
[Artifact/source inventory](static-response-repair-artifacts.json) ·
[Completion audit](static-response-repair-postcompile.json).

## Resource measurements and recovery

| Compiler/static measurement | Faulty e825 image | New candidate | Change |
|---|---:|---:|---:|
| Compiler program bytes | 1,437,555 | 1,437,547 | -8 |
| Application BIN bytes | 1,437,696 | 1,437,696 | 0 |
| Static RAM | 113,896 | 113,896 | 0 |
| Free bytes per 7,602,176-byte slot | 6,164,480 | 6,164,480 | 0 |

These are compiler/build measurements, not runtime heap or timing measurements.
The metadata has a distinct build ID; the exact new application hash establishes
its packaged identity. The older e825 image must not be substituted even though
its binary size is the same.

Exact mandatory older source/text-v2 rollback: **1,413,200 bytes**, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It lacks Privacy Fix 1 and subsequent dashboard/editor/response repairs. It is
application-only and does not restore scripts, filesystem content or old settings.
Historical images/packages/refs stay preserved. The owner's private `w7uhm8z7`
backup is not accessed or published.

## Owner review boundary

From a fresh extraction, with EvilDuck **unplugged**:

```bash
python3 preflight.py --directory .
```

Require package integrity PASS, no selected write ranges, `plan_ready: false`
and no hardware/installation authorization. The installer lineage and safeguards
are unchanged apart from generated release binding. Its historical backup-folder
prefix does not identify the new application. A later installation deliberately
creates a new private full-flash backup before final confirmation; it may contain
credentials and scripts. No existing backup is overwritten or deleted.

Use the [short acceptance sheet](static-response-repair-acceptance.md) after a
separately authorized owner installation: correlate the new app identity with a
fresh full-page, nonempty script response and normal authentication/status.
Matching an isolated GET alone does not distinguish this image from the old
one. No payload, settings save, file overwrite or repeat of accepted keyboard,
lock-wait, executed STOP or privacy milestones is requested.

[Reproduction](static-response-repair-reproduction.md) ·
[Platform evidence boundaries](static-response-repair-platforms.md).
H1 remains opt-in/experimental; canonical Hak5 encoding remains unresolved.
No hardware access, flashing, OTA, owner-script execution, password reset,
storage mutation or private backup/credential access occurred in this task.
