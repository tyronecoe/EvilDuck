# Stage 14 internal-variable capability matrix

Baseline inventory: all **38** Stage 9 native/extension names. Status is production behavior, not parser recognition. The 37 native names are protected by `internal_vars::reserved`; `$_OS` remains extension-defined. Seven lock properties plus five random/jitter properties are implemented. Twenty-five native properties remain unsupported and reserved. No unsupported property accepts a fake VAR/DEFINE/READ declaration or write.

The registry is fixed name arrays plus typed dispatch in `duck_vars.cpp`, declared in `internal_vars.h`; no dynamic table, symbol slot, or second expression parser. Lookup status distinguishes Number, Unsupported, Unavailable, Undefined and RandomError; entropy faults never masquerade as unknown host lock state. Current/saved lock evidence comes from `hid_backend.cpp`; extension storage reads come from actual `attackmode.cpp`/`usb_msc.cpp`.

| Name | Feasibility | Stage 14 behavior | Type / access / default | Lifetime and missing dependency |
|---|---|---|---|---|
| $_BUTTON_ENABLED | Partially implementable; wiring must be verified | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | GPIO0/bootstrap safety and button event/debounce subsystem missing; EN is not a user button |
| $_BUTTON_PUSH_RECEIVED | Partially implementable; wiring must be verified | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | GPIO0/bootstrap safety and button event/debounce subsystem missing; EN is not a user button |
| $_BUTTON_TIMEOUT | Partially implementable; wiring must be verified | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | GPIO0/bootstrap safety and button event/debounce subsystem missing; EN is not a user button |
| $_BUTTON_USER_DEFINED | Partially implementable; wiring must be verified | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | GPIO0/bootstrap safety and button event/debounce subsystem missing; EN is not a user button |
| $_CAPSLOCK_ON | Implementable; implemented in software | Observed LED bit; unknown read errors | uint16 Boolean0/1; read-only; unknown | USB session; last observed report, not proof of OS synchronization |
| $_CURRENT_ATTACKMODE | Partially implementable; active descriptor contract needed | Unsupported; reserved reads/writes/declarations error | No guessed currently-operating USB value | Logical Stage10 mode is not a USB-personality change; exact active identity/endian contract needs dedicated review |
| $_CURRENT_PID | Partially implementable; active descriptor contract needed | Unsupported; reserved reads/writes/declarations error | No guessed currently-operating USB value | Logical Stage10 mode is not a USB-personality change; exact active identity/endian contract needs dedicated review |
| $_CURRENT_VID | Partially implementable; active descriptor contract needed | Unsupported; reserved reads/writes/declarations error | No guessed currently-operating USB value | Logical Stage10 mode is not a USB-personality change; exact active identity/endian contract needs dedicated review |
| $_EXFIL_LEDS_ENABLED | Partially implementable; RGB policy needed | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | One RGB pixel, not independent Hak5 LEDs; truthful indication/priority/driver policy missing |
| $_EXFIL_MODE_ENABLED | Partially implementable; RGB policy needed | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | One RGB pixel, not independent Hak5 LEDs; truthful indication/priority/driver policy missing |
| $_HOST_CONFIGURATION_REQUEST_COUNT | Partially implementable; USB request hook needed | Unsupported; reserved reads/writes/declarations error | No fabricated enumeration count | Pinned public device hooks do not expose canonical configuration-request counter; no OS inference |
| $_INJECTING_LEDS_ENABLED | Partially implementable; RGB policy needed | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | One RGB pixel, not independent Hak5 LEDs; truthful indication/priority/driver policy missing |
| $_JITTER_ENABLED | Implemented cooperative scheduler control | Validated Boolean0/1 read/write | uint16 Boolean; defaultFALSE | Script/reset lifetime; pending event retains its selected interval |
| $_JITTER_MAX | Implemented cooperative scheduler control | Numeric read/write | uint16 milliseconds; default20; zero valid | Script/reset lifetime; added uniform0..MAX prepress wait, not total-host-cadence promise |
| $_LED_CONTINUOUS_SHOW_STORAGE_ACTIVITY | Partially implementable; RGB policy needed | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | One RGB pixel, not independent Hak5 LEDs; truthful indication/priority/driver policy missing |
| $_LED_SHOW_CAPS | Partially implementable; RGB policy needed | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | One RGB pixel, not independent Hak5 LEDs; truthful indication/priority/driver policy missing |
| $_LED_SHOW_NUM | Partially implementable; RGB policy needed | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | One RGB pixel, not independent Hak5 LEDs; truthful indication/priority/driver policy missing |
| $_LED_SHOW_SCROLL | Partially implementable; RGB policy needed | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | One RGB pixel, not independent Hak5 LEDs; truthful indication/priority/driver policy missing |
| $_NUMLOCK_ON | Implementable; implemented in software | Observed LED bit; unknown read errors | uint16 Boolean0/1; read-only; unknown | USB session; last observed report, not proof of OS synchronization |
| $_OS | Partially implementable extension | Ordinary extension/user global; no built-in detection | User type/value; no automatic default | Script lifetime; OS_DETECT dependencies/heuristic reference not implemented |
| $_RANDOM_CHAR_KEYCODE | Deferred reference-dependent feature | Unsupported; reserved reads/writes/declarations error | No invented seed/packed scancode representation | See stage14-deferred-features.md; no seed.bin access/write |
| $_RANDOM_INT | Implemented device-backed sampling | Fresh inclusive random read; invalid range/source failure errors | uint16 read-only; default range0..9 | Native esp_random per draw; no preflight sampling, no seed.bin claim |
| $_RANDOM_LETTER_KEYCODE | Deferred reference-dependent feature | Unsupported; reserved reads/writes/declarations error | No invented seed/packed scancode representation | See stage14-deferred-features.md; no seed.bin access/write |
| $_RANDOM_LOWER_LETTER_KEYCODE | Deferred reference-dependent feature | Unsupported; reserved reads/writes/declarations error | No invented seed/packed scancode representation | See stage14-deferred-features.md; no seed.bin access/write |
| $_RANDOM_MAX | Implemented range setting | Validated numeric write/read | uint16 read/write; default9 | Script/reset lifetime; reversed bounds allowed temporarily, draw rejects |
| $_RANDOM_MIN | Implemented range setting | Validated numeric write/read | uint16 read/write; default0 | Script/reset lifetime; reversed bounds allowed temporarily, draw rejects |
| $_RANDOM_NUMBER_KEYCODE | Deferred reference-dependent feature | Unsupported; reserved reads/writes/declarations error | No invented seed/packed scancode representation | See stage14-deferred-features.md; no seed.bin access/write |
| $_RANDOM_SEED | Deferred reference-dependent feature | Unsupported; reserved reads/writes/declarations error | No invented seed/packed scancode representation | See stage14-deferred-features.md; no seed.bin access/write |
| $_RANDOM_SPECIAL_KEYCODE | Deferred reference-dependent feature | Unsupported; reserved reads/writes/declarations error | No invented seed/packed scancode representation | See stage14-deferred-features.md; no seed.bin access/write |
| $_RANDOM_UPPER_LETTER_KEYCODE | Deferred reference-dependent feature | Unsupported; reserved reads/writes/declarations error | No invented seed/packed scancode representation | See stage14-deferred-features.md; no seed.bin access/write |
| $_RECEIVED_HOST_LOCK_LED_REPLY | Implementable; implemented in software | Valid LED payload received this session | uint16 Boolean0/1; read-only; FALSE | USB session; false is absence of evidence, not locks OFF |
| $_SAVED_CAPSLOCK_ON | Implementable; implemented in software | First observed attach state or explicit SAVE; unknown read errors | uint16 Boolean0/1; read-only; unknown | USB session; first valid report/SAVE, cleared on loss |
| $_SAVED_NUMLOCK_ON | Implementable; implemented in software | First observed attach state or explicit SAVE; unknown read errors | uint16 Boolean0/1; read-only; unknown | USB session; first valid report/SAVE, cleared on loss |
| $_SAVED_SCROLLLOCK_ON | Implementable; implemented in software | First observed attach state or explicit SAVE; unknown read errors | uint16 Boolean0/1; read-only; unknown | USB session; first valid report/SAVE, cleared on loss |
| $_SCROLLLOCK_ON | Implementable; implemented in software | Observed LED bit; unknown read errors | uint16 Boolean0/1; read-only; unknown | USB session; last observed report, not proof of OS synchronization |
| $_STORAGE_ACTIVITY_TIMEOUT | Partially implementable; activity instrumentation needed | Unsupported; reserved reads/writes/declarations error | No fake countdown/default | Local backing-media state is available, canonical host-activity countdown is not instrumented |
| $_STORAGE_LEDS_ENABLED | Partially implementable; RGB policy needed | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | One RGB pixel, not independent Hak5 LEDs; truthful indication/priority/driver policy missing |
| $_SYSTEM_LEDS_ENABLED | Partially implementable; RGB policy needed | Unsupported; reserved reads/writes/declarations error | No exposed value or mutable setting | One RGB pixel, not independent Hak5 LEDs; truthful indication/priority/driver policy missing |

