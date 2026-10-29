# Bounded Route B payload restart — implementation report

Baseline `7230bcddcdddd6b7e305f07721b7922df01dbd91`; isolated branch `routeb-payload-restart-v1`; candidate `ROUTEB-PAYLOAD-RESTART-v1`. The accepted application's five scoped High Sierra owner passes are preserved in [owner evidence](payload-restart-owner-evidence.md). No new physical testing is performed here.

## Change and preservation boundary

Exact argument-free `RESTART_PAYLOAD` uses a distinct cached event and the existing owner-scoped neutral-clear barrier before privately rewinding execution. It retains the same Program/revision/borrow, request/session/lease, captured Caps timing, backend ID sequence, diagnostic history and original whole-request budgets. It resets per-execution values, call/evaluation/text/delay/pending state and random/jitter defaults. It does not call `Runtime::start()`, reload storage or queue an external Start. [Exact grammar and policy](payload-restart-design.md), [compatibility update](payload-restart-compatibility.md), [three-trial acceptance sheet](payload-restart-acceptance.md).

STOP remains cooperative and prioritized; ambiguous output, disconnects and cleanup failures retain existing quarantine behavior. Local neutral submission is not proof of host receipt, global key release or USB retirement. Ordinary RESET remains clear-and-continue, preserving runtime settings. Official restart intent and EvilDuck-specific state/budget policy are distinguished explicitly.

Preserve accepted text/keyboard utilities, randomization/jitter, expressions/functions, preprocessing, inline INJECT_MOD, HOLD/RELEASE, lock feedback, authentication, explicit Route B selection and EDR1. No USB identity, descriptor, partition, settings-schema, PSRAM, global core or SDK change is introduced. INJECT_VAR remains blocked; research and unresolved reference fields stay unchanged.

## Verification

The final composed native run passed **403 cases, zero failures, 15,211 assertions**:32 new restart cases contribute278 assertions, and371 selected existing cases contribute14,933. ASan, UBSan and leak detection completed cleanly. [Exact results, compiler command, input hashes and development diagnostics](payload-restart-test-results.json). Missing/zero candidate selectors were intentionally rejected and are classified separately.

Coverage exercises neutral-before-output ordering, exactly-once retries, budgets/clock wrap, nested function/expression abandonment, default reset, Program borrowing, same request/lease, STOP/callback races, disconnect/quarantine, malformed retained source, exclusions and subsequent-run isolation. Relevant accepted text/keyboard, randomization/jitter, preprocessing, keyboard ownership, lock-feedback and EDR1 cases are included. These are mocked local outcomes, not physical High Sierra validation.

Development run native-v1 failed compilation because the new test driver omitted `adapter.h`. Native-v2 completed401 PASS/2 FAIL: Y28 incorrectly assumed an ordinary run starts the standalone diagnostic trial; Y30 allowed only1,200 turns for separate1,000-turn pending and1,000-turn cleanup budgets. Those test assumptions were corrected without changing production behavior. Native-v3 is the final403-case result above; development counts are not added to its totals.

### Historical V14 provenance correction

The old text/keyboard receipt recorded V14 as53 assertions and inferred that the last source edit was compiled because the executable timestamp was later. Inspection now shows that the old binary lacks the late held-key/jitter assertion string, while the unchanged historical driver contains that branch. The old `final_driver_used` timestamp inference was therefore incorrect. Historical source, binary, receipt and report remain unchanged as evidence; this correction does not retroactively certify the missing coverage.

The fresh run executes V14's full79 assertions, adding26 held-key/jitter checks relative to the prior receipt. Accordingly the371 selected cases now contribute14,933 assertions, not the old14,907. No regression expectation was weakened; the26 newly executed assertions are counted only in this fresh run. The new receipt records this provenance gap explicitly. Earlier generated-copy identity substitutions and previously documented capability adaptations remain separately described; they do not modify historical files.

The final public package passed **44 package checks and 38 mock-installer checks**, zero failures. [Package results](payload-restart-package-tests.json), [mock-installer results](payload-restart-installer-tests.json). Tests use disposable public copies and synthetic tool/device responses; no actual serial endpoint is opened. No Linux mock or successful build establishes physical High Sierra behavior. Preserve historical test classifications and all existing artifacts/refs.

