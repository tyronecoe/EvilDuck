# Stage 11 persistent keyboard ownership design

Baseline: Stage 10 `5ac88388635ac2d6e464eb17006aea2e8819dae4`.
Scope: keyboard ownership, canonical clearing/cancellation, parser validation and
transport-loss recovery. No MSC, partition, Micro, expression or Stage 12 changes.

## Reference and compatibility decisions before implementation

Official Hak5 pages: [holding keys](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/holding-keys.md),
[keystroke injection](https://documentation.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection.md),
[payload control](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/payload-control.md),
[quick reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference.md).
New HTTPS retrieval returns 403. The Stage 9 official snapshots were read and their
SHA-256 verified against its recorded provenance; see Stage 9 reference-source JSON.
No independent Hak5 compiler/device reference is available. Page instructions and
host-command examples are not executed. This is not a latest-reference claim.

Documented forms: `HOLD key`, `RELEASE key`, `INJECT_MOD modifier`, standalone
`INJECT_MOD` preceding modifier holding, `RESET`, `STOP_PAYLOAD`. Each HOLD/RELEASE
accepts one physical named key/alphanumeric or modifier, not a new chord syntax.
RESET clears the keyboard buffer and continues flow; it never reboots hardware.
STOP_PAYLOAD uses existing STOP cancellation. RESTART_PAYLOAD remains unsupported.

INJECT_MOD inline emits one transient modifier-only report and restores persistent
ownership. Standalone INJECT_MOD is a non-output prefix annotation for the following
injection; it does not acquire a modifier or alter later masks. Scope across arbitrary
commands is undocumented. Because EvilDuck already accepts modifier-only commands
and direct modifier HOLD/RELEASE, the annotation needs no sticky permission state.
Direct modifier ownership without the prefix remains an explicit compatibility
extension; both prefixed and unprefixed RELEASE appear in official examples. Do not
invent a sticky modifier mask, numeric INJECT_MOD syntax, or undocumented parameters.

HOLD uses physical usage names (as previous bare keys do), not locale string
translation; single punctuation may be rejected unless a named physical key is used.
Text retains US/DE translation. Held modifiers intentionally affect text/Enter/dead
keys through OR merging. A transient key already persistently held stays down,
without fabricating a release/repress edge. OS autorepeat/accent output is host policy.
HOLD/RELEASE/inline INJECT_MOD participate in the existing default-delay/history
mechanism; repeated HOLD/RELEASE is logically idempotent. RESET/standalone INJECT_MOD
and STOP do not replace repeat history. Rejected/unsupported syntax fails preflight.

## Bounded state and transport contract

One backend fixed modifier byte + six usage bytes owns persistent keys. Ownership
is scoped by the existing exclusive script/live executor. Starting a script clears
previous live ownership; live commands cannot mutate an active script. Live holds
may persist across accepted live commands until release/reset/STOP/transport loss.

No report queue or dynamic ownership structures. HOLD proposes a fixed local copy and commits only after endpoint acceptance.
RELEASE clears logical ownership immediately and retries one fixed target report
before any later press, so transport refusal cannot restore released keys. Idempotent unchanged operations need
no redundant report. Press reports merge persistent and transient keys, deduplicate
usages, OR modifiers and reject a seventh distinct usage before sending or changing
ownership. A refusal retries one pending scheduler operation; an overflow fails
safely through the existing source/line runtime-error path. Invalid requests never
silently discard a persistent or transient key. Ordinary release restores the held
report; cancellation/RESET clear logical ownership immediately and retain one
priority zero-report obligation until accepted. New presses cannot overtake it.

Pinned Arduino 3.3.0 USB STOPPED event is posted from tud_umount_cb. The asynchronous
handler records only an atomic loss flag, without taking the execution lock or
sending HID. Main-loop update observes that flag and mounted-state falling edges via the pinned
ESPUSB public Boolean conversion (started && tinyusb_device_mounted),
clears ownership, cancels running work and prioritizes a zero report on reconnect.
Readiness false alone can mean backpressure/suspend and must not imply disconnect.
A loss flag survives a disconnect/reconnect between main-loop ticks. Every enqueue
checks the flag and mounted state again to reject loss observed between update
and a press. The SDK submission/event race is not an atomic host-ACK guarantee. Polling is a
fallback, not proof that every physical cable event is delivered by the SDK.

All ownership operations run under the existing recursive execution lock. The event
flag is atomic. Five-ms transient dwell and bounded locale strokes remain. Release
acceptance means queued to TinyUSB, not acknowledged by the host; disconnected hosts
cannot receive a release. A refused release remains pending and no stale key is
re-injected. Real transport behavior, autorepeat, macOS High Sierra Option/dead keys,
and task/heap high-water still require separately approved physical testing.
