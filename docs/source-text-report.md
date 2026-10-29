# Route B source/text portability — implementation report

Baseline `2bdf7e6cea7fb1a343d4ac0973a90578264ced07`; branch `routeb-source-text-portability-v1`; candidate `ROUTEB-SOURCE-TEXT-PORTABILITY-v1`. The accepted restart application's three scoped High Sierra owner passes and expected build ID are recorded in [owner evidence](source-text-owner-evidence.md) and the new [accepted-baseline record](source-text-accepted-baseline.json). Missing identifiers stay unknown; no new physical testing occurs here.

## Focused change and reference finding

Permit one optional leading UTF-8 BOM through the composed adapter while preserving raw bytes/identity and the8192-byte limit. Partial, repeated/misplaced markers, UTF-16 and other unsupported non-ASCII remain rejected before output. Extend the fourteen language aliases to inline operands with ordinary STRING/STRINGLN behavior; bare openers retain blocks and canonical terminators. Inline aliases are permitted bounded REPEAT text leaves; blocks remain rejected as repeat bodies.

The requested no-terminator inline form is explicitly an **EvilDuck extension**. Official documentation establishes blocks; saved official compiler regexes establish same-line suffixed forms ending END_STRING/END_STRINGLN. They do not establish the requested nonterminated form. Here inline terminator-looking tokens remain literal, matching ordinary text semantics, and official terminated-form compatibility is not newly claimed. [Exact design](source-text-design.md), [reference hashes/quotes](source-text-references.json), [compatibility inventory](source-text-compatibility.md).

Preserve restart/RESET budgets and identity, immutable Program/source capture, held/transient merging, collision/rollover handling, randomness/jitter, STOP/quarantine, preprocessing, functions, authentication, EDR1 and explicit engine selection. No USB identity/descriptor, partitions, settings, layout, Caps timing or global core/SDK change. INJECT_VAR remains blocked; no renewed research or broad Caps investigation occurs.

## Verification

The final fresh composed native run passed **435 cases, zero failures, 16,922 assertions**:32 new source/text cases contribute1,697 assertions, and403 selected earlier cases contribute15,225. ASan, UBSan and leak detection completed cleanly. No native development compiler/test failure occurred in this stage. [Exact per-case results, compiler command, source input identities and controls](source-text-test-results.json).

Coverage exercises BOM chunk/retry boundaries, raw size limits, LF/CRLF/no final newline, all aliases/formatting/DEFINE, unchanged blocks, REPEAT, malformed retained-source rejection versus exclusions, retries, held state, STOP/restart and cross-run isolation. Tests use actual composed modules with mocked transport/storage/clocks/randomness; these are local software observations, not physical Mac validation.

### Explicit generated expectation changes

The historical files remain unchanged. Generated candidate copies adapt only superseded BOM/inline-alias expectations: P14 changes17→26 assertions when production-adapter BOM admission becomes accepted; V11 changes16→25 for its equivalent BOM path; V06 changes11→7 by removing two now-supported inline-alias refusal inputs. The net change is **+14 assertions**, so the403 baseline cases contribute15,225 here rather than the prior15,211. The inherited receipt category `selected_unchanged_regressions` includes these declared generated adaptations and must not be read as a claim that obsolete refusals still pass.

The prior V14 provenance correction and earlier R27/U27 capability dispositions remain separately recorded; no old result or fault classification is rewritten. The earlier403-case receipt is historical; this release's selected cases were freshly executed. Package/mock-installer checks and target build/link results must be recorded separately. Linux mocks/builds do not prove physical Mac behavior.

## Resources and dependency provenance

The clean isolated build and final post-link verification passed using the unchanged approved Arduino ESP32 core3.3.0 archive profile, ESP32-S3/16MiB custom partitions, PSRAM disabled and existing USB-OTG/TinyUSB/CDC/240MHz/flash options. All177 SDK archive identities, dependency/source guards, startup/HID/NVS/ownership proofs, source selectors and ELF-to-BIN checks pass. No global core/SDK was patched or archive replaced. [Full linked receipt](source-text-build.json), [resource comparison](source-text-resources.json).

| Measurement | Accepted restart | Candidate | Delta |
|---|---:|---:|---:|
| Compiler program bytes |1,412,535|1,412,775|+240|
| Application BIN bytes |1,412,688|1,412,928|+240|
| Static RAM bytes |113,888|113,888|0|
| Free OTA bytes per slot |6,189,488|6,189,248|-240|

Each OTA slot remains7,602,176 bytes; free capacity is **81.414164%**. Application SHA-256: `2e2f7b5af6cbc9d7cac8b112276d4f38ab140aa6f041129b62269596a128a9e3`. ELF SHA-256: `73075c299027b8a20df80ba73b953e494b0e0ea2f2529314883bc8b8c0ee234f`. Expected partition table remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

Native Program/Runtime/CompileSession sizes remain6,936/4,944/4,144 bytes. The new `textCommandKind` compiler frame estimate is48 B. Other selected frame estimates remain unchanged, including Adapter step144 B, Runtime rewind32 B/deliver48 B/tick112 B, Compiler statement352 B/line240 B, com update176 B, coordinator tick384 B, setup80 B and loop32 B. These are individual static compiler frames, not cumulative task-stack high-water or measured physical headroom. No physical heap, timing or USB delivery measurement is claimed.

Final linked evidence includes the adapter-step to compiler-start call path, selected source/profile identity, retained rewind path and inherited safety guards. The first post-link checker attempt matched both executable `Adapter::step` and its local constant `signature` data symbol by prefix. The **new** verifier was corrected to select executable `nm` symbol types, then rerun successfully. This was a verification-tool false positive: no firmware, dependency or safety-predicate semantics changed, and the first native suite still passed without errors. The initial checker diagnostic remains separate from the final successful receipt.

The [preservation receipt](source-text-preservation.json) records all2,092 baseline files and executable modes unchanged, plus235 frozen Stage26 files passing. The new source manifest identifies exactly three changed generated application files: `core.cpp`, `adapter.cpp` and build ID in `caps_trial.h`; all source/artifact hashes are in the linked receipt. Historical source and evidence are not rewritten.

## Delivery and acceptance boundary

One review-only `evilduck-routeb-source-text-portability-macos-v1.zip`, with exact accepted restart rollback **1,412,688 bytes**, SHA-256 `1d4ea6394306885b832619adb3436eaeeccc0a67ce8b73e1f20dd0f9c7d0a060`. Preserve High Sierra10.13.6/Bash3.2/Python3.8/esptool4.12. Final archive identity, package/installer results, publication/download verification and previous-ref comparisons remain PENDING until performed.

The [short acceptance sheet](source-text-acceptance.md) requires a byte-verified BOM fixture through authenticated save/readback and explicit Route B launch; editor paste is insufficient. Its reviewed HTTP route uses X-Duck-Password, not Basic auth. The Python3.8 snippet keeps credentials in memory, refuses existing remote names and redirects, performs no retry and never starts execution. Device operations in that sheet are only for later separately authorized owner testing; none is performed during development.

GO: review after required checks pass. New physical behavior remains unverified. No hardware access, real HID execution, flashing, OTA, formatting, settings reset, private-backup access or owner-script execution is authorized by package preparation.
