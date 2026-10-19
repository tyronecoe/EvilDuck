# Owner evidence and provenance — 2026-10-19

Owner confirmed installed dashboard buildId **MAC-CAPS-TIMING-20261019-v1** and
application SHA-256 **5e10009fd3e5a0a862b4f7bed1f7f28ba8464f7bb1066fd8091c6e01b2ed4a59**.
The existing published image is 1,397,968 bytes. This is owner-reported installed
provenance, not a cloud readback. The new package carries those exact bytes as rollback.

Owner reports from macOS High Sierra10.13.6: built-in Apple keyboard05AC:0259,
EvilDuck303A:1001, keyboard usage1/6. At500ms ordinary Caps dwell, EvilDuck text case
and polled host Caps flags can toggle without the built-in keyboard LED/physical
case following. Both HIDSystem and CombinedSession polled sources agreed in23/30
transitions; this does not establish per-device synchronization. Physical typing
sometimes reconciled the flag toOFF. Some transitions continued during repeated
STOP attempts; unplugging ended them. The polled observer did not send input.
Counters measure sampled flag transitions, not new USB reports.

Cause remains UNRESOLVED. No cloud hardware, current USB capture, private backups,
owner scripts or physical keyboard text were accessed. Existing successful typing
and functional fixtures remain historical owner evidence with their original limits.

Owner reiterated High Sierra10.13.6 as the target during this task. No modern macOS synchronization model is assumed; native IOKit and actual built-in LED behavior require tests on that specific Mac.
