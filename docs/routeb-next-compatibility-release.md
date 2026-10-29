# Next Route B compatibility release — proposal only

Starting application: [accepted text/keyboard baseline](routeb-accepted-baseline.md). No command in this proposal is newly implemented. The current inventory is [here](routeb-accepted-compatibility.md). The acceptance closeout does not authorize a firmware implementation, build, installer, hardware test, HID output, flashing or OTA.

## Ranked work groups

Rankings are engineering judgments, not measured compatibility percentages.

| Rank / group | Practical usefulness | Evidence strength | Implementation risk / test effort |
|---|---|---|---|
| 1. Bounded execution restart | High: controlled repetition without copying source | Official `RESTART_PAYLOAD` restart-from-beginning semantics; variable and budget lifetimes unspecified | Medium–high / medium–high: continuation, ownership and budget boundaries |
| 2. Source-file portability | Medium–high: fewer editor/file-format surprises | Direct verified source and P14 evidence: compiler accepts initial UTF-8 BOM, composed adapter rejects it | Low–medium / low–medium: admission, chunk boundaries and physical-line diagnostics |
| 3. Explicit keyboard-layout support | High when scripts use non-US punctuation | General official layout concept is documented; exact additional maps need separately verified references | High / high: device map versus host input source, modifiers, dead keys and physical fixtures |

Recommend one focused **bounded restart** release next. Source portability is a separate small follow-up; it should not be disguised as a new DuckyScript command. Additional layout work requires a selected target layout and verified map; Canadian/US observations alone do not establish a general mapping. Neither follow-up requires waiting for Windows to perform independent Mac-compatible work.

No significant existing safety defect was established by this targeted source review. The known BOM boundary is a documented limitation, not evidence of unsafe execution. Reassess priority if a reproducible safety defect emerges. INJECT_VAR and stored random-keycode properties stay blocked; no new independent runtime evidence exists here, and no compiler checks or broad searches are repeated.

## Exact proposed grammar and evidence boundary

```ducky
RESTART_PAYLOAD
```

One exact argument-free statement; ordinary existing whitespace and comment rules apply. Reject arguments, expressions, aliases and `REPEAT 2 RESTART_PAYLOAD`. Retained malformed source must reject before any output, including inactive runtime branches and unused functions. Preprocessor-excluded source retains its distinct established treatment.

Official [Payload Control](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/payload-control.md) states that the command ceases current execution and restarts from the beginning. Its example makes following text unreachable. Existing source capture: `docs/text-keyboard-references.json`, payload-control SHA-256 `8fde4569850a7fecb0a42c9aa95258977ebb8c7322622d9b84a379e0570bec7c`. No official runtime was executed. The detailed state/reset and finite-limit rules below are **proposed EvilDuck policies**, not claimed canonical Hak5 equivalence.

## Required implementation contract, if separately approved

Use the current composed compiler/runtime/adapter/scheduler. Append `Op::Restart` and a distinct `EventType::Restart` without renumbering existing enums. Reserve the command name; emit one instruction. Add no second interpreter, HID path, restart queue or external Start call.

1. Runtime emits and caches one Restart event, bypassing jitter. Adapter routes it to existing owner-scoped `route_b::reset`, keeping Restart distinct from ordinary RESET throughout retries. Accept only the actual matching Done result; stale, wrong or duplicate observations cannot rewind execution.
2. After accepted neutral submission, a private rewind helper resets PC to zero and clears user values/initialization, call frames, expression continuations, return state, text/block/delay cursors, pending events and sampled operands/jitter choices. Restore random bounds 0–9 and jitter disabled/max20 ms. Keep random/feedback providers and contexts; do not reseed entropy. Return immediately and run the first instruction on a later tick.
3. Preserve Program pointer/revision/borrow, compiled constants/functions/preprocessor selections and source identity. Do not reopen storage, recompile, release/reborrow Program, or call `Runtime::start()` during restart. That method resets global execution accounting and is unsuitable.
4. Preserve original start timestamp, cumulative steps/ticks and configured limits. Current maximums remain 10,000 steps, 100,000 ticks and 30 seconds elapsed; smaller valid caller limits also survive. Restart consumes ordinary work and cannot refresh these limits. Limit exhaustion follows existing error/cleanup behavior, even though the official illustrative loop runs indefinitely.
5. Retain the same coordinator request, lease/session, captured Caps timing, monotonic backend operation IDs, diagnostics and first-fault history. Do not detach/reacquire, publish an intermediate terminal status or repeat initial sync. Existing per-operation deadlines still apply normally; no global budget reset is permitted.
6. STOP polling remains before runtime progress, including after scheduler/callback work. STOP/failure during clear suppresses rewind and all later output. Not-ready submissions stay cooperative. Ambiguous acceptance, disconnect, timeout and quarantine follow existing policies. Releases/cleanup remain prioritized.

