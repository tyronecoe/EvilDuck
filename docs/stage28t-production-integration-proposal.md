# Stage28T default-off production integration proposal — NOT APPLIED

`tests/stage28t/production-review-only.patch` is the combined four-file delta
against exact parent `EvilDuckS3/com.cpp`, `com.h`, `hid_backend.cpp`,
`hid_backend.h`. A preparation control applies it to fresh original scratch
files and verifies byte-identical outputs to the tested S-then-T patch chain.
All original tracked firmware remains unchanged. The patch references new
Stage28T seam/lease headers/includes through the native test include path.

It is a concrete native prototype, not a deployable target patch. It uses
`std::thread::id` and thread-local permission under host Guard; do not enable
its two selectors in a firmware build. The paired selectors are explicit and
default-off: `EVILDUCK_NATIVE_SCHEDULER_ROUTE_B` and
`EVILDUCK_NATIVE_REAL_BACKEND_B`. Tested configuration enables both or neither;
S-only support remains in unchanged Stage28S, not this composed candidate.

Before a separate production integration proposal is authorized:

1. Review the outcome contract and accept conservative permanent quarantine on
   ambiguous lower returns. Retain local-only acknowledgement terminology.
2. Specify actual task owner/token lifetime and reentrancy without assuming a
   recursive mutex, public IDs or com busy exclude all producers. Inventory real
   callbacks, core submissions, mode changes, settings, file/OTA and USB lifecycle.
3. Add an explicit opt-in dispatch/file Reader adapter, bounded read/seek error
   handling and diagnostics. Preserve the legacy engine default and startup
   profiles. Native source capture is capped8,192, not an unbounded file loader.
4. Specify stop/running/UI state and callback ownership for native sessions.
   A legacy duckscript stop callback cannot be presumed to cancel the Adapter.
5. Perform separately authorized target ABI/compile/resource checks and check
   transport readiness/instance/ID/protocol. No such build was performed here.
6. Only after independent deployment review, owner authorization and recovery/
   first-boot gates, consider supervised harmless physical tests. Nothing in
   these Linux traces proves host layout, delivery, neutral release or retirement.

The proposal must retain preview checked numeric semantics and S's whitelist;
no modifiers/HOLD/INJECT_MOD/RESET or device commands are silently added. Strict A
can remain separately unresolved; no vendor response is required for this local
native result. Do not add another generic endpoint model to finish Route B.

Rollback/review now means discard only external scratch trees or leave the two
selectors disabled in those trees. There is no installed dependency/firmware
change to reverse. Preserve historical S/T receipts and the default-off comparison.
No automatic arming, retry after quarantine or transition to hardware exists.
