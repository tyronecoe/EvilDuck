# Explicit Mac Caps timing — design and lifetime

Selected source chain: tests/mac_caps -> tests/caps_duration -> tests/led_feedback
and its inherited pinned composition. Baseline is
baddb8f2d3bb6060e0f72e6cbe58377c894c86bb. Root firmware and every prior source,
profile, verifier, package and remote ref are preserved. No SDK/core patch is added.

Authenticated GET/POST `/caps-timing` observes/sets a RAM-only selection. POST
requires mode exactly `standard` (5ms) or `mac` (500ms). Missing/other values fail400;
auth failures remain401 and lock contention409. No request starts a script, sends
HID, writes NVS/settings/storage or changes USB. Default after reboot is5ms;
selection survives completed/cancelled runs until explicitly changed or rebooted.
There is no arming or automatic execution. UI states future and captured timing.

Ordinary Route B admission copies the selected value into its queued request and
Status under the existing publication lock before ownership becomes observable.
The immutable effective value is returned as effectiveCapsMs in HTTP admission,
routeBCapsMs in the coherent /status capture, and requestCapsMs separately from
selectedMs in /caps-timing. Changing RAM selection while a request is queued,
compiling, delayed or pressing cannot change that request. Terminal evidence keeps
its admitted value. CLI Route B uses the same admission function.

The actual selected scheduler sends through `seam.inc`/`com.cpp`/backend lease.
After beginReport succeeds, waitFor samples millis and schedules Release. Only a
single-key report with reportModifiers==0,reportCount==1,key0==0x39 uses the
admission's capsMs. Chords with Shift/Control/Alt/GUI and all other usages retain
5ms. The selected shortcut table has canonical uppercase CAPSLOCK only; no CAPS,
CAPS_LOCK or case-insensitive alias is added. Compiler Op::Key/EventType::KeyTap
preserves the modifier byte through the adapter and report scheduler. Matching
by validated report encoding avoids a second parser or guessed source aliases.

Diagnostic admissions override ordinary selection with their own0=>5/100/250/500ms
snapshot. Existing one-shot5-second focus delay and per-trial record remain. Only
500ms diagnostic is physically confirmed by the owner;100/250 are not proven.
No DELAY statement is reinterpreted as a key hold. No general HOLD/RELEASE support,
global slowdown, host settings alteration or descriptor spoofing is introduced.

All existing STOP/cancel, release attempts, one-second pending/clearing bounds,
backend ownership, readiness polling without submission, ambiguous-called-false
quarantine and no-replay policies remain. The cooperative wait has no sleeping
HTTP handler, callback, critical section or detached timer. Ownership persists
through cleanup. A failed/ambiguous/disconnected operation does not guarantee the
host released a key or restored Caps. No blind toggle is a recovery mechanism.

Feedback continues to represent host-selected LED state for THIS interface.
Fresh=>existing valid session/configured/not-suspended/<=5seconds rules. Stale
current fields remain null; lastKnownCaps/lastKnownNum explicitly retain history,
with reportAgeUs quoted64-bit microseconds (or null if unobserved/clock anomaly).
Session invalidation makes evidence unknown. Neither cached false nor null proves
another keyboard's physical state. The new build ID is
MAC-CAPS-TIMING-20261019-v1. No receiver wire format or transport routing changes.
