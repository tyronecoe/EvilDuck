# Route B text and keyboard utilities — bounded contract

Baseline: `d30ec43aab0fe535afb3cbc79f80bcd2837c3129`. Isolated branch: `routeb-text-keyboard-utilities-v1`. Candidate build: `ROUTEB-TEXT-KEYBOARD-v1`.

This layer targets the actual composed Route B compiler/runtime/adapter, not legacy `run`, main alone or uncomposed preview code. It adds three related utilities while preserving the accepted randomization/jitter application and historical overlays.

## Embedded-language text blocks

Support these exact, argument-free block openers:

| STRING family | STRINGLN family |
|---|---|
| `STRING_POWERSHELL` | `STRINGLN_POWERSHELL` |
| `STRING_BATCH` | `STRINGLN_BATCH` |
| `STRING_BASH` | `STRINGLN_BASH` |
| `STRING_JAVASCRIPT` | `STRINGLN_JAVASCRIPT` |
| `STRING_PYTHON` | `STRINGLN_PYTHON` |
| `STRING_RUBY` | `STRINGLN_RUBY` |
| `STRING_HTML` | `STRINGLN_HTML` |

STRING aliases terminate with `END_STRING`; STRINGLN aliases terminate with `END_STRINGLN`. No suffixed closing form is invented. Inline arguments, unknown suffixes, mismatched delimiters and missing terminators reject safely. Reserve the new command names against function shadowing.

These are aliases for existing text blocks. STRING strips leading whitespace and joins lines; STRINGLN removes the first formatting tab and preserves remaining indentation and line breaks under the existing block engine's contract. Reuse its DEFINE expansion, literal command-looking body handling, source-line diagnostics, cooperative delivery and bounds. No host-language parser or interpreter executes the contents. Preserve plain STRING/STRINGLN behavior and do not silently widen ASCII admission, Unicode or layout support.

Reference: official [Keystroke Injection](https://documentation.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection.md), “Embedded Language Blocks”. Pro-only syntax highlighting does not make these text semantics Pro-only.

## RESET: clear and continue

Only exact, argument-free `RESET` is supported. It clears all script-owned held keys and modifiers using the existing neutral-report path, then continues the same execution. It must preserve user variables, random bounds, jitter settings, function/control state, request identity and the current owner lease. It is neither ESP reset nor payload restart.

Use an explicit event and owner-scoped scheduler admission. Do not call the script/session cancellation path to implement a continuing command. RESET bypasses jitter. Releases and cleanup keep their existing priority; do not add key-down dwell or new Caps timing behavior to a clear operation.

The continuation barrier is local: a newly requested neutral clear must satisfy the existing bounded submission/ownership accounting before later output is admitted. Queue invocation, accepted submission, local completion and host receipt are distinct. A local neutral submission does not prove host-global release. Backpressure remains cooperative; STOP, disconnects, timeouts, invalid observations and ambiguous acceptance retain existing cleanup/quarantine behavior. No retry may replay an ambiguously accepted operation.

Reference: official [Payload Control](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/payload-control.md), RESET clears the HID buffer without changing payload flow.

## Inline REPEAT: explicit bounded subset

Grammar:

```ducky
REPEAT 4 STRINGLN hello
REPEAT 3 TAB
REPEAT 10 RANDOM_NUMBER
```

The count is a decimal literal from **2 through 128**. No expression, hexadecimal count or runtime count variable is added. One inline leaf statement follows: nonempty STRING/STRINGLN text, DELAY with its existing expression grammar, a supported named key/chord, inline INJECT_MOD, or one of the six supported random-character commands.

Reject nested REPEAT, assignments, structural statements, standalone function calls, HOLD/RELEASE, RESET, WAIT commands and block openers as repeated bodies. Reject a missing body and bare `REPEAT 4`; do not fall back to history-based “repeat previous command”. REPLAY is not added.

Compile one validated leaf and lower to bounded copies sharing its operand storage. Yield between instruction copies; do not introduce an unbounded compiler loop or runtime expansion buffer. The total existing **128-instruction** program limit still applies, so a count of 128 does not promise that additional surrounding instructions fit. Other source/line/text/compiler/runtime budgets remain unchanged. All copies keep the physical REPEAT source line for diagnostics.

Each repeated runtime operation reevaluates its dynamic operand and random selection normally. Retries reuse that operation's selected value and do not advance to the next copy. DEFINE processing retains existing boundaries; do not manufacture arbitrary structural commands through substitution.

Primary evidence: the captured official Community `handleRepeat` delegates the inline body once per count, and the [v1.3.1 changelog](https://payloadstudio.hak5.org/community/CHANGELOG.html) demonstrates `REPEAT 4 TAB`. This differs from EvilDuck's legacy history-based REPEAT/REPLAY implementation. The numeric/body limits above are declared EvilDuck restrictions, not a full official repeat-grammar claim.

## Preservation boundary

Preserve checked expressions, functions, preprocessing, all six random-character commands, numeric ranges, jitter defaults and retry caching, inline INJECT_MOD, HOLD/RELEASE, lock-feedback evidence, EDR1, authentication and explicit engine selection. No USB identity, descriptor, partition, settings schema, SDK archive or global toolchain changes are needed. Keep Mac Caps timing unchanged. RESET is a keyboard clear, not an NVS/settings reset.

INJECT_VAR and stored random-keycode properties remain blocked pending independent official-runtime evidence. Preserve the completed research, reproduced checks and null runtime fields without repeating those checks or broad searches. RESTART_PAYLOAD, host-lock restoration and extra hardware-dependent commands remain outside this release.
