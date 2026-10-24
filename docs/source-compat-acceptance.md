# Harmless owner acceptance sheet — review before any installation

No physical operation is authorized by this sheet. Keep the installed `ROUTEB-LOCK-FEEDBACK-20261023-v1` and its current rollback. New helper v4 and firmware candidate are separate deliveries: v4 remains bound to that installed lock-feedback build, not the preprocessing candidate. Do not change EDR1 or Caps timing for these tests.

## Helper v4 (existing installed firmware)

Follow `lock-feedback-helper-v4.md`. Prepare/compile before Start; explicit `APPLY ONCE`, one manually assigned request ID, fixed 15s DELAY / 5s WAIT and 3s focus countdown, no retries. Save native API results, helper exit, exact request ID, boot/session if available, timestamped Terminal log, TextEdit `111` and same-request dashboard status separately. Missing boot/session or log evidence remains unverified. Do not recycle another request's screenshot. No firmware is needed for this correction.

## Future preprocessing candidate (only after separate installation approval)

Confirm installed build `ROUTEB-PREPROCESS-20261024-v1` from reviewed package; autorun remains disabled. Open an empty TextEdit document. Explicitly save/start one harmless fixture at a time through dashboard Route B or CLI `routeb`, never the legacy CLI run path. No shell commands or host automation are part of any fixture.

Fixture 1:

```ducky
DEFINE #EXTRA FALSE
IF_DEFINED_TRUE #EXTRA
STRING BAD
ELSE_DEFINED
STRINGLN 111selected
END_IF_DEFINED
```

Require one exact line `111selected`, same-request `Completed` and no `BAD`. Capture request/boot/session, screenshots and diagnostics.

Fixture 2:

```ducky
EXTENSION Benign
VERSION 1.0
FUNCTION result()
RETURN 1
END_FUNCTION
END_EXTENSION
IF result() == 1 THEN
STRINGLN 222extension
END_IF
```

Require one exact `222extension` line and same-request `Completed`. Do not infer that arbitrary downloaded extensions or OS detection are supported.

Fixture 3:

```ducky
EXTENSION StopCheck
HOLD SHIFT
DELAY 10000
STRING BAD
END_EXTENSION
```

With blank TextEdit focused, explicitly start once; use dashboard `STOP` during delay. Require `Cancelled`, `BAD` absent, and harmless manually typed lowercase after cancellation. Keep `STOP` accessible. Local cleanup submission does not prove all physical USB/key-release guarantees. Do not automatically replay an ambiguous trial.

A deliberate malformed source with missing `END_IF_DEFINED` should reject before any text. Preserve its physical line/error diagnostic. `STOP` remains available. These tests validate only reviewed fixtures on the owner Mac running macOS 10.13.6; uncertain platform behavior is UNVERIFIED/PLATFORM-LIMITED, not universal failure. Windows 11 remains a later platform opportunity. No physical tests of this new candidate have occurred in Codex.
