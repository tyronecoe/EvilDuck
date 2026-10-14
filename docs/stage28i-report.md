# Stage28I read-only integration readiness and host-validation gate

**GO: offline static audit review and optional disconnected owner host smoke only.**
**NO-GO: Stage26 integration/modification, production adapter, real HID/USB, firmware ELF/BIN/UF2,
physical flashing/boot/OTA/upload/deployment. No Stage28J started.**

Exact base `28857c2b1895f96a8e29c5fd69a69495237a1347` (Stage28H), clean HEAD verified before edits.
Delivery branch stage28i-integration-readiness-audit is created only after deliverables/checks
are ready. Stage27A physical lane is entirely separate, unchanged and owner-controlled.
All existing source, tests, reports, dependencies, partitions and profiles remain unchanged.

## Executive outcome — NOT a drop-in integration

Actual source inspection establishes a concrete interface inventory and 19-seam gap matrix.
The production APIs are duckscript/com/hid_backend, not a guessed duckyscript or keyboard module.
Initial filename probes found no guessed filenames; actual rg file discovery located and verified
all required real interfaces. No required source architecture is inaccessible.

Answered by source evidence:
- Preview emits typed Events into a Bridge that owns Runtime+Planner; transport callback gets
  mock snapshots, NOT source commands. The backend has no equivalent public verbatim snapshot sink.
- Firmware beginReport merges a single backend persistent ledger. Four preview owners/selective
  release and fresh idempotent source acknowledgement are not its existing semantics.
- com admission, raw transport enqueue, shared completion semaphore and actual host delivery are
  different evidence levels. Merely returning true from a public helper is not adequate mapping.
- Preview explicit neutral drain differs from production automatic cancel/update clearing.
- Source/IR bounds, scheduler budgets/timing, arithmetic and locale/extension behavior differ.
  Numeric example source analysis: 65535+1 wraps to 0 in production versus preview Arithmetic error;
  this is a deliberate-policy mismatch, not a newly executed production/runtime bug claim.
- Startup controlled/safe/legacy paths, checked settings, web/CLI and app-only OTA surfaces are
  independently located; no path is entered or firmware change made.

Still BLOCKED/UNKNOWN:
- Native High Sierra 10.13.6 Apple compiler/stock Bash smoke: **NOT TESTED / PENDING OWNER**.
- Chosen report authority, source acknowledgement boundary and per-action/session correlation,
  async request serialization, protocol/descriptor behavior and peak integration placement budget.
- Actual linked TinyUSB transfer/copy/refusal/complete side effects and host interpretation,
  current physical installed profile/layout, USB/CDC/MSC behavior, runtime latency/heap/stack.
- INJECT_MOD/modifier-source lifecycle and RESET independent-owner scope; no canonical oracle.
  Existing production engineering policy does not independently resolve these preview gates.

The raw queue path always passes keyboard report ID while core wrapper has conditional boot-ID
normalization. This is CONFIRMED route divergence; actual protocol depends on first constructors/
configuration/host negotiation, UNKNOWN here. Do not label it a demonstrated physical defect,
change descriptors or treat its conditional branch as proof of currently negotiated boot mode.
No full linked constructor/callback callgraph or physical transport test was undertaken.

## Reviewable next steps, not authorizations

Gate A: owner runs unchanged Stage28H kit disconnected; native platform/compiler and exact exit/
trace evidence required. Gate B: peer review chooses ownership, ack/protocol/callback, threading,
source capacity, numeric/locale/extension scope and memory ledger. Gate C: separate owner-approved
non-device mock contract/harness only; NOT implemented or authorized now. Gate D: separate explicit
approval before considering integration design and independent supervised physical plan; physical
execution needs its own later authorization. All in stage28i-gated-roadmap.md.

Owner can run from unpacked root, EvilDuck UNPLUGGED:

```sh
bash tests/stage28h/run_host_smoke.sh
```

Existing 365-assertion/3-trace/19-vector/4-zero-callback-negative kit unchanged, available and
exercised in fresh Stage28H suite on Linux. No new Mac runner or owner-machine automation.
Only sanitized platform/compiler/exit/relevant diagnostics requested, no credentials/backups.
No owner native output has been supplied; neither Linux PASS nor static review marks gate A PASS.
Stock recovery resource availability stays OWNER CONFIRMED EXTERNALLY, not a download/search
blocker. Recovery/artifact/physical authorization belongs to the independent deployment lane.

## Fresh actual tests and environment

