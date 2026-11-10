# Observer v2: inconclusive USB-only detection closeout

Recorded 2026-11-10. **The observer supplied useful diagnostic evidence; a
High Sierra classifier and detection/branching release are not justified.**
Stop this USB-only development attempt here. No v3, longer collection, repeated
frozen export or new owner capture is requested. A specific independently
justified discriminator is required before reconsidering detector development.

This is a documentation/evidence closeout, not firmware acceptance or a new
firmware stage. The original five-second prefix remains INCOMPLETE and the
export remains UNKNOWN / NO_VALIDATED_RULE. No historical flags are repaired.

## Identity, provenance and acceptance boundaries

The assessed source is branch `routeb-usb-enum-observer-h1-review-v2`, report
checkpoint `10a0aa7685688d41ba474eae37bfa32f1647c86f`, firmware checkpoint
`b075e551e07f7b15124bdad3caa564c614f78ba4`, build
`ROUTEB-USB-ENUM-OBSERVER-H1-v2`. Its application is 1,450,624 bytes, SHA-256
`b7ac50eebe6fb5e3d69d97f20004e1014c46fb116845e30864f56de5de6d384e`.

The owner reports successful v2 installation after offline preflight PASS. The
supplied export names that build. V2 is therefore the last owner-reported running
image; no subsequent DEFINE return is reported. Independent installed-byte
readback, current physical typing acceptance and request/receipt identifiers
remain unknown. This is one development capture on an Intel Mac running
macOS High Sierra 10.13.6. The iPhone is the Wi-Fi dashboard client, not the USB
host; exact hub/cable topology is not fully documented.

The [original handoff](usb-os-observer-v2-owner-evidence/HANDOFF.txt) is copied
byte-for-byte. Its [raw JSON appendix](usb-os-observer-v2-owner-evidence/evilduck-usb-observations-v2.json)
is preserved as 2,817 bytes without a trailing newline, SHA-256:

```text
9d75febf13a302fc4d4328696f15b895010a07af6375d08c57d886ce0dd36feb
```

This establishes supplied-file integrity, not independent device provenance.
The [new evidence manifest](usb-os-observer-v2-owner-evidence.json) records the
observations and unknown fields. Despite its name, the unchanged historical
[usb-os-observer-v2-evidence.json](usb-os-observer-v2-evidence.json) records
**v1** evidence: five exports representing three boots, all already examined.
V1's unretained order-21 header remains unknown. The new MSC witness cannot
identify it retroactively. None of these captures remains held out.

All accepted DEL, DEFINE, H1, right-modifier and inherited lock-wait milestones
remain closed. H1 stays opt-in and experimental; canonical Hak5 numeric encoding
remains unresolved. No acceptance reruns are requested because identifiers are
missing. The original [evidence gate](usb-os-evidence-gate.json), contracts,
build/test receipts and release packages remain historical records unchanged.

## Findings and evidence strength

| Evidence | Supported conclusion | Boundary |
|---|---|---|
| Generation 2 begins at 260 ms; nine prefix headers occur at 272-277 ms; foreground starts at 700 ms | Early boot retention operates before the foreground window starts. Speed 0 means FULL in the pinned SDK. | Reset/unplug counts do not prove physical unplugging or topology. |
| Prefix closes at 5700 ms with nine observed/retained headers and coherent SDK configured=false | INCOMPLETE is correct under the frozen five-second contract. | Tail and live samples cannot change the historical prefix. |
| First tail selected SETUP is at 9289 ms, with observed order 1 | No additional port-0 DCD SETUP callbacks were counted between 277 and 9289 ms: 9012 ms. | This is not proof of USB silence, absent packets/transfers, or a host/device cause. |
| SET_CONFIGURATION and first recorded tail SDK-true sample occur at 9291 ms | Configuration evidence arrives 3591 ms after prefix cutoff. | SDK status and a request header do not prove completed transactions. |
| Tail: 13 observed, 12 selected, one ignored, one unsupported | Counters reconcile; the unsupported header is identified. | The complete tail request sequence was not retained. |
| Maximum coherent foreground service gap is 2 ms through finalization at 10700 ms | Accepted observer service calls remained within this bound over their recorded scope. | This is not USB IRQ/task/transfer or whole-system latency. |
| Live sample at 187965 ms is configured=true, generation 2, mismatch=false | A later coherent SDK sample reports configured. | It cannot reconstruct earlier state or establish historical mismatch absence. |

