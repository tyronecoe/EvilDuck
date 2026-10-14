# Proposed transport acceptance contract — DOCUMENTATION ONLY

No adapter, API, patch, real callback, endpoint or firmware implements this contract. All names below are proposed interface roles/pseudocode, **not existing SDK symbols**. Existing Planner/Bridge source stays unchanged. Evidence and current API limitations: `stage28l-usb-source-evidence.md`.

## Select one meaning for Accepted

| Option | Current feasibility | Decision |
|---|---|---|
| Copy/endpoint admission → Accepted | Raw entry copies and returns lower submission status, but refusal side effects, protocol and lock/lifetime classification need work | Not selected: it would advance source before a correlated transfer; Stage28K mock copying is not this physical boundary |
| Blocking `USBHID::SendReport` bool → Accepted | Public, but shared semaphore, late/extra gives, concurrent raw producers and post-submit timeout lose correlation | Reject as adapter boundary; not cooperative and cannot distinguish current completion |
| Correlated successful IN completion → Accepted | Requires future token/lifetime/provenance/fence APIs not provided today | **RECOMMENDED PROPOSAL**: only exact current completion with matching genuine submission identity and shape may satisfy R |

Accepted means **the chosen current report action's tagged USB IN transfer completed successfully at the stack/controller boundary**, with full expected length and current bound framing; it does not mean the OS/app interpreted it or released keys. On a healthy completion a retirement certificate must additionally establish safe buffer/context reuse before the next submission. If completion and retirement are separate, retain the success latch and poll Retry until both are present; do not return Accepted while resources prevent the required next action. The contract's return predicate is therefore **current correlated success AND safe retirement AND valid epoch/framing AND this action still eligible**. For E-bearing work, eligibility excludes cancelled E; an explicitly requested fresh drain with E=0 remains eligible after source cancellation, once prior resources are retired. A global cancelled-source flag must not prevent that management drain. The success event alone never creates an E acknowledgement.

Source event admission, immutable snapshot preparation, copy/submission, correlated completion, resource retirement, source ack and application host behavior remain different observations. Planner sees its existing synchronous `Retry/Accepted/Failed` Sink result, but a future adapter/service may retain asynchronous state between polls. Press and restoration are separate R actions; only after all required final report actions Accepted does unchanged Bridge allow the next Runtime retry to acknowledge E once. Delay has an E acceptance/timer but no transport R/Q; sync, setup and drain have E=0.

## Minimal future boundary required, not implemented

A separately reviewed transport service needs these semantics:

- Bounded, nonblocking submission with outcomes **NotSubmitted**, **Submitted**, **Ambiguous/Failed**. Publish a never-reused Q before any callback is possible; service owns an immutable framed buffer and reports whether it took ownership. The proposed request carries payload 8 and bound ID/protocol separately, and framing happens exactly once. If a future implementation uses the raw class entry, it must pass payload 8 / len 8 plus the selected ID, never preframed 9 plus nonzero ID. Expected wire 9 is validation/lifetime data, not a second prefix. Definitely-not-submitted attempts retire Q immediately; a later submission attempt may use a new Q for the same R.
- Genuine tagged observations `(C,Q,result,instance,endpoint,protocol,reportId,length)` whose Q originates at transfer creation and survives the actual completion event path. Payload shape/data is a check, never identity. Tagging whichever record is current at callback dispatch is prohibited.
- Success/failure retirement and an explicit fence certificate that no further DMA/access/callback for Q/C can occur. NotSubmitted certifies no transfer ownership. Reset/disconnect must separately retire old work or leave it quarantined; mount/ready is not a fence.
- A controlled core observer integrated with its existing strong completion handler and failed path, preserving existing semaphore/routing behavior outside the exclusive preview lease. No duplicate global complete symbol or unreviewed weak override. Exact lower stack source/build provenance is mandatory before a change.

An application token cannot create identity in the tokenless SDK callback. To use one slot safely without a low-level token requires independent proof of exclusive writers, exactly one outstanding transfer, no duplicate/late callback after retirement, connection/protocol fencing and callback quiescence before reuse. Those guarantees are **not established**; core comments explicitly admit late/extra semaphore events. A core observer alone is insufficient. The smallest *semantic* change is a token-bearing nonblocking submit/observe/retire boundary plus endpoint producer exclusivity; its exact source patch surface is BLOCKED pending shipped SDK/DCD provenance. A future implementation may carry Q through the controller/event record or demonstrate an equivalent proven fence; it may not guess a SDK structure/patch now.

