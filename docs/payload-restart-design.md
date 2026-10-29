# Route B bounded payload restart contract

Baseline: `7230bcddcdddd6b7e305f07721b7922df01dbd91`. Isolated branch: `routeb-payload-restart-v1`. Candidate build: `ROUTEB-PAYLOAD-RESTART-v1`. This additive layer targets the actual composed Route B compiler/runtime/adapter, not the legacy engine or standalone preview source.

## Grammar and reference boundary

```ducky
RESTART_PAYLOAD
```

Only the exact argument-free statement is supported, subject to existing whitespace/comment rules. Reject arguments, expressions, aliases and `REPEAT 2 RESTART_PAYLOAD`. Validate all retained source before output, including inactive runtime branches and unused functions; preprocessor-excluded source retains its existing distinct treatment.

Official [Payload Control](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/payload-control.md) documents ceasing current flow and restarting at the beginning, making following statements unreachable. The existing primary-source capture is recorded in `text-keyboard-references.json`, SHA-256 `8fde4569850a7fecb0a42c9aa95258977ebb8c7322622d9b84a379e0570bec7c`. No official runtime was executed here. The state lifetimes and finite limits below are explicit **EvilDuck policies**, not a claim of complete canonical runtime equivalence.

## Clear before rewind

The compiler appends a Restart instruction and a distinct Restart event without renumbering existing entries. Runtime retains that one event through retries. The adapter uses the existing owner-scoped `route_b::reset` neutral-clear operation, while preserving the event's Restart identity. Only the matching actual Done result can advance it; stale or duplicate observations cannot trigger rewind.

After that neutral submission barrier, a private runtime helper rewinds PC to zero. It does not call `Runtime::start()`, cancel the session, release/reborrow Program, reopen storage, recompile source or enqueue an external Start. It returns immediately so the first restarted instruction runs on a later cooperative tick. Restart bypasses typing jitter; releases and cleanup retain priority.

The barrier establishes fresh owner-matched local neutral **submission**. It is not proof of host receipt, host-global key release or endpoint retirement. Ordinary RESET remains a clear-and-continue command that preserves variables/settings; RESTART_PAYLOAD deliberately resets per-execution state.

## Reset and preserved state

On successful rewind, clear user values and initialization flags, call frames, expression continuations, return state, text/block/delay cursors, pending events and sampled random/jitter decisions. Restore random bounds 0–9 and jitter disabled/max20 ms. Keep randomness and feedback providers/context pointers; do not reseed entropy.

Preserve Program pointer/revision/borrow, compiled constants/functions/preprocessor selections, original source identity, request/session/lease, captured Caps timing, monotonic backend operation IDs, counters and first-fault history. Do not detach/reacquire, publish an intermediate terminal state or repeat initial synchronization.

Preserve original start time, cumulative steps/ticks and configured limits, including smaller valid caller limits. Existing maxima remain **10,000 steps, 100,000 ticks and 30 seconds elapsed**. Restart consumes ordinary work and cannot refresh these budgets. Exhaustion follows normal error/cleanup behavior; this differs deliberately from an indefinite illustrative official restart loop. Existing per-operation clear deadlines also remain effective.

STOP polling stays before runtime progress, including after scheduler/callback work. STOP/failure during clearing prevents rewind and later output. Not-ready transport is cooperative; disconnect, ambiguous acceptance, timeout and quarantine follow existing refusal/cleanup policies. No retry may replay ambiguously accepted output.

## Preservation

Preserve text aliases, inline REPEAT, RESET, functions/expressions, preprocessing, randomization/jitter, inline INJECT_MOD, HOLD/RELEASE, lock feedback, STOP, authentication, explicit engine selection and EDR1. No layout, USB identity/descriptor, partition, settings schema, SDK archive, PSRAM setting or global dependency changes are needed. Restart does not reset NVS, format storage, repair settings or normalize host lock state.

INJECT_VAR and stored random-keycode properties remain blocked pending independent official-runtime evidence. Their completed research and unresolved fields are unchanged. No broad Caps investigation or new reference search is part of this release.
