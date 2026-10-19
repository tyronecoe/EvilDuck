# Language support, host state and the finite reflection scope

## Actual selected Route B versus legacy engine

| Feature | Selected Route B evidence | Boundary |
|---|---|---|
| STRING/STRINGLN, text blocks | Existing compiler/runtime and composed tests | US bounded character path; not arbitrary Unicode or all locales |
| Variables, integer expressions, IF, WHILE, FUNCTION/RETURN | Existing core.cpp compiler/runtime and regression fixtures | Documented bounds remain; unrelated keyboard indicators do not block these features |
| CAPSLOCK | shortcut_keys.h named=>0x39, Op::Key/modifier0, Adapter::receive=>route_b::key=>com scheduler | Opt-in captured500ms for standalone reports; new ordinary path requires owner acceptance |
| Caps chord | Compiler preserves modifiers to scheduler | Remains short5ms; not silently extended |
| General HOLD/RELEASE | Preview grammar recognizes; Adapter rejects ownershipCommands before output | Unsupported in composed Route B; no broad support added |
| WAIT_FOR_CAPS_ON/OFF/CHANGE | Not recognized by selected Route B compiler | Preflight rejects before output. Do not use these in new acceptance script |
| $_CAPSLOCK_ON | Route B expression environment does not connect legacy internal registry | Unsupported here; native test checks rejection, not parser-name recognition |
| SAVE/RESTORE_HOST_KEYBOARD_LOCK_STATE | Not selected Route B commands | Unsupported here; no automatic restore claim |
| Legacy lock commands/variables | Shared legacy com.cpp and duck_vars.cpp have separate implementations | Not evidence those features work through Route B; ordinary web/CLI live dispatch may follow legacy paths |

Legacy source context: duck_vars.cpp:157–234 fixed internal registry;
com.cpp lock commands use actual lockState known/session/change counts, configurable
legacy lock timeout (default5000ms,1..65535ms) and cooperative waits/restore.
Those legacy semantics do not become Route B support merely because modules link.
They depend on host reports visible to this interface. Future Route B lock waits
need their own reviewed cooperative timeout/cancel/unknown-state contract. No such
feature is implemented by this patch. Normal legacy Caps timing remains unchanged.

## Host feedback evidence and references

Owner's500ms diagnostic changed EvilDuck-generated case and produced fresh Caps
OUTPUT. Laptop/Razer state can remain independent. HID LED OUTPUT is addressed to
this interface; it is not a light sensor or another keyboard's keystroke stream.
No descriptor, passthrough or longer press is promised to reveal global state.
A future explicitly run Mac helper could select a physical keyboard and forward
only its lock state, but would be host-assisted, require native High Sierra
validation and separate authorization. No broad recorder/helper is implemented.

Apple source retrieved from:
https://github.com/apple-oss-distributions/IOHIDFamily/blob/IOHIDFamily-1446.140.2/IOHIDEventSystemPlugIns/IOHIDKeyboardFilter.mm
SHA2568025012b790ee619a6c839ded944e7a27d35069b0bd05e4f14bb9be31981634a,
97,318bytes. Lines397–415 read HIDCapsLockStateCache;2383–2426 retain per-filter
Caps state and set the LED element on `_service`. This is source context consistent
with owner observations, not attestation of the owner's running OS. Its timing
constant/configuration is not used to infer this device's minimum threshold.

Hak5 official quick reference:
https://docs.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference
Fresh retrieval returned HTTP403 in this environment. The owner supplied its Lock
Keys macOS caveat; we record that provenance rather than claiming fresh independent
retrieval. No evidence establishes a genuine Rubber Ducky always bypasses per-
keyboard host state. This task makes no full DuckyScript3.0 compatibility claim.

## Existing custom fixed-message protocol — inspected, unchanged

`led_receiver.cpp:consume` uses Caps bit1 transitions as CLOCK and Num bit0 as DATA.
Scroll bit2 is accepted as feedback but NOT required by this decoder. It searches
32-bit sync0x45445231 (EDR1), then reads one length byte, exactly the17-byte
`EVILDUCK TEST 123` payload and big-endian CRC16-CCITT-FALSE (init0xffff/poly0x1021)
over length+payload. Size equality and exact fixed text are mandatory. No arbitrary
message/log/file/keystroke collection exists. Ring64;16 events serviced per turn;
RAM-only;120-second timeout; authenticated start/stop/clear/download unchanged.
A409 Already receiving is separate from Caps execution busy.

Remaining physical dependency: independent, reproducible Num DATA feedback plus
clock/data ordering/rate sufficient for the exact decoder. Caps alone cannot prove
a full frame. Native mock frame success is not native host-helper or physical
message success. Scroll is optional diagnostic evidence, not a hidden completion
gate for EDR1. Complete fixed-message delivery remains unverified.

Smallest next channel observation (owner-operated only after separately reviewed
installation): with no receiver/script active, note build/boot/session and fresh
baseline reports; focus an empty editor and run ONCE:

```
DELAY 5000
NUMLOCK
DELAY 4000
NUMLOCK
```

Refresh the authenticated LED snapshot between toggles and afterward. Seek actual
same-session accepted OUTPUT with Num bit0 changed then returned, and report age.
Do not use another keyboard's light as proof. This tests the existing short Num
path, whose physical behavior is unverified; no response cannot by itself prove
all possible Num encodings/timings are unavailable. Stop after this bounded trial,
record ambiguity and do not fake data or replay indefinitely. Scroll can be tested
separately only if later needed; it is not needed for current EDR1.

If Num remains unavailable, EDR1 is blocked by its DATA channel. A separately
versioned **EDR2-CAPS-ONLY-FIXED proposal** could encode the same fixed payload with
bounded Caps transition timing and checksum, eliminating Num dependence. It is
NOT implemented or wire-compatible with EDR1; timing/error bounds and a native
High Sierra helper would require separate review/tests. It must remain finite,
RAM-only, explicit, no arbitrary typing capture. Do not substitute that proposal
for evidence that the current protocol delivered a message.
