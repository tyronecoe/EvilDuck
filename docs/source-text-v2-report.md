# Source/text v2 implementation report

Baseline `1659544f392a0523fa6e598423001e11919370aa`; branch `routeb-source-text-portability-v2`; build `ROUTEB-SOURCE-TEXT-PORTABILITY-v2`. No physical acceptance is newly claimed. The accepted baseline remains restart1,412,688 bytes / `1d4ea6394306885b832619adb3436eaeeccc0a67ce8b73e1f20dd0f9c7d0a060`.

Adds suffixed-alias-only final matching closing-token syntax, before DEFINE. Ordinary STRING/STRINGLN and blocks retain literal behavior; BOM handling is unchanged. Delimiter ambiguity is fail-closed under the [design](source-text-v2-design.md). The compiler's first-substring removal and tab failure are recorded observations, not emulated. [Compatibility](source-text-v2-compatibility.md), [acceptance sheet](source-text-v2-acceptance.md).

## Evidence and verification

Selected pinned public compiler functions reproduce14 positive simple forms and5 edge observations, using mocked character mapping/ENTER. [Reference receipt](source-text-v2-reference-results.json). No official runtime or real HID executes. Initial investigation extraction needed flexible brace spacing, and an uncaught tab-probe exception was changed to a per-case recorded TypeError observation; these were harness corrections, not firmware test outcomes.

Fresh composed native tests: **457 PASS, 0 FAIL; 17,612 assertions** (22 new cases/690 assertions and435 candidate-adapted baseline cases/16,922 assertions). ASan/UBSan/leak checks completed cleanly, with no native development failures. [Per-case receipt and command](source-text-v2-test-results.json). Build/package results are recorded separately below. Native coverage includes all14 forms, exact reports, ordinary literal tokens, unchanged blocks, DEFINE grammar boundary, bounded REPEAT, malformed retained source, BOM, held state, retries, STOP/restart and quarantine. Historical expectations remain untouched; generated Z12 changes only its obsolete literal-terminator expectation to v2 syntax precedence. Previous generated adaptations remain documented; no totals are retroactively changed.

## Resources and delivery

Approved isolated Arduino ESP32 3.3.0 archive profile; ESP32-S3/16MiB, PSRAM disabled, unchanged USB/partitions/dependencies/SDK. Retain all177 archive identities and source/ELF guards. Baseline program1,412,775, BIN1,412,928, RAM113,888, freeOTA6,189,248bytes per7,602,176-byte slot. Clean build and post-link verification PASS. [Build receipt](source-text-v2-build.json), [resources](source-text-v2-resources.json). Program **1,413,055 B** (+280 versus v1); BIN **1,413,200 B** (+272 versus v1, +512 versus accepted restart); static RAM **113,888 B** unchanged; OTA free **6,188,976 B**, 81.410586%. All177 SDK archives, source/profile/startup/HID/NVS/ownership/feedback/rewind guards and ELF-to-BIN checks pass.

Application SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. ELF SHA-256 `acb58b6bcf383d6301317484103662edc5bf6c8fb24f3f3829b1e6250e095e86`. Partition SHA remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`. Object sizes Program6,936/Runtime4,944/CompileSession4,144 B remain unchanged. Compiler::statement frame grows352→368 B (+16); other selected frames are unchanged. Exact compiler frame estimates are in the resource receipt; they are not hardware stack high-water or heap/latency measurements. No new runtime allocation or state buffer is introduced.

Only two composed files change: `core.cpp` and build identity `caps_trial.h`. BOM adapter, backend, scheduler, storage, EDR1, USB descriptors and partition sources remain unchanged. [Preservation receipt](source-text-v2-preservation.json): all2,124 historical files/modes and235 frozen files unchanged. No global core/SDK was patched.

One distinct review-only `evilduck-routeb-source-text-portability-macos-v2.zip`; exact accepted restart rollback required, not unaccepted v1. Preserve High Sierra10.13.6/Bash3.2/Python3.8/esptool4.12. All **46 package checks and 38 mock-installer checks passed**, zero failures. [Package results](source-text-v2-package-tests.json), [installer results](source-text-v2-installer-tests.json). The46th check explicitly requires the inherited v1 source/text proof as well as v2. The tests use public disposable copies and synthetic metadata/tool responses, not a real serial port.

Public ZIP **2,395,166 bytes**, SHA-256 `589c277b48838777a9333304e29ba7c1052a0a022558fa5f2bf0a1ffe7d2f1d0`. [Artifact inventory](source-text-v2-artifact.json). All24 members,20 support bindings, both applications and CRC checked; deterministic re-archiving is byte-identical. Publication/download verification follows separately. The package report is a frozen pre-publication snapshot.

GO: candidate review after checks. Physical testing/installation/HID/flashing/OTA need separate owner authorization. No such access, private backup use, automatic payload execution, formatting, settings reset or EDR1 change occurs. INJECT_VAR remains blocked.
