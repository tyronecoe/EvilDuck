# Change B — bounded USB LED diagnostic and fixed-message receiver

Source-only experimental review candidate on top of separate STOP commit
`ef0ff5a`. No hardware, host helper or original owner file has been accessed.
No physical installation/USB return result is claimed.

## Implementation and boundary

The exact pinned Arduino3.3.0 keyboard descriptor uses reportID1 and five LED
OUTPUT bits plus padding. The existing Stage16 normalized OUTPUT route and
FeedbackKeyboard override remain; FEATURE is not treated as LED feedback. The
existing lock-state registry still updates through its short feedback critical
section. The new optional `EVILDUCK_LED_RETURN_TEST=1` ingress records only a
fixed mask/session/64-bit esp_timer timestamp into a64-entry RAM queue. It never
waits for the execution mutex, allocates, writes files/settings or sends HTTP/HID.
A separate tiny static critical section serializes the queue. Existing stopped
USB-session invalidation flushes queued input and aborts active receive. Session
tokens are software evidence, not authenticated on-wire epochs or proof every
physical disconnect is delivered by the SDK.

The normal controlled execution loop drains at most16events/turn, outside USB
callbacks. Safe-start/error-latched branches still return before this service.
No new task, USB descriptor, keyboard layout, report format or transport owner is
introduced. A fresh receive session is explicitly armed, bounded to120seconds,
and accepts only EVILDUCK TEST 123. It cannot collect arbitrary host data.
Repeated states, noise, stale sessions, invalid length/CRC, wrong fixed text,
clock regression, queue overflow and disconnect are handled fail-closed. Counters
saturate; the lifetime overflow counter is not silently reset by a new session.

Protocol/framing/pacing are specified in [the sender README](../host_tests/led_return/README.md).
It is a custom test protocol, not Hak5-compatible reflection, encryption or USB
host acknowledgment. Only fixed-data integrity is established by the decoder.

Authenticated APIs retain live `X-Duck-Password` checking and the bounded execution
capture guard. Responses are sent after capture release:

| Method/path | Effect |
|---|---|
| GET `/led-test` | observed/stale/disconnected/unknown state, Num/Caps/Scroll, timestamp, counts |
| POST `/led-test/start` | arm one120-second RAM-only receive session;409 if already armed |
| POST `/led-test/stop` | stop receiving, independent of STOP script |
| POST `/led-test/clear` | clear only RAM result/session state |
| GET `/led-test/data` | verified fixed message only;409 before successful integrity check |

Unknown/stale bits are JSON null, not confidently false. `mask` and timestamp
remain last-observed evidence; `capturedAtUs` is a separate request capture time.
The home page has explicit start/stop/refresh/view/download/clear controls.
Received text is rendered with textContent; authenticated downloads use fetched
owned bytes/Blob rather than an unauthenticated URL. No HTML or executable payload
is derived from received content. There is no filesystem persistence. Historical
completed results may remain after disconnection, distinct from unknown current LED
state, until the owner clears them.

Review also corrected Change A's fetch timeout to include the response BODY, not
only arrival of headers. A new regression covers a stalled202 body. No successful
STOP is displayed on either timeout. This refinement is in the combined B delta;
the original A commit remains independently reviewable and unchanged.

## Software checks actually executed

-103 composed production native cases PASS,0FAIL,5,884 assertions:19 new LED cases,
  all8STOP,18HTTP-contention,25keyboard and33controlled-application regressions.
-63 additional unchanged backend/diagnostic cases PASS,0FAIL,2,650 assertions.
  Same exclusions documented in the HTTP report remain; no expectations weakened.
  These ran before the final JS-only body-timeout refinement; exercised C++ code
  is unchanged, and the103-case suite ran again on the final assets.
-Combined positive C++:166PASS,0FAIL,8,534 assertions. ASan/UBSan/leaks clean.
-10 actual STOP-JS VM groups PASS,21assertions;3LED-JS groups PASS,5assertions,
  including hostile-text rendering. Not real browser/iPhone rendering tests.
-Independent Python crc_hqx vector matches native CRC0xd6cc for length+fixed data.

Malformed ID/null/zero/oversize/reserved bits, actual normalized adapter, unknown
versus observed all-off, full roundtrip with repeated reports, wrong CRC/length/
nonfixed text, timeout equality, overflow, invalidation, stale feedback, unarmed
ignore, reset/stop, auth on every API, concurrent ingress, execution cancellation
while receiving and safe served assets are covered. No physical LED observation
or Windows/macOS capture/delivery is included in these passing counts.

