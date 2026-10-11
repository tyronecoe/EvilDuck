# Stage 8 keyboard capability inventory

Evidence is software-only: actual firmware sources run against mocked USB,
clock/storage/output. Exact HID usage/report bytes were tested. No macOS,
Windows, Linux, real USB endpoint or physical SD/SPIFFS behavior is certified.
No full DuckyScript 3.0 compatibility claim is made.

## Keyboard features

| Feature | Software status | Boundary / physical work remaining |
| --- | --- | --- |
| F1–F24 | Confirmed reference mappings | F1–12 0x3A–45, F13–24 0x68–73; host actions require testing |
| Navigation/editing/system keys and aliases | Confirmed implemented mappings | Insert/Home/PageUp/Delete/End/PageDown/arrows, Enter/Tab/Escape/Backspace/Space, CapsLock/NumLock/ScrollLock/PrintScreen/Pause/Menu; effects depend on host/editor |
| Keypad | Confirmed implemented NUM_* mappings | 0–9, slash/star/minus/plus/Enter/dot and NumLock; no named keypad equals, comma or extended keypad family; NumLock and locale affect output |
| Modifiers | Confirmed all 256 masks | E0–E7 encode left/right Ctrl/Shift/Alt/GUI in the modifier byte; COMMAND and OPTION alias left GUI/Alt |
| Space/hyphen named chords | Confirmed within bounds | Up to six distinct named keys plus eight modifier bits; duplicate suppression; seven distinct named keys reject before HID |
| Literal punctuation with modifiers | Confirmed US/DE report sequences | Locale modifier OR explicit chord mask; two-stroke dead keys keep the mask; physical host shortcuts/composition differ |
| Mixed named/literal groups | Partially supported compatibility behavior | Named keys flush as one released chord; later literal characters form sequential strokes, rather than arbitrary simultaneous physical/character chords. Use named physical keys for a simultaneous group |
| Press/release order | Confirmed mocked reports | One combined press report then all-zero release, dwell at least 5 ms; does not imitate four separate modifier/key ordering reports |
| US ASCII | Confirmed all 128 indices / printable runtime | Standard US layout assumption; control indices 8,9,10,13,27,127 mapped, other controls skipped; does not infer CapsLock state |
| DE ASCII | Confirmed all 128 indices / printable runtime | German PC/ISO basic assumption, QWERTZ, AltGr and 102nd key; not a macOS German layout certification |
| DE UTF-8 | Confirmed finite table | § ° ² ³ Ä Ö Ü ß ä ö ü € plus two-stroke spacing acute ´; not all Latin/Unicode characters |
| DE dead keys | Confirmed two-stroke reports | ^ = grave-position then Space; ` = Shift+equal-position then Space; ´ = equal-position then Space. Standard DE tilde is AltGr+plus without extra Space |
| Unsupported Unicode | Explicit bounded legacy skip | One well-formed UTF-8 scalar skipped, invalid byte skipped, no fabricated key; one warning per text operation. Emoji, CJK, é, normalization/composing are unsupported |
| Other locales / variants | Unsupported | Only US and DE are registered; GB/ES/FR/RU and optional header declarations are not working layouts. No US International, German nodeadkeys/deadtilde or Mac German profile |
| Host layout / lock state discovery | Unsupported | LOCALE chooses device mapping, does not change/query host input source, CapsLock, NumLock or ScrollLock; Shift text can invert under CapsLock |
| STOP, errors, cancellation | Confirmed mocked release/ownership | Pending text/commands canceled; deferred release has priority. A disconnected host receives no release until USB is ready; no promise of physical reconnect behavior |
| Dead-key cancellation | Keys released; composition partly supported | Can cancel second Space/tail, but cannot undo host's pending dead-key/compose state. No automatic Escape or other unsolicited host action is sent |
| USB backpressure/refused queue | Confirmed retry and no duplicate accepted reports | Bus enumeration/reset/disconnect, delivery completion and host timing require physical validation |
| HOLD / RELEASE / INJECT_MOD | Unsupported canonical commands | Runtime five-ms ownership is not persistent language-level HOLD/RELEASE; standalone modifiers remain an EvilDuck extension |
| Consumer/media/NKRO/boot-protocol features | Unsupported / not established | Six-key keyboard report only, no media report page; existing TinyUSB report descriptor/protocol is unchanged; no claim of boot-keyboard or arbitrary NKRO support |
| Raw KEYCODE | EvilDuck extension, tested | Modifier byte plus at most six key bytes; E0–E7 folded into modifier mask, duplicates removed, zero and >=0xA5 nonmodifier usages ignored, preserving existing policy |
| Physical bare A–Z / digits | EvilDuck compatibility, tested | Case-insensitive named physical keys, independent of locale; use STRING for localized/shifted characters. RETURN is Enter only outside functions; use ENTER inside functions |
| LOCALE, text interpolation, REPEAT/REPLAY | EvilDuck compatibility, tested | Existing rules unchanged; constants/repeated output use corrected HID path. Locale selection persists until changed, not host-configured |

German `#` retains usage 0x31 (the existing physical backslash-position mapping),
consistent with the standard PC row. USB's non-US # usage 0x32 and host handling
must not be confused with a universal Unicode mapping. AltGr is the right-Alt bit
0x40, not an invented Ctrl+Alt substitution. Apple Option combinations can differ.

