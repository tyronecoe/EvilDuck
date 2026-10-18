# USB keyboard descriptor and LED receive-path investigation

Source references are paths within the verified isolated Arduino3.3.0 core or the
final composed application. `caps-duration-feedback-evidence.json` records hashes,
linked descriptor bytes and the actual shipped HID object's relocation/disassembly.
`caps-duration-build.json` records final ELF and source/archive closure.

## Advertised keyboard, without a descriptor change

- Application `hid_backend.cpp`: static `USBHID HID` precedes `FeedbackKeyboard`.
  `USBHID.cpp:288–300` initializes interface protocol on the first constructor.
  Therefore this composition requests protocol NONE(0), not boot-keyboard protocol1.
  This is a valid report-protocol HID keyboard configuration, not proof that the
  Mac recognized it. Changing this could change host binding/caches and endpoint
  allocation; this release deliberately does not change it.
- `USBHIDKeyboard.cpp:35–51` contributes the standard keyboard report descriptor.
  Exact67-byte descriptor extracted from the final linked ELF matches the installed
  baseline's descriptor: SHA256
  `c988ffa0edde6feba3bbad521bec074df11ddf73aac98559204d9c3574a66dea`.

  Generic Desktop usage Keyboard, Application collection, reportID1. Input is
  8modifier bits, reserved8bits and six8bit key usages. Output is5LED bits
  Num/Caps/Scroll/Compose/Kana plus3constant padding bits. Application receiver
  accepts only the supported3lock bits; it does not claim all five capabilities.
- `USBHID.cpp:193–215`, `usbd.h:TUD_HID_INOUT_DESCRIPTOR`: interface class3,
  subclass0/protocol0, interrupt OUT and IN, 64byte max packets,1ms advertised
  interval. Endpoint numbers are runtime-allocated; a linked source inventory is
  not a physical descriptor capture. CDC coexists through unchanged core setup.
  Active protocol is sampled separately; owner baseline showed report mode1.
- No VID/PID, strings, report IDs, descriptor bytes, partition table, SDK archive
  or protocol fallback is changed by this task. The compiled report descriptor,
  its USBHIDKeyboard object and Arduino USBHID/core inputs are hash-identified.

## All supported receive routes and boundaries

Pinned TinyUSB source reference revision
`8a78804ff91271fb32008288777fad9fe73f5735`,
`src/class/hid/hid_device.c` SHA256
`e12cd2ea98d60d3ebe2741f3b2156c1d53e6fce4d4f48d603deda58324240a99`,
was freshly retrieved and hash-checked against historical provenance. Source
behavior and shipped object references are separate evidence levels; there is no
new source-to-object rebuild attestation for the precompiled SDK.

1. `hidd_control_xfer_cb`, source325–343: SET_REPORT SETUP checks wLength against
   endpoint buffer capacity. ACK takes report type/ID from wValue and length from
   request, strips a matching optional leading nonzero ID under its bounds rule,
   then calls `tud_hid_set_report_cb`. Setup failures/stalls and control transfers
   that never reach ACK do not arrive at the instrumented application boundary.
2. `hidd_open`,252–267: opens descriptor endpoint pair and arms OUT. In
   `hidd_xfer_cb`,387–416, successful OUT completion calls that SAME callback with
   instance,ID0,typeOUTPUT and endpoint buffer/length. Failed transfers invoke
   `tud_hid_report_failed_cb` instead, then OUT is rearmed. No separate successful
   interrupt-OUT receiver bypasses the raw hook in these inspected paths.
3. Actual shipped `libarduino_tinyusb.a` SHA256
   `dece5cdd1d132dabb5e2022d8e3d293592b10f03de5902d9740994d652dd9a18`:
   `hid_device.c.obj` has callback references from control and transfer functions.
   The receipt retains exact object SHA and disassembly; no full-controller
   execution or physical bus capture is claimed.
4. Patched `USBHID.cpp:tud_hid_set_report_cb` invokes raw diagnostic before its
   instance/null/length/type/registry checks. It counts both successful paths above
   if reached. It normalizes only the existing registered/prefixed OUTPUT forms.
   FEATURE is separate; it never becomes keyboard LED OUTPUT. No guessed ID0
   unprefixed-byte fallback is added. The real callback/outlined diagnostic helper
   and real completion/lifecycle hooks are verified in the final linked ELF.
5. Registry/object comparison and actual derived `_onOutput` reach
   `hid_backend::receiveLockReport`, which checks ID1, one-byte length, reserved
   padding, configuration, suspension and feedback session. No payload contents
   beyond accepted lock bits are logged. Unknown/stale locks remain null.

## Conclusion and next discriminating observation

No concrete receive-routing defect is established by the owner's zero-arrival
samples. They establish absence at SET_REPORT callback entry, not at the wire.
They do not establish an ID0 format or justify FEATURE routing. Invalid frames,
unknown IDs, unsupported boot forms and session loss still fail visibly.

First perform the ONE selected duration trial and manual unshifted `abc` check.
That tests a specific Caps-output timing hypothesis without changing recognition.
If it works, feedback is still a separate question. Optional owner-only read-only
I/O Registry inspection (OWNER-CHECK.md) should identify whether the matching USB
interface has an IOHID keyboard service and exposes the same report descriptor/LED
OUTPUT. No matching service narrows the next investigation to enumeration/binding.
A matching correct service with no firmware arrivals leaves host emission, failed
OUT/control stages or USB transport unresolved; another host comparison or a
separately reviewed capture may then be justified. Windows remains untested.
Do not reflash solely to repeat the same zero-arrival observation.
