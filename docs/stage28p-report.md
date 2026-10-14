# Stage28P actual builder controller execution and retirement feasibility

**GO: review executed controller-path evidence and the source-backed change/retirement design. NO-GO: real integration, installed dependency changes, target/SDK/firmware builds/images, live USB/HID, physical access/flash/boot/OTA or automatic Stage28Q. Strict success-plus-retirement remains NOT SATISFIED.**

Exact clean parentd57e9d1a2b7280f0b5f415d93ae9e7d23db54871; branchstage28p-builder-dcd-lifecycle. All1,118 historical files/paths/executable modes and235 frozen Stage26 files remain unchanged;40 prior remote refs must remain unchanged at publication. Only new P tests/docs/receipts are delivered. Committed integrity receipt is explicitly precommit/self-hash-excluded; final SHA/publication proof is provided separately.

## Practical result

The actual builder-selected dcd_dwc2.c executes natively with its complete source body byte-identical. Scheduling, FIFO progression, interrupt dispatch, reset, suspend, close/stall and event emission are genuine vendor functions, not Stage28O's fake DCD. Pinned common.c byte-packing executes with a two-file platform/I/O adaptation. Actual TinyUSB stack queue/task/class receives its genuine DCD helper events. Read-only probes do not redefine static or mutate driver state.

**33 primary observation PASS /0 unexpected FAIL /167 assertions.** These are software observations under explicit register/OS assumptions, not strict controller-contract passes. Three expected watchdog observations are separate, with no finished assertion/leak/coverage claim. A deliberately failing P negative control exits1 as intended. Completed P cases are ASan/UBSan/detect_leaks=1 clean.

Unchanged Stage28O runner executed once separately:46 PASS/931 assertions; freshly supplied unchanged N baseline20 observation PASS/131; O disabled compatibility20 observation PASS/131. Its two old-contract reproductions and O/N negative controls retain original classification. No repeated run/prior historical total is added as new assertions. No full old-suite or owner Mac rerun.

## Findings that move the controller review forward

- Actual retained buffer cursor/max packet/length and9-byte ID framing are observed.137-byte direct DCD transfer progresses64/64/9 under explicitly scripted FIFO consumption. Real tusb_fifo pointer transfer also executes, with its unmodeled TSIZ semantics explicitly distinguished.
- Closed endpoint refuses before replacing metadata. Direct DCD submission has no busy guard: an outstanding pointer/length can be overwritten. A completion IRQ then reads the current descriptor; duplicate/old notice cannot authenticate the original action.
- Actual completion can occur before dcd_edpt_xfer returns via a controlled spin-unlock interleaving and genuine IRQ/queue/class dispatch. Observer reentry changes the class's borrowed buffer/descriptor.
- Reset clears descriptor software state; close-all leaves retained pointer/length while zeroing max packet. Suspend emits **UNPLUGGED**, matching the builder's custom behavior. Weakfalse DCD deinit is ignored by stack teardown; forced late handler reaches deleted queue via fake null guard, not real robustness.
- Injected inconsistent transfer-size status does not change the emitted stored length. Injected timeout/AHB-error bits create no failure completion in the tested slave handler; retained ownership is unresolved.
- Queue fifth-event refusal is recorded; controller's void helper/handler receives no admission outcome. There is no retirement/event-publisher certificate. Unresolved IN NAK, FIFO flush and original common-core reset waits hit the external watchdog.

These are deliberately injected snapshots/interleavings, not proof physical hardware ordinarily generates invalid, duplicate, stale or impossible status combinations. Post-close/reset paths depend on old status being deliberately retained despite masks/flush; actual silicon clearing/propagation remains unverified. Long direct DCD cases bypass HID copying and may yield a class callback buffer unrelated to the raw transfer; fake observer bounds are not vendor validation.

## Prototype gate and remaining blockers

**No semantic tagged controller prototype is implemented.** Native execution establishes why copying C/Q into the current mutable descriptor and reading it in the ISR would be unsafe. Genuine originating identity requires forbidding descriptor reuse until a reviewed controller/IRQ-publication fence establishes no older work can reach it. This stage does not establish that condition. Implementing a current-slot retag or inventing a ready-bit certificate would violate the assignment, so identity/retirement integration is explicitly deferred.

The implementation-ready path map specifies fixed original records, finite try ownership, publish-before-enable, ISR/task synchronization, explicit queue-loss feedback, per-endpoint checked retirement, observer quiescence, cancellation/fresh-neutral and no automatic resume. Exact unknowns: W1C/status/FIFO-pop/posted effects, actual disable/flush/IRQ conditions, FreeRTOS critical and inter-core ordering/affinity, full producer exclusivity, core/CDC/MSC integration, coordinated target ABI/source-object verification and physical behavior. OUT data/RXFLVL, DMA and isochronous hardware are unexecuted. Stage28O's fake-tagged acceptance remains separately useful but is not promoted to a real-controller guarantee.

## Provenance and resources

Builderafa5cdd0d41d7e465d2e39867b24aef48b1c7b84, TinyUSB8a78804ff91271fb32008288777fad9fe73f5735, IDFb66b5448e0dfac6be135e6f0ac21010aba231180, Arduino3.3.0/SDKidf-release_v5.5-b66b5448-v1. Selected file SHA d12ef24b093d542a5e42d7cdf10d4170b1d139c5eb061db26df3b26cb1eee81a. Four new DWC2 files and one FreeRTOS source-only header are retrieved at official full revisions; selected builder recipe/config and prior archive evidence rehashed. Exact21 original stack files, input/output patch hashes, fixtures/compiler/commands/coverage are recorded. Protected installed core/SDK/package identity is checked, never patched. Package abbreviations and publisher full pins are not a complete shipped-source-to-object attestation.

Native sizeof descriptor array336B, driver control8B. These are host measurements of unchanged driver structures, not target static RAM, physical heap/latency/task-stack or firmware/OTA measurements. All fixture registers/journals are fixed process-owned storage. No new production allocation or memory claim is made.

## New file inventory

Tests/stage28p/: boundary.c, boundary.h, tusb_config.h, tusb_os_custom.h, stage28p_platform.h, platform.c, driver_unit.c, test_controller.c, native-io-adaptation.patch, prepare_sources.py, run_tests.py, verify_scope.py.

Docs/: stage28p-owner-scope.md, stage28p-source-and-boundary-manifest.json, stage28p-controller-ownership.md, stage28p-retirement-design.md, stage28p-controller-change-plan.md, stage28p-test-report.md, stage28p-test-results.json, stage28p-report.md, stage28p-integrity.json.

No production/preview/Arduino Micro/historical files, pins/profiles/approval cells, partitions/USB identities, installed source/SDK/global tools, owner backups/credentials/payloads changed. No physical or real HID activity, firmware generation or Stage28Q. Recommended next narrow proposal is an official-source-backed endpoint disable/flush/interrupt model and producer-fence contract; authorize core/FreeRTOS, target ABI and physical tests separately rather than automatic expansion.
