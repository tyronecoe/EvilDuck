# DEL alias — bounded Route B contract

Target: `ROUTEB-DEL-ALIAS-H1-v1`, additive to the complete
`ROUTEB-PREVIOUS-COMMAND-REPEAT-v1` composition. Branch:
`routeb-del-alias-h1-v1`. The starting publication checkpoint is
`557dc81f65b672d5b701b681664ef6ff0a7e5d44`; its firmware checkpoint is
`820a575a45e5a4f644921d663a650110667a6ab2`.

This document specifies the change and acceptance criteria. Execution results,
clean-build identities and package results belong in the separate release
report; this contract does not claim installation or owner acceptance.

## Established gap and primary reference

The official [Hak5 quick reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference)
explicitly lists `INSERT DELETE DEL BACKSPACE` under Cursor Keys. The planning
stage retrieved that page on **2026-11-07**: 39,018 bytes, SHA-256
`cd38fd8410bc7833f6ae047ed0d845454e6fd75c4171245f5841f2e8595617a2`.
No publication/revision date was supplied. The ordinary page URL succeeded;
some `.md` requests returned HTTP 403. This source establishes the spelling,
not every runtime or host outcome.

The verified parent composition maps `DELETE` to page-07 usage `0x4c`, but its
`shortcut_keys.h::named()` omits `DEL`. Source inspection predicts a bare `DEL`
fails UnknownStatement/code13; a modifier chord containing it fails Syntax/code15;
HOLD/RELEASE and inline REPEAT forms fail Unsupported/code14. These were planning
findings, not newly executed test results. Separate Legacy tests already know
`DEL`; that never established selected Route B support.

## Exact source behavior

- Add exact uppercase `DEL` as an alias of `DELETE`, keyboard usage **0x4c**,
  forward delete. Do not substitute Backspace/usage0x2a.
- Reuse the existing bare-key, chord, HOLD/RELEASE and eligible REPEAT paths.
  Supported DEFINE expansion positions accept it wherever they accept DELETE;
  no new command/prefix expansion is introduced.
- Existing case sensitivity remains. Lowercase/mixed-case variants, unknown
  lookalikes and extra operands reject according to the corresponding existing
  DELETE/parser contract.
- `STRING DEL`, STRINGLN and multiline block contents remain ordinary text.
  Raw source byte0x7f remains invalid; its ASCII name is unrelated to this command.
- Existing inline `REPEAT 2..128 leaf` means total executions; standalone
  `REPEAT 1..128` means additional executions of the preceding eligible leaf.
  The whole program still fits128 IR instructions. No repeat-policy change.

Adding a named key would incidentally reserve `DEL` as a function identifier.
Preserve the previously legal `FUNCTION DEL()` declaration, `DEL()` calls,
function values in expressions and `$DEL` variables. The narrow policy is to
exclude **only exact DEL** from the dynamic named-key reservation check.
`named()` uses exact comparison, so bare `DEL` and `DEL()` are unambiguous.
All other reservations remain unchanged. This identifier-preservation policy is
an EvilDuck compatibility decision, not an assertion about Hak5 identifiers.

## Existing execution and report path

The only functional source changes are in composed `shortcut_keys.h` and
`core.cpp`'s reservation predicate. A separate build-ID change identifies the
candidate. No new opcode, numeric decoder, scheduler, HID backend, storage or
HTTP interface is required.

The existing path remains Compiler Key -> Adapter -> Route B seam -> scheduler
-> leased HID backend. A bare alias uses report ID1 and the eight-byte keyboard
report payload:

```text
00 00 4c 00 00 00 00 00
```

The report ID is supplied separately to TinyUSB; this is not a complete USB wire
packet. Existing key-down dwell, jitter settings and held-state merging apply.
After a transient tap, restore the persistent held baseline. Existing collision,
six-key rollover, single-owner, backpressure, operation-correlation, STOP,
priority cleanup, disconnect and quarantine/no-replay behavior remain in the
same implementation paths. Local submission does not prove host reception or
host-global release. No Caps normalization or new layout support is introduced.

H1 remains opt-in and experimental. Neither this source alias nor right-side
modifier names change H1's finite US-printable decoder or prove canonical Hak5
numeric scancode encoding.

## Required software and target checks

Use the actual composed modules with mocked HID, storage and clocks:

1. DEL/DELETE parity in IR, events, report ID/payload order and restoration.
2. Existing modifier/chord forms, right modifiers, HOLD/RELEASE, supported DEFINE
   positions and both REPEAT forms.
3. Literal text/blocks, DEL() declaration/calls/value expressions and $DEL.
4. Malformed retained source rejected before output, physical diagnostic lines,
   and unchanged preprocessing exclusions.
5. Held-state restoration, same-key collision, rollover refusal, transport
   backpressure and no duplicate accepted output.
6. STOP during pending work, disconnect/quarantine, restart and later-run
   isolation; existing keyboard, REPEAT, preprocessing, H1/right-modifier,
   privacy/dashboard and EDR1 regressions.

Run applicable ASan/UBSan/leak checks. Source/native receipts and the actual
clean target must reconcile to the same final201 source inventory. Preserve
historical receipts and disclose failures; do not relabel old totals as new.

The canonical target entry must select the additive overlay and unique identity.
Use the approved isolated archive-based Arduino ESP32 3.3.0 profile, unchanged
committed-source/dependency checks, USB identity,16MiB partitions and disabled
PSRAM. Preserve inherited release proof assertions rather than bypassing guards.
Report measured application/static-RAM deltas after the build. No physical
hardware, payload execution, installation, flashing or OTA is part of preparation.

## Short later owner check

Only after separately authorized installation, use a **new unsaved TextEdit
plain-text document**, with the intended input source selected. Record the
assigned request and terminal result separately from visible output.

1. Type `abc`, move left twice, send DEL: expect **ac** and Completed. Compare
   DELETE in another blank document; it must produce the same result.
2. Type `abcde`, move left four times, send DEL then standalone REPEAT1: expect
   **ade** and Completed.
3. In blank TextEdit, `STRING SHOULD_NOT_APPEAR` followed by `DEL extra` must
   compile-reject at physical line2/code13 before any output.

These checks concern the alias only. Accepted H1/right-modifier/lock-wait groups
are not reopened. No broad Caps campaign or Windows hardware is required.

## Exact recovery requirement

Every candidate package retains the exact **1,413,200-byte** source/text-v2
standalone application, SHA-256:

```text
cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02
```

It lacks later privacy/dashboard/editor fixes and is not a full-device or
filesystem restore. Preserve all historical packages and private recovery
artifacts. Package review, software verification and matching hashes do not
establish installation, boot, USB completion or physical acceptance.
