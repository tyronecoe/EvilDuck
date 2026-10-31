# Right Modifiers H1 — scoped owner-acceptance closeout

**Four scoped owner-reported physical PASS results on Intel MacBook / macOS High Sierra 10.13.6 / TextEdit, including one STOP-variant PASS.** This is not a claim that all four original published fixtures were executed unchanged. The owner used the iPhone Wi-Fi dashboard at `192.168.4.1` and explicit Route B execution, according to the supplied handoff dated October 31, 2026.

Codex reviewed the handoff, the published acceptance sheet and release provenance, and inspected the hash-bound release sources. **The original screenshots and raw logs were not attached to this closeout session**, and the handoff supplies no image filenames. Observations below remain attributed owner summaries, not independently measured hardware, wire captures or photographs inspected by Codex. [Structured receipt](h1-right-modifiers-owner-closeout.json) preserves the handoff identity, exact reported source lines, unknowns and limitations.

## Test A — Right Shift/mixed modifier typing: owner-reported PASS

**Request 1: Completed.** TextEdit reportedly showed exactly **`AbCDe`** on one line. The reported script matches the published `rm-shift.txt` lines:

```ducky
DELAY 5000
HOLD RSHIFT
STRING a
RELEASE RSHIFT
STRING b
SHIFT-RSHIFT c
RSHIFT d
INJECT_MOD RSHIFT
STRING e
ENTER
```

The visible output and completion match the fixture expectation. There is no independent USB report-byte capture proving left/right bits on the wire. Exact trailing newline/source-file byte identities were not supplied; source lines above are recorded from the handoff.

## Test B — STOP/recovery variant: owner-reported PASS for the executed variant

**Request 3: Cancelled.** The owner reportedly pressed STOP during the delayed/held portion. TextEdit stayed blank until the owner manually typed **`abc123`**, which appeared exactly in lowercase with unshifted digits; no **`BAD`** appeared. The actual script supplied and executed in the testing conversation was:

```ducky
DELAY 3000
HOLD RSHIFT
DELAY 15000
STRING BAD
RELEASE RSHIFT
```

This is **not an exact run of the published `rm-stop.txt` fixture**. That original fixture uses initial DELAY5000, types an initial `a` under held Shift (expected `A`), then DELAY10000 and `STRINGLN 999bad`. The executed variant uses DELAY3000/15000, has **no initial text**, uses `STRING BAD`, and includes explicit RELEASE RSHIFT after the suffix. Preserve those differences; neither script nor its historic expectation is rewritten to match the other.

This supports scoped owner STOP/manual-recovery observations for the executed variant. No independent HID capture or timing trace proves the precise hold instant or a universal host-release guarantee. The published original fixture remains preserved; no unsolicited exact-fixture retest is requested by this closeout.

## Test C — Right modifier-only taps: owner-reported PASS

**Request 4: Completed.** TextEdit reportedly showed exactly **`222taps`**, with no unexpected application action reported. The reported script matches published `rm-modifier-taps.txt`:

```ducky
DELAY 5000
INJECT_MOD RCTRL
INJECT_MOD RALT
INJECT_MOD RGUI
STRINGLN 222taps
```

This is a scoped observation of benign tap behavior, text and completion on this Mac. It does not independently prove distinct right-side HID bytes or behavior across macOS versions, keyboard layouts, AltGr/dead keys or other platforms.

## Test D — Duplicate modifier rejection: owner-reported PASS

**Request 5: Compile failure, physical line 2, code 15.** The owner explicitly confirmed completely blank TextEdit before afterward manually typing **`abc123`** normally in lowercase. The reported script matches published `rm-malformed.txt`:

```ducky
STRINGLN 999bad
RSHIFT-RSHIFT a
```

This specific duplicate physical modifier combination was reportedly rejected before any first-line output. The later manual typing is a **normal keyboard check**, not independent held-modifier recovery evidence: this source failed compilation.

## Request and identity boundaries

