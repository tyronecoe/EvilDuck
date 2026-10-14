# Proposed report/action contract — SPECIFICATION ONLY

No interface below is executable, implemented, owner-approved or connected to USB. It describes the D01–D06 proposal for a possible separately authorized synthetic Stage28K. Existing Bridge/Planner APIs and Stage28H fixtures remain unchanged; fixture PASS is a memory-only baseline, not a device oracle.

## Identity, evidence and bounded ownership

One serialized owner drives one Bridge. Planner is the only authority for its four ownership records, modifier bitmap and six distinct nonmodifier union. Owner 3 is the script owner; owners 0–2 are pre-session mock setup, not concurrent live firmware clients. Setup authority cannot mutate ownership while source Runtime executes. Union is sorted; shared claims do not duplicate a key. A transient tap of an already held usage and a seventh distinct key reject atomically. Source modifier HOLD/RELEASE, INJECT_MOD and RESET remain BLOCKED.

**PROPOSED CHOICE:** introduce a wrapper-only synthetic journal identity `(S,E,R)`: S is session, E is source intent, R is one snapshot action. Use fixed-width unsigned 64-bit monotonic counters, never wrap/reuse; exhaustion rejects a new session/action before admission. Session allocation has a single lifetime owner; reconstructing it while retaining old callbacks is prohibited. These counters are not present in current Bridge. A future implementation must justify their storage in its ledger.

At most one R is outstanding. A tap has two sequential actions: press R1 and restoration R2, same E; ownership change has one R; sync and drain have R but no E. Different actions with identical eight bytes still have different R. Retry preserves S/E/R/bytes and does not readmit ownership, consume a source event or increment source acknowledgement. Frozen snapshots cannot alias a mutable driver buffer. Delay has an E but no report R.

Evidence levels are distinct:

| Evidence | Meaning | Does NOT prove |
|---|---|---|
| API invocation / source admission | Intent entered the current scheduler | Report accepted, queued or delivered |
| Proposed mock Accepted | Current immutable R copied into a bounded synthetic journal exactly once; future copies/capacity are specified, not dynamic or unbounded | USB queue, transfer or host input |
| Actual queue admission | Real driver reports admission under independently reviewed ownership/copy semantics | Completion, host receipt or interpretation |
| Optional correlated completion | Independent token ties a real completion to current S/R | OS key state or TextEdit output |
| Host observation | Separately authorized physical host evidence | Delivery of a different, disconnected or stale action |

D02 selects only mock Accepted. The journal cannot silently discard a record on capacity exhaustion: fail closed before accepting it. Its future exact capacity must cover the authorized finite fixture or explicitly stop before overflow. No ring overwriting is assumed.

Do not call the current Sink again after returning Accepted for R. Press acceptance allows only the next restoration action; source E is acknowledged once only after all its required report actions are accepted and the Runtime next attempts that same E. Ownership admission versus acceptance is recorded separately. A successful `tud_hid_n_report` call is **not proven physical delivery**. Correlated-completion mode is an unselected alternative requiring a separate contract: if later selected, submission and completion must be separate states and a queued action must not be retransmitted merely because completion is pending. Never retrofit that interpretation into Accepted here.

## Finite-state transition proposal

These are wrapper specification states, not renamed current Bridge enums. NVS/USB/device state is not accessed. `ZERO` means `00 00 00 00 00 00 00 00`. Current-action receipts are explicit, not inferred from `lastAccepted()` equality.

