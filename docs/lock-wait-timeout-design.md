# Bounded cooperative lock waits — EvilDuck extension

Candidate **ROUTEB-LOCK-WAIT-TIMEOUT-v1**, isolated from accepted source/text v2. Exact syntax:

```ducky
$_EVILDUCK_LOCK_TIMEOUT = 10000
WAIT_FOR_CAPS_ON
```

The property reads/writes uint16 milliseconds, range1–65535 inclusive, default5000. It is a project usability extension, not a new canonical Hak5 property and not a fix for host LED delivery. No declaration/shadowing, clamping/wrapping, persistence, new WAIT arguments or aliases. Internal operand10 and setting selector4 are appended; existing IDs remain. Known-zero retained assignments reject during both statement parsing and final validation, with no provider sampling. Runtime-derived zero fails at its assignment before the setting changes. Existing overflow/undefined/function diagnostics remain.

Runtime state is fixed-size. Each of nine LockWait events captures its timeout once. Event appends `waitTimeoutMs=5000` after existing members, preserving existing aggregate argument meanings. Adapter first entry records timeout, selector, start, boot and session; retries require identical selector/timeout and never restart the deadline. uint32 elapsed >= timeout expires; expiry wins over matching evidence at that boundary. New Start and RESTART_PAYLOAD restore5000; keyboard RESET retains the setting. Original cumulative30s/step/tick budgets and smaller caller budgets survive restart.65535ms cannot override them. No source/Program copy, new heap, settings/NVS write or extra HID/LED action.

Freshness remains the existing independent five-second evidence-clock policy. Every attempted wait reads coherent interface-specific evidence. Exhaustion/session failures remain errors. After checking wait expiry, a stale/unknown snapshot retries. A fresh snapshot may acquire CHANGE's baseline; a subsequent fresh snapshot succeeds if the same-bit transition counter advanced. The baseline survives stale intervals, and rapid away/back transitions remain detectable. This does not establish a timestamp for every individual transition: no stronger freshness guarantee for the transition itself is invented. ON/OFF require fresh matching evidence, including fresh reports arriving after5s within a longer wait. Unknown never means OFF; other-bit/identical reports do not satisfy CHANGE.

Only five generated sources change: core.cpp/core.h, adapter.cpp/adapter.h and caps_trial.h. Exact before/after/patch hashes are in [source manifest](../tests/lock_wait_timeout/source-manifest.json). All earlier layers and guards remain pinned; [prepare](../tests/lock_wait_timeout/prepare_sources.py) applies only to disposable copies. STOP/cleanup, ownership, held reports, rollover/collisions, EDR1, authentication, source/BOM/alias/preprocessing and USB/layout/partition policies remain unchanged. INJECT_VAR stays blocked.
