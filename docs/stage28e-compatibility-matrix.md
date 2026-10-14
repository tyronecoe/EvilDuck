# Stage28E opt-in mock capability matrix

Language-command statuses are unchanged. The formerly deferred mock adapter now exists opt-in.
Historical matrices remain intact; no physical or full DS3 compatibility claim.

| Feature | Status | Evidence |
|---|---|---|
| Opt-in Runtime-to-Planner bridge | Implemented mock-only | Complete-script exact vectors and acknowledgement tests |
| Character/KeyTap press plus restoration | Implemented within existing limits | Ack waits, identical neighbors and long Retry tests |
| Delay accepted after preceding actions | Implemented virtual scheduling | No report for Delay; accepted timestamp/wrap/stalled tests |
| Persistent owner setup/restoration | Prepared internal API only | Shift restore, held-tap/rollover and completion cleanup |
| Cancel/STOP/error plus explicit drain | Implemented mock-only | No fabricated ack, failure snapshots, neutral/restart gate |
| HOLD/RELEASE parser commands | Still unsupported in preview | No grammar or legacy dispatch change |
| Unicode/DE/dead keys/host locks | Still unsupported | Preflight/domain rejection; no approximation |
| Real HID/USB/OS/transport or physical release | Absent/unauthorized | Only opaque memory reports; no hardware operation |
