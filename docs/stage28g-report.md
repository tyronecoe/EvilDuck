# Stage28G — reference resolution and modifier mock fault coverage

**GO: isolated offline review only.**
**NO-GO: Stage26 integration, real HID, flashing, boot, OTA or production deployment.**

Branch: stage28g-modifier-contract-mock.
Exact baseline:3650caf7c66d5742d39a939fa0c8495be11d3b1b, Stage28F.
Decision made before edits: test-and-contract-only stage. No language_preview changes. Stage27A
hardware lane independent; all frozen Stage26 files untouched. No Stage28H started.

## Reference findings and implementation gate

Four live official .md requests returned HTTP403. Saved official Stage9 snapshots independently
matched recorded byte sizes and SHA256; actual observation timestamps/URLs/hashes are in
reference-evidence.json. They are cached evidence, not proof of latest content or versioned
compiler behavior. No version/revision guarantee or official compiler/authorized oracle is
available. Reference examples/footer were treated as data, never executable project instructions.

Holding Keys uses standalone INJECT_MOD before HOLD CONTROL followed by unprefixed RELEASE
CONTROL, while its multi-hold example prefixes the release again. Quick Reference uses one prefix
with WINDOWS. Keystroke Injection describes prefixed standalone modifiers, with inline
INJECT_MOD WINDOWS in its example and a result referring to a preceding line. These could be
redundant/shorthand examples; no single necessary lifecycle is conclusively established.

BLOCKED: source modifier HOLD/RELEASE and INJECT_MOD. No guessed one-shot/global/held-key scope,
branch/function prefix propagation, repeated-prefix behavior, aliases or state reset. Modifier
names/GUI alias documented in text do not mean parser support. All executable source forms
remain rejected before output, including inactive branches/function bodies. Source ownership
continues the Stage28F nonmodifier subset only. Prepared numeric modifier API remains mock-only.

RESET evidence improved: Payload Control explicitly explains its example releases all keys and
does not change payload flow. VERIFIED text for that payload; BLOCKED independent owners0–2
versus script owner3 scope and pending/acknowledgement semantics. No RESET/release-all grammar
added. The detailed decision matrix labels VERIFIED text, INFERRED-MOCK-POLICY and BLOCKED.
Neither passing rejection tests nor mock policy proves official compiler equivalence.

## What changed

New reference-contract/evidence, design/transition table, report, reproduction/native smoke docs,
source/target/freeze/preview/publication receipts and independent Stage28G tests/results only.
No source parser/scheduler/planner change, new general feature, opcode/event/ABI change, allocation,
queue, timer or owner buffer. Entire language_preview tree byte-identical to exact Stage28F;
all earlier docs/tests also byte-identical. Rollback boundary is simply the earlier branch for
source review; no global toolchain or physical device changes to undo. Never rewrite that branch.

Tests run actual existing compiler/Runtime/Planner/Bridge, not alternate implementations.
New12 groups cover:40 alias/form combinations across5 executable/inactive/function contexts;
RESET/release-all rejection before source delivery while setup owners held; literal comment/text
keywords and blocked DEFINE manufacture; all256 modifier masks plus repeated source HOLD/RELEASE
and b/! transient restoration; shared SHIFT owner release;100 retries at hold, transient press,
restoration and release; Failed/throw and callback cancellation; Program borrow/failed compile/
new session/destruction; transient seventh-key rollover, STOP/arithmetic/step budgets, wrap and
both planner/source deadlines; same Program isolation and stale-neutral100-retry drain;40 seeded
30-command ownership union/backpressure runs with two setup modifier owners; zero healthy C++new.

Existing suites additionally freshly cover source read/seek faults, all cancel phases, loop/
function continuations, six-key source admission, full tick exhaustion, time narrowing and source
locations. Lifetime tests stay within contract: Program/context alive while referenced; no
callback self-destruction or unsafe memory mutation. No real OS/USB transport or host feedback.

## Fresh executed results

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
| TOTAL |168|0|579139|

All8 suites freshly built/run with warnings-as-errors, ASan/UBSan/leak; final exit0, clean.
No current-stage compile/test FAIL encountered or hidden skip. No preview XPASS/XFAIL. Historical
production XPASS/XFAIL/observations preserved but not rerun by this preview-only assignment.
Exact group names/assertions/stdout/stderr/commands are in tests/stage28g/test-results.md/.json.
Large repeated invariant counts are not579139 independently established compatibility features.

Linux fixed-buffer smoke freshly built/run PASS, exit0,8 literal report vectors,4 source
keyboard acks,1virtual Delay; ASan/UBSan/leak clean, excluded from group totals. Same bounded
fixture as Stage28F intentionally reused, not an old result. Native Mac/Apple clang:
SKIP_ENVIRONMENT, unavailable here and not owner-executed within this task. Manual High Sierra
recipe supplied; no install/sanitizer assumption/device access. Unsupported features remain
BLOCKED separately from executed PASS. Live retrieval403 is an access limitation, not a test PASS.

