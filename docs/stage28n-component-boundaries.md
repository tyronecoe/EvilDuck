# Stage28N actual component and substitution boundary

Native runner compiles these unmodified TinyUSB revision `8a78804ff91271fb32008288777fad9fe73f5735` translation units:

| Source | Real code exercised / limitation |
|---|---|
| src/tusb.c | tusb_rhport_init and endpoint claim/release primitives; all native cases enter the real device initializer |
| src/device/usbd.c | dcd_event_handler, queue_event, tud_task_ext, configuration/reset/control dispatch, endpoint busy/claim/xfer and deinit. Real dispatch calls HID class via real class-driver mapping |
| src/device/usbd_control.c | Real status/EP0 completion/control ACK logic, including SET_PROTOCOL ACK. Native SET_CONFIGURATION establishes mapping; no physical enumeration |
| src/class/hid/hid_device.c | Real init/reset/open/control/report copy/framing/xfer callback and deinit. No direct hand-written application callback substitutes for dispatcher/class bodies |
| src/common/tusb_fifo.c | Compiled unchanged as support; FIFO routines have **no positive executed-function coverage** in this HID/custom-OS fixture, not claimed exercised |

Every case has GNU gcov executed function/range/count evidence from its fresh process, linked to source hashes and host config in JSON. Coverage instrumentation changes host objects, not source or SDK binaries. All21 required vendor C/header files were freshly retrieved/byte-checked against official full revision; preparation was independently exercised into a second minimal source tree, then used for final build. Five C units and16 headers are the actual vendor include closure. There are no SDK header includes in the final minimal tree.

## Fake boundaries

`tests/stage28n/boundary.c/.h` implements DCD/controller primitives: record borrowed pointer/copy at submit, accept/refuse, emit controlled genuine `dcd_event_handler` events, record open/close/deinit calls. It never reads/writes MMIO, registers, FIFO, DMA, device nodes or USB endpoints. Fixture instance0/interface0/EP0x81/KEYBOARD/ID1 are chosen descriptors, **not discovered board values**. Control EP0 transfers are separately recorded. N02 tests raw ID0 byte framing even though the fixture report descriptor declares ID1; it is not a host descriptor-validity claim. N18 likewise observes raw ID1 framing after a boot-protocol property change, not host acceptance of that mismatch. Late-event cases deliberately re-inject the old endpoint/result/length tuple after reuse; that tuple has no authentic old/new token.

Application descriptor/complete/failed callbacks are host observers; no Arduino core is linked. They record instance/type/length and bounded buffer bytes. `submission_identity_exposed:false` annotates the source-verified ABI, not a generated Q or runtime reflection. Diagnostic order numbers establish forced call ordering only; they are not transfer identities. Callback buffer addresses are not published or used to correlate transfers. One diagnostic case intentionally compares/reads the known static class buffer after its callback to expose reuse; this is not a lifetime guarantee for application code.

Supported `OPT_OS_CUSTOM` implementation (`tusb_os_custom.h` + boundary.c): copied ring capacity4, no allocation, timeout0 try receive delivers nonempty FIFO events; default tud_task_ext drains normally. No forced receive-yield remains. Order around reset is inspected through a real callback. Queue saturation returns failure; ISR flag is recorded but no actual ISR exists. Real FreeRTOS non-ISR WAIT_FOREVER send can block instead of returning our forced full result. Mutex acquisition records the actual WAIT_FOREVER argument. Forced would-block/failure returns exercise ignored result paths; they **do not reproduce a kernel wait or prove bounded entry**. Spin functions record balance, without real locks/cores. Real scheduler/ISR/locking behavior remains unexecuted.

Buffers/journals: submissions, callbacks and event logs each128 fixed entries; OS queue4 slots×64B validates actual native event size≤64. Capacity overflow aborts rather than overwriting evidence. Host dcd_event_t is24B in executed sizeof receipts; no target layout measured. Callback declared lengths are recorded, copying at most64B even when an injected declared length70 exceeds the class buffer. That guard is in the fake observer, **not proof the vendor callback validates malformed completion lengths**. This fixture is not a production resource estimate or a zero-heap SDK claim.

## Specifically unexecuted boundaries

**N21 BLOCKED — selected builder DCD runtime.** Builder `components/arduino_tinyusb/src/dcd_dwc2.c` at `afa5cdd0d41d7e465d2e39867b24aef48b1c7b84` is the selected controller code, not upstream DCD. It depends on DWC2 MMIO, hardware endpoint/FIFO interrupt state and ESP32 platform/interrupt support; dwc2_esp32.h uses physical register bases, USB wrapper and ESP-IDF support. Executing it safely would need a separately validated register/platform/controller substitution, beyond this small DCD API boundary. No empty/gated DCD compilation is counted as execution. Source and existing archive instructions are inspected only.

**N22 BLOCKED — protected Arduino USBHID runtime.** Full USBHID.cpp includes Arduino/ESP32 USB descriptor registry, event/runtime and FreeRTOS semaphore/mutex infrastructure. These are not linked into the custom-OS fixture. Compiling an extracted SendReport body or a hand-written semaphore model would not test the actual core TU. Protected source331–374 and existing linked strong complete/weak failed hooks remain source/static evidence only. No installed core alteration or fake replacement is represented as production integration.

All physical controller, host, FreeRTOS, CDC/MSC coexistence, ROM/startup and firmware surfaces are unexecuted. Existing Stage28M is separately rerun unchanged; earlier broad suites are not repeated without a new risk, and their old results are not promoted to fresh counts.