The barrier proves local owner-matched neutral submission only. It does not prove host receipt, global key release or endpoint retirement. Restart does not repair NVS, reset settings, reconfigure USB, change EDR1 or normalize host lock state.

### Source seams and preservation

Coordinates below refer to the generated `EvilDuckS3/*` entries in `docs/text-keyboard-build.json`, verified against its source inventory, not uncomposed preview or legacy files:

| Seam | Current source evidence | Future change |
|---|---|---|
| Command, enums, execution limits | `core.cpp:283–365`; `core.h:6–19,94–113` | Exact statement plus appended instruction/event |
| Runtime lifecycle | `core.cpp:612–625,689–740` | Private rewind after accepted event; preserve borrow/budgets |
| Instruction dispatch | `core.cpp:742–767` | Emit cached Restart event; discard interrupted call/evaluation chain on rewind |
| Adapter result matching / STOP | `adapter.cpp:67–86,88–134` | Reuse existing reset admission/result path; preserve cancellation and counters |
| Neutral barrier | `seam.inc:16–21,78–89`; `com.cpp:643–648` | Reuse existing protected clear, no cancellation-as-restart |
| Coordinator identity | `coordinator.cpp:48–61,99–137` | Preserve request/lease and explicit engine selection |

Preserve all accepted text/keyboard, expressions/functions, preprocessing, randomization/jitter, lock feedback, EDR1, authentication, STOP, collision/rollover and quarantine behavior. No dependency/core/SDK, partition, descriptor, settings-schema or PSRAM changes are needed. Expect only bounded fixed state, not a second Program or source copy; exact size/RAM/stack impact requires a later approved build and must not be invented here.

## Proposed meaningful automated verification

Test actual composed modules with deterministic mocked clocks, HID, storage and randomness:

- Restart at top level, inside WHILE and inside a function suspended in an outer expression: no old return/operand/control state survives and following old-flow text stays unreachable.
- Exact neutral report before restarted output; held modifiers/nonmodifiers clear; matching request/session retained and operation IDs strictly increase.
- NoCall backpressure admits one clear; wrong/stale/duplicate results never rewind. STOP before admission, during retries and at callback completion wins; ambiguous acceptance/disconnect quarantines without replay.
- Program revision and borrow retained; zero source/storage callbacks after initial capture; attempts to mutate/reborrow fail under existing ownership rules.
- Variables and random/jitter defaults reset; DEFINE/functions remain compiled; discarded random/jitter choices cannot leak into a new operation. Fresh operations sample once and retries retain selections.
- Original elapsed/step/tick limits survive repeated restarts, including restart-only scripts, smaller caller budgets and uint32 clock wrap. No busy loop or nested synchronous execution.
- Request/Caps timing and cumulative diagnostic counters remain stable; no intermediate terminal status or external Start queue entry. Terminal cleanup and subsequent independent runs remain correct.
- Malformed retained source, exclusions, STOP/error cleanup, bounded REPEAT, aliases, RESET, keyboard ownership, preprocessing, randomization/jitter, lock feedback and EDR1 regressions.

Run relevant existing composed suites with ASan/UBSan/leak checks after a future implementation. Retain historical classifications and separate new results from existing 371-case receipts. A clean isolated approved-profile build/post-link check and exact accepted rollback binding would be required only after implementation authorization.

## Short future High Sierra acceptance sheet — not authorization

Use one explicit Start per trial, blank TextEdit, Caps off, recorded input source/build/request and accessible STOP. Never run a proposed fixture on the currently accepted firmware: it does not implement restart. No helper or LED protocol change is needed.

**1. Restart flow:** `STRINGLN 111restart`, `DELAY 3000`, `RESTART_PAYLOAD`, `STRINGLN 999bad` on separate lines. Observe the first two `111restart` lines, then STOP during the delay. Require Cancelled and no `999bad`; no automatic replay or precise timing claim.

**2. Held-state rewind:** `STRING a`, `HOLD SHIFT`, `DELAY 3000`, `RESTART_PAYLOAD`. Observe two lowercase `a` characters, then STOP during the second delay. Require Cancelled and normal harmless manual lowercase afterward. This tests local workflow only, not general host release guarantees.

**3. Malformed source:** `RESTART_PAYLOAD extra`. Require compile rejection and blank TextEdit; record actual request/line/code rather than predicting them.

Keep exhaustive reset/default/budget/race boundaries automated. Preserve screenshots and available identifiers. Missing evidence is UNVERIFIED; an isolated legacy-host constraint is PLATFORM-LIMITED, not universal failure. Candidate implementation and physical tests need separate review and authorization. Every future package must bind rollback to `53acc374ef38be652b6847d4b84f2dc7d42fa73a3dd54ea62d5208be4cbc0167` (1,412,400 bytes), not the older jitter image.
