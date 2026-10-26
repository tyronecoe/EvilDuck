# Actual composed Route B — text/keyboard utilities inventory

This table describes the separately composed `ROUTEB-TEXT-KEYBOARD-v1` candidate. “Working” requires the new software receipts; physical acceptance is separate. Baseline source is `d30ec43aab0fe535afb3cbc79f80bcd2837c3129`.

| Capability | Accepted composed baseline | Verified software candidate behavior / limit |
|---|---|---|
| Fourteen embedded-language STRING/STRINGLN aliases | Missing; available only in legacy Stage13 | Reuse ordinary streamed blocks; seven exact suffixes, no embedded execution, ordinary END_STRING/END_STRINGLN termination. Working in composed native tests; physical verification pending. |
| RESET keyboard-buffer clear | Reserved but Unsupported; legacy path exists | Owner-scoped neutral clear and local barrier, then continue; no variable/settings/flow reset or host-release guarantee. Working in composed native tests; physical verification pending. |
| Inline REPEAT | Missing; legacy has different history semantics | Decimal2–128 and one permitted inline leaf, total128IR limit; no nested/bodyless/history fallback. Working in composed native tests; physical verification pending. |
| Plain text/blocks and DEFINE | Existing bounded support | Preserve formatting, expansion boundaries and physical-line diagnostics. |
| Variables, IF/WHILE, functions and RETURN | Existing bounded support | Preserve evaluator, function continuations and budgets. |
| Preprocessing/EXTENSION/VERSION | Existing bounded support | Preserve exclusions, wrapper limits and malformed retained-source rejection. |
| Random character groups, RANDOM_INT/MIN/MAX, jitter | Existing support plus scoped owner passes | Preserve sampler limits, per-run defaults, cache/retry behavior and arithmetic policies. |
| HOLD/RELEASE, inline INJECT_MOD, STOP | Existing support plus scoped owner passes | Preserve lease, merging/restoration, collisions, rollover and cancellation/quarantine. |
| Lock feedback, bounded WAIT, EDR1 | Existing partial or tested-configuration support | Preserve interface-specific evidence and custom fixed-message protocol. No broad Caps claims. |
| INJECT_VAR and stored random-keycode properties | Blocked | Independent official-runtime encoding/release evidence still missing. Research remains complete and unchanged. |
| RESTART_PAYLOAD, host-lock restoration, new hardware commands | Outside release | Do not infer support from legacy files or introduce guessed contracts. |

ASCII admission, US device mapping, source/line/IR/text limits, finite execution/wait budgets and inline-only INJECT_MOD remain deliberate restrictions. No universal keyboard-layout or DuckyScript3 certification is claimed. See `text-keyboard-design.md` for exact new syntax and policies.