## Finite asynchronous mapping to the unchanged Sink

R snapshot is immutable; one transport Q may own the endpoint at a time. A poll is not a new submission. IDs are never allocated by byte equality. A new identical snapshot after successful retirement belongs to a new R/Q.

| Adapter state / input | Action and next state | Sink result / source effect |
|---|---|---|
| Idle / new current R | Validate exclusive lease, epoch/framing, context and budget; retain snapshot, bind S/E/R; allocate Q, publish Submitting before call | No early source ack |
| Submitting / definitely NotSubmitted | Record known refusal, retire Q; keep R/bytes; schedule another bounded attempt with fresh Q | Retry; no accepted transfer or E ack |
| Submitting / Submitted, no observation | AwaitCompletion; do not submit again | Retry |
| Submitting / early completion before call returns | Callback records tagged observation only; owner resolves submit outcome and completion in order | Retry until a coherent submitted/current-success/retirement record; inconsistent outcome → Failed |
| AwaitCompletion / poll | Compare current action identity and immutable bytes; bounded observation processing; no resubmit | Retry, consumes normal Planner attempt budget |
| AwaitCompletion / exact success, full shape and retirement | CompletionLatched | Next current poll returns Accepted exactly once for R; then release slot for next R |
| AwaitCompletion / success but retirement pending | Keep immutable slot and success latch | Retry; don't allow next action or use success to revive cancelled E |
| Any / actual failure, unexpected shape, ambiguity or deadline | First fault latched; terminal/quarantine pending resource retirement | Failed, no fabricated Accepted; do not resubmit uncertain Q |
| CompletionLatched / duplicate callback | Classify duplicate by genuine C/Q; bounded diagnostic only | No second Accepted, new R or E ack |
| Any / cancelled source | Stop source immediately; existing Submitted Q may still complete/retire | Never Accepted to cancelled E; no source resume |
| Terminal retiring / exact late completion | Retire resources only; keep first fault/source tombstone | No source acknowledgement; eligible for explicit fresh drain only after retirement fence |
| Any / stale C/Q, wrong instance/ID/length | Stale known retired observations ignored; malformed current observations fault | Never map to current R based on bytes/current slot |
| Any / protocol/suspend/reset/disconnect change | Epoch invalid, stop progress; preserve current slot until certified retirement | Failed/terminal undrained; reconnect alone cannot restore Ready |

**Proposed pseudocode, not executable:**

```text
owner_step(now):
    consume sticky cancel/loss/overflow first
    consume at most one bounded transport observation
    if source cancelled: retire only; never acknowledge cancelled E
    otherwise perform at most one Bridge step

sink_poll(current_R, snapshot):
    if a different unresolved R exists: fail protocol
    if current_R has validated success + retirement in the bound epoch:
        consume its receipt once; return Accepted
    if terminal/invalid/ambiguous/budget exhausted: return Failed
    if Q was submitted: return Retry            # NO duplicate submission
    if eligible for one nonblocking attempt: publish Q before submitting
    return Retry                              # copying/queueing is not Accepted
```

Existing Sink only supplies eight bytes, not R. As in Stage28K, a future wrapper may bind R using authoritative admission/Planner phase and single-owner transitions; it must never identify R by snapshot equality. USB observation Q must be independently genuine; the wrapper ledger does not repair the missing transport token. Any cancellation between returning current R Accepted and source retry suppresses E ack. If source ack has already happened, it cannot be undone; later completion/resource failure cannot invent a second ack.

## Progress and limits

Retain Planner 256 attempts / 30,000 ms, Runtime 10,000 steps / 100,000 ticks / 30,000 ms and compiler 65,536 steps. All elapsed comparisons use caller uint32 clock with small-wrap/short-gap assumption. Exact equality is timeout. Pending-completion polls count against Planner attempts; a rapidly stepped pending transfer can hit 256 before 30 seconds. This is an explicit strict policy, not an excuse to silently enlarge budgets. No busy polling, blocking SendReport or waiting on a lock required by a callback. New service submission/retirement deadlines cannot extend those ceilings.

Timeout before submission may yield bounded Retry if definitely NotSubmitted and budget remains; at the actual deadline return Failed. Timeout after possible submission is ambiguous/quarantined, never an automatic retransmission. Missing/failed/late completion is not safe host neutralization. Recovery needs independent retirement and fresh drain; no automatic transition or release request from destructor.
