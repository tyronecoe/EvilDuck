# Stage 14 deferred compatibility investigation

Official provenance: stage14-reference-sources.json. No device/compiler reference executed.

## INJECT_VAR and random scancode properties

The randomization page documents storing $_RANDOM_LETTER_KEYCODE in a numeric global
and invoking INJECT_VAR twice to reproduce the same character. It explicitly says
$_RANDOM_INT cannot be injected as its decimal text without a TRANSLATE extension.
This establishes a scancode contract, not its byte packing. No supplied prose/table
independently establishes modifier/key byte order, high/low-byte masks, invalid usage
handling, layout lifetime or multiple-stroke dead-key representation. A chosen C++
USB HID encoding would be an invented compatibility claim. Therefore INJECT_VAR and
six $_RANDOM_*_KEYCODE variables remain reserved/unsupported. Stage14 random commands
translate a sampled ASCII character through the existing US/DE engine, without
exposing a fabricated packed value.

Proposed separate milestone: obtain a versioned reference compiler or explicit
encoding specification; compare harmless lowercase, uppercase, digit, Shift symbol,
AltGr and German dead-key results. Verify packing/endian order, zero/invalid values,
owned-key merge and rollover, same stored value repeated, locale changes between
capture/injection, cooperative cancellation and exact mocked reports. Preserve
integer decimal interpolation as an EvilDuck extension, not INJECT_VAR semantics.

## RESTART_PAYLOAD

The official payload-control page establishes cease current execution and start
again from the beginning; its Hello World example loops without reaching following
text. It does not specify whether user variables, internal properties, saved host
lock state, random seed/stream, attackmode, locale, LEDs, held keys or default delay
survive a restart. These cannot be inferred from the RESET command, which clears
keyboard state and continues. RESTART_PAYLOAD remains unsupported in Stage14.

Proposed separate reviewed milestone: define reference-backed reset/persistence
profile and bounded restart/progress budget; release keys before rewinding; cancel
pending jitter/delay/text/function work; reset source reader/call/control stacks
without recursive run(); retain immutable preprocessing decisions or explicitly
revalidate source; preserve meaningful physical-line diagnostics and STOP responsiveness.
Tests must cover restarted held keys, transport refusal, functions/loops, source
faults, seed/variable/settings lifetime, and no-progress restarts. No implementation,
physical migration or Stage15 authorization is implied.

## seed.bin and device identity

The docs describe seed.bin on Hak5 microSD and $_RANDOM_SEED as its seed, but supply
no reliable file geometry/algorithm/version contract. EvilDuck uses ESP32 esp_random
per sampled value. It neither reads nor writes seed.bin, and leaves $_RANDOM_SEED
unsupported rather than returning unrelated hardware entropy as a claimed file seed.
Host-only reproducible sources are testing adapters, not DuckyScript commands.
Random USB identity/personality options remain deferred; descriptors are unchanged.