The [pinned closure and phase logic](https://github.com/tyronecoe/EvilDuck/blob/10a0aa7685688d41ba474eae37bfa32f1647c86f/tests/usb_os_observer_v2/application.patch#L78)
freezes the prefix. The [tail counter increments before filtering](https://github.com/tyronecoe/EvilDuck/blob/10a0aa7685688d41ba474eae37bfa32f1647c86f/tests/usb_os_observer_v2/application.patch#L119),
which is why firstSetup.order=1 narrows the SETUP-callback gap despite the
compressed tail. Ordinary SOF, suspend/resume, transfer-completion and function
events are intentionally outside this retained-header account.

The [coherent sample logic](https://github.com/tyronecoe/EvilDuck/blob/10a0aa7685688d41ba474eae37bfa32f1647c86f/tests/usb_os_observer_v2/application.patch#L145)
measures accepted foreground service from the first anchor at 700 ms through
finalization at 10700 ms; it excludes pre-anchor time, mismatched samples and
later service. No coherent SDK-true sample was recorded before 9291 ms, but a
brief transition between samples cannot be excluded. The later download did not
cause the missing prefix configuration. Host scheduling, device USB-task
servicing and link/hub behavior remain possible contributors to pacing; this
capture does not distinguish them or justify blaming MSC.

## MSC interpretation: observer policy versus SDK behavior

The first unsupported witness is at 9303 ms, tail-local order 12, reason 2:
`A1/FE, wValue=0, wIndex=0, wLength=1`. It matches GET MAX LUN on the
source-backed MSC interface 0 of the unchanged MSC0/HID1/CDC2-3 composition.
The sole global USBMSC object registers its interface and allocates LUN0 even
while media is inactive. Media inactivity does not remove this interface.

Source and linked-code analysis in the preceding assessment established:

| Evidence class | Finding |
|---|---|
| Composed source | `usb_msc.cpp:14` constructs the sole USBMSC object. `hid_backend.cpp:98-105` excludes FE under the observer policy; `hid_backend.cpp:200` forwards the original event once with unchanged arguments. |
| Approved Arduino 3.3.0 source | `cores/esp32/USBMSC.cpp:188-205` allocates/registers MSC independently of media; lines 63-65 return the allocated LUN count. Descriptor ordering in `esp32-hal-tinyusb.h:92` and `.c:663` puts MSC first. |
| Pinned SDK headers | `class/msc/msc.h:67` defines MSC_REQ_GET_MAX_LUN as 254. |
| Current linked ELF | Interface dispatch reaches `mscd_control_xfer_cb` at 0x4208443c. The FE path validates value 0/length 1, calls the linked LUN callback at 0x42039c34, rejects a zero count, subtracts one and schedules one byte at the `tud_control_xfer` call site 0x4208453a. |

With one allocated LUN, the **expected linked-code response is byte 0**. That is
an implementation expectation, not observed response data. This header was
recorded before SDK processing; the capture cannot establish successful response,
status-stage completion or host acceptance. Observer unsupported does not mean
SDK rejection or failed enumeration. No descriptors or media settings need to
change to explain it. The [export code](https://github.com/tyronecoe/EvilDuck/blob/10a0aa7685688d41ba474eae37bfa32f1647c86f/tests/usb_os_observer_v2_web/application.patch#L22)
also explicitly labels SDK samples as not transaction completion and emits
UNKNOWN literally; this is a capture-only status, not a completed detector.

Inspected ELF SHA-256:
`5e473ffd5813e7cea7c30871123352ceeeb64ac657519ff93ad951b096c1622d`.
Inspected SDK `libarduino_tinyusb.a` SHA-256:
`dece5cdd1d132dabb5e2022d8e3d293592b10f03de5902d9740994d652dd9a18`.
The local SDK supplies headers/precompiled code rather than the relevant C
implementation files; dispatch statements above are linked-binary inspection.
The supplied [official BOT specification, section 3.2](https://www.usb.org/sites/default/files/usbmassbulk_10.pdf)
could not be freshly retrieved during assessment (HTTP 403). It is a reference
lead, not a claimed successful new primary-document retrieval.

## Decision and bounded reopening gate

No independent primary evidence reviewed establishes a positive High Sierra
signature under this identity. GET MAX LUN and generic enumeration timing do not
meet the original gate. The known Mac label is context, never classifier input.

| Rank | Option | Decision/tradeoff |
|---|---|---|
| 1 | Reuse existing evidence; close this detection attempt as inconclusive | Adopted. No firmware/API change, extra capture or new package. Retain exact working DEFINE return. |
| 2 | Prospective capture-policy clarification | Deferred until an independently justified rule requires it. Exact known-MSC handling could improve interpretation; initialization sufficiency and OS classification would remain separate. |
| 3 | Another observer, longer collection or broader campaign now | Not justified. Additional known-Mac traces do not supply independent OS discrimination, and current instrumentation has only 32 bytes of declared resource margin. |

This closeout changes no runtime interface and introduces no classifier/getter.
Any future change needs separate approval and a specific new evidence lead.
It must preserve the 64-record bound, five-second prefix plus five-second tail,
header-only fields and authenticated explicit export, or obtain approval for a
different prospective contract. Historical exports/flags must remain unchanged.
Known MSC handling must require exactly A1/FE, value 0, interface 0 and length 1;
unexpected shapes must stay distinct. Recognizing it cannot fill the prefix gap
or produce a positive OS result.

Retain the 2048-byte observer-owned state/frame bound, maximum own frame 256 bytes,
and export bound 12288 bytes. Current reported usage is 2016/2048 bytes; external
clock-entry frames and whole-IRQ peak are separate limitations. Any later code
change must remeasure the bound rather than claim stack/latency acceptance from
compiler estimates. Preserve descriptors, keyboard behavior, STOP/cleanup,
privacy fixes, budgets and dependency guards. Capture no data stages,
descriptor/string contents, HID reports, keystrokes, files or credentials; use no
host helper, lock probe, automatic script, persistent learning or upload.

If a specific independent rule eventually justifies work, focused tests must
cover this delayed sequence, exact/malformed MSC shapes, five/ten-second deadline
boundaries, immutable historical state, overflow, generation/reset races,
clock wrap, exact forwarding, STOP/cleanup and unchanged USB identity. A future
positive rule needs independent comparison or authoritative evidence, then
separately scoped fresh validation **after rule freeze**. Existing examined
captures cannot become held-out data. Absent that evidence, stop rather than
publish an always-UNKNOWN detector. No new owner capture is requested now.

## Exact working-firmware return

The existing observer v2 ZIP contains unchanged
`working-define-labels-macos-review-v1.zip`, 2,691,374 bytes, SHA-256:

```text
b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed
```

Its `application.bin` is the working `ROUTEB-DEFINE-LABELS-H1-v1` application,
1,438,048 bytes, SHA-256:

```text
167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30
```

For a later deliberate owner return, extract this nested kit into its own folder.
With EvilDuck unplugged, run its offline check from that folder:

```bash
python3 preflight.py --directory .
```

Stop on integrity failure. Follow that kit's original guarded **install** action,
ROM-entry and rediscovered-port instructions, including its explicit confirmation
and retained private backup. This closeout performs no installation, automatic
reboot or retry. No repeated DEL/DEFINE/H1/lock-wait campaign is required.

The outer observer package's rollback instead selects older source/text-v2:
1,413,200 bytes, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
That remains mandatory historical recovery, lacks later privacy/dashboard fixes,
is not the working DEFINE return and is not a full-device restore. Neither
application-only path restores deleted scripts or historical settings. Preserve
both artifacts and every private backup. Package hashes do not prove installed
bytes or physical recovery success. High Sierra 10.13.6, Bash 3.2, Python 3.8 and
esptool 4.12 requirements remain unchanged.

## Verification and actions

The [closeout verification receipt](usb-os-observer-v2-closeout-verification.json)
records fresh supplied-file, counter/arithmetic, archive/recovery and change-scope
checks: **44 PASS, 0 FAIL**. All **201 composed source-inventory entries** match
their existing build hashes; existing application/ELF and both recovery
identities also match. All 47 preexisting local refs were checked unchanged;
remote refs were not queried or pushed. These are offline integrity checks,
not new firmware regression,
sanitizer, runtime or physical results. Earlier test/build/package totals remain
historical. No previous suite is rerun solely to close this evidence stage.

Only documentation and evidence files are changed locally. No firmware changes,
new tests, builds, packages, remote pushes, hardware access, real HID execution,
flashing, OTA, formatting, settings reset or private-data inspection occur in
this closeout. Owner installation/capture is reported evidence, not an operation
performed here. Firmware and recovery bytes remain unchanged.