No native property is declared fundamentally hardware-inapplicable solely because its driver is missing. Independent physical dual LEDs, a reset/EN user-input interpretation and authoritative OS identification are hardware/semantic mismatches; software equivalents require separate review. Physical lock support remains unverified on the user’s High Sierra host.

## Explicit EvilDuck extensions

| Name | Type / access / default | Evidence and lifetime |
|---|---|---|
| `$_EVILDUCK_LOCK_KNOWN` | Boolean; read-only; FALSE | Valid report observed this USB session; same evidence limitation as received flag |
| `$_EVILDUCK_LOCK_TIMEOUT` | uint16 milliseconds; read/write; 5000; valid1..65535 | Executor policy only. Assignment through Stage3 evaluator; cannot VAR/DEFINE shadow. Resets when user-variable run state resets, including STOP/start/end; persists across accepted live commands until reset |
| `$_EVILDUCK_HID_ENABLED` | Boolean; read-only; initial TRUE | Stage10 logical injection gate, not host enumeration/personality |
| `$_EVILDUCK_STORAGE_REQUESTED` | Boolean; read-only; initial FALSE | Requested logical mode, preserved through failures/ejection, cleared OFF/cancelled preparation |
| `$_EVILDUCK_STORAGE_PREPARING` | Boolean; read-only; initial FALSE | Actual Stage10 cooperative preparation state |
| `$_EVILDUCK_STORAGE_ACTIVE` | Boolean; read-only; initial FALSE | Actual validated local raw backing media. Does not prove host mounted USB MSC |
| `$_EVILDUCK_STORAGE_FAILED` | Boolean; read-only; initial FALSE | Actual Stage10 Failed state, not host-side error classification |
| `$_EVILDUCK_STORAGE_STATE` | uint16 enum; read-only;0 | Off0 / Preparing1 / Active2 / Ejected3 / Failed4 from actual Stage10 state |

