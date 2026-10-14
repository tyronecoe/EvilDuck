# Stage28G reference decision — made before code changes

**Decision: BLOCKED source modifier ownership / INJECT_MOD and RESET implementation.**
Deliver reference analysis and additional deterministic rejection/fault tests only. Do not change
language_preview or guess prefix scope. All runtime/compiler/planner/bridge bytes remain Stage28F.

Four official saved Stage9 snapshots were independently hash/size verified against Stage28F
provenance. Live .md retrieval at the observation times in stage28g-reference-evidence.json
returned403 for all four. No current-version claim, published compiler version or authorized
behavior oracle is available. Cached reference footer instructions are not project instructions;
examples were read as evidence, never executed. No proprietary compiler source used.

References:

1. [Holding Keys](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/holding-keys), sections HOLD and RELEASE, Holding Modifier Keys, Holding Multiple Keys.
2. [Quick Reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference), Holding Keys and Payload Control.
3. [Keystroke Injection](https://documentation.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection), Standalone Modifier Keys.
4. [Payload Control](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/payload-control), RESET.

## Concrete evidence and contradictions

Holding Modifier Keys example uses:

```
INJECT_MOD
HOLD CONTROL
DELAY 4000
RELEASE CONTROL
```

Holding Multiple Keys instead repeats the prefix before release:

```
INJECT_MOD
HOLD CONTROL
DELAY 5000
INJECT_MOD
RELEASE CONTROL
```

Quick Reference repeats the first pattern using WINDOWS, no second prefix before release.
Keystroke Injection says standalone modifiers must be prefixed; its example uses the SAME LINE
`INJECT_MOD WINDOWS`, while its explanatory result refers to INJECT_MOD on the line above.
These may be shorthand/redundant examples, not necessarily incompatible compiler behaviors,
but do not independently establish whether scope is one operation, held modifier, session or
something else. Resolving by assumption would invent semantics, especially across branching.

Payload Control is stronger than the quick-reference summary alone: says RESET clears the HID
keystroke buffer without changing payload flow; example omits RELEASE SHIFT and explicitly
explains 'the RESET command released all keys'. This verifies that example's release-all effect,
not an independent-owner ownership policy or acknowledgement/drain contract. Our owner0–2 setup
sources are an EvilDuck mock extension, absent from the reference's single-payload model.

| Question | Classification | Evidence / missing requirement |
|---|---|---|
| HOLD key / RELEASE key with required key operand | VERIFIED text | Holding Keys; existing Stage28F subset retained |
| Canonical uppercase INJECT_MOD and modifier commands appear | VERIFIED text | All cited examples; not complete grammar proof |
| GUI/WINDOWS aliases for standalone modifier | VERIFIED text | Keystroke Injection describes GUI alias; no implemented source modifier support |
| CONTROL/SHIFT/ALT modifier names | VERIFIED text | Holding Keys introductory modifier list; no edge/scope oracle |
| One-shot prefix consumed by next command | BLOCKED | Not established by contradictory release/example layouts |
| Prefix persists through DELAY or applies to matching RELEASE | BLOCKED | Single-prefix examples suggest this but do not define lifecycle |
| Prefix before ordinary text/nonmodifier HOLD | BLOCKED | No consumption rule established |
| Prefix across IF/WHILE/function/RETURN boundary | BLOCKED | No authoritative lifecycle specification |
| Repeated prefix, failed prefix, cancel/new compile/restart | BLOCKED | No authoritative state/reset contract |
| Prefix operand alias case or right-side modifier names | BLOCKED | No broadened grammar from intuition |
| RESET clears buffer and releases keys in example, not reboot/restart | VERIFIED text | Payload Control explicit result |
| RESET clears script owner3 versus independent owners0–2 | BLOCKED | Independent owners do not exist in reference model |
| RESET during Retry/in-flight report or source acknowledgement | BLOCKED | No complete reference transport/state contract |
| Stage28F idempotent HOLD/RELEASE and fresh union acceptance | INFERRED-MOCK-POLICY | Explicit engineering policy, unchanged |
| Prepared modifier bitmap union; owner3 selective nonmodifier release | INFERRED-MOCK-POLICY | Existing bounded planner/bridge contract, tests verify mock behavior |
| Cancel/STOP clears intent, explicit current-action zero drain | INFERRED-MOCK-POLICY | Does not imply host received physical release |

## Implemented / rejected domain

No new aliases, prefix forms or opcodes. HOLD/RELEASE retain lowercase a–z, digits0–9 and the ten
existing nonmodifier named keys. Modifier names, inline or standalone INJECT_MOD, RESET and
invented release-all forms reject during full preflight even in inactive branches/functions.
Comment/text bodies remain literal, so rejected keyword-looking text there is data, not a prefix.
DEFINE cannot manufacture a structural command; malformed operand expansion fails atomically.
Failed compile cannot publish prefix state because no prefix state exists. Active Program borrowing,
new sessions, cancellation, drain and restart preserve their prior guards and lifetime boundaries.

What would unblock implementation: independently sourced specification or properly authorized
non-keyboard behavior oracle vectors covering BOTH prefix forms, required release prefix,
intervening statements, branches, loops/functions, repeated prefixes and reset/owner scope.
No real HID experiment is authorized. An explicit EvilDuck extension profile is an alternative
future reviewed decision, not official compatibility and not added here.
