# Composed Route B compatibility — random lowercase update

Read together with the baseline source-compatibility inventory; this table describes the actual composed candidate, not main, legacy CLI run, or uncomposed language_preview. Source evidence: `tests/random_lowercase/application.patch` and pinned parent chain. Working means bounded software support unless physical evidence is explicitly cited.

| Feature | Classification | Evidence / limit |
|---|---|---|
| RANDOM_LOWERCASE_LETTER | Working in offline tests; physically unverified | Exact no-argument instruction; official 26-letter set; one cached character per operation, bounded sampling; deterministic mocked composed reports. |
| INJECT_VAR | Unsupported / reference blocker | Explicit retained-source rejection; numeric format/modifiers/validity/locale/release contract unresolved. It is not decimal printing. |
| Random packed-keycode variables | Unsupported | Stage15 vectors stay null; no fake numeric encoding or user-variable shadowing claim. |
| Other random character commands, numeric RNG properties, seed controls, jitter | Missing in composed Route B | Deliberately outside this bounded group; no broader randomization success inferred. |
| HOLD/RELEASE and inline INJECT_MOD | Preserved | Existing lease/rollover/STOP behavior, exact reports; bare INJECT_MOD remains unsupported. |
| IF/WHILE/functions/variables/STRING | Preserved bounded subset | Single evaluator, existing cached continuation/event behavior; variables can control loop count but cannot capture a canonical packed random keycode. |
| Conditional preprocessing/extensions/VERSION | Preserved | Owner reports four baseline acceptance trials passed; fresh composed regressions retain limits and physical diagnostics. |
| Lock feedback and WAIT | Preserved partial support | Interface-specific observed evidence; fixed 5s waits and existing unknown/stale/session policies. No global Caps claim. |
| EDR1 | Unchanged | Existing custom fixed-message protocol and regression fixtures; no new LED return or capture capabilities. |

US keyboard translation remains the composed path. Native mocks verify report bytes, not physical host layout. A lower-letter selection while SHIFT is held produces the existing merged Shift report; host Caps/input-source settings may alter visible text. No automatic Caps normalization, new locale or arbitrary Unicode is claimed. Direct compiler BOM acceptance still does not bypass composed ASCII admission. Legacy/preview functionality is not substituted as evidence of composed support.
