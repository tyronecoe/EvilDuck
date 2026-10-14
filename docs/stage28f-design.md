# Stage28F mock ownership architecture and transition table

The command contract precedes implementation. Two appended opcodes and EventType values keep
original numeric values, Instruction12B/Event4B/Sink signature and all memory bounds unchanged.
Both compiler passes preserve Stage28B lexical modes. Existing operand DEFINE expansion runs
before exact single-token key selection. Invalid syntax is rejected before ready publication;
rollover/held-tap collisions depend on runtime union state and are runtime-only errors.

Runtime executes one ownership instruction into its existing pending Event. Retry does not
advance pc or a suspended function frame. Bridge reserves owner3 only for Programs containing
ownership instructions; bounded scan<=128 IR entries at start, not a new compiler table. Older
Programs may use all four setup owners unchanged. An occupied script owner rejects start in
Prepared, before borrowing/starting Runtime, and can be released through existing Prepared API.

Planner confirmed ownership uses the same bounded proposal/copy/snapshot and six-key checks as
existing ownership. The new confirm flag queues the union in Held phase even when already equal
to lastAccepted. Existing hold/release APIs retain their original no-op deduplication. No heap,
queue, new report buffer, frame, timer, user variable or owner table. Bridge admits once, Waiting
until current Held report acceptance, then Ackable; next matching pending Runtime callback
acknowledges once. The next identical command requires a separate fresh report acceptance.
Transient events still require press AND restoration. Delay still belongs solely to Runtime.

| Trigger | State / report | Ack / terminal effect |
|---|---|---|
| Initial sync | Syncing, pending zero | Prepared only after accepted current sync |
| HOLD key | Runtime pending -> Waiting, proposed union/Held | No source ack at logical admission |
| Repeated HOLD / absent RELEASE | Same union but fresh Held action | No reuse of earlier report acceptance |
| Selective RELEASE | Remove only owner3 claim; other owners remain | Union still includes shared key if another owner holds it |
| Occupied owner3 at source start | Prepared rejection PlannerRejected | Runtime stays Idle; setup state unchanged |
| Transient held usage / seventh key | Reject proposal, original source Failed | Error line retained; no partial proposal/report |
| Held report Retry | Waiting, same pending bytes | No ack, replay or following command |
| Held report Accepted | Ackable | Next owned Runtime tick acknowledges exactly once |
| Held sink Failed / throw | Failing then Runtime SinkFailure | First event, Held phase, planner reason and physical line snapshot |
| Deadline / attempt exhaustion | Planner fail or original Runtime timeout first | No ordinary action follows |
| Cancel before/after acceptance | Runtime Cancelled, intent cleared, owners logically empty | Accepted evidence retained; no fabricated source ack |
| Callback cancel + Accepted | Actual union snapshot recorded even after cancel | No ordinary source progression; release may remain required |
| Callback cancel + Retry / Failed / throw | Prior evidence / uncertainty retained | Never manufacture accepted release |
| STOP / arithmetic / step failure | Cancelled / Error | Clear logical owners, preserve nonneutral accepted report |
| Completion | Completed, owners logically cleared | No auto neutral report or destructor transport |
| Explicit drain | Terminal -> Draining, zero only | Return original terminal only after current drain action leaves Working and neutralConfirmed |
| Drain Retry / fault / budget exhaustion | Still Draining or Error | Earlier neutral cannot finish current drain |
| Restart | Requires terminal + neutral evidence, then new sync | In-place Runtime reset; no stale intent, variable or ack |

Bridge guards source window, report reentry and driver recursion unchanged. First diagnostic stays
stable across drain faults; live Planner getters describe later cleanup faults. One step advances
one Runtime turn OR at most one report attempt. Budgets remain10000 instructions/100000 ticks/
30000ms, Planner256 attempts/30000ms; callers may narrow only. No blocking delay or wall-clock API.

Program and report-context lifetime contracts remain Stage28E's; single-thread only. Original
Program must outlive all Program-dependent observations until a successful begin/destruction.
Caller callbacks must return promptly; self-destruction/cross-thread/memory corruption is outside
boundary. A standalone Sink receives new Hold/Release types and must implement or reject them;
source Sink struct ABI unchanged does not imply old binary exhaustiveness handling.

Modifier commands and release-all are blocked, not guessed. Completion/cancel logical cleanup
is not a physical release. No OS/USB endpoint, descriptors/report IDs, locale, lock feedback,
transport detach/reconnect or host typematic claim. Stage27A hardware lane remains independent.
