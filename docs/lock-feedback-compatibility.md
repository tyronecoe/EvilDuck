# Route B host lock-feedback contract

This additive candidate uses the existing pinned composed Route B engine; it
never falls back to legacy execution. Dashboard Run/Save & Run select Route B;
ordinary CLI `run` remains legacy. CLI `routeb <file>` explicitly selects Route B.

| Read-only expression operand | Meaning |
|---|---|
| `$_NUMLOCK_ON` | Bit 0 of fresh validated EvilDuck keyboard LED output |
| `$_CAPSLOCK_ON` | Bit 1 of that output |
| `$_SCROLLLOCK_ON` | Bit 2 of that output |
| `$_RECEIVED_HOST_LOCK_LED_REPLY` | At least one accepted reply in the current USB session; historical within that session |
| `$_EVILDUCK_LOCK_KNOWN` | EvilDuck extension: fresh, usable evidence, age at most 5,000,000us |

The flags are Boolean 0/1. Unknown/stale lock-bit reads fail with
`FeedbackUnavailable`; they never fabricate OFF. Exhausted evidence fails all
reads. USB lifecycle invalidation clears history and establishes a new session.
Assignments, `VAR` shadowing, unknown internal names and timeout-variable writes
are rejected during all-branch preflight, including unused functions. Ordinary
variable identifier limits and the single bounded Stage 3-derived evaluator are
unchanged. A dedicated fixed internal token avoids lengthening ordinary symbols.

The existing evaluator is eager, **not short-circuiting**. A historical reply is
not a freshness guard. Use nested guards, and still handle a read becoming stale
between evaluation ticks:

```ducky
IF $_EVILDUCK_LOCK_KNOWN THEN
IF $_CAPSLOCK_ON THEN
STRING 111
END_IF
END_IF
```

Each internal operand is resolved once at its runtime evaluation point and cached
in the existing continuation. Preflight never samples the device. Multiple
operands are not one atomic device snapshot; each individual read is coherent.
Function suspension or HID backpressure does not repeat an already resolved
operand.

Exact no-argument commands are `WAIT_FOR_NUM_ON`, `WAIT_FOR_NUM_OFF`,
`WAIT_FOR_NUM_CHANGE`, and the same ON/OFF/CHANGE forms for CAPS and SCROLL.
ON/OFF accept an already fresh matching report, or await one. CHANGE establishes
a fresh baseline, then requires a later accepted report changing that specific
bit in the same boot/session. Fixed per-bit uint64 transition counts retain
rapid away/back transitions; identical or other-bit reports do not satisfy it.
Unknown/stale evidence waits without assuming a baseline. The fixed 5000ms
runtime-entry deadline never restarts and wins at the exact expiry boundary.
Existing overall 30s execution, step and tick limits may terminate a run sooner.
Waits are cooperative and separate from the existing 1000ms HID pending deadline.

| Condition | Result / cleanup |
|---|---|
| Missing feedback | Wait until original deadline; lock-bit reads fail |
| Stale report | No ON/OFF success or CHANGE baseline; historical reply may remain true |
| Fixed wait expiry | Deadline reason, Timeout diagnostic with source line; existing neutral cleanup |
| Boot/session change, evidence exhaustion | Unavailable diagnostic; cleanup |
| Disconnect/suspend/quarantine | Existing environment/loss refusal, cleanup or quarantine; no replay |
| Backward evidence clock | Latched exhaustion/unavailable; no assumed ordering |
| STOP / STOP_PAYLOAD / runtime error | Existing lease-owned priority neutral cleanup; no later text |
| Cleanup backpressure | Ownership retained until bounded clear succeeds or quarantine |

Official spellings and reply semantics are backed by the repository's saved
Stage 9/12 reference inventory and
[Hak5 lock keys](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/lock-keys.md),
[quick reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference.md).
The five-second freshness/deadline, failure policy and LOCK_KNOWN are explicit
EvilDuck safety policies, not claims of identical Hak5 timing. No new live online
reference behavior was assumed. SAVE/RESTORE and configurable LOCK_TIMEOUT remain
unsupported in Route B. HOLD/RELEASE/inline INJECT_MOD are preserved as previously
documented; no grammar or protocol expansion was made outside this group.

Evidence is interface-specific LED output actually received on the registered
EvilDuck keyboard (report ID 1), not the Mac global Caps flags or built-in LED.
EDR1 also generates LED reports; do not run it during physical lock-wait trials.
Its protocol, timing, fixed message and separate lifetime are unchanged.
Software callback tokens cannot authenticate a delayed USB report arriving after
reconnection: there is no on-wire boot/session token. Neither a received report
nor local neutral submission proves host-wide lock state or key release.
Scroll feedback and all new physical behavior remain UNVERIFIED. High Sierra
limitations must be separated from implementation failures; Windows 11 checks
remain a later platform opportunity, not a prerequisite for offline work.