These eight extensions are reserved and do not consume the 16 ordinary variable slots. State is read afresh, not cached in a mutable user symbol. Actual requested/preparing/active/ejected/failed/retry/OFF paths have production-module fault tests. Nothing exposes canonical host-visible CURRENT_ATTACKMODE under an extension alias.

## Command and evidence limits

Nine exact no-argument WAIT_FOR variants, SAVE_HOST_KEYBOARD_LOCK_STATE and RESTORE_HOST_KEYBOARD_LOCK_STATE are implemented. Waits and restore have an explicit total timeout; restore refuses unknown state, disabled HID or held ownership. Accepted IN reports are not evidence of a lock-state change. Matching subsequent observed transitions are required before continuing restore. ON/OFF waits require known observed bits; CHANGE requires a real per-lock transition after baseline. Save is session-local and does not persist NVS.

Preflight rejects malformed syntax and reserved declarations/writes before preceding HID output. Missing feedback is runtime-dependent and can fail after earlier valid output. Unknown/unsupported internal interpolation errors rather than typing a literal fake setting. Unknown ordinary `$_CUSTOM` names remain user extensions for compatibility; the documented native names are protected. Case is significant, consistent with ordinary variables.

Firmware/mocks are software evidence only. Packet delivery, host LED policy, callback routing over physical USB, real task-stack/heap contention and High Sierra synchronization require separately authorized hardware validation.

Stage14 mutable random/jitter settings reset with begin/end/STOP/error; live commands retain settings until reset. RESET only clears keyboard ownership and does not reset these settings. Source stream is device-owned and not reseeded by script resets. Host-only seeded/injected sources are testing adapters. Earlier feasibility descriptions incorrectly grouped JITTER_ENABLED with RGB policy; jitter needs the scheduler/RNG, not LED hardware.
