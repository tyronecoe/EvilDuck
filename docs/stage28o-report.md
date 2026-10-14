# Stage28O isolated native tagged-transfer prototype

**GO: review executed isolated native software predicates and the original/prototype comparison. NO-GO: installed dependency changes, production integration, target/SDK/firmware builds/images, live USB/HID, hardware boot/flash/OTA or automatic Stage28P.**

Exact clean parent300c8dc649efce448d931d0b7bbfdba2a46d4e97; new branchstage28o-native-tagged-transfer-prototype. No previous tracked file/path/mode changes. All1,096 historical files and235 frozen Stage26 files are checked independently;39 previous remote refs must remain unchanged and only this new branch may be published. The integrity JSON is a precommit receipt excluding its own hash. Final commit/publication proof is supplied separately.

## Result

A deterministic opt-in patch augments actual publisher-pinned TinyUSB usbd.c, hid_device.c and dcd.h, plus a narrow native API header. Genuine submission ownership, actual copied event queue/task dispatch, HID class and observer execute through fake controller/CUSTOM OS seams. No handwritten substitute dispatcher/class, competing production core hook or modified installed dependency is used.

**46 primary PASS, 0 unexpected FAIL,931 assertions.** Unchanged Stage28N baseline:20 observation PASS/131 assertions. Disabled opt-in compatibility:20 observation PASS/131 assertions; every original functional receipt matches. These three executions total1,193 assertions, explicitly separated rather than presented as new language compatibility. Two focused original-contract reproductions each exit1 as intended; the O negative control and inherited N baseline negative control each exit1 separately. ASan/UBSan/detect_leaks=1 are clean. Three preparation utility checks are separate static checks, not C assertions. Per-case functions/lines, event C/Q/queue transitions, frames, callback timing, outcomes/certificates and commands are in test-results/report.

Closed under fake assumptions: Q/C created before ownership and carried through real completion dispatch; stale validation before busy/claim/map/buffer access; checked nonwaiting claim and shape validation; no oversize claim leak; no pending resubmission; actual shared-boundary lease; stable observer data; first-fault/loss handling; cancellation eligibility; explicit transfer retirement plus observer quiescence; checked64-bit exhaustion. Early completion works; contradictory refusal, failed unlock and attempted early reclamation quarantine instead of silently retrying. Reset/unplug/protocol/reconnect cannot restore eligibility automatically. Fresh zero drain/sync uses a new lifetime/ticket after explicit old-resource retirement.

The real builder DCD/core still lack those native seam contracts. Native certificates are fake, not controller proof. No actual Runtime/Planner/Bridge was integrated or acknowledged, and host key release is not claimed.

## Provenance and resources

Pinned TinyUSB8a78804ff91271fb32008288777fad9fe73f5735; builderafa5cdd0d41d7e465d2e39867b24aef48b1c7b84; IDFb66b5448e0dfac6be135e6f0ac21010aba231180; controlled Arduino3.3.0/SDKidf-release_v5.5-b66b5448-v1. All21 original inputs were freshly prepared and hashed. Original/prototype copies remain external; exact four-file outputs and patch SHA are recorded. Five cached selected builder source/config records are independently rehashed, static only. Protected core/SDK and cached package/member identities are checked without modifying them.

Package versions.txt records **abbreviated** builder/TinyUSB/IDF revisions; the full pinned revisions and official full-revision native source hashes are separately recorded. This is not a full shipped-source-to-object attestation. The actual selected builder DCD is not patched or executed.

Native measured event24→40B, coordinator96B including transfer48B, immutable frame9B; transient observer snapshot48B. Custom queue4×64B slots remains fixed. Diagnostic journals are fixed-size fixture evidence, not production memory. No firmware/OTA, target ABI, physical heap/latency/task-stack or real USB measurements occur.

## Findings, limitations and verification corrections

Duplicate/stale/bad-length events are deliberate fault injection, not claims that physical hardware normally emits them. Single pending observation plus duplicate filtering blocks reuse while unconsumed; legal single-slot execution cannot overflow that observation slot. Its defensive overflow branch is not claimed reached by real dispatch. The four-event queue overflow is executed and sticky-faulted. Concurrency is serialized fake execution with specified reentry, not a real RTOS race test.

Real controller identity/fence/retirement, FreeRTOS boundedness, complete producer inventory, full Arduino observer/hook and CDC/MSC integration, negotiated board binding, target coordinated ABI/source-object verification and physical behavior remain separate blockers. N21/N22 stay BLOCKED/source-static. Direct DCD and unreviewed lifecycle paths are not covered by the lease. Original tud_task_ext is not turned into a bounded production scheduler. No Linux/Mac result is promoted to device evidence.

Development verification corrected two receipt checks: O34 intentionally enters two legacy pre-lease WAIT_FOREVER calls; all opt-in claim attempts still use0. Package revision verification originally expected full40-character strings in versions.txt; it now verifies the actual publisher abbreviations against full pins and authenticated hashes. No vendor test expectations/flags were weakened, no compile error downgraded, and intermediate/repeated runs are not added to final totals. Additional unlock, admission reentry and in-flight reclamation tests were added after source review and all final cases were rerun.

## File inventory and delivery boundary

New tests/stage28o/: boundary.c, boundary.h, tusb_config.h, tusb_os_custom.h, tagged.h, usbd_extension.inc, tinyusb-native.patch, prepare_sources.py, run_tests.py, test_components.c, old_contract_reproducer.c, test_preparation.py, verify_scope.py.

New docs/: stage28o-owner-scope.md, stage28o-input-and-patch-manifest.json, stage28o-prototype-contract.md, stage28o-baseline-comparison.md, stage28o-test-report.md, stage28o-test-results.json, stage28o-remaining-controller-core-work.md, stage28o-report.md, stage28o-integrity.json.

No language_preview, firmware, Arduino Micro, profiles, approval cells, installed dependencies/toolchains, partitions, USB identities/descriptors, owner files, backups or credentials changed. No real HID/OS injection, hardware access, flash/erase/format/boot/OTA, target/firmware artifacts or Stage28P. Recommended next narrow proposal: review actual builder DCD identity/retirement seam feasibility and synchronization/producer requirements, under separate authorization.
