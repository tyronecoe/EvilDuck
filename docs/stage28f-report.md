# Stage28F — reference-backed mock ownership commands

**GO: isolated offline review only.**
**NO-GO: Stage26 integration, real HID, flashing, boot, OTA or production deployment.**

Delivery branch: stage28f-mock-ownership-commands.
Exact base: b23fc8b6bf8f5ff1deb5f0eb83abe7058d29eaa5 (Stage28E).
No previous branch/report/test expectation rewritten. Stage27A remains owner-controlled using
frozen Stage26. Original firmware availability remains owner-confirmed externally; no private
backup/device access, stock-firmware search or recovery work in this stage.

## Implemented subset and limits

HOLD key and RELEASE key now compile, preflight and execute in language_preview only.
Supported operands: lowercase a–z,0–9, ENTER TAB SPACE ESCAPE BACKSPACE DELETE UPARROW DOWNARROW
LEFTARROW RIGHTARROW. Exact uppercase command/named spelling. Existing bounded operand DEFINE
expansion, physical source lines, comment/text modes, conditions, loops and function continuations
are reused. No parser library, second expression evaluator, general owner syntax or runtime FIFO.

The saved authoritative Hak5 Holding Keys and Quick Reference specify these command forms and
letter/navigation examples; four official saved snapshots were SHA-256 rechecked. Reference URLs,
provenance and explicit decisions appear in command-contract/reference-evidence. No new latest-
documentation or independent official compiler-oracle claim. Cached examples were not executed.

BLOCKED: source modifier HOLD/RELEASE and INJECT_MOD pending exact prefix lifetime evidence;
RESET/release-all pending buffer versus independent-owner scope evidence. No guessed syntax or
bare RELEASE. Persistent SHIFT remains the prior Prepared mock API and is tested with source
ownership/transient text; it is not source modifier support. Idempotence and extra acceptance of
unchanged reports are documented mock policies where official edge semantics are unspecified.
No Unicode, DE, dead-key/host-lock/typematic, real endpoint, report-ID or USB claim.

## Architecture and acknowledgement

Two appended opcodes/event types keep all original numeric values and Event4B/Sink signature.
A standalone Sink must explicitly implement/reject these new types; struct ABI stability does
not mean an old exhaustive handler automatically supports ownership. Program ownershipCommands
scans at most128 IR entries. Programs containing ownership commands reserve script owner3; start
rejects occupied owner3 in Prepared without starting Runtime or mutating setup state. Older
Programs retain all four setup owners. Prepared owners0–2 can independently hold the same usage;
script release removes only its claim. Transient held-usage taps and seventh distinct key reject.

Planner confirmed ownership reuses existing atomic proposal/snapshot/rollover checks and queues
one Held report even when unchanged. Bridge admits one pending Runtime intent, returns Retry,
and waits for current Held report acceptance. Only then is it Ackable and the next owned Runtime
callback acknowledges once. Identical consecutive commands start distinct actions. Source taps
still require accepted press and restoration; Delay timing remains solely Runtime-owned.

One step performs one Runtime turn OR one report attempt. No additional field, table, dynamic
queue or report buffer. Source instruction/tick/elapsed caps10000/100000/30000ms and planner
256-attempt/30000ms caps remain, including narrowing, wrap and backpressure behavior. Fixed
Program/CompileSession/Bridge allocation is recommended; synchronous compile still has its
previous larger caller stack cost. Lifetime/reentrancy constraints and source error propagation
remain Stage28E's. Full transition table is in stage28f-design.md.

Completion/STOP/runtime error/cancel clear logical owners, not accepted evidence. Cancellation
inside a callback cannot erase a report actually accepted afterward. Sink failure retains the
first source event, physical line, Held phase and reason. Explicit drain remains separate, zero
only, and completes only on its current accepted action plus neutral confirmation. Prior neutral
evidence does not acknowledge repeated RELEASE or drain. Restart resets fixed Runtime storage
only after the existing neutral gate, then synchronizes again. No destructor report emission.

## Fresh executed verification

| Suite | PASS groups | FAIL | Assertions |
|---|---:|---:|---:|
| Stage27B |25|0|2543|
| Stage28A |23|0|526|
| Stage28B |26|0|4733|
| Stage28C |17|0|390573|
| Stage28D |21|0|14989|
| Stage28E |24|0|109591|
| Stage28F |20|0|18419|
| Total |156|0|541374|

All freshly executed with warnings-as-errors, ASan/UBSan/leak detection; clean final results.
Exact group names, assertions and stdout/stderr/compile commands are in new test-results.md/.json.
Previous runners and tests unchanged. No preview XPASS/XFAIL or skipped runtime suite. Historical
production diagnostic XPASS/XFAIL and observations preserved, not rerun or conflated with these
preview-only counts. Unsupported-command rejection is not a compatibility pass.

