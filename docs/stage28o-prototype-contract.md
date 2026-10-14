# Opt-in native contract and actual implementation

**EXPERIMENTAL NATIVE ONLY. Not installed, firmware-integrated or authorized for physical use.** CFG_TUD_TAGGED_NATIVE is absent/0 by default; native coordinated objects are built with1 explicitly. Disabling it removes added event fields/functions/lease guards and preserves legacy API/layout/behavior, checked against all20 Stage28N observation receipts. No changed header is combined with a precompiled SDK object.

## Genuine changed source path

The deterministic patch changes three genuine pinned vendor files and adds one narrow API header. Existing MIT preambles remain intact in source copies. Exact input/output/patch hashes are in stage28o-input-and-patch-manifest.json. templates tagged.h/usbd_extension.inc retain the added authoring text; they are not separately compiled implementations. Real dispatch, configuration mapping, class callback and OS queue still execute.

| Patched source/symbol | Actual role |
|---|---|
| hid_device.c, tud_hid_tagged_bind/try | Validate instance, obtain genuine class endpoint/protocol, invoke separate checked entry. Fixture accepts ID0/1; ID0 tests byte framing only, not host descriptor compatibility |
| usbd.c, usbd_tagged_bind/try | Single endpoint lease and immutable outstanding state; validated raw8; monotonic C/Q; checked timeout0 lock; busy/claim ownership; framing once; publication before fake DCD call |
| dcd.h, dcd_event_t.xfer_complete | Opt-in C/Q, instance, protocol, report-ID carried in the actual copied completion event. Fake controller emits the identity from its specific original record, not the current slot |
| usbd.c, dcd_event_handler/queue_event | Tagged events bypass current ISR driver lookup and enter genuine copied queue. Reset/unplug/configuration/protocol requests invalidate eligibility at ingress. Queue refusal sets a sticky fault outside the full queue |
| usbd.c, tud_task_ext | Validate C/Q, endpoint, port, shape, epoch and duplicate status BEFORE busy/claimed clearing, current driver mapping or class-buffer use. Rejects never access a newer transfer |
| hid_device.c, hidd_xfer_cb | Genuine dispatcher reaches real class. Leased input invokes tagged observer with stable retained frame; unleased legacy behavior stays unchanged |
| usbd.c, observe/take/retire/fence/release/unbind | Separate completion success, controller retirement, pending/in-progress observer, eligibility and reclamation. Explicit owner operations; no destructor send or automatic resumption |

Patched source line/function coverage is recorded per case, so line numbers are tied to exact output hashes rather than guessed target objects. src/tusb.c/usbd_control.c/tusb_fifo.c remain byte-identical. tusb_fifo.c compiles as support; no positive FIFO execution is claimed.

## Identities and submission outcomes

C is an explicitly established fixture endpoint/configuration/protocol lifetime. Binding reads the real native HID class and ready/busy/claim state; it does not discover a physical board. Q is burned before any claim or controller ownership. Counter overflow refuses new admission, while old work may still retire. Default limit is UINT64_MAX; lower limit8 tests boundaries efficiently, and O41 uses the true64-bit maximum with an explicitly compiled test seed. Seed/limit overrides are native test inputs, not production settings.

One active transfer stores C/Q, instance, endpoint, protocol, ID, full length, immutable frame and ownership outcome. Pending polls return NotSubmitted **for that new attempt** with TAG_PENDING, without allocating Q or calling the controller; the original Submitted/Ambiguous transfer remains active. No Sink/Runtime is integrated; no source acknowledgement is claimed. usbd_tagged_accepted is a correlated predicate, not an exactly-once language acknowledgement.

