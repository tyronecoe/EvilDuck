# Route B random lowercase — implementation and reference report

Baseline: `83c1b7da9ae3aca4fda51fe96f5959a31e3ec9b4`; isolated branch `routeb-random-lowercase-v1`. Prior remote tips were inspected before branching; no relevant newer work required incorporation. The owner's accepted preprocessing build and four scoped trial results are recorded separately in `random-lowercase-owner-evidence.md`, without inventing missing boot/session identifiers or repeating physical tests.

## What is implemented, and what is not

**INJECT_VAR remains unsupported.** Official sources establish stored-scancode injection, not its numeric packing, modifiers, validity or locale/release representation. Payload Studio's HTTP200 page is an authentication/license page, not an independently available compiler. No authenticated access was attempted. Stage15 unresolved vectors remain unchanged. The current compiler explicitly rejects retained INJECT_VAR before output; it does not print decimal values or invent an EvilDuck packing.

The separately identified fallback implements exact, argument-free `RANDOM_LOWERCASE_LETTER` with the official 26-letter a–z set. Source order, IF/WHILE/functions, preprocessing exclusions and extension wrappers are existing paths. Uppercase/digit/symbol groups, numeric RNG variables, packed-keycode capture/reuse, seed controls and jitter remain out of scope. See the bounded contract and updated matrix for limits.

Production uses SDK `esp_random()` through an injected callback; deterministic native tests substitute the API and also directly inject providers into Runtime. Sampling rejects the top 22 uint32 values and limits attempts to 8, with at most one draw per tick. It caches the selected ordinary Character event through retries. Runtime sampler state is cleared on start/cancel/error; provider dependencies have an explicit lifetime contract. Existing lease ownership, held/transient reports, collision/rollover refusal, cooperative deadlines, STOP/error cleanup and quarantine remain intact. No new transport event, allocation table, settings, storage format, LED protocol or USB descriptor change was introduced. No cryptographic or physical entropy-quality claim is made.

The additive pinned patch changes only composed `core.cpp`, `core.h`, `adapter.cpp` and the candidate identity in `caps_trial.h`. Historical source/patches/verifiers, working packages, owner evidence and the helperv4 path fix are retained unchanged. New ErrorCode/IR values are appended; Timeout26 and PreprocessorSyntax36 remain stable.

## Verification

The actual composed modules are tested with mocked storage/USB/clocks/SDK entropy. Thirty new cases cover all 26 deterministic letters and exact eight-byte report ordering; range boundaries and bounded rejection; invalid retained syntax and excluded source; INJECT_VAR/property rejection; loops/functions/extensions; held modifiers/keys, collision and seventh-key refusal; backpressure and cached retries; STOP before/during output; disconnect, ambiguity/quarantine, exhaustion and subsequent-run isolation. Direct Runtime tests cover missing/false/throwing providers, cancellation inside callback, repeated sink retries and fixed-state allocation behavior. No tests access hardware or execute owner scripts.

The first native compile exposed a collision with an existing test-harness esp_random stub. A test-only SDK-header substitution now isolates the injected random character provider; the production adapter still compiles against the real SDK header. No production change was needed for that harness issue. An early post-link invocation correctly failed because the build report was not yet complete, and the new verifier initially compared against the wrong parent preparation pin. Those verification issues were corrected; dependency predicates were not removed. The final verifier checks the actual linked deviceRandom→esp_random call and inherited compiler, USB/NVS, source, startup and archive identities.

Final test and package receipts alongside this report provide exact executed counts. Historical unsupported/obsolete status fixtures remain separately classified by inherited regression tooling; unresolved vectors are not counted as compatibility passes. Repeated artifact checks are not added as new distinct feature tests. Python-only packaging tests use fake esptool and disposable public files; they do not validate macOS IOKit or physical installation.

## Clean build and resources

