# Next Route B release recommendation — proposal only

The accepted starting point is **ROUTEB-SOURCE-TEXT-PORTABILITY-v2**, release `789815a70544e0b8f3967f8ab68d9f4f1f4e5f62`. The exact application is **1,413,200 bytes**, SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. See the [accepted-baseline record](source-text-v2-accepted-baseline.json) and [current composed inventory](routeb-current-compatibility.md). This document replaces the older next-release recommendation for present planning; its historical restart proposal and receipts remain unchanged.

Recommend one small **configurable cooperative lock-wait deadline** release. It would reuse the existing legacy spelling `$_EVILDUCK_LOCK_TIMEOUT` as an explicitly labeled **EvilDuck extension**, not a newly claimed Hak5 command or canonical internal property. No proposed behavior is implemented by this closeout. Implementation, a build/package and any physical test require later approval.

## Benefit and alternatives

| Rank / group | Practical benefit and reference strength | Risk and verification cost |
|---|---|---|
| 1. Configurable bounded lock waits | Let a script choose a short failure window or allow more than five seconds for a supervised interaction. The project already specifies this property in the legacy engine; current Route B has a fixed five-second deadline. | Low–medium: fixed state and deadline plumbing through the existing evaluator/event/adapter. No additional LED or HID action. Boundary, lifetime, retry and cancellation tests are essential. |
| 2. SAVE/RESTORE host keyboard lock state | Official command spellings are established in the existing lock-key references; useful for scripts that deliberately alter lock state. | Higher: active Caps/Num/Scroll taps, confirmation, host behavior and restoration ambiguity. The existing Mac observations do not prove reliable global restoration. Do not reopen broad Caps diagnostics to make this the next release. |
| 3. One explicitly selected additional keyboard layout | Useful for a concrete non-US punctuation requirement; general layout selection is documented. | Higher: no additional target/map has been selected and independently verified. Canadian/US example passes do not validate a complete map or dead-key behavior. Defer until a concrete target exists. |

No significant reproducible safety defect was established in this targeted review. The proposed timeout is a usability improvement, not a fix for Mac LED delivery, USB retirement, stale feedback or a demonstrated firmware fault. It does not make a longer wait outlive the existing whole-request budgets.

## Exact proposed contract

```ducky
$_EVILDUCK_LOCK_TIMEOUT = 10000
WAIT_FOR_CAPS_ON
```

- Add one read/write numeric internal property, in **milliseconds**, valid **1–65535 inclusive**, default **5000**. Use the existing bounded uint16 expression evaluator for assignments and reads; no `VAR` declaration, shadowing, persistence, new WAIT arguments or aliases. Preserve arithmetic overflow/error policy; do not clamp or wrap an invalid value.
- A statically known invalid assignment must reject during retained-source preflight. A dynamically computed invalid assignment must fail at its source line before changing the setting or starting its subsequent wait. Invalid retained statements in inactive runtime branches and unused functions still reject; preprocessor exclusions retain their existing distinct contract.
- Each assignment evaluates once through the existing continuation. Each of the nine existing `WAIT_FOR_NUM/CAPS/SCROLL_ON/OFF/CHANGE` operations captures the current value once when the wait event is created; its adapter deadline starts on first wait entry. Retries retain that captured value and original start time. A mismatched command or timeout while an operation is pending must fail, not reset the deadline.
- Expiry is `elapsed >= captured_timeout`; expiry wins over matching evidence at exactly that boundary. Use the existing wrap-safe uint32 elapsed comparison. No unbounded waits or automatic retries/restarts are added.
- Restore 5000 on a new execution and `RESTART_PAYLOAD`; ordinary `RESET` retains the setting, like current random/jitter settings. Keep it in execution-local fixed state, never NVS or settings. A later run cannot inherit it.
- Keep **five-second LED-evidence freshness independent** of the chosen wait duration. ON/OFF still require fresh matching evidence; CHANGE still needs a fresh baseline and a later bit transition in the same boot/session. Unknown/stale evidence never becomes OFF, and identical/other-bit reports do not satisfy CHANGE.
- Preserve the original whole-request **30-second elapsed**, step and tick budgets, including smaller caller budgets. A setting of 65535 is representable but cannot override those limits. Preserve the separate HID-operation and cleanup deadlines.
- Preserve owner/request/lease identity, cooperative scheduling, STOP priority, held-state restoration, collision/rollover checks, disconnect/error cleanup and ambiguity/quarantine. The property itself sends no lock-key action, HID report or LED request and changes no EDR1 protocol/timing.