| State / event | Required checks | Next state / effect | Acknowledgement evidence |
|---|---|---|---|
| Idle / begin S | Valid context/budgets; no old undrained session; unique S | SyncPending with fresh ZERO R | None |
| SyncPending / Retry | Current S/R; prompt callback | Same bytes/identity; one bounded attempt | None |
| SyncPending / Accepted | Current R copied exactly once | Prepared | Sync receipt only, not E |
| Prepared / start ready Program | Stable Program/context; reserved script owner available | RunningIdle | No report or source ack merely from start |
| RunningIdle / report-bearing E | No pending R; valid usage/union; current E | ReportPending R1; admitted E once | None |
| ReportPending / Retry | Current R immutable; below deadlines/attempt limit | Same state | None; no duplicate admission |
| ReportPending / Accepted press | Current R1 | ReportPending restoration R2, same E | R1 receipt only |
| ReportPending / Accepted ownership or restoration | Current final R | Ackable E | Final receipt; E not acked until source retry |
| Ackable / Runtime retries same E | Current intent matches and not cancelled | RunningIdle; acknowledge E once | One source ack; same bytes of a new E cannot reuse this receipt |
| RunningIdle / Delay E | No pending report work | Runtime records Delay acceptance at that tick; waiting until elapsed | Delay ack only, no report receipt |
| Any active state / cancel or terminal STOP/error/completion | Serialized terminal event; no callback invoked recursively | TerminalUndrained; future E discarded, logical claims cleared | No implicit neutral/host release claim |
| TerminalUndrained / request explicit drain | No report call in progress; sink/context still valid | DrainPending, fresh ZERO R | Prior accepted ZERO is not this R's receipt |
| DrainPending / Retry or known queue refusal | No admission at proposed boundary | Same pending R until bounded deadline | Host state remains UNKNOWN; restart denied |
| DrainPending / Accepted | Current R; no stale receipt | TerminalDrained | Mock current neutral receipt only |
| TerminalDrained / new begin | Unique next S, no pending old callback/work | Fresh SyncPending for new S | Previous drain proves only chosen mock boundary |
| Any pending state / Failed, exception, unsupported enum or timeout | Latch first diagnostic and phase | TerminalUndrained; abort future source work; explicit drain can be requested later | No fabricated acceptance; neutral status uncertain |
| Any state / stale completion | S/R wrong, obsolete or cancelled | Ignore for ack; bounded diagnostic/uncertainty record only | Cannot resolve new R or restart barrier |
| Any state / reentrant begin/start/step/ownership/drain | Callback currently executing | Reject mutating request or suppress nested step; finish current serialized operation | No nested report/admission/ack |
| Any active state / disconnect or ambiguous submission | Physical variant not selected; inject only a mock failure | TerminalUndrained with uncertainty; later reconnect itself is not acceptance | Requires current fresh drain plus next sync at chosen boundary |

The unchanged Bridge allows `cancel()` during a callback, while guards reject several other operations. The proposal serializes externally requested cancellation until the callback returns; cancellation has priority over source acknowledgement. A callback's return can establish acceptance of an already offered R even if cancellation was requested, but cannot resume/ack cancelled E. This is a wrapper policy to test later, not a new thread-safety claim about Bridge.

All clocks are caller-supplied uint32 ticks. Keep unchanged ceilings: Planner 256 attempts/30,000 ms; Runtime 10,000 steps/100,000 ticks/30,000 ms; compile 65,536 steps. Check `uint32(now − since) >= limit`, including equality. Require intervals within current small ceilings and no sampling gap of a full uint32 clock cycle; such a gap is outside the assumed clock contract. A small wrap works; arbitrary backward clocks are invalid. Runtime's total timeout can end a long Delay before its per-event duration; never widen a limit to hide that. Delay starts once on its source Accepted tick; no com default-delay/jitter/5 ms dwell is added. One step attempts at most one report or advances one Runtime tick; never spin on Retry.

## Tabletop traces — all SPECIFICATION-ONLY, not new executed tests

Eight-byte abbreviations: Z=ZERO; A=`00 00 04 00 00 00 00 00`; B=`00 00 05 00 00 00 00 00`; AB=`00 00 04 05 00 00 00 00`; ShiftA=`02 00 04 00 00 00 00 00`. Setup events are not canonical modifier source syntax. Each row assumes fresh sync was accepted unless stated otherwise.

