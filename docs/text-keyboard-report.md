# Route B text and keyboard utilities — implementation report

Baseline `d30ec43aab0fe535afb3cbc79f80bcd2837c3129`; branch `routeb-text-keyboard-utilities-v1`; candidate `ROUTEB-TEXT-KEYBOARD-v1`. The accepted baseline's four scoped High Sierra owner passes are recorded in [owner evidence](text-keyboard-owner-evidence.md). No hardware testing is performed by this work.

## Focused change

Fourteen embedded-language text aliases reuse the existing bounded block engine. Inline `REPEAT` with a decimal count of 2–128 lowers permitted leaf statements into bounded instructions sharing operand storage; each compiler step copies at most one additional instruction. The existing total 128-instruction limit still applies. `RESET` requests an owner-scoped neutral clear and continues without cancelling the session. [Exact grammar and limits](text-keyboard-design.md), [compatibility inventory](text-keyboard-compatibility.md), [short acceptance sheet](text-keyboard-acceptance.md).

No host-language execution, new layout, USB identity/descriptor/partition change, settings reset or EDR1 modification is added. Existing expressions/functions, randomization/jitter, preprocessing, HOLD/RELEASE, inline INJECT_MOD, STOP and lease/quarantine safeguards remain intact in the focused regressions. INJECT_VAR stays blocked; its completed research and unresolved contract fields are preserved.

## Fresh software verification

The final composed native run passed **371 cases, 14,907 assertions, zero failures**. The 40 new cases contribute 1,853 assertions; the 331 selected existing cases contribute 13,054 assertions. ASan, UBSan and leak detection completed without reported errors. Existing allocation probes also pass; this is not a measurement of device heap or runtime latency.

The new cases cover all fourteen aliases and delimiters; literal command-looking text; indentation/newlines/DEFINE; malformed retained source versus preprocessing exclusions; REPEAT count/IR limits and cancellation during cooperative expansion; fresh random selections between repetitions with cached transport retries; RESET exact neutral reports, counter/operation association and continued execution; competing/wrong-session/reentrant clear attempts; STOP, backpressure, disconnect, quarantine and subsequent-run isolation. RESET bypasses jitter and preserves runtime settings. The test driver predates the executed native binary (source 00:29:26 UTC; executable 00:30:26 UTC on the recorded build date), consistent with the final driver being compiled in this run; source identities remain the stronger provenance evidence.

[Exact native results and command](text-keyboard-test-results.json) records per-case output, sanitizer configuration and intentional selector rejection controls. Historical refusal fixtures are not edited. The inherited generated-copy adaptations for R27/U27 remove only character commands added in earlier approved releases; seed rejection and the separate historical dispositions remain. The inherited `selected_unchanged_regressions` label includes those documented candidate adaptations and is not a claim that obsolete capability refusals still pass.

RESET's barrier establishes a fresh owner-scoped neutral **submission** under the existing transport contract. It does not establish host receipt, global key release or a new USB retirement guarantee. The script cannot continue based on a stale clear counter, and ambiguously accepted transport calls remain quarantined rather than replayed.

The separately bound package passed **43 package checks and 38 mock-installer checks**, zero failures. [Package checks](text-keyboard-package-tests.json), [mock installer checks](text-keyboard-installer-tests.json). These exercise disposable public copies and synthetic chip/layout/security/tool responses; no serial endpoint is opened. No publication success is inferred from these checks. Native Linux verification does not establish High Sierra USB behavior or physical acceptance.

## Clean isolated build and resources

The clean firmware build and final linked verification passed using the existing approved Arduino ESP32 core 3.3.0 archive profile: ESP32-S3, 16 MiB custom partitions, PSRAM disabled, USB-OTG/TinyUSB, CDC-on-boot, 240 MHz and existing CPU/flash settings. All 177 SDK archive identities, startup/HID/NVS/ownership checks, selected source/compile flags and ELF-to-BIN regeneration remain guarded. No global core/SDK modification or replacement archive occurred.

| Measurement | Accepted randomization/jitter | Candidate | Delta |
|---|---:|---:|---:|
| Compiler program bytes | 1,410,939 | 1,412,247 | +1,308 |
| Application BIN bytes | 1,411,088 | 1,412,400 | +1,312 |
| Static RAM bytes | 113,880 | 113,888 | +8 |
| Free OTA bytes per slot | 6,191,088 | 6,189,776 | -1,312 |

Each OTA slot remains 7,602,176 bytes; free capacity is **81.421109%**. Application SHA-256: `53acc374ef38be652b6847d4b84f2dc7d42fa73a3dd54ea62d5208be4cbc0167`. ELF SHA-256: `3eb651b2c9ecea3218f0de60b4816198a7407499c75f128470c1696737040a81`. Expected partition-table SHA-256 remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

