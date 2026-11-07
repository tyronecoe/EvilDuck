# Bounded previous-command REPEAT — source-only contract

Status: local source implementation and offline verification; **no new target image, package or physical acceptance**.

The local branch `routeb-previous-command-repeat-v1` starts at clean
`fcba0385ce21662c7a504e0c9b6fba0dfa2c4f8d`. The complete parent composition is the
201-file static-response-repair tree, including experimental opt-in H1/right
modifiers, bounded lock waits, privacy, dashboard and editor repairs. This is not
an implementation against the uncomposed or legacy firmware tree.

## Grammar and counts

| Form | Bounded meaning |
|---|---|
| `REPEAT n leaf` | Existing form: literal decimal **2–128**, **n total** executions of the inline leaf |
| `leaf` followed by `REPEAT n` | New form: literal decimal **1–128**, **n additional** executions of that preceding eligible leaf |

The existing **128 total IR instructions** still applies. A lone `TAB` plus
`REPEAT 127` fits exactly; `TAB` plus `REPEAT 128` rejects before output. Other
instructions consume the same budget. Leading zeros use ordinary decimal
interpretation; surrounding whitespace uses the existing parser rules. Counts
are not expressions, variables, hexadecimal numbers or DEFINE substitutions.

The shared eligible subset remains exactly the old inline whitelist: nonempty
inline STRING/STRINGLN, all fourteen supported suffixed inline aliases (including
their matching same-line terminated forms), supported named keys/chords, inline
INJECT_MOD, DELAY and the six random-character commands. Closed multiline text
blocks are not eligible. No REPLAY, new keycodes or new host-language execution is
added. Literal END_STRING/END_STRINGLN in ordinary STRING/STRINGLN is unchanged.

Selection is lexical after preprocessing, not a runtime history of keyboard
events. Blank lines, REM/REM_BLOCK, DEFINE, preprocessing directives, excluded
source and EXTENSION/VERSION wrappers preserve it. An eligible DELAY replaces an
older text predecessor: `STRING x`, `DELAY 10`, `REPEAT 3` types one x and executes
four 10-ms delays.

Every retained IF/ELSE/ELSE IF/END_IF, WHILE/END_WHILE and
FUNCTION/RETURN/END_FUNCTION boundary invalidates selection. So does any
intervening ineligible executable statement, including assignments, HOLD/RELEASE,
RESET, RESTART_PAYLOAD, STOP_PAYLOAD, lock waits, function calls and H1 INJECT_VAR.
Multiline openers and closers explicitly invalidate it even though they bypass
the ordinary statement parser. Never search backwards past such a barrier.

Successful REPEAT consumes eligibility. A following standalone REPEAT needs a
fresh eligible leaf; comments/directives do not make chaining legal. Consecutive
inline forms remain supported, as does an inline form following a standalone
form. Nested inline REPEAT remains rejected.

| Failure | Existing diagnostic at the physical REPEAT line |
|---|---|
| Missing, zero, negative, malformed or nonliteral count | Syntax **15** |
| Count above 128, or expanded program above 128 instructions | CodeLimit **4** |
| No eligible predecessor, a barrier, or prohibited standalone chaining | Unsupported **14** |

Retained malformed source rejects before runtime, even inside inactive runtime
branches and unused functions. Preprocessor-excluded source remains excluded.

## Evidence and compatibility limits

The prior read-only investigation established these separate contracts; this
stage reuses those findings and does not rerun official compiler experiments:

