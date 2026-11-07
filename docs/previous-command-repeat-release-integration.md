# Previous-command REPEAT — committed release integration

Candidate build ID: `ROUTEB-PREVIOUS-COMMAND-REPEAT-v1`.
Branch: `routeb-previous-command-repeat-v1`, descended from
`fcba0385ce21662c7a504e0c9b6fba0dfa2c4f8d`.

This stage advances the already implemented compiler-only REPEAT source through
the normal committed-source release process. The owner explicitly authorized
local checkpoint commits, one clean target build and a local review package.
It does not authorize a push, merge, installation, serial/device access, HID
execution, flashing or OTA.

## Source and provenance boundary

The original 12 uncommitted implementation/test/document inputs and six raw
receipts were hash-verified before release integration. Those historical files
remain unchanged except for the canonical normal build selector, which now
selects the additive release entry. New release files live under
`tests/previous_command_repeat_release/`; packaging is a separately pinned local
review stage. No scratch, private backup, credential or owner-script contents
belong in the checkpoint.

The final overlay runs after the entire previous-command REPEAT composition,
including experimental H1/right modifiers, bounded lock waits, privacy, editor,
dashboard and static-response fixes. Its final delta changes only the build-ID
literal in `caps_trial.h`. All 201 source files are pinned; `core.cpp` remains
`01fda98ee58d34cd523241cfdd1da37b6992e037b889ce964ce3e32c899b0c4b`.
Compared with the privacy integration base, exactly four source paths differ:
`core.cpp`, `webfiles.h`, `webserver.cpp`, `caps_trial.h`; 197 remain identical.
Compared with the last static-response candidate, only the REPEAT compiler and
new identity differ. No runtime/HID, storage, authentication, USB descriptor,
partition, PSRAM, dependency or SDK-profile change is authorized.

Before compilation, the original static-response `build_inputs()` must execute
its actual dirty-worktree and Git-blob guards. The new builder extends that
committed inventory to every selected REPEAT/release input and records the exact
source checkpoint. No uncommitted-manifest fallback or temporary commit outside
the reviewed branch is substituted. The checkpoint, source inventory and
selected input bytes must remain stable throughout clean compilation and
verification. Package-only commits do not change the recorded compiler context.

## Verification requirements

The additive release verifier retains all 190 inherited assertion nodes and
their dependency, startup, profile, ownership, image and link predicates. Only
the explicit final source/identity expectations advance. It adds committed
REPEAT-input coverage, final 201-file source checks and actual compiled/linked
compiler witnesses, while retaining the existing static-handler pointer/length
and asset-body proof. An omitted compiler overlay, old core, wrong build ID,
tampered input or false provenance must reject.

Fresh final-composition native and browser checks bind the production bytes;
historical tests and expected values are not edited. Mocks retain historical
fixture identity where needed, and the actual final target identity is verified
independently rather than inferred from a mock label. Source-only stage results
and its failed development receipts remain preserved in their original files.

The clean build must use the existing isolated archive-based Arduino ESP32 3.3.0
profile and unchanged toolchain/dependency guards. A passing native test is not
target compilation, and a linked image is not owner hardware acceptance. Actual
application/ELF hashes, sizes, resource measurements and verification outcomes
must be recorded after the build; no prospective application hash is asserted
here.

Fresh pre-checkpoint checks on the final 201-file source passed: 50 REPEAT cases
(2,739 assertions), 28 privacy cases (736), 558 inherited native cases (23,901),
and 86 web/editor/dashboard groups (1,518). Causal controls, profile refusals,
ASan, UBSan and leak checks also passed. Their summary is
`/workspace/scratch/previous-command-repeat-release/final-regressions-v1.json`,
SHA-256 `3e56c00ca144755dcd39f86a62810e2e4ace7b49a21056ab0fa2874bfd9ee1af`.
The later freshly generated target source must match this complete inventory;
identity in a mock is not substituted for target-image evidence.

The first clean compile/link at local checkpoint
`24a31d3e0efce0e4365aaf79f05161cf78943bee` succeeded and passed the new target
source/object/ELF/DWARF and streaming checks. Its complete release chain then
refused an inherited right-modifier predicate that still looked for modifier
parsing directly in `Compiler::statement`; that handler now resides in
`Compiler::statementImpl`. This is an expected handler-location integration
change, not a reason to omit the predicate. The additive verifier advances only
that exact frozen-unit function expectation, keeps all 190 assertions, and also
checks modifier calls in the reachable new implementation. The partial first
build and failure receipt remain preserved. A new local checkpoint and fresh
clean build are required; no post-compilation exception or guard relaxation is
used to approve the earlier context. Production source bytes remain unchanged.

## Review package and owner boundary

The new Mac ZIP must bind the exact newly built image and committed source,
retain guarded Bash 3.2/Python 3.8/esptool 4.12 tooling, and pass fresh extraction,
offline preflight and mock-installer checks. Without owner-specific device
metadata, `plan_ready`, `installation_authorized` and `hardware_access` remain
false and `selected_write_ranges` remains empty. Preparation must not call a
real installer/device path.

The exact older rollback is **1,413,200 bytes**, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
Its bytes remain unchanged. It is an older source/text-v2 standalone application
without newer privacy/dashboard/editor repairs, not a full-device/filesystem
restore. The e825 editor image is not a known-good recovery substitute.

Future separately authorized owner checks use the existing benign TextEdit
fixtures: `T05R:xxxx:DONE` plus newline for standalone, `T05I:xxx:DONE` plus newline
for inline, and first-line REPEAT rejection at line 1/code 14 with blank TextEdit.
Record both actual text and matching request/status. Prior T00–T04/T06–T08 passes,
T05R Request 11 failure, T05W pass and T05I Request 14 pass remain scoped owner
evidence with their original limitations. Do not rerun that whole physical suite
automatically. H1 remains opt-in and experimental; canonical Hak5 scalar encoding
remains unresolved.
