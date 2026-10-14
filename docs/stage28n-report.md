# Stage28N native pinned USB component report

**GO: review actual native component observations and the minimal future change design. CONTRACT NOT SATISFIED by unchanged stack. NO-GO: production integration, installed dependency changes, live USB/HID, target/SDK/firmware builds/images, flash/boot/OTA or automatic Stage28O.**

Parent `50ec41349136bfaddbac6a44622c3c25e2ce42e3`, clean Stage28M branch; delivery `stage28n-pinned-usb-components`. Frozen Stage26 `968c8e0aaf459b0b8b652cc57fe88225894ab64b`. Only new Stage28N tests/docs/receipts are delivered. All1,079 historical files/paths/executable modes and235 frozen files remain unchanged; old refs must remain unchanged at publication. Final SHA/post-push proof is supplied separately, not embedded self-referentially in precommit integrity receipt.

## Concrete progress

A native harness executes byte-identical publisher-pinned TinyUSB C dispatch/class/submission/claim/control paths through a fake DCD and supported CUSTOM OS. No vendor edits, handwritten replacement class/dispatcher, private static access or actual application callback shortcut. Each case has gcov function/source evidence. All21 required vendor files were independently retrieved/hashed, and the final suite used a second minimal fresh source tree containing only those files. Source material and builds remain scratch; no dependency tree/archive is committed.

**20 observation PASS / 0 unexpected FAIL / 131 primary assertions**, ASan/UBSan/leak clean. Negative control exits1 separately. Unchanged Stage28M executed once: **36 PASS / 0 FAIL / 9,689 assertions**, separately counted; K01 reproduction/correction classifications remain intact. N21 builder DCD runtime and N22 full protected core runtime are BLOCKED/NOT EXECUTED, not PASS. No Mac or device behavior claimed.

Important actual-code observations:

- Raw8 is copied/framed before fake lower submission; ID1 produces9 bytes, ID0 eight. Completion can traverse real queue/task/class before lower submit returns.
- Busy/claimed exclusion does not create an owner lease. Oversized refusal after claim retains it until explicit release; bool-false/ready cannot be treated as generic clean refusal.
- Injected duplicate completion triggers another callback. An old event around buffer/endpoint reuse reads current bytes and can clear current busy state; event has endpoint/result/len, not C/Q.
- Callback-time resubmission can change its borrowed buffer. Partial/oversized length reaches observer; fake observer bounds are not a SDK guarantee.
- Reset/unplug/configuration clear mappings but do not certify event/controller retirement; finite fixture queue drops fifth event. WAIT_FOREVER primitive is entered; real kernel waits are not executed.
- Protocol property changes through genuine control ACK; raw report-ID framing remains caller-directed. Builder-selected hardware suspend maps to UNPLUGGED, unlike explicitly injected SUSPEND scenario.
- Forced false DCD deinit is ignored by actual tud_deinit; later event reaches deleted queue. Fake null guard prevents a host crash and is not real malformed-USB protection.

These are observed unchanged-code behaviors under deliberate substitutions/injections. They do not assert physical hardware normally creates duplicate/stale/bad-length events or that current firmware exercises each misuse. Exact receipts and limits: test-report/results and component-boundaries.

## Provenance layers

A: official package digest430,471,837 B / `a871d945c6bfb685ecff5e30ad759f280c841ea143071466b2e611bd1800f18f`, cached ZIP/member independently rechecked. TinyUSB archive1,109,204 B / `dece5cdd1d132dabb5e2022d8e3d293592b10f03de5902d9740994d652dd9a18`; versions/config and protected core tree/pins unchanged.

B: publisher-recorded builder `afa5cdd0d41d7e465d2e39867b24aef48b1c7b84`, TinyUSB `8a78804ff91271fb32008288777fad9fe73f5735`, IDF `b66b5448e0dfac6be135e6f0ac21010aba231180`. Selected builder DCD and recipe freshly read/hashed; upstream DCD not substituted.

C: exact21 C/header bytes compiled natively, official URLs/revision/SHA plus45 fixture/system include-source records, host config/shim/compiler hashes and commands in source-manifest/results. Config differs deliberately: CUSTOM OS, queue4, HID1/64B, no CDC/MSC, fixed fixture descriptors.

D: matching shipped headers and existing archive/debug/relocation evidence support specific source/ABI findings. New archive extraction inspects only already pinned objects; archived usbd provides weak dcd_deinit, selected DCD has no source definition. Existing controlled ELF retains strong complete and weak failed hooks, with no exact dcd_deinit symbol. Not a new firmware build.

E: full source working-tree/compile/source-to-object equivalence and physical lifecycle remain unproven. No signed attestation is demanded as the only possible evidence; specific corroborated facts are separated from whole-build confidence. No SDK replacement/rebuild was attempted.

## Design and remaining gates

The documented smallest coherent plan is opt-in tagged HID IN try-submit + per-endpoint fence: Q/C created before ownership, retained in DCD/event/dispatcher/class/core; generation checked before endpoint busy clearing; explicit bounded ownership outcome; stable success shape plus controller retirement; additional observer/context fence; actual producer lease/binding; extension of existing hooks without competing strong globals. ABI/config/archive compatibility must be verified in a future isolated authorized process. No patch implemented. Stage28L predicate/budgets, Stage28M barrier/E guard and language subset unchanged.

Native execution resolves actual dispatch behavior and tested-byte provenance; authentic correlation, bounded real entry, real retirement/quiescence, producer/concurrency/binding and physical behavior remain separate blockers. Recommended next proposal is separately reviewed native-only tagged-event/checked-try prototype, not automatic SDK patch, production adapter or board test. See minimal-change-design and limitations/next-gates.

## New file inventory

Tests: boundary.c, boundary.h, tusb_config.h, tusb_os_custom.h, test_components.c, prepare_sources.py, run_tests.py, verify_scope.py under tests/stage28n/.

Docs: stage28n-owner-scope.md, stage28n-source-manifest.json, stage28n-component-boundaries.md, stage28n-test-report.md, stage28n-test-results.json, stage28n-minimal-change-design.md, stage28n-limitations-and-next-gates.md, stage28n-report.md, stage28n-integrity.json under docs/.

Integrity receipt contains precommit scope/hash/ref evidence, excluding its own hash. Publication must add only new Stage28N ref, preserve38 previous refs and leave clean worktree. No previous firmware, Arduino Micro, core/SDK/global tools, preview/historical tests/docs/profiles, identity/descriptors/partitions/settings or owner files modified. No physical access, private backups, stored owner payloads, credential access, HID/OS injection, target/firmware build, flash/erase/format/boot/OTA. Stock availability remains owner-confirmed external. Stage28O not begun.
