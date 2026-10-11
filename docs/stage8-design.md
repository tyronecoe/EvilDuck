# Stage 8 HID and locale contract

Baseline: Stage 7 `68f44b7a7bd1478064b32316fa49a62f68d8527b`.
Only mocked USB endpoints are used. No hardware or Stage 9 work is authorized.
The pinned 3.3.0 core, 16 MiB partitions, PSRAM-disabled profile, migration
safeguards and Arduino Micro sources remain unchanged.

## Reference and audit

Reviewed Stage 1–7 execution contracts/reports/tests and migration notes. HID
references: [USB HID Usage Tables 1.5, keyboard page 0x07, section 10](https://www.usb.org/sites/default/files/hut1_5.pdf),
[Hak5 keystroke injection](https://docs.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection.md)
(the project's already retrieved official text), Arduino ESP32 3.3.0's
USBHIDKeyboard/TinyUSB keyboard descriptor, and xkeyboard-config's standard
German `de(basic)` and inherited `latin(type4)` layout. These establish usage
numbers and intended German PC/ISO positions, not macOS/Windows physical behavior.
Only US and DE are actually registered. Conditional GB/ES/FR/RU declarations do
not constitute implemented locales.

## Changes planned before implementation

* F1–F12 remain 0x3A–0x45; F13–F24 become 0x68–0x73 (not contiguous with F12).
* Rebuild DE as exactly 128 indexed ASCII pairs, preserving intended printable
  positions, correcting the missing control slots and `&` to Shift+7. Preserve
  its existing two-stroke circumflex, grave and acute handling. Standard DE has
  non-dead AltGr+plus tilde; no extra space is added for a different layout variant.
* Carry explicit chord modifiers through locale punctuation/dead-key strokes.
  Existing code incorrectly emits a modifier-only report and releases it before
  literal punctuation. STRING itself retains automatic locale modifiers only.
* Accept documented hyphen-delimited named-key combinations and OPTION as ALT.
  A lone `-` remains a literal character. Empty hyphen segments are errors. This
  applies only to keyboard statements, never STRING, expressions or filenames.
  OPTION becomes a supported modifier name and therefore joins the existing
  function-name collision rule; a legacy function named OPTION must be renamed.
* Fix literal parenthesis/chord tokens wrongly classified as function calls;
  genuine named invocations and malformed call diagnostics retain Stage 6 checks.
* Fix the discovered END navigation-key collision: only END IF / END WHILE
  are structural aliases; bare END and valid END key groups are keyboard commands.
* Suppress duplicate named keys before occupying six-key slots. Reject more than
  six distinct named keys in one report during preflight rather than silently
  dropping keys. This is an intentional safety diagnostic change. KEYCODE's
  existing six-input-byte limit/filtering remains unchanged.
* Keep the legacy skip policy for unsupported text characters, but consume a
  well-formed unsupported UTF-8 scalar as one bounded unit and log one warning
  per text operation. Invalid UTF-8 consumes one byte without output. No Unicode
  normalization, OS-specific Unicode entry, or claim of full Unicode is added.

## Architecture and bounds

Keep one cooperative report path: modifier byte, reserved zero, six key bytes,
separate report ID. One report press then an all-zero release, minimum existing
5 ms dwell. Dead keys produce at most two separately released strokes. A tiny
per-text modifier mask and warning flag carry state; no heap-backed HID queue,
new parser engine, library, worker or descriptor change is needed. Locale lookup
and report construction must allocate nothing. Existing String command parsing
and fixed-size line buffers remain bounded and are not claimed allocation-free.

Cancellation retains the priority deferred release. USB queue refusal must be
retried without consuming text or producing duplicate accepted reports. A host
that is disconnected cannot receive a release until transport becomes ready;
readiness simulation cannot establish real disconnect/enumeration behavior.

## Verification order

Reference-backed exhaustive ASCII, F-key, named-key/modifier and raw report tests;
then script integration, repeat/DEFINE/block/control-flow, fault/cancellation and
transport refusal tests; allocation probe; all earlier suites with ASan/UBSan;
clean pinned firmware build, partition checks and stack/resource analysis. Leave
historical diagnostic labels intact: proven fixes should become XPASS naturally.
Document remaining language and host/layout gaps for review; do not implement
Stage 9.
