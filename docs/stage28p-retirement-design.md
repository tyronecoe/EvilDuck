# Transfer retirement and observer quiescence: design, not certificate

**Strict Stage28L success-plus-retirement acceptance remains unavailable at this actual-controller boundary.** There is no deployed or native tagged controller prototype. The original driver emits endpoint/result/current length, keeps a mutable cursor, lacks a busy/active-generation refusal and has no per-endpoint retirement/fence API. The real spin interface is void/critical, not an immediate checked try-lock. Tested software paths support these findings; no simulated status bit is promoted to hardware protection.

## Why C/Q cannot simply be added to current xfer_ctl_t

Actual P03/P09/P10/P11 demonstrate descriptor overwrite and unlabeled completion: an interrupt serviced after reuse reads the newer descriptor, including its newer total length. Storing Q there and reading it at ISR time would relabel an old IRQ. P12/P18/P34 additionally expose conditional reset/close/deinit publication. Stage28O can reject a genuinely old Q before clearing newer state, but it cannot recover identity that this controller has already lost. Completion bytes, buffer addresses, ready flags and FIFO ordering are not identities.

A safe future implementation needs an immutable originating record retained **until authoritative controller retirement and publisher fencing**, with descriptor reuse prohibited. Only then can the ISR publish that record's original C/Q. It must independently establish that an older IRQ cannot reach a newer record; no source inspection here establishes that hardware condition. Therefore the Stage28P prototype implementation gate is deferred rather than implementing a current-slot retag.

## A — No further buffer/FIFO/DMA/IRQ access

Proposed per-endpoint states: Idle → Published → Scheduled → CompletionObserved or AbortRequested → Retiring → Retired. Any ambiguity/error/loss → Quarantined. Publish raw8/bound-ID immutable frame, initial pointer/length and original C/Q before enabling/scheduling. Use an independently checked finite try-ownership primitive; keep the legacy path outside its lease. Closed/busy/contended before ownership can be definite refusal; after enable/publication ambiguity retains the record. Reject reuse, polling retransmission and identity wrap.

For retirement, review endpoint-specific interrupt/admission exclusion, pending FIFO fill/completion publications, controller NAK/disable confirmation, FIFO flush/data/cache/DMA state, old IRQ status capture/acknowledgment, and memory visibility on every involved core. Verify relevant hardware status and its exact meaning using official controller documentation and later approved tests. Existing INEPNE/EPDISD/flush busy-waits are not finite try APIs; a scripted ready bit is insufficient. No automatic whole-controller teardown: common RX FIFO, EP0, CDC/MSC and global masks share resources.

Normal XFRC alone cannot certify retirement: retained cursor/FIFO reference remains, driver may service TXFE, and late IRQ shape is not authenticated. Source total length is trusted even with inconsistent simulated TSIZ (P33). Reset clears software state; close sets max_size0; disconnect/unplug/deinit do not expose a checked producer fence. These must not be converted into fabricated success. If stop/flush/IRQ exclusion cannot be proved, retain bounded quarantine and deny reuse/restart.

## B — No old event/observer can access reclaimed context

After preventing future controller publication, capture/fence an ISR publication already in progress, retain immutable event C/Q, account for queue admissions/loss, drain or safely classify already queued old work, and fence in-progress observers. Only explicit certificate with the correct lifetime/ticket permits reclamation. Queue empty, success callback or reconnect alone is insufficient. A class callback can resubmit/mutate the shared buffer before it returns (P35); a typed snapshot/context lease must replace that borrowed-buffer assumption in a separately reviewed core integration.

The genuine void dcd_event_handler/helper cannot tell DCD that the queue rejected a completion; P20 loses the fifth notice. Coordinated publisher feedback or an independent sticky fault is required. Missing observations cannot mean completion/retirement. Stage28O's queue/snapshot/fence guards remain useful but its fake controller certificates are not installed here.

## Error, cancellation and lifetime contract

Cancellation revokes source acceptance immediately and retains old resource ownership. Late completion may only aid independently proved retirement; it cannot acknowledge cancelled work. Preserve first fault, overflow state and unresolved record. After A and B are independently certified, explicitly request a fresh neutral drain; old equal zero bytes cannot satisfy it. New connection/protocol C requires its own synchronization; reconnect/configured/ready never automatically resumes. No destructor submission or automatic arming.

Identity exhaustion denies new Q/C without wrapping and continues retirement-only handling of old records. This is a future actual-controller requirement, not an implemented DCD test result; unchanged Stage28O separately tests that rule under its fake model. No Runtime/Planner/Bridge is executed or acknowledged in P.

## Acceptance gates

1. Authoritative source-backed endpoint-disable/flush/IRQ-retirement conditions and a falsifiable register model; W1C/status/FIFO-pop/posted semantics must be verified, not guessed.
2. Proven ISR/task/cross-core producer ownership, bounded try-entry and synchronization; normal endpoint ISR and task spin paths must be analyzed together with actual affinity.
3. Authenticated originating record through helper/queue/class/core, sticky publication faults and actual observer fence.
4. Coordinated exact source/config/object/ABI verification in a separately authorized isolated target process.
5. Separately authorized supervised hardware/controller/host tests; no physical action is authorized by this stage.

Until these gates are met, Accepted remains false/unavailable for real transport and production integration remains NO-GO. Existing firmware/preview APIs, source subset, K01 barrier, conservative E capacity and budgets remain unchanged.
