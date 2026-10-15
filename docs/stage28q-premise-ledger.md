# Retirement premise ledger

**Conclusion: public evidence does not establish a complete safe descriptor-reuse sequence.** Official TRMv1.8 §32.5 explicitly restricts comprehensive USB-OTG register specifications under NDA. No generic DWC2 or host-channel sequence is substituted for the missing applicable device guarantee. Full official URLs, exact sizes/SHA-256 and revisions are in stage28q-source-and-model-manifest.json; retrieved PDFs/headers stay in scratch. Printed and PDF file pages below are1-based and independently extracted from these exact documents.

| ID | Exact reference / location | Supported claim and applicability | Classification / remaining ambiguity |
|---|---|---|---|
| D01 | ESP32-S3 TRMv1.8,2026-03-04; §32.2.2, printed/file1227 | EP0 bidirectional, six additional endpoints, five simultaneous IN includingEP0, shared RX and dedicated IN TX FIFOs | DOCUMENTATION ESTABLISHED. Does not establish flush addressing or retirement |
| D02 | Same, §32.3.2.2, printed/file1230–1231; §32.3.3.2 p1232 | Slave CPU FIFO pushes/pops; dedicated device TX data; no device request queues; host determines IN order | DOCUMENTATION ESTABLISHED. Pushing data is not host delivery; metadata/posted timing not specified |
| D03 | Same, §32.3.4, printed/file1233 and hierarchy figure32.3-5 p1234 | Single USB-OTG interrupt routed to one CPU; global/endpoint hierarchy and masks | DOCUMENTATION ESTABLISHED. Mask does not document draining CPU pending/ISR-active/publication |
| D04 | Same, §32.3.6.2, printed/file1235–1236, table32.3-1 | Slave IN transaction/transfer programming and transfer-complete indication | DOCUMENTATION ESTABLISHED at this abstraction. No no-future-buffer-reader/old-IRQ certificate |
| D05 | Same, §32.5, printed/file1242 | Comprehensive USB-OTG register specifications are NDA restricted; official technical-inquiry support route | DOCUMENTATION ESTABLISHED blocker. No unsupported download/bypass or support contact performed |
| D06 | ESP32-S3 Erratav1.3,2025-03-31; §3.5 USBOTG-4289 printed9–10/file11–12; history printed11/file13 | USB-OTG ROM-download restriction for specified products/batches, including somev0.2; USB Serial/JTAG distinct | DOCUMENTATION ESTABLISHED. Does not solve endpoint retirement; no new owner-device/recovery assertion |
| S01 | Selected builder DCD SHA d12ef24b…eee81a, lines307–345 | Software requests IN SNAK, polls INEPNE, requests EPDIS, polls EPDISD, writes acknowledgement, flushes TX using epnum | SOURCE SUPPORTED only. This order motivates the conditional proposal, not a documented complete silicon fence |
| S02 | Same,261–302 and common.h flush helpers111–122 | TX FIFO selection is allocated/control-field-dependent; disable flush uses epnum; close-all flushes all | SOURCE SUPPORTED. Correct endpoint-to-FIFO flush mapping and no collateral EP0/CDC/MSC effect unresolved; no bug declared solely from names |
| S03 | Same,601–628/876–923/985–1029/1038–1130 | Mutable descriptor replaced on submit; ISR reads current length/cursor; normal endpoint IRQ has no general usbd spin lock; suspend emits UNPLUGGED | SOURCE and prior native P evidence. Original C/Q unavailable; close/reset does not authenticate old work |
| S04 | Pinned TinyUSB dwc2_type.h DIEPINT_*_Pos definitions; selected DCD886–923/1005 | Bit positions complete0,disabled1,INEPNE6,TXFE7; driver writes interrupt snapshot to acknowledge and comments TXFE read-only | SOURCE SUPPORTED intent. Model W1C for0/1, RO6/7 is a conditional abstraction; exact INEPNE clearing and concurrent set/clear priority unresolved |
| S05 | IDFb66b…1180 components/soc/esp32s3/include/soc/usb_dwc_struct.h119–135,718–835 | Global reset/flush and device endpoint control/interrupt bit layouts | SOURCE SUPPORTED layout. Names/bitfields provide no independent timing/W1C/retirement semantics |
| S06 | Same IDF hal/esp32s3/include/hal/usb_dwc_ll.h240–265,287–310 | Source flush busy-waits; global status write-back clear intent | SOURCE SUPPORTED. Nonperiodic/periodic TX helper selection is HOST-oriented; not adopted as device endpoint FIFO proof |
| S07 | Same IDF esp_intr_alloc.h123–146,273–289,312–327; intr_alloc.c767–812,916–954 | Interrupt allocation on calling CPU; cross-core free may IPC-block; disable handles routing/shared-source status | SOURCE/API SUPPORTED. No per-endpoint finite ISR/publisher-quiescence certificate supplied by these calls |
| S08 | Pinned TinyUSB dwc2_esp32.h98–112 and osal_freertos.h105–127 (P records) | Driver calls esp_intr_alloc/free via void platform wrappers; FreeRTOS spin wrapper enters/exits critical | SOURCE SUPPORTED. Actual owner task/core placement not verified here; errors are not a checked retirement API |
| S09 | Pinned IDF Xtensa portmacro.h450–460,565–588; port.c468–515 | Timeout-taking critical API checks spinlock result/restores prior interrupt level on failure; ordinary enter uses NO_TIMEOUT | SOURCE SUPPORTED. Timeout0 is a possible future seam, not executed target locking/latency or complete ISR exclusion proof |

## Certificate premises explicitly NOT established

The eight model premise fields must all be true for a conditional candidate run. The public profile supplies none as a complete certificate, so requests stop without simulated hardware writes.

- `sequence`: applicable complete endpoint stop/flush/ack ordering. S01 supplies software order only; D05 leaves hardware details missing.
- `stop_access`: disable/flush acknowledgement excludes every old buffer/FIFO reader, including software IRQ fill. Not established.
- `no_late_status`: no old status/CPU dispatch can reach a newer descriptor after the fence. D03 does not provide this.
- `visibility`: requested effects/status and immutable record publication have sufficient device/inter-core ordering. No fixed delay is used as proof.
- `software_fence`: authenticated endpoint producer stop, active-ISR/publication exclusion and observer accounting. A proposed protocol, not existing pinned DCD functionality.
- `exclusive`: every submit/open/close/stall/reset/protocol producer participates. Existing raw DCD overwrite and full firmware producer coverage do not meet this.
- `ack_order`: simultaneous status assertion/acknowledgement cannot silently lose unresolved work. Public same-bit priority is unavailable; model explores both orders and quarantines ambiguity.
- `scope`: selected FIFO and masks are correct for this endpoint and do not disturb EP0/CDC/MSC. Shared/global operations require separate coordination.

No PDF/source statement is converted into a measured physical guarantee. Errata absence of a listed endpoint issue is not evidence that the missing guarantee holds. No need to upload private backups or repeat Mac smoke arises from this ledger.
