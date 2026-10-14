# Original versus native opt-in comparison

Unmodified exact21-file input corpus executed once through the unchanged Stage28N runner:20 observation PASS/131 assertions, all CONTRACT NOT SATISFIED. Opt-in-disabled patched copies execute the same20 original fixture cases:20 observation PASS/131 assertions; every original functional receipt field matches, not merely the final count. Negative controls and old defects stay separate. No historical expectation was rewritten.

| Demonstrated original gap | Baseline evidence | Prototype evidence / closure within fake boundary |
|---|---|---|
| Old event clears a newer endpoint, uses reused bytes | N09/N11–13; new original diagnostic exits1 on required newer busy state | O11–13/O15–16/O30/O43: original C/Q retained in controller→event; pre-clear rejection preserves new busy/frame and does not notify observer |
| Oversize refusal leaks claim | N05; new original diagnostic exits1 when next valid report cannot claim | O03: validate raw length before claim/copy; following valid tagged report completes normally |
| WAIT_FOREVER/ignored lock result | N15 | O04/O39/O45–46: timeout0 checked admission, retained unlock ambiguity and reentry/cancellation guard. Not a FreeRTOS timing proof |
| Tokenless/equal reports and duplicate notice | N07–09 | O09–11/O15/O42: distinct original Q, exact current identity validation; duplicate does not create another receipt |
| Borrowed callback buffer changes on reentry | N17 | O20/O27: immutable frame/snapshot and in-progress barrier; reentry denied, snapshot unchanged |
| Partial/oversized length reaches observer | N03 | O17–19/O35: shape/result rejection before current state/class observation |
| Early callback before submit return | N04 | O06–07/O37/O40: publish before lower call, genuine real dispatch can complete early; contradictory refusal quarantines, submission-in-progress blocks reuse |
| Reset/unplug/reopen and protocol do not retire | N10–13/N18 | O12–14/O38/O44: immediate eligibility invalidation; only explicit fake retirement/fence allows cleanup; reconnect cannot resume |
| Queue loss not a sticky ownership fault | N14 | O25: fifth event rejected, independent loss latch, no acceptance; explicit retirement still required |
| Busy exclusion is not a lease | N16 | O26/O34: shared legacy claim/release/xfer/FIFO paths denied while leased. Direct DCD/other unreviewed routes remain a blocker |
| Deinit/completion not retirement | N20 | O01/O24/O27/O36/O44: success, retirement, observer fence and eligible acceptance separate. Real deinit/fence remains unimplemented |

The two focused original reproductions run genuine unpatched vendor logic with the original boundary.c. They exit1 on the intended stale-busy or next-claim contract expectation, independently of baseline observation PASS. Equivalent new sequences are O11 and O03. They use a different checked API and authentic fake ticket path, deliberately: the legacy tokenless API cannot supply those guarantees. A single shared tagged API driver cannot be compiled against the original SDK without inventing its API. Original receipts/code are not changed to claim success.

**Closed only under fake assumptions:** submission-created identity end-to-end, early state publication, pre-state-clear stale rejection, checked admission/shape, no claim leak on new-entry refusal, leased shared submission boundaries, immutable observations, no pending resubmission, sticky loss, explicit resource/observer gating, cancellation eligibility and ID exhaustion.

**Not closed:** actual builder DCD identity propagation and retirement/fence; bounded FreeRTOS/controller entry; authentic board binding/protocol/descriptor; complete producer exclusivity; actual Arduino hook/CDC/MSC integration; target ABI/config/archive compatibility; complete shipped source-to-object equivalence; physical transport or host behavior. Baseline N21/N22 remain BLOCKED/source-static, not secretly replaced with another controller/core.
