# Stage28D mock planning contract

Offline internal API only; no parser changes, USB/report ID/descriptor/transport or Runtime adapter.
Report is eight bytes: modifiers, reserved zero, six ascending distinct keyboard page07 usages.
Ordinary usages04..73 and modifier usagesE0..E7 are accepted as physical model IDs; arbitrary
character bytes are never cast to usages. US mapping is explicit printable ASCII32..126 plus
TAB9 and LF10->ENTER only. Unicode/control bytes reject. No locale/lock/host text guarantees.

Four persistent owners each hold six usages and eight modifier bits; acquisition/release is
idempotent, shared usage remains until all owners release. Union occupancy must stay<=6;
proposals are rejected without logical mutation on overflow. One transient action at a time,
no queued/nested action. Tap of a persistently held usage rejects HeldTap, because an edge cannot
be promised without temporarily releasing another owner. All persistent modifiers survive text.
Lowercase with persistent SHIFT can produce uppercase on a host; reports are not a text oracle.

Desired logical union, pending report and last Accepted snapshot are independent. Desired owners
commit on valid API admission, not sink acceptance; ordinary mutation rejects while Working.
Identical persistent snapshots deduplicate without publication, but owner changes still commit.
Transient press and restoration to desired persistent union both require Accepted before Ready.
Every step attempts at most one report; Retry preserves bytes/phase. No dwell/real timing/typematic
claim. DELAY remains outside this API: a future mock bridge must drain a tap before consuming delay.

A new session first synchronizes neutral through a mock report. Cancellation/stop clears internal
ownership/actions only; accepted reports are retained as evidence. Failed/throwing callbacks mark
uncertainty even if last accepted was neutral. No claim that cancellation releases any remote key.
Explicit drain may publish only neutral; bounded Retry/failure remains honest. Restart requires
confirmed mock neutral after terminal state, then synchronizes again. It never silently forgets
an accepted press. All action/drain attempts share256-attempt and30000ms hard maximum policies;
caller can narrow budgets. uint32 elapsed wraps safely. No clock-based real sleep or HID operation.

Single-threaded API; one planner cannot start a second session while active. Reentrant mutations/
step/start/drain reject, cancel is permitted. If callback cancels then returns Accepted, the actual
attempted snapshot is still recorded before stopping; release requirement is not falsely cleared.
Source/runtime caps remain unchanged. No dynamic allocation; fixed owner table, three report
buffers and one action slot. Callback/context lifetime is caller-owned until planner is no longer
used, callbacks must return promptly; self-destruction/cross-thread access is outside contract.

## Exact failure and completion boundaries

A hold/release proposal commits desired logical owners before publication; acceptance alone
updates lastAccepted. Ready after a tap means the persistent snapshot was restored, which may
still contain held keys/modifiers. neutralConfirmed is a distinct global-neutral evidence query;
releaseRequired is its negation, including legitimate persistent holds and initial unknown state.
No-op ownership changes deduplicate; session synchronization and explicit drain intentionally
publish zero even if previous accepted snapshot was already zero. Press is never deduplicated
against a held key: that tap is rejected instead. Ordinary usages04..73 include non-US, power
and keypad selectors as raw model IDs, not implemented host features or parsed command names.

Each action's press+restoration share the same attempt/time budget; press acceptance does not
reset it. Pending holds/drains also have bounded budgets. A denied action is not enqueued and
leaves desired/accepted snapshots intact. Timers apply to pending actions, not idle persistent
holds. Budget failure conservatively marks release uncertainty even after only Retry returns.
Each explicitly requested new drain gets a new bounded budget, with no automatic retry loop.
Terminal sink errors preserve reason/phase/pending attempted snapshot even if later ordinary
API calls reject. Double cancellation does not overwrite the original cancelled phase.

A callback cancelling before returning Accepted still causes that attempted report to be recorded
as accepted; cancelling and returning Retry leaves the prior accepted evidence. Throw/Failed after
cancellation enters Failed with uncertainty. Internal clearing cannot undo either already accepted
report. Input/output snapshots use small fixed copies to withstand cancellation during callback.
No real report receipt, disconnect or endpoint session identification is modeled.

Modifier-mask API inputs are16-bit and reject values>255 with InvalidModifiers before conversion, avoiding silent truncation.
