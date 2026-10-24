# Route B preprocessing and Mac helper v4 — implementation report

Source baseline `32e22650f98faec03ebdce71446e9f48e8d39fe5`. Work continues on the existing branch; no `INJECT_MOD` branch or reimplementation. Helper v4 and firmware candidate are independent artifacts. No hardware access, flashing, OTA, real HID actions or owner payload execution occurred.

## Findings and changes

Actual retained composed lock-feedback sources were verified against all 10 after-hashes. Inline `INJECT_MOD` and lease-bound `HOLD/RELEASE` already exist, including exact-report, single-owner and `STOP` regressions. Preserve them; bare `INJECT_MOD` remains outside the agreed grammar. Branch names and stale standalone preview README statements are not evidence of missing composed functionality.

Part A’s permanent host path fix resolves the script's absolute canonical location and checks its unresolved native sibling leaf for regular/executable/nonsymlink status. The subprocess uses that absolute path. Authentication, explicit consent, assigned ID/session/freshness/`STOP` guards, all timeouts and at most one action/no retries remain. Relative/absolute invocation, another working directory, spaces, executable/symlink and script-symlink scenarios pass mocked regressions. Native C and firmware are unchanged. See separate helper v4 report/ZIP/publication receipt; owner physical-workaround evidence is not presented as new v4 execution.

Part B is an additive pinned patch on composed `core.cpp/core.h` and `caps_trial.h` identity only. Four canonical preprocessing directives freeze compile-time inclusion; `EXTENSION` / `END_EXTENSION` wrappers and optional `VERSION` are nonexecuting metadata. Source-order Boolean flags, fixed depth 8, 16 extensions, 23-character names and 63-character dotted versions are explicit profile restrictions. Fixed bitmap/source hashes preserve physical diagnostics and included/excluded read failures. Excluded ordinary unsupported source is not semantically validated or inventoried; lexical/metadata/directive structure still validates. See `source-compat-design.md`, `source-compat-compatibility.md` and `source-compat-references.json` for reference limits and exact rules.

The existing `Runtime`, ownership backend, USB/LED callbacks, wait logic, EDR1 receiver, partition table, settings, startup behavior and schemas are unchanged. New compiler storage is 4,096 bytes, no dynamic table or recursion, native Compiler size is 3,840 bytes. New diagnostics append existing enum values, preserving Timeout code 26. No additional script autorun or automatic transition is introduced.

## Investigation corrections preserved

An initial runner negative-control assertion used the wrong source-selector diagnostic wording; it stopped before compilation. The first composed run reported P14 and D12 failures. P14 assumed BOM admission incorrectly: the unchanged adapter rejects non-ASCII before the compiler. Direct compiler accepts BOM; final P14 records composed refusal and separate CRLF/no-final-newline success, not BOM compatibility. D12 was a generated fixture copy still expecting the old build ID; the test-only substitution was moved after all copies were created. Historical fixtures themselves remain unchanged. These were not relabeled as firmware fixes or discarded silently.

Review also found unmatched `END_REM` in excluded source could be ignored; the additive compiler now rejects it structurally, with a dedicated regression. The provisional first firmware build was stopped when this correction changed the source pin; no success is claimed for that interrupted build. Final patch SHA-256 `90500b0d96745eb04abf2493a619c1ba69ea38b784b548524bcc7edf0f9e76cd` was then frozen for clean build v2 and final tests.

## Clean firmware build and provenance

Profile `ROUTEB-PREPROCESS-20261024-v1`. Clean approved isolated Arduino ESP32 core 3.3.0/archive-feedback profile, ESP32-S3, 16 MiB, PSRAM disabled, existing USB-OTG/TinyUSB/CDC/CPU/flash configuration. No installed core or SDK modified. All 177 SDK archives, 284 inputs, 3 response files, 13 linker scripts and inherited USB/NVS/startup/source/ownership/feedback safeguards pass final post-link verification. Actual linked `CompileSession::step→Compiler::step→Compiler::line→preprocessing` edges verified; ELF-to-BIN regeneration passes.

| Measurement | Installed lock-feedback artifact | New candidate | Change |
|---|---:|---:|---:|
| Compiler program bytes | 1,407,859 | 1,409,475 | +1,616 |
| Application BIN bytes | 1,408,000 | 1,409,616 | +1,616 |
| Static RAM bytes | 112,120 | 113,848 | +1,728 |
| Free OTA bytes per `0x740000` slot | 6,194,176 | 6,192,560 | -1,616 |

New application SHA-256 `4251f320019dd813f2f0f4810c96f084f08127fa6a35ea6c99faece336e3ad5d`; free OTA capacity is 81.45773%. Compiler/frame estimates: preprocessing 48 B, line 208 B, Compiler step 144 B, CompileSession step 32 B, `route_u` tick 384 B, loop 32 B. These are individual compiler estimates, not summed task high-water measurements. Synchronous `Program::compile`'s 4,224 B object-file frame is dead-stripped from production; normal Route B uses static `CompileSession`. Native no-C++-heap probes cover compiler work, not all subsystem allocations. No physical heap/latency/stack measurements were taken.

## Verification, delivery and remaining limits

The final composed native run passed **221 cases, zero failures and 8,363 assertions**: 37 new preprocessing cases with 455 assertions, plus 184 unchanged selected regressions with 7,908 assertions. ASan, UBSan and leak detection were clean. The host helper has a separate **56-method** suite: 55 current checks and one expected historical v1 control. Repeated source, package and download runs are not added as distinct passes.

Complete results, clean-build details and linked dependency/source/archive/artifact hashes are in the adjacent `source-compat-*` results/build/link receipts. Historical language/refusal/status observations remain separately classified by inherited runners. Fresh official Markdown retrieval via curl succeeded; a default urllib request returned 403; no independent Hak5 compiler equivalence is claimed.

Package assembly must bind exact current rollback `ae079c5a1b0c10849bdf79c12a40e5f0f3a01fb50996e4499f5352b91b1c9a5d`, 1,408,000 bytes from the untouched public working package. Do not reuse the older keyboard-control rollback. Public package and installer identity/fault tests use disposable copies/mock esptool only. Package preflight lacking actual installed metadata must not emit a physical write plan. Hashes verify public software; installed firmware identity remains owner/installer-reported, not newly read back here.

GO: review the separate host helper and preprocessing candidate artifacts and harmless acceptance sheet. Physical installation/testing still requires owner review and separate explicit approval; no action has occurred. Keep the working lock-feedback installed. Source-profile limits, composed BOM refusal, missing independent compiler oracle, legacy CLI versus Route B distinction, Windows 11/unperformed host coverage, global Caps and host key-release/USB retirement guarantees remain explicit limitations. Helper v4 stays bound to current lock-feedback; it does not silently retarget the new firmware candidate. No broad Caps investigation is needed.
