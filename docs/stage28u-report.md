# Stage28U — portable Route B coordinator and bounded file dispatch

**GO: review the isolated candidate. NO-GO: production integration/deployment,
linked firmware, live USB/HID, device operations or automatic Stage28V.**

Exact clean starting parent `3e450127f7e6e1664a97be1107a18253844bfe35` was verified.
Branch: `stage28u-portable-coordinator-file-dispatch`. All changes are new
Stage28U files. Existing source, profiles, partitions, descriptors, core/SDK,
historical reports and T patches remain unchanged.

## Implemented and proven within the software boundary

- A portable, explicit owner task replaces T's host-thread lease. The target uses
  real pinned FreeRTOS handles and critical-section declarations; native tests
  substitute only platform primitives. Four fixed copied requests, monotonic
  IDs and short publication sections avoid borrowed source/HTTP pointers.
- The real duckscript dispatch/status/STOP/update functions are patched only in
  scratch. Legacy remains default; RouteB requires an explicit API. Preparing,
  stopping and quarantine remain busy. Native Runtime steps only on the owner.
- Actual File interface capture is bounded to8,192 bytes,32-byte reads and a
  checked second pass without another source buffer. Seek/position/EOF/size and
  byte changes fail closed. Explicit SD/SPIFFS selection does not fall back.
- Priority STOP/loss bypass ordinary queue saturation and are polled after
  scheduler work before the next source tick. No accepted work is retroactively
  withdrawn. Quarantine retains ownership and blocks automatic restart.
- Actual scheduler/backend retain T's precall versus called-false distinction,
  fresh local sync, first-fault identity, no replay and ambiguous/loss quarantine.
  Foreign direct mutators reject before execution locks in tested paths.
- Shared service transactions support copied tokens, one admitted chunk and
  deferred abort/retirement. Actual CLI and mode/layout guards execute natively.
  Network/storage/loop paths compile as real target objects but are not falsely
  counted as runtime-tested. Upload/restart fail closed in the enabled candidate.

No grammar, numeric semantics or S/T subset expansion. No target std::thread or
thread-local lease symbols, SDK archive rebuild or installed source change.
LOCAL_SCHEDULER_DONE and LOCAL_CLEARING_SUBMITTED remain local-only, not USB
completion, retirement, host delivery or host release. Strict Route A is still
UNRESOLVED; no support message was sent.

## Final executed results

| Category | PASS | Unexpected FAIL | Assertions |
| --- | ---: | ---: | ---: |
| U01–U64 primary | 64 | 0 | 515 |
| Unchanged Stage28T, once | 47 | 0 | 467 |
| Affected production regressions | 77 | 0 | 67,371 |
| Final default-off comparison, same77 cases | 77 | 0 | 67,371 |
| Existing controlled-startup regression | 30 | 0 | 635 |

Seven preparation controls pass separately. Fourteen Xtensa object/metadata
compilations pass. Native ASan/UBSan/leak checks are clean. Deliberate U/T
negative assertions are separate expected controls, not unexpected failures.
Development/superseded runs are disclosed, not counted again. Historical
XPASS/XFAIL, watchdog and compatibility observations retain their classifications.
No unrelated generic model or owner Mac smoke was rerun.

## Resources and provenance

Native Adapter22,608B (+16 versus T). Target Adapter22,528B includes
Program6,936B, CompileSession2,408B, Runtime4,872B and source8,193B;
do not double count nested members. Target Publication552B and FileSource44B
are separate. Selected static payloads, including backend/route/gate, sum23,374B
before linker alignment or existing legacy/framework state. This is not linked
firmware RAM. Native allocations include all fixtures and platform mocks.
Target coordinator tick frame304B is an individual compiler estimate, not total
stack. No OTA headroom, heap margin or device high-water was measured.

The source manifest binds original inputs, unchanged T composition, exact U
patch and scratch outputs, candidate headers/includes, native executable hashes
and tool versions. Target receipts record source/object/compiler/SDK/core hashes,
commands, real task symbols, response-file hashes, layouts, frames and unresolved
platform references. Successful objects are not final linked-firmware provenance.

## Remaining blockers and next review

Direct settings/media/MSC/core/USB lifecycle callers can still bypass selected
wrappers. Real network transactions, callback/request ownership and task affinity
are not certified by native token tests or object compilation. Upload/restart
are unavailable in this candidate, rather than partially enabled. External-media
snapshot exclusivity, actual filesystem/task waits, final link/resource checks,
frontend selection and full service coverage require separate review.

Existing startup guards are preserved, not replaced with universal quiescence:
the original normal profile's legacy autorun policy is unchanged. RouteB adds
no boot selection/output/arming. Any later linked controlled build must retain
its own startup/recovery/artifact gates; a read-only profile cannot automatically
transition to writable operation. Physical installation remains unauthorized.

Next recommendation: review the concrete task/service contract and resolve the
matrix's direct bypasses and disabled-handler policy before separately authorizing
a controlled link. Do not automatically start Stage28V or hardware tests.

## Integrity and delivery

All1,217 historical paths/bytes/modes and235 frozen Stage26 files are checked
directly against Git. Snapshot45 previous remote refs before/after publication;
only the new U branch may be added. Integrity JSON is explicitly PRECOMMIT,
self-hash excluded; exact final commit/publication verification is external.
Git whitespace checks exclude only the required single-space blank context in
the exact hashed unified patch. No other whitespace/warning expectation changed.

Changed-file inventory: all files under `tests/stage28u/` plus the new
`docs/stage28u-*` documents/receipts; the complete per-file size/SHA inventory is
in integrity JSON. Main, previous branches and baseline artifacts remain intact.
No hardware access, real HID output, owner payload/backup access, flashing,
formatting, boot, OTA, firmware generation or Stage28V work occurred.

### Exact added-file list

- `docs/stage28u-coverage.json`
- `docs/stage28u-dispatch-and-file-lifetime.md`
- `docs/stage28u-integration-review.md`
- `docs/stage28u-integrity.json`
- `docs/stage28u-native-results.json`
- `docs/stage28u-owner-scope.md`
- `docs/stage28u-producer-transaction-matrix.md`
- `docs/stage28u-report.md`
- `docs/stage28u-resource-ledger.md`
- `docs/stage28u-source-and-patch-manifest.json`
- `docs/stage28u-target-object-results.json`
- `docs/stage28u-task-and-service-contract.md`
- `docs/stage28u-test-report.md`
- `tests/stage28u/adapter.cpp`
- `tests/stage28u/adapter.h`
- `tests/stage28u/backend_lease.h`
- `tests/stage28u/backend_lease.inc`
- `tests/stage28u/check_preparation.py`
- `tests/stage28u/coordinator.cpp`
- `tests/stage28u/coordinator.h`
- `tests/stage28u/file_source.cpp`
- `tests/stage28u/file_source.h`
- `tests/stage28u/lower.cpp`
- `tests/stage28u/lower.h`
- `tests/stage28u/mocks/FS.h`
- `tests/stage28u/mocks/USBHID.h`
- `tests/stage28u/msc_platform.cpp`
- `tests/stage28u/portable.patch`
- `tests/stage28u/prepare_sources.py`
- `tests/stage28u/run_regressions.py`
- `tests/stage28u/run_tests.py`
- `tests/stage28u/scheduler_seam.h`
- `tests/stage28u/seam.inc`
- `tests/stage28u/target_check.py`
- `tests/stage28u/task_platform.h`
- `tests/stage28u/test_main.cpp`
- `tests/stage28u/verify_scope.py`
