# Composed Route B compatibility inventory

Consolidated **2026-11-08**. This inventory distinguishes selected source
acceptance, runtime semantics, USB capability and demonstrated host outcome.
It is not a percentage or a claim that every downloadable Hak5 payload works.

## Baseline and evidence identities

| Identity | Current record |
|---|---|
| Latest owner-recorded installed release | `ROUTEB-DEL-ALIAS-H1-v1`; intended release identity, full running dashboard ID unavailable |
| Recorded DEL firmware checkpoint | `2e3efa295d46aef55b4d39af9cf3a9a40bb70422` |
| DEL application | 1,437,888 bytes; SHA-256 `d1571be81619e464ee997d0ba8ebbf7e7b8a8b4252e4debc9d9144b9ebe6b379` |
| DEL publication checkpoint | `6bcfb605c8249b63be2be9f79a00e4e81863fbf6` |
| DEL publication ZIP | 2,644,497 bytes; SHA-256 `6dbc548c0e58714511c77f29ef50449f07d3ed94ef4422d09fe755e3f4b0f116` |
| Later owner evidence | Offline integrity PASS; installer reported BOTH_APPLICATION_COMPARISONS_PASS; owner said "Both tests worked" and handoff described `ab` twice in TextEdit |
| New development candidate | `ROUTEB-DEFINE-LABELS-H1-v1`; separate from the DEL installed/owner-observation record |

The [DEL owner closeout](del-alias-owner-closeout.md) preserves the scoped later
installation, boot/input and editing observations. Full running build ID,
request IDs and matching Completed statuses were not supplied; they remain
unknown and do not require repeating the closed comparison. The source/image
identities above identify the intended release, not a new independent device
readback. The earlier owner-recorded REPEAT installation remains historical;
it is not used to deny the later DEL installation report.

The new DEFINE candidate changes only bounded constant-name capacity and its
matching preprocessing lookup. Source/test/build/package outcomes belong in
[its delivery report](define-labels-release-delivery.md) and
[structured results](define-labels-release-results.json). Those software/target
receipts do not establish installation or physical acceptance of the new image.

The reviewed parent is the actual 201-file tree selected by
[the DEL release preparer](../tests/del_alias_release/prepare_sources.py) and
[manifest](../tests/del_alias_release/source-manifest.json). Parent `core.cpp`
SHA-256 is
`d567a199a247fc585bb8f61c7459323a14ca8ca4bd14ff60690284d334f5431d`.
The selected tree was
`/workspace/scratch/del-alias-release/build-v1/candidate/EvilDuckS3`.
References marked **C:** below describe that hash-bound DEL parent; new
DEFINE-label capacity is specified separately. The root firmware, standalone
preview and separate Legacy interpreter do not substitute for this composition.
The historical preview wording inside a linked header is stale.

[DEL delivery](del-alias-release-delivery.md),
[structured results](del-alias-release-results.json),
[publication note](del-alias-review-download.md) and
[later owner closeout](del-alias-owner-closeout.md) distinguish source/build,
publication and physical-observation stages. Earlier local/not-installed/pending
labels remain historical; the later owner closeout updates the current record
without rewriting prior packages or receipts. Old test totals are **historical
receipts**, not newly executed checks by this inventory update.

The supported profile is bounded **source compatibility**: Route B compiles
source into its own program. It is not an `inject.bin` loader or complete DS3
runtime compatibility. Original Hak5 Legacy1.0 is not synonymous with EvilDuck's
custom Legacy engine.

## Evidence vocabulary

- **IMPLEMENTED**: active selected source/runtime path exists.
- **SOFTWARE-TESTED**: the cited actual-composition mocks/checks establish their
  specified software behavior, not a physical host result.
- **OWNER-REPORTED PASS**: the identified scoped macOS10.13.6 observation. Missing
  request/session/raw evidence stays unknown.
- **PARTIAL**, **UNSUPPORTED**, **REFERENCE-UNRESOLVED** and **HOST-DEPENDENT** are
  separate boundaries and may coexist. Passing expected rejection is not support.