References: [USB HUT 1.5, keyboard page 0x07](https://www.usb.org/sites/default/files/hut1_5.pdf),
[Hak5 keystroke injection](https://documentation.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection.md),
[Hak5 holding keys](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/holding-keys.md),
xkeyboard-config `de(basic)` and `latin(type4)` rows. Tests do not use a Hak5
reference compiler/device oracle. The Hak5 basic key list contains an apparent
F0 typo; USB usage references control F-key numbering, not that typo.

## Deferred non-keyboard compatibility inventory for Stage 9

This is an inventory for the next review, not Stage 9 implementation or a complete
audit of every Hak5 command. Source parser/Stage 1–7 contracts establish:

* Implemented: bounded source/preflight, REM/REM_BLOCK, global 16-bit variables,
  immutable single-pass DEFINE, shared expressions, IF chains, guarded WHILE,
  bounded functions/returns/calls and streamed STRING/STRINGLN.
* Unsupported documented surfaces: persistent HOLD/RELEASE/INJECT_MOD and lock
  feedback/control, language-specific STRING block aliases, internal/runtime
  Hak5 variables, randomization/host-detection mechanisms, extended ATTACKMODE
  VID/PID/vendor/product options, button/LED-wait commands and hardware-specific
  exfiltration/storage capabilities. Inventory official commands and distinguish
  hardware-inapplicable features before prioritizing implementations.
* Deliberate or uncertain differences requiring reference work: operator
  precedence/eager logical evaluation, uint16 wrapping/shift bounds, numeric
  limits and 0^0; DEFINE overlap/redefinition/nonrecursion and prevention of
  structural macro generation; text interpolation extension; void return
  consumption and no arguments; eight combined control frames/eight calls;
  total-loop/stalled and call-budget safety guards versus Hak5 infinite loops.
* Existing EvilDuck extensions: quoted text variables/READ, SAVE/APPEND/KEYCODE,
  LOCALE/RGB settings, WAIT/default-delay aliases, no-THEN legacy IF/text truth,
  previous-command REPEAT rather than a new block-loop meaning; source/global
  state limits must stay explicit rather than labeled full language compatibility.
* Infrastructure limitations: legacy READ loads its complete file; concurrent
  same-size script edits are not fully authenticated; preflight global-symbol
  inventory is not path-sensitive; actual web responsiveness under SD latency,
  firmware task-stack/heap peaks and physical OTA/storage behavior need testing.

Recommended Stage 9 first deliverable: a command-by-command official-reference
matrix with harmless fixtures, exact unsupported diagnostics, hardware relevance
and documented differences. Prioritize persistent key ownership/lock feedback and
reference ambiguities before claiming more broad compatibility. Do not begin it
until Stage 8 review.

## Later High Sierra 10.13.6 validation

After separate hardware/migration authorization, start with a blank TextEdit plain
text document. Explicitly select the intended host input source; use harmless
letters/digits/punctuation and spacing accents, verify Enter/tab/whitespace and
release on STOP, and inspect repeat/timing and reconnect behavior. Test Ctrl/GUI/
Option shortcuts only where their effects are understood and harmless. Confirm
CapsLock/NumLock assumptions and German PC-vs-Mac differences. Do not execute the
repository payload collection as a keyboard smoke test. No part of this procedure
was executed during Stage 8.