The 8-byte static RAM increase corresponds to fixed RESET owner bookkeeping; no unbounded state or new runtime queue is introduced. Native `Runtime`, `Program` and `CompileSession` object sizes remain 4,944, 6,936 and 4,144 bytes. Compiler workspace remains fixed at 4,096 bytes. Target compiler frame estimates are unchanged for `Compiler::line` (240 B), `Compiler::step` (144 B), `CompileSession::step` (32 B), `Runtime::sample` (64 B), `Runtime::deliver` (48 B), `Runtime::tick` (112 B), `Runtime::evaluationStep` (144 B), adapter step (144 B), coordinator tick (384 B), setup (80 B) and loop (32 B). The new `route_b::reset` frame is 192 B, and `com::update` grows from 80 B to 176 B (+96 B) because the continuing clear path checks owner/counter state. That increase requires future physical stack-water observation; it is not evidence of stack overflow or measured physical headroom. The synchronous compiler's 4,224-byte object-file frame is not a linked production path.

[Resource receipt](text-keyboard-resources.json) records the frame and size comparison. [Preservation receipt](text-keyboard-preservation.json) records all 2,022 baseline files/modes unchanged. [Linked build receipt](text-keyboard-build.json) contains actual source/artifact inventories, command settings, archive identities and disassembly. Final linked checks include compiler/preprocessing call edges, the existing sampler/jitter path, and RESET edges from the adapter through owner admission and clear service. These compiler frame estimates are not cumulative task-stack high-water or hardware heap measurements.

## Delivery and readiness

One Mac application-only review ZIP must bind exact rollback to the accepted **1,411,088-byte** application, SHA-256 `2e1d8345417c6f23a5df3d884db42dd2a0f9f305120ee494c56a58048e677496`. Preserve High Sierra 10.13.6, Bash 3.2, Python 3.8 and esptool 4.12 interfaces and explicit owner confirmation. Public ZIP: **2,336,378 bytes**, SHA-256 `9a60e91e142fea74b746bef352d16139cccaf9fd45ca5e5a10549c91b846dc9e`. [Artifact inventory](text-keyboard-artifact.json). All 24 members, CRC, support bindings and both application images are verified; deterministic re-archiving produces identical bytes. The bundled report is the source-commit pre-publication snapshot. Publication/download verification follows separately without regenerating the frozen archive. No LED helper or second installation package is needed.

GO: software review and package preparation after required checks. NO-GO: installation, physical testing, flashing, OTA or automatic script execution without separate owner approval. No broad Caps diagnostic campaign or new INJECT_VAR investigation is required. Keep historical firmware/packages, working rollback, owner backups and previous remote refs untouched.

## Source and review inventory

Only new `tests/text_keyboard/*`, `docs/text-keyboard-*` and the new public ZIP are added. The composition patch changes seven generated application sources: compiler/runtime `core.cpp`/`core.h`, `adapter.cpp`, scheduler `seam.inc`/`scheduler_seam.h`/`com.cpp`, and `caps_trial.h` for build identity. Historical sources are unchanged. The complete 201-file candidate inventory and all before/after hashes are in the build receipt and source manifest. An independent read-only review rehashed all 201 source files and five build artifacts and found no release-blocking defect.

One initial packaging invocation used a mistyped full source commit and was rejected by Git ancestry validation before creating an output. The corrected invocation binds actual source `3780a4884bfd5eab9394b2fa5626298f62712349`; this operator error is outside test counts and did not require a firmware change. No unexpected native/package/installer failures occurred.

## Publication result

The [commit-pinned Mac ZIP](https://raw.githubusercontent.com/tyronecoe/EvilDuck/3040eec3c925c4fda74ff3fa26a8f87ad47dee5c/downloads/evilduck-routeb-text-keyboard-macos-v1.zip) was downloaded and matched **2,336,378 bytes** and SHA-256 `9a60e91e142fea74b746bef352d16139cccaf9fd45ca5e5a10549c91b846dc9e`, the repository blob, ZIP CRC and both application identities. [Publication receipt](text-keyboard-publication.json) records all **73 previous remote refs unchanged** and only the isolated branch added. Exact changed files/modes/hashes are in the [new-file inventory](text-keyboard-file-inventory.json). The final working tree and branch tip are checked after the receipt commit.

**GO:** review this software-tested candidate and its short acceptance sheet. **NO-GO:** installation or physical acceptance without separate owner approval. New aliases, RESET and inline REPEAT remain physically unverified. No hardware access, real HID output, stored-owner-script execution, flashing, OTA, formatting or settings reset occurred. INJECT_VAR remains blocked; no new firmware stage is started automatically.
