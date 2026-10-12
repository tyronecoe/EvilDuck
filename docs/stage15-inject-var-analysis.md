# INJECT_VAR independent-reference investigation

No implementation in Stage15. Official saved randomization and quick-reference
sources are verified against Stage14 provenance. Current randomization Markdown and
encoder.hak5.org return403. A read-only GitHub public repository search for official
Hak5 encoder projects returned no items; this does not prove no private/versioned
compiler exists. Hak5-owned payload examples are source examples, not an encoder oracle.
No downloadable independent official compiler/verified numeric format was obtained.

Established: INJECT_VAR consumes a numeric variable containing a scancode; storing
$_RANDOM_LETTER_KEYCODE and injecting twice repeats the same selected character.
$_RANDOM_INT is not decimal text; TRANSLATE is used for decimal representation.
Six random keycode properties are read-only. This does not establish modifier/key
byte order, bit fields, invalid usage rules, locale capture/injection behavior,
AltGr encoding or two-stroke dead-key representation. C/C++ HID report packing and
community/older DuckyScript encoders are not proof of DS3's numeric format.

The JSON reference-vector specifications deliberately keep packed_value null and
status UNRESOLVED. Eight-byte USB usage/report expectations are independently known
for the existing US/DE translator, NOT numeric DS3 encodings. Lowercase/uppercase,
digit, symbol, AltGr and dead-key vectors specify what an independent compiler/device
comparison must establish. Repetition must preserve selected value while HOLD/RELEASE
merges ownership and rejects seventh-key rollover predictably; locale changes need
an explicit reference contract. 0/65535/unsupported usages must be reference-tested,
not guessed as valid/invalid packed values. No sentinel fake format is accepted.

Production retains unsupported INJECT_VAR, $_RANDOM_*_KEYCODE and $_RANDOM_SEED.
Stage14 numeric interpolation remains explicitly EvilDuck-specific. Existing Stage14
regressions execute the actual unsupported-command/property diagnostics before HID.
These new specifications are research artifacts, not compatibility passes.
