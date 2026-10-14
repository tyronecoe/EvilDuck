# Selected controller ownership and native execution boundary

Selected source: builderafa5cdd0d41d7e465d2e39867b24aef48b1c7b84/components/arduino_tinyusb/src/dcd_dwc2.c, SHA d12ef24b093d542a5e42d7cdf10d4170b1d139c5eb061db26df3b26cb1eee81a. CMakeLists.txt26–49 explicitly selects this file plus pinned dwc2_common.c; commented upstream dcd_dwc2.c is NOT substituted. Exact TinyUSB revision8a78804ff91271fb32008288777fad9fe73f5735 supplies type/common/header/stack inputs. IDFb66b5448e0dfac6be135e6f0ac21010aba231180, Arduino3.3.0/SDKidf-release_v5.5-b66b5448-v1 unchanged. Package-recorded abbreviations, full public-source pins, byte hashes and partial object evidence remain different provenance levels; complete shipped source-to-object equivalence is unproven.

ESP32S3 source defaults in tusb_mcu.h384–396/tusb_option.h255–269 select slave1/DMA0 absent an override. Pinned builder configuration/recipe and existing archive handle_epin_slave/dfifo_write_packet relocations corroborate that path; native tests select the same defaults but CUSTOM OS and HID-only fixture, not actual board runtime. dwc2_esp32.h52–57 gives7 endpoints,5 IN FIFO allocation limit,1024B FIFO geometry and real MMIO base. Native platform replaces that base with owned process memory; it never dereferences physical addresses.

## Genuine ownership paths (line numbers in exact unchanged builder C)

| Source location | Buffer/state access and transition | Context / evidence |
|---|---|---|
| xfer_ctl_t48–54; xfer_status57 | Mutable buffer cursor, optional tu_fifo_t pointer, total_len/max_size/interval; no C/Q, active-generation, abort or retirement fields | Source; native read-only diagnostic probe |
| dfifo_alloc178–225; edpt_activate261–302 | Allocate FIFO/max packet, control/direction and endpoint interrupt masks; ESP32 IN FIFO allocation includes special EP5 case | Native EP1/OUT allocation; EP5/CDC hardware behavior source-only |
| edpt_schedule_packets351–408 | Program packet count/length, enable endpoint, enable TXFE for nonzero IN; DMA branch would use buffer address/cache but is not executed | Native genuine scheduling under register fields; actual enable timing/visibility unverified |
| dcd_edpt_xfer601–628 | Void spin acquisition; closed max_size0 refuses before new descriptor; otherwise replaces buffer/ff/length, schedules and returns true | Native P01–03; no direct busy guard: P03 overwrites outstanding descriptor |
| dcd_edpt_xfer_fifo635–660 | Validates item_size1, stores FIFO pointer and length, schedules; no completion/retirement cleanup | Native P30/P31 with genuine tusb_fifo routines |
| handle_epin_slave876–923 | XFRC publishes current total_len. TXFE reads buffer/FIFO and advances cursor as packet words are written; disables TXFE when TSIZ becomes0 | Native real functions/packing. Consumption-on-return is a scripted fixture assumption |
| handle_rxflvl_irq785–847 / handle_epout_slave851–874 | Pop RX status, copy OUT/setup bytes, advance cursor/short-packet lengths; OUT completion publishes length | OUT completion metadata P32 only. RX pop/data paths BLOCKED/unexecuted; no fabricated OUT data success |
| handle_ep_irq985–1029; dcd_int_handler1038–1130 | Capture status, acknowledge endpoint status, service class-specific IN/OUT; normal endpoint ISR has no explicit same spin lock here | Native real ISR under synthetic snapshots; W1C, pending IRQ propagation and cross-core ordering unverified |
| handle_bus_reset689–741 | Clear descriptor array, disable endpoints, reset masks/address, flush FIFOs, restore EP0; real bus-reset event emitted only by enum-done743–772 | Native. Simultaneous old IRQ P12 is conditional on deliberately preserved old DAINT/status; not proof real silicon leaves it pending |
| dcd_edpt_close_all556–587 | Spin, mask noncontrol interrupts, request disable, max_size0, flush all FIFOs; buffer/length remain stored | Native P17/P18. Forced post-close IRQ despite changed masks is adversarial simulation, not normal hardware behavior |
| edpt_disable307–345; stall664–673 | IN waits for INEPNE and EPDISD then flush; OUT waits global NAK/disable. No explicit timeout | IN scripted success P19; unresolved wait watchdog P27/P28; OUT disable source-only |
| dcd_int_handler1062–1067/1079–1089 | Builder USBSUSP emits UNPLUGGED, resets FIFO allocator; OTG session-end also unplug. Does not clear transfer descriptor or certify retirement | Actual native P14–16. Generic SUSPEND behavior is not substituted |
| init/connect/disconnect413–474,499–523 | Real core setup and USB_WRAP policy changes; fake platform stores fields only. Disconnect toggles soft-disconnect, not per-transfer retirement | Native init/weak deinit observation P34; no physical electrical effect |

## Model precision

Full driver body is byte-identical and compiled by textual inclusion into driver_unit.c. Original static declarations remain static; no scheduling/FIFO/IRQ body is rewritten or static macro stripped. That wrapper adds only read-only descriptor/sizeof probes, not a replacement driver. Per-case gcov records the actual builder file/function/lines. Six real stack/common TUs plus selected DCD execute; unchanged Stage28O remains separately rerun.

Two pinned common files are adapted, with every exact hunk/input/output hash recorded:

- Common header replaces ESP32 hardware/FreeRTOS include with a native platform. Geometry is mirrored; USB_WRAP fields are simple storage, not actual register layout.
- Original common reset/flush loops retain their predicates and unlimited iteration. Read hooks optionally clear reset/flush bits and expose AHB idle. That is scripted readiness, not hardware evidence.
- Genuine FIFO helper byte packing stays intact. Load/store hooks record each written word. A packet-return hook optionally decreases TSIZ/packet count immediately; that timing is an explicit assumption, not verified transmission/host consumption.
- In-driver volatile registers are plain process fields. W1C, read-only TXFE, FIFO/status popping, posted effects and interrupt causality are **not** emulated. platform_irq injects a chosen snapshot and performs explicit cleanup after the genuine handler; it does not transform the handler's writes into W1C hardware operations. P30's direct tusb_fifo register stores bypass packing hooks and do not advance TSIZ.

Original common.c with only platform-header substitution separately times out in reset: actual PHY boundary is reached, CSRST cannot self-clear in plain memory. Adapted wait with unresolved bits also times out. Process watchdog termination is fixture evidence, not a production deadline or leak-clean teardown.

Fake CUSTOM OS records queue copies and lock calls, with serialized synchronous reentry. It is not FreeRTOS, IRQ affinity, atomicity, multi-core memory ordering or try-lock latency. No uncontrolled threads or volatile data races are used. Data/report arrays and all journals are fixed and harmless. Real configuration requests/EP0 acknowledgments are injected in memory, not USB enumeration. Direct DCD test calls intentionally bypass class submission; their class callback buffer need not equal the raw DCD payload. Class-entry cases separately verify copied ID0/ID1 frame data.

Normal receive/DMA/isochronous hardware branches, posted/W1C behavior, true disable/flush success, actual FreeRTOS/core/CDC/MSC, physical resources and host behavior remain source-only/BLOCKED. Source comments/register definitions explain tested code intent; no official hardware-completion guarantee is inferred from names or manually preloaded bits.
