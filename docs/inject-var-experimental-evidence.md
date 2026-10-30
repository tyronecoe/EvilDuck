# INJECT_VAR: producer, storage, copy and consumer evidence

**The new compiler observations strengthen the trace but do not establish Hak5's runtime integer encoding.** H1 is a usable, explicitly chosen EvilDuck experiment; it is not a newly proven compatibility contract. No genuine DS3 runtime or physical keyboard experiment was executed here. The [machine-readable evidence](inject-var-experimental-reference-evidence.json) retains every `official_runtime_value` as null and records competing predictions with no winner.

## Preserved baseline and precise failure classification

Work starts from reviewed lock-wait commit `51583dd9008c98699f1eb082c42103bbff6c755a`. That release is software-tested, not yet owner-accepted. The latest accepted application is source/text v2, 1,413,200 bytes / `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`, as recorded in the [unchanged acceptance closeout](source-text-v2-acceptance-closeout.md). Its exact published application bytes remain rollback, not a rebuilt image.

The handoff's combined baseline is historical: `ROUTEB-RANDOMIZATION-JITTER-v1`, `d30ec43aab0fe535afb3cbc79f80bcd2837c3129`, 1,411,088 bytes / `2e1d8345417c6f23a5df3d884db42dd2a0f9f305120ee494c56a58048e677496`. Its four scoped High Sierra passes remain preserved. Its ZIP SHA `a25e703d…` differs legitimately from older uppercase ZIP `f3aa611d…`; neither is the application hash or the latest mandatory rollback.

The original physical failing INJECT_VAR fixture/transcript was not supplied in the evidence reviewed. The documented producer/store/repeat example exists, but is not a physical reproducer. These minimal examples are **new investigation fixtures**, not reconstructed owner observations:

```ducky
VAR $K = $_RANDOM_LOWER_LETTER_KEYCODE
INJECT_VAR $K
INJECT_VAR $K
```

Before the experiment, the composed parser does not recognize that getter. Separately, `VAR $K = 4` followed by `INJECT_VAR $K` reaches the explicit unsupported-command rejection. These are distinct pre-output admission failures; neither demonstrates wrong numeric decoding, wrong HID output, decimal printing or variable mutation on EvilDuck. Those paths were not implemented in the accepted firmware. The new experiment changes only its isolated composition.

## Sources and targeted retrieval

