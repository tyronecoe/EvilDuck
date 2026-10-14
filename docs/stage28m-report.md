# Stage28M report — isolated transport state, K01 and USB provenance

**GO: review the executed memory-only Stage28M transport contract and new K01 barrier. Real transport is NOT READY. NO-GO: production integration, live USB/HID, firmware, flash/boot/OTA or automatic Stage28N.**

Exact parent `9b8c2b0e76ac37c63f86a51f1a573a8466ca5669`, starting clean Stage28L branch. New delivery branch `stage28m-synthetic-transport-state`. Only new Stage28M docs/tests are changed; all1,060 historical tracked paths/bytes/modes and235 frozen Stage26 files remain unchanged. Protected core/SDK/source/archive/compiler inputs and existing controlled ELF are inspected, not modified or rebuilt. Final SHA/remote comparison is reported at delivery rather than embedded self-referentially in the precommit receipt.

## Delivered behavior and actual tests

The isolated derived driver uses unchanged Program/CompileSession/Runtime/Planner/Bridge. It rejects start with admitted or executing setup, pending/uncertain report or invalid lease. Every admitted setup request receives a retained explicit disposition. The historical K01 reproducer **exits1 for the intended missing barrier**, whereas the new same-sequence regression **exits0**; historical K code/tests/outcomes were not edited.

The synthetic service owns one immutable operational transfer, checked C/Q bound to S/E/R,8 ordinary requests and4 observations. It distinguishes definite refusal, submission and ambiguity; current success and independent retirement are both needed for Accepted. Polling does not resubmit pending work. Cancelled source never receives a late ack; resource retirement continues independently. Explicit fresh drain and new-session sync cannot use stale zero receipts. Full queues, journals, ID exhaustion, reentry, tokenless/wrong notices and strict attempt/time ceilings fail safely. No source parser, production adapter, thread, USB symbol override or dependency patch was added.

Fresh primary **36 PASS / 0 FAIL / 9,689 assertions**. All L01–L24 memory cases execute; L20's unapproved exact non-event pre-admission variant remains explicitly BLOCKED/UNSELECTED. Separate unchanged regressions **144 PASS / 0 FAIL / 546,461 assertions**, including K37/10,346. Negative control exits1 as intended; it and the historical defect reproduction are excluded from new PASS/assertion totals. Current ASan/UBSan/leak checks are clean. Healthy C++ new probe observes0 calls, limited to that probe. See test-report and JSON for per-trace variants/bytes/IDs/acks, commands, compiler version, classification and two corrected development fixture-order failures.

Host sizes: Driver182,832 B, of which Transport147,856 B; previous rerun K Driver34,128 B. Difference148,704 B is fixed test evidence/transport bookkeeping. Program6936/CompileSession2416/Bridge5056 B are already owned inside Driver, not added again. No target layout, static production RAM, firmware binary/OTA headroom, task-stack high-water, heap, USB latency or hardware memory measurement occurred. Stage28L's proposed1536 B production budget remains an estimate, not this driver's measurement.

## USB investigation outcome

Authenticated cached package ZIP and archive member match official release digest. Publisher's versions.txt identifies builder afa5cdd0d41d7e465d2e39867b24aef48b1c7b84 and TinyUSB8a78804ff91271fb32008288777fad9fe73f5735. Five installed headers match retrieved revision bytes. Builder CMake selects its own patched DCD, not upstream DCD. The source and existing compiled DCD show spin-locked submission and suspend→UNPLUGGED mapping; TinyUSB claim uses infinite mutex wait. Completion event/class/core paths still lack C/Q and explicit retirement/observer fences.

Package/member provenance and publisher-recorded revisions are established, but clean complete C source-to-object provenance is not proven merely by recorded HEAD, matched headers or similar disassembly. No SDK rebuild or patch was performed. Missing exact build working-tree attestation, bounded sender proof, authentic correlation, retirement/quiescence, exclusivity/concurrency and host behavior are separately retained blockers. Mock tags/fences cannot clear them. See usb-provenance/source-evidence for exact URLs, hashes, line spans and compile-static limits.

## File inventory

New tests:

- tests/stage28m/synthetic_transport.h
- tests/stage28m/synthetic_transport.cpp
- tests/stage28m/journal_driver.h
- tests/stage28m/journal_driver.cpp
- tests/stage28m/k01_reproducer.cpp
- tests/stage28m/test_transport.cpp
- tests/stage28m/allocation_probe.cpp
- tests/stage28m/run_tests.py
- tests/stage28m/verify_scope.py

New documentation/receipts:

- docs/stage28m-owner-scope.md
- docs/stage28m-contract-implementation.md
- docs/stage28m-k01-regression.md
- docs/stage28m-test-report.md
- docs/stage28m-test-results.json
- docs/stage28m-usb-provenance.md
- docs/stage28m-source-evidence.json
- docs/stage28m-limitations-and-next-gates.md
- docs/stage28m-report.md
- docs/stage28m-integrity.json

The integrity receipt records new-file hashes excluding itself, immutable-file verification and precommit remote refs. Publication must preserve37 prior refs and add only the new branch; final SHA/post-push proof supplied separately. No old source/docs/tests, approval cells, Arduino Micro, USB identities/descriptors, toolchains, partitions, settings or firmware profiles changed. No private backups/credentials/owner payloads read, modified or committed. Stock availability remains owner-confirmed external. Existing development tools required no setup installation/configuration changes.

No physical test, device access, boot, erase, filesystem formatting, flashing, OTA, real HID/OS key output or owner script execution occurred. No firmware images or target objects generated. Next proposed milestone is a separately reviewed exact-stack source/lifecycle component investigation and token/retirement contract; not automatic Stage28N or a production adapter.