| Result / condition | Meaning |
|---|---|
| Invalid binding/shape, checked lock contention, fake readiness busy | NotSubmitted, no controller call, active-frame change or acquired claim; Q is burned only after shape/binding admission |
| Explicit fake definite refusal | NotSubmitted; no controller-owned record; release only this acquired endpoint claim, retain no unresolved transfer; later retry needs fresh Q |
| Submitted | Fake controller owns original tagged immutable record; may already have delivered completion before return |
| Ambiguous or unexpected controller result | Keep active slot and first fault, deny resubmission; no fabricated NotSubmitted |
| Completion queued/dispatched plus contradictory NotSubmitted | TAG_CONTRADICTION, Ambiguous, retained slot; no duplicate output |
| Failed unlock after acquired claim | TAG_LOCK_RELEASE, Ambiguous quarantine, no controller call; no automatic lock recovery/restart |

Admission and submission share an in-progress barrier. Even reentry from the fake lock cannot unbind, allocate another Q or submit another frame; cancellation after acquiring that lock is checked before frame/claim publication. Mutex lock uses timeout0 and its result is honored; successful unlock is checked. The fake OS neither waits nor proves a real kernel's latency/locking semantics.

## Completion, retention and cancellation

Exact current full successful completion creates one pending observation and an immutable stack snapshot to the observer. Its frame cannot change during callback reentry. Duplicate, stale, tokenless or unrelated identities do not clear a newer endpoint or generate another observation. Malformed current shape/result invalidates the binding and preserves first fault. No raw pointer/byte equality provides identity.

Acceptance requires active/current eligible transfer, full correlated success, Submitted outcome, explicit retirement, explicit observer fence, valid/ready binding, no queued/in-progress/pending observation, no submission call in progress and no first fault. Success without retirement cannot release/reuse a frame. Retirement without success permits explicit resource release but cannot produce a successful receipt. A matching event arriving after a current fence contradicts quiescence: invalidate it, fault and deny acceptance. A deliberately injected old event after prior release is rejected before touching a newer transfer.

Cancellation invalidates eligibility; late completion cannot revive it. Independent retirement/fence can permit resource cleanup only. After explicit unbind and fresh C, a newly requested zero report can drain/synchronize; an equal old zero frame cannot satisfy it. This is fixture management, not actual Runtime cancellation/acknowledgement or proof the host released keys.

## Bounds and fake certificates

Operational coordinator: one transfer/immutable frame9B, one pending receipt, four genuine task-queue entries, queued-event and in-progress-observer counters. Native measured state96B includes transfer48B, not added again. Stack observer snapshot48B is separately transient. Native event40B vs original24B; custom OS has4×64B slots in both configurations. None are Xtensa ABI, firmware RAM, task-stack high-water or hardware heap measurements. Fixed fixture evidence capacities (controller32, observer32, event/submission/callback journals128) are test diagnostics, not proposed production storage.

A full copied event queue faults through a separate latch and invalidates acceptance. A occupied single-receipt capacity blocks fence/reuse until explicit consumption; duplicates are filtered before publishing another receipt, so legal single-slot execution cannot overflow this receipt slot. Its defensive overflow/reentrant-class branch is not claimed exercised by a genuine dispatcher event. No oldest-record dropping or unresolved-frame overwrite occurs. Missing observations never create retirement.

The fake retirement certificate asserts only the exact record's controller access ended. The fake C fence asserts all that lifetime's retained controller records have stopped emission/access. Actual queue accounting, receipt consumption and in-progress callback guards are additional requirements before reclamation. Fake assertions do not execute IRQ/DMA/FIFO abort, producer termination or real callback fencing. Deliberate stale/post-fence injection is adversarial model input, not a statement that hardware emits it.

Legacy claim/release/xfer/FIFO submission boundaries reject the leased endpoint. Raw calls directly into DCD, close/stall/open operations, other ports/classes/ISR sources and a complete firmware producer inventory are **not** intercepted or certified; full real ownership remains blocked. Native test calls are serialized, with specified synchronous reentry; there are no real threads, cores, interrupts or memory-order guarantees. Original tud_task_ext drains until empty and is not converted into a bounded RTOS scheduler. USB CDC/MSC coexistence is not exercised. Normal deinit invalidates tagged eligibility but is not a controller retirement certificate.