Initial native compilation exposed a duplicate physical header include in the
harness; it was removed without changing production code. The first related
runner selected the wrong main after composition and reported unknown T/X cases;
its source-path selection was corrected and all63 intended cases then passed.
These are recorded development failures, not disguised skips or passing tests.

## Host sender attempts and primary evidence

Windows11 source: visible PowerShell/.NET SendInput/GetKeyState sender with
partial/refused-input checks,90-second monotonic deadline, Ctrl-C and best-effort
lock restoration. SendInput/UIPI and per-thread GetKeyState limitations mean API
success is not proof of OUTPUT reports. No bypass or automatic replay is included.

macOS10.13.6 source: visible native IOHID element sender, exact VID/PID/serial
selection and output-element validation. Documented IOHIDDeviceGetValue/SetValue
APIs are available since10.5 in Apple's source. No raw report packing is guessed.
The sender requires explicit prior Caps+Num report confirmation; synchronous IOKit
calls can block. A95-second signal exit is a best-effort hard-stop backstop;
restoration cannot be guaranteed after forced termination, power loss or OS/kernel
stalls. This is not a real-time or physically tested bound. Native compilation
and permissions remain NOT TESTED, not unsupported-by-observation.

Primary reference retrieval/hash receipts are in [references](stop-led-references.json).
The direct Hak5 docs fetch returned403. No canonical wire format is inferred from
unretrieved text. Apple public source confirms API availability, not this private
owner setup's compatibility. No Windows/.NET compiler or Apple SDK is installed
in this Linux environment; neither host source is represented as compiled or run.
No new toolchain installation or global SDK/core change was made.

## Build, resource and preservation evidence

[Full clean build/link receipt](stop-led-build.json), pinned original core/SDK,
16MiB, PSRAM disabled,240MHz, existing USB-OTG/CDC/partitions. Actual linked
service/gate/USB callback, Stage18 original-error policy, checked settings,
no-format/no-examples/no-autorun controlled startup and ELF-to-BIN equality are
verified.281 link inputs, three response files,13 scripts;177 SDK archives match
the existing verified dependencies. All production source overlays are pinned in
STOP/LED manifests. Installed/global dependencies and historical firmware stay intact.

| Measurement | HTTP baseline | Combined STOP/LED | Change |
|---|---:|---:|---:|
| Compiler program | 1,366,703 | 1,376,423 | +9,720 |
| Application BIN | 1,366,848 | 1,376,576 | +9,728 |
| Static RAM | 106,328 | 107,480 | +1,152 |
| Free OTA bytes per0x740000 slot | 6,235,328 | 6,225,600 | −9,728 |
| Free OTA percentage | 82.020306% | 81.892342% | −0.127964pp |

The target receiver storage symbol is1,152B, including its fixed1,024B event ring.
No dynamic event queue exists. Existing web String allocations remain. Frame
estimates: receiver service32B, LED handler880B, STOP160B, status384B, loop32B.
These are compiler frames, not physical stack high-water/aggregate call depth.
No hardware heap, timing, stale-rate or cancellation-latency measurement occurred.

Review-only [application](../downloads/evilduck-stop-led-review.bin):1,376,576B,
SHA256 `c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4`.
ELF SHA256 `b0e2513538e83ccfedc247ae0786e5fe52c4b1cd717d1f9be69c6d566265f566`.
It is NOT an installation-approved package. Do not replace bytes in the existing
shortcut package or bypass its pinned hash check. UI assets are embedded: a future
separately reviewed application-only update and browser hard refresh are sufficient;
no whole-filesystem format/upload, examples install, NVS reset or migration is needed
for this UI change. Actual installed layout/OTA selection and update identity must
still be reviewed before any owner-authorized installation. Existing layout
NVS9000/5000, OTAe000/2000, app010000/740000, app1750000/740000,
SPIFFSe90000/160000, coredumpff0000/10000 is unchanged.

**GO:** source/build review and offline host compilation by the owner.
**PENDING:** separately authorized Windows and High Sierra LED observations, real
browser layout, fixed-message integrity and cancellation behavior.
**NO-GO in this task:** flashing, physical tests, automatic payload execution or
C-to-LED capture integration before a real supported fixed-message roundtrip.
No hardware/owner media/files have been accessed or modified.