The requested current entry point [docs.hak5.org](https://docs.hak5.org/) and targeted randomization, variables and EXFIL paths all returned HTTP403 on 2026-10-30. Their current canonical redirect/contents were therefore **not verified**. Exact attempted URLs, timestamps and failures appear in the receipt; a failed request is not evidence that the feature is absent. Previously saved official statements remain the documentary basis, including [randomization](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/randomization.md), [variable EXFIL](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/exfiltration.md#variable-exfiltration), and the recorded reference inventory. No broad search or community compiler substitution was performed.

The public [PayloadStudio Community page](https://payloadstudio.hak5.org/community/) was successfully retrieved again, 605,048 bytes / SHA256 `18efc91b48d8ada4e7aaaaebe0218e9bbc360360eb81ac182a63c4db9c10eee7`, encoder `5b4c1b5-271b6b-1690371896-STABLE`. It exactly matches the earlier capture. The prior19-function/25-check receipt was read and preserved; those checks are not presented as freshly rerun main results. The prior public changelog associates this encoder with v1.3.1 (2023-06-26), and introduces INJECT_VAR/getters in v1.3.0 (2023-03-14). These are compiler release facts, not independently determined device-firmware dates.

USB-IF URLs specifically requesting HID1.11 and HUT1.5 also returned403. Those revision names identify attempted documents, not a fresh reading or a claim they are the newest revision. USB keyboard page07 usages/report structure explain downstream reports; they cannot independently establish a proprietary VM's scalar convention. No proprietary binary was reverse-engineered.

## Additional compiler trace: 18 checks, no runtime

The [new trace tool](../tests/inject_var_experimental/compiler_trace.py) extracts unchanged selected named functions/data from the hash-pinned page and executes them in Node with bounded VM/process timeouts. Append/logging/UI helpers are explicit mocks. It does not execute the full page, browser, outer compiler pipeline, official firmware VM or HID stack. Original source is consumed from a separately downloaded local capture; no Hak5 implementation is copied into EvilDuck firmware.

The new18 passing checks target assignment/copy/EXFIL seams omitted from the previous25. They have different evidence scope from the experimental firmware tests.

| Stage | Observed source/bytes | Meaning and boundary |
|---|---|---|
| Declaration/assignment dispatch | Page5896–5912 selects `handleAssignment`; inspected statically | Both source forms reach the same compiler handler; not runtime execution |
| Read lower getter into user variable | `handleAssignment("VAR $ORIGINAL = $_RANDOM_LOWER_LETTER_KEYCODE")` → `e801 0001 fa42 0000` | Assignment op, destination register1, reserved property selector, end marker; no sampled key value |
| Other five getters | Same structure with upper `fb42`, mixed letter `ff42`, number `fc42`, special `fd42`, combined `fe42` | Every handler identifies a runtime property; `requiresLangPack` becomes true |
| Compiler placeholder allocation | `allocateVar`6284–6291 and assignment encoding allocate user slots with `0000` | `varValues` holds compiler constant-pool/placeholder serialization, not live generated variables |
| Copy | `VAR $COPY = $ORIGINAL` → `e801 0002 0001 0000` | Copy instruction references source register1 and destination2. JS does not copy a sampled runtime key |
| Inject stored copy twice | `e9e9 0002 e9e9 0002` | Two consumer operations reference the same register. The handler does not implement key decoding or host release |
| Placeholder mutation check | Original/copy remain `0000` through these compiler calls | Establishes only compiler bookkeeping invariance; not official runtime mutation behavior |
| Literal initializer | `VAR $K = 0x0204` → `e801 0001 0002 0000`, with target placeholder `0000` and constant register2 `0402` | Initializer serialization and assignment references are separate representations |
| EXFIL original/copy | `f6e9 0001 f6e9 0002` | Selects variables for a runtime consumer; says nothing about output framing, byte order, completeness or flush |
| Final assembly | Page7967–8015 loops over source, conditionally calls `generateLangPack`, then prepends `varValues` between `E8E8` markers | Static inspection only; no full-compilation claim |

The ordinary mappings and US-map identity remain independently known from the earlier captured public functions: `a`→usage04/mod00, `Z`→1d/02, `0`→27/00, `!`→1e/02. `generateLangPack`7892–7909 deliberately overwrites each entry's modifier with Shift before joining its bytes. Thus lowercase `LANG_a=0402` **cannot** be treated as a lowercase getter runtime value. Actual official scalar production, copy mutation behavior, decode and release remain unavailable.

The page also assigns distinct selector families: ASCII random properties42F4–42F9 versus KEYCODE properties42FA–42FF. This supports the documented distinction between character integers and stored keyboard actions, but does not experimentally exclude an ASCII-like runtime representation plus transformation.

## Competing explanations and concrete falsifiers

`compare_hypotheses` in the trace tool computes alternatives from independently known US strokes. Five separate algorithmic checks ensure the comparison does not declare a winner when observations are absent. A synthetic counterexample shows that 0x0402 paired with an independently established Shift+A stroke would contradict H1 and fit H2; the synthetic value is clearly labeled and is not stored as an official runtime observation.

| Intended US action, Caps off | Known usage/modifier | H1 prediction | H2 swapped prediction | ASCII-like prediction | Observed official runtime scalar |
|---|---|---|---|---|---|
| a |04/00|0004|0400|0061|UNKNOWN|
| A |04/02|0204|0402|0041|UNKNOWN|
| Z |1d/02|021d|1d02|005a|UNKNOWN|
| 0 |27/00|0027|2700|0030|UNKNOWN|
| ! |1e/02|021e|1e02|0021|UNKNOWN|
| # |20/02|0220|2002|0023|UNKNOWN|

The normalized expected report for A is `[02,00,04,00,00,00,00,00]` through the existing EvilDuck reportID1 convention. This is a downstream US/HID mapping expectation, not a scalar-encoding or physical transport observation. The receipt records corresponding reports for the six examples without calling H1's decoder.

- **H1 usage-low/modifier-high:** consistent with the single-stroke table field structure and a reasonable experimental choice. Falsify canonical H1 for a tested sample with calibrated genuine runtime scalar+independently correlated US action that differs from its prediction. Lowercase table entries still require an unseen runtime case transformation.
- **H2 usage-high/modifier-low:** not excluded. Numeric constants and register operands use different serialization helpers, so a byte-order analogy is insufficient. The same calibrated sample distinguishes H1/H2 where their predictions differ.
- **ASCII/index/tag/runtime transformation:** the register-reference consumer leaves room for a decoder lookup or transformation. No versioned tag/index rule was retrieved, so those broad alternatives have no honest numeric prediction yet. They cannot be ruled out by rejecting values from EvilDuck's chosen whitelist.
- **Forced-Shift table explanation:** both candidate runtime decoders could alter table cells for lowercase. A cell labeled a with bytes0402 therefore selects neither hypothesis. It must not be used as a synthetic official observation to choose a winner.

All these explanations remain underdetermined by available compiler evidence. No observed runtime result contradicts H1; there also is no observed runtime result proving it. The experimental whitelist, zero/65535 refusals, US layout scope, held-state merge and release policy are EvilDuck design decisions, not results of these reference checks.

## Smallest decisive reference result and implementation boundary

Use the separately prepared synthetic-only reference kit: calibrate raw EXFIL constants first, then capture a generated key once, copy it, record original/copy before and after two injections, and correlate the visible pair and device/compiler/layout/Caps context. A dedicated generated result region prevents unrelated historical data from being mistaken for this trial. Do not examine owner files, execute a host shell, collect normal typing or replay automatically. This task prepares that procedure; it does not perform it.

The current Route B has appropriate reusable seams: checked uint16 variables/continuations, bounded random sampler, `KeyTap` event, owner-scoped `route_b::key`, held/transient merge, restoration and STOP/error/disconnect cleanup. A prototype can define H1 explicitly and test those paths without changing historical profiles. Such passes establish practical selected EvilDuck behavior only. They do not fill historical null vectors, attest genuine DS3 behavior, demonstrate physical High Sierra operation or justify a canonical-compatibility label.

**Statuses:** compiler assignment/copy emission CONFIRMED within selected-function scope; official runtime scalar encoding UNRESOLVED; opt-in H1 experimental policy technically justified for software investigation; physical behavior NOT TESTED. The prototype's implementation/build receipts remain separate from this evidence report.
