# Proposed minimal coherent transport change — NOT IMPLEMENTED

The current stack does **not** satisfy Stage28L success+retirement acceptance. Native tests verify actual source dispatch under substituted controller/OS boundaries; they do not implement genuine transfer identities or retirement. No patch/SDK replacement/core adapter is delivered.

Select one coordinated, opt-in **tagged HID IN transaction plus endpoint fence** design. Preserve legacy APIs/behaviors outside an exclusive endpoint lease. Generating application Q at callback time, matching bytes/pointers, or accepting the shared semaphore is rejected by N07–N09/N17 evidence. Event clearing must validate generation before changing current endpoint state; simply filtering at the final observer is too late.

| Existing path / exact location | Proposed change | Why / affected callers and builds | Required future validation |
|---|---|---|---|
| HID entry hid_device.c113–131; internal hidd_interface_t/hidd_epbuf_t | Optional ticketed try-submit accepts raw8 plus separately bound ID, Q allocated before any ownership/callback; retain immutable frame/reference and expected length | Current copy/framing works, but no identity or bounded claim; preserve raw legacy callers outside lease | Fresh refusal, invalid shape, no duplicate prefix, early completion, ownership outcomes |
| tusb.c200–229 tu_edpt_claim/release; OSAL mutex functions | Checked try-claim and bounded unlock strategy, no WAIT_FOREVER; reject before copying/ownership if lock/lease/binding unavailable | N15 reaches infinite-wait parameter and ignored forced failure. Do not redefine old API's bool as safe refusal | Actual pinned OS primitives; interrupt/task contention, no unlock without ownership, finite try/failure |
| usbd.c1366–1422 endpoint claim/xfer/status | Store outstanding token and epoch with busy/claimed; preserve early-completion ordering; prevent any other producer from using leased IN | N04 shows completion before return; N05 only busy exclusion, N16 no owner identity | Multiple producers, successful early callback, contradictory lower outcome, no false NotSubmitted |
| Builder DCD xfer_ctl_t / dcd_edpt_xfer601–628; completion emit876–922 and reset1038–1090 | Carry actual Q/C from accepted transfer into ISR completion before any endpoint-state reuse; checked per-endpoint abort/retire implementation | Current descriptor stores buffer/len, not ticket; reset/slave/FIFO/IRQ lifetime is controller-specific | Pinned DCD source/config ABI and actual register/IRQ retirement proof; cannot manufacture success |
| dcd.h49–88 dcd_event_t,220–229 completion helper; usbd event queue | Extend optional event payload with authentic Q/C and retained outcome/shape; bounded loss flags outside queue; reset/loss stamps old epoch | N14 finite queue loses fifth event; unchanged event contains only endpoint/result/len. Current ISR flag is not a lifetime token | Queue full, no dropped-retirement success, old events after new binding, exact target event layout |
| usbd.c622–707 event dispatch / endpoint state clearing | Reject old generation **before** clearing current busy/claimed or routing through reused ep2drv; retire old work through its retained record | N09/N11/N12/N13 show old notices around reset/reuse cannot be identified by current mapping | No stale callback clears new transfer, reset ordering, delayed/duplicate acknowledgements |
| hid_device.c386–418 class completion | Ticketed observation carries original token/binding and stable completion shape; reject partial/unexpected type/length before transport Accepted | N03 exposes partial/oversized callback lengths; N17 exposes mutable borrowed contents during callback reentry | Copy/retirement ordering, bounded observation publication, unchanged legacy callbacks |
| Protected USBHID.cpp331–374 strong complete/weak failed path | Extend reviewed core observer inside existing hook, not competing strong globals; preserve legacy semaphore semantics for legacy calls | Existing tokenless semaphore is not a current action receipt; full core runtime untested N22 | Full linked-symbol/ABI verification later, early/late semaphore wakes, no hidden block/duplicate observer |
| Registry/descriptor/protocol + existing producers | One opt-in exclusive endpoint lease across raw scheduler/legacy/manual/core entry; read actual negotiated interface/endpoint/report/protocol binding | Native fixture values are not board binding; N18 raw ID framing independent of boot protocol property, N19 raw can route EP0 when unconfigured | Production producer inventory, binding refusal/change, CDC/MSC coexistence, no descriptor/identity change |
| tud_deinit / dcd_deinit / observer lifecycle | Separate checked endpoint retirement and observer fence; do not infer a certificate from deinit return, reconnect or empty queue | N20 ignores false DCD deinit and sends late event toward deleted queue; archived usbd provides weak false DCD deinit | Checked controller stop, ISR producer fence, queued events, active observers, failed/quarantined teardown |

