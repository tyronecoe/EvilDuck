# Optional passive Caps/modifier observer — native Mac pending

This source is provided for review, not run on the cloud Mac (none is available).
It uses public IOHIDManager APIs, nonseizing open, keyboard usage1/6 and explicit
VID/PID matches303A:1001 and05AC:0259. It filters Caps usage0x39 and modifier usages
0xE0..0xE7 **before reading values**. No ordinary key values, text, serial, paths or
names are output. It never sends reports/events, seizes a device, installs a driver,
uses persistence or uploads. It opens matched services to observe; it is not raw
USB capture or proof macOS exposes every Caps input as an IOHID element value.

On the owner's Mac, with already installed compiler tools, optional source review
and separately supervised test:

```bash
clang -std=c11 -Wall -Wextra mac_caps_observer.c -framework IOKit -framework CoreFoundation -o caps-observer
./caps-observer 30
```

Foreground run1..120seconds (default30), at most2000 filtered events. Ctrl-C ends it.
Output is relative monotonic host microseconds, fixed service label `evilduck` or
`builtin`, Caps/modifier usage, Boolean/value. It does not share the ESP timestamp
origin. Manually record start/STOP boundaries; do not infer synchronized clocks.

Native High Sierra compile, API behavior and permissions are PENDING OWNER. No sudo,
new packages/drivers or permission bypass is recommended. Stop on compile/open or
permission errors and report only sanitized diagnostic lines/compiler version. Do
not change OS security merely to obtain output. IOHIDManager access varies by OS
and device; no events is insufficient evidence of no USB traffic. The earlier
CGEventSourceFlagsState observer reports host flags, not individual service events.
Ordinary letters may trigger host flag reconciliation but are never logged here.
Cloud portable filter test covers six allow/deny vectors only, not native IOKit.