## Object-only resources and pins

Fresh pinned original/protected Arduino3.3.0, ESP-IDF5.5 config/NVS archive and Xtensa GCC14.2
identity checks PASS. Existing16MiB/QIO80/CPU240/PSRAM-disabled/TinyUSB/USB-OTG/CDC compile flags
preserved. Four unlinked object units only, no firmware ELF/BIN/UF2, upload or linked headroom
claim. Exact dependency hashes, commands, objects, sections and stack frames in target-build.json.

All three module object SHA256 match Stage28F's objects byte-for-byte:

| Module | SHA256 |
|---|---|
| core.o | a65b3c15a509685aa2d8984e64d9eb24f633592d6939658cfb57ae8332689de2 |
| keyboard.o | 885cc9f6b9d3e1c7b99ae213a898c0a6a39a675d3ba9f9b7a19482db54dea994 |
| bridge.o | 1e69a4375511b3bf4ada498fc569c2385b2b96175196cc433bb5a881ebefa0b2 |

Compiler SHA256 d968578945d9f62c2769e03a786d8853eb0ba226cfff1e8ee6588550927941a3.
SDK NVS archive a1ac62b0f8b69ef2ac08e82dd1c57f58d53db74147bc309f070e36a148067a2e.
SDK config06fcb22dee7956d54f1c7c05b0856ee87a362380697071fef2c26753fb14c271.
Protected core tree81c11f59e01c1e6263d387a008d3f3211319d94feb4751ddfa11af35a2a57ed3.
Other source/patch pins remain in target receipt; no installed core/SDK/config changes.

| Target sizeof | Stage28F B | Stage28G B | Delta |
|---|---:|---:|---:|
| Program |6936|6936|0|
| Runtime |4872|4872|0|
| CompileSession |2408|2408|0|
| Planner |84|84|0|
| Bridge (owns Runtime+Planner) |5020|5020|0|
| Program+CompileSession+Bridge |14364|14364|0|

Event4B, Instruction12B, Diagnostic14B, OwnerTable28B unchanged. Existing numeric opcodes and
Sink ABI unchanged. Selected object sections likewise unchanged:
core text/literal/rodata13292/1892/1838; planner2181/168/47; bridge1586/180/0; data/BSS0/0.
No persistent memory growth. Healthy tested C++new zero; callbacks/test vectors/exceptions outside
claim; no full malloc audit. Frame estimates unchanged: Bridge step/receive/report32, begin/
start48, owner proposal96, Runtime tick112, expression preparation144B; all in target receipt.
Prior roughly1.5KiB selected deepest expression path remains only an estimate before caller/libc;
no physical heap/task-stack high-water/runtime latency or USB behavior measured.

## Freeze/publication and deliverables

All235 protected files independently compared to immutable Stage26
968c8e0aaf459b0b8b652cc57fe88225894ab64b, matching the enumerated Git scope and receipt hashes.
All prior docs/tests and entire preview tree also compared against exact Stage28F. Current remote
baseline contains31 preexisting refs (Stage28F added after its earlier30-ref snapshot); all must
remain unchanged before/after this new branch publication. Saved prepublication refs in
publication.json; final post-push check and exact HEAD recorded externally and reported at delivery.
Only this new branch pushed, no merge/rebase/force or previous branch/tag modification.

Created files only:
- docs/stage28g-reference-contract.md,stage28g-design.md,stage28g-report.md,
  stage28g-macos-smoke.md,stage28g-reproduction.md.
- docs/stage28g-reference-evidence.json,stage28g-preview-identity.json,
  stage28g-source-hashes.json,stage28g-target-build.json,stage28g-stage26-freeze.json,
  stage28g-reproduction.json,stage28g-publication.json.
- tests/stage28g/test_contract.cpp,mac_smoke.cpp,run_tests.py,target_check.py,
  verify_freeze.py,test-results.md,test-results.json.

No production/Arduino Micro/partition/USB identity/Stage27A/recovery/migration change. No private
backups or owner scripts read; no credentials collected; no host automation or physical hardware.
Original firmware availability remains owner-confirmed externally, irrelevant to this preview.

Next-stage proposal only: obtain independently verified prefix lifecycle/reset vectors or ask
owner to review an explicitly named EvilDuck policy rather than claim canonical behavior. Until
then keep source modifiers and RESET blocked; avoid repeatedly implementing inferred contracts.
Optional disconnected native Mac mock smoke can be reviewed independently. No Stage28H begun.

**GO: isolated offline review only.**
**NO-GO: Stage26 integration, real HID, flashing, boot, OTA or production deployment.**