## Identity and ownership outcome contract

A persistent transport coordinator allocates never-reused Q before offering one report. Stack-owned C is incremented/invalidated at the trusted endpoint/protocol lifetime boundary before new admissions, not read from a callback-time mounted bool. Associate `(C,Q)` with application S/E/R by creation, never by byte equality. DCD transfer state must latch the ticket at ownership and copy it into the actual event. No wrap/reuse/reconstruction while old contexts remain unresolved. Loss/overflow preserves first fault and quarantines old work.

Proposed pseudocode, not an existing SDK API:

```text
try_submit(bound_epoch, ticket, raw8, report_id):
    reject stale binding or nonexclusive producer before side effects
    checked try-claim; on definite refusal retire unused ticket -> NotSubmitted
    publish owning descriptor before scheduling (early callback possible)
    schedule at bounded controller entry -> Submitted or Ambiguous ownership
observe_tagged_event:
    validate original ticket/epoch before modifying current endpoint state
    retain exact success/failure separately from transfer retirement
```

Submitted does not mean Accepted. If completion occurs before submit returns, record it without recursive Bridge mutation; owner resolves both call outcome and observation. A lower failure after possible ownership cannot be retried automatically; NotSubmitted requires independently proved absence of controller access/callback ownership. Current DCD closed-endpoint guard supports a specific refusal analysis, not a blanket bool-false guarantee.

## Two distinct certificates

**Transfer retirement:** controller/driver independently proves it cannot read/write Q's immutable buffer again (FIFO/DMA, IRQ pending state, abort/error paths included). Full success may coincide with retirement only after that proof; an existing success callback alone is insufficient. The selected DCD still retains a transfer descriptor and lacks a public retirement certificate. Do not silently weaken acceptance to copying/queueing to avoid this problem.

**Observer/context quiescence:** stop old producers, retain old context, retire all old Q, fence ISR event publication and task dispatch, account for queued/in-progress observer calls, then explicitly certify no future access to old context. Queue empty, reset, unplug, hidd_deinit or tud_deinit return is not this certificate. Whole-device shutdown could disrupt CDC/MSC; prefer separately validated per-endpoint lifecycle. If safe bounded stop cannot be certified, retain finite quarantine and deny restart rather than fake success. ROM/raw driver/physical assumptions remain outside software component evidence.

Existing weak dcd_deinit in archived usbd returns false; builder DCD has no concrete definition. Existing controlled ELF has no exact dcd_deinit symbol (dead/unlinked path), so this is not a claim its current application executes that deinit. A future fence needs a real reviewed checked controller mechanism, not merely another callback name.

## Costs and gates

Ticket/event structures, class-driver function signatures, queue item sizes, DCD state and core observer interfaces would change together. Require explicit CFG opt-in and all affected TinyUSB/OS/controller objects rebuilt from pinned sources under a separately authorized isolated process; never mix changed headers with old precompiled archives. Native event sizeof24B is not target ABI; added C/Q imply storage/alignment cost that needs later target object verification. No new allocation, unbounded event queue, blocking owner wait or target resource estimate is approved here.

Preserve Stage28L budgets, Stage28M K01 dispositions/barrier, conservative E guard, source subset and genuine press/restoration/source-ack order. Cancelled E cannot be acknowledged; retired old work permits only explicitly requested fresh E0 drain, and new S requires fresh sync. No parser/descriptor/partition change or auto-arming. Host neutrality remains a separately supervised physical question.

**Selected predicate remains strict and currently unavailable.** Smallest next proposal: owner review of this coordinated path table, then a separately scoped native opt-in tagged-event/checked-try prototype against these exact C inputs with explicit fake retirement certificates. That would test new software semantics only; actual controller retirement and full patched SDK/core ABI/build/physical gates would still need their own evidence and authorization. Stage28O is not begun automatically.