## Clean build and resources

The clean isolated build and final linked verification passed using the unchanged approved Arduino ESP32 core3.3.0 archive profile, ESP32-S3,16MiB custom partitions, PSRAM disabled and existing USB-OTG/TinyUSB/CDC/240MHz/flash settings. All177 SDK archive identities, dependency/source pins, source selectors, linked restart/clear/ownership call evidence and ELF-to-BIN checks pass. No global installation was patched or archive replaced. [Full build/link receipt](payload-restart-build.json), [resource comparison](payload-restart-resources.json).

| Measurement | Accepted text/keyboard | Restart candidate | Delta |
|---|---:|---:|---:|
| Compiler program bytes |1,412,247|1,412,535|+288|
| Application BIN bytes |1,412,400|1,412,688|+288|
| Static RAM bytes |113,888|113,888|0|
| Free OTA bytes per slot |6,189,776|6,189,488|-288|

Each OTA slot remains7,602,176 bytes; free capacity is **81.417321%**. Application SHA-256: `1d4ea6394306885b832619adb3436eaeeccc0a67ce8b73e1f20dd0f9c7d0a060`. ELF SHA-256: `77ed84b9f99c77e36e2bf0ca2f09cb44f8ce0c4685556d61a4d285cd97b244a7`. Partition-table identity remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

Native object sizes remain unchanged: Program6,936 B, Runtime4,944 B and CompileSession4,144 B; compiler workspace remains4,096 B. The new `Runtime::rewindExecution` compiler frame is32 B. All other selected frames retain the accepted values, including Runtime deliver48 B/tick112 B/evaluation144 B, adapter step144 B, reset192 B, com update176 B, coordinator tick384 B, setup80 B and loop32 B. These are static compiler estimates, not cumulative task-stack high-water or measured physical headroom. Y32 confirms no C++ heap allocation during the tested runtime rewind/callback-cancellation sequence. Hardware heap, stack high-water, latency, entropy quality and USB delivery remain unmeasured.

Post-link verification confirms the linked rewind symbol and deliver-to-rewind edge alongside the inherited neutral-clear/ownership, USB, NVS, feedback and source/profile safeguards. The [preservation receipt](payload-restart-preservation.json) records all2,061 baseline files and executable modes unchanged and235 frozen Stage26 files passing. Exact before/after hashes are in the new source manifest, with the complete candidate inventory in the build receipt.

## Delivery

Prepare one review-only `evilduck-routeb-payload-restart-macos-v1.zip`. Bind exact accepted rollback **1,412,400 bytes**, SHA-256 `53acc374ef38be652b6847d4b84f2dc7d42fa73a3dd54ea62d5208be4cbc0167`; preserve High Sierra10.13.6/Bash3.2/Python3.8/esptool4.12 interfaces. Public ZIP: **2,371,203 bytes**, SHA-256 `36e2ca0df08eeea1cec5e766330a0e4699351d28cfa2b2f382d3e112052d15f2`. [Artifact inventory](payload-restart-artifact.json). All 24 members, 20 support bindings, both application images and CRC are verified; deterministic re-archiving matches exactly. Independent archive review confirmed S3 headers, image checksums, unchanged table geometry and app-only ranges. Publication/download verification follows separately. The bundled report is the source-commit pre-publication snapshot; it is not regenerated to claim later checks. No new LED helper is required.

GO: software/package review after required checks pass. Physical installation/testing, flashing, real HID output and OTA require separate owner approval. No hardware access, stored owner payload execution, settings reset or formatting is authorized by this release preparation.

## Source inventory

Only new `tests/payload_restart/*`, `docs/payload-restart-*` and the new public ZIP are added. The pinned composition patch changes four generated application files: `core.cpp`, `core.h`, `adapter.cpp` and build identity in `caps_trial.h`. The scheduler, backend, storage and EDR1 source bytes remain unchanged. An independent source/artifact review rehashed all 201 candidate sources and five build artifacts, confirmed the four-file delta and linked rewind-to-deliver edge, and found no blocking defect. Exact source pins and final linked evidence are retained in the build receipt.