| Suite | PASS groups | FAIL | Assertions |
|---|---:|---:|---:|
| Stage27B |25|0|2543|
| Stage28A |23|0|526|
| Stage28B |26|0|4733|
| Stage28C |17|0|390573|
| Stage28D |21|0|14989|
| Stage28E |24|0|109591|
| Stage28F |20|0|18419|
| Stage28G |12|0|37765|
| Stage28H |19|0|483|
| TOTAL |187|0|579622|

All 9 published runners freshly compiled/executed with original expectations, fresh external
outputs, warnings-as-errors and ASan/UBSan/leak for applicable C++ paths; completed exit 0.
No new runtime suite or inflated group/assertion count. Exact names, commands/stdout/status are
in stage28i-test-results.json, with project path redacted. Intentional synthetic failures/ENV
skips in Stage28H are verified classification checks, not real feature passes. No preview
XPASS/XFAIL; historical production diagnostics unchanged and unrerun by preview-only assignment.

Native Mac cloud SKIP_ENVIRONMENT, owner gate PENDING. No runtime test or source defect encountered; a documentation JSON-builder quoting error was
corrected and checked (not a runtime test failure).
source lookup discovery corrected initial nonexistent assumed filenames/dependency include path
through actual inventory, not by adding fake interfaces. No stop condition requiring unsafe fix.
Host tools observed Python 3.12.14/GNU Bash 5.2.37/Debian GCC 14.2.0-19. No tool installation/config
change. Existing cloud setup reused. Audit-only checker separately validates exact source spans
and scope against Git, not another compatibility test; static counts in its receipt.

## Object-only resources and provenance

Existing pinned check actually ran: Arduino 3.3.0/ESP-IDF 5.5/Xtensa GCC 14.2,16MiB/QIO80/CPU240,
PSRAM disabled, existing USB-OTG/TinyUSB/CDC flags. Original/protected core, compiler and SDK
pins pass. Four unlinked objects only; no linked firmware image or production memory measurement.
core/keyboard/bridge object SHA256 and selected sections identical to Stage28H; exact source/
dependency/object hashes and frame metadata in stage28i-target-build.json (project paths redacted).

| Target object storage | Bytes | Delta from Stage28H |
|---|---:|---:|
| Program |6936|0|
| Runtime |4872|0|
| CompileSession |2408|0|
| Planner |84|0|
| Bridge (contains Runtime+Planner) |5020|0|
| Event / Instruction |4/12|0|

Program+CompileSession+Bridge = 14,364 B is only these objects, NOT a complete integration RAM budget.
Do not add contained Runtime/Planner again. Existing firmware contexts, source buffers/reader,
UI/tasks, allocation peaks and compiler stack need separate future evidence. No available OTA/
heap/stack high-water/latency predicted. All original opcodes/Sink ABI/ownership/ceilings unchanged.
Selected text/literal/rodata core 13292/1892/1838, planner 2181/168/47, bridge 1586/180/0 and data/BSS 0/0
unchanged. Existing selected Runtime tick 112/expression 144/ownership 96/Bridge step 32 B frames
unchanged; not complete task-stack proof. No newly measured zero-malloc claim.

## Integrity, scope and delivery inventory

235 protected Stage26 files independently compare to immutable Git
968c8e0aaf459b0b8b652cc57fe88225894ab64b; inventory derived from Git by unchanged freeze verifier.
All preexisting tracked files additionally checked byte-identical to Stage28H by new static audit;
new paths restricted to stage28i docs/tests. Exactly 40 source spans (35 repo +5 dependency) carry
file/span hashes and line coordinates, enabling drift detection without emitting source contents.
No private original images, owner scripts, credentials, real device or OS injection accessed.
No Arduino Micro/core/SDK/partition/USB identity/startup/settings/update/migration change.

Only added files:
- docs/stage28i-report.md,stage28i-readiness-matrix.md,stage28i-gated-roadmap.md,
  stage28i-reproduction.md.
- docs/stage28i-source-evidence.json,stage28i-readiness.json,stage28i-test-results.json,
  stage28i-target-build.json,stage28i-stage26-freeze.json,stage28i-static-audit.json,
  stage28i-source-hashes.json,stage28i-publication.json.
- tests/stage28i/audit_sources.py.

Before/after publication compare all 33 preexisting remote refs, including exact Stage28H head;
only new stage28i-integration-readiness-audit added, no force/merge/rebase. Final SHA/post-push
verification recorded at delivery and externally, prepublication snapshot in publication receipt.
Only Git publication/integrity operations use network, no HTTP/oracle/payload/telemetry operations.

**GO: review static audit and optional disconnected owner smoke.**
**NO-GO: integration/adapter implementation, real HID/USB, firmware images, flash/boot/OTA.**
No Stage28J or future C/D implementation started. Await owner review/native evidence.