For every compatibility claim ask: **A** is the spelling accepted? **B** is its
behavior/failure implemented? **C** does the USB path supply it? **D** was the
stated host objective observed? A source name, compiled symbol or successful
submission does not answer all four.

## Selected language and keyboard profile

| Group | Implemented behavior and explicit limits | Evidence boundary |
|---|---|---|
| Text and aliases | STRING/STRINGLN inline and multiline blocks; fourteen aliases from POWERSHELL/BATCH/BASH/JAVASCRIPT/PYTHON/RUBY/HTML. Bare openers retain blocks; simple matching same-line terminated aliases are compiler-function-backed. Nonterminated inline aliases are EvilDuck extensions. Commands emit text, never execute embedded languages. Ordinary closing-token words remain literal. | Scoped owner text/alias passes plus software boundary tests. [v2 contract](source-text-v2-design.md), [reference results](source-text-v2-reference-results.json). Not every delimiter/alias physically certified. |
| Source formatting | Exactly one EFBBBF at raw offset0, preserved/counting toward8,192 bytes; LF/CRLF/missing final newline. Partial/repeated/misplaced BOM, UTF16, unsupported controls/non-ASCII reject before output. | Source/text-v2 owner BOM trial: all30 bytes uploaded/read back, one111bom, Request1Completed. Source readback is not application readback. `C:adapter.cpp:97`; [source contract](source-text-design.md). |
| DEFINE/comments/preprocessing | DEL parent: constant labels at most23 bytes including optional #. New DEFINE candidate: at most31 bytes in32-byte cells, including # and excluding NUL; collection and conditional-flag lookup share the bound. Sixteen constants, existing grammar/boundaries/nonrecursive expansion, REM blocks, conditional depth8/literal flags, sixteen EXTENSION wrappers and VERSION remain. | [DEFINE contract](define-labels-design.md) and its release receipts distinguish the new capacity from parent evidence. Variables/functions are not widened. Retained branches/unused functions still preflight; exclusions stay distinct and wrappers cannot implement unsupported bodies. `C:core.cpp:269,489,550`. |
| Variables/control flow | Bounded global uint16 values, IF/ELSE IF/ELSE, WHILE, no-argument functions/RETURN and cooperative expression continuations. Checked arithmetic, exponentiation and eager Boolean evaluation remain project policy. | Owner examples and composed software coverage; no universal operator-edge claim. No arbitrary signed arithmetic, general interpolation or guessed compound-assignment behavior. |
| Randomization/jitter | Six character commands; bounded unbiased sampling/cached retry decisions. Integer range inclusive/default0–9/uint16; sequential updates permitted, reversed interval fails on draw. Optional pre-press jitter defaults disabled/max20ms; release/cleanup priority and per-run reset. | Scoped owner controls/range passes. RANDOM_CHAR's72-character spacing interpretation is documented policy. Statistical quality/precise timing remain unmeasured. [contract](randomization-jitter-design.md). |
| Named keys/chords/modifiers | Existing keys, US character operands, inline INJECT_MOD. RCTRL/RSHIFT/RALT/RGUI use standard right-side modifier bits but are EvilDuck source extensions. Bare/prefix INJECT_MOD unsupported. DEL and DELETE both map to0x4c forward delete; DEL() function compatibility remains preserved. | `C:shortcut_keys.h:17`; [DEL closeout](del-alias-owner-closeout.md) records the two owner comparisons, with request/status gaps preserved. [Right-modifier compatibility](h1-right-modifiers-compatibility.md); no generalized AltGr or locale claim. |
| HOLD/RELEASE | Lease-owned persistent state, transient restoration, six-nonmodifier limit, same-key collision and rollover refusals. Direct modifier ownership is an EvilDuck extension. | Scoped held-Shift/STOP owner results and composed tests. No general host-wide release guarantee. |
| RESET/restart/STOP | RESET clears keyboard state and continues. RESTART_PAYLOAD clears before rewind, keeps request/lease and cumulative budgets, resets per-run state. STOP is cooperative, single-owner and cleanup-prioritized; ambiguous acceptance/cleanup failure may quarantine without replay. | Accepted representative owner groups and software boundary tests. Device STOP does not terminate a host process already launched. [restart contract](payload-restart-design.md). |
| Both REPEAT forms | Inline literal2–128 means total executions; standalone literal1–128 means additional eligible-leaf executions. Entire program128 IR maximum. Defined lexical barriers/chaining refusal and eligible leaf list remain bounded EvilDuck policies. | [REPEAT contract](previous-command-repeat-design.md) and actual target receipts. Already implemented; no proposal to repair the old missing-standalone defect again. |
| Lock feedback/waits | Nine exact ON/OFF/CHANGE waits. `$_EVILDUCK_LOCK_TIMEOUT` is implemented here as an EvilDuck extension: default5,000ms, range1–65,535; cumulative30s budget still applies. Feedback freshness separately5s/current USB session; unknown/stale never means fabricatedOFF. | [timeout contract](lock-wait-timeout-design.md); accepted three planned inherited groups. Reports concern this interface, not necessarily global Mac lock state. |
| Experimental H1 | Opt-in finite US-printable stored-keycode path and six random-keycode getters. Existing capture/copy/reuse and release paths; no arbitrary numeric keycodes. | Four scoped owner passes. **Canonical Hak5 numeric encoding remains REFERENCE-UNRESOLVED.** [H1 design](inject-var-experimental-design.md), [closeout](inject-var-h1-owner-test-closeout.md). |
| Privacy/dashboard/editor | Password replacement write-only; blank/omitted preserves saved values. Credential readback/echo removed. Failed-load editor safeguards, coherent dashboard state and complete static-response resource delivery inherited. | Actual-composition software/linked target evidence from later receipts. No claim that earlier installed images contain these fixes solely because their filenames exist. |

