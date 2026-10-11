# Stage 12 design and compatibility decisions

Baseline: Stage 11 `3714866f88ac8a42cbfffc93bf2ba7572bd3a7b7`.

## Reference established before implementation

Read Stage 9 matrix/reference/roadmap and Stage 10/11 designs and reports, plus actual
expression/symbol, parser, scheduler, HID, attackmode and MSC production modules.
Official variables, quick-reference and lock-key pages are the Stage 9 HTTPS snapshots;
fresh requests return HTTP 403. Hashes/provenance are retained in the Stage 12 source
record. No independent Hak5 runtime comparison is available.

Canonical names: WAIT_FOR_{CAPS,NUM,SCROLL}_{ON,OFF,CHANGE},
SAVE_HOST_KEYBOARD_LOCK_STATE, RESTORE_HOST_KEYBOARD_LOCK_STATE; no arguments.
Current and saved Caps/Num/Scroll variables are unsigned16 Boolean reads; the
RECEIVED_HOST_LOCK_LED_REPLY flag is evidence that a valid report arrived this USB
session, not a claim that a host will synchronize future changes.

## Device-backed registry

Use fixed name lists and typed dispatch with no per-run dynamic symbol entries. All 37 native
names from the 38-name audit are reserved; `$_OS` is deliberately retained as an
extension-defined ordinary variable (no built-in OS claim). Unsupported native reads
and writes diagnose. VAR/DEFINE/READ may not shadow reserved properties. Supported
read-only names cannot be assigned. User variables and text interpolation retain
existing semantics. The sole Stage 3 evaluator gains diagnostic lookup results for
unsupported and unavailable values, not another parser. Syntax preflight knows the
type without reading unknown runtime state.

Seven canonical lock variables are supported. Unknown current/saved lock values
fail at runtime instead of returning FALSE. Received-report defaults FALSE. Other
native properties are deferred rather than returning simulated settings. In
particular CURRENT_ATTACKMODE cannot truthfully describe dynamically enumerated
USB personalities; Stage 10 logical modes do not implement that contract.

Explicit EvilDuck extensions expose logical HID enabled, storage requested,
preparing, locally active, failed, and state enum (off0/preparing1/active2/ejected3/
failed4), lock-known, and a writable uint16 lock timeout (default5000ms; valid1..65535).
These are not host-visible storage/personality assertions. Timeout resets for every
script/live session reset; its assignment uses the existing expression evaluator.
Read-only device state persists independently of user symbols. Ordinary script
completion, STOP/STOP_PAYLOAD and RESET do not erase observed lock evidence; RESET
only clears keyboard ownership. USB loss/new backend initialization invalidates
observed and saved states immediately. First valid report initializes saved attach
state; explicit SAVE overwrites it for that USB session. Saved state persists across
script runs in the same USB session.

## OUT reports and synchronization

Core3.3.0 USBHIDKeyboard::_onOutput ignores len and reads buffer[0]. Override it in a
small derived keyboard without changing its descriptor. USBHID.cpp routes interrupt
OUT ID0 by stripping the report-ID byte, but nonzero-ID control SET_REPORT through
_onSetFeature. Override that hook too for the descriptor's keyboard LED payload.
The hook lacks report-type/session metadata; document that limitation instead of
claiming full control-request authentication. Validate ID1, nonnull, exactly1 byte,
reserved padding bits zero; five LED bits are permitted, only three lock bits used.
The upstream ID0 zero-length routing dereference occurs before the device hook and
cannot be repaired without changing the pinned core; retain as upstream limitation.

Fixed snapshots in a dedicated short critical section avoid blocking USB callbacks on the executor mutex. Tag
observations/saved state and transition counters with USB session generation;
explicit stale-token input is rejected. Disconnect invalidation occurs in the USB
callback and mounted-state falling-edge fallback. Physical USB has no wire epoch;
a delayed packet first delivered after reconnect cannot be intrinsically identified
as old. Do not claim otherwise. Monotonic per-lock transition counters distinguish
real changes from repeated reports and preserve rapid changes between updates.
Counters/session generations are uint32 and wrap at2^32; at the bounded wait deadline a full-cycle ABA would require impractical transition throughput. Physical USB-session provenance still has no wire token.

The first clean embedded build rejected a lock-free atomic assertion: this toolchain does not guarantee lock-free32-bit C++ atomics. The final design uses native portMUX critical sections containing only fixed copies/bit operations, and a separate host mutex. There is no callback queue, allocation, I/O, executor lock or CAS retry/drop policy. Snapshots and all transition counters update together.

## Cooperative commands

ON/OFF waits complete only on known observed desired state. CHANGE with no initial
feedback establishes a baseline on the first report, then waits for a transition.
All waits use wrap-safe deadlines, default5000ms. This bounded timeout is a safety
divergence from documented indefinite waits. Cancellation uses Stage 11 releases.
SAVE requires known state. RESTORE requires a known saved/current state in the same
session and HID enabled; persistent keys/modifiers must first be explicitly released.
Restore presses/releases one lock key at a time via the existing scheduler and
requires a subsequent matching observed transition, never queue acceptance as ACK.
A total deadline and bounded toggle budget prevent indefinite host-state contention.
No automatic save/restore on script completion and no new USB personality.

All changes and verification are offline; no physical USB/HID/storage operations.
