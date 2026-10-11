# Stage 12 pinned HID OUT contract and evidence limits

Source: installed Arduino ESP32 **3.3.0** USBHIDKeyboard.cpp/.h,
USBHID.cpp/.h, USB.cpp/.h; hashes and upstream URLs are in
[reference sources](stage12-reference-sources.json). The SDK keyboard descriptor
uses `TUD_HID_REPORT_DESC_KEYBOARD(HID_REPORT_ID(HID_REPORT_ID_KEYBOARD))`.
Its keyboard report ID is1; IN payload is modifier/reserved/six keys (8 bytes).
Keyboard LED output is one byte: Num bit0, Caps bit1, Scroll bit2, Compose bit3,
Kana bit4, three padding bits. Accepting bits3/4 is descriptor-compatible, not a
claim to implement Compose/Kana commands. Padding bits5..7 reject.

## Actual pinned routing

`USBHID.cpp::tud_hid_set_report_cb` treats report_id0 with type0/OUTPUT as interrupt
output. It first tries a report0 device; if none, it takes buffer[0] as report ID
and forwards buffer+1 with size-1 to `_onOutput`. Thus the device hook expects
ID1 and one normalized payload byte, not a two-byte ID+LED wire buffer.

For nonzero report ID, the same callback calls `tinyusb_on_set_feature`, which
invokes `_onSetFeature`; the branch does not retain the OUTPUT/FEATURE type for
the device. The Stage12 derived keyboard overrides both virtual hooks and forwards
them to the same strictly ID/length/padding-validated production receiver. The
original `_onOutput` dereferences buffer[0] without checking len and posts a USB
keyboard LED event with portMAX_DELAY. The derived handler bypasses both behaviors:
no event-queue blocking, no unchecked payload read, no custom descriptor/identity.
No other firmware module registered a keyboard LED event subscriber to preserve.

The callback captures the current firmware USB-session generation at entry.
Receiver validation checks that token against the current snapshot inside a
separate short critical section. It rejects detached endpoints, latched transport
loss and stale explicit tokens. Disconnect callback latches loss before invalidating
feedback. Main-loop mounted falling-edge detection is an additional fallback.

## Upstream limitations retained explicitly

* The pinned top-level ID0 routing accesses buffer[0] and subtracts1 before the
  derived handler can see a zero-length buffer. Stage12 prevents zero-length/null
  dereference at the device hook, but does not repair this earlier upstream path.
  Normal TinyUSB OUT packet delivery must be checked physically; deliberately
  malformed traffic at this boundary requires a separate stack-hardening review.
* `_onSetFeature` lacks report-type information. A descriptor-conforming host
  control OUTPUT report is supported through this route; the firmware cannot
  distinguish an otherwise identical malformed FEATURE request at that hook.
  The keyboard descriptor advertises LED OUTPUT and no matching feature payload.
  Do not claim full request-type authentication from ID/length validation.
* USB LED reports contain no firmware session token or injection transaction ID.
  Tokens reject previously captured callbacks, but a delayed packet first delivered
  after reconnect has no intrinsic prior-session identity. A matching LED change
  is observed evidence of target state, not proof it was caused by our key tap.
* A host may not send every report or synchronize each lock key. All three exposed
  values mean bits of the latest valid keyboard LED report. They do not certify
  OS policy, real keyboard indicators or another attached keyboard's state.
* There is no timeout-based aging of passive observed variables in the same USB
  session. Wait/restore timeouts bound commands; a static observed bit remains
  the last report, not an assertion that fresh feedback arrived continuously.

## Synchronization and bounds

Native32-bit C++ atomics are not guaranteed lock-free by this toolchain; the
initial embedded compile correctly rejected that assumption. The final fixed
20-byte LockState holds session uint32, known/saved-known flags, current/saved
three-bit masks and three uint32 transition counters. Native portMUX critical
sections protect only fixed state copies/bit operations. Host tests use a dedicated
mutex with the same scope. No execution Guard, filesystem/driver calls, HID sends,
logging, heap allocation or event queue occurs inside the feedback critical section.
This is not a measured real-time latency guarantee; physical contention is pending.

First evidence saves attach state. Explicit SAVE copies only known evidence.
Disconnect/new backend begin clears current and saved evidence and counters while
incrementing session. Repeated identical reports do not count as transitions;
rapid changes are retained even when the mask returns to baseline before update.
Counter/session wrap is defined unsigned32; full2^32 transition alias cannot occur
at USB keyboard throughput inside the maximum65535ms wait. No unlimited history is
claimed. ON/OFF waits accept already observed desired state. Unknown CHANGE waits
first establish a baseline, then require a transition. Default total deadline is
5000ms; the explicit EvilDuck timeout property permits1..65535.

Restore refuses held ownership, disabled HID and unknown state. It selects one
mismatched lock bit, schedules a transient physical usage (Num0x53/Caps0x39/
Scroll0x47), releases it, and requires a subsequent observed matching transition.
The pending press rechecks state after IN backpressure, so it cannot knowingly
undo a bit already restored before enqueue. Host races after that check remain
possible. Six planned-toggle maximum and one overall deadline bound contention.
Endpoint refusal/5ms dwell/release/feedback waits remain cooperative. STOP/errors
clear runtime-owned keys through Stage11 priority-release retry. No host release
is claimed while disconnected. Lock waits/save/restore do not replace legacy repeat
history; a later REPEAT still repeats the last existing repeatable command.

## What tests prove

Production virtual handlers, receiver, registry, scheduler, expression/control
flow, cancellation and Stage10 state modules are compiled with mocked USB/storage/
clock. Every valid LED byte, invalid payload, observed transition, timeout, stale
explicit token, concurrency and exact restore IN payload is tested. The tests do
not execute all of Arduino/TinyUSB over a physical endpoint, prove control versus
interrupt transfer routing on a host, or validate macOS High Sierra behavior.

Later authorized validation should use harmless plain-text TextEdit fixtures,
match input layout, observe actual OUT reports, and independently check Caps/Num/
Scroll, save/restore, release/reconnect and report delivery under web/SD traffic.
No hardware validation, migration or host key injection happened in this stage.
