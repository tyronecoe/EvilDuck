# Stage 25 controlled first-boot contract

Select `--controlled-normal-start` explicitly through the protected isolated builder.
Default normal, deployment-safe, and experimental readonly remain separate profiles.
The default normal profile retains legacy behavior and is **not** the reviewed first-boot
candidate. Contradictory safe/controlled flags fail at argument parsing and compilation.
No runtime command, button or payload switches these compile-time profiles.

## Controlled sequence

1. Latch one application setup attempt. Loop stays quiescent until setup completes.
2. Check the Stage18 original NVS startup status; failure never loads settings or mounts media.
3. Inspect canonical SDK partition descriptors: exactly the six reviewed writable main-flash
   partitions, correct names/types/subtypes/addresses/sizes, no encryption/readonly or extras.
   Missing/allocation/lookup/ambiguous/wrong-layout states fail closed and release iterators.
4. Read existing typed `duck` settings without setters/commits. Missing namespace or missing,
   blank, invalid/type-mismatched/unreadable security fields stops the application. AP password
   must not equal the existing public legacy default. CR/LF/NUL/length errors fail. Stored
   autorun true is refused. There is no settings schema change or repair/default write.
5. Mount required SPIFFS with `SPIFFS.begin(false)`. Failure stops before SD and application
   HID/MSC/CLI/web/scheduler. No formatting or example installer is requested. Optional SD
   remains supported; no card is not fatal when the required SPIFFS is healthy.
6. Prepare AP using validated credentials and checked WiFi.mode/softAP return values.
   Failure attempts WIFI_OFF, returns failure and leaves the application unarmed. It does
   not claim a physical shutdown acknowledgement or an operating HTTP endpoint.
7. Start existing LED, application HID/locale, default HID-only attackmode, CLI and web;
   mark setup complete and allow the existing scheduler. No autorun call or example installer
   occurs. Default attackmode ends any storage preparation and does not activate MSC.

These are application-level gates, not a pre-NVS bootloader policy. NVS initialization
occurs earlier in the pinned SDK/core; Stage18 automatic whole-partition erase remains
removed, but normal writable SDK recovery/read/Wi-Fi activity may modify NVS. For an
explicit fresh writable installation those SDK operations must be accepted within the
reviewed NVS region. This is not byte-preservation or raw-flash interception. Verify the
installed table before any future application boot; the setup check cannot undo earlier
SDK operations against an incorrectly installed table.

## Runtime compatibility decisions

Controlled reset refuses to replace valid credentials with the old legacy/blank defaults.
Controlled setters reject blank/legacy/malformed security inputs and cannot enable autorun.
Explicit healthy settings saves remain supported, including their existing non-atomic
multi-key limitation. Existing normal-profile settings/reset/autorun behavior remains
unchanged. Failed setup cannot re-arm through another setup call, loop, web/CLI or script.

The internal fresh SPIFFS image starts with zero files. The controlled candidate does not
install examples; the existing manual library catalog is not an installation action.
SD contents are separate and are never cleared: an existing card may contain existing
scripts, but none executes automatically. No new language features or HID commands are added.

Owner-private provisioning uses `tools/stage25_fresh_config.py`, the pinned Stage24 image
generator/geometry and explicit owner SSID/AP/web passwords. Known legacy AP credentials
are rejected before generation. Do not commit private configs, generated NVS or owner images.
Existing outputs and backups are never overwritten. No automatic filesystem provisioning,
settings repair, factory erase or writable transition is implemented.

The network/USB/server calls remain subsystem APIs, not proof of host-visible operation.
Internal SDK mount bookkeeping and writable NVS effects are not claimed absent. Initial
SDK/CDC/global-constructor activity is outside application quiescence; no new early-boot
immutability guarantee is made. Physical acceptance requires separate authorization.