## Evidence and future implementation boundary

The coordinates below refer to the actual generated `EvilDuckS3` tree bound by the **201-file** [v2 build receipt](source-text-v2-build.json), not uncomposed preview or legacy sources. The source composition is rooted at [the v2 preparation layer](../tests/source_text_v2/prepare_sources.py), which retains all earlier pinned layers.

| Seam | Verified current source | Proposed bounded change, if approved |
|---|---|---|
| Internal operand recognition | `core.cpp:141–143` recognizes ten internal operands | Append the timeout operand ID; preserve existing IDs and resolve the value from Runtime state rather than the feedback provider. |
| Assignment/preflight | `core.cpp:319–327` recognizes four writable settings | Append a timeout setting selector and apply the same evaluator; add known-value 1–65535 validation without evaluating device/random providers during compilation. |
| Runtime setting/evaluation | `core.h:109`; `core.cpp:676–697,791–794` | Add one fixed uint16 setting and one read case; validate dynamic zero before committing. Continue cached expression/function evaluation with no second evaluation. |
| Lifecycle | `core.cpp:648–655,725–732,795–796` | Default on Start and restart rewind; preserve across keyboard-only RESET. Do not call Start from restart or refresh execution budgets. |
| Wait event | `core.h:94–97`; `core.cpp:805` currently carries only the wait selector | Append a dedicated uint16 `waitTimeoutMs` member to the in-process Event with default 5000 for existing aggregate producers; Runtime explicitly captures its setting when constructing LockWait. Other event kinds ignore this member. Preserve all current enum numbers, report fields and existing aggregate argument meanings. This is not an HTTP or USB wire-field change. |
| Wait deadline | `adapter.h:14–17`; `adapter.cpp:51–64`, especially fixed `5000` at line 56 | Capture/validate the event timeout on first entry, require it unchanged on Retry, and compare against the existing start timestamp. Keep session, transition, freshness, timeout diagnostic and cleanup behavior. |

