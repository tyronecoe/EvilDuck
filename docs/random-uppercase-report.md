# Route B random uppercase — implementation report

Baseline: `485d1a31c7d1ef868aef99c92c15ebd9b75994b5`. Isolated branch: `routeb-random-uppercase-v1`. Candidate: `ROUTEB-RANDOM-UPPER-20261025-v1`. The accepted installed lowercase application, owner-operated trials and available identifiers are recorded in `random-uppercase-owner-evidence.md`. They are not independent hardware tests performed by Codex.

## Focused change

The official Hak5 randomization table specifies `RANDOM_UPPERCASE_LETTER` and `ABCDEFGHIJKLMNOPQRSTUVWXYZ`. This candidate adds that exact argument-free command through a separately pinned composition layer on the actual lowercase Route B modules. It reuses the existing bounded random reader, ordinary Character event, uppercase translation, persistent-state merging and cleanup. It does not change legacy/main or uncomposed preview behavior as a substitute for this composed support.

At most one raw draw occurs per runtime tick, with eight attempts maximum. The existing uint32 rejection band remains the top 22 values. The selected A–Z character is cached through sink/transport retries. Existing lowercase output, single-owner execution, collision/rollover refusal, STOP/error cleanup, disconnect handling and ambiguity/quarantine remain required invariants. No Caps normalization, layout, seed/numeric RNG, jitter, USB identity, partition, settings or EDR1 change is introduced. INJECT_VAR stays explicitly unsupported; its research and unresolved vectors remain unchanged.

See `random-uppercase-design.md` and `random-uppercase-compatibility.md` for the bounded grammar and limits. The historical lowercase R27 test remains unchanged; the new composed suite must explicitly account for its obsolete uppercase-rejection expectation rather than silently weaken historical results.

## Verification receipts

The fresh composed native run passed **285 cases, 10,853 assertions, zero final failures**: 34 uppercase cases / 1,277 assertions and 251 baseline-regression cases / 9,576 assertions. ASan, UBSan and leak detection completed without reported errors. U24 verifies no C++ heap allocation during selection and cached sink retries; U30 exercises 100 randomized loop operations. This is synthetic native evidence, not hardware entropy, heap or USB delivery measurement.

[Exact test receipt](random-uppercase-test-results.json) records commands, per-case output, selector rejection controls and historical classifications. The generated copy of R27 removes only uppercase from its unsupported-command list; the historical file is unchanged and all other unsupported random-group checks remain. The receipt's inherited `selected_unchanged_regressions` category contains that explicitly documented R27 adaptation; it is not a claim that the obsolete uppercase refusal still passes.

Earlier development observations remain recorded: the first runner stopped on an escaped-string setup assertion before tests; the next run passed all 34 uppercase cases but D12 expected the old lowercase build-ID prefix (284 PASS / 1 harness-expectation FAIL). The final run corrected only generated candidate-ID substitutions and passed all cases. No production behavior was changed to make these checks pass. Historical test drivers/mock inputs are hash-pinned before generated adaptation; all 1,961 baseline files and all 235 Stage26 frozen files remain unchanged.

The bound package passed **41 package checks and 38 mock installer checks**, zero failures. These exercise actual packaged images/preflight/installer with synthetic metadata and injected tool responses, never a serial device. Receipts: [package](random-uppercase-package-tests.json), [mock installer](random-uppercase-installer-tests.json). Python 3.8 grammar is checked; native execution here uses Python 3.12.14/Bash 5.2.37/Linux, not High Sierra. Prior capability refusals and historical HTTP-auth expectations retain their separate dispositions.

## Clean build and resource comparison

The approved isolated Arduino ESP32 3.3.0 archive-feedback profile is required, with ESP32-S3, 16 MiB custom partitions, PSRAM disabled, USB-OTG/TinyUSB/CDC and existing CPU/flash settings. All source/dependency and post-link guards remain mandatory. No global toolchain or SDK archive replacement is authorized.

| Measurement | Accepted lowercase | Uppercase candidate | Delta |
|---|---:|---:|---:|
| Compiler program bytes | 1,409,803 | 1,409,875 | +72 |
| Application BIN bytes | 1,409,952 | 1,410,016 | +64 |
| Static RAM bytes | 113,856 | 113,856 | 0 |
| Free OTA bytes per slot | 6,192,224 | 6,192,160 | −64 |

Clean compilation and post-link verification passed. Application SHA-256: `2cdb3e182dbbc3f2f2be21154cc49516e74337ed5c0c52a75aa772d1ef8eb098`. ELF SHA-256: `b71ba43f0639c60042f27c20b4d795e63ae5e9a7fe4eb6e1ebd7c17435a8c352`. Free OTA capacity: 81.452468% of each 7,602,176-byte slot. Partition identity remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

Full evidence: [linked build receipt](random-uppercase-build.json), [compact resources](random-uppercase-resources.json), [primary reference retrieval](random-uppercase-references.json). The verifier checked exact source/compiled-source equality, linked compiler call edges, production `esp_random()` binding, USB/NVS/startup guards, all 177 unchanged SDK archive identities, and ELF-to-BIN byte equality. Selected unchanged target compiler frame estimates: Runtime::tick 128 B; Adapter::step 144 B; Compiler::line 224 B; CompileSession::step 32 B; coordinator tick 384 B; setup 80 B; loop 32 B. The 4,224-byte synchronous Program::compile object-file frame is not a linked production path. One fixed alphabet byte is added to Runtime; no queue or per-character allocation is added. Physical heap, task-stack high-water, runtime latency and randomness quality are not measured by this stage.

## Review-only delivery

Package one Mac application-only ZIP with exact rollback to the accepted lowercase application, SHA-256 `0a4faafeba059c9578cd938e260eedcf03be2c34b53731e6bbfc5178799fd774`, 1,409,952 bytes. Preserve High Sierra 10.13.6, Bash 3.2, Python 3.8, esptool 4.12, installed-layout/security checks and explicit owner confirmation. No LED helper is needed. Source commit: `b3906f1b4131c56719ff1b8a132dea7dad41f7c7`. Package: `evilduck-routeb-random-uppercase-macos-v1.zip`, **2,228,270 bytes**, SHA-256 `f3aa611dea7ba10cc133a3e7b58d22e3747f40bc88c410cd955f6bfd8253fbae`. [Artifact inventory](random-uppercase-artifact.json). The package's bundled report reflects pre-publication state; publication/download verification is recorded separately in the repository's final publication receipt. This avoids a circular archive hash.

The short TextEdit sheet covers ten uppercase random letters, mixed-case controls, STOP/Shift recovery and malformed rejection. Repeated random letters are valid. Canadian/US lowercase observations do not establish universal layout support or uppercase physical acceptance. New uppercase functionality remains physically unverified.

**GO: offline implementation/review and verified package preparation. NO-GO: hardware access, installation, flashing, OTA or automatic script execution without separate owner approval.** Keep the working firmware, rollback, private backups and historical evidence untouched. No renewed broad Caps investigation is required.
