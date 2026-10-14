# Stage28G design — contract and tests, no engine changes

Implementation gate: blocked prefix lifecycle and cross-owner RESET scope. No source feature
added. No new enums/opcodes, data field, Sink ABI, buffer, owner, allocation, timer or scheduler.
All language_preview files byte-identical to Stage28F; see preview-identity and target receipts.

Tests use actual compiler/Runtime/Planner/Bridge with memory-only report callbacks. The new suite
is independently runnable; fixture helpers are copied into its own test TU, and only unchanged
Stage27B helper code is included (not a nested prior runner). No previous test/runners edited.
Existing compiler domains and Stage28F confirmed-owner paths are observed, not reimplemented.
Vectors have literal/page07 expectations and model unions for seeded mock property checking.

| Situation | Existing tested behavior | Evidence |
|---|---|---|
| Any prefix/alias/RESET source in executable or inactive/function region | Full preflight rejection; no source output | New rejection/context matrix and reset tests |
| Same keywords inside comments/text blocks | Comment skipped / text literal | New literal/DEFINE test |
| Prepared modifier owners plus source nonmodifier operations | Bitwise union retained through ownership/tap/restoration |256 masks and shared owner tests |
| Multiple setup owners share SHIFT | Releasing one setup owner retains the other's claim | Shared owner/selective release test |
| Source HOLD/RELEASE Repeat | Fresh Held report acceptance per command | New mask/100+retry tests plus Stage28F |
| Transient action while nonconflicting key held | Press and restoration both required, original modifiers restored |100 press/restoration retries |
| Source seventh key or transient seventh key | Reject without partial report; source diagnostic | New six-key/transient rollover plus Stage28F hold rollover |
| Source fault while modifier retained | Error line/phase and first snapshot retained; cleanup explicit | Failed/throw tests |
| Report callback cancel then Accepted/Retry/throw | Actual acceptance retained or prior evidence kept/uncertain; no source ack | Callback fault test |
| STOP/arithmetic/limit/timeout | Subsequent source commands prevented; owners logically cleared | New combined modifier error/budget test |
| Compile while Program borrowed | Busy, active Program remains ready, no new prefix state | Borrow/restart test |
| Failed new compile | Not ready; Runtime start fails, accepted setup snapshot not fabricated neutral | Borrow/restart test |
| Destruction after accepted hold | No report delivery; Program borrow released | Destruction test |
| Current zero drain retries despite prior neutral | Remains Draining until that action accepts | Fresh-drain100-retry test |
| Shared Program at two bridges | Second Runtime borrow refused; first session undisturbed | Session isolation test |

One-intent and one-Runtime-turn OR one-report-attempt invariants checked by trace driver. No
ordinary command continues after cancellation/error. Owned Program/context lifetimes comply
with Stage28E/F: do not self-destruct objects inside callbacks or use a destroyed Program.
Single-thread only. Callback exception allocation and test trace vector allocation are outside
hot-path zero-new claim. Healthy compile/setup/source/cleanup path verifies zero C++new.
No allocator replacement or production fault-policy change is made here.

No authoritative semantics inferred from these tests: Prepared modifiers are internal mock
API, not source INJECT_MOD support. RESET rejects, so tests cannot prove canonical RESET behavior.
Use the reference decision table for VERIFIED text / chosen mock policy / BLOCKED distinctions.