The name/range/default are independently documented project behavior in [the Stage14 internal-variable matrix](stage14-internal-variable-matrix.md#explicit-evilduck-extensions), with actual legacy assignment/range/lifetime cases in [Stage12 tests](../tests/stage12/test_main.cpp) and legacy wait use in `EvilDuckS3/com.cpp:192`. They are **not** evidence that the property currently works through Route B. The [current lock-feedback contract](lock-feedback-compatibility.md) explicitly says Route B lacks configurable timeouts.

Official [lock keys](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/lock-keys.md) and the recorded [reference inventory](stage9-reference-sources.json) support the existing wait spellings and feedback distinction. They do not establish this extension's finite timing policy. Targeted direct requests for lock-keys, operators and delay Markdown returned HTTP403 during planning; no new official-runtime evidence was obtained or inferred. Existing evidence also does not justify adding unary `!`/`~`, `+=`/`++` or guessed keycode encodings under a canonical compatibility claim.

Expected resource impact is a few fixed scalar fields and one Event member; there is no reason for heap allocation, a second interpreter or source copies. Exact application/RAM/frame effects require a later authorized clean build and post-link check; none were measured for this recommendation. Preserve all dependency guards, USB identity, layout, authentication, explicit engine selection, source/text/BOM grammar, EDR1 and accepted features.

## Meaningful automated verification for a later implementation

Run the actual newly composed modules with mocked storage, HID and clocks, extending existing lock-feedback tests rather than replacing the engine with a stand-in. Existing [N27 and N34](../tests/lock_feedback/test_main.cpp) cover exact-expiry priority and the independent freshness boundary; they are starting points, not evidence for the proposed feature.

- Read default5000; assign/read 1,5000,65535 and expressions/function results. Reject zero, overflow, declarations/shadowing and malformed retained source before output where statically knowable; dynamic invalid assignments fail without accepting the new setting or beginning a wait.
- Test before/at/after expiry, uint32 wrap, a matching report at exact expiry, and 65535 limited by the unchanged whole-request budget. Repeated Retry, wrong/mutated pending timeout, callbacks and function suspension cannot refresh the original deadline or reevaluate an operand.
- Exercise all nine waits, already matching fresh states, absent/stale feedback, CHANGE baseline and same-session transitions, rapid away/back transitions and session/exhaustion errors. Extending the wait never extends freshness or fabricates a state.
- Test new-run and restart defaults, RESET preservation, two successive waits with different captured settings, STOP before and during a wait, held Shift cleanup, disconnects, cleanup backpressure/quarantine and subsequent-run isolation. Compare exact mock reports; changing this property must add no HID/LED operation.
- Rerun relevant ownership/keyboard, lock-feedback, randomization/jitter, source/text/BOM, preprocessing, restart, authentication and EDR1 regressions; run applicable ASan/UBSan/leak checks. Keep fresh results separate from inspected historical receipts. Only after implementation approval and successful checks should a clean approved-profile build and a new review package be considered.

## Three short future High Sierra trials — not authorization

Run these only after a future candidate is approved for installation and the owner separately authorizes testing. They are **not supported by the current accepted v2 firmware**. Keep blank TextEdit, known input source/Caps state, build/request evidence, accessible STOP, autorun disabled and one deliberate Start per trial. No native LED helper or EDR1 session is needed for these passive deadline checks.

1. **Setting and defaults:** use conditional branches to emit `111default` only when the initial value is5000; assign10000 and emit `222set` only on readback equality; execute RESET and emit `333reset` only when10000 remains. A separate deliberate run verifies default5000 again. Exhaustive restart/default checks stay automated; no timer accuracy claim is made from visible output.
2. **Bounded wait:** set1000, enter `WAIT_FOR_CAPS_CHANGE`, then place `STRINGLN 999bad` afterward. Do not deliberately change any lock state. Record the actual request, terminal timeout diagnostic and blank TextEdit. If an unexpected qualifying transition completes the wait, or a disconnect/other budget intervenes, preserve the result as inconclusive for timeout acceptance and do not automatically replay. The trial does not prove LED delivery, host-global state or precise one-second timing.
3. **STOP and held-Shift recovery:** set10000, HOLD SHIFT, enter `WAIT_FOR_CAPS_CHANGE`, then place unwanted marker text afterward. Correlate the actual running request with **`routeBWaiting=true` in the existing authenticated `/status` response**, then STOP once. The current visible dashboard does not display a dedicated waiting label; do not invent one. Require scoped Cancelled status, absent marker and harmless manual lowercase afterward. If the wait completes before STOP, do not claim the intended cancellation window was tested or replay automatically. Existing `routeBWaitCommand`, `routeBWaitStartedMs` and `routeBWaitSession` fields can help preserve that correlation (`C:webserver.cpp:592` in the hash-bound v2 tree); no new endpoint or helper is required.

Treat identifiable High Sierra/tooling limitations as platform-limited and missing/ambiguous evidence as unverified. Windows availability is not a prerequisite. Do not reopen broad Caps diagnostics or expand layouts for this group.

Every future package must contain exact rollback to the accepted v2 application above, reused from the published ZIP, not rebuilt. The earlier restart application is now an older recovery resource. **INJECT_VAR and stored random-keycode properties remain blocked** pending independent official-runtime evidence. This closeout authorizes no firmware implementation, build, new package, hardware access, HID execution, flashing or OTA.