- [Archived original Hak5 documentation](https://web.archive.org/web/20220414222651/https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript#repeat),
  captured 2022-04-14, explicitly describes n additional executions: its DOWN /
  REPEAT 100 example says 101 executions total.
- [PayloadStudio Community](https://payloadstudio.hak5.org/community/), encoder
  `5b4c1b5-271b6b-1690371896-STABLE`, handleRepeat lines 7705–7726, delegates the
  same-line body n times. Captured source SHA-256:
  `18efc91b48d8ada4e7aaaaebe0218e9bbc360360eb81ac182a63c4db9c10eee7`.
- [Official legacy repository archive](https://web.archive.org/web/20200805094201/https://github.com/hak5darren/USB-Rubber-Ducky)
  identifies commit `640ca08ddc04042c7c84a7ce3e040805b31a44a0`, dated 2016-12-07.
  Its exact [Encoder.java object surviving through the fork network](https://github.com/keland/USB-Rubber-Ducky/blob/640ca08ddc04042c7c84a7ce3e040805b31a44a0/Encoder/src/Encoder.java#L199)
  selects the preceding physical line, including DELAY. Chained REPEAT falls
  through key translation rather than implementing additive same-leaf history.
  Encoder v2.6.4 is a tool version, not evidence of a DuckyScript 2.0 generation.

Skipping comments/directives, lexical boundaries, eligible leaves, literal
bounds and explicit chaining refusal are **bounded EvilDuck policies**. They do
not reproduce every legacy encoder quirk. EvilDuck's separate legacy engine has
different runtime history behavior, including additive chains and skipping DELAY
for remembered keyboard history. This addition is not complete legacy-engine
equivalence or blanket Hak5 DuckyScript 3.0 certification.

## Implementation and preservation

The additive overlay changes only composed `core.cpp`; the other 200 files,
including `core.h`, runtime/HID/adapter/backend code, privacy/authentication,
storage, dashboard resources, build identity and dependency guards remain
byte-identical. Compiler methods are reorganized around one shared whitelist;
ordinary runtime evaluation/delivery code is untouched.

A 16-bit predecessor index references immutable IR. Standalone REPEAT reuses the
existing shared-operand copy state, attributes copies to its physical source
line, and generates at most one copy per cooperative compiler step. There is no
new opcode, runtime history, source reparse, text-arena duplication or allocation.
The new index is reset on compilation passes, abort/detach and new sessions.
Runtime restart uses the existing compiled program and carries no new history.

Each repeated operation follows normal fresh operand/random evaluation; pending
evaluations and transport retries retain their selected value. Existing limits,
STOP, release priority, held-state restoration, ownership, quarantine and
ambiguous-event no-replay behavior remain in their original paths. The fixed
compiler workspace must remain at most 4,096 bytes.

The normal source entry now supports `--compose-only --from-composed PATH
--output-dir NEW_PATH`. It verifies the exact complete parent, copies it to
`NEW_PATH/EvilDuckS3`, applies the pinned delta with zero fuzz/offset, then verifies
all 201 final sources. Wrong/omitted/duplicate overlays are refused.

Target builds fail closed in this source-only stage. Historical release verifiers
pin the older exact core; a separate target-integration stage must extend their
source bindings and assign a unique new build identity. No Arduino compiler is
invoked by this source entry. Fresh composition from the verified parent is
tested; raw target-scaffold reconstruction is not newly verified here.

The exact rollback remains **1,413,200 bytes**, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It was hash-checked without modification. This is standalone source/text-v2
application recovery, not a complete flash/filesystem backup. H1 remains opt-in
and experimental; canonical Hak5 numeric encoding remains unresolved.

## Scoped owner evidence and later acceptance

Preserve the supplied observations individually:

| Observation | Supplied result and limitation |
|---|---|
| T00–T04 and T06–T08 | Eight scoped owner-reported passes; original suite fixtures/complete receipts unavailable here |
| Original T05 / reduced T05R | Standalone REPEAT failure; Request 11, physical line 4, code 15; TextEdit blank |
| T05I | Request 14 Completed and owner-reported PASS; not an independent screenshot of TextEdit output |
| T05W | Owner-reported bounded WHILE equivalent PASS; request/session unknown |

Other missing identifiers remain unknown. Earlier editor HTTP 409 is separate
from this parser failure. The published static-response candidate does not prove
the exact application installed on hardware. No old pass is reopened and no
automatic physical retry is proposed.

After a separately authorized build, package and owner installation, use:

```ducky
DELAY 5000
STRING T05R:
STRING x
REPEAT 3
STRING :DONE
ENTER
```

Expect `T05R:xxxx:DONE` plus one Enter and the matching request Completed.
The unchanged inline control replaces the two middle statements with
`REPEAT 3 STRING x` and uses prefix T05I:; expect `T05I:xxx:DONE` plus one Enter.
First-line `REPEAT 3` must reject at line 1/code 14 with blank TextEdit. One short
held-Shift repeated-delay STOP check should show cancellation, no later suffix
and normal manually typed lowercase recovery. These checks are **not executed**
or authorized as part of this source-only stage.
