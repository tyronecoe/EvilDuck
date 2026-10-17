# Route B transient keyboard shortcut candidate

This is a new opt-in composition from `6280b1d7b465f5d29800fa230ab60f3b04bf77c4`.
The installed hardware baseline remains Stage28X `134b295deaebcb93f94beb63f2d46f102a7d6555`.
The supplied October 16 audit is the implementation brief; its prior 38 probe
results are supplied evidence, not new executions by this task.

## Syntax and limits

A shortcut has one or more DISTINCT modifier bits followed by exactly one key.
Examples: `COMMAND a`, `SHIFT LEFTARROW`, `CTRL ALT DELETE`,
`CTRL-ALT-DELETE`, `COMMAND-OPTION-SHIFT LEFT`. Spaces/tabs separate tokens;
hyphens may separate modifier names or the final key. Empty hyphen tokens and
spaces around hyphen separators are rejected. Use `CTRL -` for the literal minus
key. Duplicate aliases for the same modifier bit are rejected conservatively,
not claimed to reproduce every PayloadStudio duplicate-handling case.

Canonical left modifier names: SHIFT=0x02, CONTROL/CTRL=0x01, ALT/OPTION=0x04,
COMMAND/WINDOWS/GUI=0x08. OPTION is evidenced in Hak5's documented combination
names. No unverified RGUI/RCOMMAND/RWINDOWS/ROPTION aliases were added.
Standalone modifiers remain rejected; INJECT_MOD semantics are deferred.

Named taps: the original ten plus UP/DOWN/LEFT/RIGHT, HOME, END, PAGEUP, PAGEDOWN,
INSERT, PRINTSCREEN, PAUSE/BREAK, MENU/APP, CAPSLOCK, NUMLOCK, SCROLLLOCK and F1–F24.
F1–F12 map to 0x3a–0x45; F13–F24 map to 0x68–0x73. F0, F01 and F25 reject.
F10 is verified against the pinned TinyUSB HID constants, not inferred from the
apparent Hak5 F0 typo. F13–F24 are an explicitly identified HID-backed EvilDuck
extension to the saved Hak5 keystroke page's function-key inventory; no claim of
independent official compiler equivalence for these names.

Key operands may also be exactly one printable US ASCII character. Uppercase and
shifted punctuation add Shift to the explicit mask. No new Unicode, locale,
keypad vocabulary or multi-nonmodifier chord semantics are introduced. The actual
adapter still requires the US locale and rejects non-ASCII source bytes.

Existing DEFINE expansion is used ONLY on the final key operand, preserving its
single-pass/word boundaries. It cannot manufacture modifier prefixes or new
structural commands. Keys/modifier names are now reserved function identifiers;
`FUNCTION F1()` or `FUNCTION COMMAND()` rejects. `$COMMAND` remains a valid user
variable. This is an explicit vocabulary compatibility change for this candidate;
the installed build and old builders retain their previous vocabulary.

## End-to-end ownership and acknowledgement

`tests/keyboard_shortcuts/shortcuts.patch` changes ONLY disposable composed sources:

- `shortcut_keys.h`: fixed name/usage table and shared US character mapping.
- `core.cpp/.h`: source grammar; Key IR uses its otherwise-unused `symbol` byte
  for modifiers; Event adds a default-zero uint8 modifier field. Other event
  initializers therefore retain zero modifiers. No second expression evaluator.
- `bridge.cpp`, `keyboard.cpp`: mock Bridge carries mask into Planner::tap;
  retry identity includes modifiers; planner text and shortcut characters share
  one mapping. Bridge rejects non-key events with nonzero modifiers.
- `adapter.cpp`, `scheduler_seam.h`, `seam.inc`, `com.cpp`: actual Route B event
  dispatch passes usage + mask into the existing guarded report scheduler.
  A retry must match type, value AND modifiers; no second admission is created.

Existing instruction and expression limits, single loop owner, execution lock,
backend lease, queue/readiness handling, source verification, default timing,
first-fault quarantine and explicit cleanup/detach remain intact. No raw HID
submission from compiler or adapter. No legacy-engine fallback. Existing US
translation and actual backend eight-byte reports, report ID 1, remain unchanged.

The source core's ownership operand lookup shares the named-key table, but the
actual candidate ALWAYS rejects any Program containing HOLD/RELEASE, even in
inactive code, before synchronization. No persistent ownership feature is enabled.
INJECT_MOD, RESET, restart, storage/mode switches, device variables and host
feedback remain outside the Route B supported subset. This patch does not bridge
legacy capabilities into Route B.

Local scheduler Done means the existing backend accepted the press and restoration
submissions under their immutable operation identity. It does NOT prove host
receipt, host key release or endpoint retirement. Ambiguous called-false results
and disconnects quarantine without retransmission or fabricated cleanup success.

## Isolation and reproducibility

All tracked historical firmware, preview, tests, builders, partition files and
package bytes remain unchanged. New wrappers reproduce exact historical X with
its original pins, then apply a separately hash-pinned fuzz-zero patch. A new
`EVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1` flag is mandatory for the new shared header.
No globally installed dependencies are patched. Existing S3 protection/ELF checks
are retained; the new verifier substitutes exact reviewed delta hashes only for
changed scratch files and independently checks the new four-argument key symbol.

Startup diagnostic banners still identify the inherited W/X composition; they
are NOT sufficient to identify this candidate. Use the new selector, source
manifest, final application SHA and linked receipt together. The existing X/Y
public package is the rollback reference, never silently repackaged or replaced.

The experimental read-only and production-safe profiles are not altered. This
builder creates a controlled normal-start, Route B-selected-capable, diagnostics-on
REVIEW candidate; boot does not select/execute Route B or enable autorun. The old
normal Run path stays legacy. No installation or change to the owner's device is
authorized by successful software validation.
