# Right-side modifier names on experimental H1 Route B

Candidate build: **ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1**. This is an additive, opt-in firmware composition over the owner-tested H1 application, including configurable lock waits. It is not a change to default non-H1 builders. The new source names are **EvilDuck extensions**; no exact canonical Hak5 spelling is asserted.

## Grammar and report representation

| Token | Existing USB modifier-byte bit | Keyboard usage for ownership |
|---|---:|---:|
| `RCTRL` | `0x10` | `0xE4` |
| `RSHIFT` | `0x20` | `0xE5` |
| `RALT` | `0x40` | `0xE6` |
| `RGUI` | `0x80` | `0xE7` |

These use the existing eight-bit keyboard modifier representation, report ID, descriptors and transport. They do not add an alternate keyboard implementation or alter layout selection. Right Alt is not a promise of general AltGr/dead-key/international-layout support. Host interpretation remains platform/layout dependent.

Each name is accepted wherever the existing Route B modifier vocabulary is used:

```ducky
RSHIFT a
CTRL-RSHIFT a
INJECT_MOD RCTRL
HOLD RSHIFT
RELEASE RSHIFT
```

The examples define grammar, not instructions to execute host shortcuts. Benign owner fixtures are provided separately. Existing left-side aliases keep their current meanings: CTRL/CONTROL `0x01`, SHIFT `0x02`, ALT/OPTION `0x04`, GUI/WINDOWS/COMMAND `0x08`.

Chord syntax still requires a terminal key operand. Modifier prefixes may use the existing whitespace/hyphen delimiters. Existing delimiter rejection remains: missing key, doubled hyphen, whitespace immediately after a hyphen or trailing extra operands do not silently acquire new meanings. Duplicate physical modifier bits in one chord reject, including aliases for the same bit. Left and right bits are distinct, so `SHIFT-RSHIFT a` is a valid two-bit chord. `INJECT_MOD` still takes exactly one modifier token; bare, list, numeric and extra-operand forms reject. HOLD/RELEASE still take one supported physical key/modifier per statement. Bare `RSHIFT` is not a sticky-mode command.

## Ownership and operation lifecycle

The shared source-name lookup feeds the established compiler events, runtime, adapter, scheduler and HID backend. Existing held/transient OR merging, six-key rollover/collision limits, fresh operation correlation and backpressure semantics remain. A transient release restores persistent held state. Repeated HOLD and release of an unheld key retain the established idempotent logical policy with a fresh operation's report admission. A modifier-only tap of an already-held same physical modifier refuses rather than pretending to generate a release/repress edge. Left versus right ownership remains distinguishable.

Completion, external STOP, STOP_PAYLOAD, RESET, restart and errors use existing neutral/owned-state cleanup. Ambiguous submission or loss retains quarantine and no automatic replay. Cooperative scheduling, wait evidence freshness, captured wait deadlines, cumulative execution budgets and per-run settings remain inherited. Local report submission/cleanup is not host acknowledgement, universal host-key release or USB endpoint-retirement proof.

## H1 contract is unchanged

The experimental packed `INJECT_VAR` scalar continues to use only its finite US-printable whitelist, with modifier zero or **left Shift `0x02`**. Named right-side modifier support does not admit high-byte `0x10`, `0x20`, `0x40` or `0x80` into that decoder. Random-keycode generation and ordinary variable storage/copy semantics are unchanged. Canonical Hak5 runtime encoding remains unresolved; no new reference study is implied.

The new candidate keeps H1 explicitly experimental. The source/text-v2 application remains the mandatory exact rollback: **1,413,200 bytes**, SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. The inherited H1 application is **1,414,080 bytes**, SHA-256 `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd`; its owner-scoped passes are preserved rather than overwritten by new physical claims.

The owner's [3/3 inherited lock-wait acceptance clarification](https://github.com/tyronecoe/EvilDuck/blob/routeb-h1-right-modifiers-v1/docs/h1-right-modifiers-owner-correction.md) is bundled into this development task. It requires no repeated milestone trial. New right-side behavior remains software-tested only until separately approved owner acceptance. No hardware operation, firmware installation or automatic payload execution is authorized by the source or package.
