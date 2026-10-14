# Stage28F command contract — offline mock only

Baseline b23fc8b6bf8f5ff1deb5f0eb83abe7058d29eaa5. No production integration.
Contract selected before production-preview edits. Authoritative saved Hak5 references:
[Holding Keys](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/holding-keys)
and [Quick Reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference).
Saved Stage9 snapshots and their SHA-256 provenance are in stage28f-reference-evidence.json.
No new latest-reference or compiler-oracle claim; examples in references were read, never run.
USB HID Usage Tables1.5 section10 supplies page07 usage identities (Stage28D evidence).

| Command | Implemented syntax | Reference basis | Admission |
|---|---|---|---|
| HOLD | HOLD key | Both commands require a key; multiple HOLD commands permitted; quick reference HOLD a | One supported nonmodifier token |
| RELEASE | RELEASE key | Release specified key; quick reference RELEASE a | Same single-token domain |
| Modifier commands | BLOCKED | Holding Keys requires INJECT_MOD; examples disagree on RELEASE prefix | Do not infer prefix scope; source HOLD/RELEASE SHIFT etc rejected |
| RESET / release-all | BLOCKED | Quick Reference says clears keystroke buffer | Buffer/all-owner scope and foreign ownership unresolved; no invented RELEASE_ALL or bare RELEASE |

Supported key tokens: lowercase ASCII a–z, digits0–9, and existing preview named keys
ENTER TAB SPACE ESCAPE BACKSPACE DELETE UPARROW DOWNARROW LEFTARROW RIGHTARROW.
Exactly uppercase command/named spelling; no chords, numeric usages, uppercase-letter SHIFT
inference, punctuation, aliases, modifiers, Unicode or expressions. Named-key identities match
existing transient keys. DEFINE expansion is the existing bounded single-pass operand expansion;
it cannot manufacture statements. Malformed operands reject during complete preflight, including
inactive/runtime-function regions; literal text/comment modes retain existing handling.

Persistent ownership survives DELAY, IF, WHILE and function calls until RELEASE or runtime terminal
cleanup. Lifetime is one bridge session, not local function scope. One dedicated script owner3;
Prepared setup owners0–2 are independent. All four owners remain available for prior ownership-free Programs; existing Prepared API remains available, but start of a Program containing ownership commands
refuses occupied owner3 (without starting Runtime or altering owners). No second script owner
syntax. Shared same usage with another owner is allowed by the existing union ownership model;
script RELEASE affects only owner3. A transient tap of any held usage rejects rather than faking
an edge. Six distinct nonmodifier keys maximum; rejected proposals have no partial effects.

Idempotent repeated HOLD and RELEASE (including absent key) are explicit mock compatibility
policies: reference does not specify repeated-operation behavior. Each admitted source ownership
command requires a fresh acceptance of its corresponding union report, including unchanged
reports; earlier acceptance cannot acknowledge it. One report transition, not tap/restoration.
Retry repeats identical pending bytes, never duplicates logical admission or source ack.
Completion/STOP/error/cancel clear logical owners but do not claim accepted release. Owner must
explicitly drain; that separate action emits only zero, requires its own acceptance, and gates
restart. No auto release-all statement, implicit destructor delivery or physical-release claim.

Persistent SHIFT coverage uses Prepared mock API only; this is not canonical modifier source
support. US/page07 mock only; no host OS, typematic, descriptors, report ID, real transport,
Unicode, locale/dead keys, lock state or wall-clock guarantee. Existing bounds stay unchanged.
