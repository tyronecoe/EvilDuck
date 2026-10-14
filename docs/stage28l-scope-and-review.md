# Stage28L scope and baseline review

**GO: review the source-backed transport/ownership design. NO-GO: adapter implementation, production integration, live USB/HID, firmware images, flash, boot, OTA or automatic Stage28M.**

Exact clean starting HEAD: `4532c9c5d386aa0d4a1c83cd7eeaef495f0c6e8b`, branch `stage28k-synthetic-report-journal`. Frozen Stage26: `968c8e0aaf459b0b8b652cc57fe88225894ab64b`. Only eight new `docs/stage28l-*` files are delivered; no code/test/API/patch/configuration changes. Existing checkout reused without resetting work. New branch `stage28l-transport-ownership-design` is created only for this delivery; any existing name must not be overwritten.

## Prior evidence retained, not rerun

Stage28K's 37 PASS groups / 10,346 primary assertions and separate 187 legacy PASS groups / 579,622 assertions remain **prior results**. Its Driver was 34,032 target / 34,128 host bytes, with 19,668 additional target bytes beyond Program/CompileSession/Bridge. No Stage28L regression, sanitizer, sizeof, object build, firmware build or owner Mac test was executed. New evidence is source/hash/Git inspection and disassembly of **existing** pinned archive members and the already built, hash-matched Stage26 ELF. Archive extraction into scratch does not rebuild or replace a dependency.

The owner-native High Sierra E–H evidence remains owner-reported/screenshot-observed, not cloud native/device testing. Its compiler/exit and leak-disabled Mac scope are preserved from `stage28k-owner-approval.md`; no rerun requested. Original recovery firmware is OWNER CONFIRMED AVAILABLE EXTERNALLY, not a search/request blocker.

## Stage28K review findings

| ID | Concrete observation and source | Disposition |
|---|---|---|
| K01 | `tests/stage28k/journal_driver.cpp:38–42` starts Runtime without checking `requestCount_`; `:59–64` admits setup handoff while Prepared; `:129` consumes requests only while Prepared; `:13` clears them at terminal. An admitted queued setup request can remain unexecuted if start crosses that boundary first | **SOURCE-VERIFIED handoff gap**, not newly runtime-reproduced or a reversal of prior test outcomes. Future design rejects start until queue empty, no setup action pending and every request has an explicit disposition; propose a later mock regression. No repair here |
| K02 | `:133–137` conservatively checks E capacity before a tick with no current intent; `:103–111` identifies Delay through post-tick counter changes | **Documented limitation**, not a new defect. Retain finite-harness restriction; exact final Delay/non-event progress requires a separately reviewed pre-admission hook. No private inspection/parser duplicate |
| K03 | `:146–148` ignores all completion notices for acceptance; `:93–98` accepts only by copying its current mock snapshot | **Retained invariant**. This is not real completion correlation. A callback's matching generated S/R alone is not authentic submission identity |
| K04 | `:9–18,115–122` terminal clearing versus explicit fresh drain; `:85–99,141–144` callback request deferred until after report return | **Retained source contract** within single-owner memory scope. No real device cancellation/resource-retirement proof |
| K05 | `journal_driver.h:7,54–66` fixed arrays and lifetime counters; `core.h:6–9,37–92`, `bridge.h:14–16` fixed limits/embedded ownership | **Retained capacities/lifetimes**, not production placement approval. Do not carry evidence arrays into firmware or count embedded Runtime/Planner/Compiler twice |

No claim that source review alone establishes full RTOS race freedom or repairs prior evidence. K01 is a precise future acceptance gap; an admission receipt is not setup execution. Historical tests/docs/approval cells remain byte-identical.

## Design decision

Recommend **correlated successful USB transfer completion**, with independent retirement/quiescence evidence, as the future Planner Sink Accepted boundary. Submission/copy is not enough. That observation is **not safely exposed by the current public backend/core**: completion is tokenless and core discards its metadata; raw and legacy producers coexist; lower-level lifecycle source provenance is incomplete. No Stage28K mock label is promoted into USB success. The design can be reviewed now; implementation remains blocked until separately scoped API/dependency evidence and approval.

The narrow next proposal is a synthetic transport-contract harness for genuine-tag versus tokenless observations, retirement, queue overflow and K01 start barriers. It must not manufacture SDK guarantees. A pinned source/lifecycle investigation must precede any real backend patch. No Stage28M is begun or authorized by this document.
