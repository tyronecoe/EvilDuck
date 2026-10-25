# Combined Route B randomization/jitter release

Baseline `9ebdb7195910a247921a7a4e032934fbc372cdc4`; isolated branch `routeb-randomization-jitter-v1`; candidate `ROUTEB-RANDOMIZATION-JITTER-v1`. Source changes only in new composition tooling/docs/package. The owner-reported uppercase acceptance is in randomization-jitter-owner-evidence.md; no hardware testing is performed here.

Adds four character commands, three numeric properties and two optional jitter properties. Exact grammar,72-character spacing interpretation, endpoints, per-run defaults and EvilDuck scheduling policies are in [design](randomization-jitter-design.md). INJECT_VAR remains unsupported. Existing transport/keyboard backend, Mac Caps dwell, USB/NVS safeguards, partition geometry, authentication and EDR1 remain unchanged.

## Verification

Fresh final native verification: **331 PASS / 0 FAIL, 13,054 assertions**. New46 cases contribute2,209 assertions;285 selected baseline cases contribute10,845. ASan/UBSan/leak detection pass. T46 verifies no C++ heap allocation during jitter selection and cached sink retries; the existing sampler allocation probe also passes. T01–T04 exhaust every alphabet and expected HID mapping; numeric tests exercise full width, equal/reversed ranges, resumable operands, functions/conditions/loops; jitter tests verify exact0/20ms endpoints,65,535ms pending/cancellation,30-second budget timeout, clock wrap, release bypass and retries. Composed STOP, disconnect and cleanup tests pass.

[Exact results and commands](randomization-jitter-test-results.json). Initial320-case and expanded330-case runs also passed; they are recorded as development runs, not added to the final totals. Historical R27/U27 files remain unchanged. Their generated candidate copies remove newly supported commands from old refusal lists; seed rejection stays. The inherited receipt category `selected_unchanged_regressions` includes those explicitly documented adaptations, so it does not claim obsolete capability refusals still pass. Other historical dispositions remain separately recorded.

All 1,991baseline files and executable modes remain unchanged; Stage26freeze235files passes. [Preservation receipt](randomization-jitter-preservation.json). Python3.8grammar checks pass. Execution here uses Python3.12.14/GNU Bash5.2/Linux; native High Sierra execution remains pending. Package tests operate on disposable public copies and synthetic metadata only.

## Resources and artifacts

Clean isolated build and final post-link verification PASS. [Full receipt](randomization-jitter-build.json), [resource comparison](randomization-jitter-resources.json), [primary references](randomization-jitter-references.json).

| Measurement | Accepted uppercase | Combined | Delta |
|---|---:|---:|---:|
| Compiler program bytes | 1,409,875 | 1,410,939 | +1,064 |
| Application BIN bytes | 1,410,016 | 1,411,088 | +1,072 |
| Static RAM bytes | 113,856 | 113,880 | +24 |
| Free bytes per OTA slot | 6,192,160 | 6,191,088 | −1,072 |

Free OTA capacity81.438367%. Application SHA-256 `2e1d8345417c6f23a5df3d884db42dd2a0f9f305120ee494c56a58048e677496`; ELF SHA-256 `fdccd93ae2422dd16c2284599abe6d3935f7c2da9ab51b218a27c50262b30b0c`. Partition identity remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

The24-byte fixed Runtime state increase is measured in both native object size (4920→4944bytes) and target static RAM. Program/CompileSession native sizes stay6936/4144bytes. No new allocation or queue path is introduced. Compiler frame estimates: sampler64B(new), deliver32→48B, tick128→112B, evaluationStep144B(unchanged), Compiler::line224→240B, Adapter::step144B, CompileSession::step32B, coordinator tick384B, setup80B and loop32B unchanged. Frame sizes are not cumulative task-stack high-water measurements.

Post-link checks include exact source/compiled-source identity; linked sampler call edges from expression evaluation, event delivery and tick; esp_random binding; inherited USB/NVS/startup/ownership checks;177unchanged SDK archives; ELF-to-BIN equality. Production partition/USB metadata and global toolchain are unchanged. Package and publication receipts follow separately. Exact rollback remains uppercase application1410016 bytes / `2cdb3e182dbbc3f2f2be21154cc49516e74337ed5c0c52a75aa772d1ef8eb098`. No physical heap, stack-high-water, entropy-quality or latency measurement is claimed.

GO: offline software review and package preparation. NO-GO: installation/hardware/OTA without separate owner approval. See short acceptance sheet; no LED helper is required. Public package cannot authorize itself for installation.

## Timing and compatibility limits

The existing default30-second runtime budget remains. A MAX65535ms jitter setting is accepted but a long draw can time out before output; cleanup remains prioritized. Official docs do not specify jitter endpoints or command boundaries, so the chosen inclusive pre-press policy is explicitly EvilDuck-specific. RANDOM_CHAR excludes ambiguous whitespace by owner selection. Native Linux verification does not establish High Sierra USB delivery, physical entropy quality or universal keyboard layouts.

## Source and delivery inventory

Only new `tests/randomization_jitter/*`, `docs/randomization-jitter-*` and the public ZIP are added. The composed delta changes `core.cpp`, `core.h` and `caps_trial.h`; the adapter, HID backend, descriptor, report scheduler, storage and EDR1 sources remain unchanged. Before/after hashes and appended opcodes/errors are in the source manifest; the full201-file candidate inventory is in the build receipt. No new callback API or parser is introduced.

The bound package passed **42 package checks and38 mock installer checks**, zero failures. [Package results](randomization-jitter-package-tests.json), [mock installer results](randomization-jitter-installer-tests.json). Final ZIP inspection verifies24 members (20 support files plus application, rollback, expected table and manifest), CRC, all support bindings, both app identities, Python3.8grammar and shell syntax. An ad hoc review initially expected25 members; that count assertion was corrected against the explicit manifest inventory and passed without changing the ZIP. The unbound source preflight correctly refuses RELEASE_NOT_BOUND; only the packaged bound preflight is release-ready.

Public ZIP `evilduck-routeb-randomization-jitter-macos-v1.zip`: **2,306,499 bytes**, SHA-256 `a25e703dbd8198fa9dfa29f3f04a278ae0b704ae220bd377b8fad0036ac964d1`. [Artifact inventory](randomization-jitter-artifact.json). No LED helper or second installation package is needed. Published-byte verification is a separate receipt to avoid circular archive hashes. The package's bundled report is a pre-publication snapshot.
