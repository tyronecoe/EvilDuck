# Combined randomization and cooperative jitter contract

Baseline: `9ebdb7195910a247921a7a4e032934fbc372cdc4`. Build: `ROUTEB-RANDOMIZATION-JITTER-v1`. New additive composition uses actual Route B compiler/runtime/report modules, not the legacy engine or an uncomposed preview.

## Exact grammar and alphabets

All six commands are argument-free and reserved against function shadowing:

| Command | Selection alphabet |
|---|---|
| RANDOM_LOWERCASE_LETTER | `abcdefghijklmnopqrstuvwxyz` |
| RANDOM_UPPERCASE_LETTER | `ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| RANDOM_LETTER | `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| RANDOM_NUMBER | `0123456789` |
| RANDOM_SPECIAL | `!@#$%^&*()` |
| RANDOM_CHAR | Lowercase + uppercase + digits + specials above: 72 characters |

The official RANDOM_CHAR table shows ambiguous whitespace between letter groups. The owner selected exclusion of whitespace. This is explicit EvilDuck policy, not verified official compiler behavior. Symbols use the current US report translation. Canadian/US lower-letter observations do not establish all symbol mappings on those input sources. No new layout support or Caps normalization is added.

## Numeric variables

`$_RANDOM_INT` is read-only; `$_RANDOM_MIN` and `$_RANDOM_MAX` are readable/writable unsigned16 settings, initialized to 0 and 9 on each execution. Use assignments, not VAR declarations, for internal settings. User declarations cannot shadow reserved internal names. Bounds may temporarily be reversed during sequential updates; drawing from a reversed interval fails explicitly with RandomRange. No clamping, repair or wrapping occurs. Both endpoints are included; equal bounds return the constant without consuming entropy. This endpoint/degenerate policy is supported by documented min/max intent and examples, but no primary numeric wire-format claim is made.

Literal and expression arithmetic retains the existing checked16-bit evaluator. Out-of-range literals, underflow, arithmetic overflow, bad target names and read-only assignments are rejected; invalid dynamic values fail during execution without subsequent output. Numeric values are calculations, not packed scancodes. INJECT_VAR, stored random-keycode properties and seed controls remain unsupported.

Each executed RANDOM_INT operand gets a new sample. A pending operand pins its bounds and attempt state; the postfix cursor yields at that operand until complete, preserving earlier operands and function continuations. Preflight never consumes entropy. A stored user variable reuses its captured integer normally.

## Bounded sampler and lifetime

One shared fixed-state sampler uses injected uint32 words, rejection threshold `2^32 - (2^32 mod width)`, width 1–65536 computed with wider arithmetic. It makes at most one provider draw per runtime tick and eight attempts per sample. Exhaustion, missing/failed/throwing provider, cancellation and reversed bounds are explicit errors/state transitions. Selection survives transport retries; accepted output is never replayed. Start/cancel/error reset pending sample/jitter state. All five runtime settings reset on start, including a reused Runtime object. The production provider remains `esp_random()`; no source/seed persistence change or cryptographic/physical entropy-quality claim.

## Jitter policy

`$_JITTER_ENABLED` is readable/writable Boolean (FALSE/TRUE or evaluated0/1). `$_JITTER_MAX` is readable/writable0–65535 milliseconds. Defaults on each execution are FALSE and20. Other Boolean values fail explicitly. Official docs describe variable cadence and defaults but leave endpoints, distribution and command boundaries underspecified. The following is the reviewed EvilDuck scheduling policy:

* Before each Character, KeyTap (individual key, chord or modifier tap) or HOLD operation, draw one inclusive delay0–MAX. STRINGLN/block newlines are key operations too. Cache the event and delay/start time across retries.
* RELEASE, transient release/restoration and STOP/error cleanup bypass jitter. The report scheduler, dwell and standalone Mac Caps500ms setting remain unchanged.
* The gate runs before press admission. It yields using wrap-safe uint32 elapsed time; no delay/sleep call, wait loop, new task or growing queue is added. Existing elapsed/tick budgets still apply: the default total runtime limit remains30 seconds, so a permitted65,535ms setting may produce a safely timed-out run rather than a completed character. No budget extension is implicit.
* Disabled jitter or MAX=0 adds no gate delay and consumes no entropy. Explicit DELAY and lock-feedback waits keep their existing behavior. Jitter adds a pre-press interval; it does not promise a total host-observed inter-key maximum.
* STOP/cancellation/disconnect prevents a pending gated press and clears pending state through existing ownership cleanup. A chord has one gate, not separate delays for report bytes/modifiers. HOLD may wait; RELEASE does not.

Authentication, explicit engine selection, preprocessing, functions, HOLD/RELEASE, inline INJECT_MOD, lock-feedback evidence, quarantine and EDR1 remain existing paths. Cleanup submission is not host delivery or global key-release proof.
