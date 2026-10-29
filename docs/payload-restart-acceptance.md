# Three-trial High Sierra acceptance — review only

Candidate: `ROUTEB-PAYLOAD-RESTART-v1`. This sheet does not authorize installation or physical testing. Keep accepted `ROUTEB-TEXT-KEYBOARD-v1` and its exact rollback until a separate owner review authorizes the new candidate.

For a future authorized trial, use macOS High Sierra10.13.6, blank TextEdit, Caps off, no manually held modifiers, recorded input source/build/request and explicit Route B selection. Keep STOP accessible and autorun disabled. One explicit Start per trial; no automatic replay. Never run these new restart fixtures on the old accepted firmware, which lacks restart. No LED helper or protocol change is needed.

## 1. Restart flow

```ducky
STRINGLN 111restart
DELAY 3000
RESTART_PAYLOAD
STRINGLN 999bad
```

Observe the first two `111restart` lines, then press STOP during the delay. Require Cancelled and no `999bad`. Associate visible text/status with the same request. This is not a precise timing or latency measurement.

## 2. Held-state rewind

```ducky
STRING a
HOLD SHIFT
DELAY 3000
RESTART_PAYLOAD
```

Observe two lowercase `a` characters, then press STOP during the second delay. Require Cancelled and normal harmless manual lowercase afterward. This tests the scoped local workflow, not general host-global release or USB retirement.

## 3. Malformed source

```ducky
RESTART_PAYLOAD extra
```

Require compile rejection and blank TextEdit. Record actual request/line/diagnostic rather than predicting them.

Keep exhaustive budget/default/race/boundary checks automated. Preserve screenshots, package/build identity, time, input source and available request/boot/session identifiers; leave missing identifiers unknown. Missing or ambiguous evidence is UNVERIFIED. An identified High Sierra tooling/host constraint is PLATFORM-LIMITED, not universal product failure. A demonstrated incorrect implementation result applies only to the tested conditions. No broad Caps campaign or Windows prerequisite is required for these independent Mac checks.