The right-modifier sequence uses **A=1, B=3, C=4, D=5**. **Request 2 remains unknown**; no outcome, error or particular execution is inferred from the numbering gap. These IDs do not overwrite identifiers in the separate earlier four-check H1 or inherited lock-wait milestones.

Intended release: **ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1**. The handoff summarizes a dashboard screenshot showing only **`ROUTEB-RIGHT-MODIFIERS-H1-EXPERIME...`**, cropped at the end. **That screenshot does not independently establish the complete running build ID.** No exact contemporaneous full-ID record or independent device-image readback is supplied in this handoff. Release/installer/package identity is kept separate from proof of what exact bytes ran on hardware.

| Preserved published artifact | Bytes | SHA-256 |
|---|---:|---|
| `evilduck-routeb-right-modifiers-h1-experimental-macos-v1.zip` | 2,471,296 | `9a3593735799d36d1db949c2982558a384dc5f6de43f2d3f804c4bfb15fc113e` |
| Candidate application from that package | 1,414,176 | `12134383e75505704d7efebf33cb7b7fdd7bd8f609038fbc575e911a0ad69ca3` |
| Mandatory accepted source/text-v2 rollback | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

The [published release report](h1-right-modifiers-report.md) and [artifact inventory](h1-right-modifiers-artifacts.json) retain their original evidence. Release commit: `2a99ed58bcb6f52912627c698158ef02abd2e421`; package commit: `abe9c548f01a4bf5f43c0a791fbb449b418a2227`; implementation commit: `6d15952e40f9016c4374b8b0403883ebb2290d9a`; packaging tools commit: `245792db1a15468ae7d04cd0882d177cfa9ae03a`. Offline hash checks do not establish equivalence to independently read-back device bytes. Rollback remains exact and mandatory; this closeout does not promote H1 to a default profile or replace the rollback baseline.

Unsupplied boot/session identifiers, per-trial timestamps, screenshot/log filenames, diagnostic details for A/B/C, source-file readback hashes and installation-comparison evidence remain unknown. No USB packet capture, host acknowledgment, physical right-vs-left report-byte proof or universal release guarantee was obtained in these runs. **LED feedback on High Sierra remains unknown/unverified**; these tests do not resolve it. H1/right-modifier features stay experimental and **canonical Hak5 compatibility, including INJECT_VAR numeric encoding, remains unresolved**.

## Fresh closeout checks and preserved history

[Closeout verification](h1-right-modifiers-owner-verification.json) records fresh documentation/receipt checks, script-vs-fixture reconciliation, release source/artifact identities, relative links and historical file/mode preservation. Historical **558 native PASS / 23,901 assertions**, sanitizer results and **83 package / 38 mock-installer PASS** remain separate prior software evidence; none was rerun here. The original [acceptance sheet](h1-right-modifiers-acceptance.md), fixtures, source/build tools, reports, application/kit ZIPs and earlier closeouts remain unchanged. The current candidate compatibility document receives only a dated link to this later evidence, retaining its original text and the package's enclosed copy unchanged.

No firmware edits, builds, new packages, hardware access, HID execution, flashing, OTA, new feature implementation or physical repetition occurred. Publication/download and prior-ref verification are recorded after push. This record closes the four scoped owner-reported outcomes **including the STOP variant**, without strengthening them into independently measured hardware proof.

## Proposed next research stage — no implementation

Recommend **offline acceptance-receipt consistency checking** as the next isolated research capability. Evaluate reuse of existing JSON/manifest tools to distinguish exact fixtures from reported variants, cropped identifiers from verified identities, per-sequence request IDs and missing evidence. The practical benefit is fewer ambiguous closeouts without requiring another hardware campaign.

The proposal should remain local and read-only over public or deliberately supplied sanitized records, collect no credentials, send no device/network actions, expand no firmware/USB capability and infer no PASS from missing evidence. Research/design would require a separate instruction; no checker or next feature is implemented in this task. Keep the current firmware and recovery artifacts frozen while this evidence-quality proposal is reviewed.