| Trace | Proposed transitions | Expected snapshot / acceptance / ack evidence |
|---|---|---|
| T01 fresh identical source HOLDs | E1 HOLD a: pending→accepted→ack; E2 HOLD a follows independently | A/R1 and A/R2 both freshly Accepted; admissions=2, acks=2. R1 cannot ack E2 |
| T02 shared-owner selective RELEASE | Prepared owner0 claims a; script owner3 HOLD a then RELEASE a | A persists on both script actions, fresh receipts each; owner0 survives selective release. Terminal cleanup separately clears all logical setup claims |
| T03 transient conflicts with held usage | After HOLD a accepted, source tap a | HeldTap rejection before transient admission; no fake key edge/report. Terminal error requires explicit drain |
| T04 seventh distinct key | Six union keys claimed; next HOLD seventh | Rollover rejects without partially adding key or accepting E; prior snapshot remains historical, cancellation clears logical claims |
| T05 press Retry and restoration Retry | E tap a → R1 A Retry Retry Accepted → R2 Z Retry Accepted → ack | Attempts=5, report receipts=2, admissions=1, acks=1; retries reuse bytes/identity; press alone cannot ack |
| T06 Delay after acknowledgement | E1 tap has both receipts and ack at t; E2 Delay 5 accepted at d≥t | No report for E2. No next command before elapsed 5 at d; Delay accepted once, not measured from press submission |
| T07 cancel before acceptance | R1 A Retry; cancel before next attempt | No further A attempt/source ack; terminal clears owners; fresh drain Z/R2 must be Accepted to permit proposed restart |
| T08 cancel after press accepted | R1 A Accepted; cancel before restoration accepted | Source ack=0; do not emit old restoration as live source work. Drain is distinct Z/Rnew; late R1 evidence cannot acknowledge cancelled E |
| T09 cancellation at callback return | Callback offers R and queues cancel request then returns Accepted | Record R receipt if valid; serialize cancellation before Runtime ack; source ack=0; no reentrant report; new drain required |
| T10 old session completion | S1 cancelled; S2 cannot begin before S1 drain; later old R completion arrives | Old completion never satisfies drain/new sync/current source ack, even when bytes are ZERO; diagnostic bounded |
| T11 queue refusal and disconnect uncertainty | Pending press refusal means Retry only if known not admitted; inject disconnect failure | No guessed success/retransmission after ambiguous admission; terminal uncertain; reconnect alone cannot show keys released; fresh drain required |
| T12 historical zero is not current drain | Z accepted during earlier sync/restoration; terminal then explicit drain Z/Rnew returns Retry | Remain DrainPending despite `lastAccepted` Z; only Rnew Accepted permits barrier. Mirrors intent of Stage28H stale-zero fixture |
| T13 planner attempt timeout | Same R retries 256 times, next step checks exhausted budget | TerminalUndrained/Attempts without 257th sink call; no source ack or false neutral |
| T14 elapsed wrap | R queued at 0xfffffff0, limit=32; Retry at 0x0000000f, next at 0x00000010 | Elapsed 31 permits attempt; elapsed 32 fails before callback. This is a small-wrap example, not wall-clock evidence |
| T15 callback reentrancy | While R offered, request nested step/start/HOLD/drain | No nested report or changed ownership. Invalid requests reject; nested step no-ops; current valid acceptance handled once |
| T16 restart barrier | Terminal drain Retry, begin requested; drain then Accepted, next begin sync Retry | First begin denied. New session remains SyncPending until its own Z receipt; neither reconnect nor previous drain can ack new sync |
| T17 unsupported source / failed preflight | INJECT_MOD or RESET, malformed expression, oversized source | No Program ready/session start or source callbacks; diagnostics with physical location, zero report attempts from rejected Program |
| T18 prepared modifier with transient text | Prepared owner0 holds SHIFT; source character a then restoration | ShiftA press, `02 00 00 00 00 00 00 00` restoration; ack after both. No claim about resulting OS case or supported source modifier syntax |

These expectations are reviewable proposals informed by `keyboard.cpp:29–83`, `bridge.cpp:15–92`, `core.cpp:415–477` and Stage28H fixtures. No IDs, transport callbacks, restart wrapper or asynchronous handoff were implemented. Future Stage28K must explicitly distinguish its new synthetic ledger assertions from existing fixture counts and reject any contract contradiction rather than change old expectations.
