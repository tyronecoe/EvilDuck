# Compatibility update — bounded lock waits

Accepted starting firmware remains **ROUTEB-SOURCE-TEXT-PORTABILITY-v2** until separate owner acceptance. [Current baseline inventory](routeb-current-compatibility.md) is historical input, not silently rewritten.

| Capability | Candidate scope |
|---|---|
| $_EVILDUCK_LOCK_TIMEOUT | New read/write EvilDuck extension: default5000ms, inclusive1–65535, execution-local, reset by Start/restart, retained by RESET |
| Nine WAIT_FOR_NUM/CAPS/SCROLL_ON/OFF/CHANGE statements | Existing exact no-argument grammar; capture timeout once; cooperative immutable deadline |
| Freshness and transitions | Existing five-second freshness; same-boot/session counter policy preserved, no fabricated states |
| Other accepted features | Source/text v2, restart, RESET/REPEAT, keyboard ownership, inline INJECT_MOD, preprocessing, randomization/jitter, lock evidence and EDR1 preserved through composed regressions |
| INJECT_VAR / stored keycodes | Still blocked by unresolved independent official-runtime contract |
| SAVE/RESTORE, extra layouts, global Caps normalization | Deferred; no implementation or new host compatibility claim |

New bounded lock waits are physically unverified. Software tests are mocks over actual composed production modules, not physical USB or macOS execution. Older scoped owner results remain in [accepted v2 evidence](source-text-v2-accepted-baseline.json). No fresh compatibility percentage, general host-release guarantee, entropy-quality, precise latency or Windows claim is made.
