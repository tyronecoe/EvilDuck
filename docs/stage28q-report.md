# Stage28Q retirement, register semantics and producer-fence decision

**GO: review the ledger, conditional native sequencer/model and fence contract. Safe real descriptor reuse remains UNRESOLVED. NO-GO: production/installed dependency changes, target/SDK/firmware builds/images, live USB/HID, board/boot/flash/OTA or automatic Stage28R.**

Exact clean parentf1ca7ffdfc5499a1ffd7dff4b126b0024e022c25; new branchstage28q-endpoint-retirement-fence. All1,139 parent-tracked files/paths/executable modes,235 frozen Stage26 files and41 previous remote refs must remain unchanged. Integrity receipt is precommit/self-hash-excluded; final publication proof supplied separately.

## Answer to the owner question

A complete documented safe descriptor-reuse sequence is **not established from the available public material**. Official ESP32-S3 TRMv1.8 §32.5 printed/file1242 says comprehensive USB-OTG register specifications are NDA restricted. Public FIFO/interrupt hierarchy and source behavior are established, but exact disable/flush/no-late-old-IRQ, simultaneous status/ack ordering, posted/inter-core visibility and endpoint-scoped producer/observer guarantees are missing. Reading a new C/Q from a reusable current descriptor would still be unsafe; P's deferral is preserved.

The implemented native candidate is finite and conditional. It follows the pinned driver's SNAK→INEPNE→EPDIS→EPDISD→flush intent, surrounded by explicit admission, publisher and observer gates. Each step performs at most one modeled operation;32-step/100-caller-unit ceilings fail closed. Independent raw/mask/CPU/ISR state, W1C hypotheses, delayed handshakes/FIFO effects, sticky queue loss and in-progress work can falsify reuse. Missing any of8 required certificate premises produces Unresolved/Quarantined, with no request writes in the public profile. Nothing auto-cooperates or auto-arms.

Original immutable record/ticket survives until the complete gate. Already copied old events retain their originating model ticket and cannot select a new record. This publisher API is hypothetical; real raw IRQs do not provide that identity. A forced post-gate old CPU/origin injection violates the synthetic no-late-source premise and invalidates the gate; it is not evidence that a shipping driver could detect it. Real C/Q preservation therefore remains blocked until a no-reassignment fence is independently established.

## Executed verification

**37 new native model PASS /0 unexpected final FAIL /419 assertions**, completed ASan/UBSan/leak-clean; deliberate negative control exits1 separately. Unchanged P executed once:33 observation PASS/167 assertions, with3 expected watchdog observations and its negative control separate. O/baseline/disabled totals are preserved historical classifications, not re-executed or added. No Mac rerun.

A real development finding was preserved and corrected: initial source acceptance conflated retirement with success. Pre-fix scratch reproducer exits1; same corrected reproducer exits0. Final acceptance requires a current full correlated successful model receipt, all retirement/quiescence predicates and uncancelled eligibility. Failed/partial/no receipt cannot accept. Another fixture correction made Q20's forced old CPU interrupt explicit rather than trying to enter from masked raw status alone. No historical expectations or hardware semantics were weakened.

New Q model does **not** execute the vendor driver against its semantic registers. P's direct volatile field implementation cannot reproduce W1C, CPU pending or posted behavior without a reviewed wider accessor adaptation and missing hardware semantics. That coupling is explicitly BLOCKED, not replaced by P's fake/plain fields and claimed faithful. Unchanged P's actual original driver body executes separately under its existing declared limitations.

## Evidence and remaining narrow gate

Official TRM and applicable erratav1.3 PDFs plus exact pinned IDF controller-layout, interrupt and Xtensa port sources are recorded with URLs/version/page/line/SHA. Errata USBOTG-4289 concerns ROM download availability, not endpoint retirement. Host-channel flush helpers are not copied into a device prescription. Device FIFO-number selection versus epnum flush is an explicit unresolved mapping issue, not a newly proven bug. Package/builder/TinyUSB/IDF pins and protected core/SDK remain unchanged; no large SDK was fetched and complete shipped source-to-object equivalence is not asserted.

Next narrow step: owner/reviewer obtains authoritative applicable device disable/flush/W1C/late-interrupt conditions through Espressif's documented support route, especially correct endpoint-to-FIFO flush mapping, then reviews a finite allocated-core publisher fence. No support message was sent. No target build, real DCD patch, adapter or hardware test is started automatically. Absent those guarantees, keep the public reuse gate closed and retain bounded quarantine.

Native object sizes are recorded per executed receipt, not target ABI/static RAM, device heap, task-stack high-water or latency. Fixed event4, trace64 and record/frame storage are test/component bounds; no unbounded allocation or dynamic AST/report queue is introduced. Runtime/Planner limits, preview APIs/subset, K01 barrier and conservative E capacity remain byte-identical.

## Added-file inventory

Tests/stage28q/: model.h, model.cpp, test_model.cpp, receipt_reproducer.cpp, run_tests.py, verify_scope.py, retrieve_references.py.

Docs/: stage28q-owner-scope.md, stage28q-premise-ledger.md, stage28q-source-and-model-manifest.json, stage28q-retirement-sequence.md, stage28q-producer-fence.md, stage28q-test-report.md, stage28q-test-results.json, stage28q-report.md, stage28q-integrity.json.

No historical, production, Arduino Micro, installed core/SDK/global tool, partition/profile/approval cell, USB identity/descriptor, private backup/credential/owner payload changes. No real MMIO/device/USB/HID/enumeration, firmware generation, physical boot/flash/erase/format/OTA or Stage28R. Original recovery availability remains owner-confirmed externally; exact old-data preservation is not reinstated.
