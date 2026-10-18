# Reviewed caps/queue candidate

Source/build profile revision: ace54c7 (full commit in manifest). Selected runtime
composition is unchanged from d32a60bd3fef73e38293f95905f5905eb41b32fd, materialized
through tests/caps_queue. This is the additive publisher-archive build approved
after f47e46d, not the unavailable historical core-tree reproduction.

Changes already present in this composition: compact STOP/details, correlated
execution request receipts, authenticated stored SD/library deletion through POST,
exact 17-byte RAM-only LED download validation and endpoint routing, feedback
callback diagnostics, and failed-save/stale-run protection. Existing HTTP bounded
locking, single-owner Route B execution and cancellation remain verified by native
production-source mocks. No new interpreter behavior is introduced by packaging.

Clean full target compile and final link closure passed. Program1,381,631 bytes;
BIN1,381,776 bytes; staticRAM107,488 bytes. Each0x740000 OTA slot retains6,220,400
bytes (81.8239409%). Compared with the c20 build: program+5,208; BIN+5,200;
staticRAM+8 bytes. The8KiB loop-task allocation remains selected in linked code;
compiler frame estimates are not runtime stack high-water or additive call depth.
The largest recorded frame is Program::compile2496 bytes; diagnostics handler1888,
CLI parse1728. No physical heap/task-stack measurements were performed.

Application SHA-256:
573a86715f41f9d5e6628a8ff9117c176f178c8c014c5986d1f8e9bca01fc1bf
ELF SHA-256:
bcc8b0ce6fe2d5f6f46ebb709aa2115f312e107d2670d887475b2099af241b12

Final ELF checks confirm one strong HID SET_REPORT callback, corrected OUTPUT
routing, no legacy FEATURE-as-LED workaround, protected Arduino NVS error hook,
no Arduino automatic NVS erase in initArduino, controlled startup settings/storage
checks before application HID, no startup examples/autorun, Route B diagnostics,
5-tick bounded HTTP wait, correct loop/update ordering, and exact ELF-to-image
regeneration. All177 consumed SDK archive identities remain unchanged. Upstream
SDK recovery can still mutate NVS during normal writable operation; app-only
installation preserves flash regions but does not promise runtime NVS immutability.

Caps Lock and LED feedback are **physically unverified**. A0x39 tap and simulated
reports do not prove host acceptance. ID0 unprefixed feedback routing remains a
known limitation; no guessed keyboard-ID normalization is added. HOLD/RELEASE
are unsupported in this Route B capability gate. Local cleanup submission does
not prove host key release. Native High Sierra serial execution of these new
helpers remains owner-local. No hardware, real HID, flashing or OTA occurred.

Rollback is the exact c20dc399 current working application, not the previous
package's older shortcut rollback. Follow the two Mac guides, with separate
owner review before any write or boot.
