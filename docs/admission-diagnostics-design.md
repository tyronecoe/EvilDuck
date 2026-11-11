# Route B admission diagnostics v1

Build identity: **ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1**. This is an uninstalled
review candidate, not new owner acceptance or an installed-byte attestation.
The source parent is local closeout `eb4c5d721e30893f7df908ac610d287d7541acf5`,
reviewed observer-v2 firmware checkpoint `b075e551e07f7b15124bdad3caa564c614f78ba4`.
Existing v2 application: 1,450,624 bytes, SHA-256
`b7ac50eebe6fb5e3d69d97f20004e1014c46fb116845e30864f56de5de6d384e`.

## Root cause and bounded correction

Source loading can refuse a byte before `CompileSession::start()` establishes
the current compilation. The old accessor selected `compiler_.error()` for such
faults: a fresh request could show code 0/line 0, and a reused adapter could show
a previous compiler error. This is incorrect reporting, not an admission bypass.
The two pre-fix controls run on the exact old composition record both outcomes
and zero request-attributable report output.

The maintained delta in `tests/admission_diagnostics/application.patch` changes
only `adapter.cpp` and `adapter.h`; a separate release overlay changes only
`caps_trial.h` identity. The other 198 composed sources retain their original
bytes. Historical source directories, manifests and packages are unchanged.

An adapter-owned `Error` snapshot belongs to the current accepted prepare request.
Eligibility guards run first: busy, reentrant, active-lease and other ineligible
prepares preserve the active request and its diagnostic. Once a new prepare is
accepted, clear the snapshot, physical-line counter and stale deferred-cancel
intent before reader validation or seek can fail.

On the first fault, snapshot its current origin before cancellation/cleanup:

| Origin | Diagnostic and classification |
|---|---|
| Existing admission byte/BOM rejection | `InvalidSource`, existing code **2**, physical fault line, column 1; existing Capability reason. |
| Current compiler failure | Current compiler code/line/column, existing Compiler reason. |
| Current runtime failure | Current runtime code/line/column, existing Runtime reason. |
| Lock timeout/evidence failure | Existing Timeout/FeedbackUnavailable code and runtime line. |
| Reader, size, seek or other non-encoding failure | Existing reason; no fabricated InvalidSource or borrowed earlier compiler/runtime error. |

`diagnostic()` returns the retained snapshot. While a new request is loading or
compiling without a fault, it returns no error. Later cleanup/cancellation cannot
replace the first cause. A successful subsequent request has clean diagnostics.
There is no new public status schema or error-code numbering.

## Source and execution preservation

Source acceptance and validation order remain unchanged. Count physical lines
from one, advancing only on accepted LF bytes, including the LF in CRLF. Keep
that counter across chunks and Retry without processing a byte twice. Bare CR
remains the compiler's existing responsibility; no competing grammar validator
is introduced. Partial initial BOM at EOF remains InvalidSource on line 1.

Retain the exact optional initial EF BB BF marker, raw source identity/captured
size, 8192-byte raw limit, supported ASCII/control policy, 128 IR limit and every
existing execution budget. Malformed retained source still rejects before lease
acquisition or HID output. Oversized-file classification is not changed.

Compiler/runtime, Legacy/Route B selection, DEFINE, expressions/functions,
H1 experimental encoding, keyboard translation, held/transient ownership,
STOP/cleanup, ambiguity/quarantine, authentication/privacy, EDR1, storage,
dependencies, descriptors, USB identity and partitions remain unchanged.
The USB-only OS-estimate design stays paused; this stage adds no OS capability
and rewrites no historical v1/v2 capture.

## Verification and release requirements

Use the actual composed adapter/coordinator and RAM-only clock/storage/HID mocks.
Retain the raw pre-fix expected-versus-observed controls. Add fresh/reused,
prior compiler/runtime error, valid-invalid-valid, physical-line/chunk/Retry,
BOM/NUL/non-ASCII, reader/seek/size, cancellation/ineligible prepare, first fault,
status publication and per-request zero-output coverage. Derive fixture lines
independently, rather than duplicating the implementation as the oracle.

Run applicable composed regressions and ASan/UBSan/leak checks; old receipts are
historical unless actually rerun. The approved Arduino ESP32 3.3.0 archive-based
profile, committed-source guard, dependency pins and inherited target/release
assertions remain mandatory. Clean-build to a new output directory and measure
the fixed storage and target limits. No build guard may be bypassed to finish.

Prepare one local High Sierra 10.13.6 review ZIP, preserving Bash 3.2, Python 3.8
and esptool 4.12. Bind actual candidate/source/profile/dependency/member hashes.
Reuse the original guarded application-only installer and offline checks, with
explicit new identity binding. Local checkpoint commits are authorized; pushing,
publication, hardware access, installation, flashing and OTA are not.

## Distinct recovery roles

Working DEFINE return: original `working-define-labels-macos-review-v1.zip`,
2,691,374 bytes, SHA-256
`b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed`.
Its application is 1,438,048 bytes, SHA-256
`167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`.
Extract that nested kit separately and use its original guarded install action
for a later deliberate owner return to DEFINE.

The outer rollback instead selects older source/text-v2, 1,413,200 bytes,
SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It lacks later privacy/dashboard fixes and is not a full-device restore.
Neither application-only recovery restores deleted scripts or past settings.
Preserve both exact images, all previous packages/captures/refs and private backups.
