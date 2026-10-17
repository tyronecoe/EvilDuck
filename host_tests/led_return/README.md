# Visible fixed-message LED return test — hardware results NOT TESTED

No capture runs in these senders. The only transferable message is **EVILDUCK TEST
123** (17ASCII bytes). This custom protocol is not claimed Hak5 compatible.
Use only after separate owner authorization; Codex neither connects nor executes
these helpers. This is not a system-wide keylogger or proof of another keyboard's
traffic interception.

First inspect the actual candidate's authenticated LED diagnostics using harmless,
manual Caps/Num/Scroll changes. `observed=false` means unknown, not all-off;
`feedback=stale` is historical evidence, not current state. OS key state or API
success is not proof the S3 received an OUTPUT report. In particular, do not assume
Mac Num/Scroll semantics match Windows. If both Num(data) and Caps(clock) reports
are not observed, this two-bit test is unsupported for that host/setup. Do not
claim success by substituting keycode submission for observed LED return.

Protocol: one zero training byte, `EDR1`32-bit sliding sync, length17, the fixed17
ASCII bytes, CRC16-CCITT-FALSE (poly0x1021, initial0xffff) over length+payload,
high CRC byte first. All bytes MSB-first. NumLED bit0 carries data; every CapsLED
bit1 transition clocks one bit, sampled after data settles. Repeated same-clock
reports do not clock another bit. Training tolerates initial unknown feedback.
ScrollLED is irrelevant. Reference frame:
`0045445231114556494c4455434b205445535420313233d6cc`.

Pacing is deliberately slow: Windows at least60ms settling per state, plus60ms
between data and clock and after clock; Mac100ms before/after clock. OS/USB
coalescing, other keyboards, user changes or timing may still break transmission.
Receiver deadline120seconds; senders have90-second soft deadlines. Mac additionally
uses a95-second signal exit; OS/kernel stalls and forced termination prevent an
absolute runtime/restoration guarantee. No automatic retransmit.
The64-event queue is drained at most16events/loop. Overflow, invalid length/CRC,
wrong fixed text, session loss or clock regression abort rather than report delivery.
Ordinary user lock changes do not constitute a successful arbitrary message;
CRC is integrity checking, NOT authentication or cryptographic protection.

Use authenticated Start receiving immediately before a deliberate sender run.
STOP script and Stop receiving are independent. Receiver state/result are RAM-only;
no payload/NVS/filesystem writes occur. View/download is authenticated, rendered as
text, and available only for an integrity-verified fixed message. Clear deletes only
the RAM result. Disconnect invalidates current feedback and aborts an active session;
a completed result can remain identified as historical RAM data until cleared.

Windows11 attempt: standard visible PowerShell5.1/.NET Framework console:
`powershell -NoProfile -File .\send-windows.ps1`. Respect execution policy/UIPI;
never add Bypass/Unrestricted or disable security controls. It prompts for SEND,
uses documented SendInput/GetKeyState, aborts partial/refused input and restores
initial Caps/Num state in finally when possible. Closing/killing/power loss can
prevent restoration; inspect lock states manually. The sender has not been compiled
or executed on Windows in this Linux workspace. No Windows/USB compatibility PASS.

macOS10.13.6 attempt: build locally with installed Apple developer tools:
`clang -std=c11 -Wall -Wextra send-macos.c -framework IOKit -framework CoreFoundation -o send-macos`.
No compiler installation/download is performed. Invoke only after actual observed
Caps+Num output evidence: `./send-macos --caps-num-confirmed EXACT_USB_SERIAL`.
Type SEND. Exact VID303A/PID1001/serial matching must yield one HID device, with
readable/writable LED output elements. IOHIDDeviceSetValue avoids guessing report
ID/buffer packing. Permission, missing element, ambiguity or failed set is an
unsupported/error result, not success. Respect OS prompts; no seizure or bypass.
Primary APIs date to older macOS, but the actual High Sierra SDK build/runtime and
S3 USB return remain NOT TESTED. The compiler is intentionally rejected on Linux.

Linux: protocol vectors and receiver are testable offline. A Linux physical LED
sender is not supplied; delivery is an explicit remaining gap, not a compatibility
pass. `protocol_vectors.py` performs no USB, capture, network or filesystem writes.

Fallback scope, not implemented: an authenticated bounded HTTP fake-message upload
endpoint plus visible host sender would require a separate review of route access,
request-size limits, browser CSRF/origin handling and owner network connectivity.
It would be a local HTTP channel, not LED reflection. Mac home Wi-Fi does not imply
a route to EvilDuck; EvilDuck AP does not itself supply Internet/webhook routing.

Optional finite launcher sources are in `launchers/`. They were not run on a host.
Review local paths and replace the Mac serial placeholder before separate approval.
They only open the visible local sender; no downloads, policy bypass or automatic
SEND confirmation. The receiver must already be explicitly armed.