New coverage: every supported operand and exact Runtime event; malformed/inactive/callee syntax
preflight atomicity; DEFINE/BOM/CRLF/no-final-newline and literal modes; same-command fresh ack;
SHIFT plus independent owner/selective/shared release; occupied script-owner rejection and old
owner3 compatibility; hold across Delay/IF/WHILE/functions and numeric function continuations;
six-key boundary/seventh and held-tap atomic rejection;100 hold plus100 release retries;
cancel before/admission/acceptance/source-ack for hold/release; callback cancel Accepted/Retry/
Failed/throw; source-line/first-error snapshots; wrap/attempt/elapsed caps; STOP/arithmetic/step/
pending Delay cleanup; stale-neutral drain retries/failures/restart; borrowing/reentry;40 seeded
30-command union/backpressure runs; new-command reader read/seek/cancel atomicity; confirmed
owner API invalid/no-op/shared checks; zero C++new on measured healthy compile/runtime/planner/
bridge/drain paths. Prior suites cover shared sync/press/restoration/drain phase faults, stalled
clocks and repeated mutation boundaries unchanged.

Development check FAILs were fixture compilation errors: a BOM hex escape consumed DEFINE's
first hex digit; a compatibility test redeclared its legacy Program. Both corrected and rerun;
not runtime defects, not relabeled PASS. No essential unresolved failure. A shell chain's final
optional clang++ lookup returned1 after a successful smoke; independent smoke execution exit0
is recorded. Linux fixed-buffer smoke PASS with8 exact reports/4 keyboard acks/1Delay, sanitizers
clean (excluded from group totals). Native macOS/Apple clang SKIP_ENVIRONMENT; not available and
no owner-native results supplied. stage28f-macos-smoke.md is the manual offline High Sierra recipe.

## Object-only resources and provenance

Original/protected Arduino3.3.0 core, ESP-IDF5.5 config/NVS archive, Xtensa GCC14.2 and frozen
compile flags verified before four OBJECT-ONLY compilations.16MiB/QIO80/CPU240, PSRAM disabled,
USB-OTG/TinyUSB/CDC pins preserved. No firmware ELF/BIN/UF2 or production headroom measurement.
Final preview source hashes independently match object receipts. Exact hashes, compiler/source
flags, selected sections, undefined symbols and frame estimates are in stage28f-target-build.json;
source/test hashes are in stage28f-source-hashes.json. No global core/toolchain change.

| Target sizeof | Stage28E B | Stage28F B | Delta |
|---|---:|---:|---:|
| Program |6936|6936|0|
| Runtime |4872|4872|0|
| CompileSession |2408|2408|0|
| Planner |84|84|0|
| Bridge (includes Runtime+Planner) |5020|5020|0|
| Diagnostic (inside Bridge) |14|14|0|
| Program+CompileSession+Bridge |14364|14364|0|

Compiler internal2312B, Event4, Instruction12, Continuation516, CallFrame6, TextCursor14,
Report8/Owner7/OwnerTable28 unchanged. No writable global data/BSS added. Zero C++new observed
on tested healthy path; sink tracing/exception allocation and arbitrary user callbacks excluded
from that claim. No complete malloc accounting or physical heap/latency/high-water measurements.

| Selected unlinked sections | Stage28E text/literal/rodata B | Stage28F B |
|---|---:|---:|
| Core |13007/1856/1838|13292/1892/1838|
| Planner |2063/160/47|2181/168/47|
| Bridge |1476/160/0|1586/180/0|
| Writable data/BSS, all modules |0/0|0/0|

Selected code/literal total grows577B across objects; not linked firmware flash growth. No
production image built or slot headroom inferred. Bridge frames remain step/receive/report32B,
begin/start48B. Ownership proposal96B; new confirmed wrappers/ownerEmpty32B; Program scan32B.
Core tick112B and expression preparation144B remain; prior roughly1.5KiB selected deepest
expression path before callers/libc remains an estimate, not full callgraph task-stack proof.
Compiler stack/frame metadata is retained in target report, no recursive ownership execution.

## Freeze, publication and review

All235 protected files compare byte-identical to immutable Stage26 commit
968c8e0aaf459b0b8b652cc57fe88225894ab64b, independently enumerated from Git, not only receipt
trust. Production partitions/Arduino Micro/USB identity/migration safeguards unchanged. Prior
stage artifacts/docs/tests untouched. Before publication30 existing remote refs were captured
and compared; push only this new branch, never force or merge. Prepublication refs are in stage28f-publication.json; post-push comparison and new exact HEAD
verification must also pass before reporting delivery (external receipt plus final GitHub SHA).

Modified: language_preview/{core,keyboard,bridge}.{cpp,h} and language_preview/README.md.
Created: docs/stage28f-{command-contract,design,report,reproduction,macos-smoke}.md,
reference-evidence.json,stage26-freeze.json,target-build.json,source-hashes.json,publication.json;
tests/stage28f/{test_ownership.cpp,mac_smoke.cpp,run_tests.py,target_check.py,verify_freeze.py,
test-results.md,test-results.json}. Commit diff is the complete change inventory.

Stage28G proposal only: review exact modifier-prefix lifetime and RESET scope against an
independent reference before any source extension. Alternatively extend mock event-contract
fault testing; do not integrate production or start another stage automatically. Host/native
smoke may be performed separately with the device disconnected. No hardware permission follows.

**GO: isolated offline review only.**
**NO-GO: Stage26 integration, real HID, flashing, boot, OTA or production deployment.**
