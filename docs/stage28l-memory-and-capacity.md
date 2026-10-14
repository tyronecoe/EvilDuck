# Proposed bounded adapter storage — not a target measurement

Stage28K's prior target object evidence is Program 6936 B + CompileSession 2408 B + Bridge 5020 B = **14,364 B**. Bridge already contains Runtime/Planner and CompileSession contains Compiler. No fresh Stage28L sizeof, compile, firmware RAM, heap, task-stack, latency or OTA measurements occurred. The 34,032 B synthetic Driver and its 256-action/128-intent evidence arrays are not carried into a production design.

## Arithmetic design budgets, subject to future sizeof/layout proof

| Proposed persistent item | Capacity × slot budget | Estimated bytes | Lifetime / rationale |
|---|---:|---:|---|
| Operational in-flight/quarantine slot | 1 × 256 | 256 | One `(C,S,E,R,Q)` binding, immutable payload 8 / framed bytes up to 9, submit/completion/retirement flags, deadlines. Keep cancelled/ambiguous Q here until certified retirement |
| Ordinary copied request slots | 8 × 64 | 512 | Fixed request cookie/op/parameters or owner-managed source handle, not full source/borrowed HTTP pointer. Full rejects before admission |
| Tagged observation slots | 4 × 96 | 384 | IDs/metadata/result and bounded copied wire shape. Capacity allows small bursts, not guaranteed losslessness; full latches fault/quarantine |
| Optional diagnostic records | 4 × 64 | 256 | First fault plus bounded recent classifications; diagnostics cannot substitute for operational retirement state. Store generic codes/IDs/lengths, not script text, credentials or default key-payload logs. Never overwrite first fault |
| Coordinator/publication control budget | 1 × 128 | 128 | Monotonic counters, current epoch/lease, sticky urgent flags, indexes, retired watermark and short critical-section state |
| Proposed extra budget | — | **1,536** | Arithmetic estimate only; not sizeof or a verified upper bound |
| Prior independent preview objects + proposed budget | — | **15,900** | Planning subtotal, not complete production RAM or device headroom |

Exact field layout/alignment, synchronization storage and complete API lifetime requirements need a future reviewed implementation/target layout check. If they exceed budgets, report revised ledger; do not silently resize or omit operational evidence. Source/file/context registry, raw Reader/cache, UI/Strings, existing executor coexistence, SDK/DCD token storage, WiFi/filesystem costs and all task stacks remain **UNKNOWN additional costs**. One bounded reusable slot is not permission to discard an unresolved Q or reuse its identity.

Known existing costs from actual inspected source/archive, not physical measurements:

- Compiled HID `_hidd_epbuf` symbol size **192 B** and `_hidd_itf` **12 B** in pinned `hid_device.c.obj`; this confirms selected compiled static storage, not complete USB memory. SDK config HID buffer 64 B, CDC RX/TX 64 B each / max ports 2, MSC buffer 4096 B are settings, not a summed live allocation measurement.
- Core HID creates binary semaphore and mutex (`USBHID.cpp:294–301`), allocates descriptor total and report-ID arrays (`:121,154–174`); kernel allocator overhead/descriptor aggregate/other class memory UNKNOWN here.
- Core USB task is created with **4096 stack-size argument**, plus a separate USB event task with queue size 5 and configured stack argument (`USB.cpp:132–149`). ESP-IDF argument units/context must be kept distinct from measured use; no task high-water claim. Loop task stack comes from `getArduinoLoopTaskStackSize`; existing loop/context stack peaks UNKNOWN.
- Shared CDC/MSC/controller task and WiFi/web/filesystem/task allocations must remain in the future peak ledger. No zero-heap or free-OTA prediction follows from the small proposed adapter subtotal.

## Capacity, identity and exact-progress policy

Retain Stage28K's conservative E-capacity guard **as an explicit finite-harness limitation**; do not repair or relax it in this stage. Evidence journal exhaustion (256 reports / 128 intents) is separate from uint64 lifetime exhaustion. A production operational slot may be reused after completion/retirement and downstream acknowledgement disposition, but C/S/E/R/Q identities may never wrap/reuse. Fixed diagnostics may drop recent diagnostics with visible overflow while retaining first fault; operational unresolved evidence may not be dropped.

If exact non-event/final Delay progress at the last E is required later, the minimal proposed language-side contract is a bounded **pre-admission event reservation hook**, distinct from Sink output, invoked before a fresh event can be accepted (including Delay). It would allow owner to grant/refuse a new E before any source effect, preserve one event admission, and never re-reserve on Retry. Non-event evaluation/wait/completion ticks would not consume E. This is **not an existing public API** and not authorized for implementation. It needs separate owner review and tests across text, functions, eager expression side effects, Delay and cancellation. Do not infer next events from byte snapshots/private state or duplicate the parser.

Until such a hook is reviewed, retain the conservative guard and stop safely at lifetime capacity; disclose that a last Delay/non-event tick can be stopped earlier than the unchanged engine would otherwise finish. No counter wrap or fabricated source success to force progress. Requests at start must also satisfy the K01 queue/setup-work barrier.

Progress ceilings remain unchanged: compiler 65,536 steps; Runtime 10,000 steps / 100,000 ticks / 30,000 ms; Planner 256 polls / 30,000 ms. Async completion polls consume attempts without duplicate submissions. Propose at most one owner Bridge step per scheduled iteration and no tight retries; exact cadence/fairness and shared USB locks require future RTOS measurement. No source subset expansion: checked arithmetic/US model remains opt-in; source modifiers, INJECT_MOD, RESET ownership, production locale/Unicode/interpolation/extensions retain their previous unsupported/blocked status.