Clean approved isolated Arduino ESP32 core 3.3.0/archive-feedback profile; ESP32-S3, 16 MiB custom table, PSRAM disabled, existing USB-OTG/TinyUSB/CDC, CPU and flash settings unchanged. All 177 SDK archives remain identical to the approved archive profile. No global toolchain was patched. Full post-link checks retain compiled-source/ELF/BIN identity, existing source/profile selectors and final linked RNG-provider evidence.

| Measurement | Accepted preprocessing baseline | New candidate | Delta |
|---|---:|---:|---:|
| Compiler program bytes | 1,409,475 | 1,409,803 | +328 |
| Application BIN bytes | 1,409,616 | 1,409,952 | +336 |
| Static RAM bytes | 113,848 | 113,856 | +8 |
| Free OTA bytes per slot | 6,192,560 | 6,192,224 | -336 |

Free OTA capacity: 81.45331%. Application SHA-256 `0a4faafeba059c9578cd938e260eedcf03be2c34b53731e6bbfc5178799fd774`; ELF SHA-256 `63b501860da914019b1548d90ebdfcde8f290d5e44290ff0e6ae6849ffbba0d6`. Individual target compiler frame estimates: Runtime::tick 128 B, deviceRandom 32 B, Adapter::step 144 B, Compiler::line 224 B, CompileSession::step 32 B. These are not physical task-stack high-water or latency measurements. SDK RNG call duration/entropy depends on the target environment and is not measured here. No new per-character C++ allocation is intended or required.

## Delivery and remaining physical checks

The Mac application-only package must bind exact rollback `4251f320019dd813f2f0f4810c96f084f08127fa6a35ea6c99faece336e3ad5d`,1,409,616bytes from the untouched accepted public preprocessing ZIP. The older lock-feedback application is not the rollback target. Existing table/OTA/security/owner-confirmation guards and Python 3.8/Bash 3.2/esptool 4.12 package interfaces remain. No LED helper is needed, supplied or silently retargeted.

Review the short benign TextEdit acceptance sheet: fixed prefix, 10 random lowercase letters and suffix; separately supervised STOP and malformed-source refusal. Correct US input source, Caps off and no held Shift are prerequisites for interpreting lowercase visible text. Under intentional held Shift, merged reports may correctly produce uppercase. Windows 11 and new physical behavior remain unverified; macOS 10.13.6 limitations must not be generalized to every platform.

**GO: review the software candidate and reference blocker. No physical installation/testing is authorized.** The installed accepted firmware is untouched. No hardware access, flashing, erase, format, OTA, automatic payload execution, EDR1 changes or broad Caps investigation occurred. New sample behavior is software-tested only; INJECT_VAR canonical compatibility is not claimed.

Final native verification: **251 PASS, 0 FAIL, 9,578 assertions** — 30 new cases with1,215 assertions and221 selected baseline regressions with8,363 assertions. ASan/UBSan/leak checks are clean. The final driver includes a no-C++-heap probe during random selection and repeated sink retries. Repeated runs are not summed as extra feature passes. Native object sizes measured here: Runtime4,920bytes, Program6,936bytes, CompileSession4,144bytes; these are Linux ABI object sizes, not target task-stack consumption. The production clean-build static-RAM increase is8bytes. All1,930 baseline tracked files/modes and235 frozen Stage26 files remain unchanged; all code changes are additive overlays and new tooling/docs.

## Final package verification

The review-only Mac ZIP is **2,227,706 bytes**, SHA-256 `b2c93548e5239e79fef5ffac09cb5231f5edc2873cc0b7774832fe426aecbef5`, bound to source commit `6fc1e500f493683f30363261d59ebbdeca1f276c`. The actual package passed **40 integrity/fault checks** and **38 bound-installer checks**, zero failures, using public synthetic metadata and fake esptool only. Python3.8 grammar, Bash syntax, exact image/rollback identities, no unapproved nonapplication ranges, missing-metadata refusal and deterministic byte-identical rearchive are checked. This verifies software/package behavior, not physical installation or High Sierra native behavior. See separate artifact/package/installer receipts. No new LED helper is required or bundled.
