# Stage28K limits and next review gates

**GO: review the actually executed synthetic-only D01–D10 harness and T01–T18 evidence.**
**NO-GO: Stage26 integration, production adapter/ledger, real HID/USB/OS input, enumeration, firmware images, flash, boot, OTA, autorun, settings/storage changes or Stage28L.**

All T01–T18 have actual PASS evidence; none is merely tabletop modeled or a blocked trace relabeled PASS. The source engines and all prior tests/reports remain unchanged. Explicit owner approval is for this synthetic milestone only.

| Boundary | Established here | Still missing / next decision |
|---|---|---|
| Current action and source identity | Admission/ack counter deltas plus Planner phases; immutable Retry; once-only journal acceptance; exact byte fixtures | No raw next-Event/opcode hook. Conservative pre-tick E-capacity guard can stop a non-event tick at exhaustion; review this policy before any relaxation |
| Neutral and cancellation | Fresh current zero record gates restart; old zero and notices cannot substitute; callback cancel deferred before source ack | Only mock-boundary neutrality. Actual host release, reconnect delivery and transport state UNKNOWN |
| Completion | Arbitrary old/current/duplicate completion inputs cannot manufacture a receipt | Every notice is diagnostic only. Actual linked queue/copy/transfer semantics and token correlation remain unselected/unverified |
| Threading | One test driver owner; eight requests; priority cancellation; reentrant calls rejected | No real threads, interrupts, RTOS handoff, lock ordering, web/CLI/USB concurrency proof |
| Memory | Fixed non-overwriting 256 report / 128 intent / eight request storage; actual host/target sizeof; healthy C++ new probe | Synthetic Driver 34,032 target B is NOT a recommended firmware allocation. Production peak heap/task stacks/latency/OTA margin UNKNOWN |
| Lifetime | Persistent member objects; stable synthetic Reader/context; cancel/destructor cleanup tested under ASan/UBSan/leak | No immunity to caller freeing source/context early. Identity lifetime belongs to one Driver; rebuilding while retaining callbacks prohibited |
| Clock and progress | One report or tick per step; 256 attempt boundary; 31/32 small-wrap deadline; source Delay timing and runtime timeout | No backward/full-cycle sampling guarantee, real USB timing, dwell/jitter, scheduler fairness or physical latency measurement |
| Language | Old preview caps, checked arithmetic, US reference mapping, function STOP, rejected unsupported preflight | Source modifier HOLD/RELEASE, INJECT_MOD, RESET owner scope remain BLOCKED; production wrap/DE/Unicode/dead keys/interpolation/extensions not adopted |
| Native host | Owner-reported High Sierra E–H results/versions/explicit H exit recorded; cloud tests fresh | Stage28K itself not run on Mac; earlier native memory PASS does not validate board or USB. Mac leak detection disabled for E–G |
| Startup/recovery | No production entry, table/schema/service/arming changes; freeze and previous refs preserved | Physical profile, layout, recovery access, artifact installation and operation authorization remain separate owner gates |

## Recommended next choice, not automatic Stage28L work

Review this branch, especially the counter-delta association, conservative E barrier, per-Driver identity lifetime, finite evidence capacity, first-fault persistence and diagnostic-only notices. Accept or request precise changes based on these executed fixtures; do not infer a real adapter contract from the journal's Accepted label. If a future scope requires exact progress at exhausted E capacity, or true opcode/event interception, it needs a separately reviewed contract/API proposal, not hidden inspection of private fields or equal-byte inference.

A narrowly scoped future milestone could independently specify correlated transport observations and a firmware ownership/thread boundary as a **design**, using actual linked dependency evidence if separately authorized. It must not skip source subset, memory placement, profile/autorun, callback protocol, recovery and supervised physical-plan review. There is no authorization here to produce linked firmware or test a board. Owner-confirmed stock firmware availability is not a search/request blocker; recovery functionality is a distinct future physical question.

No action is performed on the owner's Mac. Do not request another E–H rerun merely to repeat the already reported native milestone. Stop for review; Stage28L has not begun.