Runtime bounds remain: source8,192B, physical line256B, IR128, operand storage4,096B,
symbols32, functions/constants16 each, nesting16, call depth8, expressions64
items/depth16;10,000steps,100,000ticks and30s cumulative runtime. See
`C:core.h:6`. Source bytes and instruction count are different limits.

Route B requires HID enabled and **device locale US** (`C:seam.inc:37`). Printable
ASCII plus supported TAB/LF events use the ordinary translation path. Linked
DE/GB/other tables do not enable Route B layout selection. Earlier US/Canadian
host examples do not certify all punctuation, dead keys or arbitrary Unicode.

## Twelve-technique capability matrix

Primary references are the official [quick reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference),
[keyboard documentation](https://documentation.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection),
[extensions](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/extensions),
[lock keys](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/lock-keys),
[attack modes](https://documentation.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/attack-modes),
[exfiltration](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/exfiltration)
and [official README](https://github.com/hak5/usbrubberducky-payloads/blob/master/README.md).
Planning retrieved these on2026-11-07; publication/revision dates were not supplied.

| Technique | Hak5 supplies | Selected Route B source/runtime/USB evidence | Host result or remaining blocker |
|---|---|---|---|
| Keystroke Injection | Native text, keys, modifiers and timing. | IMPLEMENTED/SOFTWARE-TESTED bounded grammar and keyboard reports, `C:core.cpp:325`, `shortcut_keys.h:17`, `seam.inc:50`. DEL alias is implemented and has scoped owner editing observations. | Scoped OWNER-REPORTED PASS; US/ASCII and finite source/report limits, not all payloads/locales. |
| HID Spoofing | Keyboard enumeration; native ATTACKMODE modes/identity parameters. | PARTIAL fixed configured keyboard enumeration. Route B has no ATTACKMODE handler; reserved name is not implementation (`C:core.cpp:83,484`). | Payload-selected identities/modes unsupported. No descriptor/impersonation work. |
| Living off the Land | Host commands/tools invoked by payload input. | HOST-DEPENDENT; keyboard launch mechanics do not confer permissions. | Harmless Bash lab evidence is scoped launch behavior, not elevation/universal portability. |
| OS Fingerprinting | OS_DETECT extension requiring telemetry including configuration requests/lock replies. | UNSUPPORTED detector. The DEFINE candidate addresses only the27-byte-label admission gap; actual next unmodified-source compile outcome belongs in its release results. Existing lock telemetry remains a subset. `C:core.cpp:159`; legacy reserved properties fall through Unsupported at `duck_vars.cpp:232`. | Counter event/reset/timing/overflow/session contract unresolved; OS symbols, indicators, Route B lock save/restore, USB mode/identity/reconnect and full-extension capacity remain separate. No OS probe or manual/fixed-label substitute. |
| Keystroke Reflection | LED reflection and loot storage. | PARTIAL custom fixed17-byte EDR1 (`C:led_receiver.h:5`, `led_receiver.cpp:21`). No arbitrary EXFIL. | Historical OWNER-REPORTED PASS on old CAPS-STOP-TRACE build plus iPhone viewing, not fresh current-build verification or Hak5 protocol compatibility. |
| Credential Dumping | Host-side operations governed by credential-store permissions. | HOST-DEPENDENT; no native credential collection. | G10 synthetic only; G11 separate fake-item keychain only. No genuine credential/vault/memory access established or planned. |
| Keylogging / Input Capture | Requires a suitable host collection/hardware path. | UNSUPPORTED. Enumerating as a keyboard does not receive unrelated input; output callback is LED metadata (`C:hid_backend.cpp:215`). | Optional model limited to fabricated text in its own visible lab field; no global/background capture. |
| Data Exfiltration | EXFIL/loot/LED reflection and host-dependent transfers. | UNSUPPORTED general transfer; PARTIAL unchanged fixed EDR1 transport. Exact message/length/CRC enforcement at `C:led_receiver.cpp:21`. | No arbitrary-data receiver, loot storage or upload endpoints. Synthetic local fixtures/memory sinks only. |
| Payload Staging | Control flow and payload/host arrangements. | PARTIAL/HOST-DEPENDENT short launcher/local fixtures within bounds (`C:core.h:6`). | Host process may outlive injection STOP. No download-and-execute chain/persistence. |
| Environment Awareness | Internal variables, extensions and host-derived facts. | PARTIAL branching/fresh lock evidence (`C:adapter.cpp:45`, `hid_backend.cpp:248`). | No OS/application-focus/permission oracle. Unknown/stale/session distinctions retained. |
| Anti-Analysis | Payload-specific techniques, not a blanket capability. | UNSUPPORTED as detection/evasion. Implemented jitter/randomness does not establish those features. | Documentation only; no evasion, stealth or protection-disabling work. |
| Conditional Execution | Native conditions, loops, functions/RETURN. | IMPLEMENTED/SOFTWARE-TESTED bounded selected profile (`C:core.cpp:321`, `core.h:8`). | Scoped owner examples; eager/check-arithmetic policies and unsupported operators remain explicit. |

## Accepted owner records and remaining evidence gaps

- [DEL closeout](del-alias-owner-closeout.md): owner reported offline integrity PASS,
  installer BOTH_APPLICATION_COMPARISONS_PASS, and "Both tests worked". The handoff
  describes `ab` twice in TextEdit. Installation/boot/input observations are scoped;
  full running ID, requests and Completed statuses remain unknown. No rerun is
  required and no universal HID/USB guarantee is claimed.
- G01–G05: scoped owner-reported passes from the supplied testing conversation.
  G06–G09: later **All 4 tests passed** supersedes earlier pending labels; G07
  remains H1, not canonical numeric proof. Original full pack filenames and
  independent receipts were not available here. Do not confuse these with native
  tests reusing G-labels. The G06 TextEdit job processor and G06 Bash staging/
  rollback lab are different objectives; their full filenames remain unknown.
- G10: synthetic parsing/redaction, not saved-password/vault access. G11: separate
  keychain containing a fake Wi-Fi-shaped item; no actual Wi-Fi credential-access
  or later physical-pass claim without evidence.
- [H1 closeout](inject-var-h1-owner-test-closeout.md): four scoped passes; fixed
  Request1, random-copy Request6, successful STOP request unknown. Earlier
  Request2 remains inconclusive. Numeric scalar was not captured.
- [Right-modifier closeout](h1-right-modifiers-owner-closeout.md): four scoped
  passes, including **executed STOP variant** Request3Cancelled/manualabc123;
  A1/C4/D5 remain separate. Request2unknown, build ID cropped, raw screenshots/
  logs independently unavailable. No physical right/left-bit certification.
- [Inherited wait correction](h1-right-modifiers-owner-correction.md): three
  planned groups,3/3PASS, Requests1/2/3/6. Attempts4/5 were owner-described handling
  mistakes outside the count; no outstanding failed group or automatic retest.
- [EDR1 acceptance](keyboard-control-owner-acceptance.md): old
  CAPS-STOP-TRACE-20261019-v1, boot74f39b50638bee97/session3,408accepted reports,
  exact 17-byte `EVILDUCK TEST 123`. Separate later iPhone820-report image is not
  merged into that trial. Restoration API accepted; global restoration unproven.
- Source/text-v2's four High Sierra passes remain: terminated aliases/literals/
  blocks, restart/held-Shift/STOP, malformed rejection, complete stored-file BOM
  upload/readback/execution. Its source-file readback is not firmware readback.

No accepted group is reopened because identifiers are missing. iPhone dashboard
viewing does not establish wired iPhone HID support, and the separate Pico
Bluetooth bridge is not evidence for this firmware. Statistical randomness,
precise timing, global host release and universal layout/USB guarantees remain
unmeasured or outside the scoped observations.

## Legacy-only, unsupported and reference-dependent boundaries

- DEFAULT_DELAY/DEFAULTDELAY, custom WAIT/REPLAY history, general STRING variable
  interpolation and READ/SAVE/APPEND remain separate Legacy-engine behavior,
  not Route B or automatically original Legacy1.0 semantics. Standalone REPEAT
  is now implemented under its own explicit bounded contract.
- SAVE/RESTORE host lock state and saved-lock properties remain unsupported in
  Route B. Active restoration needs a separately reviewed fresh-evidence contract.
- Canonical INJECT_VAR is REFERENCE-UNRESOLVED; the active bounded H1 experiment
  is neither missing nor proof of Hak5 values. Preserve unresolved vectors and
  completed compiler research; no broad reinvestigation absent a specific lead.
- The [DEFINE capacity increment](define-labels-design.md) addresses one proven
  source-admission gap in the pinned OS extension. It changes no detector, counter,
  OS state or host probe. Full source/IR/runtime requirements remain to be established
  after the next actual compile-only diagnostic; no larger budget is presumed.
- Button/indicator commands, OS detection, dynamic USB modes/identities,
  consumer/media reports, imports, arbitrary Unicode and generalized AltGr are
  unsupported/outside this profile. Reserved names and linked code are not proof.
- Invalid source admission currently has a diagnostic gap: the precompiler gate
  can expose no error or a previous compiler error while still rejecting before
  output. The [roadmap](routeb-compatibility-roadmap-20261107.md) isolates this
  future fix; no silent acceptance/limit expansion or whole-source bypass.

Explicit authenticated Route B paths and CLI `routeb <filename>` select this
engine. Ordinary `run`/Legacy interfaces remain separate, with no automatic
fallback on refusal. Preserve write-only passwords, authentication, single-owner
STOP, quarantine/no replay, source identity and storage/USB safeguards.

## Recovery and host observations

Mandatory exact rollback remains the source/text-v2 standalone application,
**1,413,200 bytes**, SHA-256:

```text
cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02
```

This older recovery lacks later privacy/dashboard/editor repairs and does not
restore deleted scripts, filesystem contents or settings. Preserve all published
packages and private recovery artifacts. The faulty e825 editor image is not a
known-good replacement rollback. Package integrity is not boot/USB acceptance.

Control+J remains the observed Screen command-submission workaround, not a
universal requirement. Rediscover and verify `/dev/cu.usbmodem*` after reconnect,
never assume a previous suffix. Mac High Sierra10.13.6, Bash3.2, Python3.8 and
esptool4.12 compatibility remain required for future packages. No Windows
availability or repeated broad Caps campaign is a prerequisite for bounded
Mac-compatible development. See the [next increments](routeb-compatibility-roadmap-20261107.md)
and [DEFINE-label contract](define-labels-design.md).
